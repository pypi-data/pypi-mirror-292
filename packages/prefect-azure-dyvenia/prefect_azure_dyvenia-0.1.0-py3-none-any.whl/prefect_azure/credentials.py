"""Credential classes used to perform authenticated interactions with Azure"""

import functools
from typing import TYPE_CHECKING, Optional

from pydantic import SecretStr

try:
    from azure.cosmos import CosmosClient

    if TYPE_CHECKING:
        from azure.cosmos import ContainerProxy, DatabaseProxy
except ModuleNotFoundError:
    pass  # a descriptive error will be raised in get_client

try:
    from azure.storage.blob.aio import BlobClient, BlobServiceClient, ContainerClient
except ModuleNotFoundError:
    pass  # a descriptive error will be raised in get_client

try:
    from azureml.core.authentication import ServicePrincipalAuthentication
    from azureml.core.workspace import Workspace
except ModuleNotFoundError:
    pass  # a descriptive error will be raised in get_workspace

try:
    from azure.identity import ClientSecretCredential
except ModuleNotFoundError:
    pass  # a descriptive error will be raised in get_client

try:
    from azure.keyvault.secrets import SecretClient
except ModuleNotFoundError:
    pass  # a descriptive error will be raised in get_client

from prefect.blocks.core import Block

HELP_URLS = {
    "blob_storage": "https://docs.microsoft.com/en-us/azure/storage/blobs/storage-quickstart-blobs-python#copy-your-credentials-from-the-azure-portal",  # noqa
    "cosmos_db": "https://docs.microsoft.com/en-us/azure/cosmos-db/sql/create-sql-api-python#update-your-connection-string",  # noqa
    "ml_datastore": "https://github.com/Azure/MachineLearningNotebooks/blob/master/how-to-use-azureml/manage-azureml-service/authentication-in-azureml/authentication-in-azureml.ipynb",  # noqa
    "keyvault": "https://learn.microsoft.com/en-us/python/api/azure-identity/azure.identity.clientsecretcredential?view=azure-python",  # noqa
}
HELP_FMT = "Please visit {help_url} for retrieving the proper connection string."


def _raise_help_msg(key: str):
    """
    Raises a helpful error message.

    Args:
        key: the key to access HELP_URLS
    """

    def outer(func):
        """
        Used for decorator.
        """

        @functools.wraps(func)
        def inner(*args, **kwargs):
            """
            Used for decorator.
            """
            try:
                return func(*args, **kwargs)
            except NameError as exc:
                raise ImportError(
                    f"To use prefect_azure.{key}, install prefect-azure with the "
                    f"'{key}' extra: `pip install 'prefect_azure[{key}]'`"
                ) from exc
            except ValueError as exc:
                raise ValueError(HELP_FMT.format(help_url=HELP_URLS[key])) from exc

        return inner

    return outer


class AzureKeyVaultCredentials(Block):
    """
    Block used to manage Aure KeyVault authentication with Azure.
    Authentication is handled via the `azure-keyvault-secrets` module through
    a service principal (Azure name for a service account).

    Args:
        vault_name: The name of the Keyvault to be accessed.
        tenant_id: The active directory tenant that the service account belongs to.
        client_id: The service principal ID.
        client_secret: The service principal password/key.

    Example:
        Load stored Azure KeyVault credentials:
        ```python
        from prefect_azure import AzureKeyVaultCredentials
        azure_keyvault_credentials_block = AzureKeyVaultCredentials.load("MY_BLOCK_NAME")  # noqa
        ```
    """

    _block_type_name = "Azure KeyVault Credentials"
    _logo_url = "https://images.ctfassets.net/gm98wzqotmnx/6AiQ6HRIft8TspZH7AfyZg/39fd82bdbb186db85560f688746c8cdd/azure.png?h=250"  # noqa  # change this

    vault_name: str
    tenant_id: str
    client_id: str
    client_secret: SecretStr

    @_raise_help_msg("keyvault")
    def get_client(self) -> "SecretClient":
        """
        Get an Azure Key Vault client.

        Returns:
            SecretClient: An authenticated Azure Key Vault client that can be used
            to interact with an Azure Key Vault instance.
        """
        client_secret = self.client_secret.get_secret_value()
        credential = ClientSecretCredential(
            tenant_id=self.tenant_id,
            client_id=self.client_id,
            client_secret=client_secret,
        )
        vault_url = f"https://{self.vault_name}.vault.azure.net"
        return SecretClient(vault_url=vault_url, credential=credential)

    def get_secret(self, secret: str) -> str:
        """
        Retrieve a secret from an Azure Key Vault instance.

        Args:
            secret (str): The secret to retrieve.

        Returns:
            str: The value of the secret.
        """
        client = self.get_client()
        return client.get_secret(secret).value


class AzureKeyVaultSecretReference(Block):
    """
    Block used for storing references to Azure Key Vault secrets.
    For this purpose, we store here the relevant Key Vault credentials block,
    as well as the name of the secret inside that Key Vault instance,
    which holds the target credentials. This is done so that we only store Key Vault
    credentials on Prefect, and all the other secrets are fetched from Azure Key Vault.

    Args:
        credentials (AzureKeyVaultCredentials, optional): The service principal
            credentials to be used to authenticate to Azure Key Vault
            and retrieve the `secret` secret.
        secret (str): The secret in Azure Key Vault containing the credentials.
    """

    _block_type_name = "Azure KeyVault Secret Reference"
    _logo_url = "https://images.ctfassets.net/gm98wzqotmnx/6AiQ6HRIft8TspZH7AfyZg/39fd82bdbb186db85560f688746c8cdd/azure.png?h=250"  # noqa  # change this

    credentials: AzureKeyVaultCredentials
    secret: str

    def get_secret(self) -> str:
        """
        Retrieve a secret from an Azure Key Vault instance.

        Returns:
            str: The value of the secret.
        """
        return self.credentials.get_secret(self.secret)


class AzureBlobStorageCredentials(Block):
    """
    Block used to manage Blob Storage authentication with Azure.
    Azure authentication is handled via the `azure` module through
    a connection string, or through the `azure-keyvault-secrets` module through
    `AzureKeyVaultCredentials`.

    If authenticating with a connection string, specify only the `connection_string`.
    If authenticating with credentials stored in Azure Key Vault, specify both
    `keyvault_credentials` and `keyvault_key`.

    Note that while keyvault authentication is not yet supported in tasks,
    as they all use `AzureBlobStorageCredentials.get_blob_client()`,
    which in turn uses `BlobServiceClient.from_connection_string()`.

    Args:
        connection_string (str, optional): The connection string to be used
            for authentication.
        keyvault_credentials (AzureKeyVaultCredentials, optional): The service principal
            credentials to be used to authenticate to Azure Key Vault
            and retrieve the `keyvault_key` secret.
        keyvault_key (str, optional): The key in Azure Key Vault containing Blob Storage
            credentials. Required when using `keyvault_credentials`.

    Example:
        Load stored Azure Blob Storage credentials:
        ```python
        from prefect_azure import AzureBlobStorageCredentials
        azure_credentials_block = AzureBlobStorageCredentials.load("BLOCK_NAME")
        ```

    Create an Azure Key Vault secret with Azure Blob Storage credentials
    and use it in Prefect:
    ```python
    from prefect_azure import AzureBlobStorageCredentials

    # Create a key vault credential that stores the credentials
    # to an Azure Key Vault.
    vault_name = "my_keyvault"
    config = {
        "vault_name": vault_name,
        "tenant_id": "TENANT_ID",
        "client_id": "CLIENT_ID",
        "client_secret": "CLIENT_SECRET",
    }
    keyvault_block = AzureKeyVaultCredentials(**config)
    keyvault_block.save(vault_name, overwrite=True)

    # Create an ADLS credential using `AzureBlobStorageCredentials`
    # which will fetch the credentials from Azure Key Vault.
    azure_keyvault_credentials_block = AzureKeyVaultCredentials.load(vault_name)
    adls_credentials = AzureBlobStorageCredentials(
        keyvault_credentials=azure_keyvault_credentials_block,
        keyvault_key="my_adls_service_principal_secret",
    )
    adls_credentials.save("adls-dev")

    # Now we can use them in a flow
    adls_credentials = AzureBlobStorageCredentials.load("adls-dev")
    ```
    """

    _block_type_name = "Azure Blob Storage Credentials"
    _logo_url = "https://images.ctfassets.net/gm98wzqotmnx/6AiQ6HRIft8TspZH7AfyZg/39fd82bdbb186db85560f688746c8cdd/azure.png?h=250"  # noqa

    connection_string: Optional[SecretStr]
    keyvault_credentials: Optional[AzureKeyVaultCredentials]
    keyvault_key: Optional[str]

    @_raise_help_msg("blob_storage")
    def get_client(self) -> "BlobServiceClient":
        """
        Returns an authenticated base Blob Service client that can be used to create
        other clients for Azure services.

        Example:
            Create an authorized Blob Service session
            ```python
            import os
            import asyncio
            from prefect import flow
            from prefect_azure import AzureBlobStorageCredentials

            @flow
            async def example_get_client_flow():
                connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
                azure_credentials = AzureBlobStorageCredentials(
                    connection_string=connection_string,
                )
                async with azure_credentials.get_client() as blob_service_client:
                    # run other code here
                    pass

            asyncio.run(example_get_client_flow())
            ```
        """
        return BlobServiceClient.from_connection_string(
            self.connection_string.get_secret_value()
        )

    @_raise_help_msg("blob_storage")
    def get_blob_client(self, container, blob) -> "BlobClient":
        """
        Returns an authenticated Blob client that can be used to
        download and upload blobs.

        Args:
            container: Name of the Blob Storage container to retrieve from.
            blob: Name of the blob within this container to retrieve.

        Example:
            Create an authorized Blob session
            ```python
            import os
            import asyncio
            from prefect import flow
            from prefect_azure import AzureBlobStorageCredentials

            @flow
            async def example_get_blob_client_flow():
                connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
                azure_credentials = AzureBlobStorageCredentials(
                    connection_string=connection_string,
                )
                async with azure_credentials.get_blob_client(
                    "container", "blob"
                ) as blob_client:
                    # run other code here
                    pass

            asyncio.run(example_get_blob_client_flow())
            ```
        """
        blob_client = BlobClient.from_connection_string(
            self.connection_string.get_secret_value(), container, blob
        )
        return blob_client

    @_raise_help_msg("blob_storage")
    def get_container_client(self, container) -> "ContainerClient":
        """
        Returns an authenticated Container client that can be used to create clients
        for Azure services.

        Args:
            container: Name of the Blob Storage container to retrieve from.

        Example:
            Create an authorized Container session
            ```python
            import os
            import asyncio
            from prefect import flow
            from prefect_azure import AzureBlobStorageCredentials

            @flow
            async def example_get_container_client_flow():
                connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
                azure_credentials = AzureBlobStorageCredentials(
                    connection_string=connection_string,
                )
                async with azure_credentials.get_container_client(
                    "container"
                ) as container_client:
                    # run other code here
                    pass

            asyncio.run(example_get_container_client_flow())
            ```
        """
        container_client = ContainerClient.from_connection_string(
            self.connection_string.get_secret_value(), container
        )
        return container_client


class AzureCosmosDbCredentials(Block):
    """
    Block used to manage Cosmos DB authentication with Azure.
    Azure authentication is handled via the `azure` module through
    a connection string.

    Args:
        connection_string: Includes the authorization information required.

    Example:
        Load stored Azure Cosmos DB credentials:
        ```python
        from prefect_azure import AzureCosmosDbCredentials
        azure_credentials_block = AzureCosmosDbCredentials.load("MY_BLOCK_NAME")
        ```
    """

    _block_type_name = "Azure Cosmos DB Credentials"
    _logo_url = "https://images.ctfassets.net/gm98wzqotmnx/6AiQ6HRIft8TspZH7AfyZg/39fd82bdbb186db85560f688746c8cdd/azure.png?h=250"  # noqa

    connection_string: SecretStr

    @_raise_help_msg("cosmos_db")
    def get_client(self) -> "CosmosClient":
        """
        Returns an authenticated Cosmos client that can be used to create
        other clients for Azure services.

        Example:
            Create an authorized Cosmos session
            ```python
            import os
            from prefect import flow
            from prefect_azure import AzureCosmosDbCredentials

            @flow
            def example_get_client_flow():
                connection_string = os.getenv("AZURE_COSMOS_CONNECTION_STRING")
                azure_credentials = AzureCosmosDbCredentials(
                    connection_string=connection_string,
                )
                cosmos_client = azure_credentials.get_client()
                return cosmos_client

            example_get_client_flow()
            ```
        """
        return CosmosClient.from_connection_string(
            self.connection_string.get_secret_value()
        )

    def get_database_client(self, database: str) -> "DatabaseProxy":
        """
        Returns an authenticated Database client.

        Args:
            database: Name of the database.

        Example:
            Create an authorized Cosmos session
            ```python
            import os
            from prefect import flow
            from prefect_azure import AzureCosmosDbCredentials

            @flow
            def example_get_client_flow():
                connection_string = os.getenv("AZURE_COSMOS_CONNECTION_STRING")
                azure_credentials = AzureCosmosDbCredentials(
                    connection_string=connection_string,
                )
                cosmos_client = azure_credentials.get_database_client()
                return cosmos_client

            example_get_database_client_flow()
            ```
        """
        cosmos_client = self.get_client()
        database_client = cosmos_client.get_database_client(database=database)
        return database_client

    def get_container_client(self, container: str, database: str) -> "ContainerProxy":
        """
        Returns an authenticated Container client used for querying.

        Args:
            container: Name of the Cosmos DB container to retrieve from.
            database: Name of the Cosmos DB database.

        Example:
            Create an authorized Container session
            ```python
            import os
            from prefect import flow
            from prefect_azure import AzureBlobStorageCredentials

            @flow
            def example_get_container_client_flow():
                connection_string = os.getenv("AZURE_COSMOS_CONNECTION_STRING")
                azure_credentials = AzureCosmosDbCredentials(
                    connection_string=connection_string,
                )
                container_client = azure_credentials.get_container_client(container)
                return container_client

            example_get_container_client_flow()
            ```
        """
        database_client = self.get_database_client(database)
        container_client = database_client.get_container_client(container=container)
        return container_client


class AzureMlCredentials(Block):
    """
    Block used to manage authentication with AzureML. Azure authentication is
    handled via the `azure` module.

    Args:
        tenant_id: The active directory tenant that the service identity belongs to.
        service_principal_id: The service principal ID.
        service_principal_password: The service principal password/key.
        subscription_id: The Azure subscription ID containing the workspace.
        resource_group: The resource group containing the workspace.
        workspace_name: The existing workspace name.

    Example:
        Load stored AzureML credentials:
        ```python
        from prefect_azure import AzureMlCredentials
        azure_ml_credentials_block = AzureMlCredentials.load("MY_BLOCK_NAME")
        ```
    """

    _block_type_name = "AzureML Credentials"
    _logo_url = "https://images.ctfassets.net/gm98wzqotmnx/6AiQ6HRIft8TspZH7AfyZg/39fd82bdbb186db85560f688746c8cdd/azure.png?h=250"  # noqa

    tenant_id: str
    service_principal_id: str
    service_principal_password: SecretStr
    subscription_id: str
    resource_group: str
    workspace_name: str

    @_raise_help_msg("ml_datastore")
    def get_workspace(self) -> "Workspace":
        """
        Returns an authenticated base Workspace that can be used in
        Azure's Datasets and Datastores.

        Example:
            Create an authorized workspace
            ```python
            import os
            from prefect import flow
            from prefect_azure import AzureMlCredentials
            @flow
            def example_get_workspace_flow():
                azure_credentials = AzureMlCredentials(
                    tenant_id="tenant_id",
                    service_principal_id="service_principal_id",
                    service_principal_password="service_principal_password",
                    subscription_id="subscription_id",
                    resource_group="resource_group",
                    workspace_name="workspace_name"
                )
                workspace_client = azure_credentials.get_workspace()
                return workspace_client
            example_get_workspace_flow()
            ```
        """
        service_principal_password = self.service_principal_password.get_secret_value()
        service_principal_authentication = ServicePrincipalAuthentication(
            tenant_id=self.tenant_id,
            service_principal_id=self.service_principal_id,
            service_principal_password=service_principal_password,
        )

        workspace = Workspace(
            subscription_id=self.subscription_id,
            resource_group=self.resource_group,
            workspace_name=self.workspace_name,
            auth=service_principal_authentication,
        )

        return workspace

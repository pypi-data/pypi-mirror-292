from unittest.mock import MagicMock

from azure.storage.blob import BlobClient, BlobServiceClient, ContainerClient
from conftest import CosmosClientMock, SecretClientMock
from prefect import flow

from prefect_azure.credentials import (
    AzureBlobStorageCredentials,
    AzureCosmosDbCredentials,
    AzureKeyVaultCredentials,
    AzureKeyVaultSecretReference,
    AzureMlCredentials,
)


def test_get_service_client(blob_connection_string):
    @flow
    def test_flow():
        client = AzureBlobStorageCredentials(
            connection_string=blob_connection_string
        ).get_client()
        return client

    client = test_flow()
    assert isinstance(client, BlobServiceClient)


def test_get_blob_container_client(blob_connection_string):
    @flow
    def test_flow():
        client = AzureBlobStorageCredentials(
            connection_string=blob_connection_string
        ).get_container_client("container")
        return client

    client = test_flow()
    assert isinstance(client, ContainerClient)
    client.container_name == "container"


def test_get_blob_client(blob_connection_string):
    @flow
    def test_flow():
        client = AzureBlobStorageCredentials(
            connection_string=blob_connection_string
        ).get_blob_client("container", "blob")
        return client

    client = test_flow()
    assert isinstance(client, BlobClient)
    client.container_name == "container"
    client.blob_name == "blob"


def test_get_cosmos_client(cosmos_connection_string):
    @flow
    def test_flow():
        client = AzureCosmosDbCredentials(
            connection_string=cosmos_connection_string
        ).get_client()
        return client

    client = test_flow()
    assert isinstance(client, CosmosClientMock)


def test_get_database_client(cosmos_connection_string):
    @flow
    def test_flow():
        client = AzureCosmosDbCredentials(
            connection_string=cosmos_connection_string
        ).get_database_client("database")
        return client

    client = test_flow()
    assert client.database == "database"


def test_get_cosmos_container_client(cosmos_connection_string):
    @flow
    def test_flow():
        client = AzureCosmosDbCredentials(
            connection_string=cosmos_connection_string
        ).get_container_client("container", "database")
        return client

    client = test_flow()
    assert client.container == "container"


def test_get_workspace(monkeypatch):
    monkeypatch.setattr("prefect_azure.credentials.Workspace", MagicMock)

    @flow
    def test_flow():
        workspace = AzureMlCredentials(
            tenant_id="tenant_id",
            service_principal_id="service_principal_id",
            service_principal_password="service_principal_password",
            subscription_id="subscription_id",
            resource_group="resource_group",
            workspace_name="workspace_name",
        ).get_workspace()
        return workspace

    workspace = test_flow()
    assert isinstance(workspace, MagicMock)


def test_get_keyvault_client(keyvault_credentials):
    # This one breaks with `TypeError: cannot pickle '_thread._local' object`
    # if trying to use inside a flow.
    client = AzureKeyVaultCredentials(**keyvault_credentials).get_client()
    assert isinstance(client, SecretClientMock)


def test_get_keyvault_secret(keyvault_credentials):
    @flow
    def test_flow():
        secret_value = AzureKeyVaultCredentials(**keyvault_credentials).get_secret(
            secret="secret"
        )
        return secret_value

    secret_value = test_flow()
    assert secret_value == "secret_value"


def test_get_keyvault_secret_by_reference(keyvault_credentials):
    @flow
    def test_flow():
        credentials = AzureKeyVaultCredentials(**keyvault_credentials)
        secret_value = AzureKeyVaultSecretReference(
            credentials=credentials, secret="secret"
        ).get_secret()
        return secret_value

    secret_value = test_flow()
    assert secret_value == "secret_value"

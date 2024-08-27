from setuptools import find_packages, setup

import versioneer

with open("README.md") as readme_file:
    readme = readme_file.read()

extras_require = {
    "blob_storage": ["azure-storage-blob"],
    "cosmos_db": ["azure-cosmos"],
    "ml_datastore": ["azureml-core"],
    "key_vault": ["azure-keyvault-secrets>=4.6.0", "azure-identity>=1.11.0"],
}
extras_require["all_extras"] = sorted(
    {lib for key in extras_require.values() for lib in key if key != "dev"}
)

setup(
    name="prefect-azure-dyvenia",
    description="Prefect tasks and subflows for interacting with Azure",
    license="Apache License 2.0",
    author="Prefect Technologies, Inc.",
    author_email="help@prefect.io",
    keywords="prefect",
    url="https://github.com/Trymzet/prefect-azure",
    long_description=readme,
    long_description_content_type="text/markdown",
    version="0.1.0",
    packages=find_packages(exclude=("tests", "docs")),
    python_requires=">=3.7",
    install_requires=["prefect"],
    extras_require=extras_require,
    entry_points={
        "prefect.collections": [
            "AzureBlobStorageCredentials = prefect_azure.credentials",
            "AzureCosmosDbCredentials = prefect_azure.credentials",
            "AzureMlCredentials = prefect_azure.credentials",
            "AzureKeyVaultCredentials = prefect_azure.credentials",
            "AzureKeyVaultSecretReference = prefect_azure.credentials",
        ]
    },
    classifiers=[
        "Natural Language :: English",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Software Development :: Libraries",
    ],
)

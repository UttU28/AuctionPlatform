from azure.storage.blob import BlobServiceClient
from werkzeug.utils import secure_filename
from config import AzureBLOBConfig
import os

# Configuration for Azure Blob Storage


def get_blob_service_client():
    return BlobServiceClient.from_connection_string(AzureBLOBConfig.AZURE_CONNECTION_STRING)

def upload_to_blob(file, resumeName):
    blob_service_client = get_blob_service_client()
    blob_client = blob_service_client.get_blob_client(container=AzureBLOBConfig.CONTAINER_NAME, blob=resumeName)
    blob_client.upload_blob(file, overwrite=True)
    # GOOD LUCK FINDING THIS WHEN IT TURNS TO ERROR 08/11/2024 4:29 AM Bitch
    return resumeName

def download_from_blob(filename):
    blob_service_client = get_blob_service_client()
    blob_client = blob_service_client.get_blob_client(container=AzureBLOBConfig.CONTAINER_NAME, blob=filename)

    # Download the blob to a byte stream
    download_stream = blob_client.download_blob()
    return download_stream.readall()

def list_blobs():
    blob_service_client = get_blob_service_client()
    container_client = blob_service_client.get_container_client(AzureBLOBConfig.CONTAINER_NAME)

    # List all blobs in the container
    blob_list = container_client.list_blobs()
    return [blob.name for blob in blob_list]

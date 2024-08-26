import os
from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions
from datetime import datetime, timedelta
from dotenv import load_dotenv


class AzureBlobManager:
    def __init__(self, account_name=None, account_key=None, cdn_hostname=None, service_name=None,
                 container_name="teesign"):
        load_dotenv()
        self.account_name = account_name or os.getenv("AZURE_STORAGE_ACCOUNT_NAME")
        self.account_key = account_key or os.getenv("AZURE_STORAGE_ACCOUNT_KEY")
        self.cdn_hostname = cdn_hostname or os.getenv("AZURE_CDN_HOSTNAME")
        self.service_name = service_name or os.getenv("SERVICE_NAME")  # Service name from env or passed in
        self.container_name = container_name
        self.blob_service_client = BlobServiceClient.from_connection_string(
            f"DefaultEndpointsProtocol=https;AccountName={self.account_name};AccountKey={self.account_key};EndpointSuffix=core.windows.net"
        )

    def get_container_client(self, container_name=None):
        container_name = container_name or self.container_name
        return self.blob_service_client.get_container_client(container_name)

    def create_container(self, container_name=None):
        container_name = container_name or self.container_name
        container_client = self.get_container_client(container_name)
        try:
            container_client.create_container()
            print(f"Container '{container_name}' created successfully.")
        except Exception as e:
            if "ContainerAlreadyExists" in str(e):
                print(f"Container '{container_name}' already exists.")
            else:
                print(f"Could not create container '{container_name}'. Error: {e}")

    def upload_to_blob(self, file_path, blob_name, container_name=None):
        container_name = container_name or self.container_name
        blob_name = f"{self.service_name}/{blob_name}"  # Prepend service name to the blob name
        container_client = self.get_container_client(container_name)
        blob_client = container_client.get_blob_client(blob_name)
        with open(file_path, "rb") as data:
            blob_client.upload_blob(data, overwrite=True)
        return blob_client.url

    def generate_blob_sas_token(self, blob_path, expiry_hours=1, container_name=None):
        container_name = container_name or self.container_name
        blob_path = f"{self.service_name}/{blob_path}"  # Prepend service name to the blob path
        sas_token = generate_blob_sas(
            account_name=self.blob_service_client.account_name,
            container_name=container_name,
            blob_name=blob_path,
            account_key=self.blob_service_client.credential.account_key,
            permission=BlobSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(hours=expiry_hours)
        )
        return sas_token

    def get_cdn_url(self, blob_name, container_name=None):
        container_name = container_name or self.container_name
        blob_name = f"{self.service_name}/{blob_name}"  # Prepend service name to the blob name
        sas_token = self.generate_blob_sas_token(blob_name, container_name=container_name)
        front_door_url = f"https://{self.cdn_hostname}/{container_name}/{blob_name}?{sas_token}"
        return front_door_url

    async def download_from_blob(self, container_name, blob_name, download_path):
        container_client = self.blob_service_client(container_name)
        blob_client = container_client.get_blob_client(blob_name)

        # Create the directory if it does not exist
        os.makedirs(os.path.dirname(download_path), exist_ok=True)

        with open(download_path, "wb") as download_file:
            download_file.write(blob_client.download_blob().readall())

    @staticmethod
    def file_exists_locally(file_path):
        return os.path.exists(file_path)

    async def ensure_local_copy(self, container_name, blob_name, local_path):
        if not AzureBlobManager.file_exists_locally(local_path):
            print(f"Downloading '{blob_name}' to '{local_path}'")
            await self.download_from_blob(container_name, blob_name, local_path)

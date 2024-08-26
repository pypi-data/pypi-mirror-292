import os
from urllib.parse import urlparse, parse_qsl, urlunparse, quote
import requests
from PIL import Image
from io import BytesIO
from bson import ObjectId

class FileManager:
    @staticmethod
    def file_exists_locally(file_path):
        return os.path.exists(file_path)

    @staticmethod
    def download_image(image_url: str, save_path: str) -> None:
        parsed_url = urlparse(image_url)
        query = dict(parse_qsl(parsed_url.query))
        encoded_query = "&".join([f"{quote(k)}={quote(v)}" for k, v in query.items()])
        encoded_url = urlunparse(parsed_url._replace(query=encoded_query))

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }

        response = requests.get(encoded_url, headers=headers)
        if response.status_code == 200:
            image = Image.open(BytesIO(response.content))
            image.save(save_path)
        else:
            raise Exception(f"{response.status_code}: Failed to download image.")


    @staticmethod
    def to_json_serializable(data):
        if isinstance(data, ObjectId):
            return str(data)
        elif isinstance(data, list):
            return [FileManager.to_json_serializable(item) for item in data]
        elif isinstance(data, dict):
            return {key: FileManager.to_json_serializable(value) for key, value in data.items()}
        else:
            return data

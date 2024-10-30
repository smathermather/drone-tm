import os
import requests
from datetime import datetime
from loguru import logger as log


class OpenAerialMapUploader:
    def __init__(self, api_token):
        self.api_token = api_token
        self.base_url = "https://api.openaerialmap.org"
        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json",
        }

    def create_metadata(
        self,
        image_path,
        title,
        provider="Drone Provider",
        platform="drone",
        sensor="RGB",
    ):
        """
        Generates metadata required by Open Aerial Map.
        Modify this method as per your metadata needs.
        """
        filename = os.path.basename(image_path)
        metadata = {
            "title": title,
            "provider": provider,
            "platform": platform,
            "sensor": sensor,
            "acquisition_start": datetime.now().isoformat(),
            "acquisition_end": datetime.now().isoformat(),
            # "description": "Uploaded drone imagery",
            # "tags": ["drone", "aerial", "RGB"],
            "filename": filename,
            "urls": [
                "https://oam-uploader-production-temp.s3.us-east-1.amazonaws.com/odm_orthophoto-4-bitw4cw6j.tif"
            ],
            "license": "CC-BY 4.0",
            "contact": None,
        }
        return metadata

    def upload_image(self, image_path, metadata):
        """
        Uploads an image to Open Aerial Map with associated metadata.
        """
        upload_url = f"{self.base_url}/uploads"
        # Prepare the files and metadata for upload
        files = {"file": open(image_path, "rb")}
        response = requests.post(
            upload_url, files=files, data=metadata, headers=self.headers
        )
        # Check if the upload is successful
        if response.status_code == 201:
            log.info(f"Image uploaded successfully: {response.json()['url']}")
        else:
            log.error(
                f"Failed to upload image: {response.status_code} - {response.text}"
            )

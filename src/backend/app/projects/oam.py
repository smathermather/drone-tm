import os
import requests
from datetime import datetime
from app.config import settings


class OpenAerialMapUploader:
    def __init__(self, api_token):
        self.api_token = api_token
        self.base_url = "https://api.openaerialmap.org"
        self.headers = {
            'Authorization': f'Bearer {self.api_token}',
            'Content-Type': 'application/json'
        }

    def create_metadata(self, image_path, title, provider="Drone Provider", platform="drone", sensor="RGB"):
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
            "description": "Uploaded drone imagery",
            "tags": ["drone", "aerial", "RGB"],
            "filename": filename
        }
        return metadata

    def upload_image(self, image_path, metadata):
        """
        Uploads an image to Open Aerial Map with associated metadata.
        """
        upload_url = f"{self.base_url}/meta"
        # Prepare the files and metadata for upload
        files = {'file': open(image_path, 'rb')}
        response = requests.post(upload_url, files=files, data=metadata, headers=self.headers)
        
        # Check if the upload is successful
        if response.status_code == 201:
            print(f"Image uploaded successfully: {response.json()['url']}")
        else:
            print(f"Failed to upload image: {response.status_code} - {response.text}")

if __name__ == "__main__":
    # Replace with your actual API token from Open Aerial Map
    api_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJfaWQiOiI2NzIwOTM5NWNhZmQ0ZjAwMDFlNDhhYWMiLCJuYW1lIjoiUHJhZGlwIFRoYXBhIiwiY29udGFjdF9lbWFpbCI6InByYWRpcHRoYXBhLm5heGFAZ21haWwuY29tIiwic2NvcGUiOiJ1c2VyIiwiaWF0IjoxNzMwMTkxMjcwLCJleHAiOjE3NjE3MjcyNzB9.9q93w-E2MxebVBHSyRZngBty3lEwgsfjr0uX9gc7x54"

    uploader = OpenAerialMapUploader(api_token)

    # Path to the drone imagery
    image_path = "path/to/your/drone/image.tif"

    # Create metadata for the image
    metadata = uploader.create_metadata(image_path, title="My Drone Image")

    # Upload the image to Open Aerial Map
    uploader.upload_image(image_path, metadata)
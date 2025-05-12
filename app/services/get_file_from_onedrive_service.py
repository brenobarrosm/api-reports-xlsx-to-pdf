import requests
from io import BytesIO


class GetFileFromOneDriveService:
    def execute(self, url: str) -> BytesIO:
        file = self.download_onedrive_file_to_bytesio(url)
        return file

    @staticmethod
    def download_onedrive_file_to_bytesio(url: str):
        if '?download=1' not in url and '&download=1' not in url:
            if '?' in url:
                url += '&download=1'
            else:
                url += '?download=1'

        response = requests.get(url)
        response.raise_for_status()
        file_bytes = BytesIO(response.content)
        return file_bytes

import os
import requests
import zipfile
from pathlib import Path
from urllib.parse import unquote


class ModpackProcessor:
    def __init__(self, destination_folder):
        self.destination_folder = Path(destination_folder)
        self.destination_folder.mkdir(parents=True, exist_ok=True)

    def download_extract(self, zip_url, user_agent):
        # Get the modpack name from the zip URL
        modpack_name = Path(unquote(zip_url)).stem
        headers = {
            "User-Agent": user_agent
        }

        # Download the modpack zip file
        response = requests.get(zip_url, stream=True, headers=headers)
        zip_path = self.destination_folder / f"{modpack_name}"
        with open(zip_path, 'wb') as file:
            file.write(response.content)
        print("Modpack downloaded.")

        # Extract the zip file
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(self.destination_folder)
        print("Modpack extracted.")

        # Clean up zip file after extraction
        os.remove(zip_path)

        return self._locate_manifest_and_overrides(), modpack_name

    def _locate_manifest_and_overrides(self):
        manifest_path = None
        overrides_path = None
        for root, dirs, files in os.walk(self.destination_folder):
            if "modrinth.index.json" in files:
                manifest_path = Path(root) / "modrinth.index.json"
            if "overrides" in dirs:
                overrides_path = Path(root) / "overrides"
        return manifest_path, overrides_path

    def process_modpack(self, zip_url):
        (manifest_path, overrides_path), modpack_name = self.download_extract(zip_url, "KTrain5169/MC-Modpack-Downloader v1.0-develop | Python/3.11.9 | requests/2.32.3")

        if manifest_path is None:
            raise FileNotFoundError("modrinth.index.json not found.")

        # Return paths for further processing, even if overrides_path is None
        return manifest_path, overrides_path, modpack_name

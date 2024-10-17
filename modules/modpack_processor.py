import os
import requests
import zipfile
from pathlib import Path

class ModpackProcessor:
    def __init__(self, destination_folder):
        self.destination_folder = Path(destination_folder)
        self.destination_folder.mkdir(parents=True, exist_ok=True)

    def process_modpack(self, zip_url, status_callback=print):
        # Get the modpack name from the URL, and decode the name to avoid URL-encoded characters
        modpack_name = Path(zip_url).stem
        decoded_modpack_name = Path(modpack_name).name.replace("%2B", "+")  # Decode any URL-encoded characters
        target_folder = self.destination_folder / decoded_modpack_name

        # Download the modpack zip file
        response = requests.get(zip_url, stream=True)
        zip_path = self.destination_folder / f"{decoded_modpack_name}.mrpack"
        with open(zip_path, 'wb') as file:
            file.write(response.content)
        status_callback(f"Modpack downloaded to {zip_path}.")

        # Extract the zip file into the target folder
        target_folder.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(target_folder)
        status_callback(f"Modpack extracted to {target_folder}.")

        # Clean up zip file after extraction
        os.remove(zip_path)
    
        # Locate manifest and overrides
        manifest_path, overrides_path = self._locate_manifest_and_overrides(decoded_modpack_name)
        return manifest_path, overrides_path, decoded_modpack_name

    def _locate_manifest_and_overrides(self, modpack_name):
        manifest_path = None
        overrides_path = None
        destination_folder = self.destination_folder / modpack_name
    
        # Debug: Print out the full directory structure
        print(f"Searching for manifest and overrides in {destination_folder}")
        for root, dirs, files in os.walk(destination_folder):
            print(f"Found directory: {root}")
            for file in files:
                print(f"  File: {file}")
            for dir_name in dirs:
                print(f"  Directory: {dir_name}")

            if "modrinth.index.json" in files:
                manifest_path = Path(root) / "modrinth.index.json"
                print(f"Manifest found at: {manifest_path}")
            if "overrides" in dirs:
                overrides_path = Path(root) / "overrides"
                print(f"Overrides found at: {overrides_path}")

        return manifest_path, overrides_path


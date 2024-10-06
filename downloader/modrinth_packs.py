import requests
import shutil
import json
from pathlib import Path


class ModrinthProcessor:
    def process(self, manifest_path, overrides_path, destination_folder, modpack_name):
        # Create a subfolder with the modpack name
        destination_folder = Path(destination_folder) / modpack_name
        destination_folder.mkdir(parents=True, exist_ok=True)

        # Process the overrides folder, if it exists and is not None
        if overrides_path and overrides_path.exists():
            for item in overrides_path.iterdir():
                target_path = destination_folder / item.name
                if item.is_dir():
                    shutil.copytree(item, target_path, dirs_exist_ok=True)
                else:
                    shutil.copy2(item, target_path)
            print("Overrides folder contents copied.")
            # Remove the overrides folder after copying its contents
            shutil.rmtree(overrides_path)
            print("Overrides folder deleted.")

        # Process the Modrinth index file, if it exists
        if manifest_path and manifest_path.exists():
            with open(manifest_path, 'r') as manifest_file:
                manifest = json.load(manifest_file)

            for file in manifest['files']:
                mod_url = file['downloads'][0]
                mod_path = file.get('path')

                # Determine the target folder and file name from the 'path' key
                mod_file_path = destination_folder / mod_path
                mod_file_path.parent.mkdir(parents=True, exist_ok=True)

                # Request the mod file
                headers = {
                    "User-Agent": "KTrain5169/MC-Modpack-Downloader v1.0-develop | Python/3.11.9 | requests/2.32.3"
                }
                mod_response = requests.get(mod_url, headers=headers)
                with open(mod_file_path, 'wb') as mod_file:
                    mod_file.write(mod_response.content)
                print(f"Downloaded {mod_path} to {mod_file_path}")

            # Remove the manifest file after processing
            manifest_path.unlink()
            print("Modrinth index file deleted.")

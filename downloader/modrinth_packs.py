import requests
import shutil
import json
from pathlib import Path
from tkinter import messagebox


class ModrinthProcessor:
    def process(self, manifest_path, overrides_path, destination_folder, modpack_name, status_callback):
        destination_folder = Path(destination_folder) / modpack_name

        if destination_folder.exists():
            messagebox.showerror(
                "Error", f"The folder '{destination_folder}' already exists. Please delete it before trying again.")
            return

        destination_folder.mkdir(parents=True)
        status_callback(f"Created folder '{destination_folder}'.")

        if overrides_path and overrides_path.exists():
            for item in overrides_path.iterdir():
                target_path = destination_folder / item.name
                if item.is_dir():
                    if target_path.exists() and target_path.is_dir():
                        status_callback(
                            f"Merging contents into existing directory '{target_path}'.")
                        shutil.copytree(item, target_path, dirs_exist_ok=True)
                    else:
                        shutil.copytree(item, target_path)
                else:
                    shutil.copy2(item, target_path)
            status_callback("Overrides folder contents copied.")
            shutil.rmtree(overrides_path)
            status_callback("Overrides folder deleted.")

        # Process the Modrinth index file, if it exists
        if manifest_path and manifest_path.exists():
            with open(manifest_path, 'r') as manifest_file:
                manifest = json.load(manifest_file)

            # Loop through each file and download it to the appropriate location
            for file in manifest['files']:
                mod_url = file['downloads'][0]
                # Use the full path specified in the 'path' key
                mod_path = file.get('path', 'mods')

                # Determine the target folder and file name from the 'path' key
                mod_file_path = destination_folder / mod_path

                # Ensure the folder for the file exists
                mod_file_path.parent.mkdir(parents=True, exist_ok=True)

                # Check if the file already exists
                if mod_file_path.exists():
                    status_callback(
                        f"File {mod_file_path} already exists, skipping download.")
                    continue  # Skip the download if the file already exists

                # Request the mod file
                try:
                    mod_response = requests.get(mod_url)
                    if mod_response.status_code == 200:  # Check for successful response
                        with open(mod_file_path, 'wb') as mod_file:
                            mod_file.write(mod_response.content)
                        # Update status via callback
                        status_callback(
                            f"Downloaded {mod_path} to {mod_file_path}")
                    else:
                        status_callback(
                            f"Failed to download {mod_path}: {mod_response.status_code}")
                except Exception as e:
                    status_callback(f"Error downloading {mod_path}: {e}")

            # Remove the manifest file after processing
            manifest_path.unlink()
            status_callback("Modrinth index file deleted.")

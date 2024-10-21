import os
import requests
import zipfile
import shutil
import json
import hashlib
from pathlib import Path
from urllib.parse import unquote


headers = {
    "User-Agent": "unpacker/v1.0.0-develop | github.com/KTrain5169/unpacker"
}


class ModpackProcessor:
    def __init__(self, destination_folder, server_mode=False):
        self.destination_folder = Path(destination_folder)
        self.destination_folder.mkdir(parents=True, exist_ok=True)
        self.server_mode = server_mode

    def process_modpack(self, zip_url, status_callback=print):
        modpack_name = unquote(Path(zip_url).stem)
        target_folder = self.destination_folder / modpack_name

        # Download the modpack zip file
        message = f"Downloading modpack from: {zip_url}"
        print(message)
        status_callback(message)

        response = requests.get(zip_url, stream=True, headers=headers)
        if response.status_code != 200:
            message = "Failed to download modpack."
            print(message)
            status_callback(message)
            return None, None, None

        zip_path = self.destination_folder / f"{modpack_name}.mrpack"
        with open(zip_path, 'wb') as file:
            file.write(response.content)

        message = f"Modpack downloaded to: {zip_path}"
        print(message)
        status_callback(message)

        # Extract the zip file into the target folder
        target_folder.mkdir(parents=True, exist_ok=True)
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(target_folder)
            message = f"Modpack extracted to: {target_folder}"
            print(message)
            status_callback(message)
        except Exception as e:
            message = f"Error during extraction: {e}"
            print(message)
            status_callback(message)
            return None, None, None

        # Clean up zip file after extraction
        os.remove(zip_path)

        # Locate manifest and overrides
        manifest_path, overrides_path = self._locate_manifest_and_overrides(
            modpack_name)

        # Log found paths
        if manifest_path:
            print(f"Manifest file found at: {manifest_path}")
        if overrides_path:
            print(f"Overrides folder found at: {overrides_path}")

        # Process the mod files listed in the manifest
        if manifest_path:
            self.process_mods(manifest_path, target_folder, status_callback)

        # Process the files from overrides if present
        if overrides_path and overrides_path.exists():
            self.process_overrides(
                overrides_path, target_folder, status_callback)

        # Cleanup will only happen if we have found files
        if manifest_path or (overrides_path and overrides_path.exists()):
            self.cleanup(manifest_path, overrides_path,
                         target_folder, status_callback)
        else:
            print("No manifest or overrides found, skipping cleanup.")

        finish_message = "Finished unpacking, enjoy the pack!"
        status_callback(finish_message)

        return manifest_path, overrides_path, modpack_name

    def _locate_manifest_and_overrides(self, modpack_name):
        manifest_path = None
        overrides_path = None
        destination_folder = self.destination_folder / modpack_name

        print(f"Searching for manifest and overrides in {destination_folder}")
        for root, dirs, files in os.walk(destination_folder):
            if "modrinth.index.json" in files:
                manifest_path = Path(root) / "modrinth.index.json"
            if "overrides" in dirs:
                overrides_path = Path(root) / "overrides"

        return manifest_path, overrides_path

    def process_overrides(self, overrides_path, target_folder,
                          status_callback):
        for item in overrides_path.iterdir():
            target_path = target_folder / item.name
            if item.is_dir():
                # Copy the directory recursively
                shutil.copytree(item, target_path, dirs_exist_ok=True)
                status_callback(f"Copied directory: {item} to {target_path}")
            else:
                # Copy the file
                shutil.copy2(item, target_path)
                status_callback(f"Copied file: {item} to {target_path}")

    def process_mods(self, manifest_path, target_folder, status_callback):
        # Load the manifest
        with open(manifest_path, 'r') as f:
            manifest = json.load(f)

        # Process each file in the manifest
        for file in manifest['files']:
            # Check if we're in server mode
            if self.server_mode and file.get('env',
                                             {}).get(
                                                'server') == 'unsupported':
                status_callback(
                    f"Skipping server-unsupported mod: {file['path']}")
                continue

            # Otherwise, check if the mod is client-supported
            if not self.server_mode and file.get('env',
                                                 {}).get(
                                                    'client') == 'unsupported':
                status_callback(
                    f"Skipping client-unsupported mod: {file['path']}")
                continue

            # Construct the path where the mod should be downloaded
            mod_file_path = target_folder / file['path']
            mod_file_path.parent.mkdir(parents=True, exist_ok=True)

            # Download the mod file from the 'downloads' key
            download_url = file['downloads'][0]
            response = requests.get(download_url, stream=True)
            if response.status_code == 200:
                with open(mod_file_path, 'wb') as mod_file:
                    for chunk in response.iter_content(chunk_size=8192):
                        mod_file.write(chunk)

                # Verify the hash if provided
                self.verify_hashes(mod_file_path, file, status_callback)

                status_callback(
                 f"Downloaded and verified {file['path']} to {mod_file_path}")
            else:
                status_callback(f"Failed to download mod file: {file['path']}")

    def verify_hashes(self, mod_file_path, file, status_callback):
        # Verify the hash if provided
        sha1 = file.get('hashes', {}).get('sha1')
        sha512 = file.get('hashes', {}).get('sha512')

        if sha1:
            # Calculate SHA1
            hasher = hashlib.sha1()
            with open(mod_file_path, 'rb') as f:
                while chunk := f.read(8192):
                    hasher.update(chunk)
            calculated_sha1 = hasher.hexdigest()
            if calculated_sha1 != sha1:
                status_callback(f"SHA1 hash mismatch for {file['path']}!")

        if sha512:
            # Calculate SHA512
            hasher = hashlib.sha512()
            with open(mod_file_path, 'rb') as f:
                while chunk := f.read(8192):
                    hasher.update(chunk)
            calculated_sha512 = hasher.hexdigest()
            if calculated_sha512 != sha512:
                status_callback(f"SHA512 hash mismatch for {file['path']}!")

    def cleanup(self, manifest_path, overrides_path, target_folder,
                status_callback=print):
        # Remove the overrides folder if it exists
        if overrides_path and overrides_path.exists():
            shutil.rmtree(overrides_path)
            status_callback(f"Removed overrides folder: {overrides_path}")

        # Remove the manifest file if it exists
        if manifest_path and manifest_path.exists():
            manifest_path.unlink()
            status_callback(f"Removed manifest file: {manifest_path}")

        # Optionally remove the target folder if it's empty
        if not any(target_folder.iterdir()):
            target_folder.rmdir()
            status_callback(f"Removed empty folder: {target_folder}")

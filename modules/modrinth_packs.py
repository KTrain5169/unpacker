import requests
import shutil
import json
import hashlib
import threading
from pathlib import Path
from tkinter import messagebox
from io import BytesIO


class ModrinthProcessor:
    def __init__(self):
        self.search_results = []

    def search_modrinth(self, query, callback):
        """Searches Modrinth for modpacks matching the query and uses a callback to return results."""
        # Start a thread to perform the search
        search_thread = threading.Thread(target=self._perform_search, args=(query, callback))
        search_thread.start()

    def _perform_search(self, query, callback):
        """Performs the actual search request to the Modrinth API."""
        # Make the request to Modrinth's search endpoint
        try:
            response = requests.get(f"https://api.modrinth.com/v2/search?query={query}")
            if response.status_code == 200:
                data = response.json()
                self.search_results = [hit for hit in data["hits"] if hit["project_type"] == "modpack"]

                # Invoke the callback with the search results
                callback(self.search_results)
            else:
                callback(None)
                print(f"Failed to fetch results: {response.status_code}")
        except requests.RequestException as e:
            callback(None)
            print(f"An error occurred: {e}")

    def fetch_icon(self, icon_url):
        """Fetches the icon for a modpack and returns it as an Image."""
        try:
            response = requests.get(icon_url)
            if response.status_code == 200:
                return BytesIO(response.content)
            else:
                print(f"Failed to download icon: {response.status_code}")
                return None
        except requests.RequestException as e:
            print(f"Error fetching icon: {e}")
            return None

    def process(self, manifest_path, overrides_path, destination_folder, modpack_name, status_callback=print):
        # Ensure destination directory is set up
        destination_folder = Path(destination_folder) / modpack_name
        
        # Check for and handle the manifest file
        if manifest_path and manifest_path.exists():
            with open(manifest_path, 'r') as manifest_file:
                manifest = json.load(manifest_file)
                for file in manifest.get('files', []):
                    mod_url = file['downloads'][0]
                    mod_path = file.get('path', 'mods')
                    mod_file_path = destination_folder / mod_path
                    mod_file_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Download mod files
                    try:
                        mod_response = requests.get(mod_url)
                        if mod_response.status_code == 200:
                            with open(mod_file_path, 'wb') as mod_file:
                                mod_file.write(mod_response.content)
                            status_callback(f"Downloaded {mod_file_path}")
                        else:
                            status_callback(f"Failed to download {mod_file_path}: {mod_response.status_code}")
                    except Exception as e:
                        status_callback(f"Error downloading {mod_file_path}: {e}")
        else:
            status_callback("No manifest file found, skipping file downloads.")

        # Handle the overrides folder
        if overrides_path and overrides_path.exists():
            for item in overrides_path.iterdir():
                target_path = destination_folder / item.name
                if item.is_dir():
                    shutil.copytree(item, target_path, dirs_exist_ok=True)
                else:
                    shutil.copy2(item, target_path)
            status_callback("Overrides folder processed.")

        # Cleanup: remove the overrides folder and manifest file after processing
        if overrides_path and overrides_path.exists():
            shutil.rmtree(overrides_path)
            status_callback(f"Removed overrides folder: {overrides_path}")
        
        if manifest_path and manifest_path.exists():
            manifest_path.unlink()
            status_callback(f"Removed manifest file: {manifest_path}")


    def download_and_verify(self, mod_url, mod_file_path, expected_sha1, expected_sha512, status_callback):
        """Downloads the file and verifies its hash."""
        try:
            mod_response = requests.get(mod_url)
            if mod_response.status_code == 200:
                with open(mod_file_path, 'wb') as mod_file:
                    mod_file.write(mod_response.content)
                # Update status via callback
                status_callback(f"Downloaded {mod_file_path}.")

                # Verify the file hashes
                if not self.verify_hashes(mod_file_path, expected_sha1, expected_sha512):
                    status_callback(
                        f"Hash mismatch for {mod_file_path}! Expected SHA-1: {expected_sha1}, SHA-512: {expected_sha512}.")
                else:
                    status_callback(f"Verified hashes for {mod_file_path}.")
            else:
                status_callback(
                    f"Failed to download {mod_file_path}: {mod_response.status_code}")
        except Exception as e:
            status_callback(f"Error downloading {mod_file_path}: {e}")

    def verify_hashes(self, file_path, expected_sha1, expected_sha512):
        """Verifies the SHA-1 and SHA-512 hashes of the downloaded file against expected values."""
        hash_sha1 = hashlib.sha1()
        hash_sha512 = hashlib.sha512()

        # Read the file in chunks to avoid memory issues with large files
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha1.update(chunk)
                hash_sha512.update(chunk)

        # Calculate the file's hashes
        file_sha1 = hash_sha1.hexdigest()
        file_sha512 = hash_sha512.hexdigest()

        # Compare the calculated hashes with the expected ones
        return (file_sha1 == expected_sha1) and (file_sha512 == expected_sha512)

if __name__ == "__main__":
    print("Testing BytesIO...")
    try:
        data = BytesIO(b"test")
        print("BytesIO is working.")
    except NameError as e:
        print(f"NameError occurred: {e}")

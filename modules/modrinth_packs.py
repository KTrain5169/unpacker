import threading
import requests
from io import BytesIO


headers = {
    "User-Agent": "unpacker/v1.0.0-develop | github.com/KTrain5169/unpacker"
}


class ModrinthProcessor:
    def __init__(self):
        self.search_results = []

    def search_modrinth(self, query, callback):
        search_thread = threading.Thread(target=self._perform_search, args=(query, callback))
        search_thread.start()

    def _perform_search(self, query, callback):
        try:
            response = requests.get(f"https://api.modrinth.com/v2/search?query={query}", headers=headers)
            if response.status_code == 200:
                data = response.json()
                self.search_results = [hit for hit in data["hits"] if hit["project_type"] == "modpack"]
                callback(self.search_results)
            else:
                callback(None)
                print(f"Failed to fetch results: {response.status_code}")
        except requests.RequestException as e:
            callback(None)
            print(f"An error occurred: {e}")

    def get_modpack_version(self, project_id, callback):
        """Fetches the latest version data for a given project and retrieves the download URL."""
        try:
            response = requests.get(f"https://api.modrinth.com/v2/project/{project_id}/version", headers=headers)
            if response.status_code == 200:
                versions = response.json()
                if versions and versions[0]["files"]:
                    callback(versions[0]["files"][0]["url"])
                else:
                    callback(None)
            else:
                callback(None)
                print(f"Failed to fetch version data: {response.status_code}")
        except requests.RequestException as e:
            callback(None)
            print(f"An error occurred while fetching version data: {e}")

    def fetch_icon(self, icon_url):
        """Fetches the icon for a modpack and returns it as an Image."""
        try:
            response = requests.get(icon_url, headers=headers)
            if response.status_code == 200:
                return BytesIO(response.content)
            else:
                print(f"Failed to download icon: {response.status_code}")
                return None
        except requests.RequestException as e:
            print(f"Error fetching icon: {e}")
            return None

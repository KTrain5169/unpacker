import os
import requests
from pathlib import Path
from modules.modpack_processor import ModpackProcessor
from modules.modrinth_packs import ModrinthProcessor

def main():
    # Get modpack URL and output folder from the user
    modpack_url = input("Enter the Modpack URL: ")
    output_folder = input("Enter the Output Folder Path: ")

    # Check if output folder exists, create if not
    output_folder_path = Path(output_folder)
    if not output_folder_path.exists():
        output_folder_path.mkdir(parents=True, exist_ok=True)

    # Initialize processors
    modpack_processor = ModpackProcessor(output_folder)
    modrinth_processor = ModrinthProcessor()

    # Process the modpack download
    try:
        print("Downloading modpack...")
        manifest_path, overrides_path, modpack_name = modpack_processor.process_modpack(modpack_url, status_callback=print_status)
        print("Processing modpack files...")
        modrinth_processor.process(manifest_path, overrides_path, output_folder, modpack_name, status_callback=print_status)
        print("Modpack downloaded and processed successfully!")
    except Exception as e:
        print(f"An error occurred: {e}")

def print_status(message):
    print(message)

if __name__ == "__main__":
    main()

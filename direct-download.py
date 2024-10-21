import os
import argparse
from pathlib import Path
from modules.modpack_processor import ModpackProcessor


def main():
    # Set up argument parsing
    parser = argparse.ArgumentParser(
        description="Download and process a Minecraft modpack.")
    parser.add_argument('-u', '--url', type=str, help='Modpack download URL')
    parser.add_argument('-o', '--output', type=str,
                        help='Output folder path (default: current directory)')
    parser.add_argument('-s', '--server', action='store_true',
                        help="Enable Server mode (skip client-only mods)")

    # Parse the arguments
    args = parser.parse_args()

    # Determine modpack URL and output folder
    if args.url:
        modpack_url = args.url
        # If output folder is not provided, default to the CWD
        output_folder = args.output if args.output else os.getcwd()
    else:
        # Interactive mode: prompt the user for inputs if no args were given
        modpack_url = input("Enter the Modpack URL: ")
        output_folder = input(
            "Enter the Output Folder Path (or press Enter to use the current directory): ")
        # Default to current directory if no output folder was specified
        if not output_folder:
            output_folder = os.getcwd()

    # Check if output folder exists, create if not
    output_folder_path = Path(output_folder)
    if not output_folder_path.exists():
        output_folder_path.mkdir(parents=True, exist_ok=True)

    # Initialize the modpack processor with server mode
    modpack_processor = ModpackProcessor(
        output_folder, server_mode=args.server)

    # Process the modpack download
    try:
        print("Downloading modpack...")
        manifest_path, overrides_path, modpack_name = modpack_processor.process_modpack(
            modpack_url, status_callback=print_status)

        if manifest_path or overrides_path:
            pass
        else:
            print("Failed to locate manifest or overrides in the modpack.")
    except Exception as e:
        print(f"An error occurred: {e}")


def print_status(message):
    print(message)


if __name__ == "__main__":
    main()

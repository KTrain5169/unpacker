import tkinter as tk
from tkinter import filedialog, messagebox
import threading
from downloader.modpack_processor import ModpackProcessor
from downloader.modrinth_packs import ModrinthProcessor


class ModpackDownloaderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Minecraft Modpack Downloader")
        self.root.geometry("500x350")

        # Output folder variable
        self.output_folder = tk.StringVar()

        # URL entry label and field
        url_label = tk.Label(root, text="Modpack URL:")
        url_label.pack(pady=10)

        self.url_entry = tk.Entry(root, width=50)
        self.url_entry.pack(pady=5)

        # Output folder button
        output_folder_button = tk.Button(
            root, text="Select Output Folder", command=self.select_output_folder)
        output_folder_button.pack(pady=10)

        # Output folder label
        self.output_folder_label = tk.Label(root, text="No folder selected")
        self.output_folder_label.pack(pady=5)

        # Status label
        self.status_label = tk.Label(root, text="", fg="blue")
        self.status_label.pack(pady=10)

        # Go button
        go_button = tk.Button(root, text="Go!", bg="green", fg="white", font=(
            "Arial", 14), command=self.start_download)
        go_button.pack(pady=20)

    def select_output_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.output_folder.set(folder_selected)
            self.output_folder_label.config(
                text=f"Output folder: {folder_selected}")

    def start_download(self):
        url = self.url_entry.get()
        output_folder = self.output_folder.get()

        if not url:
            messagebox.showerror("Error", "Please enter a URL.")
            return
        if not output_folder:
            messagebox.showerror("Error", "Please select an output folder.")
            return

        # Start the download in a separate thread
        threading.Thread(target=self.download_modpack,
                         args=(url, output_folder)).start()

    def download_modpack(self, url, output_folder):
        self.update_status("Downloading modpack...")

        try:
            modpack_processor = ModpackProcessor(output_folder)
            manifest_path, overrides_path, modpack_name = modpack_processor.process_modpack(
                url)

            self.update_status("Processing modpack...")
            modrinth_processor = ModrinthProcessor()
            modrinth_processor.process(
                manifest_path, overrides_path, output_folder, modpack_name, self.update_status)

            self.update_status(
                "Modpack downloaded and processed successfully!")
        except Exception as e:
            self.update_status(f"An error occurred: {e}")

    def update_status(self, message):
        """Update the status label with the given message."""
        self.status_label.config(text=message)


if __name__ == "__main__":
    root = tk.Tk()
    app = ModpackDownloaderGUI(root)
    root.mainloop()

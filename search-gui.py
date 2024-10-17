from tkinter import Tk, Entry, Button, Label, ttk, messagebox, filedialog
from PIL import Image, ImageTk
from modules.modrinth_packs import ModrinthProcessor
from modules.modpack_processor import ModpackProcessor
import threading

class ModrinthSearchGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("unpacker - Modrinth Search")
        self.root.geometry("800x600")
        self.processor = ModrinthProcessor()
        self.modpack_processor = None  # Initialize in the download step

        # GUI setup for searching and displaying results
        Label(root, text="Search Modrinth for Modpacks:").pack(pady=5)
        self.search_entry = Entry(root, width=40)
        self.search_entry.pack(pady=5)
        Button(root, text="Search", command=self.start_search).pack(pady=5)

        # Dropdown for modpack selection
        self.modpack_dropdown = ttk.Combobox(root, state="readonly", width=50)
        self.modpack_dropdown.pack(pady=5)
        
        # Modpack info display
        self.modpack_title = Label(root, text="", font=("Arial", 14, "bold"))
        self.modpack_title.pack(pady=5)
        self.modpack_description = Label(root, text="", wraplength=500, justify="left")
        self.modpack_description.pack(pady=5)
        self.modpack_icon_label = Label(root)
        self.modpack_icon_label.pack(pady=5)

        # Button to download modpack
        Button(root, text="Select Output Folder", command=self.select_output_folder).pack(pady=5)
        self.output_folder_label = Label(root, text="No folder selected")
        self.output_folder_label.pack(pady=5)
        Button(root, text="Download Modpack", command=self.start_download).pack(pady=10)

        # Search results and output folder variables
        self.search_results = []
        self.selected_modpack_id = None
        self.output_folder = None

    def start_search(self):
        query = self.search_entry.get()
        if not query:
            messagebox.showwarning("Warning", "Please enter a search term.")
            return
        self.processor.search_modrinth(query, self.display_results)

    def display_results(self, results):
        if results:
            self.search_results = results
            modpack_names = [result["title"] for result in results]
            self.modpack_dropdown["values"] = modpack_names
            self.modpack_dropdown.current(0)
            self.modpack_dropdown.bind("<<ComboboxSelected>>", self.on_dropdown_select)
            self.on_dropdown_select(None)  # Show first result by default
        else:
            messagebox.showerror("Error", "No results found or an error occurred.")

    def on_dropdown_select(self, event):
        selection = self.modpack_dropdown.current()
        modpack = self.search_results[selection]
        self.modpack_title.config(text=modpack["title"])
        self.modpack_description.config(text=modpack["description"])
        self.selected_modpack_id = modpack["project_id"]

        # Fetch and display icon
        icon_url = modpack.get("icon_url")
        if icon_url:
            icon_data = self.processor.fetch_icon(icon_url)
            if icon_data:
                image = Image.open(icon_data)
                image = image.resize((100, 100), Image.LANCZOS)
                icon_photo = ImageTk.PhotoImage(image)
                self.modpack_icon_label.config(image=icon_photo)
                self.modpack_icon_label.image = icon_photo

    def select_output_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.output_folder = folder_selected
            self.output_folder_label.config(text=f"Output folder: {self.output_folder}")

    def start_download(self):
        if not self.output_folder:
            messagebox.showerror("Error", "Please select an output folder.")
            return
        if not self.selected_modpack_id:
            messagebox.showerror("Error", "Please select a modpack to download.")
            return

        # Fetch modpack download URL and start download
        self.processor.get_modpack_version(self.selected_modpack_id, self.download_modpack)

    def download_modpack(self, download_url):
        if download_url:
            # Use ModpackProcessor to handle the download and extraction
            self.modpack_processor = ModpackProcessor(self.output_folder)
            threading.Thread(
                target=self.modpack_processor.process_modpack,
                args=(download_url,)
            ).start()
        else:
            messagebox.showerror("Error", "Failed to retrieve download URL for the selected modpack.")

    def update_status(self, message):
        self.output_folder_label.config(text=message)

if __name__ == "__main__":
    root = Tk()
    app = ModrinthSearchGUI(root)
    root.mainloop()

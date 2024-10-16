import tkinter as tk
from tkinter import ttk, messagebox
import requests
from io import BytesIO
from PIL import Image, ImageTk

class ModrinthSearchGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Modrinth Modpack Search")
        self.root.geometry("600x400")

        # Modrinth Search Section
        tk.Label(root, text="Search Modrinth for Modpacks:").pack(pady=5)
        self.search_entry = tk.Entry(root, width=40)
        self.search_entry.pack(pady=5)
        
        search_button = tk.Button(root, text="Search", command=self.search_modrinth)
        search_button.pack(pady=5)

        # Modpack Selection Dropdown
        self.modpack_var = tk.StringVar(root)
        self.modpack_dropdown = ttk.Combobox(root, textvariable=self.modpack_var, state="readonly", width=50)
        self.modpack_dropdown.pack(pady=5)

        # Modpack Information Display
        self.modpack_title = tk.Label(root, text="", font=("Arial", 14, "bold"))
        self.modpack_title.pack(pady=5)

        self.modpack_description = tk.Label(root, text="", wraplength=500, justify="left")
        self.modpack_description.pack(pady=5)

        self.modpack_icon_label = tk.Label(root)
        self.modpack_icon_label.pack(pady=5)

        # Placeholder for search results
        self.search_results = []

    def search_modrinth(self):
        query = self.search_entry.get()
        if not query:
            messagebox.showwarning("Warning", "Please enter a search term.")
            return

        # Fetch results from Modrinth API
        response = requests.get(f"https://api.modrinth.com/v2/search?query={query}")
        if response.status_code == 200:
            data = response.json()
            self.search_results = [hit for hit in data["hits"] if hit["project_type"] == "modpack"]

            if not self.search_results:
                messagebox.showinfo("Info", "No modpacks found.")
                return

            # Populate dropdown with modpack names
            modpack_names = [result["title"] for result in self.search_results]
            self.modpack_dropdown["values"] = modpack_names
            self.modpack_dropdown.current(0)  # Select first modpack by default

            # Display details of the first modpack
            self.display_modpack_info(0)
            self.modpack_dropdown.bind("<<ComboboxSelected>>", self.on_modpack_select)
        else:
            messagebox.showerror("Error", f"Failed to fetch results: {response.status_code}")

    def on_modpack_select(self, event):
        selection = self.modpack_dropdown.current()
        self.display_modpack_info(selection)

    def display_modpack_info(self, index):
        if not self.search_results:
            return

        modpack = self.search_results[index]
        self.modpack_title.config(text=modpack["title"])
        self.modpack_description.config(text=modpack["description"])

        # Fetch and display the icon
        icon_url = modpack.get("icon_url")
        if icon_url:
            response = requests.get(icon_url)
            if response.status_code == 200:
                image_data = BytesIO(response.content)
                icon_image = Image.open(image_data)
                icon_image = icon_image.resize((100, 100), Image.ANTIALIAS)
                self.icon_photo = ImageTk.PhotoImage(icon_image)
                self.modpack_icon_label.config(image=self.icon_photo)

if __name__ == "__main__":
    root = tk.Tk()
    app = ModrinthSearchGUI(root)
    root.mainloop()

from tkinter import Tk, Entry, Button, Label, ttk, messagebox, StringVar
from PIL import Image, ImageTk
from modules.modrinth_packs import ModrinthProcessor


class ModrinthSearchGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("unpacker - Modrinth Search")
        self.root.geometry("800x600")
        self.processor = ModrinthProcessor()

        # Search UI elements
        Label(root, text="Search Modrinth for Modpacks:").pack(pady=5)
        self.search_entry = Entry(root, width=40)
        self.search_entry.pack(pady=5)
        Button(root, text="Search", command=self.start_search).pack(pady=5)

        # Dropdown for search results
        self.modpack_var = StringVar(root)
        self.modpack_dropdown = ttk.Combobox(root, textvariable=self.modpack_var, state="readonly", width=50)
        self.modpack_dropdown.pack(pady=5)

        # Display area for modpack details
        self.modpack_title = Label(root, text="", font=("Arial", 14, "bold"))
        self.modpack_title.pack(pady=5)
        self.modpack_description = Label(root, text="", wraplength=500, justify="left")
        self.modpack_description.pack(pady=5)
        self.modpack_icon_label = Label(root)
        self.modpack_icon_label.pack(pady=5)

        # Search results storage
        self.search_results = []

    def start_search(self):
        query = self.search_entry.get()
        if not query:
            messagebox.showwarning("Warning", "Please enter a search term.")
            return
        # Start the search in a background thread
        self.processor.search_modrinth(query, self.display_results)

    def display_results(self, results):
        if results:
            self.search_results = results
            modpack_names = [result["title"] for result in results]
            self.modpack_dropdown["values"] = modpack_names
            self.modpack_dropdown.current(0)
            self.on_modpack_select(0)
            self.modpack_dropdown.bind("<<ComboboxSelected>>", self.on_dropdown_select)
        else:
            messagebox.showerror("Error", "No results found or an error occurred.")

    def on_dropdown_select(self, event):
        selection = self.modpack_dropdown.current()
        self.on_modpack_select(selection)

    def on_modpack_select(self, index):
        modpack = self.search_results[index]
        self.modpack_title.config(text=modpack["title"])
        self.modpack_description.config(text=modpack["description"])
        icon_url = modpack.get("icon_url")
        
        if icon_url:
            icon_data = self.processor.fetch_icon(icon_url)
            if icon_data:
                image = Image.open(icon_data)
                image = image.resize((100, 100), Image.LANCZOS)
                icon_photo = ImageTk.PhotoImage(image)
                self.modpack_icon_label.config(image=icon_photo)
                self.modpack_icon_label.image = icon_photo  # Keep a reference to prevent GC

if __name__ == "__main__":
    root = Tk()
    app = ModrinthSearchGUI(root)
    root.mainloop()

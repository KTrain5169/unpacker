from downloader.modpack_processor import ModpackProcessor
from downloader.modrinth_packs import ModrinthProcessor

modpack_processor = ModpackProcessor("downloaded-mrpacks")

manifest_path, overrides_path, modpack_name = modpack_processor.process_modpack(str(input("Paste the link to the mrpack file here: ")))

modrinth_processor = ModrinthProcessor()

modrinth_processor.process(manifest_path, overrides_path, "downloaded-mrpacks",
                           modpack_name)

# unpacker - a Minecraft modpack extractor

This is a "simple" modpack downloader & extractor for Minecraft, written in Python.

## Supported formats

Currently, the only supported pack specification is Modrinth's mrpack format, but support for CurseForge modpacks *might* come at a later date.
Other pack forms may be considered.

## How does this work?

Modrinth's `mrpack` format is just a `zip` file with a renamed extension. So, the program downloads the `mrpack` file and extracts it like a `zip` file.
Afterwards, the program reads the `modrinth.index.json` file, which contains links to download projects in the pack. It's why modpacks are so light, because they are (usually) links instead of actual mods.

If the modpack contains an `overrides` folder, which may be the case for most modpacks, it will also copy over the `overrides/` contents.

Lastly, it will delete the `overrides/` and `modrinth.index.json` directory/file, as it's not needed after this.

You can now drag the folders into your instance!

## What security measures are put to ensure the files are the correctly downloaded projects?

Great question! This program (as of the time of writing this, at least) ~~has no checks for now. However, Modrinth's JSON file has both SHA1 and SHA256 values of the projects in the pack. Adding a file hash checker that checks both the SHA values to ensure legitimacy could be good for mod security, and is something I'm interested in adding to the downloader module.~~

Update: The program now has support for ensuring modpack dependency integrity (i.e. the projects in the modpack). SHA-1 and SHA-512 are the only values, since they are required in a `modrinth.index.json`.

## Should I use this?

Absolutely... not! If you can, try to use a third-party launcher instead. (For `mrpack` packs, you can use [Prism](https://prismlauncher.org), [Modrinth](https://modrinth.com/app) or [ATLauncher](https://atlauncher.com), all open-source.) This was more a project for fun and shouldn't be taken seriously *for now*.

## CLI usage

The direct-download script can also double as a CLI app. Here are the commands for it:

* --url (-u for short) - Specifies the download URL.
* --output (-o for short) - Specifies the output directory. If omitted but --url or -u is used, it will download into the current working directory instead.

# CLAUDE.md — orientation for AI-assisted sessions

## What this project is
A local Flask app for importing photos from a Pixel phone and managing a personal photo library.
See README.md for the full workflow diagram and feature roadmap.

## Key design decisions (not obvious from the code)

**UUID filenames are intentional.** Losing the original filename is a feature — it obscures
capture date and sequence. Do not "fix" this or suggest preserving original names.

**Copyright name is hardcoded.** `COPYRIGHT_NAME = "Matt Daniel"` in `metadata_tools.py`.
This is correct; it is not a placeholder.

**pyexiv2 must come from apt, not pip.** It is a native extension that links against libexiv2.
The venv is created with `--system-site-packages` specifically to reach the apt-installed package.
Do not attempt `pip install py3exiv2` — it will fail or produce a broken install.
The apt package is `python3-py3exiv2`.

**catalog.db is a dedup guard, not a library manager.** The `original_cksum UNIQUE` constraint
prevents re-importing the same file across multiple runs. It is not a full media database;
DigiKam manages the actual library metadata.

**Watermark runs before copyright metadata write.** In `import_media.py`, `apply_watermark()`
is called before `add_copyright_metadata()` so that pyexiv2 has the final word on EXIF tags.

**Photo Stream sync uses a DigiKam XMP tag.** `sync_lib.py` looks for files tagged with
`"Photo Stream"` in `Xmp.digiKam.TagsList`. This tag must be applied inside DigiKam.

## Resilio Sync integration (in progress)
Two sync folders are planned:
- `media_in/Camera` ← phone DCIM (one-way archive, Resilio handles transport)
- `photo_stream/` ↔ phone PhotoStream (two-way, conflict resolution via `conflict_resolver.py`)

Resilio conflict files are named: `<uuid> (<device>'s conflicted copy YYYY-MM-DD HH-MM-SS).<ext>`
The resolver keeps whichever version has the later modification timestamp.

## Module map
| File | Purpose |
|------|---------|
| `app.py` | Flask app — all routes |
| `import_media.py` | Core import logic (copy, rename, checksum, dedup) |
| `metadata_tools.py` | EXIF/IPTC read/write via pyexiv2 |
| `watermark_utils.py` | Pillow-based text watermark (lower-right corner) |
| `sync_lib.py` | Bidirectional sync of Photo Stream tagged files |
| `conflict_resolver.py` | Resolves Resilio Sync conflict files (newer wins) |
| `catalog_utils.py` | catalog.db creation and dedup |
| `UUID_namer.py` | UUID filename generation and validation |
| `lib_organiser.py` | One-off tool to reorganise an existing flat photo dump into YYYY/MM/ |
| `start.sh` | Checks system deps, creates venv, starts Flask |

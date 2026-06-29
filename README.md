# Media Manager

A local Flask app for importing, organising, and syncing a personal photo library.

## Directory structure

```
~/Pictures/
└── Media Manager/          ← created automatically on first run
    ├── Photo In/           ← Resilio 2-way sync with phone DCIM/Camera
    └── Photo Stream/       ← processed library (DigiKam scans here)
        ├── catalog.db
        ├── 2025/
        │   └── 06/
        │       └── <uuid>.jpg
        └── 2026/
            └── ...
```

## Workflow overview

```
Pixel phone
    │
    │  Resilio Sync (always-on, WiFi)
    │  DCIM/Camera  ◄──────────────►  Photo In/       (2-way — delete from Photo In
    │  PhotoStream  ◄───────────────►  Photo Stream/   propagates back to phone DCIM)
    │
    ▼
[Flask app — Import]
    Photo In/ ──► Photo Stream/YYYY/MM/<uuid>.jpg
                  + UUID rename
                  + EXIF/IPTC copyright metadata
                  + optional watermark
                  + optional DigiKam "Photo Stream" XMP tag
```

## Running

```bash
./start.sh
```

`start.sh` checks system dependencies, creates the Python venv if needed, installs pip packages,
and starts the app at http://127.0.0.1:5000.

### System dependencies (apt)

```bash
sudo apt install python3-py3exiv2 python3-venv python3-full
```

## Features

### Import
Copy photos from a source directory (e.g. Resilio staging folder) into the library.
- Renames files to UUID hex names (obscures capture date and sequence)
- Organises into `YYYY/MM/` subdirectories using EXIF date
- Writes copyright metadata (EXIF + IPTC) — `© YYYY Matt Daniel`
- Optionally applies a visible watermark (© text, lower-right corner)
- Deduplication via checksum — re-importing the same file is a no-op

### Sync Library
Syncs files tagged **Photo Stream** in DigiKam between two local directories.
Bidirectional: newer modification time wins. Intended as the mechanism to populate
the `photo_stream/` export folder before Resilio delivers it to the phone.

### Resolve Conflicts
Cleans up Resilio Sync conflict files in the photo stream folder.
Resilio names conflicts: `<uuid> (<device>'s conflicted copy YYYY-MM-DD HH-MM-SS).<ext>`
This tool compares modification timestamps and keeps the newer version.
Run in dry-run mode first (default) to preview before applying.

---

## Roadmap

### Phase 1 — Conflict resolution ✓
Detect and resolve Resilio Sync conflict files in the photo stream directory.
Newer modification time wins; loser is discarded. Available as both a Flask
page and a standalone CLI (`python conflict_resolver.py <dir> [--apply]`).

### Phase 2 — Photo Stream push
Wire the existing `sync_lib.py` Photo Stream sync into the Flask UI.
Add a dedicated **Photo Stream** page with:
- Push: copy DigiKam-tagged images from the library into `photo_stream/`
  (Resilio then delivers them to the phone automatically)
- Pull preview: show what would change before committing

### Phase 3 — Integrated phone sync cycle
Combine the above into a single "Sync with phone" operation:
1. Resolve any outstanding conflicts in `photo_stream/`
2. Pull new photos from `media_in/Camera` into the library (import)
3. Push updated Photo Stream export to `photo_stream/` (Resilio delivers)

This makes the full cycle a single button press. Resilio handles all
transport; the app handles all logic.

### Phase 4 — Sync status dashboard
Show current state at a glance:
- How many unimported files are waiting in `media_in/Camera`
- How many conflicts are pending in `photo_stream/`
- Last sync timestamps
- Resilio folder status (if Resilio exposes a local API)

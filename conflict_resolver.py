"""
Resolves Resilio Sync conflict files in a photo stream directory.

When both sides edit the same UUID-named file, Resilio renames the
losing version to:
    <uuid> (<device>'s conflicted copy YYYY-MM-DD HH-MM-SS).<ext>

This module finds those pairs and keeps whichever version has the
later modification timestamp, discarding the older one.
"""

import os
import re
from datetime import datetime

from metadata_tools import get_modified_time

# Matches: "<uuid> (anything containing 'conflicted copy').<ext>"
_CONFLICT_RE = re.compile(
    r'^([0-9a-f]{32}) \(.*conflicted copy.*\)(\.[^.]+)$',
    re.IGNORECASE,
)

_IMAGE_EXTS = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}


def _mod_time(path):
    try:
        return get_modified_time(path)
    except Exception:
        return datetime.fromtimestamp(os.path.getmtime(path))


def find_conflicts(directory):
    """
    Walk directory and return a list of (original_path, conflict_path) pairs.
    Only yields pairs where the original file also exists.
    """
    pairs = []
    for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if d[0] != '.']
        files[:] = [f for f in files if f[0] != '.']
        for filename in files:
            m = _CONFLICT_RE.match(filename)
            if not m:
                continue
            ext = m.group(2).lower()
            if ext not in _IMAGE_EXTS:
                continue
            original = os.path.join(root, m.group(1) + m.group(2))
            conflict = os.path.join(root, filename)
            pairs.append((original, conflict))
    return pairs


def resolve_conflict(original, conflict, dry_run=False):
    """
    Resolve a single conflict pair. Returns a human-readable result string.

    Rules:
    - If original is missing: promote conflict (rename it to original path).
    - If both exist: keep whichever has the later mod time; delete the other.
    - Equal timestamps: keep original, delete conflict (no-op preference).
    """
    orig_exists = os.path.exists(original)
    conf_exists = os.path.exists(conflict)

    if not conf_exists:
        return f"SKIP  (conflict file already gone): {os.path.basename(conflict)}"

    if not orig_exists:
        if not dry_run:
            os.rename(conflict, original)
        return f"PROMOTE  {os.path.basename(conflict)} → {os.path.basename(original)}"

    orig_ts = _mod_time(original)
    conf_ts = _mod_time(conflict)
    delta = abs((conf_ts - orig_ts).total_seconds())
    delta_str = f"{delta:.0f}s"

    if conf_ts > orig_ts:
        if not dry_run:
            os.replace(conflict, original)
        return f"KEEP CONFLICT  (newer by {delta_str}): {os.path.basename(original)}"
    else:
        if not dry_run:
            os.remove(conflict)
        return f"KEEP ORIGINAL  (newer by {delta_str}): {os.path.basename(original)}"


def resolve_all(directory, dry_run=True):
    """
    Find and resolve all conflicts under directory.
    Returns (conflict_count, list_of_result_strings).
    """
    pairs = find_conflicts(directory)
    results = []
    for original, conflict in pairs:
        results.append(resolve_conflict(original, conflict, dry_run=dry_run))
    return len(pairs), results


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Resolve Resilio Sync conflicts')
    parser.add_argument('directory', help='Photo stream directory to scan')
    parser.add_argument('--apply', action='store_true', help='Actually resolve (default is dry run)')
    args = parser.parse_args()

    count, results = resolve_all(args.directory, dry_run=not args.apply)
    mode = 'DRY RUN' if not args.apply else 'APPLIED'
    print(f"[{mode}] {count} conflict(s) found in {args.directory}")
    for r in results:
        print(f"  {r}")

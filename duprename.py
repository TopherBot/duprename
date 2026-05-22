#!/usr/bin/env python3
"""duprename – Auto‑rename duplicate filenames in a directory.

Usage:
    duprename [--dry-run] [directory]

If no directory is given, the current working directory is used.
"""
import argparse
import os
import sys
from collections import defaultdict

def generate_new_name(original_path, existing_names):
    """Return a new unique filename for *original_path*.

    *existing_names* is a set of filenames already present in the target
    directory (case‑insensitive).  The function appends `` (n)`` before the
    file extension, incrementing *n* until the name is unique.
    """
    dirname, basename = os.path.split(original_path)
    name, ext = os.path.splitext(basename)
    i = 1
    while True:
        new_basename = f"{name} ({i}){ext}"
        candidate = os.path.join(dirname, new_basename)
        if candidate.lower() not in existing_names:
            return candidate
        i += 1

def process_directory(root, dry_run=False):
    # Gather files (non‑recursive) and detect duplicates (case‑insensitive)
    files = [os.path.join(root, f) for f in os.listdir(root) if os.path.isfile(os.path.join(root, f))]
    name_map = defaultdict(list)  # lower‑case name -> list of paths
    for f in files:
        name_map[os.path.basename(f).lower()].append(f)

    # Prepare a set of all existing filenames (lower‑case) for quick lookup
    existing = {os.path.basename(p).lower() for p in files}

    actions = []
    for lower_name, paths in name_map.items():
        if len(paths) <= 1:
            continue  # no duplicate
        # Keep the first occurrence unchanged; rename the rest
        for original in paths[1:]:
            new_path = generate_new_name(original, existing)
            actions.append((original, new_path))
            # Update the set so later generations avoid collisions
            existing.add(os.path.basename(new_path).lower()
)
    # Execute or report actions
    if not actions:
        print("No duplicate filenames found.")
        return
    for src, dst in actions:
        if dry_run:
            print(f"[DRY‑RUN] Would rename: {src} -> {dst}")
        else:
            print(f"Renaming: {src} -> {dst}")
            os.rename(src, dst)

def parse_args():
    parser = argparse.ArgumentParser(description="Auto‑rename duplicate files in a directory.")
    parser.add_argument(
        "directory",
        nargs="?",
        default=".",
        help="Target directory (default: current working directory)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be renamed without performing any changes",
    )
    return parser.parse_args()

def main():
    args = parse_args()
    target = os.path.abspath(args.directory)
    if not os.path.isdir(target):
        print(f"Error: '{target}' is not a directory", file=sys.stderr)
        sys.exit(1)
    process_directory(target, dry_run=args.dry_run)

if __name__ == "__main__":
    main()

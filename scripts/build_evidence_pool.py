#!/usr/bin/env python3
"""Build the city-council-meetings-2026 evidence pool.

Processes 7 VTT transcripts and 9 TXT agendas into normalized markdown source files.
"""

import hashlib
import os
import re
import subprocess
import sys

BASE_DIR = "/Users/cristos/Documents/projects/2026-south-portland-school-budget"
POOL_DIR = os.path.join(BASE_DIR, "docs/evidence-pools/city-council-meetings-2026")
SOURCES_DIR = os.path.join(POOL_DIR, "sources")
DATA_DIR = os.path.join(BASE_DIR, "data/city-council/meetings")
PARSER_SCRIPT = os.path.join(BASE_DIR, "scripts/parse_vtt.py")

# VTT transcripts: (source_id, filename, date_dir, title)
VTT_SOURCES = [
    ("001", "001-council-meeting-2026-01-06.md", "2026-01-06",
     "City Council Regular Meeting — January 6, 2026"),
    ("002", "002-council-workshop-2026-01-13.md", "2026-01-13",
     "City Council Workshop — January 13, 2026"),
    ("003", "003-council-meeting-2026-01-20.md", "2026-01-20",
     "City Council Regular Meeting — January 20, 2026"),
    ("004", "004-council-meeting-2026-02-03.md", "2026-02-03",
     "City Council Regular Meeting — February 3, 2026"),
    ("005", "005-council-workshop-2026-02-10.md", "2026-02-10",
     "City Council Workshop — February 10, 2026"),
    ("006", "006-council-meeting-2026-02-17.md", "2026-02-17",
     "City Council Regular Meeting — February 17, 2026"),
    ("007", "007-council-meeting-2026-03-05.md", "2026-03-05",
     "City Council Regular Meeting — March 5, 2026"),
]

# TXT agendas: (source_id, filename, date_dir, title)
TXT_SOURCES = [
    ("008", "008-council-agenda-2026-01-06.md", "2026-01-06",
     "City Council Agenda — January 6, 2026"),
    ("009", "009-council-agenda-2026-01-13.md", "2026-01-13",
     "City Council Agenda — January 13, 2026"),
    ("010", "010-council-agenda-2026-01-15.md", "2026-01-15",
     "City Council Goal Setting Workshop Agenda — January 15, 2026"),
    ("011", "011-council-agenda-2026-01-20.md", "2026-01-20",
     "City Council Agenda — January 20, 2026"),
    ("012", "012-council-agenda-2026-02-03.md", "2026-02-03",
     "City Council Agenda — February 3, 2026"),
    ("013", "013-council-agenda-2026-02-10.md", "2026-02-10",
     "City Council Agenda — February 10, 2026"),
    ("014", "014-council-agenda-2026-02-17.md", "2026-02-17",
     "City Council Agenda — February 17, 2026"),
    ("015", "015-council-agenda-2026-03-05.md", "2026-03-05",
     "City Council Agenda — March 5, 2026"),
    ("016", "016-council-agenda-2026-03-10.md", "2026-03-10",
     "City Council Agenda — March 10, 2026"),
]


def sha256_file(filepath):
    """Compute SHA-256 hash of a file."""
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def relative_path(filepath):
    """Convert absolute path to relative from BASE_DIR."""
    return os.path.relpath(filepath, BASE_DIR)


def process_vtt(source_id, out_filename, date_dir, title):
    """Process a VTT transcript into a normalized markdown file."""
    vtt_path = os.path.join(DATA_DIR, date_dir, "transcript.en-x-autogen.vtt")
    rel_path = relative_path(vtt_path)
    file_hash = sha256_file(vtt_path)

    # Run the parser
    result = subprocess.run(
        [sys.executable, PARSER_SCRIPT, vtt_path],
        capture_output=True, text=True, check=True
    )
    lines = result.stdout.strip().split("\n")
    duration = lines[0]  # HH:MM:SS
    transcript_text = "\n".join(lines[1:]).strip()

    frontmatter = f"""---
source-id: "{source_id}"
title: "{title}"
type: media
path: "{rel_path}"
fetched: 2026-03-09T00:00:00Z
hash: "sha256:{file_hash}"
duration: "{duration}"
speakers: []
notes: "Auto-generated Vimeo captions. May contain transcription errors."
---"""

    body = f"""
# {title}

**Duration:** {duration}
**Source:** Auto-generated Vimeo captions (VTT)

## Transcript

{transcript_text}
"""

    out_path = os.path.join(SOURCES_DIR, out_filename)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(frontmatter + "\n" + body)

    print(f"  [VTT] {out_filename} ({duration}, {len(lines)-1} groups)")
    return {
        "source_id": source_id,
        "title": title,
        "type": "media",
        "path": rel_path,
        "hash": f"sha256:{file_hash}",
        "duration": duration,
        "out_file": out_filename,
    }


def process_txt(source_id, out_filename, date_dir, title):
    """Process a TXT agenda into a normalized markdown file."""
    txt_path = os.path.join(DATA_DIR, date_dir, "agenda.txt")
    rel_path = relative_path(txt_path)
    file_hash = sha256_file(txt_path)

    with open(txt_path, "r", encoding="utf-8") as f:
        content = f.read()

    frontmatter = f"""---
source-id: "{source_id}"
title: "{title}"
type: local
path: "{rel_path}"
fetched: 2026-03-09T00:00:00Z
hash: "sha256:{file_hash}"
---"""

    out_path = os.path.join(SOURCES_DIR, out_filename)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(frontmatter + "\n\n" + content)

    print(f"  [TXT] {out_filename} ({len(content.splitlines())} lines)")
    return {
        "source_id": source_id,
        "title": title,
        "type": "local",
        "path": rel_path,
        "hash": f"sha256:{file_hash}",
        "out_file": out_filename,
    }


def build_manifest(all_sources):
    """Build manifest.yaml."""
    lines = [
        "pool: city-council-meetings-2026",
        "created: 2026-03-09",
        "refreshed: 2026-03-09",
        "tags:",
        "  - city-council",
        "  - meetings",
        "  - budget",
        "  - governance",
        "  - south-portland",
        "  - agendas",
        "freshness-ttl:",
        "  media: never",
        "  local: never",
        "",
        "sources:",
    ]

    for s in all_sources:
        lines.append(f'  - source-id: "{s["source_id"]}"')
        lines.append(f'    title: "{s["title"]}"')
        lines.append(f'    type: {s["type"]}')
        lines.append(f'    path: "{s["path"]}"')
        lines.append(f'    hash: "{s["hash"]}"')
        lines.append(f'    file: "sources/{s["out_file"]}"')
        if "duration" in s:
            lines.append(f'    duration: "{s["duration"]}"')
        lines.append("")

    manifest_path = os.path.join(POOL_DIR, "manifest.yaml")
    with open(manifest_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"\n  Manifest written: {manifest_path}")


def main():
    os.makedirs(SOURCES_DIR, exist_ok=True)

    all_sources = []

    print("Processing VTT transcripts...")
    for sid, fname, date_dir, title in VTT_SOURCES:
        info = process_vtt(sid, fname, date_dir, title)
        all_sources.append(info)

    print("\nProcessing TXT agendas...")
    for sid, fname, date_dir, title in TXT_SOURCES:
        info = process_txt(sid, fname, date_dir, title)
        all_sources.append(info)

    print("\nBuilding manifest...")
    build_manifest(all_sources)

    print("\nDone! All 16 sources processed.")


if __name__ == "__main__":
    main()

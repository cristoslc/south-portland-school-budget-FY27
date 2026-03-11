#!/usr/bin/env python3
"""Vimeo VTT Connector — download auto-generated captions from SPC-TV videos.

Uses yt-dlp to fetch VTT subtitle files. No API token required.

Usage:
    python3 scripts/connectors/vimeo.py                  # download all missing VTTs
    python3 scripts/connectors/vimeo.py --check-only     # list what would be downloaded
    python3 scripts/connectors/vimeo.py --vimeo-id ID    # process a single video
    python3 scripts/connectors/vimeo.py --discover        # find and add new channel videos
"""

import argparse
import json
import logging
import os
import re
import subprocess
import sys
import tempfile
import shutil

import yaml

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("vimeo-connector")

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))
DEFAULT_CONFIG = os.path.join(SCRIPT_DIR, "vimeo-sources.yaml")

# Channel URL template — the /videos page is a playlist yt-dlp can enumerate
CHANNEL_URL = "https://vimeo.com/{channel}/videos"


def load_config(config_path):
    """Load and validate the sources config. Returns the full config dict."""
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    sources = config.get("sources", [])
    if not sources:
        log.warning("No sources found in config file")
    return config


def check_yt_dlp():
    """Verify yt-dlp is available."""
    if not shutil.which("yt-dlp"):
        log.error("yt-dlp not found on PATH. Install with: brew install yt-dlp")
        sys.exit(1)


def download_vtt(vimeo_id, output_path):
    """Download VTT captions for a single Vimeo video.

    Returns True on success, False on failure.
    """
    output_dir = os.path.dirname(output_path)
    os.makedirs(output_dir, exist_ok=True)

    # yt-dlp writes to a pattern-based filename; we use a temp dir and move
    with tempfile.TemporaryDirectory() as tmpdir:
        cmd = [
            "yt-dlp",
            "--write-sub",
            "--sub-lang", "en-x-autogen",
            "--sub-format", "vtt",
            "--skip-download",
            "--no-warnings",
            "-o", os.path.join(tmpdir, "video.%(ext)s"),
            f"https://vimeo.com/{vimeo_id}",
        ]

        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=60
            )
        except subprocess.TimeoutExpired:
            log.error("Timeout downloading VTT for Vimeo ID %s", vimeo_id)
            return False

        if result.returncode != 0:
            stderr = result.stderr.strip()
            if "no subtitles" in stderr.lower() or "no subtitle" in stderr.lower():
                log.warning("No auto-generated captions for Vimeo ID %s", vimeo_id)
            else:
                log.error(
                    "yt-dlp failed for Vimeo ID %s (exit %d): %s",
                    vimeo_id, result.returncode, stderr[:200],
                )
            return False

        # Find the downloaded VTT file
        vtt_files = [f for f in os.listdir(tmpdir) if f.endswith(".vtt")]
        if not vtt_files:
            log.warning("No VTT file produced for Vimeo ID %s", vimeo_id)
            return False

        shutil.move(os.path.join(tmpdir, vtt_files[0]), output_path)
        return True


def discover_channel(channel_id):
    """List all videos on a Vimeo channel using yt-dlp.

    Returns a list of dicts with keys: id, title, upload_date.
    """
    url = CHANNEL_URL.format(channel=channel_id)
    cmd = [
        "yt-dlp",
        "--flat-playlist",
        "--dump-json",
        "--no-warnings",
        url,
    ]

    log.info("Discovering videos on channel: %s", channel_id)
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    except subprocess.TimeoutExpired:
        log.error("Timeout listing channel %s", channel_id)
        return []

    if result.returncode != 0:
        log.error("yt-dlp channel listing failed: %s", result.stderr.strip()[:300])
        return []

    videos = []
    for line in result.stdout.strip().split("\n"):
        if not line.strip():
            continue
        try:
            data = json.loads(line)
            videos.append({
                "id": str(data.get("id", "")),
                "title": data.get("title", ""),
                "upload_date": data.get("upload_date", ""),  # YYYYMMDD
            })
        except json.JSONDecodeError:
            continue

    log.info("Found %d video(s) on channel", len(videos))
    return videos


def infer_metadata(video):
    """Infer meeting type, subtype, date, and output path from video metadata.

    Returns a dict with keys: vimeo_id, type, subtype, date, output.
    """
    title = video.get("title", "").lower()
    vimeo_id = video["id"]

    # Infer meeting type from title
    if "school board" in title or "school dept" in title or "school department" in title:
        meeting_type = "school-board"
    elif "city council" in title or "council" in title:
        meeting_type = "city-council"
    else:
        meeting_type = "school-board"  # default for SPC-TV

    # Infer subtype from title
    if "budget forum" in title:
        subtype = "budget-forum"
    elif "budget workshop" in title:
        subtype = "budget-workshop"
    elif "workshop" in title:
        subtype = "workshop"
    else:
        subtype = "regular-meeting"

    # Infer date from upload_date (YYYYMMDD) or title
    upload_date = video.get("upload_date", "")
    if upload_date and len(upload_date) == 8:
        date = f"{upload_date[:4]}-{upload_date[4:6]}-{upload_date[6:8]}"
    else:
        # Try to extract date from title
        m = re.search(r"(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})", video.get("title", ""))
        if m:
            month, day, year = m.group(1), m.group(2), m.group(3)
            if len(year) == 2:
                year = f"20{year}"
            date = f"{year}-{int(month):02d}-{int(day):02d}"
        else:
            date = "unknown"

    # Build output path
    dir_name = date
    if subtype != "regular-meeting":
        dir_name = f"{date}-{subtype}"

    output = f"data/{meeting_type}/meetings/{dir_name}/transcript.en-x-autogen.vtt"

    return {
        "vimeo_id": vimeo_id,
        "type": meeting_type,
        "subtype": subtype,
        "date": date,
        "output": output,
    }


def save_config(config_path, config):
    """Write the config back to YAML, preserving comments at top."""
    # Read original to preserve header comments
    with open(config_path, "r") as f:
        original = f.read()

    header_lines = []
    for line in original.split("\n"):
        if line.startswith("#") or line.strip() == "":
            header_lines.append(line)
        else:
            break

    header = "\n".join(header_lines)
    if header:
        header += "\n\n"

    body = yaml.dump(config, default_flow_style=False, sort_keys=False)

    with open(config_path, "w") as f:
        f.write(header)
        f.write(body)


def discover_and_update(config_path):
    """Discover new channel videos and add them to config.

    Returns the number of new entries added.
    """
    config = load_config(config_path)
    channel_id = config.get("channel", "spctv")
    sources = config.get("sources", [])

    # Get known video IDs
    known_ids = {str(s["vimeo_id"]) for s in sources}

    # Discover channel videos
    videos = discover_channel(channel_id)
    if not videos:
        log.info("No videos found on channel (or channel listing failed)")
        return 0

    # Find new videos
    new_videos = [v for v in videos if v["id"] not in known_ids]
    if not new_videos:
        log.info("All %d channel videos are already in config", len(videos))
        return 0

    log.info("Found %d new video(s) not in config:", len(new_videos))

    added = 0
    for video in new_videos:
        meta = infer_metadata(video)
        log.info("  NEW: %s — %s/%s %s (Vimeo %s)",
                 video.get("title", "?"), meta["type"], meta["subtype"],
                 meta["date"], meta["vimeo_id"])

        sources.append(meta)
        added += 1

    # Save updated config
    config["sources"] = sources
    save_config(config_path, config)
    log.info("Added %d new entry/entries to %s", added, os.path.basename(config_path))

    return added


def run(config_path, check_only=False, single_id=None, discover=False):
    """Main connector logic."""
    check_yt_dlp()

    # Discovery phase: find new videos and add to config
    if discover:
        new_count = discover_and_update(config_path)
        if new_count > 0:
            log.info("Discovery added %d new source(s) — proceeding to download", new_count)
        else:
            log.info("Discovery complete — no new sources found")

    config = load_config(config_path)
    sources = config.get("sources", [])

    if single_id:
        sources = [s for s in sources if str(s["vimeo_id"]) == str(single_id)]
        if not sources:
            log.error("Vimeo ID %s not found in config", single_id)
            return 1

    stats = {"skipped": 0, "downloaded": 0, "failed": 0, "would_download": 0}

    for source in sources:
        vimeo_id = source["vimeo_id"]
        output_path = os.path.join(PROJECT_ROOT, source["output"])
        label = f"{source['type']}/{source['date']} (Vimeo {vimeo_id})"

        if os.path.exists(output_path):
            log.info("SKIP %s — already exists", label)
            stats["skipped"] += 1
            continue

        if check_only:
            log.info("WOULD DOWNLOAD %s → %s", label, source["output"])
            stats["would_download"] += 1
            continue

        log.info("DOWNLOADING %s", label)
        if download_vtt(vimeo_id, output_path):
            file_size = os.path.getsize(output_path)
            log.info("OK %s — %d bytes", label, file_size)
            stats["downloaded"] += 1
        else:
            stats["failed"] += 1

    # Summary
    log.info("---")
    if check_only:
        log.info(
            "Check complete: %d would download, %d already exist",
            stats["would_download"], stats["skipped"],
        )
    else:
        log.info(
            "Done: %d downloaded, %d skipped, %d failed",
            stats["downloaded"], stats["skipped"], stats["failed"],
        )

    return 1 if stats["failed"] > 0 else 0


def main():
    parser = argparse.ArgumentParser(description="Vimeo VTT Connector")
    parser.add_argument(
        "--check-only", action="store_true",
        help="List what would be downloaded without downloading",
    )
    parser.add_argument(
        "--vimeo-id", type=str,
        help="Process a single Vimeo video ID",
    )
    parser.add_argument(
        "--discover", action="store_true",
        help="Discover new videos from the SPC-TV channel and add to config",
    )
    parser.add_argument(
        "--config", type=str, default=DEFAULT_CONFIG,
        help="Path to vimeo-sources.yaml",
    )
    args = parser.parse_args()

    sys.exit(run(args.config, check_only=args.check_only,
                 single_id=args.vimeo_id, discover=args.discover))


if __name__ == "__main__":
    main()

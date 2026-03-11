#!/usr/bin/env python3
"""Vimeo VTT Connector — download auto-generated captions from SPC-TV videos.

Uses yt-dlp to fetch VTT subtitle files. No API token required.

Usage:
    python3 scripts/connectors/vimeo.py                  # download all missing VTTs
    python3 scripts/connectors/vimeo.py --check-only     # list what would be downloaded
    python3 scripts/connectors/vimeo.py --vimeo-id ID    # process a single video
"""

import argparse
import logging
import os
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


def load_config(config_path):
    """Load and validate the sources config."""
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    sources = config.get("sources", [])
    if not sources:
        log.warning("No sources found in config file")
    return sources


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


def run(config_path, check_only=False, single_id=None):
    """Main connector logic."""
    check_yt_dlp()
    sources = load_config(config_path)

    if single_id:
        sources = [s for s in sources if s["vimeo_id"] == single_id]
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
        "--config", type=str, default=DEFAULT_CONFIG,
        help="Path to vimeo-sources.yaml",
    )
    args = parser.parse_args()

    sys.exit(run(args.config, check_only=args.check_only, single_id=args.vimeo_id))


if __name__ == "__main__":
    main()

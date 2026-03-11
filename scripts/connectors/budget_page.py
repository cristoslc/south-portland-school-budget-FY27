#!/usr/bin/env python3
"""Budget Page PDF Connector — download documents from spsdme.org/budget27.

Documents are hosted on Google Drive/Docs/Sheets with public sharing.
This connector uses a YAML config file mapping URLs to local output paths,
and can discover new links by scraping the budget page HTML and auto-adding them.

Usage:
    python3 scripts/connectors/budget_page.py                  # download all missing docs
    python3 scripts/connectors/budget_page.py --check-only     # list what would be downloaded
    python3 scripts/connectors/budget_page.py --discover        # find new links, add to config, download
"""

import argparse
import logging
import os
import re
import sys
from datetime import date
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError

import yaml

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("budget-page-connector")

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))
DEFAULT_CONFIG = os.path.join(SCRIPT_DIR, "budget-page-sources.yaml")

# Google URL patterns for extracting document IDs and building export URLs
DRIVE_FILE_RE = re.compile(r"drive\.google\.com/file/d/([a-zA-Z0-9_-]+)")
SLIDES_RE = re.compile(r"docs\.google\.com/presentation/d/([a-zA-Z0-9_-]+)")
SHEETS_RE = re.compile(r"docs\.google\.com/spreadsheets/d/([a-zA-Z0-9_-]+)")

# Page link extraction: Google Drive, Docs, Sheets URLs
# The Apptegy CMS embeds content as escaped JSON, so URLs appear with
# various quoting styles (plain ", escaped \", or \\")
PAGE_LINK_RE = re.compile(
    r'(https://(?:drive\.google\.com/file/d/|docs\.google\.com/'
    r'(?:presentation|spreadsheets)/d/)[a-zA-Z0-9_-]+(?:/[a-zA-Z0-9_?=&%-]*)*)'
)

# For extracting surrounding text from HTML near a link
LINK_CONTEXT_RE = re.compile(
    r'(?:>([^<]{1,100})<[^>]*(?:href|src)=["\']?'
    r'(https://(?:drive\.google\.com|docs\.google\.com)[^"\'>\s]+)'
    r'|'
    r'(?:href|src)=["\']?'
    r'(https://(?:drive\.google\.com|docs\.google\.com)[^"\'>\s]+)'
    r'["\']?[^>]*>([^<]{1,100})<)',
    re.IGNORECASE
)


def load_config(config_path):
    """Load and validate the sources config."""
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    sources = config.get("sources", [])
    if not sources:
        log.warning("No sources found in config file")
    return config


def google_export_url(url):
    """Convert a Google sharing URL to a direct download/export URL.

    Returns (export_url, extension) tuple.
    """
    m = DRIVE_FILE_RE.search(url)
    if m:
        file_id = m.group(1)
        return f"https://drive.google.com/uc?export=download&id={file_id}", None

    m = SLIDES_RE.search(url)
    if m:
        doc_id = m.group(1)
        return f"https://docs.google.com/presentation/d/{doc_id}/export/pdf", ".pdf"

    m = SHEETS_RE.search(url)
    if m:
        doc_id = m.group(1)
        return f"https://docs.google.com/spreadsheets/d/{doc_id}/export?format=xlsx", ".xlsx"

    return None, None


def download_file(url, output_path):
    """Download a file from a Google URL to the output path.

    Returns True on success, False on failure.
    """
    export_url, _ = google_export_url(url)
    if not export_url:
        log.error("Cannot determine export URL for: %s", url)
        return False

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    req = Request(export_url, headers={
        "User-Agent": "Mozilla/5.0 (compatible; budget-connector/1.0)",
    })
    try:
        with urlopen(req, timeout=60) as resp:
            content = resp.read()
            if len(content) < 100:
                log.error("Suspiciously small file (%d bytes) from %s", len(content), url)
                return False
            with open(output_path, "wb") as f:
                f.write(content)
            return True
    except (URLError, HTTPError) as e:
        log.error("Download failed for %s: %s", url, e)
        return False


def discover_page_links(page_url):
    """Fetch the budget page and extract all Google document links with context.

    Returns a list of dicts with keys: url, label (surrounding text or "").
    """
    req = Request(page_url, headers={
        "User-Agent": "Mozilla/5.0 (compatible; budget-connector/1.0)",
        "Accept": "text/html",
    })
    try:
        with urlopen(req, timeout=30) as resp:
            html = resp.read().decode("utf-8")
    except (URLError, HTTPError) as e:
        log.error("Failed to fetch budget page %s: %s", page_url, e)
        return []

    # Build a map of URL -> surrounding text from link context
    url_labels = {}
    for m in LINK_CONTEXT_RE.finditer(html):
        pre_text, pre_url, post_url, post_text = m.groups()
        url = pre_url or post_url
        label = (pre_text or post_text or "").strip()
        if url and label:
            base = url.split("?")[0]
            url_labels[base] = label

    # Extract all Google document links
    links = PAGE_LINK_RE.findall(html)
    seen = set()
    unique = []
    for link in links:
        base = link.split("?")[0]
        if base not in seen:
            seen.add(base)
            label = url_labels.get(base, "")
            unique.append({"url": link, "label": label})

    if not unique:
        log.warning("Zero document links found on %s — page structure may have changed", page_url)

    return unique


def infer_source_metadata(url, label=""):
    """Infer type, date, label, and output path for a discovered URL."""
    today = date.today().isoformat()

    # Determine document type from URL
    if SLIDES_RE.search(url):
        doc_type = "presentation"
        ext = ".pdf"
    elif SHEETS_RE.search(url):
        doc_type = "document"
        ext = ".xlsx"
    else:
        doc_type = "document"
        ext = ".pdf"

    # Clean up label for use as filename slug
    if not label:
        label = f"discovered-{doc_type}"

    slug = re.sub(r'[^a-z0-9]+', '-', label.lower()).strip('-')[:60]

    # Map to output path directory
    if doc_type == "presentation":
        subdir = "presentations"
    else:
        subdir = "documents" if SHEETS_RE.search(url) else "meetings"
        if DRIVE_FILE_RE.search(url):
            subdir = "documents"

    output = f"data/school-board/budget-fy27/{subdir}/{today}-{slug}{ext}"

    return {
        "url": url,
        "type": doc_type,
        "date": today,
        "label": label or f"Discovered {doc_type}",
        "output": output,
    }


def save_config(config_path, config):
    """Write the config back to YAML, preserving header comments."""
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


def auto_add_sources(config_path, page_url):
    """Discover new links, generate metadata, append to config.

    Returns the number of new entries added.
    """
    config = load_config(config_path)
    sources = config.get("sources", [])

    # Known URL bases
    configured_bases = {s["url"].split("?")[0] for s in sources}

    # Discover
    page_links = discover_page_links(page_url)
    if not page_links:
        return 0

    new_links = [l for l in page_links if l["url"].split("?")[0] not in configured_bases]
    if not new_links:
        log.info("All %d page links are already in config", len(page_links))
        return 0

    log.info("Found %d new link(s) not in config:", len(new_links))

    added = 0
    for link_info in new_links:
        meta = infer_source_metadata(link_info["url"], link_info.get("label", ""))
        log.info("  NEW: %s — %s (%s)", meta["label"], meta["type"], meta["url"][:80])
        sources.append(meta)
        added += 1

    config["sources"] = sources
    save_config(config_path, config)
    log.info("Added %d new entry/entries to %s", added, os.path.basename(config_path))

    return added


def run(config_path, check_only=False, discover=False):
    """Main connector logic."""
    config = load_config(config_path)
    page_url = config.get("page_url", "")

    # Discovery phase: find new links and add to config
    if discover and page_url:
        new_count = auto_add_sources(config_path, page_url)
        if new_count > 0:
            log.info("Discovery added %d new source(s) — proceeding to download", new_count)
            # Reload config with new entries
            config = load_config(config_path)
        else:
            log.info("Discovery complete — no new sources found")
    elif discover and not page_url:
        log.warning("--discover requested but no page_url in config — skipping discovery")

    sources = config.get("sources", [])
    stats = {"skipped": 0, "downloaded": 0, "failed": 0, "would_download": 0}

    for source in sources:
        url = source["url"]
        output_path = os.path.join(PROJECT_ROOT, source["output"])
        label = f"{source.get('type', '?')}/{source.get('date', '?')} — {source.get('label', '?')}"

        if os.path.exists(output_path):
            log.info("SKIP %s — already exists", label)
            stats["skipped"] += 1
            continue

        if check_only:
            log.info("WOULD DOWNLOAD %s → %s", label, source["output"])
            stats["would_download"] += 1
            continue

        log.info("DOWNLOADING %s", label)
        if download_file(url, output_path):
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
    parser = argparse.ArgumentParser(description="Budget Page PDF Connector")
    parser.add_argument(
        "--check-only", action="store_true",
        help="List what would be downloaded without downloading",
    )
    parser.add_argument(
        "--discover", action="store_true",
        help="Discover new links on the budget page, add to config, and download",
    )
    parser.add_argument(
        "--config", type=str, default=DEFAULT_CONFIG,
        help="Path to budget-page-sources.yaml",
    )
    args = parser.parse_args()

    sys.exit(run(args.config, check_only=args.check_only, discover=args.discover))


if __name__ == "__main__":
    main()

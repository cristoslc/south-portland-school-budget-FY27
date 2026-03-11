#!/usr/bin/env python3
"""Budget Page Live Discovery Connector — download documents from spsdme.org/budget27.

Fetches the budget page on every run, extracts document links, and downloads
any that are not already present locally. Uses DiscoveryHistory for history
tracking and backoff.

Supported document types: PDF (Google Drive), XLSX (Google Sheets export),
PDF (Google Docs export). Google Slides pubembed URLs are logged as unsupported
and skipped.

Usage:
    python3 scripts/connectors/budget_page.py              # download missing docs
    python3 scripts/connectors/budget_page.py --check-only # list what would be downloaded
"""

import argparse
import logging
import os
import re
import sys
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from pipeline.discovery import DiscoveryHistory

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("budget-page-connector")

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))

BUDGET_PAGE_URL = "https://www.spsdme.org/budget27"
DOCUMENTS_DIR = os.path.join(PROJECT_ROOT, "data", "school-board", "budget-fy27", "documents")
HISTORY_PATH = os.path.join(PROJECT_ROOT, "data", "school-board", "budget-fy27", "discovery.jsonl")

# Google URL patterns
DRIVE_FILE_RE = re.compile(r"drive\.google\.com/file/d/([a-zA-Z0-9_-]+)")
DOCS_RE = re.compile(r"docs\.google\.com/document/d/([a-zA-Z0-9_-]+)")
SHEETS_RE = re.compile(r"docs\.google\.com/spreadsheets/d/([a-zA-Z0-9_-]+)")
SLIDES_RE = re.compile(r"docs\.google\.com/presentation/d/([a-zA-Z0-9_-]+)")
SLIDES_PUBEMBED_RE = re.compile(
    r"docs\.google\.com/presentation/d/[a-zA-Z0-9_-]+/embed"
)

# Extract all Google Drive/Docs/Sheets/Slides links from the page
PAGE_LINK_RE = re.compile(
    r'(https://(?:drive\.google\.com/file/d/|docs\.google\.com/'
    r'(?:document|spreadsheets|presentation)/d/)[a-zA-Z0-9_-]+(?:/[a-zA-Z0-9_.?=&%-]*)*)'
)

# Capture surrounding anchor text near a link
LINK_CONTEXT_RE = re.compile(
    r'(?:>([^<]{1,100})<[^>]*(?:href|src)=["\']?'
    r'(https://(?:drive\.google\.com|docs\.google\.com)[^"\'>\s]+)'
    r'|'
    r'(?:href|src)=["\']?'
    r'(https://(?:drive\.google\.com|docs\.google\.com)[^"\'>\s]+)'
    r'["\']?[^>]*>([^<]{1,100})<)',
    re.IGNORECASE,
)


def classify_url(url):
    """Classify a Google URL and return (url_type, export_url, extension).

    url_type is one of: "drive_pdf", "docs_pdf", "sheets_xlsx", "slides_unsupported".
    Returns (None, None, None) for unrecognised URLs.
    """
    if SLIDES_PUBEMBED_RE.search(url):
        return "slides_unsupported", None, None

    m = SLIDES_RE.search(url)
    if m:
        return "slides_unsupported", None, None

    m = DRIVE_FILE_RE.search(url)
    if m:
        file_id = m.group(1)
        export_url = f"https://drive.google.com/uc?export=download&id={file_id}"
        return "drive_pdf", export_url, ".pdf"

    m = DOCS_RE.search(url)
    if m:
        doc_id = m.group(1)
        export_url = f"https://docs.google.com/document/d/{doc_id}/export?format=pdf"
        return "docs_pdf", export_url, ".pdf"

    m = SHEETS_RE.search(url)
    if m:
        doc_id = m.group(1)
        export_url = f"https://docs.google.com/spreadsheets/d/{doc_id}/export?format=xlsx"
        return "sheets_xlsx", export_url, ".xlsx"

    return None, None, None


def fetch_page_links(page_url):
    """Fetch the budget page and extract all Google document links.

    Returns a list of dicts: [{url, label}, ...].
    On network error, returns an empty list (logged as error).
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

    # Build URL -> label map from anchor context
    url_labels = {}
    for m in LINK_CONTEXT_RE.finditer(html):
        pre_text, pre_url, post_url, post_text = m.groups()
        url = pre_url or post_url
        label = (pre_text or post_text or "").strip()
        if url and label:
            base = url.split("?")[0]
            url_labels[base] = label

    # Extract unique links
    seen = set()
    unique = []
    for link in PAGE_LINK_RE.findall(html):
        base = link.split("?")[0]
        if base not in seen:
            seen.add(base)
            unique.append({"url": link, "label": url_labels.get(base, "")})

    if not unique:
        log.warning(
            "Zero document links found on %s — page structure may have changed",
            page_url,
        )
    else:
        log.info("Found %d document link(s) on %s", len(unique), page_url)

    return unique


def local_filename(url, label, extension):
    """Derive a local filename from URL and label."""
    slug = re.sub(r'[^a-z0-9]+', '-', label.lower()).strip('-')[:60] if label else ""
    if not slug:
        # Fall back to a hash of the URL base
        base = url.split("?")[0].rstrip("/")
        doc_id = base.split("/")[-1]
        slug = doc_id[:40]
    return slug + extension


def download_file(export_url, output_path):
    """Download a file from export_url to output_path.

    Returns True on success, False on failure.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    req = Request(export_url, headers={
        "User-Agent": "Mozilla/5.0 (compatible; budget-connector/1.0)",
    })
    try:
        with urlopen(req, timeout=60) as resp:
            content = resp.read()
            if len(content) < 100:
                log.error(
                    "Suspiciously small file (%d bytes) from %s", len(content), export_url
                )
                return False
            with open(output_path, "wb") as f:
                f.write(content)
        return True
    except (URLError, HTTPError) as e:
        log.error("Download failed for %s: %s", export_url, e)
        return False


def run(check_only=False):
    """Main connector logic — live discovery and download."""
    history = DiscoveryHistory(HISTORY_PATH)

    # Fetch and parse the budget page
    links = fetch_page_links(BUDGET_PAGE_URL)
    if not links:
        log.warning("No links retrieved — exiting without downloading")
        return 0

    stats = {"skipped_existing": 0, "skipped_backoff": 0, "skipped_unsupported": 0,
             "downloaded": 0, "failed": 0, "would_download": 0}

    for link_info in links:
        url = link_info["url"]
        label = link_info.get("label", "")

        url_type, export_url, extension = classify_url(url)

        # Unsupported: Google Slides pubembed
        if url_type == "slides_unsupported":
            log.warning("UNSUPPORTED (Google Slides pubembed) — skipping: %s", url)
            history.record_attempt(url, label, "skipped",
                                   error="Google Slides pubembed not supported")
            stats["skipped_unsupported"] += 1
            continue

        # Unrecognised URL pattern
        if url_type is None:
            log.debug("Unrecognised URL pattern — skipping: %s", url)
            continue

        # Derive local path
        filename = local_filename(url, label, extension)
        output_path = os.path.join(DOCUMENTS_DIR, filename)

        # Skip if already on disk
        if os.path.exists(output_path):
            log.info("SKIP (exists) %s", filename)
            stats["skipped_existing"] += 1
            continue

        # Check backoff
        if not history.should_attempt(url):
            stats["skipped_backoff"] += 1
            continue

        if check_only:
            log.info("WOULD DOWNLOAD %s → %s", label or url[:60], filename)
            stats["would_download"] += 1
            continue

        log.info("DOWNLOADING %s → %s", label or url[:60], filename)
        success = download_file(export_url, output_path)
        if success:
            file_size = os.path.getsize(output_path)
            log.info("OK %s — %d bytes", filename, file_size)
            history.record_attempt(url, label, "ok")
            stats["downloaded"] += 1
        else:
            history.record_attempt(url, label, "failed",
                                   error="download error (see logs)")
            stats["failed"] += 1

    log.info("---")
    if check_only:
        log.info(
            "Check complete: %d would download, %d already exist, "
            "%d unsupported, %d in backoff",
            stats["would_download"], stats["skipped_existing"],
            stats["skipped_unsupported"], stats["skipped_backoff"],
        )
    else:
        log.info(
            "Done: %d downloaded, %d skipped (exist), %d failed, "
            "%d unsupported, %d in backoff",
            stats["downloaded"], stats["skipped_existing"], stats["failed"],
            stats["skipped_unsupported"], stats["skipped_backoff"],
        )

    # Exit 0 on partial success (individual failures are non-fatal)
    return 0


def main():
    parser = argparse.ArgumentParser(description="Budget Page Live Discovery Connector")
    parser.add_argument(
        "--check-only", action="store_true",
        help="List what would be downloaded without downloading",
    )
    args = parser.parse_args()
    sys.exit(run(check_only=args.check_only))


if __name__ == "__main__":
    main()

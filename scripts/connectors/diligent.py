#!/usr/bin/env python3
"""Diligent Community Agenda Connector — fetch city council agendas via REST API.

The Diligent Community portal (southportland-gov.community.diligentoneplatform.com)
exposes a public JSON API. No authentication required.

Usage:
    python3 scripts/connectors/diligent.py                     # fetch all new agendas
    python3 scripts/connectors/diligent.py --check-only        # list what would be fetched
    python3 scripts/connectors/diligent.py --meeting-id 1285   # fetch a single meeting
    python3 scripts/connectors/diligent.py --from 2026-03-01 --to 2026-04-01
"""

import argparse
import html
import logging
import os
import re
import sys
from datetime import datetime, timedelta
from urllib.request import urlopen, Request
from urllib.error import URLError
import json

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("diligent-connector")

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))
DATA_DIR = os.path.join(PROJECT_ROOT, "data", "city-council", "meetings")

BASE_URL = "https://southportland-gov.community.diligentoneplatform.com"
MEETINGS_ENDPOINT = "/Services/MeetingsService.svc/meetings"
DOCUMENTS_ENDPOINT = "/Services/MeetingsService.svc/meetings/{id}/meetingDocuments"
MEETING_DATA_ENDPOINT = "/Services/MeetingsService.svc/meetings/{id}/meetingData"

# Filter to these meeting type names (case-insensitive substring match)
COUNCIL_TYPES = ["city council"]


def api_get(path):
    """Make a GET request to the Diligent Community API."""
    url = f"{BASE_URL}{path}"
    req = Request(url, headers={"Accept": "application/json"})
    try:
        with urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except URLError as e:
        log.error("API request failed: %s — %s", url, e)
        return None
    except json.JSONDecodeError as e:
        log.error("Invalid JSON from %s: %s", url, e)
        return None


def fetch_meetings(date_from, date_to):
    """Fetch meeting list for a date range, filtered to City Council."""
    path = f"{MEETINGS_ENDPOINT}?from={date_from}&to={date_to}&loadall=false"
    data = api_get(path)
    if data is None:
        return []

    meetings = []
    for m in data:
        name = m.get("MeetingTypeName", "") or m.get("Name", "")
        if any(ct in name.lower() for ct in COUNCIL_TYPES):
            meetings.append(m)

    return meetings


def fetch_agenda_html(meeting_id):
    """Fetch the agenda HTML for a specific meeting."""
    path = DOCUMENTS_ENDPOINT.format(id=meeting_id)
    data = api_get(path)
    if data is None:
        return None

    docs = data.get("Documents", [])
    if not docs:
        return None

    # The first document typically contains the agenda
    return docs[0].get("Html", "")


def fetch_meeting_metadata(meeting_id):
    """Fetch meeting metadata (location, time)."""
    path = MEETING_DATA_ENDPOINT.format(id=meeting_id)
    return api_get(path)


def html_to_text(html_content):
    """Convert agenda HTML to structured plain text.

    Preserves headings, list items, and paragraph breaks.
    """
    if not html_content:
        return ""

    text = html_content

    # Replace common block elements with newlines
    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"</p>", "\n\n", text, flags=re.IGNORECASE)
    text = re.sub(r"</div>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"</tr>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"</li>", "\n", text, flags=re.IGNORECASE)

    # Convert headings to text with markers
    for level in range(1, 7):
        text = re.sub(
            rf"<h{level}[^>]*>(.*?)</h{level}>",
            lambda m: f"\n{'#' * level} {m.group(1).strip()}\n",
            text,
            flags=re.IGNORECASE | re.DOTALL,
        )

    # Convert list items
    text = re.sub(r"<li[^>]*>", "- ", text, flags=re.IGNORECASE)

    # Convert bold/strong
    text = re.sub(r"<strong[^>]*>(.*?)</strong>", r"\1", text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r"<b[^>]*>(.*?)</b>", r"\1", text, flags=re.IGNORECASE | re.DOTALL)

    # Strip remaining tags
    text = re.sub(r"<[^>]+>", "", text)

    # Decode HTML entities
    text = html.unescape(text)

    # Clean up whitespace
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = text.strip()

    return text


def meeting_date_str(meeting):
    """Extract the date string (YYYY-MM-DD) from a meeting record.

    The meetings-list endpoint provides MeetingDate directly.
    The meetingData endpoint only has Name (e.g., "City Council Meeting - Mar 05 2026"),
    so we parse the date from the name as a fallback.
    """
    date = meeting.get("MeetingDate", "")
    if date:
        return date[:10]

    # Fallback: parse date from Name like "City Council Meeting - Mar 05 2026"
    name = meeting.get("Name", "")
    match = re.search(r"(\w{3})\s+(\d{2})\s+(\d{4})", name)
    if match:
        try:
            parsed = datetime.strptime(match.group(0), "%b %d %Y")
            return parsed.strftime("%Y-%m-%d")
        except ValueError:
            pass

    log.warning("Could not extract date from meeting: %s", meeting.get("Id"))
    return ""


def output_path_for_meeting(meeting):
    """Determine the output file path for a meeting's agenda."""
    date = meeting_date_str(meeting)
    return os.path.join(DATA_DIR, date, "agenda.txt")


def run(date_from, date_to, check_only=False, single_meeting_id=None):
    """Main connector logic."""
    stats = {"skipped": 0, "downloaded": 0, "failed": 0, "would_download": 0, "no_agenda": 0}

    if single_meeting_id:
        # Fetch single meeting metadata to build a meeting-like record
        meta = fetch_meeting_metadata(single_meeting_id)
        if meta is None:
            log.error("Could not fetch metadata for meeting ID %s", single_meeting_id)
            return 1
        meetings = [{"Id": single_meeting_id, **meta}]
    else:
        log.info("Fetching meetings from %s to %s", date_from, date_to)
        meetings = fetch_meetings(date_from, date_to)
        log.info("Found %d City Council meeting(s)", len(meetings))

    for meeting in meetings:
        mid = meeting.get("Id")
        date = meeting_date_str(meeting)
        name = meeting.get("MeetingTypeName", "") or meeting.get("Name", "")
        label = f"{name} — {date} (ID {mid})"
        out_path = output_path_for_meeting(meeting)

        if not date:
            log.error("SKIP %s — could not determine date", label)
            stats["failed"] += 1
            continue

        if os.path.exists(out_path):
            log.info("SKIP %s — already exists", label)
            stats["skipped"] += 1
            continue

        if check_only:
            log.info("WOULD DOWNLOAD %s", label)
            stats["would_download"] += 1
            continue

        log.info("FETCHING %s", label)
        agenda_html = fetch_agenda_html(mid)
        if not agenda_html:
            log.info("NO AGENDA %s — no documents published", label)
            stats["no_agenda"] += 1
            continue

        agenda_text = html_to_text(agenda_html)
        if not agenda_text.strip():
            log.info("NO AGENDA %s — empty after conversion", label)
            stats["no_agenda"] += 1
            continue

        # Build the output with source header
        source_url = f"{BASE_URL}/Portal/MeetingInformation.aspx?Id={mid}"
        location = meeting.get("Location", meeting.get("MeetingLocation", ""))
        header_lines = [
            name,
            f"{date}",
        ]
        if location:
            header_lines.append(location)
        header_lines.append(f"\nSource: {source_url}\n")

        full_text = "\n".join(header_lines) + "\n" + agenda_text

        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(full_text)

        log.info("OK %s — %d chars", label, len(full_text))
        stats["downloaded"] += 1

    # Summary
    log.info("---")
    if check_only:
        log.info(
            "Check complete: %d would download, %d already exist",
            stats["would_download"], stats["skipped"],
        )
    else:
        log.info(
            "Done: %d downloaded, %d skipped, %d no agenda, %d failed",
            stats["downloaded"], stats["skipped"], stats["no_agenda"], stats["failed"],
        )

    return 1 if stats["failed"] > 0 else 0


def _override_base_url(url):
    global BASE_URL
    BASE_URL = url


def main():
    parser = argparse.ArgumentParser(description="Diligent Community Agenda Connector")
    parser.add_argument("--check-only", action="store_true")
    parser.add_argument("--meeting-id", type=int, help="Fetch a single meeting by ID")
    parser.add_argument(
        "--from", dest="date_from", type=str,
        default=(datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d"),
        help="Start date (YYYY-MM-DD, default: 90 days ago)",
    )
    parser.add_argument(
        "--to", dest="date_to", type=str,
        default="9999-12-31",
        help="End date (YYYY-MM-DD, default: far future)",
    )
    parser.add_argument("--base-url", type=str, default=BASE_URL)
    args = parser.parse_args()

    if args.base_url != BASE_URL:
        _override_base_url(args.base_url)

    sys.exit(run(args.date_from, args.date_to, check_only=args.check_only, single_meeting_id=args.meeting_id))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Source-to-Meeting Affiliation bundler — SPEC-017.

Reads evidence pool manifests and data directories, affiliates each source
with the correct meeting using heuristic rules, and writes meeting bundle
manifests per SPEC-016 schema.

Usage:
    python3 scripts/bundle_meetings.py              # full run
    python3 scripts/bundle_meetings.py --dry-run    # show affiliations without writing
    python3 scripts/bundle_meetings.py --force      # overwrite existing manifests

Exit codes:
    0 — success
    1 — errors encountered
"""

import argparse
import datetime
import hashlib
import logging
import re
import sys
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("bundle_meetings")

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent

# Evidence pool directories
POOLS_DIR = PROJECT_ROOT / "docs" / "evidence-pools"
BUNDLES_DIR = PROJECT_ROOT / "data" / "interpretation" / "bundles"

# Data directories
SB_MEETINGS_DIR = PROJECT_ROOT / "data" / "school-board" / "meetings"
CC_MEETINGS_DIR = PROJECT_ROOT / "data" / "city-council" / "meetings"
BUDGET_MEETINGS_DIR = PROJECT_ROOT / "data" / "school-board" / "budget-fy27" / "meetings"
BUDGET_PRESENTATIONS_DIR = PROJECT_ROOT / "data" / "school-board" / "budget-fy27" / "presentations"
BUDGET_DOCUMENTS_DIR = PROJECT_ROOT / "data" / "school-board" / "budget-fy27" / "documents"

# Date pattern: YYYY-MM-DD at the start of a directory or filename
DATE_RE = re.compile(r"(\d{4}-\d{2}-\d{2})")


# ---------------------------------------------------------------------------
# YAML helpers — avoid dependency on PyYAML for writing; use it for reading
# ---------------------------------------------------------------------------

def _load_yaml(path):
    """Load a YAML file. Requires PyYAML."""
    try:
        import yaml
    except ImportError:
        log.error("PyYAML is required: pip install pyyaml")
        sys.exit(2)
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def _yaml_str(value):
    """Quote a string value for YAML output."""
    # Always double-quote to avoid YAML gotchas with dates, booleans, etc.
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'



# ---------------------------------------------------------------------------
# Source inventory — read all three evidence pool manifests
# ---------------------------------------------------------------------------

class PoolSource:
    """A single source from an evidence pool manifest."""

    def __init__(self, pool_name, raw):
        self.pool = pool_name
        # Handle both "id" and "source-id" key patterns
        self.source_id = str(raw.get("id") or raw.get("source-id", ""))
        self.title = raw.get("title", "")
        self.source_type = raw.get("type", "document")
        self.path = raw.get("path", "")
        self.file = raw.get("file", "")  # normalized markdown path
        self.hash = raw.get("hash", "")
        self.duration = raw.get("duration", "")
        self.slug = raw.get("slug", "")
        # Extract date from path
        self.date = self._extract_date()

    def _extract_date(self):
        """Extract a YYYY-MM-DD date from the source path or slug."""
        for text in [self.path, self.slug, self.title]:
            m = DATE_RE.search(text)
            if m:
                try:
                    return datetime.date.fromisoformat(m.group(1))
                except ValueError:
                    continue
        return None

    @property
    def abs_path(self):
        return str(PROJECT_ROOT / self.path) if self.path else ""

    @property
    def normalized_path(self):
        """Full relative path to normalized markdown in evidence pool."""
        if self.file:
            pool_dir = f"docs/evidence-pools/{self.pool}"
            # file field may already include the pool prefix or be relative
            if self.file.startswith("sources/"):
                return f"{pool_dir}/{self.file}"
            return self.file
        return ""

    def __repr__(self):
        return f"PoolSource({self.pool}/{self.source_id}: {self.path})"


def load_pool_sources():
    """Load all sources from all three evidence pool manifests."""
    sources = []
    pool_names = [
        "school-board-budget-meetings",
        "city-council-meetings-2026",
        "fy27-budget-documents",
    ]
    for pool_name in pool_names:
        manifest_path = POOLS_DIR / pool_name / "manifest.yaml"
        if not manifest_path.exists():
            log.warning("Evidence pool manifest not found: %s", manifest_path)
            continue
        data = _load_yaml(manifest_path)
        for raw in data.get("sources", []):
            sources.append(PoolSource(pool_name, raw))

    log.info("Loaded %d sources from %d evidence pools", len(sources), len(pool_names))
    return sources


# ---------------------------------------------------------------------------
# Meeting discovery — find all meetings from data directories
# ---------------------------------------------------------------------------

class Meeting:
    """A meeting discovered from data directories."""

    def __init__(self, date, body, meeting_type, dir_path, suffix=""):
        self.date = date
        self.body = body
        self.meeting_type = meeting_type
        self.dir_path = dir_path
        self.suffix = suffix  # e.g., "workshop", "budget-forum"
        self.sources = []  # will be populated during affiliation

    @property
    def bundle_dir_name(self):
        """Directory name for the bundle: YYYY-MM-DD-body."""
        return f"{self.date.isoformat()}-{self.body}"

    @property
    def title(self):
        """Human-readable title."""
        type_labels = {
            "regular": "Regular Meeting",
            "workshop": "Workshop",
            "budget-workshop": "Budget Workshop",
            "budget-forum": "Public Budget Forum",
            "joint": "Joint Budget Guidance Workshop",
            "special": "Special Meeting",
        }
        body_labels = {
            "school-board": "School Board",
            "city-council": "City Council",
        }
        label = type_labels.get(self.meeting_type, "Meeting")
        body_label = body_labels.get(self.body, self.body)
        date_str = self.date.strftime("%B %-d, %Y")
        return f"{body_label} {label} — {date_str}"

    def __repr__(self):
        return f"Meeting({self.date}, {self.body}, {self.meeting_type})"


def _classify_meeting_type(dirname_suffix):
    """Infer meeting_type from directory name suffix."""
    suffix = dirname_suffix.lower()
    if "budget-workshop" in suffix:
        return "budget-workshop"
    if "workshop" in suffix:
        return "workshop"
    if "budget-forum" in suffix:
        return "budget-forum"
    return "regular"


def discover_meetings():
    """Discover all meetings from data directories."""
    meetings = {}  # key: (date, body)

    # School board meetings
    if SB_MEETINGS_DIR.exists():
        for d in sorted(SB_MEETINGS_DIR.iterdir()):
            if not d.is_dir():
                continue
            m = DATE_RE.match(d.name)
            if not m:
                continue
            try:
                date = datetime.date.fromisoformat(m.group(1))
            except ValueError:
                continue
            suffix = d.name[len(m.group(1)):].lstrip("-")
            mt = _classify_meeting_type(suffix)
            meetings[(date, "school-board")] = Meeting(
                date, "school-board", mt, str(d), suffix
            )

    # City council meetings
    if CC_MEETINGS_DIR.exists():
        for d in sorted(CC_MEETINGS_DIR.iterdir()):
            if not d.is_dir():
                continue
            m = DATE_RE.match(d.name)
            if not m:
                continue
            try:
                date = datetime.date.fromisoformat(m.group(1))
            except ValueError:
                continue
            suffix = d.name[len(m.group(1)):].lstrip("-")
            mt = _classify_meeting_type(suffix)
            meetings[(date, "city-council")] = Meeting(
                date, "city-council", mt, str(d), suffix
            )

    # Budget FY27 meeting directories — these map to school board meetings
    # but we need to handle the 2025-12-17 workshop which isn't in SB meetings
    if BUDGET_MEETINGS_DIR.exists():
        for d in sorted(BUDGET_MEETINGS_DIR.iterdir()):
            if not d.is_dir():
                continue
            m = DATE_RE.match(d.name)
            if not m:
                continue
            try:
                date = datetime.date.fromisoformat(m.group(1))
            except ValueError:
                continue
            key = (date, "school-board")
            if key not in meetings:
                suffix = d.name[len(m.group(1)):].lstrip("-")
                mt = _classify_meeting_type(suffix)
                meetings[key] = Meeting(
                    date, "school-board", mt, str(d), suffix
                )

    # Special case: 2026-02-10 city council meeting is actually a joint meeting
    joint_key = (datetime.date(2026, 2, 10), "city-council")
    if joint_key in meetings:
        meetings[joint_key].meeting_type = "joint"

    log.info("Discovered %d meetings", len(meetings))
    return meetings


# ---------------------------------------------------------------------------
# Heuristic affiliation — match sources to meetings by date
# ---------------------------------------------------------------------------

def _map_source_type(pool_type, path):
    """Map evidence pool source type to bundle source_type enum."""
    path_lower = path.lower()

    if pool_type == "media":
        return "transcript"

    # Check path for clues
    if "agenda" in path_lower:
        return "agenda"
    if "packet" in path_lower:
        return "packet"
    if "slides" in path_lower or "presentation" in path_lower:
        return "presentation"
    if path_lower.endswith(".xlsx") or path_lower.endswith(".csv"):
        return "spreadsheet"
    if "discussion" in path_lower:
        return "presentation"

    if pool_type in ("document", "local"):
        return "document"

    return "other"


def _make_source_entry(pool_source, meeting):
    """Create a bundle source entry dict from a PoolSource."""
    body_prefix = "sb" if meeting.body == "school-board" else "cc"
    stype = _map_source_type(pool_source.source_type, pool_source.path)

    # Build a deterministic source_id
    source_id = f"{body_prefix}-{stype}-{meeting.date.isoformat()}"
    # Add pool source id to disambiguate multiple sources of same type
    source_id += f"-{pool_source.source_id}"

    entry = {
        "source_id": source_id,
        "source_type": stype,
        "title": pool_source.title,
        "path": pool_source.path,
    }

    if pool_source.normalized_path:
        np = pool_source.normalized_path
        # Verify the normalized path exists
        if (PROJECT_ROOT / np).exists():
            entry["normalized_path"] = np

    entry["evidence_pool"] = pool_source.pool

    if pool_source.title and pool_source.title != "Packet" and pool_source.title != "Agenda":
        # Title is descriptive enough to skip description
        pass

    if pool_source.hash:
        entry["hash"] = pool_source.hash

    if pool_source.duration:
        entry["duration"] = pool_source.duration

    return entry


def _deduplicate_sources(sources):
    """Remove duplicate sources that reference the same raw file path.

    The fy27-budget-documents pool has duplicate entries (original ids 001-012
    and later-added source-ids 013-025) for the same files. Keep the one with
    the richer metadata (more fields populated).
    """
    by_path = {}
    for src in sources:
        path = src.path
        if path in by_path:
            existing = by_path[path]
            # Prefer the one with more metadata
            existing_score = sum(1 for v in [existing.title, existing.slug,
                                              existing.duration, existing.hash] if v)
            new_score = sum(1 for v in [src.title, src.slug,
                                         src.duration, src.hash] if v)
            if new_score > existing_score:
                by_path[path] = src
        else:
            by_path[path] = src
    return list(by_path.values())


def affiliate_sources(sources, meetings):
    """Affiliate each source with the correct meeting using heuristics.

    Returns (affiliated_count, unaffiliated list).
    """
    # Deduplicate sources that point to the same raw file
    unique_sources = _deduplicate_sources(sources)
    log.info("After deduplication: %d unique sources (from %d total)",
             len(unique_sources), len(sources))

    affiliated = 0
    unaffiliated = []

    for src in unique_sources:
        if src.date is None:
            unaffiliated.append(src)
            log.warning("No date extractable from source: %s", src)
            continue

        # Determine which body this source belongs to
        if src.pool == "school-board-budget-meetings":
            target_body = "school-board"
        elif src.pool == "city-council-meetings-2026":
            target_body = "city-council"
        elif src.pool == "fy27-budget-documents":
            # FY27 budget docs: check if the date matches a specific meeting
            # Some docs (like 2026-02-10 council-board discussion) go to
            # city council despite being in the budget pool
            if "council" in src.path.lower() and "board" not in src.title.lower().replace("council", ""):
                target_body = "city-council"
            else:
                target_body = "school-board"
        else:
            target_body = "school-board"

        # Special case: 2026-02-10 council-board discussion goes to city council
        if src.date == datetime.date(2026, 2, 10) and "council" in src.path.lower():
            target_body = "city-council"

        key = (src.date, target_body)
        if key in meetings:
            meetings[key].sources.append(src)
            affiliated += 1
        else:
            # Try the other body (cross-body affiliation)
            other_body = "city-council" if target_body == "school-board" else "school-board"
            alt_key = (src.date, other_body)
            if alt_key in meetings:
                meetings[alt_key].sources.append(src)
                affiliated += 1
                log.info("Cross-body affiliation: %s -> %s", src, alt_key)
            else:
                unaffiliated.append(src)
                log.warning("No meeting found for source: %s (date=%s, body=%s)",
                            src, src.date, target_body)

    log.info("Affiliated %d sources, %d unaffiliated",
             affiliated, len(unaffiliated))
    return affiliated, unaffiliated


# ---------------------------------------------------------------------------
# Agenda-aware cross-referencing (Task 3)
# ---------------------------------------------------------------------------

def cross_reference_agendas(meetings, unaffiliated):
    """For unaffiliated sources, try temporal proximity to the nearest meeting.

    Budget documents posted between meetings get affiliated with the meeting
    whose date best matches. This handles presentations posted a few days
    before or after a meeting.
    """
    if not unaffiliated:
        return 0, []

    # Build sorted list of (date, body) meeting keys
    sb_dates = sorted(d for (d, b) in meetings if b == "school-board")
    cc_dates = sorted(d for (d, b) in meetings if b == "city-council")

    still_unaffiliated = []
    cross_ref_count = 0

    for src in unaffiliated:
        if src.date is None:
            still_unaffiliated.append(src)
            continue

        # Determine target body
        if src.pool == "city-council-meetings-2026":
            dates = cc_dates
            body = "city-council"
        else:
            dates = sb_dates
            body = "school-board"

        # Find the nearest meeting date
        nearest = _find_nearest_date(src.date, dates)
        if nearest is not None:
            key = (nearest, body)
            if key in meetings:
                meetings[key].sources.append(src)
                cross_ref_count += 1
                log.info("Agenda cross-ref: %s -> %s (proximity: %d days)",
                         src, key, abs((src.date - nearest).days))
                continue

        still_unaffiliated.append(src)

    log.info("Agenda cross-ref affiliated %d additional sources, %d remain",
             cross_ref_count, len(still_unaffiliated))
    return cross_ref_count, still_unaffiliated


def _find_nearest_date(target, sorted_dates):
    """Find the nearest date in sorted_dates to target, within 14 days."""
    if not sorted_dates:
        return None

    best = None
    best_delta = datetime.timedelta(days=15)  # max 14 days

    for d in sorted_dates:
        delta = abs(target - d)
        if delta < best_delta:
            best = d
            best_delta = delta

    return best


# ---------------------------------------------------------------------------
# LLM-assisted classification fallback (Task 4)
# ---------------------------------------------------------------------------

def llm_classify_fallback(unaffiliated):
    """Stub for LLM-assisted classification.

    For this project, heuristics should cover all cases. If any sources
    remain unaffiliated, log them as requiring manual review.
    """
    if not unaffiliated:
        log.info("LLM fallback: no unaffiliated sources requiring LLM classification")
        return

    log.warning(
        "LLM fallback: %d source(s) could not be affiliated by heuristics or "
        "agenda cross-referencing. These require manual review:",
        len(unaffiliated),
    )
    for src in unaffiliated:
        log.warning("  - %s (pool=%s, date=%s)", src.path, src.pool, src.date)


# ---------------------------------------------------------------------------
# Idempotency layer (Task 5)
# ---------------------------------------------------------------------------

def _content_hash(text):
    """Compute SHA-256 hash of text content."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _read_file_text(path):
    """Read file as text, return empty string if not found."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except (FileNotFoundError, OSError):
        return ""


def check_idempotency(manifest_path, new_content):
    """Check if writing this manifest would change anything.

    Returns True if the file needs updating, False if content is identical.
    """
    existing = _read_file_text(manifest_path)
    if not existing:
        return True  # file doesn't exist yet

    return _content_hash(existing) != _content_hash(new_content)


# ---------------------------------------------------------------------------
# Bundle generation
# ---------------------------------------------------------------------------

def _find_agenda_ref(meeting):
    """Find the agenda file path for a meeting, if one exists."""
    # Check in meeting directory first
    dir_path = Path(meeting.dir_path)

    # School board budget meetings may have agenda in budget-fy27 path
    for agenda_name in ["agenda.pdf", "agenda.txt"]:
        agenda_path = dir_path / agenda_name
        if agenda_path.exists():
            return str(agenda_path.relative_to(PROJECT_ROOT))

    # Check budget-fy27 meetings directory for school board
    if meeting.body == "school-board":
        budget_dir = BUDGET_MEETINGS_DIR
        for d in budget_dir.iterdir() if budget_dir.exists() else []:
            if not d.is_dir():
                continue
            m = DATE_RE.match(d.name)
            if m:
                try:
                    date = datetime.date.fromisoformat(m.group(1))
                except ValueError:
                    continue
                if date == meeting.date:
                    for agenda_name in ["agenda.pdf", "agenda.txt"]:
                        agenda_path = d / agenda_name
                        if agenda_path.exists():
                            return str(agenda_path.relative_to(PROJECT_ROOT))

    return None


def build_manifest_data(meeting):
    """Build a manifest dict for a meeting."""
    # Sort sources by type priority: transcript, agenda, packet, presentation,
    # spreadsheet, document, other
    type_order = {
        "transcript": 0, "agenda": 1, "packet": 2, "presentation": 3,
        "spreadsheet": 4, "document": 5, "other": 6,
    }

    source_entries = []
    for src in meeting.sources:
        entry = _make_source_entry(src, meeting)
        source_entries.append(entry)

    # Sort by type, then by source_id for deterministic output
    source_entries.sort(key=lambda e: (
        type_order.get(e["source_type"], 99),
        e["source_id"],
    ))

    # Deduplicate entries by path (belt-and-suspenders after pool dedup)
    seen_paths = set()
    deduped = []
    for entry in source_entries:
        if entry["path"] not in seen_paths:
            seen_paths.add(entry["path"])
            deduped.append(entry)
    source_entries = deduped

    if not source_entries:
        return None

    manifest = {
        "schema_version": "1.0",
        "meeting_date": meeting.date.isoformat(),
        "meeting_type": meeting.meeting_type,
        "body": meeting.body,
        "title": meeting.title,
        "sources": source_entries,
    }

    # Add agenda_ref if found
    agenda_ref = _find_agenda_ref(meeting)
    if agenda_ref:
        manifest["agenda_ref"] = agenda_ref

    return manifest


def generate_manifest_text(manifest_data):
    """Generate the YAML text for a manifest, for idempotency comparison."""
    lines = []
    lines.append(f"schema_version: {_yaml_str(manifest_data['schema_version'])}")
    lines.append("")
    lines.append(f"meeting_date: {_yaml_str(manifest_data['meeting_date'])}")
    lines.append(f"meeting_type: {manifest_data['meeting_type']}")
    lines.append(f"body: {manifest_data['body']}")

    if manifest_data.get("title"):
        lines.append(f"title: {_yaml_str(manifest_data['title'])}")

    if manifest_data.get("agenda_ref"):
        lines.append(f"")
        lines.append(f"agenda_ref: {manifest_data['agenda_ref']}")

    if manifest_data.get("video_url"):
        lines.append(f"video_url: {manifest_data['video_url']}")

    if manifest_data.get("notes"):
        lines.append(f"notes: >")
        words = manifest_data["notes"].split()
        current_line = "  "
        for word in words:
            if len(current_line) + len(word) + 1 > 74:
                lines.append(current_line.rstrip())
                current_line = "  " + word
            else:
                if current_line.strip():
                    current_line += " " + word
                else:
                    current_line += word
        if current_line.strip():
            lines.append(current_line.rstrip())

    lines.append("")
    lines.append("sources:")
    for src in manifest_data["sources"]:
        lines.append(f"  - source_id: {_yaml_str(src['source_id'])}")
        lines.append(f"    source_type: {src['source_type']}")
        lines.append(f"    title: {_yaml_str(src['title'])}")
        lines.append(f"    path: {src['path']}")
        if src.get("normalized_path"):
            lines.append(f"    normalized_path: {src['normalized_path']}")
        if src.get("evidence_pool"):
            lines.append(f"    evidence_pool: {src['evidence_pool']}")
        if src.get("description"):
            lines.append(f"    description: {_yaml_str(src['description'])}")
        if src.get("hash"):
            lines.append(f"    hash: {_yaml_str(src['hash'])}")
        if src.get("duration"):
            lines.append(f"    duration: {_yaml_str(src['duration'])}")
        lines.append("")

    while lines and lines[-1] == "":
        lines.pop()
    lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Existing manifest protection
# ---------------------------------------------------------------------------

# These manifests were manually created and should not be overwritten
# unless --force is used
PROTECTED_BUNDLES = {
    "2026-02-10-city-council",
    "2026-03-02-school-board",
    "2026-03-05-city-council",
}


def is_protected(bundle_dir_name):
    """Check if a bundle directory is a protected manually-created manifest."""
    return bundle_dir_name in PROTECTED_BUNDLES


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Affiliate evidence pool sources with meetings (SPEC-017)"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Show affiliations without writing manifests",
    )
    parser.add_argument(
        "--force", action="store_true",
        help="Overwrite existing manifests (including manually-created ones)",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true",
        help="Enable debug logging",
    )
    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    log.info("=== Source-to-Meeting Affiliation (SPEC-017) ===")

    # Step 1: Load all evidence pool sources
    sources = load_pool_sources()

    # Step 2: Discover all meetings from data directories
    meetings = discover_meetings()

    # Step 3: Heuristic affiliation
    log.info("--- Heuristic affiliation ---")
    affiliated_count, unaffiliated = affiliate_sources(sources, meetings)

    # Step 4: Agenda-aware cross-referencing
    log.info("--- Agenda cross-referencing ---")
    cross_ref_count, still_unaffiliated = cross_reference_agendas(
        meetings, unaffiliated
    )

    # Step 5: LLM fallback
    log.info("--- LLM classification fallback ---")
    llm_classify_fallback(still_unaffiliated)

    # Step 6: Generate and write bundle manifests
    log.info("--- Generating bundle manifests ---")
    written = 0
    skipped_empty = 0
    skipped_protected = 0
    skipped_idempotent = 0
    total_sources_bundled = 0

    for key in sorted(meetings.keys()):
        meeting = meetings[key]
        manifest_data = build_manifest_data(meeting)

        if manifest_data is None:
            skipped_empty += 1
            log.debug("Skipping %s: no sources affiliated", meeting)
            continue

        total_sources_bundled += len(manifest_data["sources"])
        bundle_dir = BUNDLES_DIR / meeting.bundle_dir_name
        manifest_path = bundle_dir / "manifest.yaml"

        if args.dry_run:
            log.info("  [dry-run] Would write %s (%d sources)",
                     manifest_path.relative_to(PROJECT_ROOT),
                     len(manifest_data["sources"]))
            for src in manifest_data["sources"]:
                log.info("    - %s (%s)", src["source_id"], src["source_type"])
            written += 1
            continue

        # Check if this is a protected bundle
        if is_protected(meeting.bundle_dir_name) and not args.force:
            if manifest_path.exists():
                skipped_protected += 1
                log.info("  Skipping protected bundle: %s (use --force to overwrite)",
                         meeting.bundle_dir_name)
                continue

        # Idempotency check
        new_content = generate_manifest_text(manifest_data)
        if manifest_path.exists() and not check_idempotency(manifest_path, new_content):
            skipped_idempotent += 1
            log.debug("Skipping %s: content unchanged", meeting.bundle_dir_name)
            continue

        # Write the manifest
        bundle_dir.mkdir(parents=True, exist_ok=True)
        with open(manifest_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        written += 1
        log.info("  Wrote %s (%d sources)",
                 manifest_path.relative_to(PROJECT_ROOT),
                 len(manifest_data["sources"]))

    # Summary
    log.info("")
    log.info("=== Summary ===")
    log.info("Meetings discovered:       %d", len(meetings))
    log.info("Sources affiliated:        %d (heuristic) + %d (cross-ref)",
             affiliated_count, cross_ref_count)
    log.info("Sources unaffiliated:      %d", len(still_unaffiliated))
    log.info("Total sources bundled:     %d", total_sources_bundled)
    log.info("Manifests written:         %d", written)
    log.info("Skipped (no sources):      %d", skipped_empty)
    log.info("Skipped (protected):       %d", skipped_protected)
    log.info("Skipped (unchanged):       %d", skipped_idempotent)

    if still_unaffiliated:
        log.warning("")
        log.warning("Unaffiliated sources requiring manual review:")
        for src in still_unaffiliated:
            log.warning("  - %s", src)

    return 0 if not still_unaffiliated else 1


if __name__ == "__main__":
    sys.exit(main())

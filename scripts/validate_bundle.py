#!/usr/bin/env python3
"""Validate a meeting bundle manifest or inter-meeting evidence manifest.

Checks:
  - Required fields present
  - Enum values valid (meeting_type, body, source_type)
  - Date formats are ISO 8601 (YYYY-MM-DD)
  - Referenced source paths resolve to existing files
  - Inter-meeting date ranges consistent (posted_after < posted_before)

Usage:
    python3 scripts/validate_bundle.py <manifest.yaml>
    python3 scripts/validate_bundle.py --inter-meeting <manifest.yaml>
    python3 scripts/validate_bundle.py --all

Exit codes:
    0 — valid
    1 — validation errors found
    2 — usage error (bad arguments, file not found)
"""

import argparse
import datetime
import logging
import sys
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("validate_bundle")

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent

# --- Schema constants ---

VALID_MEETING_TYPES = {"workshop", "regular", "special", "budget-forum",
                       "budget-workshop", "joint"}

VALID_BODIES = {"school-board", "city-council"}

VALID_SOURCE_TYPES = {"transcript", "agenda", "packet", "presentation",
                      "spreadsheet", "document", "other"}

VALID_INTER_MEETING_SOURCE_TYPES = {"news-article", "public-statement",
                                     "document", "letter", "announcement",
                                     "other"}

VALID_INTER_MEETING_BODIES = {"school-board", "city-council", "both"}


def parse_date(value, field_name):
    """Parse and validate an ISO 8601 date string. Returns (date, errors)."""
    errors = []
    if not isinstance(value, str):
        # PyYAML may parse bare dates as datetime.date objects
        if isinstance(value, datetime.date):
            return value, errors
        errors.append(f"{field_name}: expected string, got {type(value).__name__}")
        return None, errors

    try:
        return datetime.date.fromisoformat(value), errors
    except ValueError:
        errors.append(
            f"{field_name}: invalid date format '{value}' — expected YYYY-MM-DD"
        )
        return None, errors


def validate_bundle_manifest(data, check_paths=True):
    """Validate a meeting bundle manifest. Returns list of error strings."""
    errors = []

    # schema_version
    sv = data.get("schema_version")
    if sv is None:
        errors.append("missing required field: schema_version")
    elif str(sv) != "1.0":
        errors.append(f"schema_version: expected '1.0', got '{sv}'")

    # meeting_date
    md = data.get("meeting_date")
    if md is None:
        errors.append("missing required field: meeting_date")
    else:
        _, date_errs = parse_date(md, "meeting_date")
        errors.extend(date_errs)

    # meeting_type
    mt = data.get("meeting_type")
    if mt is None:
        errors.append("missing required field: meeting_type")
    elif mt not in VALID_MEETING_TYPES:
        errors.append(
            f"meeting_type: invalid value '{mt}' — "
            f"expected one of: {', '.join(sorted(VALID_MEETING_TYPES))}"
        )

    # body
    body = data.get("body")
    if body is None:
        errors.append("missing required field: body")
    elif body not in VALID_BODIES:
        errors.append(
            f"body: invalid value '{body}' — "
            f"expected one of: {', '.join(sorted(VALID_BODIES))}"
        )

    # sources
    sources = data.get("sources")
    if sources is None:
        errors.append("missing required field: sources")
    elif not isinstance(sources, list):
        errors.append("sources: expected a list")
    elif len(sources) == 0:
        errors.append("sources: must contain at least one entry")
    else:
        for i, src in enumerate(sources):
            prefix = f"sources[{i}]"
            errors.extend(
                _validate_source_entry(src, prefix, check_paths)
            )

    # Check for unexpected top-level fields
    known_fields = {"schema_version", "meeting_date", "meeting_type", "body",
                    "title", "sources", "agenda_ref", "video_url", "notes"}
    for key in data:
        if key not in known_fields:
            errors.append(f"unexpected field: '{key}'")

    # If agenda_ref is set, check path resolves
    agenda_ref = data.get("agenda_ref")
    if agenda_ref and check_paths:
        agenda_path = PROJECT_ROOT / agenda_ref
        if not agenda_path.exists():
            errors.append(
                f"agenda_ref: file not found — {agenda_ref}"
            )

    return errors


def _validate_source_entry(src, prefix, check_paths):
    """Validate a single source entry in a bundle manifest."""
    errors = []

    if not isinstance(src, dict):
        errors.append(f"{prefix}: expected a mapping, got {type(src).__name__}")
        return errors

    # Required fields
    for field in ("source_id", "source_type", "title", "path"):
        if field not in src:
            errors.append(f"{prefix}: missing required field '{field}'")

    # source_type enum
    st = src.get("source_type")
    if st is not None and st not in VALID_SOURCE_TYPES:
        errors.append(
            f"{prefix}.source_type: invalid value '{st}' — "
            f"expected one of: {', '.join(sorted(VALID_SOURCE_TYPES))}"
        )

    # path resolution
    path = src.get("path")
    if path and check_paths:
        full_path = PROJECT_ROOT / path
        if not full_path.exists():
            errors.append(f"{prefix}.path: file not found — {path}")

    # normalized_path resolution
    np = src.get("normalized_path")
    if np and check_paths:
        full_np = PROJECT_ROOT / np
        if not full_np.exists():
            errors.append(f"{prefix}.normalized_path: file not found — {np}")

    # hash format
    h = src.get("hash")
    if h is not None:
        if not isinstance(h, str) or not h.startswith("sha256:"):
            errors.append(
                f"{prefix}.hash: expected format 'sha256:<64 hex chars>', got '{h}'"
            )
        elif len(h) != 71:  # "sha256:" (7) + 64 hex chars
            errors.append(
                f"{prefix}.hash: expected 64 hex chars after 'sha256:', "
                f"got {len(h) - 7}"
            )

    # duration format
    dur = src.get("duration")
    if dur is not None:
        if not isinstance(dur, str):
            errors.append(f"{prefix}.duration: expected string, got {type(dur).__name__}")
        else:
            parts = dur.split(":")
            if len(parts) != 3 or not all(p.isdigit() and len(p) == 2 for p in parts):
                errors.append(
                    f"{prefix}.duration: invalid format '{dur}' — expected HH:MM:SS"
                )

    # Unexpected fields
    known = {"source_id", "source_type", "title", "path", "normalized_path",
             "evidence_pool", "description", "hash", "duration"}
    for key in src:
        if key not in known:
            errors.append(f"{prefix}: unexpected field '{key}'")

    return errors


def validate_inter_meeting_manifest(data, check_paths=True):
    """Validate an inter-meeting evidence manifest. Returns list of errors."""
    errors = []

    # schema_version
    sv = data.get("schema_version")
    if sv is None:
        errors.append("missing required field: schema_version")
    elif str(sv) != "1.0":
        errors.append(f"schema_version: expected '1.0', got '{sv}'")

    # entries
    entries = data.get("entries")
    if entries is None:
        errors.append("missing required field: entries")
    elif not isinstance(entries, list):
        errors.append("entries: expected a list")
    else:
        for i, entry in enumerate(entries):
            prefix = f"entries[{i}]"
            errors.extend(
                _validate_inter_meeting_entry(entry, prefix, check_paths)
            )

    # Unexpected top-level fields
    known_fields = {"schema_version", "entries"}
    for key in data:
        if key not in known_fields:
            errors.append(f"unexpected field: '{key}'")

    return errors


def _validate_inter_meeting_entry(entry, prefix, check_paths):
    """Validate a single inter-meeting evidence entry."""
    errors = []

    if not isinstance(entry, dict):
        errors.append(f"{prefix}: expected a mapping, got {type(entry).__name__}")
        return errors

    # Required fields
    for field in ("entry_id", "date_posted", "source_type", "source_path",
                  "description", "date_range"):
        if field not in entry:
            errors.append(f"{prefix}: missing required field '{field}'")

    # date_posted
    dp = entry.get("date_posted")
    if dp is not None:
        _, date_errs = parse_date(dp, f"{prefix}.date_posted")
        errors.extend(date_errs)

    # source_type enum
    st = entry.get("source_type")
    if st is not None and st not in VALID_INTER_MEETING_SOURCE_TYPES:
        errors.append(
            f"{prefix}.source_type: invalid value '{st}' — expected one of: "
            f"{', '.join(sorted(VALID_INTER_MEETING_SOURCE_TYPES))}"
        )

    # source_path resolution
    sp = entry.get("source_path")
    if sp and check_paths:
        full_sp = PROJECT_ROOT / sp
        if not full_sp.exists():
            errors.append(f"{prefix}.source_path: file not found — {sp}")

    # body enum (optional)
    body = entry.get("body")
    if body is not None and body not in VALID_INTER_MEETING_BODIES:
        errors.append(
            f"{prefix}.body: invalid value '{body}' — expected one of: "
            f"{', '.join(sorted(VALID_INTER_MEETING_BODIES))}"
        )

    # date_range
    dr = entry.get("date_range")
    if dr is not None:
        if not isinstance(dr, dict):
            errors.append(f"{prefix}.date_range: expected a mapping")
        else:
            pa = dr.get("posted_after")
            pb = dr.get("posted_before")

            if pa is None:
                errors.append(
                    f"{prefix}.date_range: missing required field 'posted_after'"
                )
            else:
                pa_date, pa_errs = parse_date(pa, f"{prefix}.date_range.posted_after")
                errors.extend(pa_errs)

            if pb is None:
                errors.append(
                    f"{prefix}.date_range: missing required field 'posted_before'"
                )
            else:
                pb_date, pb_errs = parse_date(pb, f"{prefix}.date_range.posted_before")
                errors.extend(pb_errs)

            # Consistency: posted_after < posted_before
            if pa is not None and pb is not None:
                pa_date, _ = parse_date(pa, "")
                pb_date, _ = parse_date(pb, "")
                if pa_date and pb_date and pa_date >= pb_date:
                    errors.append(
                        f"{prefix}.date_range: posted_after ({pa}) must be "
                        f"before posted_before ({pb})"
                    )

            # Unexpected fields in date_range
            for key in dr:
                if key not in ("posted_after", "posted_before"):
                    errors.append(
                        f"{prefix}.date_range: unexpected field '{key}'"
                    )

    # normalized_path resolution
    np_val = entry.get("normalized_path")
    if np_val and check_paths:
        full_np = PROJECT_ROOT / np_val
        if not full_np.exists():
            errors.append(
                f"{prefix}.normalized_path: file not found — {np_val}"
            )

    # Unexpected fields
    known = {"entry_id", "date_posted", "source_type", "source_path", "title",
             "description", "date_range", "body", "normalized_path"}
    for key in entry:
        if key not in known:
            errors.append(f"{prefix}: unexpected field '{key}'")

    return errors


def find_all_bundles():
    """Find all bundle manifest files under data/interpretation/bundles/."""
    bundles_dir = PROJECT_ROOT / "data" / "interpretation" / "bundles"
    if not bundles_dir.exists():
        return []
    manifests = sorted(bundles_dir.glob("*/manifest.yaml"))
    return manifests


def find_inter_meeting_manifest():
    """Find the inter-meeting manifest if it exists."""
    path = PROJECT_ROOT / "data" / "interpretation" / "inter-meeting" / "manifest.yaml"
    if path.exists():
        return path
    return None


def main():
    parser = argparse.ArgumentParser(
        description="Validate meeting bundle or inter-meeting evidence manifests"
    )
    parser.add_argument(
        "manifest", nargs="?",
        help="Path to a manifest.yaml file to validate",
    )
    parser.add_argument(
        "--inter-meeting", action="store_true",
        help="Treat the manifest as an inter-meeting evidence manifest",
    )
    parser.add_argument(
        "--all", action="store_true",
        help="Validate all bundle manifests and the inter-meeting manifest",
    )
    parser.add_argument(
        "--no-check-paths", action="store_true",
        help="Skip checking whether source paths resolve to existing files",
    )
    args = parser.parse_args()

    if not args.manifest and not args.all:
        parser.error("either provide a manifest path or use --all")

    # Import yaml here so we get a clear error if it's missing
    try:
        import yaml
    except ImportError:
        log.error("PyYAML is required: pip install pyyaml")
        sys.exit(2)

    check_paths = not args.no_check_paths
    total_errors = 0
    files_checked = 0

    if args.all:
        # Validate all bundles
        bundles = find_all_bundles()
        if not bundles:
            log.info("No bundle manifests found in data/interpretation/bundles/")
        for manifest_path in bundles:
            files_checked += 1
            errs = _validate_file(
                manifest_path, is_inter_meeting=False,
                check_paths=check_paths, yaml_mod=yaml
            )
            total_errors += errs

        # Validate inter-meeting manifest
        im_path = find_inter_meeting_manifest()
        if im_path:
            files_checked += 1
            errs = _validate_file(
                im_path, is_inter_meeting=True,
                check_paths=check_paths, yaml_mod=yaml
            )
            total_errors += errs
        else:
            log.info("No inter-meeting manifest found")

        log.info("")
        log.info("Checked %d file(s), %d error(s) total",
                 files_checked, total_errors)

    else:
        manifest_path = Path(args.manifest).resolve()
        if not manifest_path.exists():
            log.error("File not found: %s", manifest_path)
            sys.exit(2)

        total_errors = _validate_file(
            manifest_path, is_inter_meeting=args.inter_meeting,
            check_paths=check_paths, yaml_mod=yaml
        )

    sys.exit(1 if total_errors > 0 else 0)


def _validate_file(manifest_path, is_inter_meeting, check_paths, yaml_mod):
    """Load and validate a single manifest file. Returns error count."""
    rel = manifest_path.relative_to(PROJECT_ROOT) if manifest_path.is_relative_to(PROJECT_ROOT) else manifest_path

    try:
        with open(manifest_path, "r", encoding="utf-8") as f:
            data = yaml_mod.safe_load(f)
    except Exception as e:
        log.error("%s — YAML parse error: %s", rel, e)
        return 1

    if data is None:
        log.error("%s — empty or null YAML document", rel)
        return 1

    if not isinstance(data, dict):
        log.error("%s — expected a YAML mapping at top level", rel)
        return 1

    if is_inter_meeting:
        errors = validate_inter_meeting_manifest(data, check_paths)
    else:
        errors = validate_bundle_manifest(data, check_paths)

    if errors:
        log.error("%s — %d validation error(s):", rel, len(errors))
        for err in errors:
            log.error("  %s", err)
    else:
        log.info("%s — valid", rel)

    return len(errors)


if __name__ == "__main__":
    main()

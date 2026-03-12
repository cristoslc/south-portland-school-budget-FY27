#!/usr/bin/env python3
"""Validate an interpretation output document against the schema.

Checks:
  - YAML frontmatter has required fields (schema_version, meeting_id, persona_id)
  - Optional frontmatter fields have valid formats (dates, patterns)
  - All three body sections exist (Structured Points, Journey Map, Reactions)
  - Structured points have required fields (fact, source, emotional valence, threat level)
  - Emotional valence values are from the allowed enum
  - Threat level values map to valid levels (high, moderate, low, none)
  - Journey map beats have required columns
  - Reactions section is non-empty

Usage:
    python3 scripts/validate_interpretation.py <interpretation.md>
    python3 scripts/validate_interpretation.py --all

Exit codes:
    0 — valid
    1 — validation errors found
    2 — usage error (bad arguments, file not found)
"""

import argparse
import datetime
import logging
import re
import sys
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("validate_interpretation")

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent

# --- Schema constants ---

VALID_EMOTIONAL_VALENCES = {
    "alarmed", "anxious", "frustrated", "skeptical",
    "neutral", "cautiously_optimistic", "reassured", "empowered",
}

VALID_THREAT_LEVELS = {"high", "moderate", "low", "none"}

THREAT_LEVEL_INT_MAP = {"none": 1, "low": 2, "moderate": 3, "high": 4}

MEETING_ID_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}-[a-z][a-z0-9-]+$")
PERSONA_ID_PATTERN = re.compile(r"^PERSONA-\d{3}$")


def parse_date(value, field_name):
    """Parse and validate an ISO 8601 date string. Returns (date, errors)."""
    errors = []
    if not isinstance(value, str):
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


def split_frontmatter_and_body(text):
    """Split a markdown document with YAML frontmatter into (frontmatter_str, body_str).

    Expects the document to start with '---' and have a closing '---'.
    Returns (frontmatter_str, body_str) or (None, None) on failure.
    """
    text = text.lstrip("\ufeff")  # strip BOM if present
    if not text.startswith("---"):
        return None, None

    # Find the closing ---
    end = text.find("\n---", 3)
    if end == -1:
        return None, None

    frontmatter_str = text[3:end].strip()
    body_str = text[end + 4:].strip()
    return frontmatter_str, body_str


def parse_frontmatter(frontmatter_str, yaml_mod):
    """Parse YAML frontmatter string. Returns (dict, errors)."""
    errors = []
    try:
        data = yaml_mod.safe_load(frontmatter_str)
    except Exception as e:
        errors.append(f"frontmatter: YAML parse error — {e}")
        return None, errors

    if data is None:
        errors.append("frontmatter: empty or null YAML")
        return None, errors

    if not isinstance(data, dict):
        errors.append("frontmatter: expected a YAML mapping")
        return None, errors

    return data, errors


def validate_frontmatter(data):
    """Validate frontmatter fields. Returns list of error strings."""
    errors = []

    # schema_version (required)
    sv = data.get("schema_version")
    if sv is None:
        errors.append("frontmatter: missing required field 'schema_version'")
    elif str(sv) != "1.0":
        errors.append(f"frontmatter: schema_version expected '1.0', got '{sv}'")

    # meeting_id (required)
    mid = data.get("meeting_id")
    if mid is None:
        errors.append("frontmatter: missing required field 'meeting_id'")
    elif not isinstance(mid, str):
        errors.append(f"frontmatter: meeting_id expected string, got {type(mid).__name__}")
    elif not MEETING_ID_PATTERN.match(mid):
        errors.append(
            f"frontmatter: meeting_id '{mid}' does not match expected pattern "
            f"YYYY-MM-DD-<body-slug>"
        )

    # persona_id (required)
    pid = data.get("persona_id")
    if pid is None:
        errors.append("frontmatter: missing required field 'persona_id'")
    elif not isinstance(pid, str):
        errors.append(f"frontmatter: persona_id expected string, got {type(pid).__name__}")
    elif not PERSONA_ID_PATTERN.match(pid):
        errors.append(
            f"frontmatter: persona_id '{pid}' does not match expected pattern PERSONA-NNN"
        )

    # Optional date fields
    for field in ("meeting_date", "interpretation_date"):
        val = data.get(field)
        if val is not None:
            _, date_errs = parse_date(val, f"frontmatter.{field}")
            errors.extend(date_errs)

    # Check for unexpected fields
    known_fields = {
        "schema_version", "meeting_id", "persona_id", "persona_name",
        "meeting_date", "meeting_title", "interpretation_date",
        "interpreter_model",
    }
    for key in data:
        if key not in known_fields:
            errors.append(f"frontmatter: unexpected field '{key}'")

    return errors


def validate_structured_points(body):
    """Validate the Structured Points section. Returns (point_count, errors)."""
    errors = []

    # Find the Structured Points section
    sp_match = re.search(r"^###?\s+Structured\s+Points\s*$", body, re.MULTILINE)
    if not sp_match:
        errors.append("body: missing '### Structured Points' section")
        return 0, errors

    # Get content between Structured Points and the next ### section
    sp_start = sp_match.end()
    next_section = re.search(r"^###?\s+", body[sp_start:], re.MULTILINE)
    if next_section:
        sp_content = body[sp_start:sp_start + next_section.start()]
    else:
        sp_content = body[sp_start:]

    # Find individual points (#### headers)
    point_headers = list(re.finditer(r"^####\s+\d+\.\s+(.+)$", sp_content, re.MULTILINE))

    if len(point_headers) == 0:
        errors.append("structured_points: no points found (expected 5-8)")
        return 0, errors

    if len(point_headers) < 5:
        errors.append(
            f"structured_points: found {len(point_headers)} point(s), expected at least 5"
        )
    elif len(point_headers) > 8:
        errors.append(
            f"structured_points: found {len(point_headers)} point(s), expected at most 8"
        )

    # Validate each point
    for i, header in enumerate(point_headers):
        point_num = i + 1
        prefix = f"structured_points[{point_num}]"

        # Get this point's content (up to next point or end of section)
        start = header.end()
        if i + 1 < len(point_headers):
            end = point_headers[i + 1].start()
        else:
            end = len(sp_content)
        point_text = sp_content[start:end]

        # Check required fields
        _validate_point_fields(point_text, prefix, errors)

    return len(point_headers), errors


def _validate_point_fields(point_text, prefix, errors):
    """Validate fields within a single structured point."""
    # Fact
    fact_match = re.search(r"\*\*Fact:\*\*\s*(.+)", point_text)
    if not fact_match:
        errors.append(f"{prefix}: missing '**Fact:**' field")
    elif len(fact_match.group(1).strip()) < 10:
        errors.append(f"{prefix}: fact is too short (< 10 chars)")

    # Source reference
    source_match = re.search(r"\*\*Source(?:_reference)?:\*\*\s*(.+)", point_text)
    if not source_match:
        errors.append(f"{prefix}: missing '**Source:**' field")
    elif len(source_match.group(1).strip()) < 1:
        errors.append(f"{prefix}: source reference is empty")

    # Emotional valence
    valence_match = re.search(
        r"\*\*Emotional\s+valence:\*\*\s*(\S+)", point_text
    )
    if not valence_match:
        errors.append(f"{prefix}: missing '**Emotional valence:**' field")
    else:
        valence = valence_match.group(1).strip().rstrip(",.")
        if valence not in VALID_EMOTIONAL_VALENCES:
            errors.append(
                f"{prefix}: invalid emotional_valence '{valence}' — "
                f"expected one of: {', '.join(sorted(VALID_EMOTIONAL_VALENCES))}"
            )

    # Threat level
    threat_match = re.search(
        r"\*\*Threat\s+level:\*\*\s*(\S+)", point_text
    )
    if not threat_match:
        errors.append(f"{prefix}: missing '**Threat level:**' field")
    else:
        threat = threat_match.group(1).strip().rstrip(",.")
        if threat not in VALID_THREAT_LEVELS:
            errors.append(
                f"{prefix}: invalid threat_level '{threat}' — "
                f"expected one of: {', '.join(sorted(VALID_THREAT_LEVELS))}"
            )

    # Open question (optional — just check format if present)
    # No validation needed beyond presence check


def validate_journey_map(body):
    """Validate the Journey Map section. Returns (beat_count, errors)."""
    errors = []

    jm_match = re.search(r"^###?\s+Journey\s+Map\s*$", body, re.MULTILINE)
    if not jm_match:
        errors.append("body: missing '### Journey Map' section")
        return 0, errors

    # Get content between Journey Map and the next ### section
    jm_start = jm_match.end()
    next_section = re.search(r"^###?\s+", body[jm_start:], re.MULTILINE)
    if next_section:
        jm_content = body[jm_start:jm_start + next_section.start()]
    else:
        jm_content = body[jm_start:]

    # Find the table — look for the header row with expected columns
    table_header = re.search(
        r"\|\s*Beat\s*\|\s*Time\s*\|\s*Label\s*\|\s*Emotional\s+State\s*\|\s*Trigger\s*\|\s*Internal\s+Monologue\s*\|",
        jm_content,
        re.IGNORECASE,
    )
    if not table_header:
        errors.append(
            "journey_map: table header not found — expected columns: "
            "Beat, Time, Label, Emotional State, Trigger, Internal Monologue"
        )
        return 0, errors

    # Find data rows (skip header and separator)
    table_start = table_header.end()
    table_lines = jm_content[table_start:].strip().split("\n")

    # Skip separator row (|---|---|...)
    data_lines = []
    for line in table_lines:
        line = line.strip()
        if not line:
            break
        if line.startswith("|") and not re.match(r"^\|[\s\-|:]+\|$", line):
            data_lines.append(line)

    if len(data_lines) == 0:
        errors.append("journey_map: no data rows found in table")
        return 0, errors

    if len(data_lines) < 4:
        errors.append(
            f"journey_map: found {len(data_lines)} beat(s), expected at least 4"
        )
    elif len(data_lines) > 6:
        errors.append(
            f"journey_map: found {len(data_lines)} beat(s), expected at most 6"
        )

    # Validate each row has 6 cells
    for i, line in enumerate(data_lines):
        beat_num = i + 1
        cells = [c.strip() for c in line.split("|")]
        # Split by | gives empty strings at start/end for properly formatted rows
        cells = [c for c in cells if c or c == ""]
        # A proper table row |a|b|c|d|e|f| splits into ['', 'a', 'b', 'c', 'd', 'e', 'f', '']
        # After filtering we need at least 6 non-boundary cells
        raw_cells = line.split("|")
        # Remove first and last empty from pipe-delimited
        if raw_cells and raw_cells[0].strip() == "":
            raw_cells = raw_cells[1:]
        if raw_cells and raw_cells[-1].strip() == "":
            raw_cells = raw_cells[:-1]
        content_cells = [c.strip() for c in raw_cells]

        if len(content_cells) < 6:
            errors.append(
                f"journey_map[{beat_num}]: expected 6 columns, found {len(content_cells)}"
            )
            continue

        # Check that key cells are non-empty
        col_names = ["Beat", "Time", "Label", "Emotional State", "Trigger", "Internal Monologue"]
        for j, col_name in enumerate(col_names):
            if j < len(content_cells) and not content_cells[j]:
                errors.append(
                    f"journey_map[{beat_num}]: empty '{col_name}' column"
                )

    return len(data_lines), errors


def validate_reactions(body):
    """Validate the Reactions section. Returns errors."""
    errors = []

    rx_match = re.search(r"^###?\s+Reactions\s*$", body, re.MULTILINE)
    if not rx_match:
        errors.append("body: missing '### Reactions' section")
        return errors

    # Get content after Reactions header (to end of document or next ### section)
    rx_start = rx_match.end()
    next_section = re.search(r"^###?\s+", body[rx_start:], re.MULTILINE)
    if next_section:
        rx_content = body[rx_start:rx_start + next_section.start()].strip()
    else:
        rx_content = body[rx_start:].strip()

    if not rx_content:
        errors.append("reactions: section is empty")
    elif len(rx_content) < 100:
        errors.append(
            f"reactions: content is too short ({len(rx_content)} chars, "
            f"expected at least 100)"
        )

    return errors


def validate_interpretation(text, yaml_mod):
    """Validate a full interpretation document. Returns list of error strings."""
    errors = []

    # Split frontmatter and body
    fm_str, body = split_frontmatter_and_body(text)
    if fm_str is None:
        errors.append("document: missing or malformed YAML frontmatter (no --- delimiters)")
        return errors

    # Parse and validate frontmatter
    data, parse_errors = parse_frontmatter(fm_str, yaml_mod)
    errors.extend(parse_errors)
    if data is not None:
        errors.extend(validate_frontmatter(data))

    # Validate body sections
    if not body:
        errors.append("document: body is empty (no content after frontmatter)")
        return errors

    _, sp_errors = validate_structured_points(body)
    errors.extend(sp_errors)

    _, jm_errors = validate_journey_map(body)
    errors.extend(jm_errors)

    rx_errors = validate_reactions(body)
    errors.extend(rx_errors)

    return errors


def find_all_interpretations():
    """Find all interpretation documents under data/interpretation/meetings/."""
    meetings_dir = PROJECT_ROOT / "data" / "interpretation" / "meetings"
    if not meetings_dir.exists():
        return []
    return sorted(meetings_dir.glob("*/*.md"))


def main():
    parser = argparse.ArgumentParser(
        description="Validate interpretation output documents"
    )
    parser.add_argument(
        "document", nargs="?",
        help="Path to an interpretation .md file to validate",
    )
    parser.add_argument(
        "--all", action="store_true",
        help="Validate all interpretation documents in data/interpretation/meetings/",
    )
    args = parser.parse_args()

    if not args.document and not args.all:
        parser.error("either provide a document path or use --all")

    # Import yaml here so we get a clear error if it's missing
    try:
        import yaml
    except ImportError:
        log.error("PyYAML is required: pip install pyyaml")
        sys.exit(2)

    total_errors = 0
    files_checked = 0

    if args.all:
        docs = find_all_interpretations()
        if not docs:
            log.info("No interpretation documents found in data/interpretation/meetings/")
        for doc_path in docs:
            files_checked += 1
            errs = _validate_file(doc_path, yaml_mod=yaml)
            total_errors += errs

        log.info("")
        log.info("Checked %d file(s), %d error(s) total", files_checked, total_errors)

    else:
        doc_path = Path(args.document).resolve()
        if not doc_path.exists():
            log.error("File not found: %s", doc_path)
            sys.exit(2)

        total_errors = _validate_file(doc_path, yaml_mod=yaml)

    sys.exit(1 if total_errors > 0 else 0)


def _validate_file(doc_path, yaml_mod):
    """Load and validate a single interpretation file. Returns error count."""
    rel = (
        doc_path.relative_to(PROJECT_ROOT)
        if doc_path.is_relative_to(PROJECT_ROOT)
        else doc_path
    )

    try:
        text = doc_path.read_text(encoding="utf-8")
    except Exception as e:
        log.error("%s — read error: %s", rel, e)
        return 1

    if not text.strip():
        log.error("%s — file is empty", rel)
        return 1

    errors = validate_interpretation(text, yaml_mod)

    if errors:
        log.error("%s — %d validation error(s):", rel, len(errors))
        for err in errors:
            log.error("  %s", err)
    else:
        log.info("%s — valid", rel)

    return len(errors)


if __name__ == "__main__":
    main()

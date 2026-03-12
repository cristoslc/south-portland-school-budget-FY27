#!/usr/bin/env python3
"""Cumulative Fold Engine — SPEC-021.

Integrates per-meeting interpretations (SPEC-018 format) into cumulative
narrative records (SPEC-020 format). Uses a log-structured approach per
SPIKE-006: each fold produces a new immutable cumulative record and
regenerates the summary view.

Pipeline:
  1. Load persona definition + per-meeting interpretation
  2. Load all prior cumulative records for context
  3. Construct fold prompt → LLM → new cumulative record
  4. Validate record against schema
  5. Regenerate summary view from all records

Usage:
    python3 scripts/fold_meeting.py <meeting-id>
    python3 scripts/fold_meeting.py <meeting-id> --dry-run
    python3 scripts/fold_meeting.py <meeting-id> --force
    python3 scripts/fold_meeting.py <meeting-id> --persona PERSONA-001
    python3 scripts/fold_meeting.py <meeting-id> --force --persona PERSONA-003

Exit codes:
    0 — all folds succeeded (or dry-run completed)
    1 — one or more folds failed
    2 — usage error (bad arguments, missing files, missing dependencies)
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
log = logging.getLogger("fold_meeting")

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent

PERSONA_DIR = PROJECT_ROOT / "docs" / "persona" / "Validated"
MEETINGS_DIR = PROJECT_ROOT / "data" / "interpretation" / "meetings"
CUMULATIVE_DIR = PROJECT_ROOT / "data" / "interpretation" / "cumulative"
BUNDLES_DIR = PROJECT_ROOT / "data" / "interpretation" / "bundles"

MODEL_ID = "claude-sonnet-4-20250514"

# Persona ID patterns
PERSONA_ID_RE = re.compile(r"^PERSONA-\d{3}$")
PERSONA_DIR_RE = re.compile(r"^\(PERSONA-(\d{3})\)-(.+)$")

# Word budget thresholds (soft warnings, not hard failures)
RECORD_INTERPRETATION_WORD_LIMIT = 400
SUMMARY_UNDERSTANDING_WORD_LIMIT = 300


# ============================================================================
# Persona Loader (reuses patterns from interpret_meeting.py)
# ============================================================================

class Persona:
    """A validated persona definition loaded from docs/persona/Validated/."""

    def __init__(self, persona_id, name, content, archetype=None):
        self.id = persona_id
        self.name = name
        self.content = content
        self.archetype = archetype

    def __repr__(self):
        return f"Persona({self.id}, {self.name})"


def load_personas(persona_dir=None):
    """Load all Validated persona definitions.

    Reads each persona markdown file, extracts the persona's first name
    from the H1 heading, and returns a list of Persona objects sorted by ID.
    """
    if persona_dir is None:
        persona_dir = PERSONA_DIR

    personas = []

    if not persona_dir.exists():
        log.error("Persona directory not found: %s", persona_dir)
        return personas

    for subdir in sorted(persona_dir.iterdir()):
        if not subdir.is_dir():
            continue

        dir_match = PERSONA_DIR_RE.match(subdir.name)
        if not dir_match:
            log.warning("Skipping non-persona directory: %s", subdir.name)
            continue

        persona_num = dir_match.group(1)
        persona_id = f"PERSONA-{persona_num}"

        # Find the markdown file inside
        md_files = list(subdir.glob("*.md"))
        if not md_files:
            log.warning("No markdown file found in %s", subdir.name)
            continue

        md_path = md_files[0]
        content = md_path.read_text(encoding="utf-8")

        name = _extract_persona_name(content, persona_id)
        archetype = _extract_section(content, "Archetype Label")

        personas.append(Persona(
            persona_id=persona_id,
            name=name,
            content=content,
            archetype=archetype,
        ))

    log.info("Loaded %d persona(s) from %s", len(personas), persona_dir)
    return personas


def _extract_persona_name(content, persona_id):
    """Extract the first name from the H1 heading of a persona document."""
    h1_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
    if not h1_match:
        log.warning("%s: no H1 heading found, using ID as name", persona_id)
        return persona_id

    heading = h1_match.group(1).strip()
    paren = heading.find("(")
    if paren > 0:
        return heading[:paren].strip()
    return heading


def _extract_section(content, section_title):
    """Extract the body text of a ## section from markdown content."""
    pattern = rf"^##\s+{re.escape(section_title)}\s*$"
    match = re.search(pattern, content, re.MULTILINE)
    if not match:
        return None

    start = match.end()
    next_heading = re.search(r"^##\s+", content[start:], re.MULTILINE)
    if next_heading:
        section_text = content[start:start + next_heading.start()]
    else:
        section_text = content[start:]

    return section_text.strip()


def _extract_persona_body(content):
    """Extract the persona content body (everything after frontmatter).

    Strips the YAML frontmatter and lifecycle table, returning the
    substantive persona definition for use in the prompt.
    """
    body = content
    if body.lstrip("\ufeff").startswith("---"):
        end = body.find("\n---", 3)
        if end != -1:
            body = body[end + 4:].strip()

    lifecycle_match = re.search(r"^##\s+Lifecycle\s*$", body, re.MULTILINE)
    if lifecycle_match:
        body = body[:lifecycle_match.start()].strip()

    return body


# ============================================================================
# Cumulative Record Loader
# ============================================================================

def load_prior_records(persona_id):
    """Load all existing cumulative records for a persona, sorted chronologically.

    Returns:
        list of (meeting_date_str, content_str) tuples, sorted by date.
    """
    persona_cumulative_dir = CUMULATIVE_DIR / persona_id
    if not persona_cumulative_dir.exists():
        return []

    records = []
    for md_file in sorted(persona_cumulative_dir.glob("*.md")):
        if md_file.name == "summary.md":
            continue
        # File name is the meeting date: YYYY-MM-DD.md
        date_str = md_file.stem
        content = md_file.read_text(encoding="utf-8")
        records.append((date_str, content))

    return records


def get_meeting_date_from_id(meeting_id):
    """Extract the date portion from a meeting-id like '2026-03-02-school-board'.

    Returns the date string (e.g., '2026-03-02').
    """
    parts = meeting_id.split("-")
    if len(parts) >= 3:
        return "-".join(parts[:3])
    return meeting_id


def get_body_from_id(meeting_id):
    """Extract the governing body from a meeting-id.

    '2026-03-02-school-board' -> 'school-board'
    """
    parts = meeting_id.split("-")
    if len(parts) >= 4:
        return "-".join(parts[3:])
    return "school-board"


def load_bundle_manifest(meeting_id):
    """Load the bundle manifest for a meeting to get metadata.

    Returns a dict with meeting metadata, or None if manifest not found.
    """
    try:
        import yaml
    except ImportError:
        log.warning("PyYAML not installed — cannot load bundle manifest")
        return None

    manifest_path = BUNDLES_DIR / meeting_id / "manifest.yaml"
    if not manifest_path.exists():
        log.warning("Bundle manifest not found: %s", manifest_path)
        return None

    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = yaml.safe_load(f)

    return manifest


# ============================================================================
# Interpretation Loader
# ============================================================================

def load_interpretation(meeting_id, persona_id):
    """Load the per-meeting interpretation output for a persona.

    Returns the interpretation content as a string, or None if not found.
    """
    interp_path = MEETINGS_DIR / meeting_id / f"{persona_id}.md"
    if not interp_path.exists():
        return None
    return interp_path.read_text(encoding="utf-8")


# ============================================================================
# Task 1: Fold Prompt Template
# ============================================================================

FOLD_SYSTEM_PROMPT = """\
You are a cumulative interpretation engine for a municipal school budget \
analysis project. Your job is to integrate a new per-meeting interpretation \
into a persona's evolving cumulative narrative — producing a new immutable \
record that captures what this meeting means for this persona given \
everything they have experienced so far.

Your output must be grounded in evidence. The per-meeting interpretation \
provides the new information; the prior cumulative records provide the \
persona's journey to date. Your task is to SYNTHESIZE, not merely append.

Critical instructions:
- Detect what SHIFTED: compare the new interpretation against prior records \
to identify position_shift deltas (the persona's stance changed).
- Detect SUPERSESSIONS: if information in the new interpretation explicitly \
replaces or contradicts a prior belief, mark it as a supersession delta \
with the supersedes field referencing the original position and its date.
- Track THREADS: if the new interpretation raises questions, mark them as \
thread_opened. If it answers questions from prior records' open threads, \
mark them as thread_resolved.
- Identify genuinely NEW INFORMATION: facts this persona did not previously \
know, tagged as new_information deltas.
- Write the interpretation section (~200-400 words) as a narrative of what \
this meeting means to this persona given their accumulated journey. It \
should reflect the persona's voice and concerns, not analyst language.
- Write the emotional_register as 1-2 sentences capturing the persona's \
affective state after this meeting.

Output ONLY the cumulative record document in the exact format specified. \
Do not include any preamble, explanation, or commentary outside the document."""


def build_fold_prompt(persona, interpretation_content, prior_records,
                      meeting_id, manifest):
    """Construct the fold prompt for generating a new cumulative record.

    Args:
        persona: Persona object
        interpretation_content: raw content of the per-meeting interpretation
        prior_records: list of (date_str, content_str) tuples
        meeting_id: meeting identifier string
        manifest: bundle manifest dict (or None)

    Returns:
        str: The assembled user prompt.
    """
    persona_body = _extract_persona_body(persona.content)
    meeting_date = get_meeting_date_from_id(meeting_id)
    body_name = get_body_from_id(meeting_id)

    # Determine meeting type and title from manifest
    meeting_type = "regular"
    meeting_title = meeting_id
    if manifest:
        meeting_type = manifest.get("meeting_type", "regular")
        raw_title = manifest.get("title", meeting_id)
        # Normalize em-dash to double-dash for consistency with exemplars
        meeting_title = raw_title.replace(" — ", " -- ")

    # Determine prior_meeting reference
    if prior_records:
        prior_meeting_date = prior_records[-1][0]
    else:
        prior_meeting_date = "null"

    # Build the prior records context block
    if prior_records:
        prior_block_parts = []
        for date_str, content in prior_records:
            prior_block_parts.append(
                f"--- Record: {date_str} ---\n\n{content}"
            )
        prior_block = "\n\n".join(prior_block_parts)
    else:
        prior_block = (
            "(No prior cumulative records exist. This is the first record "
            "for this persona. Set prior_meeting to null in the frontmatter. "
            "All information from the interpretation should be categorized "
            "as new_information, thread_opened, etc. — there are no prior "
            "positions to shift or supersede.)"
        )

    # Format the prior_meeting value for frontmatter instruction
    if prior_meeting_date == "null":
        prior_meeting_yaml = "null"
    else:
        prior_meeting_yaml = f'"{prior_meeting_date}"'

    prompt = f"""\
<persona>
{persona_body}
</persona>

<prior_cumulative_records>
{prior_block}
</prior_cumulative_records>

<new_interpretation>
{interpretation_content}
</new_interpretation>

<instruction>
Produce a new cumulative interpretation record for {persona.name} \
({persona.id}) based on the new per-meeting interpretation above, \
considering all prior cumulative records for context.

Your output must follow this EXACT markdown format with YAML frontmatter:

---
schema_version: "1.0"
persona_id: "{persona.id}"
persona_name: "{persona.name}"
meeting_date: "{meeting_date}"
meeting_type: {meeting_type}
body: {body_name}
prior_meeting: {prior_meeting_yaml}
interpretation_date: "{datetime.date.today().isoformat()}"
---

# Cumulative Record: {persona.name} ({persona.id})
## Meeting: {meeting_title} -- {meeting_date}

### Interpretation

[Write ~200-400 words. Narrate what this meeting means for {persona.name} \
given their entire journey to date. Reference specific facts from the new \
interpretation. Note how their understanding has evolved from prior records. \
Use present tense for this meeting's content. Write in a style appropriate \
to this persona's voice — not analyst language.]

### Deltas

| Category | Description | Evidence Ref | Supersedes |
|----------|-------------|--------------|------------|
[Produce one row per delta. Categories must be exactly one of: \
new_information, position_shift, supersession, thread_opened, thread_resolved.

For new_information: facts from the new interpretation that the persona \
did not previously know.

For position_shift: describe how the persona's stance has changed. The \
description should capture both the old and new posture.

For supersession: the Description column states the new understanding. \
The Supersedes column states the old understanding being replaced, with \
date of origin (e.g., '"difficult budget year" (2026-01-12)'). \
There must be a clear before/after — do not use supersession for \
incremental additions.

For thread_opened: a new unresolved question. Evidence Ref is optional.

For thread_resolved: a previously open thread that is now answered. \
Check the prior cumulative records for open threads that may now be resolved.

Use -- for empty cells. Every delta must have a non-empty Description.]

### Emotional Register

[1-2 sentences capturing {persona.name}'s emotional state after this meeting. \
Be specific to this persona's character and situation.]
</instruction>"""

    return prompt


def build_summary_prompt(persona, all_records):
    """Construct the prompt for regenerating a persona's summary view.

    Args:
        persona: Persona object
        all_records: list of (date_str, content_str) tuples, chronologically sorted

    Returns:
        str: The assembled user prompt.
    """
    records_block_parts = []
    for date_str, content in all_records:
        records_block_parts.append(
            f"--- Record: {date_str} ---\n\n{content}"
        )
    records_block = "\n\n".join(records_block_parts)

    last_meeting_date = all_records[-1][0]
    record_count = len(all_records)
    today = datetime.date.today().isoformat()

    prompt = f"""\
<persona_records>
{records_block}
</persona_records>

<instruction>
Generate a cumulative summary view for {persona.name} ({persona.id}) by \
synthesizing ALL {record_count} cumulative records above.

Your output must follow this EXACT markdown format with YAML frontmatter:

---
schema_version: "1.0"
persona_id: "{persona.id}"
persona_name: "{persona.name}"
last_meeting_date: "{last_meeting_date}"
record_count: {record_count}
generated_date: "{today}"
---

# Cumulative Summary: {persona.name} ({persona.id})

### Current Understanding

[Write ~150-300 words. Synthesize {persona.name}'s current understanding \
of the budget situation as of the most recent meeting. This is the \
authoritative current-state view. Present tense. Incorporate all major \
facts, positions, and concerns from across all records. Do not merely \
repeat the most recent record — synthesize the full journey.]

### Timeline of Understanding Shifts

[Numbered list, one entry per meeting. Each entry starts with the meeting \
date in bold, followed by a dash and a 1-2 sentence summary of how \
{persona.name}'s understanding shifted at that meeting. Derived from the \
interpretation and delta entries across all records.]

### Active Supersessions

| What Changed | From | To | When |
|--------------|------|----|------|
[Table of beliefs that have been explicitly replaced. Derived from \
supersession deltas across all records. If no supersessions exist, \
include the table header with no data rows.]

### Open Threads

[Bulleted list of unresolved questions. Derived by netting thread_opened \
deltas against thread_resolved deltas across all records. If a thread was \
opened in an earlier record and resolved in a later one, it should NOT \
appear here — it goes in Resolved Threads.]

### Resolved Threads

[Bulleted list with format: **Thread description**: resolution (resolved \
YYYY-MM-DD). Derived from thread_resolved deltas. If no threads have been \
resolved, write "None yet."]
</instruction>"""

    return prompt


SUMMARY_SYSTEM_PROMPT = """\
You are a summary synthesis engine for a municipal school budget analysis \
project. Your job is to regenerate a cumulative summary view for a persona \
by processing all of their immutable cumulative interpretation records in \
chronological order.

The summary view is a derived artifact — it must be entirely derivable from \
the records provided. Do not invent information not present in the records.

Output ONLY the summary document in the exact format specified. Do not \
include any preamble, explanation, or commentary outside the document."""


def estimate_tokens(text):
    """Rough token estimate: ~4 chars per token for English text."""
    return len(text) // 4


# ============================================================================
# Task 3: Idempotency Check
# ============================================================================

def record_exists(persona_id, meeting_date):
    """Check if a cumulative record already exists for this persona and meeting date.

    Args:
        persona_id: e.g., "PERSONA-001"
        meeting_date: e.g., "2026-03-02"

    Returns:
        bool: True if the record file exists.
    """
    record_path = CUMULATIVE_DIR / persona_id / f"{meeting_date}.md"
    return record_path.exists()


# ============================================================================
# Task 4: Word Budget Enforcement
# ============================================================================

def check_record_word_budget(record_text):
    """Check the interpretation section word count against the budget.

    Returns a list of warning strings (empty if within budget).
    """
    warnings = []

    # Extract interpretation section
    interp_match = re.search(
        r"###\s+Interpretation\s*\n(.*?)(?=\n###\s+|\Z)",
        record_text, re.DOTALL
    )
    if interp_match:
        interp_text = interp_match.group(1).strip()
        word_count = len(interp_text.split())
        if word_count > RECORD_INTERPRETATION_WORD_LIMIT:
            warnings.append(
                f"Interpretation section is {word_count} words "
                f"(budget: {RECORD_INTERPRETATION_WORD_LIMIT})"
            )

    return warnings


def check_summary_word_budget(summary_text):
    """Check the current_understanding section word count against the budget.

    Returns a list of warning strings (empty if within budget).
    """
    warnings = []

    cu_match = re.search(
        r"###\s+Current Understanding\s*\n(.*?)(?=\n###\s+|\Z)",
        summary_text, re.DOTALL
    )
    if cu_match:
        cu_text = cu_match.group(1).strip()
        word_count = len(cu_text.split())
        if word_count > SUMMARY_UNDERSTANDING_WORD_LIMIT:
            warnings.append(
                f"Current Understanding section is {word_count} words "
                f"(budget: {SUMMARY_UNDERSTANDING_WORD_LIMIT})"
            )

    return warnings


# ============================================================================
# Quick Validation
# ============================================================================

def _quick_validate_record(text):
    """Quick structural validation of a cumulative record.

    Returns list of error strings (empty = looks good).
    """
    errors = []

    stripped = text.lstrip("\ufeff").strip()
    if not stripped.startswith("---"):
        errors.append("missing YAML frontmatter (no opening ---)")

    if "### Interpretation" not in text:
        errors.append("missing '### Interpretation' section")
    if "### Deltas" not in text:
        errors.append("missing '### Deltas' section")
    if "### Emotional Register" not in text:
        errors.append("missing '### Emotional Register' section")

    # Check delta table has at least one data row
    delta_match = re.search(
        r"###\s+Deltas\s*\n(.*?)(?=\n###\s+|\Z)",
        text, re.DOTALL
    )
    if delta_match:
        delta_section = delta_match.group(1)
        # Count data rows (lines starting with | that are not header/separator)
        data_rows = 0
        for line in delta_section.strip().split("\n"):
            line = line.strip()
            if line.startswith("|") and not re.match(r"^\|[\s\-|:]+\|$", line):
                if "Category" not in line or "Description" not in line:
                    data_rows += 1
        if data_rows == 0:
            errors.append("delta table has no data rows")

    return errors


def _quick_validate_summary(text):
    """Quick structural validation of a summary view.

    Returns list of error strings (empty = looks good).
    """
    errors = []

    stripped = text.lstrip("\ufeff").strip()
    if not stripped.startswith("---"):
        errors.append("missing YAML frontmatter (no opening ---)")

    if "### Current Understanding" not in text:
        errors.append("missing '### Current Understanding' section")
    if "### Timeline of Understanding Shifts" not in text:
        errors.append("missing '### Timeline of Understanding Shifts' section")
    if "### Active Supersessions" not in text:
        errors.append("missing '### Active Supersessions' section")
    if "### Open Threads" not in text:
        errors.append("missing '### Open Threads' section")
    if "### Resolved Threads" not in text:
        errors.append("missing '### Resolved Threads' section")

    return errors


# ============================================================================
# Task 2 & 5: Fold Runner
# ============================================================================

def run_fold(meeting_id, personas, *, force=False, single_persona=None,
             dry_run=False):
    """Run the cumulative fold for all (or one) persona against a meeting.

    Args:
        meeting_id: meeting identifier (e.g., '2026-03-02-school-board')
        personas: list of Persona objects
        force: if True, regenerate even if record exists
        single_persona: if set, only process this PERSONA-NNN
        dry_run: if True, do everything except LLM calls

    Returns:
        dict with counts: processed, skipped, failed, no_interpretation
    """
    meeting_date = get_meeting_date_from_id(meeting_id)

    # Load bundle manifest for meeting metadata
    manifest = load_bundle_manifest(meeting_id)

    # Filter to single persona if requested
    if single_persona:
        personas = [p for p in personas if p.id == single_persona]
        if not personas:
            log.error("Persona %s not found in loaded personas", single_persona)
            return {"processed": 0, "skipped": 0, "failed": 1,
                    "no_interpretation": 0}

    stats = {"processed": 0, "skipped": 0, "failed": 0,
             "no_interpretation": 0}

    # Import anthropic lazily — only needed for actual LLM calls
    anthropic_client = None
    if not dry_run:
        try:
            import anthropic
        except ImportError:
            log.error(
                "The 'anthropic' package is required for live runs. "
                "Install it with: pip install anthropic\n"
                "For testing without LLM calls, use --dry-run."
            )
            sys.exit(2)

        import os
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            log.error(
                "ANTHROPIC_API_KEY environment variable is not set. "
                "Set it or use --dry-run for testing."
            )
            sys.exit(2)

        anthropic_client = anthropic.Anthropic(api_key=api_key)

    # Track which personas were processed (for summary regeneration)
    processed_personas = []

    for persona in personas:
        log.info("--- %s (%s) ---", persona.id, persona.name)

        # Check if interpretation exists for this meeting
        interpretation = load_interpretation(meeting_id, persona.id)
        if interpretation is None:
            log.info("  [skip] No interpretation found for %s in %s",
                     persona.id, meeting_id)
            stats["no_interpretation"] += 1
            continue

        # Task 3: Idempotency check
        if record_exists(persona.id, meeting_date) and not force:
            log.info("  [skip] Cumulative record already exists: %s/%s.md",
                     persona.id, meeting_date)
            stats["skipped"] += 1
            continue

        if record_exists(persona.id, meeting_date) and force:
            log.info("  [force] Regenerating existing record: %s/%s.md",
                     persona.id, meeting_date)

        # Load prior records
        prior_records = load_prior_records(persona.id)

        # If we're regenerating, exclude the record for this meeting date
        # from prior records (it will be overwritten)
        if force:
            prior_records = [
                (d, c) for d, c in prior_records if d != meeting_date
            ]

        log.info("  Prior records: %d", len(prior_records))

        # Build the fold prompt
        fold_prompt = build_fold_prompt(
            persona, interpretation, prior_records, meeting_id, manifest
        )
        prompt_tokens = estimate_tokens(FOLD_SYSTEM_PROMPT + fold_prompt)
        log.info("  [prompt] Fold prompt — ~%d tokens", prompt_tokens)

        if dry_run:
            log.info("  [dry-run] Would call LLM (%s) to generate record",
                     MODEL_ID)
            log.info("  [dry-run] Would write to %s/%s.md",
                     persona.id, meeting_date)
            stats["processed"] += 1
            processed_personas.append(persona)
            continue

        # --- LLM call for cumulative record ---
        try:
            log.info("  [call] Generating cumulative record via %s ...",
                     MODEL_ID)
            response = anthropic_client.messages.create(  # type: ignore[union-attr]
                model=MODEL_ID,
                max_tokens=4096,
                temperature=0,
                system=FOLD_SYSTEM_PROMPT,
                messages=[{"role": "user", "content": fold_prompt}],
            )

            record_text = ""
            for block in response.content:
                if hasattr(block, "text"):
                    record_text += block.text  # type: ignore[union-attr]

            if not record_text.strip():
                log.error("  [fail] Empty response from LLM for record")
                stats["failed"] += 1
                continue

            # Quick validate
            validation_errors = _quick_validate_record(record_text)
            if validation_errors:
                log.warning("  [warn] %d validation issue(s) in record:",
                            len(validation_errors))
                for err in validation_errors:
                    log.warning("    %s", err)

            # Task 4: Word budget check
            budget_warnings = check_record_word_budget(record_text)
            for w in budget_warnings:
                log.warning("  [budget] %s", w)

            # Write the record
            record_dir = CUMULATIVE_DIR / persona.id
            record_dir.mkdir(parents=True, exist_ok=True)
            record_path = record_dir / f"{meeting_date}.md"
            record_path.write_text(record_text, encoding="utf-8")
            log.info("  [done] Wrote record: %s (%d chars)",
                     record_path.relative_to(PROJECT_ROOT),
                     len(record_text))

            # Log token usage
            if hasattr(response, "usage"):
                log.info("  [tokens] input: %d, output: %d",
                         response.usage.input_tokens,
                         response.usage.output_tokens)

            stats["processed"] += 1
            processed_personas.append(persona)

        except Exception as e:
            log.error("  [fail] Record generation failed: %s", e)
            stats["failed"] += 1
            continue

    # --- Regenerate summary views for processed personas ---
    if processed_personas and not dry_run:
        log.info("")
        log.info("=== Regenerating summary views ===")
        for persona in processed_personas:
            _regenerate_summary(persona, anthropic_client)

    elif processed_personas and dry_run:
        log.info("")
        log.info("=== Summary views (dry-run) ===")
        for persona in processed_personas:
            all_records = load_prior_records(persona.id)
            log.info("  [dry-run] Would regenerate summary for %s "
                     "(%d records)", persona.id, len(all_records))

    return stats


def _regenerate_summary(persona, anthropic_client):
    """Regenerate the summary view for a persona from all cumulative records.

    Args:
        persona: Persona object
        anthropic_client: initialized Anthropic client
    """
    log.info("--- Summary: %s (%s) ---", persona.id, persona.name)

    all_records = load_prior_records(persona.id)
    if not all_records:
        log.warning("  No cumulative records found for %s — skipping summary",
                     persona.id)
        return

    log.info("  Records to synthesize: %d", len(all_records))

    summary_prompt = build_summary_prompt(persona, all_records)
    prompt_tokens = estimate_tokens(SUMMARY_SYSTEM_PROMPT + summary_prompt)
    log.info("  [prompt] Summary prompt — ~%d tokens", prompt_tokens)

    try:
        log.info("  [call] Generating summary via %s ...", MODEL_ID)
        response = anthropic_client.messages.create(  # type: ignore[union-attr]
            model=MODEL_ID,
            max_tokens=4096,
            temperature=0,
            system=SUMMARY_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": summary_prompt}],
        )

        summary_text = ""
        for block in response.content:
            if hasattr(block, "text"):
                summary_text += block.text  # type: ignore[union-attr]

        if not summary_text.strip():
            log.error("  [fail] Empty response from LLM for summary")
            return

        # Quick validate
        validation_errors = _quick_validate_summary(summary_text)
        if validation_errors:
            log.warning("  [warn] %d validation issue(s) in summary:",
                        len(validation_errors))
            for err in validation_errors:
                log.warning("    %s", err)

        # Task 4: Word budget check for summary
        budget_warnings = check_summary_word_budget(summary_text)
        for w in budget_warnings:
            log.warning("  [budget] %s", w)

        # Write the summary
        summary_path = CUMULATIVE_DIR / persona.id / "summary.md"
        summary_path.write_text(summary_text, encoding="utf-8")
        log.info("  [done] Wrote summary: %s (%d chars)",
                 summary_path.relative_to(PROJECT_ROOT),
                 len(summary_text))

        if hasattr(response, "usage"):
            log.info("  [tokens] input: %d, output: %d",
                     response.usage.input_tokens,
                     response.usage.output_tokens)

    except Exception as e:
        log.error("  [fail] Summary generation failed: %s", e)


# ============================================================================
# Main
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Cumulative Fold Engine (SPEC-021)"
    )
    parser.add_argument(
        "meeting_id",
        help=(
            "Meeting identifier — the bundle directory name "
            "(e.g., '2026-03-02-school-board')"
        ),
    )
    parser.add_argument(
        "--force", action="store_true",
        help="Regenerate records even if they already exist",
    )
    parser.add_argument(
        "--persona",
        help="Process only this persona (e.g., PERSONA-001)",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help=(
            "Do everything except LLM calls: load data, check idempotency, "
            "build prompts, report what would happen"
        ),
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true",
        help="Enable debug logging",
    )
    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Validate --persona format
    if args.persona and not PERSONA_ID_RE.match(args.persona):
        log.error(
            "Invalid persona ID: '%s' — expected format PERSONA-NNN "
            "(e.g., PERSONA-001)",
            args.persona,
        )
        sys.exit(2)

    log.info("=== Cumulative Fold Engine (SPEC-021) ===")
    log.info("Meeting: %s", args.meeting_id)
    if args.dry_run:
        log.info("Mode: DRY RUN (no LLM calls will be made)")

    # Validate that the meeting interpretation directory exists
    meeting_interp_dir = MEETINGS_DIR / args.meeting_id
    if not meeting_interp_dir.exists():
        log.error(
            "No interpretation outputs found for meeting '%s'. "
            "Expected directory: %s\n"
            "Run interpret_meeting.py first to generate interpretations.",
            args.meeting_id, meeting_interp_dir,
        )
        sys.exit(2)

    # Step 1: Load personas
    log.info("--- Loading personas ---")
    personas = load_personas()
    if not personas:
        log.error("No personas found. Check %s", PERSONA_DIR)
        sys.exit(2)

    # Step 2: Run fold
    if args.persona:
        log.info("Filter: %s only", args.persona)
    if args.force:
        log.info("Force: regenerating existing records")

    stats = run_fold(
        args.meeting_id,
        personas,
        force=args.force,
        single_persona=args.persona,
        dry_run=args.dry_run,
    )

    # Summary
    log.info("")
    log.info("=== Summary ===")
    log.info("Processed:          %d", stats["processed"])
    log.info("Skipped (exists):   %d", stats["skipped"])
    log.info("Skipped (no interp):%d", stats["no_interpretation"])
    log.info("Failed:             %d", stats["failed"])

    total = (stats["processed"] + stats["skipped"] +
             stats["failed"] + stats["no_interpretation"])
    log.info("Total:              %d persona(s)", total)

    if args.dry_run:
        log.info("")
        log.info("--- Dry-run token estimates ---")
        total_fold_tokens = 0
        total_summary_tokens = 0
        target_personas = personas
        if args.persona:
            target_personas = [p for p in personas if p.id == args.persona]

        manifest = load_bundle_manifest(args.meeting_id)

        for persona in target_personas:
            interpretation = load_interpretation(args.meeting_id, persona.id)
            if interpretation is None:
                continue
            prior_records = load_prior_records(persona.id)
            fold_prompt = build_fold_prompt(
                persona, interpretation, prior_records,
                args.meeting_id, manifest
            )
            fold_tokens = estimate_tokens(FOLD_SYSTEM_PROMPT + fold_prompt)
            total_fold_tokens += fold_tokens

            # Estimate summary tokens
            all_records = prior_records  # In dry-run, use existing records
            if all_records:
                summary_prompt = build_summary_prompt(persona, all_records)
                summary_tokens = estimate_tokens(
                    SUMMARY_SYSTEM_PROMPT + summary_prompt
                )
                total_summary_tokens += summary_tokens

        total_tokens = total_fold_tokens + total_summary_tokens
        log.info("Estimated fold input tokens:    ~%d", total_fold_tokens)
        log.info("Estimated summary input tokens: ~%d", total_summary_tokens)
        log.info("Estimated total input tokens:   ~%d", total_tokens)
        log.info("Estimated cost at $3/MTok input: ~$%.2f",
                 total_tokens * 3.0 / 1_000_000)

    if stats["failed"] > 0:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()

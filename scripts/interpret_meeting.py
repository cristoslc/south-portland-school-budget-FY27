#!/usr/bin/env python3
"""Per-Meeting Interpretation Runner — SPEC-019.

Orchestrates LLM-driven interpretation of a meeting bundle through
all 14 validated persona lenses, producing schema-conformant output
documents per SPEC-018.

Usage:
    python3 scripts/interpret_meeting.py <bundle-path>
    python3 scripts/interpret_meeting.py <bundle-path> --dry-run
    python3 scripts/interpret_meeting.py <bundle-path> --force
    python3 scripts/interpret_meeting.py <bundle-path> --persona PERSONA-001
    python3 scripts/interpret_meeting.py <bundle-path> --force --persona PERSONA-003

Exit codes:
    0 — all interpretations succeeded (or dry-run completed)
    1 — one or more interpretations failed
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
log = logging.getLogger("interpret_meeting")

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent

PERSONA_DIR = PROJECT_ROOT / "docs" / "persona" / "Validated"
MEETINGS_OUTPUT_DIR = PROJECT_ROOT / "data" / "interpretation" / "meetings"

MODEL_ID = "claude-sonnet-4-20250514"

# Persona ID pattern
PERSONA_ID_RE = re.compile(r"^PERSONA-\d{3}$")
PERSONA_DIR_RE = re.compile(r"^\(PERSONA-(\d{3})\)-(.+)$")

# --- Reaction audience mapping (from SPIKE-005) ---

REACTION_AUDIENCES = {
    "PERSONA-001": (
        "your partner, after the kids are in bed, recapping the school "
        "board meeting you just sat through"
    ),
    "PERSONA-002": (
        "another parent at pickup, quickly catching them up"
    ),
    "PERSONA-003": (
        "your sister on the phone, venting about what you just watched online"
    ),
    "PERSONA-004": (
        "a colleague in the teachers' lounge the next morning"
    ),
    "PERSONA-005": (
        "a fellow community organizer over coffee"
    ),
    "PERSONA-006": (
        "your neighbor, over the fence the next morning"
    ),
    "PERSONA-007": (
        "a fellow board-adjacent insider, reviewing what just happened"
    ),
    "PERSONA-008": (
        "your spouse, who asked 'how was the meeting?'"
    ),
    "PERSONA-009": (
        "your news director, pitching the story angles from tonight"
    ),
    "PERSONA-010": (
        "your editor, outlining what you want to cover"
    ),
    "PERSONA-011": (
        "the group chat -- you're the one everyone relies on for the recap"
    ),
    "PERSONA-012": (
        "your friend at lunch the next day -- they don't follow school "
        "board stuff but you're trying to explain why it matters"
    ),
    "PERSONA-013": (
        "your parent, who asked what you thought about the budget news"
    ),
    "PERSONA-014": (
        "your best friend, using the words a 9-year-old would actually use"
    ),
}

# --- Fiscal Context Summary (from SPIKE-005) ---
# Used as default when the bundle doesn't provide one

FISCAL_CONTEXT_DEFAULT = """\
Key budget figures for FY27:
- The district faces a $7.2M structural gap between current costs and revenue
- A roll-forward (no-change) budget would require an 18-19% property tax increase
- The board set a 6% tax increase ceiling, requiring ~$7.2M in cuts
- The fund balance (savings) is essentially depleted -- no cushion remains
- 78 positions (12% of staff) are proposed for elimination: 42 teachers, \
16 ed techs, 14 facilities/food/transport, 2 administrators, 4 non-bargaining
- Elementary enrollment declined 23% in four years (1,401 to 1,080 students)
- Staffing grew by 82 positions while enrollment dropped by 300 students
- Health insurance is projected to increase 12%
- State funding covers only ~20% of actual costs (should be 55%)
- Per-pupil cost: $26,651 (highest among comparable districts)
- The school tax is 61% of total property taxes"""


# ============================================================================
# Task 1: Persona Loader
# ============================================================================

class Persona:
    """A validated persona definition loaded from docs/persona/Validated/."""

    def __init__(self, persona_id, name, content, archetype=None):
        self.id = persona_id
        self.name = name
        self.content = content
        self.archetype = archetype

    @property
    def reaction_audience(self):
        return REACTION_AUDIENCES.get(self.id, "someone in their life")

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

        # Extract persona name from H1 heading: "# Maria (Concerned Elementary Parent)"
        name = _extract_persona_name(content, persona_id)

        # Extract archetype from "## Archetype Label" section
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
    """Extract the first name from the H1 heading of a persona document.

    Expects format: '# Maria (Concerned Elementary Parent)'
    Returns just the first name (e.g., 'Maria').
    """
    h1_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
    if not h1_match:
        log.warning("%s: no H1 heading found, using ID as name", persona_id)
        return persona_id

    heading = h1_match.group(1).strip()
    # Take everything before the first parenthesis as the name
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
    # Find the next ## heading or end of file
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
    # Strip frontmatter
    body = content
    if body.lstrip("\ufeff").startswith("---"):
        end = body.find("\n---", 3)
        if end != -1:
            body = body[end + 4:].strip()

    # Strip the lifecycle table (everything from "## Lifecycle" onward)
    lifecycle_match = re.search(r"^##\s+Lifecycle\s*$", body, re.MULTILINE)
    if lifecycle_match:
        body = body[:lifecycle_match.start()].strip()

    return body


# ============================================================================
# Task 2: Bundle Loader
# ============================================================================

def load_bundle(bundle_path):
    """Load a meeting bundle manifest and all affiliated source files.

    Args:
        bundle_path: Path to the bundle directory (containing manifest.yaml)
                     or directly to the manifest.yaml file.

    Returns:
        dict with keys:
            manifest: parsed YAML manifest data
            meeting_id: string identifier (e.g., '2026-03-02-school-board')
            meeting_context: combined source content as a string
            title: meeting title
            date: meeting date string
            duration: duration string if available
    """
    try:
        import yaml
    except ImportError:
        log.error("PyYAML is required: pip install pyyaml")
        sys.exit(2)

    bundle_path = Path(bundle_path).resolve()

    if bundle_path.is_dir():
        manifest_path = bundle_path / "manifest.yaml"
    else:
        manifest_path = bundle_path
        bundle_path = manifest_path.parent

    if not manifest_path.exists():
        log.error("Bundle manifest not found: %s", manifest_path)
        sys.exit(2)

    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = yaml.safe_load(f)

    if not manifest or not isinstance(manifest, dict):
        log.error("Invalid bundle manifest: %s", manifest_path)
        sys.exit(2)

    # Derive meeting_id from directory name
    meeting_id = bundle_path.name

    # Load all source content
    sources = manifest.get("sources", [])
    meeting_title = manifest.get("title", meeting_id)
    meeting_date = str(manifest.get("meeting_date", ""))

    # Find duration from transcript source if available
    duration = None
    for src in sources:
        if src.get("duration"):
            duration = src["duration"]
            break

    # Build combined meeting context from normalized source files
    context_parts = []
    source_summaries = []

    for src in sources:
        source_id = src.get("source_id", "unknown")
        source_type = src.get("source_type", "document")
        title = src.get("title", source_id)

        # Prefer normalized_path (markdown digests), fall back to raw path
        content = None

        normalized = src.get("normalized_path")
        if normalized:
            np = PROJECT_ROOT / normalized
            if np.exists():
                content = np.read_text(encoding="utf-8")

        if content is None:
            raw = src.get("path", "")
            if raw:
                rp = PROJECT_ROOT / raw
                if rp.exists() and rp.suffix in (".md", ".txt", ".vtt"):
                    content = rp.read_text(encoding="utf-8")

        if content is not None:
            # Strip YAML frontmatter from normalized sources
            clean = _strip_frontmatter(content)
            context_parts.append(
                f"--- Source: {title} [{source_type}] ---\n\n{clean}"
            )
            source_summaries.append(f"  - {source_id}: {title} ({source_type})")
            log.info("  Loaded source: %s (%s)", title, source_type)
        else:
            log.warning("  Source not readable: %s (path: %s)",
                        title, src.get("path", "N/A"))
            source_summaries.append(
                f"  - {source_id}: {title} ({source_type}) [NOT LOADED]"
            )

    meeting_context = "\n\n".join(context_parts)

    log.info("Bundle loaded: %s — %d source(s), %d chars of context",
             meeting_id, len(context_parts), len(meeting_context))

    return {
        "manifest": manifest,
        "meeting_id": meeting_id,
        "meeting_context": meeting_context,
        "title": meeting_title,
        "date": meeting_date,
        "duration": duration or "Unknown",
        "source_count": len(context_parts),
        "source_summaries": source_summaries,
    }


def _strip_frontmatter(text):
    """Strip YAML frontmatter from a markdown document."""
    text = text.lstrip("\ufeff")
    if not text.startswith("---"):
        return text.strip()
    end = text.find("\n---", 3)
    if end == -1:
        return text.strip()
    return text[end + 4:].strip()


# ============================================================================
# Task 3: Prompt Template (per SPIKE-005)
# ============================================================================

SYSTEM_PROMPT = """\
You are an interpretation engine for a municipal school budget analysis \
project. Your job is to process a school board meeting through the eyes of a \
specific community persona -- producing an interpretation that reflects how \
THIS person would experience, understand, and react to what happened in the \
meeting.

Your output must be grounded in the meeting evidence provided. Do not invent \
facts, quotes, or events. Every claim must be traceable to a specific moment \
in the meeting or a specific document.

Critical instruction: Your interpretation must be DISTINCT to this persona. \
Different personas processing the same meeting should highlight different \
facts, have different emotional reactions, ask different questions, and tell \
different stories about what happened. If your output could belong to any \
persona, you have failed."""


def build_prompt(persona, bundle_data):
    """Construct the full prompt for a single persona interpretation.

    Follows the SPIKE-005 prompt template structure:
    1. Persona definition (primes the lens)
    2. Instruction block (selective attention + output format)
    3. Meeting context (evidence)

    Returns:
        str: The assembled user prompt (system prompt is separate).
    """
    persona_body = _extract_persona_body(persona.content)
    persona_name = persona.name

    meeting_title = bundle_data["title"]
    meeting_date = bundle_data["date"]
    meeting_duration = bundle_data["duration"]
    meeting_context = bundle_data["meeting_context"]

    reaction_audience = persona.reaction_audience

    prompt = f"""\
<persona>
{persona_body}
</persona>

<instruction>
Read the meeting evidence below through the eyes of {persona_name}.

Before generating output, mentally answer these questions (do not include \
these answers in your output):
- What moments in this meeting would {persona_name} pay the most attention \
to? What would they lean forward for?
- What parts would they tune out, skim, or find irrelevant?
- What emotional arc would they experience over the course of this meeting?
- If they were telling someone about this meeting afterward, what would they \
lead with?
- What would keep them up at night after this meeting?

Now produce a three-layer interpretation. Your output MUST follow this exact \
markdown format:

---
schema_version: "1.0"
meeting_id: "{bundle_data["meeting_id"]}"
persona_id: "{persona.id}"
persona_name: "{persona_name}"
meeting_date: {meeting_date}
meeting_title: "{meeting_title.replace(" — ", " -- ").split(" — ")[0] if " — " in meeting_title else meeting_title}"
interpretation_date: {datetime.date.today().isoformat()}
interpreter_model: "{MODEL_ID}"
---

# Interpretation: {persona_name} ({persona.id})
## Meeting: {meeting_title.replace(" — ", " -- ").split(" — ")[0] if " — " in meeting_title else meeting_title} -- {meeting_date}

### Structured Points

Produce 5-8 structured points. Each point represents a specific fact, \
decision, or moment from the meeting that {persona_name} would find \
significant. Not every point needs to be negative -- include things that \
would reassure or encourage this persona too.

For each point, use this EXACT format (including the #### header with number \
and short title):

#### 1. [Short descriptive title]
- **Fact:** [A concise statement of what happened or was said, 1-2 sentences]
- **Source:** [Timestamp from transcript e.g. "[01:23--01:45]" or document \
reference e.g. "Source 012, Options Matrix". Must be traceable to evidence.]
- **Emotional valence:** [One of: positive, negative, neutral]
- **Threat level:** [Integer from 1-5, where 1 = minimal and 5 = severe]
- **Open question:** [true or false — does this point raise an unresolved \
question for {persona_name}?]

### Journey Map

Produce 4-6 ordered beats that trace {persona_name}'s emotional experience \
through the meeting chronologically. Use this EXACT four-column table format:

| Position | Meeting Event | Persona Cognitive State | Persona Emotional State |
|----------|---------------|------------------------|------------------------|
| 1 | [What happened in the meeting that triggered this beat] | [What \
{persona_name} is thinking — their cognitive processing of the event] | \
[{persona_name}'s emotional reaction] |

The journey map should tell a story with an arc -- not just list topics in \
order.

### Reactions

Write 2-3 paragraphs in {persona_name}'s authentic voice. This is how they \
would describe this meeting to {reaction_audience}.

Write as {persona_name} would actually speak or text. Use their vocabulary, \
their level of formality, their emotional register. Do not write in analyst \
or journalist voice. Do not hedge with qualifiers a real person wouldn't use. \
Be specific about what happened in the meeting -- do not be vague.
</instruction>

<meeting_context>
## Meeting: {meeting_title}
**Date:** {meeting_date}
**Duration:** {meeting_duration}

### Fiscal Context
{FISCAL_CONTEXT_DEFAULT}

### Meeting Content
{meeting_context}
</meeting_context>"""

    return prompt


def estimate_tokens(text):
    """Rough token estimate: ~4 chars per token for English text."""
    return len(text) // 4


# ============================================================================
# Task 4 & 5: Runner Loop with Resume Logic
# ============================================================================

def run_interpretation(bundle_data, personas, *, force=False,
                       single_persona=None, dry_run=False):
    """Run interpretation for all (or one) persona against a meeting bundle.

    Args:
        bundle_data: dict from load_bundle()
        personas: list of Persona objects
        force: if True, regenerate even if output exists
        single_persona: if set, only process this PERSONA-NNN
        dry_run: if True, do everything except the LLM call

    Returns:
        dict with counts: processed, skipped, failed
    """
    meeting_id = bundle_data["meeting_id"]
    output_dir = MEETINGS_OUTPUT_DIR / meeting_id
    output_dir.mkdir(parents=True, exist_ok=True)

    # Filter to single persona if requested
    if single_persona:
        personas = [p for p in personas if p.id == single_persona]
        if not personas:
            log.error("Persona %s not found in loaded personas", single_persona)
            return {"processed": 0, "skipped": 0, "failed": 1}

    stats = {"processed": 0, "skipped": 0, "failed": 0}

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

    for persona in personas:
        output_path = output_dir / f"{persona.id}.md"

        # Resume logic: skip if output already exists (unless --force)
        if output_path.exists() and not force:
            log.info("  [skip] %s — output already exists: %s",
                     persona.id, output_path.name)
            stats["skipped"] += 1
            continue

        if output_path.exists() and force:
            log.info("  [force] %s — regenerating (existing output will be "
                     "overwritten)", persona.id)

        # Build the prompt
        prompt = build_prompt(persona, bundle_data)
        prompt_tokens = estimate_tokens(SYSTEM_PROMPT + prompt)
        log.info("  [prompt] %s (%s) — ~%d tokens",
                 persona.id, persona.name, prompt_tokens)

        if dry_run:
            log.info("  [dry-run] %s — would call LLM (%s), write to %s",
                     persona.id, MODEL_ID, output_path.name)
            stats["processed"] += 1
            continue

        # Actual LLM call
        try:
            log.info("  [call] %s — calling %s ...", persona.id, MODEL_ID)
            response = anthropic_client.messages.create(  # type: ignore[union-attr]
                model=MODEL_ID,
                max_tokens=4096,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": prompt}],
            )

            # Extract text content
            output_text = ""
            for block in response.content:
                if hasattr(block, "text"):
                    output_text += block.text  # type: ignore[union-attr]

            if not output_text.strip():
                log.error("  [fail] %s — empty response from LLM", persona.id)
                stats["failed"] += 1
                continue

            # Validate the output before writing
            validation_errors = _quick_validate(output_text)
            if validation_errors:
                log.warning("  [warn] %s — %d validation issue(s):",
                            persona.id, len(validation_errors))
                for err in validation_errors:
                    log.warning("    %s", err)
                # Still write the output — let the user decide

            # Write output
            output_path.write_text(output_text, encoding="utf-8")
            log.info("  [done] %s — wrote %s (%d chars)",
                     persona.id, output_path.name, len(output_text))
            stats["processed"] += 1

            # Log token usage
            if hasattr(response, "usage"):
                log.info("  [tokens] %s — input: %d, output: %d",
                         persona.id,
                         response.usage.input_tokens,
                         response.usage.output_tokens)

        except Exception as e:
            log.error("  [fail] %s — LLM call failed: %s", persona.id, e)
            stats["failed"] += 1
            continue

    return stats


def _quick_validate(text):
    """Quick structural validation of LLM output.

    Checks for the three required sections without full schema validation.
    Returns list of error strings (empty = looks good).
    """
    errors = []

    # Check frontmatter
    stripped = text.lstrip("\ufeff").strip()
    if not stripped.startswith("---"):
        errors.append("missing YAML frontmatter (no opening ---)")

    # Check for required sections
    if "### Structured Points" not in text:
        errors.append("missing '### Structured Points' section")
    if "### Journey Map" not in text:
        errors.append("missing '### Journey Map' section")
    if "### Reactions" not in text:
        errors.append("missing '### Reactions' section")

    # Check for structured point headers
    point_count = len(re.findall(r"^####\s+\d+\.\s+", text, re.MULTILINE))
    if point_count < 5:
        errors.append(f"found {point_count} structured points, expected 5-8")
    elif point_count > 8:
        errors.append(f"found {point_count} structured points, expected 5-8")

    # Check journey map uses SPEC-018 four-column header
    if "### Journey Map" in text:
        has_spec018_header = bool(re.search(
            r"\|\s*Position\s*\|\s*Meeting\s+Event\s*\|\s*Persona\s+Cognitive\s+State\s*\|\s*Persona\s+Emotional\s+State\s*\|",
            text, re.IGNORECASE
        ))
        if not has_spec018_header:
            errors.append(
                "journey map does not use SPEC-018 columns "
                "(Position, Meeting Event, Persona Cognitive State, Persona Emotional State)"
            )

    return errors


# ============================================================================
# Main
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Per-Meeting Interpretation Runner (SPEC-019)"
    )
    parser.add_argument(
        "bundle",
        help=(
            "Path to a meeting bundle directory (containing manifest.yaml) "
            "or directly to a manifest.yaml file"
        ),
    )
    parser.add_argument(
        "--force", action="store_true",
        help="Regenerate interpretations even if output files already exist",
    )
    parser.add_argument(
        "--persona",
        help="Process only this persona (e.g., PERSONA-001)",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help=(
            "Do everything except the LLM call: load personas, load bundle, "
            "build prompts, estimate tokens, report what would happen"
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

    log.info("=== Per-Meeting Interpretation Runner (SPEC-019) ===")
    if args.dry_run:
        log.info("Mode: DRY RUN (no LLM calls will be made)")

    # Step 1: Load personas
    log.info("--- Loading personas ---")
    personas = load_personas()
    if not personas:
        log.error("No personas found. Check %s", PERSONA_DIR)
        sys.exit(2)

    # Step 2: Load bundle
    log.info("--- Loading bundle ---")
    bundle_data = load_bundle(args.bundle)

    # Step 3-5: Run interpretation loop
    log.info("--- Running interpretations ---")
    log.info("Meeting: %s", bundle_data["title"])
    log.info("Meeting ID: %s", bundle_data["meeting_id"])
    log.info("Personas: %d", len(personas))
    if args.persona:
        log.info("Filter: %s only", args.persona)
    if args.force:
        log.info("Force: regenerating existing outputs")

    stats = run_interpretation(
        bundle_data,
        personas,
        force=args.force,
        single_persona=args.persona,
        dry_run=args.dry_run,
    )

    # Summary
    log.info("")
    log.info("=== Summary ===")
    log.info("Processed:  %d", stats["processed"])
    log.info("Skipped:    %d", stats["skipped"])
    log.info("Failed:     %d", stats["failed"])

    total = stats["processed"] + stats["skipped"] + stats["failed"]
    log.info("Total:      %d persona(s)", total)

    if args.dry_run:
        # In dry-run, estimate total token usage
        total_prompt_tokens = 0
        target_personas = personas
        if args.persona:
            target_personas = [p for p in personas if p.id == args.persona]
        for persona in target_personas:
            prompt = build_prompt(persona, bundle_data)
            total_prompt_tokens += estimate_tokens(SYSTEM_PROMPT + prompt)
        log.info("")
        log.info("Estimated total input tokens: ~%d", total_prompt_tokens)
        log.info("Estimated cost at $3/MTok input: ~$%.2f",
                 total_prompt_tokens * 3.0 / 1_000_000)

    if stats["failed"] > 0:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()

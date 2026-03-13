# Interpretation Pipeline Schemas

**Pipeline:** VISION-003 (Interpretation Pipeline)

## Overview

This directory contains JSON Schema definitions (in YAML encoding) for the
interpretation pipeline's data contracts. Schemas define the structure of
meeting bundles, per-meeting interpretations, and cumulative interpretation
records.

## Directory Layout

```
data/interpretation/
  schema/
    bundle-manifest-schema.yaml         # JSON Schema for bundle manifests
    inter-meeting-manifest-schema.yaml  # JSON Schema for inter-meeting evidence
    interpretation-output-schema.yaml   # JSON Schema for per-meeting interpretations
    cumulative-record-schema.yaml       # JSON Schema for cumulative records
    cumulative-summary-schema.yaml      # JSON Schema for cumulative summary views
    cumulative-initial-state.md.template # Template for initial cumulative state
    README.md                           # This file
  bundles/
    2026-03-02-school-board/
      manifest.yaml                    # Bundle manifest for this meeting
    2026-03-05-city-council/
      manifest.yaml
    ...
  inter-meeting/
    manifest.yaml                      # Inter-meeting evidence manifest
```

### Bundle directory naming

Each bundle directory is named `<YYYY-MM-DD>-<body>`:

- **YYYY-MM-DD** — the meeting date in ISO 8601 format
- **body** — the governing body slug: `school-board` or `city-council`

Examples:
- `2026-03-02-school-board/` — School Board Budget Workshop I, March 2, 2026
- `2026-03-05-city-council/` — City Council Regular Meeting, March 5, 2026

### Manifest filename

Every bundle directory contains exactly one file: `manifest.yaml`.

## Source References

Source paths in `manifest.yaml` are **relative to the project root**, not
relative to the bundle directory. This matches the convention used by
evidence pool manifests in `docs/evidence-pools/`.

### Path fields

Each source entry has two path fields:

- **`path`** (required) — path to the raw source file in `data/`
  (e.g., `data/school-board/meetings/2026-03-02-budget-workshop-1/transcript.en-x-autogen.vtt`)
- **`normalized_path`** (optional) — path to the normalized markdown in
  `docs/evidence-pools/` (e.g., `docs/evidence-pools/school-board-budget-meetings/sources/004-budget-workshop-1-2026-03-02.md`)

Sources reference existing files; bundles do not copy or symlink data.

## Bundle Manifest Fields

### Required

| Field            | Type   | Description |
|------------------|--------|-------------|
| `schema_version` | string | Always `"1.0"` |
| `meeting_date`   | string | ISO 8601 date (`YYYY-MM-DD`) |
| `meeting_type`   | enum   | `workshop`, `regular`, `special`, `budget-forum`, `budget-workshop`, `joint` |
| `body`           | enum   | `school-board`, `city-council` |
| `sources`        | array  | List of source entries (at least 1) |

### Optional

| Field        | Type   | Description |
|--------------|--------|-------------|
| `title`      | string | Human-readable meeting title |
| `agenda_ref` | string | Path to agenda file (relative to project root) |
| `video_url`  | string | URL of the meeting video recording |
| `notes`      | string | Free-text notes about this bundle |

### Source entry fields

| Field             | Required | Type   | Description |
|-------------------|----------|--------|-------------|
| `source_id`       | yes      | string | Unique ID within the bundle |
| `source_type`     | yes      | enum   | `transcript`, `agenda`, `packet`, `presentation`, `spreadsheet`, `document`, `other` |
| `title`           | yes      | string | Human-readable title |
| `path`            | yes      | string | Path to raw source file |
| `normalized_path` | no       | string | Path to normalized markdown |
| `evidence_pool`   | no       | string | Evidence pool name |
| `description`     | no       | string | Context about the source |
| `hash`            | no       | string | `sha256:<hex>` content hash |
| `duration`        | no       | string | `HH:MM:SS` for media sources |

## Inter-Meeting Evidence

Sources not affiliated with any single meeting (e.g., news articles,
public statements between meetings) go in `data/interpretation/inter-meeting/manifest.yaml`.

Each entry includes a `date_range` with `posted_after` and `posted_before`
dates indicating which meetings the evidence falls between. This enables
the brief generator to include relevant inter-meeting context when
preparing for an upcoming meeting.

See `inter-meeting-manifest-schema.yaml` for the full schema.

---

## Interpretation Output Schema

**Spec:** SPEC-018 | **Pipeline:** VISION-003 (Interpretation Pipeline) | **Depends on:** SPIKE-005

### Overview

An **interpretation output** is a per-persona, per-meeting document produced by the
interpretation engine. Each document captures how a specific community persona
experiences and reacts to a single meeting, organized in three layers: structured
points (machine-parseable), a journey map (chronological emotional arc), and
free-form reactions (persona-voice narrative).

### Directory Layout

```
data/interpretation/
  meetings/
    2026-03-02-school-board/
      PERSONA-001.md          # Maria's interpretation
      PERSONA-006.md          # Tom's interpretation
      PERSONA-012.md          # Jaylen's interpretation
      ...
    2026-03-09-school-board/
      PERSONA-001.md
      ...
```

### File path convention

Each interpretation document is stored at:

```
data/interpretation/meetings/<meeting-id>/<persona-id>.md
```

- **meeting-id** matches the bundle directory name (e.g., `2026-03-02-school-board`)
- **persona-id** matches the persona identifier (e.g., `PERSONA-001`)

### Document format

Each interpretation document is a markdown file with YAML frontmatter:

```markdown
---
schema_version: "1.0"
meeting_id: "2026-03-02-school-board"
persona_id: "PERSONA-001"
persona_name: "Maria"
meeting_date: 2026-03-02
meeting_title: "School Board Budget Workshop I"
interpretation_date: 2026-03-13
interpreter_model: "claude-sonnet-4-20250514"
---

# Interpretation: Maria (PERSONA-001)
## Meeting: School Board Budget Workshop I -- March 2, 2026

### Structured Points

#### 1. Support cuts feel immediate
- **Fact:** Families heard that several staffing scenarios would change support levels next year.
- **Source reference:** [00:12--00:18]
- **Emotional valence:** negative
- **Threat level:** 5
- **Open question:** true

[... 5-8 points total ...]

### Journey Map

| Position | Meeting Event | Persona Cognitive State | Persona Emotional State |
|----------|---------------|------------------------|------------------------|
| 1 | Budget gap presented | Understands the scale of the shortfall | Alarmed and guarded |
| 2 | Staffing reductions discussed | Sees support staff as directly at risk | Worried and frustrated |
| 3 | Board questions transportation impacts | Connecting cuts to daily family logistics | Tense but attentive |
| 4 | Public comment pushes for clarity | Believes more explanation is still owed | Determined and uneasy |

[... 4-6 beats total ...]

### Reactions

[2-3 paragraphs in persona voice, as if recounting the meeting to
a specific person in the persona's life]
```

### Frontmatter fields

#### Required

| Field             | Type   | Description |
|-------------------|--------|-------------|
| `schema_version`  | string | Always `"1.0"` |
| `meeting_id`      | string | Meeting identifier matching bundle directory name (e.g., `2026-03-02-school-board`) |
| `persona_id`      | string | Persona identifier (e.g., `PERSONA-001`) |

#### Optional

| Field                | Type   | Description |
|----------------------|--------|-------------|
| `persona_name`       | string | Display name of the persona (e.g., "Maria") |
| `meeting_date`       | string | ISO 8601 date of the meeting (`YYYY-MM-DD`) |
| `meeting_title`      | string | Human-readable meeting title |
| `interpretation_date`| string | ISO 8601 date when interpretation was generated |
| `interpreter_model`  | string | LLM model identifier used for generation |

### Body sections

#### Layer 1: Structured Points (5-8)

Each point represents a fact, decision, or moment the persona finds significant:

| Field               | Required | Type    | Description |
|---------------------|----------|---------|-------------|
| `fact`              | yes      | string  | What happened or was said (1-2 sentences) |
| `source_reference`  | yes      | string  | Timestamp or document reference |
| `emotional_valence` | yes      | enum    | One of: `positive`, `negative`, `neutral` |
| `threat_level`      | yes      | integer | 1 (none/minimal) through 5 (severe) |
| `open_question`     | no       | boolean | Whether this point raises an open question (`true` / `false`) |

> **Compatibility note:** Obsolete fields from the SPIKE-005 draft — named
> threat levels (`high`, `moderate`, `low`, `none`), question-text strings
> for `open_question`, and the eight-value emotional valence enum (`alarmed`,
> `anxious`, `frustrated`, `skeptical`, `cautiously_optimistic`, `reassured`,
> `empowered`) — are no longer part of the normative SPEC-018 contract.

#### Layer 2: Journey Map (4-6 beats)

Chronological emotional arc through the meeting:

| Field                    | Required | Type    | Description |
|--------------------------|----------|---------|-------------|
| `position`               | yes      | integer | Chronological position (1-based) |
| `meeting_event`          | yes      | string  | What happened in the meeting at this point |
| `persona_cognitive_state`| yes      | string  | What the persona is thinking or understanding |
| `persona_emotional_state`| yes      | string  | How the persona feels (free-form) |

> **Compatibility note:** Obsolete fields from the SPIKE-005 draft
> (`timestamp_range`, `beat_label`, `emotional_state`, `trigger`,
> `internal_monologue`) are no longer part of the normative SPEC-018 contract.

#### Layer 3: Reactions

Free-form markdown in the persona's authentic voice. Written as if recounting the
meeting to a specific person in their life. Not schema-constrained.

### Schema definition

See `interpretation-output-schema.yaml` for the formal JSON Schema definition.

---

## Validation

### Bundle manifests

Run the validation script to check a bundle manifest:

```bash
python3 scripts/validate_bundle.py data/interpretation/bundles/2026-03-02-school-board/manifest.yaml
```

Or validate the inter-meeting manifest:

```bash
python3 scripts/validate_bundle.py --inter-meeting data/interpretation/inter-meeting/manifest.yaml
```

The script checks:
- All required fields are present
- Enum values are valid
- Date formats are ISO 8601
- Referenced source paths resolve to existing files
- Inter-meeting date ranges are consistent (posted_after < posted_before)

### Interpretation outputs

Run the validation script to check an interpretation document:

```bash
python3 scripts/validate_interpretation.py data/interpretation/meetings/2026-03-02-school-board/PERSONA-001.md
```

Or validate all interpretation documents:

```bash
python3 scripts/validate_interpretation.py --all
```

The script checks:
- YAML frontmatter has required fields (schema_version, meeting_id, persona_id)
- All three body sections exist (Structured Points, Journey Map, Reactions)
- Structured points have required fields (fact, source reference, emotional valence, threat level)
- Emotional valence values are one of: `positive`, `negative`, `neutral`
- Threat level parses as an integer in the range 1–5
- `open_question` parses as a boolean (`true` / `false`) when present
- Journey map table has the four SPEC-018 columns: Position, Meeting Event, Persona Cognitive State, Persona Emotional State
- Reactions section is non-empty (at least 100 characters)

---

## Cumulative Interpretation Format

**Spec:** SPEC-020 | **Pipeline:** VISION-003 (Interpretation Pipeline) | **Depends on:** SPIKE-006, SPEC-018

### Overview

The cumulative interpretation system uses a **log-structured approach**
(recommended by SPIKE-006) to track how each persona's understanding evolves
across meetings. Rather than merging interpretations into a single growing
document, each meeting produces an immutable record, and a summary view is
generated on demand.

### Architecture

- **Storage**: Immutable interpretation records (one per persona per meeting)
- **Presentation**: Generated summary views (one per persona, regenerable)
- **Source of truth**: The record store, not the summary view

### Directory Layout

```
data/interpretation/
  cumulative/
    PERSONA-001/
      2026-01-12.md     # Immutable record for meeting 1
      2026-02-04.md     # Immutable record for meeting 2
      2026-02-09.md     # Immutable record for meeting 3
      summary.md        # Generated summary view
    PERSONA-006/
      ...
```

### Cumulative Record (per-meeting, immutable)

Each record captures how a persona's understanding shifted after one meeting.
Records are write-once and never modified. File path:
`data/interpretation/cumulative/<PERSONA-ID>/<meeting-date>.md`

#### Frontmatter fields

| Field                | Required | Type        | Description |
|----------------------|----------|-------------|-------------|
| `schema_version`     | yes      | string      | Always `"1.0"` |
| `persona_id`         | yes      | string      | Persona identifier (e.g., `PERSONA-001`) |
| `persona_name`       | no       | string      | Display name (e.g., "Maria") |
| `meeting_date`       | yes      | string      | ISO 8601 date of the meeting |
| `meeting_type`       | yes      | enum        | `regular`, `workshop`, `special`, `budget-forum`, `budget-workshop`, `joint` |
| `body`               | yes      | enum        | `school-board`, `city-council` |
| `prior_meeting`      | yes      | string/null | Date of previous record, or null for first |
| `interpretation_date`| yes      | string      | ISO 8601 date when record was generated |
| `interpreter_model`  | no       | string      | LLM model identifier |

#### Body sections

1. **interpretation** (~200-400 words): Free-text narrative of what this meeting
   means to the persona. Present tense. Grounded in evidence.

2. **deltas** (structured table): What changed relative to the persona's prior
   state. Each delta has:
   - `category`: `new_information`, `position_shift`, `supersession`,
     `thread_opened`, `thread_resolved`
   - `description`: Concrete statement of the change
   - `evidence_ref` (optional): Source reference
   - `supersedes` (optional): Prior belief being replaced

3. **emotional_register** (1-2 sentences): Brief note on the persona's
   emotional state after this meeting.

### Summary View (generated, regenerable)

A summary view synthesizes all records for one persona into a current-state
overview. File path: `data/interpretation/cumulative/<PERSONA-ID>/summary.md`

#### Frontmatter fields

| Field              | Required | Type    | Description |
|--------------------|----------|---------|-------------|
| `schema_version`   | yes      | string  | Always `"1.0"` |
| `persona_id`       | yes      | string  | Persona identifier |
| `persona_name`     | no       | string  | Display name |
| `last_meeting_date`| yes      | string  | Date of most recent record |
| `record_count`     | yes      | integer | Number of records synthesized |
| `generated_date`   | yes      | string  | Date summary was generated |

#### Body sections

1. **Current Understanding** (~150-300 words): Regenerated synthesis of the
   persona's current state. Authoritative present-tense overview.

2. **Timeline of Understanding Shifts**: Ordered list with one entry per meeting
   showing date and shift summary.

3. **Active Supersessions**: Table of beliefs that have been explicitly replaced,
   with from/to/when columns.

4. **Open Threads**: Unresolved questions (thread_opened minus thread_resolved).

5. **Resolved Threads**: Questions that have been answered, with resolution
   date and summary.

### Initial State Template

The file `cumulative-initial-state.md.template` provides a template for the
first cumulative record when no prior meetings exist. It seeds the interpretation
from the persona definition's baseline goals and concerns.

### Schema definitions

- `cumulative-record-schema.yaml` -- JSON Schema for cumulative records
- `cumulative-summary-schema.yaml` -- JSON Schema for summary views

### Validation

Run the validation script to check cumulative records:

```bash
python3 scripts/validate_cumulative.py data/interpretation/cumulative/PERSONA-001/2026-01-12.md
```

Or validate all cumulative records and summary views:

```bash
python3 scripts/validate_cumulative.py --all
```

Validate only summary views:

```bash
python3 scripts/validate_cumulative.py --summary
```

The script checks:
- YAML frontmatter has required fields
- Required body sections exist (interpretation, deltas, emotional_register)
- Delta category values are from the allowed enum
- Interpretation section word count is within range (~200-400 words)
- Prior_meeting chain is consistent (null for first record, valid date otherwise)
- Summary views have all required sections

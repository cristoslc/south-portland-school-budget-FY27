# Meeting Bundle Schema

**Spec:** SPEC-016 | **Pipeline:** VISION-003 (Interpretation Pipeline)

## Overview

A **meeting bundle** groups all evidence sources affiliated with a single
meeting (transcript, agenda, budget packet, presentation slides) into a
directory with a `manifest.yaml` that describes the meeting and lists its
sources. The bundle schema defines the data contract consumed by downstream
pipeline stages: interpretation, fold, and brief generation.

## Directory Layout

```
data/interpretation/
  schema/
    bundle-manifest-schema.yaml       # JSON Schema for bundle manifests
    inter-meeting-manifest-schema.yaml # JSON Schema for inter-meeting evidence
    README.md                          # This file
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
interpretation_date: 2026-03-12
interpreter_model: "claude-sonnet-4-20250514"
---

# Interpretation: Maria (PERSONA-001)
## Meeting: School Board Budget Workshop I -- March 2, 2026

### Structured Points

#### 1. [Short title]
- **Fact:** [statement grounded in meeting evidence]
- **Source:** [timestamp or document reference]
- **Emotional valence:** [alarmed|anxious|frustrated|skeptical|neutral|cautiously_optimistic|reassured|empowered]
- **Threat level:** [high|moderate|low|none]
- **Open question:** [question in persona voice]

[... 5-8 points total ...]

### Journey Map

| Beat | Time | Label | Emotional State | Trigger | Internal Monologue |
|------|------|-------|-----------------|---------|-------------------|
| 1 | [HH:MM--HH:MM] | [3-5 word label] | [state] | [trigger] | [thought in persona voice] |
| ... | | | | | |

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
| `emotional_valence` | yes      | enum    | One of: `alarmed`, `anxious`, `frustrated`, `skeptical`, `neutral`, `cautiously_optimistic`, `reassured`, `empowered` |
| `threat_level`      | yes      | integer | 1 (none), 2 (low), 3 (moderate), 4 (high) |
| `open_question`     | no       | string  | Question in persona voice |

#### Layer 2: Journey Map (4-6 beats)

Chronological emotional arc through the meeting:

| Field               | Required | Type   | Description |
|---------------------|----------|--------|-------------|
| `timestamp_range`   | yes      | string | `[HH:MM--HH:MM]` time range |
| `beat_label`        | yes      | string | Short label (3-5 words) |
| `emotional_state`   | yes      | string | How persona feels (free-form) |
| `trigger`           | yes      | string | What caused this emotional shift |
| `internal_monologue`| yes      | string | One thought sentence in persona voice |

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
- Structured points have required fields (fact, source, emotional valence, threat level)
- Emotional valence values are from the allowed enum
- Threat level values map to valid levels (high, moderate, low, none)
- Journey map beats have required columns
- Reactions section is non-empty

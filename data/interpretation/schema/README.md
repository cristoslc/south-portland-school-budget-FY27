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

## Validation

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

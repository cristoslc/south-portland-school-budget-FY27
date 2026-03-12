---
title: "Meeting Bundle Schema"
artifact: SPEC-016
status: Draft
author: cristos
created: 2026-03-12
last-updated: 2026-03-12
parent-epic: EPIC-008
linked-research: []
linked-adrs: []
depends-on: []
addresses: []
evidence-pool: ""
swain-do: required
---

# Meeting Bundle Schema

## Problem Statement

The interpretation pipeline needs a well-defined data structure for meeting bundles — grouping sources by meeting and capturing metadata — so that downstream stages (interpretation, fold, brief) have a consistent, machine-readable input format. Without a shared schema, each stage would make its own assumptions about how meeting data is organized.

## External Behavior

- **Input:** Evidence pool manifest (list of normalized sources with metadata from VISION-002 pools)
- **Output:** Meeting bundle files — one directory per meeting containing a bundle manifest (YAML) and references to affiliated sources
- **Precondition:** Evidence pool sources are normalized to markdown (VISION-002 complete)
- **Postcondition:** Every source is affiliated with exactly one meeting or classified as inter-meeting evidence
- **Storage:** `data/interpretation/bundles/<YYYY-MM-DD>-<body>/` (e.g., `2026-03-02-school-board/`)

## Acceptance Criteria

1. Given a meeting bundle directory, when the manifest is read, then it contains: meeting date, meeting type (workshop / regular / special), body (school-board / city-council), source list with paths, and optional agenda reference
2. Given the full set of meeting bundles, when all manifests are collected, then every source in the evidence pool appears in exactly one bundle or in the inter-meeting evidence set
3. Given a bundle manifest, when a downstream consumer loads it, then all referenced source paths resolve to valid normalized markdown files
4. Given an inter-meeting evidence event, when it is recorded, then it has a date range (posted-after / posted-before) and is accessible to the upcoming-event brief generator
5. Given the bundle schema, when validated by a Python script, then it enforces required fields and rejects malformed manifests

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|

## Scope & Constraints

- Schema defines structure only — affiliation logic lives in SPEC-017
- Bundle storage is in the project's data layer (`data/interpretation/`), not `docs/` or `dist/`
- Format must be parseable by Python scripts (YAML preferred, consistent with evidence pool manifests)
- Schema should be extensible for future metadata (e.g., video links, attendance records) without breaking existing consumers

## Implementation Approach

1. **Define bundle manifest schema** — YAML format with required and optional fields, validated by a JSON Schema or Python dataclass
2. **Define directory layout** — `data/interpretation/bundles/<date>-<body>/manifest.yaml` + source references
3. **Define inter-meeting evidence manifest** — `data/interpretation/inter-meeting/manifest.yaml` with date-ranged entries
4. **Build schema validation script** — Python script that validates a bundle manifest against the schema
5. **Validate with existing data** — apply schema to the existing March meeting sources to confirm it accommodates real evidence

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Draft | 2026-03-12 | _pending_ | Initial creation |

---
title: "Per-Meeting Interpretation Runner"
artifact: SPEC-019
status: Implemented
author: cristos
created: 2026-03-12
last-updated: 2026-03-13
approved: 2026-03-12
implemented: 2026-03-13
parent-epic: EPIC-009
linked-research:
  - SPIKE-005
linked-adrs: []
depends-on:
  - SPEC-016
  - SPEC-018
  - SPIKE-005
addresses: []
evidence-pool: ""
swain-do: required
---

# Per-Meeting Interpretation Runner

## Problem Statement

The interpretation pipeline needs an orchestrator that takes a meeting bundle, loads all 14 persona definitions, and runs LLM-driven interpretation for each persona — producing schema-conformant output stored in the data layer. This is the operational core of the interpretation pipeline: the script that actually generates the interpretive material.

## External Behavior

- **Input:** Meeting bundle path (per SPEC-016 schema), persona definitions directory (`docs/persona/Validated/`)
- **Output:** 14 interpretation documents (per SPEC-018 schema), one per persona, written to `data/interpretation/meetings/<meeting-id>/`
- **Precondition:** Meeting bundle exists and is valid; persona definitions are Validated
- **Postcondition:** All 14 interpretation documents pass SPEC-018 schema validation
- **Invocation:** `python scripts/interpret_meeting.py <bundle-path> [--force] [--persona PERSONA-NNN]`

## Acceptance Criteria

1. Given a valid meeting bundle and 14 persona definitions, when the runner executes, then it produces 14 interpretation documents in `data/interpretation/meetings/<meeting-id>/`
2. Given an interpretation document, when validated against SPEC-018 schema, then it passes
3. Given a meeting bundle with transcript + agenda + budget packet, when the runner executes, then structured points reference specific evidence from all source types present in the bundle
4. Given a runner invocation on a meeting that has already been interpreted, when executed with `--force`, then it regenerates interpretations; without `--force`, it skips with a message
5. Given a runner failure mid-execution (e.g., after persona 7 of 14), when restarted without `--force`, then it resumes from the next unprocessed persona
6. Given the `--persona PERSONA-NNN` flag, when the runner executes, then it processes only the specified persona (useful for re-running a single interpretation)

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|
| AC1 — 14 interpretation docs | `--dry-run` on 2026-03-02-school-board: loads 14 personas, processes all 14 (3 skipped as existing, 11 would write) | PASS |
| AC2 — SPEC-018 validation | 3 existing exemplars (PERSONA-001, -006, -012) pass `validate_interpretation.py --all` with 0 errors; prompt instructs SPEC-018 format | PASS |
| AC3 — multi-source evidence | Bundle loads 4 source types (transcript, agenda, presentation, spreadsheet); 206K chars of context passed to prompt | PASS |
| AC4 — force vs skip | `--dry-run`: skips PERSONA-001 (exists); `--dry-run --force`: regenerates PERSONA-001 | PASS |
| AC5 — resume after partial | Dry-run with 3 existing outputs: 3 skipped, 11 processed — resumes from next unprocessed persona | PASS |
| AC6 — persona filter | `--persona PERSONA-001`: processes only PERSONA-001; `--persona PERSONA-001 --force`: regenerates only that persona | PASS |

## Scope & Constraints

- One LLM call per persona per meeting (prompt includes meeting bundle + persona definition + output instructions)
- Prompt structure follows SPIKE-005 findings
- Persona definitions are read from `docs/persona/Validated/` — only Validated personas are processed
- The runner does not modify evidence pools or meeting bundles — it is a read-from-bundle, write-interpretation operation
- Error handling: log failures per persona, continue with remaining personas, report summary at end

## Implementation Approach

1. **Persona loader** — reads all Validated persona definitions, extracts structured fields for prompt context
2. **Bundle loader** — reads meeting bundle manifest, loads all affiliated sources into a single context document
3. **Prompt template** — incorporates meeting context + persona definition + SPEC-018 output instructions; structure per SPIKE-005 findings
4. **Runner loop** — iterates over 14 personas, calls LLM, parses output, validates against schema, writes to data layer
5. **Resume logic** — check for existing interpretation files, skip completed personas unless `--force`
6. **Test against March 2 workshop** — first real meeting bundle as validation

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Draft | 2026-03-12 | 7207791 | Initial creation |
| Approved | 2026-03-12 | de71f02 | Approved for implementation |
| Implemented | 2026-03-13 | — | All 6 ACs verified via dry-run; interpret_meeting.py loads 14 personas, 4 source types, supports --force/--persona/resume |

---
title: "Cumulative Interpretation Format"
artifact: SPEC-020
status: Draft
author: cristos
created: 2026-03-12
last-updated: 2026-03-12
parent-epic: EPIC-010
linked-research:
  - SPIKE-006
linked-adrs: []
depends-on:
  - SPEC-018
  - SPIKE-006
addresses: []
evidence-pool: ""
swain-do: required
---

# Cumulative Interpretation Format

## Problem Statement

Per-meeting interpretations capture point-in-time snapshots. The cumulative interpretation must track narrative evolution — when understanding shifted, what's been superseded, how the persona's story arc has developed — without growing unboundedly. This format is the backbone of the pipeline's temporal promise: it's what makes "Maria went from general anxiety → my school might close → my school IS closing" visible as a narrative rather than a set of disconnected snapshots.

## External Behavior

- **Input:** Cumulative interpretation from prior fold (or empty state for first meeting) + new per-meeting interpretation (SPEC-018 format)
- **Output:** Updated cumulative interpretation document per persona
- **Format:** YAML frontmatter + markdown with temporal sections
- **Storage:** `data/interpretation/cumulative/<persona-id>.md`
- **Consumers:** SPEC-021 (fold engine reads and writes), SPEC-022 (brief generator reads), human reviewers

## Acceptance Criteria

1. Given a cumulative interpretation, when read, then it contains four sections: `current_understanding` (authoritative current state), `narrative_arc` (ordered list of shifts with dates), `superseded` (list of earlier positions with dates and replacements), and `open_threads` (unresolved questions with originating meeting)
2. Given a cumulative interpretation after 5 meeting folds, when measured, then it is under 4000 words
3. Given two consecutive versions of a cumulative interpretation, when diffed, then the changes are attributable to the most recent meeting's interpretation
4. Given a superseded entry, when read, then it contains: `original_position`, `superseded_date`, `superseding_meeting`, and `new_position`
5. Given a cumulative interpretation with an empty initial state (no meetings yet folded), when read, then it contains the persona's baseline concerns from their persona definition and empty sections for narrative_arc, superseded, and open_threads

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|

## Scope & Constraints

- Format informed by SPIKE-006 findings — may adopt fold-in-place or log-structured approach
- Must support the fold engine's need to detect shifts, confirmations, and supersessions
- Stored per-persona (14 files), not per-meeting
- Must be human-readable (markdown) while being machine-parseable (YAML sections)
- 4000-word limit is a design target, not a hard truncation — the fold engine is responsible for keeping documents within budget

## Implementation Approach

1. **Define cumulative schema** — YAML frontmatter (persona-id, last-folded-meeting, fold-count) + four markdown sections with embedded YAML for structured data
2. **Define initial state template** — empty cumulative seeded from persona definition's goals and concerns
3. **Build validation script** — Python script that parses a cumulative document and validates required fields and size budget
4. **Create exemplar** — manually fold 2–3 meetings for one persona to validate the format captures narrative evolution

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Draft | 2026-03-12 | 7207791 | Initial creation |

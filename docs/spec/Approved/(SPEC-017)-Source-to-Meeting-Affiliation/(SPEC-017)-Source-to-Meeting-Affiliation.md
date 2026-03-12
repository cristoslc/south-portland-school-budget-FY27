---
title: "Source-to-Meeting Affiliation"
artifact: SPEC-017
status: Approved
author: cristos
created: 2026-03-12
last-updated: 2026-03-12
parent-epic: EPIC-008
linked-research: []
linked-adrs: []
depends-on:
  - SPEC-016
addresses: []
evidence-pool: ""
swain-do: required
---

# Source-to-Meeting Affiliation

## Problem Statement

Sources in the evidence pool aren't 1:1 with meetings. A budget spreadsheet posted March 4 may belong to the March 2 workshop retroactively or the March 9 workshop prospectively, depending on its content and purpose. The bundler needs semantic logic to affiliate sources with the correct meeting, handling ambiguous cases without manual intervention for every source.

## External Behavior

- **Input:** List of normalized evidence pool sources with metadata (filename, date, source type, evidence pool origin)
- **Output:** Meeting bundle manifests per SPEC-016 schema, written to `data/interpretation/bundles/`
- **Precondition:** SPEC-016 schema is defined; evidence pool sources are normalized
- **Postcondition:** All sources affiliated; bundle manifests valid; no source unaffiliated
- **Invocation:** Python script, runnable as `python scripts/bundle_meetings.py`

## Acceptance Criteria

1. Given a VTT transcript with a meeting date in its filename (e.g., `2026-03-02-school-board-workshop.md`), when the bundler runs, then it is affiliated with the matching meeting
2. Given a presentation posted between two meetings, when the bundler runs with agenda context, then it is affiliated with the meeting where it was presented (not the posting date)
3. Given a standalone policy document unrelated to a specific meeting, when the bundler runs, then it is classified as inter-meeting evidence with appropriate date range
4. Given the complete evidence pool, when the bundler runs, then no source is unaffiliated — every source has a meeting or inter-meeting classification
5. Given a new source added to the evidence pool after initial bundling, when the bundler re-runs, then existing affiliations are preserved and the new source is affiliated
6. Given the bundler is run twice on the same evidence pool with no changes, then the output is identical (idempotent)

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|

## Scope & Constraints

- Affiliation uses heuristics first (filename patterns, dates, source type rules), supplemented by LLM classification only for ambiguous cases
- School budget content is primary; city council content that doesn't touch school budget receives lighter affiliation effort
- The bundler is idempotent — re-running produces the same result
- Must handle the existing evidence pool structure (3 pools: school-board-budget-meetings, fy27-budget-documents, city-council-meetings-2026)

## Implementation Approach

1. **Heuristic affiliation** — filename date matching, source type rules (VTT transcript → meeting with matching date; agenda → meeting with matching date)
2. **Agenda-aware affiliation** — cross-reference agenda items with document titles/content to affiliate presentations and packets with the correct meeting
3. **LLM-assisted affiliation** — for sources that heuristics can't resolve, use LLM to classify based on content
4. **Inter-meeting fallback** — sources that don't match any meeting become inter-meeting evidence
5. **Idempotency layer** — hash-based change detection to skip re-processing unchanged sources
6. **Validate against March evidence** — run against the existing 18+ meetings and 25+ budget documents

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Draft | 2026-03-12 | 7207791 | Initial creation |
| Approved | 2026-03-12 | _pending_ | Approved for implementation |

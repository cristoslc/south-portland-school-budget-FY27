---
title: "Fold Engine"
artifact: SPEC-021
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
  - SPEC-020
  - SPIKE-006
addresses: []
evidence-pool: ""
swain-do: required
---

# Fold Engine

## Problem Statement

When a new meeting is interpreted, its per-persona interpretations must be integrated into each persona's cumulative narrative. The fold must detect what shifted, what's confirmed, and what's been superseded — while preserving temporal markers that record the journey of understanding. This is LLM-driven work: the engine provides the prior cumulative state and the new interpretation, and asks the LLM to produce the updated cumulative.

## External Behavior

- **Input:** Per-meeting interpretation (SPEC-018 format) + existing cumulative interpretation (SPEC-020 format) for one persona
- **Output:** Updated cumulative interpretation (SPEC-020 format)
- **Precondition:** Per-meeting interpretation exists for the meeting being folded; cumulative interpretation exists (or empty state for first meeting)
- **Postcondition:** Updated cumulative reflects the new meeting; passes SPEC-020 validation; is within word budget
- **Invocation:** `python scripts/fold_meeting.py <meeting-id> [--persona PERSONA-NNN]`

## Acceptance Criteria

1. Given a new meeting interpretation with a fact that contradicts the cumulative's `current_understanding`, when folded, then the old position appears in `superseded` with the meeting date and the new position replaces it in `current_understanding`
2. Given a new meeting interpretation that confirms an `open_thread`, when folded, then the thread is resolved and the confirmation is recorded in `narrative_arc` with a date
3. Given a new meeting interpretation with new information not present in the cumulative, when folded, then it appears in `current_understanding` with a "first seen" date
4. Given 14 personas, when the fold engine runs on all of them for one meeting, then all 14 cumulative documents are updated
5. Given a fold operation, when the `narrative_arc` is updated, then the new entry contains the meeting date and a one-line summary of what shifted for this persona
6. Given the same meeting folded twice, when the second fold completes, then the cumulative document is identical to after the first fold (idempotent)

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|

## Scope & Constraints

- Fold is LLM-driven — the engine provides prior cumulative + new interpretation as context and asks for the updated cumulative
- Fold is per-persona (14 independent operations per meeting) — parallelizable
- Fold order matters — meetings must be folded in chronological order
- Word budget enforcement: if the cumulative exceeds 4000 words after fold, the engine must compress older narrative_arc entries (summarize, don't drop)
- The fold engine does not modify per-meeting interpretations — they are immutable inputs

## Implementation Approach

1. **Fold prompt template** — prior cumulative + new interpretation → instructions for producing updated cumulative with shift detection, confirmation marking, and supersession tracking
2. **Fold runner** — iterates over 14 personas for a given meeting, calls LLM, validates output against SPEC-020 schema
3. **Idempotency check** — compare meeting-id against cumulative's `last-folded-meeting`; skip if already folded unless `--force`
4. **Word budget enforcement** — post-fold check; if over budget, run a compression pass on older narrative_arc entries
5. **Sequential fold validation** — test by folding March meetings in order (Jan 12 → Feb → Mar 2 → Mar 9) and verifying narrative arcs emerge

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Draft | 2026-03-12 | 7207791 | Initial creation |

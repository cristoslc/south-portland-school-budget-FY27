---
title: "Interpretation Output Schema"
artifact: SPEC-018
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
  - SPIKE-005
addresses: []
evidence-pool: ""
swain-do: required
---

# Interpretation Output Schema

## Problem Statement

Per-meeting interpretation produces three layers of output (structured points, journey map, unstructured reactions) per persona. Without a defined schema, downstream consumers (cumulative fold, brief generator, future deliverables) can't reliably parse or compose from interpretation output. The schema is the shared data contract between the interpretation engine and everything downstream.

## External Behavior

- **Input:** Raw LLM interpretation output (unstructured text)
- **Output:** Structured interpretation document per persona per meeting, conforming to schema
- **Format:** YAML frontmatter + markdown body, stored in `data/interpretation/meetings/<meeting-id>/<persona-id>.md`
- **Consumers:** SPEC-020 (cumulative fold), SPEC-022 (upcoming-event brief), human reviewers

## Acceptance Criteria

1. Given an interpretation document, when parsed, then it contains three distinct sections: `structured_points`, `journey_map`, and `reactions`
2. Given a `structured_points` section, when parsed, then each point has: `fact` (string), `source_reference` (path + location), `emotional_valence` (positive / negative / neutral), `threat_level` (1–5), and `open_question` (boolean)
3. Given a `journey_map` section, when parsed, then it is an ordered sequence of beats, each with: `position` (sequential order in meeting), `meeting_event` (what happened), `persona_cognitive_state` (what the persona understands at this point), and `persona_emotional_state` (how the persona feels)
4. Given a `reactions` section, when read, then it is free-form markdown written in the persona's voice — first person, reflecting their specific concerns and perspective
5. Given interpretation documents for 3+ personas on the same meeting, when compared, then structured points highlight different facts or assign different valences to shared facts

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|
| AC1 — three sections | validate_interpretation.py checks for Structured Points, Journey Map, Reactions sections; test_validate_interpretation.py confirms | PASS |
| AC2 — structured point fields | Validator enforces fact, source_reference, emotional_valence (positive/negative/neutral), threat_level (1-5), open_question (boolean); 7 tests pass | PASS |
| AC3 — journey map beats | Validator requires 4-column table: Position, Meeting Event, Persona Cognitive State, Persona Emotional State; test_interpretation_schema_contract.py confirms | PASS |
| AC4 — reactions in persona voice | 3 exemplar docs have free-form first-person reactions; validator checks section non-empty (>100 chars) | PASS |
| AC5 — cross-persona differentiation | test_interpretation_examples.py verifies 3 personas have different point headings and valence/threat variation on shared facts | PASS |

## Scope & Constraints

- Schema is an internal data contract — not a publication format
- Must be parseable by Python (YAML frontmatter + markdown body, consistent with existing project patterns)
- Must be human-readable for quality review
- Schema may evolve based on SPIKE-005 findings — design for backward-compatible extension
- Reactions section is deliberately unstructured to preserve interpretive richness

## Implementation Approach

1. **Draft schema** — YAML frontmatter (meeting-id, persona-id, meeting-date, interpretation-date) + three markdown sections with embedded YAML for structured data
2. **Validate against SPIKE-005 outputs** — adjust schema based on what the prompt design spike actually produces
3. **Build validation script** — Python script that parses an interpretation document and validates required fields
4. **Create exemplar documents** — 2–3 interpretation documents for different personas on the same meeting, demonstrating the schema in practice

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Draft | 2026-03-12 | 7207791 | Initial creation |
| Approved | 2026-03-12 | de71f02 | Approved for implementation |
| Implemented | 2026-03-13 | — | All 5 ACs verified; 137 tests pass; validator, schema, exemplars, generator prompt all aligned |

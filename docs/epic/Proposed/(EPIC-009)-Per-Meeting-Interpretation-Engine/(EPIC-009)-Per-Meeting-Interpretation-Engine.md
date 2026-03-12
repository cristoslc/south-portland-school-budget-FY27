---
title: "Per-Meeting Interpretation Engine"
artifact: EPIC-009
status: Proposed
author: cristos
created: 2026-03-12
last-updated: 2026-03-12
parent-vision: VISION-003
success-criteria:
  - Every meeting bundle produces 14 interpretation documents (one per persona)
  - Interpretations demonstrate measurably distinct perspectives across personas
  - Structured points reference specific evidence from the meeting bundle
  - Journey maps reflect the meeting's narrative arc, not just topic lists
depends-on:
  - EPIC-008
addresses: []
evidence-pool: ""
---

# Per-Meeting Interpretation Engine

## Goal / Objective

For each meeting bundle, generate persona-specific interpretations across all 14 validated personas — producing structured points, experiential journey maps, and unstructured reactions that capture what the meeting meant to each stakeholder. This is the core interpretive layer: the place where evidence is transformed from "what happened" into "what it means to this person."

## Scope Boundaries

**In scope:**
- LLM-driven interpretation of meeting bundles through persona lenses
- Three-layer output: structured points, journey map, unstructured reactions
- Output schema definition and validation
- Output storage in the data layer
- Resume capability (restart mid-run without re-processing completed personas)

**Out of scope:**
- Meeting bundling (EPIC-008 handles upstream)
- Cumulative narrative tracking (EPIC-010 handles downstream)
- Output formatting for publication
- Real-time or live-meeting interpretation

## Child Specs

- SPEC-018: Interpretation Output Schema — three-layer output format definition
- SPEC-019: Per-Meeting Interpretation Runner — orchestration across 14 personas

## Key Dependencies

- EPIC-008 (meeting bundles provide input)
- SPIKE-005 (prompt design findings inform implementation)
- 14 Validated personas in docs/persona/Validated/

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-03-12 | 7207791 | Initial creation |

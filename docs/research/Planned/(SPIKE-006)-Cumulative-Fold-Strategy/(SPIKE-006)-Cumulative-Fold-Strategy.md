---
title: "Cumulative Fold Strategy"
artifact: SPIKE-006
status: Planned
author: cristos
created: 2026-03-12
last-updated: 2026-03-12
question: "How should cumulative per-persona narratives be structured and merged so that temporal narrative arcs are preserved without unbounded document growth?"
gate: Pre-MVP
risks-addressed:
  - Unbounded growth of cumulative documents after repeated folds
  - Loss of temporal narrative through repeated summarization
  - Silent supersession of earlier interpretations without audit trail
depends-on: []
evidence-pool: ""
---

# Cumulative Fold Strategy

## Question

How should cumulative per-persona narratives be structured and merged so that temporal narrative arcs are preserved without unbounded document growth?

## Go / No-Go Criteria

- Cumulative document after 5+ meeting folds remains under 4000 words per persona
- Temporal markers (when each persona's understanding shifted) are preserved through fold operations — not averaged or dropped
- Superseded interpretations are explicitly marked with date and replacement, not silently dropped
- Fold output can be diffed against prior version to identify what changed from the most recent meeting
- Fold is deterministic — running the same fold twice on the same input produces identical output

## Pivot Recommendation

If fold-in-place produces unwieldy documents or loses temporal fidelity, pivot to a log-structured approach: keep per-meeting interpretations as immutable records and generate a summary view on demand. This trades query-time computation for storage simplicity and perfect auditability — every interpretation is preserved verbatim. The summary view becomes a read-time concern rather than a write-time merge.

## Findings

_Populated during Active phase._

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Planned | 2026-03-12 | 7207791 | Initial creation |

---
title: "Cumulative Narrative Fold"
artifact: EPIC-010
status: Proposed
author: cristos
created: 2026-03-12
last-updated: 2026-03-12
parent-vision: VISION-003
success-criteria:
  - Cumulative interpretation is the authoritative "where does this persona stand?" document at any point in time
  - Temporal markers record when each persona's understanding shifted
  - Superseded interpretations are explicitly marked, not silently dropped
  - Cumulative documents remain under 4000 words per persona after 10+ meeting folds
depends-on:
  - EPIC-009
addresses: []
evidence-pool: ""
---

# Cumulative Narrative Fold

## Goal / Objective

Integrate each new meeting's per-persona interpretations into running cumulative narratives that track how each stakeholder's understanding evolved across the budget season. The fold captures not just the current state but the journey of understanding — when Maria learned her school might close, when Tom's property tax estimate changed, when the board's position shifted. These arcs are the interpretive richness that makes point-in-time snapshots insufficient.

## Scope Boundaries

**In scope:**
- Fold logic: detecting what shifted, what's confirmed, what's superseded
- Temporal marker preservation across fold operations
- Narrative arc tracking (ordered history of shifts per persona)
- Cumulative document format and schema
- Idempotent folding (same meeting folded twice produces same result)

**Out of scope:**
- Per-meeting interpretation generation (EPIC-009)
- Forward-looking briefs (EPIC-011)
- Publication formatting of cumulative narratives
- Cross-persona comparison or synthesis

## Child Specs

- SPEC-020: Cumulative Interpretation Format — per-persona running narrative schema
- SPEC-021: Fold Engine — integration of new interpretations into cumulative state

## Key Dependencies

- EPIC-009 (per-meeting interpretations provide input)
- SPIKE-006 (fold strategy determines implementation approach)

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-03-12 | _pending_ | Initial creation |

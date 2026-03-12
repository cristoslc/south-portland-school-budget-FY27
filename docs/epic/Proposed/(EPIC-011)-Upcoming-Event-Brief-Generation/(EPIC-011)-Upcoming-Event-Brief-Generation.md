---
title: "Upcoming-Event Brief Generation"
artifact: EPIC-011
status: Proposed
author: cristos
created: 2026-03-12
last-updated: 2026-03-12
parent-vision: VISION-003
success-criteria:
  - Briefs are available before each meeting (production deadline is pre-meeting)
  - Each brief surfaces at least one question or concern per persona relevant to the upcoming agenda
  - Briefs incorporate inter-meeting evidence events (documents posted since last meeting)
  - Briefs build forward from cumulative state, not re-interpret past meetings
depends-on:
  - EPIC-010
addresses: []
evidence-pool: ""
---

# Upcoming-Event Brief Generation

## Goal / Objective

Before each upcoming meeting, generate per-persona forward-looking briefs that synthesize what happened since the last meeting, what's on the agenda, and what each stakeholder should watch for. This is the only pipeline stage with an external scheduling dependency — briefs must exist *before* the meeting they prepare for. The briefs are the pipeline's most time-sensitive output and the most directly actionable for real stakeholders.

## Scope Boundaries

**In scope:**
- Forward-looking brief generation per persona per upcoming meeting
- Inter-meeting evidence integration (documents, media coverage, public statements posted since last meeting)
- Agenda analysis and per-persona implications
- Per-persona question and concern surfacing
- Graceful handling of missing agenda (brief without agenda analysis)

**Out of scope:**
- Cumulative narrative maintenance (EPIC-010)
- Brief formatting for publication (downstream deliverable concern)
- Real-time or live-meeting coverage
- Post-meeting retrospective briefs (that's per-meeting interpretation, EPIC-009)

## Child Specs

- SPEC-022: Upcoming-Event Brief Generator — forward-looking synthesis per persona

## Key Dependencies

- EPIC-010 (cumulative interpretation provides the "current state" input)
- Meeting calendar and agenda availability (external dependency)

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-03-12 | _pending_ | Initial creation |

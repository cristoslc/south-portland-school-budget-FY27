---
title: "Persona Interpretation Pipeline"
artifact: VISION-003
status: Active
product-type: personal
author: cristos
created: 2026-03-11
last-updated: 2026-03-11
depends-on:
  - VISION-001
  - VISION-002
evidence-pool: ""
---

# Persona Interpretation Pipeline

## Target Audience

The project author (cristos) producing the South Portland budget analysis. This pipeline generates the raw interpretive material that feeds every downstream deliverable -- briefings, meeting prep guides, narrative timelines, and formats not yet imagined.

## Value Proposition

The budget process unfolds over months across dozens of meetings, and each stakeholder experiences it differently. A parent watching the March 9 workshop lives a different meeting than a teacher or a taxpayer watching the same session. Today, producing persona-specific interpretations is a manual, per-deliverable effort -- each briefing is crafted from scratch against the full evidence pool. This means interpretations are expensive to produce, inconsistent across personas, and static: they don't capture how each stakeholder's understanding evolved as the budget process unfolded.

This vision creates a pipeline that systematically interprets every meeting through every persona's lens, then folds those interpretations into a cumulative narrative that evolves with the budget season. The result is a library of raw interpretive material -- structured facts, experiential journey maps, and unfiltered reactions -- that any downstream output can draw from. When a new meeting happens, the pipeline processes it once and every persona's understanding updates. When a new output format is needed, the interpretive raw material is already there.

## Problem Statement

The evidence pools (VISION-002) collect and normalize source material. The budget analysis (VISION-001) delivers stakeholder-facing outputs. Between those two layers, there is no systematic interpretive step. Every time an output is produced, interpretation happens ad hoc -- re-reading sources, re-inferring what matters to each persona, re-constructing the narrative arc. This is duplicative, inconsistent, and doesn't scale across 14 personas and a growing evidence base.

The deeper problem is temporal. The budget process is a story that unfolds meeting by meeting. A snapshot analysis captures the current state but loses the narrative: when did Maria learn her school might close? When did Tom's property tax estimate change? When did the board's position shift? These arcs matter for understanding -- and for preparing stakeholders for what comes next -- but they're invisible in a point-in-time briefing.

## Existing Landscape

- **Current briefings** (`dist/briefings/`) -- persona-specific but monolithic. They're authored at a point in time and don't decompose into reusable interpretive units.
- **Evidence pool synthesis** (`docs/evidence-pools/*/synthesis.md`) -- thematic summaries of source material, but persona-agnostic. They describe what happened, not what it means to specific stakeholders.
- **Persona definitions** (`docs/persona/`) -- rich profiles with goals, fears, information needs, and behavioral patterns. These are the interpretation lenses but aren't yet systematically applied to evidence.
- **No existing tool** combines persona-driven interpretation with temporal folding across a series of public meetings.

## Build vs. Buy

Tier 3 -- build from scratch. The interpretive layer is the core intellectual contribution of this project. No existing tool applies a set of stakeholder personas to a corpus of municipal meeting evidence and produces temporally-aware, per-persona interpretations. The pipeline orchestration is custom; the interpretation itself is LLM-driven using the persona definitions as system context.

## Maintenance Budget

Moderate during the active budget season (March-June 2026). Each new meeting triggers a pipeline run: bundling, interpretation across all personas, cumulative fold, and upcoming-event brief generation. The per-run effort should be low (review and approve, not author from scratch), but runs happen every 1-2 weeks as meetings occur. After the budget vote (June 2026), the pipeline can be archived. The interpretive methodology may be reusable for future budget cycles with updated personas and evidence.

## Success Metrics

- Every school board and city council meeting in the remaining budget season has per-persona interpretations generated within 48 hours
- Cumulative interpretations capture narrative arcs that are visible in retrospect (e.g., the Skillin-to-Dyer pivot, the fund balance depletion timeline)
- Upcoming-event briefs are available before each meeting and surface at least one question or concern per persona that proves relevant during the actual meeting
- Downstream deliverables (briefings, prep guides) can be produced by selecting and formatting from the interpretive library rather than re-analyzing raw evidence

## Non-Goals

- Presentation or formatting of outputs -- this produces raw material; how it's packaged for audiences is a separate concern
- Replacing evidence pool collection or normalization (VISION-002 handles that)
- Automated quality judgment -- interpretations are generated material that may need human review before publication
- Real-time or live-meeting interpretation -- the pipeline runs after meetings conclude (or before upcoming ones), not during
- Covering non-budget municipal topics in depth -- city council context is included as operational backdrop, not as primary subject matter

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-11 | fe5cf5c | Created directly in Active after conversational design review |

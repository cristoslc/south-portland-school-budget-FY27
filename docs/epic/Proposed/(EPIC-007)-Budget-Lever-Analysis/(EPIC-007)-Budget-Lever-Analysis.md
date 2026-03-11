---
title: "Budget Lever Analysis and Interactive Dashboard"
artifact: EPIC-007
status: Proposed
author: cristos
created: 2026-03-11
last-updated: 2026-03-11
parent-vision: VISION-001
success-criteria:
  - Budget levers identified and catalogued with dollar amounts and sources
  - Each lever linked to evidence (meeting transcript, slide deck, or budget document)
  - Interactive dashboard allows toggling levers on/off and displays resulting impact on mil rate and budget gap
  - Dashboard reflects the current proposed budget as the baseline
  - At least one alternative budget scenario fully costed via lever combinations
depends-on: []
addresses:
  - JOURNEY-002.PP-03
  - JOURNEY-002.PP-05
  - JOURNEY-001.PP-03
  - JOURNEY-004.PP-01
  - JOURNEY-003.PP-01
evidence-pool: ""
---

# Budget Lever Analysis and Interactive Dashboard

## Goal / Objective

Extract the discrete decision points ("levers") from the FY27 budget evidence — staffing changes, program additions/cuts, capital projects, revenue adjustments, reconfiguration savings — and build an interactive dashboard where a user can toggle levers on/off and immediately see the impact on the tax rate and budget deficit/surplus.

This is the core analysis deliverable of VISION-001: turning opaque budget documents into a tool that lets any resident answer "what if?" questions about the budget.

## Scope Boundaries

**In scope:**

- Systematic extraction of levers from all three evidence pools (school board meetings, budget documents, city council meetings)
- Categorization of levers (expenditure vs. revenue, recurring vs. one-time, discretionary vs. mandated)
- Dollar-amount quantification of each lever with source citations
- Baseline budget model (proposed FY27 budget as-is)
- Tax rate calculation model (assessed valuation, mil rate, state revenue sharing)
- Interactive dashboard (likely HTML/JS, static-hostable) with lever toggles and real-time recalculation
- At least one pre-built "what-if" scenario (e.g., no-closure alternative)

**Out of scope:**

- Advocacy for or against specific lever combinations
- Multi-year forecasting beyond FY27
- Full municipal budget (city side) — school department only
- Real-time data feeds — dashboard uses a point-in-time snapshot
- Native mobile app — web-based and responsive is sufficient

## Child Specs

_To be created. Expected decomposition:_

- Lever extraction and cataloguing (research/analysis spec)
- Budget baseline model (data spec — the numbers behind the dashboard)
- Tax rate calculation engine (computation spec)
- Interactive dashboard UI (frontend spec)

## Key Dependencies

- Evidence pools: `school-board-budget-meetings`, `fy27-budget-documents`, `city-council-meetings-2026` — all currently populated and refreshed
- Assessed valuation and mil rate data from city tax records (may need to be sourced)
- State education subsidy figures for South Portland (EPS allocation)

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-03-11 | _pending_ | Initial creation |

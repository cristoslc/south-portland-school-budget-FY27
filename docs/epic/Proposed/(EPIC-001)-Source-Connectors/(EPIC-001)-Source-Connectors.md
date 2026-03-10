---
title: "Source Connectors"
artifact: EPIC-001
status: Proposed
author: cristos
created: 2026-03-10
last-updated: 2026-03-10
parent-vision: VISION-002
success-criteria:
  - Each connector can discover new content published since its last run
  - Each connector downloads new content to the correct data/ subdirectory
  - Connectors are idempotent -- re-running produces no duplicate downloads
depends-on: []
addresses: []
evidence-pool: ""
---

# Source Connectors

## Goal / Objective

Build individual connectors for each source type that can discover and download new meeting materials. Each connector knows one source site, can detect what's new since the last check, and fetches it to the local `data/` tree.

Three connectors are needed:

1. **Vimeo / SPC-TV** -- Use the Vimeo API to list new videos on the SPC-TV channel, identify school board and city council meetings, and download auto-generated VTT captions.
2. **Diligent Community** -- Scrape the city council's new meeting portal for agenda text. Requires a headless browser (JavaScript-rendered content).
3. **spsdme.org budget page** -- Poll the budget page for new PDF links (packets, presentations, spreadsheets) and download them.

## Scope Boundaries

**In scope:**
- Source discovery (what's new since last run)
- Download to `data/` in the existing directory structure
- De-duplication (skip already-downloaded content)
- Connector-level error handling and logging

**Out of scope:**
- Content normalization (EPIC-002)
- Scheduling and orchestration (EPIC-003)
- BoardDocs connector (platform retired March 2026; historical data already collected)

## Child Specs

_To be created after SPIKE-001 and SPIKE-002 retire key risks._

## Key Dependencies

- SPIKE-001 (Vimeo API access) must confirm API availability before building the Vimeo connector
- SPIKE-002 (Diligent Community scraping) must confirm page structure before building the agenda scraper

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-03-10 | _pending_ | Initial creation |

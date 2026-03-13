---
title: "Meeting Bundler"
artifact: EPIC-008
status: Complete
author: cristos
created: 2026-03-12
last-updated: 2026-03-13
parent-vision: VISION-003
success-criteria:
  - Every source in the evidence pool is affiliated with exactly one meeting or classified as inter-meeting evidence
  - Meeting bundles include all sources presented at or directly supporting that meeting
  - Bundle metadata captures meeting date, body (school board / city council), source manifest, and optional agenda reference
depends-on: []
addresses: []
evidence-pool: ""
---

# Meeting Bundler

## Goal / Objective

Group evidence pool sources into coherent meeting bundles — one bundle per school board or city council meeting/workshop — so that downstream interpretation operates on complete meeting context rather than individual documents. The atomic unit is the meeting, not the document: an interim spreadsheet posted days before a workshop is bundled with the meeting at which it is presented.

## Scope Boundaries

**In scope:**
- Semantic affiliation of sources (transcripts, agendas, presentations, spreadsheets) to specific meetings
- Handling of inter-meeting evidence events (standalone documents not tied to a specific meeting)
- File structure and schema for bundle output
- Idempotent re-bundling when new sources are added

**Out of scope:**
- Evidence collection and normalization (VISION-002 / EPIC-001 through EPIC-006)
- Interpretation of bundled content (EPIC-009)
- Publication or formatting of bundles

## Child Specs

- SPEC-016: Meeting Bundle Schema — data structure and file layout for meeting bundles
- SPEC-017: Source-to-Meeting Affiliation — semantic logic for grouping sources with meetings

## Key Dependencies

- Depends on VISION-002 evidence pipeline being operational (EPIC-001 through EPIC-006 are Complete)
- Evidence pool sources must be normalized to markdown before bundling

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-03-12 | 7207791 | Initial creation |
| Complete | 2026-03-13 | — | SPEC-016 and SPEC-017 both Implemented; 20 bundles, 38 sources affiliated |

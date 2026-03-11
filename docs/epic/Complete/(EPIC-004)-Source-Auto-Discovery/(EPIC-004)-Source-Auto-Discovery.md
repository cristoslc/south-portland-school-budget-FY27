---
title: "Source Auto-Discovery"
artifact: EPIC-004
status: Complete
author: cristos
created: 2026-03-11
last-updated: 2026-03-11
parent-vision: VISION-002
success-criteria:
  - Vimeo connector discovers new SPC-TV videos without manual config edits
  - Budget page connector discovers and downloads new documents without manual config edits
  - Pipeline scheduled runs are fully autonomous — no human intervention between runs
  - Existing manual-config workflow still works as a fallback
depends-on:
  - EPIC-001
addresses: []
evidence-pool: ""
---

# Source Auto-Discovery

## Goal / Objective

Close the auto-discovery gap that makes the scheduled pipeline (EPIC-003) ineffective. Today, 2 of 3 source connectors require manual YAML config edits before they'll find new content — the Vimeo connector uses a static list of video IDs, and the budget page connector has `--discover` but only reports new links without acting on them. Only the Diligent connector auto-discovers via its REST API.

This epic upgrades both connectors so the pipeline's daily cron (`.github/workflows/pipeline.yml`) can run end-to-end without human intervention: discover new sources, download them, normalize to markdown, and stage changes for review.

## Scope Boundaries

**In scope:**
- Vimeo connector: scrape the SPC-TV Vimeo channel page to discover video IDs not in config, auto-add and download them
- Budget page connector: integrate `discover_page_links()` into the normal `run()` flow so new Google Drive/Slides/Sheets links are automatically downloaded
- Config file auto-update: new sources discovered at runtime get appended to YAML config for reproducibility
- Idempotency: re-running discovery produces no duplicates

**Out of scope:**
- Diligent connector changes (already auto-discovers)
- New source types beyond Vimeo and the budget page
- Notification system for discovered sources (review the git diff instead)
- Changes to the normalizers or pipeline runner (EPIC-002/003)

## Child Specs

- **SPEC-009** — Vimeo Channel Auto-Discovery (scrape SPC-TV channel, find new video IDs, auto-download VTTs)
- **SPEC-010** — Budget Page Auto-Discovery (integrate discovery into normal run, auto-download new documents)

## Key Dependencies

- EPIC-001 (Complete) — source connectors must exist before adding auto-discovery to them
- EPIC-003 (Complete) — pipeline runner must exist for scheduled execution

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-03-11 | be16135 | Initial creation |
| Active | 2026-03-11 | e4b15d4 | Decomposed into SPEC-009/010; beginning implementation |
| Complete | 2026-03-11 | _pending_ | All child specs (SPEC-009/010) Implemented |

---
title: "Budget Page Auto-Discovery"
artifact: SPEC-010
status: Implemented
author: cristos
created: 2026-03-11
last-updated: 2026-03-11
parent-epic: EPIC-004
linked-research: []
linked-adrs: []
depends-on: []
addresses: []
evidence-pool: ""
swain-do: required
---

# Budget Page Auto-Discovery

## Problem Statement

The budget page connector (`scripts/connectors/budget_page.py`) has a `--discover` flag that scrapes spsdme.org/budget27 for Google document links, but it only *reports* new links — it doesn't download them or add them to config. Discovery and download are completely separate code paths. This means the scheduled pipeline can't automatically pick up new budget documents; someone must manually copy the discovered URLs into `budget-page-sources.yaml` with metadata.

## External Behavior

**Inputs:**
- Budget page URL (already configured in `budget-page-sources.yaml` as `page_url`)
- Existing `budget-page-sources.yaml` config (list of already-known document URLs)

**Outputs:**
- Newly discovered documents are appended to `budget-page-sources.yaml` with inferred metadata (type, date, label, output path)
- Document files (PDF/XLSX) are downloaded for all new entries
- Log output reports what was discovered and downloaded

**Preconditions:**
- Network access to spsdme.org and Google Drive/Docs

**Postconditions:**
- `budget-page-sources.yaml` contains entries for all document links found on the budget page
- Files exist on disk for all config entries
- Re-running discovery produces no duplicates

**Constraints:**
- Must handle all three Google URL types (Drive files, Slides, Sheets)
- Must infer document type and generate reasonable labels from page context
- Must preserve existing config entries and format

## Acceptance Criteria

1. **Given** the budget page has a Google document link not in config, **when** the connector runs with `--discover`, **then** the new link is appended to `budget-page-sources.yaml` with type, date, label, and output path.

2. **Given** a newly discovered document link, **when** discovery completes, **then** the document is downloaded to the correct output path.

3. **Given** all page links are already in config, **when** the connector runs with `--discover`, **then** no changes are made and exit code is 0.

4. **Given** a discovered link fails to download (network error, permissions), **when** it is added to config, **then** the entry is still written to config and the failure is logged without stopping other downloads.

5. **Given** the pipeline runs `--discover` as part of normal operation, **then** it completes without requiring interactive input or manual config edits.

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|
| AC1: New link appended to config | auto_add_sources() compares discovered links against configured_bases, calls infer_source_metadata() and appends | pass |
| AC2: New document downloaded | After discovery, run() reloads config and download loop picks up new entries via download_file() | pass |
| AC3: Idempotent when all known | auto_add_sources() returns 0 when no new links found, config unchanged | pass |
| AC4: Download failure handled gracefully | download_file() returns False on error, stats["failed"] increments, loop continues to next source | pass |
| AC5: Pipeline integration | pipeline.py passes --discover to budget_page connector via supports_discover flag | pass |

## Scope & Constraints

- Only targets spsdme.org/budget27 — not a general web scraper
- Document type inference: Drive PDFs → "document", Slides → "presentation", Sheets → "document"
- Date inference: use today's date as fallback (page context rarely includes dates)
- Label inference: use the link's surrounding text on the page when possible, otherwise generate from URL
- Output path follows existing convention: `data/school-board/budget-fy27/<type>/<date>-<slug>.<ext>`
- The `--discover` flag changes from report-only to discover-and-download

## Implementation Approach

1. Refactor `discover_page_links()` to return richer metadata (surrounding text for labels)
2. Add `auto_add_sources()` that compares discovered links against config, generates metadata for new ones, and appends to YAML
3. Merge the discover and download paths: when `--discover` is passed, run discovery first, update config, then fall through to the normal download loop
4. Infer output paths from URL type and document metadata
5. Update `pipeline.py` to pass `--discover` to the budget page connector

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Draft | 2026-03-11 | be16135 | Initial creation |
| Approved | 2026-03-11 | e4b15d4 | Fully designed; ready for implementation |
| Implemented | 2026-03-11 | _pending_ | auto_add_sources(), infer_source_metadata(), merged discover+download |

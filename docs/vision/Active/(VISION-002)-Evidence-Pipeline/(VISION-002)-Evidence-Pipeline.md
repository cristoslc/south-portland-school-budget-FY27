---
title: "Automated Evidence Pipeline"
artifact: VISION-002
status: Active
product-type: personal
author: cristos
created: 2026-03-10
last-updated: 2026-03-10
depends-on:
  - VISION-001
evidence-pool: ""
---

# Automated Evidence Pipeline

## Target Audience

The project author (cristos) maintaining the South Portland budget analysis. Secondarily, anyone who forks the analysis methodology for a different municipality or budget cycle.

## Value Proposition

Evidence pools stay current without manual effort. When the school board holds a new workshop or the city council posts an agenda, the pipeline detects it, downloads the source material, normalizes it to markdown, and stages it for synthesis -- so the analysis reflects the latest public record, not a stale snapshot from whenever someone last remembered to check.

## Problem Statement

The budget process runs March through June with meetings every 1-2 weeks across two bodies (school board, city council). Each meeting produces transcripts (Vimeo auto-captions), agenda documents (BoardDocs or Diligent Community), presentation slides (PDFs on spsdme.org), and occasionally spreadsheets. Today, collecting these sources is entirely manual: visit each site, check for new postings, download files, run `parse_vtt.py`, run `build_evidence_pool.py`, and commit. It takes 30-60 minutes per meeting and is easy to fall behind on -- especially when meetings cluster (two bodies meeting the same week).

The risk isn't just inconvenience. Stale evidence pools mean the briefings in `dist/` drift from reality, and the analysis loses credibility at the exact moment the budget process heats up.

## Existing Landscape

- **Current scripts** (`parse_vtt.py`, `build_evidence_pool.py`, `add_key_points.py`) handle transformation but not discovery or download. They assume source files are already local.
- **Vimeo API** -- provides programmatic access to SPC-TV channel videos, including auto-generated captions (VTT). No scraping required; the API is well-documented.
- **BoardDocs / Diligent Community** -- no public API. Agenda text is embedded in JavaScript-rendered pages. BoardDocs was retired in March 2026; Diligent Community is the current platform. Both require scraping.
- **spsdme.org/budget27** -- static page with PDF links. Straightforward to poll for new links.
- **Generic scraping tools** (Scrapy, playwright, curl) -- mature and available. The challenge is site-specific parsing, not scraping infrastructure.
- **swain-search** -- the existing skill handles evidence pool creation interactively (with an agent in the loop). The pipeline would automate the ingest portion and hand off to swain-search for synthesis.

No existing tool combines source discovery, download, normalization, and evidence-pool integration for this specific set of municipal sources.

## Build vs. Buy

Tier 2 -- glue existing tools. The Vimeo API, a headless browser (Playwright), and the existing Python scripts cover 80% of the work. The new code is the orchestration layer: a scheduler that polls known source URLs, detects new content, dispatches the right downloader, runs the normalization scripts, and commits the result. This is a thin integration layer, not a framework.

## Maintenance Budget

Low-to-moderate during the active budget season (March-June 2026). The pipeline should run unattended on a schedule (daily or on-demand). Expect occasional breakage when source sites change markup. After the budget vote (June 2026), the pipeline can be mothballed. If reused for future budget cycles, the site-specific parsers may need updates but the orchestration layer should be stable.

## Success Metrics

- New meeting materials appear in evidence pools within 24 hours of publication, without manual intervention
- Zero missed sources across the remaining budget season (March-June 2026)
- Manual effort per meeting drops from 30-60 minutes to under 5 minutes (review and approve staged changes)

## Non-Goals

- General-purpose web scraping framework -- this is purpose-built for South Portland's specific source sites
- Automated synthesis -- the pipeline collects and normalizes; thematic synthesis remains a human/agent task via swain-search
- Real-time monitoring -- daily polling is sufficient; push notifications and webhooks are out of scope
- Covering non-budget municipal content (planning board, zoning, etc.)

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Draft | 2026-03-10 | _pending_ | Initial creation |
| Active | 2026-03-10 | _pending_ | Accepted; decomposing into epics |

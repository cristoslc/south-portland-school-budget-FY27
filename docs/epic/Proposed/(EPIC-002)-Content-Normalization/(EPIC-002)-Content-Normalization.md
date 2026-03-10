---
title: "Content Normalization"
artifact: EPIC-002
status: Proposed
author: cristos
created: 2026-03-10
last-updated: 2026-03-10
parent-vision: VISION-002
success-criteria:
  - Downloaded VTT files are converted to evidence pool source markdown
  - Downloaded PDFs are converted to evidence pool source markdown
  - HTML agenda extracts are converted to evidence pool source markdown
  - Output format matches existing evidence pool source structure (frontmatter + body)
depends-on:
  - EPIC-001
addresses: []
evidence-pool: ""
---

# Content Normalization

## Goal / Objective

Convert raw downloaded materials into structured markdown that matches the evidence pool source format. The project already has scripts (`parse_vtt.py`, `build_evidence_pool.py`, `add_key_points.py`) that handle parts of this. This epic determines what can be reused as-is, what needs adapting, and what new conversion logic is needed.

Target formats:
- **VTT → markdown** -- `parse_vtt.py` exists but may need adaptation for automated use (currently interactive)
- **PDF → markdown** -- Presentation slides, meeting packets, spreadsheets. May use existing MCP tools (pdf-to-markdown, xlsx-to-markdown) or standalone libraries.
- **HTML → markdown** -- Agenda text scraped from Diligent Community.

Each normalized source must produce a markdown file matching the evidence pool source template: YAML frontmatter (date, type, source URL) and a structured body.

## Scope Boundaries

**In scope:**
- VTT-to-markdown pipeline (building on `parse_vtt.py`)
- PDF-to-markdown pipeline for budget documents and slides
- HTML-to-markdown for scraped agenda content
- Manifest updates (`manifest.yaml`) for each evidence pool when new sources are added

**Out of scope:**
- Thematic synthesis (remains a human/agent task via swain-search)
- Key point extraction (remains manual via `add_key_points.py` until synthesis is automated)
- Source discovery and download (EPIC-001)

## Child Specs

_To be created after SPIKE-003 assesses existing script reusability._

## Key Dependencies

- EPIC-001 (Source Connectors) provides the raw files this epic normalizes
- SPIKE-003 (Normalization Script Reuse) informs how much new code is needed vs. adapting existing scripts

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-03-10 | _pending_ | Initial creation |

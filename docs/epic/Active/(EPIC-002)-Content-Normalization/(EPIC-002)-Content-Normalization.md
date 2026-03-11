---
title: "Content Normalization"
artifact: EPIC-002
status: Active
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

Target formats per SPIKE-003 findings:
- **VTT → markdown** -- `parse_vtt.py` is fully non-interactive and reusable as-is. `build_evidence_pool.py` has the right logic but needs path parameterization.
- **PDF → markdown** -- New capability needed. Python libraries (`pdfplumber` or `pymupdf`) for standalone operation.
- **HTML → markdown** -- Diligent Community returns agenda as HTML via REST API (SPIKE-002). Standard HTML-to-markdown conversion.

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

_To be created when EPIC-002 comes up for implementation._

## Key Dependencies

- EPIC-001 (Active) provides the raw files this epic normalizes
- SPIKE-003 (Complete) -- confirmed parse_vtt.py reusable, build_evidence_pool.py needs refactoring, PDF conversion is new work

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-03-10 | 7e0bc47 | Initial creation |
| Active | 2026-03-10 | 19807c6 | SPIKE-003 complete; script reuse assessed |

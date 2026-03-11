---
title: "XLSX-to-Markdown Normalizer"
artifact: SPEC-011
status: Implemented
author: cristos
created: 2026-03-11
last-updated: 2026-03-11
parent-epic: EPIC-002
linked-research: []
linked-adrs: []
depends-on: []
addresses: []
evidence-pool: ""
swain-do: required
---

# XLSX-to-Markdown Normalizer

## Problem Statement

The budget page connector downloads spreadsheets (Google Sheets exported as XLSX) but the pipeline has no normalizer for them. `pipeline.py normalize` logs "No normalizer for .xlsx — skipping" and the spreadsheet data never enters the evidence pool. Currently there is one XLSX file (`2026-03-02-models-and-matrix.xlsx`) that contains budget models and cost matrices — key budget analysis data that should be searchable in the evidence pool alongside PDFs and transcripts.

## External Behavior

**Inputs:**
- An XLSX file path
- Target evidence pool directory
- Title string and optional date

**Outputs:**
- A markdown file in the evidence pool's `sources/` directory containing the spreadsheet data as markdown tables (one section per sheet)
- Updated manifest.yaml with the new source entry

**Preconditions:**
- openpyxl is available (Python XLSX reader — no Java dependency unlike xlrd for xls)
- Target evidence pool directory exists with a manifest.yaml

**Postconditions:**
- Markdown file created with one `## Sheet: <name>` section per non-empty worksheet
- Each sheet rendered as a markdown table
- Manifest updated with source-id, hash, and file reference
- Duplicate detection via SHA-256 hash (same as other normalizers)

**Constraints:**
- Must follow the same pool_utils patterns as normalize_pdf and normalize_vtt
- Must handle sheets with merged cells, empty rows, and mixed types gracefully
- Must be callable as `python3 -m pipeline.normalize_xlsx`

## Acceptance Criteria

1. **Given** an XLSX file with one sheet, **when** normalized, **then** produces a markdown file with the sheet content as a markdown table.

2. **Given** an XLSX file with multiple sheets, **when** normalized, **then** each non-empty sheet gets its own `## Sheet: <name>` section.

3. **Given** an XLSX file already in the manifest (by hash), **when** normalized again, **then** it is skipped as a duplicate.

4. **Given** the pipeline runs `normalize` with XLSX files present, **when** complete, **then** XLSX files are processed alongside PDFs and VTTs.

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|
| 1. Single-sheet XLSX → markdown table | `normalize_xlsx.py` renders each sheet as markdown table with header + separator + data rows | Pass |
| 2. Multi-sheet XLSX → sections per sheet | Tested on `2026-03-02-models-and-matrix.xlsx`: produced 3 `## Sheet:` sections (Overview, Matrix, COMBINED) | Pass |
| 3. Duplicate detection via hash | Uses `pool_utils.find_duplicate()` with SHA-256 hash; second run skips with "duplicate of source" message | Pass |
| 4. Pipeline integration | `.xlsx` case added to `normalize_file()` in `pipeline.py`; `pipeline.py normalize` processed 38 files with 0 failures including XLSX | Pass |

## Scope & Constraints

- Only targets XLSX format (not legacy XLS or CSV)
- Does not interpret formulas — reads cell values only
- Does not preserve cell formatting, colors, or conditional formatting
- Large sheets (1000+ rows) are included in full — no truncation
- Empty sheets are skipped silently

## Implementation Approach

1. Create `pipeline/normalize_xlsx.py` following the normalize_pdf pattern
2. Use openpyxl to read worksheets and cell values
3. Convert each sheet to a markdown table (header row + data rows)
4. Wire into `pipeline.py` — add `.xlsx` handling in `normalize_file()` and `resolve_pool()`
5. Add openpyxl to the GitHub Actions workflow dependencies

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Draft | 2026-03-11 | 78dce64 | Initial creation |
| Implemented | 2026-03-11 | 465b58c | Normalizer created, tested, integrated into pipeline |

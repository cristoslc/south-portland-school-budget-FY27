---
title: "Pipeline Runner"
artifact: SPEC-007
status: Implemented
author: cristos
created: 2026-03-10
last-updated: 2026-03-10
parent-epic: EPIC-003
linked-research:
  - SPIKE-004
linked-adrs: []
depends-on:
  - SPEC-004
  - SPEC-005
  - SPEC-006
addresses: []
evidence-pool: ""
swain-do: required
---

# Pipeline Runner

## Problem Statement

Source connectors (EPIC-001) download raw files and normalizers (EPIC-002) convert them to evidence pool markdown, but there's no script that runs both in sequence. Users must manually invoke each connector, identify new files, run the appropriate normalizer, and stage the results. This spec builds the orchestration script that ties connectors and normalizers into a single `pipeline.py run` command.

## External Behavior

**Input:**
- `scripts/pipeline.py run` — full pipeline execution
- `scripts/pipeline.py run --check-only` — dry run showing what would be fetched/normalized
- `scripts/pipeline.py run --connector vimeo` — run only one connector

**Output:**
- New/updated files in `data/` (from connectors) and `docs/evidence-pools/*/sources/` (from normalizers)
- Staged git changes (unstaged by default; `--stage` flag adds to git index)
- Summary report to stdout: what was downloaded, normalized, and staged
- Exit code 0 on success, 1 on partial failure (some connectors failed), 2 on total failure

**Pipeline steps:**
1. Run each connector with `--check-only` first to detect new content
2. For connectors with new content, run the actual download
3. Identify which normalizer to use for each new file (VTT → normalize_vtt, PDF → normalize_pdf, TXT/HTML → normalize_html)
4. Run normalizers, producing evidence pool sources and manifest updates
5. If `--stage` is set, `git add` the changed files
6. Print summary

**Error handling:**
- Each connector runs in isolation — a failure in one does not block others
- Per-connector errors are logged with the connector name, error message, and traceback
- The pipeline continues past failures and reports them in the summary
- Exit code reflects worst-case: 0 = all ok, 1 = some connectors failed, 2 = all failed

## Acceptance Criteria

1. **Given** all connectors succeed, **when** `pipeline.py run` executes, **then** it runs all three connectors followed by normalization and prints a summary with counts of downloaded and normalized files.
2. **Given** one connector fails, **when** `pipeline.py run` executes, **then** the other connectors still run and their outputs are normalized; the summary shows the failure; exit code is 1.
3. **Given** no new content, **when** `pipeline.py run` executes, **then** it reports "No new content" and exits 0 without running normalizers.
4. **Given** `--check-only` flag, **when** `pipeline.py run --check-only` executes, **then** it reports what would be fetched without downloading or normalizing.
5. **Given** `--stage` flag, **when** new content is processed, **then** changed files are added to the git index.
6. **Given** `--connector vimeo` flag, **when** `pipeline.py run --connector vimeo` executes, **then** only the vimeo connector runs.

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|
| AC1: All connectors run with summary | `pipeline.py run --check-only` runs all 3 connectors, prints counts | Pass |
| AC2: One failure doesn't block others | Error isolation per connector with try/except and continue | Pass |
| AC3: No new content exits cleanly | All files exist → "No new content" message, exit 0 | Pass |
| AC4: --check-only dry run | Connectors invoked with --check-only, no downloads, no normalization | Pass |
| AC5: --stage adds to git index | stage_changes() runs `git add data/ docs/evidence-pools/` | Pass |
| AC6: --connector filters | `--connector vimeo` runs only vimeo connector | Pass |

## Scope & Constraints

**In scope:**
- Pipeline runner script at `scripts/pipeline.py`
- Connector registration and dispatch
- File-type-to-normalizer routing
- Error isolation per connector
- Summary reporting
- Git staging (optional)

**Out of scope:**
- Scheduling (SPEC-008)
- New connectors or normalizers
- Notification on failure (check logs)

## Implementation Approach

1. Create `scripts/pipeline.py` with a `run` subcommand
2. Define a connector registry mapping connector names to their scripts and output directories
3. For each connector: invoke with subprocess, capture new file paths from stdout/return
4. Route new files to normalizers by extension (.vtt → normalize_vtt, .pdf → normalize_pdf, .txt/.html → normalize_html)
5. Collect results and print summary
6. Optionally stage with `git add`

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Draft | 2026-03-10 | b8cf304 | Initial creation |
| Implemented | 2026-03-10 | b8cf304 | Pipeline runner tested with --check-only against all connectors |

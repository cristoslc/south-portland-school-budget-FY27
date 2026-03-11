---
title: "Vimeo Channel Auto-Discovery"
artifact: SPEC-009
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

# Vimeo Channel Auto-Discovery

## Problem Statement

The Vimeo connector (`scripts/connectors/vimeo.py`) only processes video IDs listed in `vimeo-sources.yaml`. New SPC-TV videos are posted every 1-2 weeks during budget season, but the pipeline can't find them — someone must manually look up the Vimeo ID and add it to the config. This makes the scheduled pipeline run useless for Vimeo content.

## External Behavior

**Inputs:**
- SPC-TV Vimeo channel URL (configured in `vimeo-sources.yaml` as `channel` field)
- Existing `vimeo-sources.yaml` config (list of already-known video IDs)

**Outputs:**
- Newly discovered videos are appended to `vimeo-sources.yaml` with inferred metadata (type, date, output path)
- VTT files are downloaded for all new videos that have auto-generated captions
- Log output reports what was discovered and downloaded

**Preconditions:**
- `yt-dlp` is available on PATH
- Network access to Vimeo

**Postconditions:**
- `vimeo-sources.yaml` contains entries for all discoverable SPC-TV videos with captions
- VTT files exist on disk for all config entries
- Re-running discovery produces no duplicates

**Constraints:**
- Must not require a Vimeo API token (use yt-dlp channel listing or page scraping)
- Must infer meeting type (school-board vs city-council) and date from video metadata
- Must preserve existing config entries and format

## Acceptance Criteria

1. **Given** the SPC-TV channel has a video not in `vimeo-sources.yaml`, **when** the connector runs with `--discover`, **then** the new video ID is appended to the config file with correct metadata.

2. **Given** a newly discovered video has auto-generated captions, **when** discovery completes, **then** the VTT file is downloaded to the correct output path.

3. **Given** all channel videos are already in config, **when** the connector runs with `--discover`, **then** no changes are made to the config file and exit code is 0.

4. **Given** a video has no auto-generated captions, **when** discovered, **then** it is added to config but logged as "no captions available" without failing the run.

5. **Given** the pipeline runs `--discover` as part of normal operation, **then** it completes without requiring interactive input or manual config edits.

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|
| AC1: New video appended to config | discover_and_update() compares channel videos against known_ids, calls infer_metadata() and appends to sources list | pass |
| AC2: VTT downloaded for new video | After discovery, run() reloads config and download loop picks up new entries via download_vtt() | pass |
| AC3: Idempotent when all known | discover_and_update() returns 0 when no new videos found, config unchanged | pass |
| AC4: No-captions video handled | download_vtt() logs warning and returns False, stats["failed"] increments but run continues | pass |
| AC5: Pipeline integration | pipeline.py passes --discover to vimeo connector via supports_discover flag | pass |

## Scope & Constraints

- Only targets the SPC-TV Vimeo channel — not a general Vimeo discovery tool
- Meeting type inference uses video title keywords ("School Board", "City Council", etc.)
- Date inference uses the video upload/publish date from yt-dlp metadata
- Output path follows the existing convention: `data/<type>/meetings/<date>/transcript.en-x-autogen.vtt`
- The `--discover` flag integrates with the existing `run()` flow — discovery happens before the download loop

## Implementation Approach

1. Add a `discover_channel()` function that uses `yt-dlp --flat-playlist` to list all videos on the SPC-TV channel
2. Compare discovered video IDs against existing config entries
3. For new videos, extract metadata (title, date) via `yt-dlp --dump-json`
4. Infer meeting type from title keywords, generate output path from convention
5. Append new entries to `vimeo-sources.yaml`
6. Run the existing download loop (which will pick up the new entries)
7. Wire `--discover` flag into the CLI and update `pipeline.py` to pass it

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Draft | 2026-03-11 | be16135 | Initial creation |
| Approved | 2026-03-11 | e4b15d4 | Fully designed; ready for implementation |
| Implemented | 2026-03-11 | _pending_ | discover_channel(), infer_metadata(), --discover CLI flag |

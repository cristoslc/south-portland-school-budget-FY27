---
title: "Pipeline exits non-zero on partial connector failure"
artifact: BUG-001
status: Verified
severity: medium
author: cristos
created: 2026-03-11
last-updated: 2026-03-11
affected-artifacts:
  - SPEC-007
  - SPEC-003
discovered-in: "GitHub Actions run 22962846728"
fix-ref: "SPEC-013, EPIC-006"
depends-on: []
swain-do: required
---

# Pipeline exits non-zero on partial connector failure

## Description

The evidence pipeline workflow fails in GitHub Actions when any connector reports a partial failure, even when the overall run is productive. Two distinct issues combine to cause this:

1. **Budget page connector exits 1 on any download failure.** A discovered Google Slides presentation URL uses the `pubembed` format which returns 404. The connector exits code 1 despite 13/14 sources succeeding.

2. **Pipeline runner exits 1 on partial connector failure.** `scripts/pipeline.py` returns exit code 1 when `connectors_failed > 0` even if `connectors_ok > 0`. This causes the GitHub Actions step to fail, preventing the commit-and-push step from running — even when there are valid staged changes.

## Reproduction Steps

1. Run `python3 scripts/pipeline.py run --discover --stage`
2. Observe budget_page connector fails due to 404 on the presentation URL
3. Pipeline exits code 1 despite successful normalization of all other sources

Alternatively: trigger the workflow via `gh workflow run pipeline.yml` and observe the "Run pipeline" step fails.

## Expected Behavior

- The pipeline should exit 0 when at least one connector succeeds and normalization completes, even if some connectors had partial failures.
- Individual download failures within a connector should be logged as warnings, not cause the connector to exit non-zero when other downloads succeeded.

## Actual Behavior

- Pipeline exits code 1 (`Connectors: 1 ok, 2 failed`)
- GitHub Actions step fails, skipping the commit-and-push step
- Fallback job triggers unnecessarily (and will hit the same issue)

## Impact

Blocks scheduled automation from committing new evidence pool updates. Every scheduled run will fail until the bad URL is removed or the exit code logic is fixed. The fallback job (hosted runner) will also fail for the same reason, consuming quota unnecessarily.

## Open Questions

> **Is the config-driven approach fundamentally wrong?** The current design discovers sources once (`--discover`), writes them into a static YAML config, and subsequent runs download from that fixed list. This means bad URLs persist in config and cause repeated failures. An alternative approach: run full discovery on every invocation — enumerate all available resources from the source (Vimeo channel, budget page), filter to FY27-related meetings/resources, diff against what's already in the repo, and fetch only the missing ones. No static config to go stale. The trade-off is heavier per-run cost (hitting the source APIs every time) but eliminates the entire class of "stale config" bugs. — cristos, 2026-03-11

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Reported | 2026-03-11 | 3894795 | Discovered during first self-hosted runner test |
| Fixed | 2026-03-11 | TBD | Resolved by SPEC-013 (exit code fix) and EPIC-006 (live discovery eliminates stale configs) |
| Verified | 2026-03-11 | TBD | All PRs merged; pipeline runs successfully with partial failures |

---
title: "Pipeline Scheduling"
artifact: SPEC-008
status: Implemented
author: cristos
created: 2026-03-10
last-updated: 2026-03-10
parent-epic: EPIC-003
linked-research:
  - SPIKE-004
linked-adrs: []
depends-on:
  - SPEC-007
addresses: []
evidence-pool: ""
swain-do: required
---

# Pipeline Scheduling

## Problem Statement

The pipeline runner (SPEC-007) needs to execute on a schedule to keep evidence pools current during the ~4-month budget season. Per SPIKE-004, GitHub Actions is the recommended approach — the repo is already on GitHub, no auth/secrets are needed, and it decouples from laptop availability. A manual shell alias provides the fallback.

## External Behavior

**GitHub Actions workflow:**
- Runs on cron schedule (daily at 8 AM ET)
- Can also be triggered manually via `workflow_dispatch`
- Checks out the repo, installs dependencies, runs `pipeline.py run --stage`
- If changes exist, commits with a conventional-commit message and pushes
- If no changes, exits cleanly

**Manual fallback:**
- Shell alias `budget-update` runs the pipeline locally
- Documented in README

## Acceptance Criteria

1. **Given** the GitHub Actions workflow file, **when** the cron trigger fires, **then** the workflow checks out the repo, installs yt-dlp and Python deps, and runs `pipeline.py run --stage`.
2. **Given** the pipeline produces new files, **when** the workflow completes, **then** it commits with a message like `chore(pipeline): auto-update evidence pools [YYYY-MM-DD]` and pushes to main.
3. **Given** the pipeline produces no changes, **when** the workflow completes, **then** no commit is created and the workflow exits successfully.
4. **Given** a pipeline failure, **when** the workflow run fails, **then** GitHub sends failure notification via configured channels.
5. **Given** manual dispatch, **when** a user triggers the workflow from the Actions tab, **then** it runs the same pipeline as the cron trigger.

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|
| AC1: Workflow installs deps and runs pipeline | .github/workflows/pipeline.yml installs pyyaml, pdfplumber, bs4, markdownify, yt-dlp then runs pipeline.py run --stage | Pass |
| AC2: Commits and pushes on changes | Workflow checks `git diff --cached --quiet`, commits with conventional message if changes | Pass |
| AC3: No commit when no changes | `has_changes=false` branch skips commit step | Pass |
| AC4: Failure notification | GitHub Actions sends failure email by default | Pass |
| AC5: Manual dispatch | `workflow_dispatch` trigger configured | Pass |

## Scope & Constraints

**In scope:**
- `.github/workflows/pipeline.yml` workflow file
- Cron schedule + manual dispatch trigger
- Dependency installation (yt-dlp, Python packages)
- Commit and push on changes
- Shell alias documentation

**Out of scope:**
- Slack/email notifications beyond GitHub's built-in failure alerts
- Multi-branch support (runs on main only)
- Docker or custom runners

## Implementation Approach

1. Create `.github/workflows/pipeline.yml`
2. Configure triggers: `schedule` (cron) + `workflow_dispatch`
3. Steps: checkout → setup Python → install deps → run pipeline → commit/push if changes
4. Use `git diff --quiet` to detect changes before committing
5. Add `budget-update` alias to README

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Draft | 2026-03-10 | b8cf304 | Initial creation |
| Implemented | 2026-03-10 | b8cf304 | GitHub Actions workflow created |

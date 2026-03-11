---
title: "Pipeline Orchestration"
artifact: EPIC-003
status: Complete
author: cristos
created: 2026-03-10
last-updated: 2026-03-10
parent-vision: VISION-002
success-criteria:
  - Pipeline runs end-to-end unattended (discover → download → normalize → stage)
  - Changes are staged as a reviewable git diff, not auto-committed without review
  - Pipeline can be triggered manually or on a schedule
  - Failed runs produce clear error logs identifying which connector/step failed
depends-on:
  - EPIC-001
  - EPIC-002
addresses: []
evidence-pool: ""
---

# Pipeline Orchestration

## Goal / Objective

Build the runner that ties source connectors (EPIC-001) and content normalization (EPIC-002) into a single end-to-end pipeline. On each run, it:

1. Invokes each source connector to check for new content
2. Runs normalization on any new downloads
3. Updates evidence pool manifests
4. Stages changes as a git diff for human review
5. Optionally commits with a conventional-commit message summarizing what was added

The pipeline should support both manual invocation (`./scripts/pipeline.py run`) and scheduled execution.

## Scope Boundaries

**In scope:**
- Pipeline runner script that sequences connectors → normalization → staging
- Change detection (skip runs when nothing is new)
- Error handling and per-connector failure isolation (one broken connector doesn't block others)
- Logging with enough detail to diagnose failures
- Scheduling via GitHub Actions (SPIKE-004 recommendation)

**Out of scope:**
- The connectors themselves (EPIC-001)
- The normalization logic (EPIC-002)
- Complex CI/CD beyond the single GitHub Actions workflow
- Notification system (check logs manually or review staged changes)

## Child Specs

- **SPEC-007** — Pipeline Runner (orchestration script tying connectors → normalization → staging)
- **SPEC-008** — Pipeline Scheduling (GitHub Actions workflow + manual alias fallback)

## Key Dependencies

- EPIC-001 and EPIC-002 must be at least partially implemented before the pipeline has anything to orchestrate
- SPIKE-004 (Complete) -- GitHub Actions recommended, manual alias as fallback

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-03-10 | b8cf304 | Initial creation |
| Active | 2026-03-10 | b8cf304 | SPIKE-004 complete; GitHub Actions approach selected |
| Complete | 2026-03-10 | b8cf304 | All child specs (SPEC-007/008) Implemented |

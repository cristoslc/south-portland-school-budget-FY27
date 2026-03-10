---
title: "Pipeline Orchestration"
artifact: EPIC-003
status: Proposed
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
- Scheduling mechanism (cron, launchd, or similar)

**Out of scope:**
- The connectors themselves (EPIC-001)
- The normalization logic (EPIC-002)
- CI/CD integration (this runs locally on the author's machine)
- Notification system (check logs manually or review staged changes)

## Child Specs

_To be created after SPIKE-004 determines scheduling approach._

## Key Dependencies

- EPIC-001 and EPIC-002 must be at least partially implemented before the pipeline has anything to orchestrate
- SPIKE-004 (Scheduling Approach) informs the execution model

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-03-10 | _pending_ | Initial creation |

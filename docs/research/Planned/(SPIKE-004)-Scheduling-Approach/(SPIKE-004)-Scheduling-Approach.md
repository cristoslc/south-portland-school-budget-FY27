---
title: "Pipeline Scheduling Approach"
artifact: SPIKE-004
status: Planned
author: cristos
created: 2026-03-10
last-updated: 2026-03-10
question: "What is the simplest reliable way to run the evidence pipeline on a schedule from a personal Mac?"
gate: Pre-MVP
risks-addressed:
  - macOS cron/launchd jobs may not run reliably on a laptop that sleeps
  - Cloud-based scheduling (GitHub Actions) may not have access to local git repo or credentials
depends-on: []
evidence-pool: ""
---

# Pipeline Scheduling Approach

## Question

What is the simplest reliable way to run the evidence pipeline on a daily or on-demand schedule? Options to evaluate:

1. **launchd (macOS)** -- native, runs on wake from sleep, but plist configuration is verbose and debugging is painful.
2. **cron** -- simpler config, but doesn't handle sleep/wake well on macOS.
3. **GitHub Actions** -- runs in the cloud, can push results back. Requires secrets for Vimeo API token and git push credentials. Decoupled from laptop availability.
4. **Manual with a reminder** -- just run `./scripts/pipeline.py run` when reminded. Simplest but defeats the "automated" goal.

Key constraints: runs on the author's MacBook, budget season is ~4 months, pipeline needs git access to commit staged changes.

## Go / No-Go Criteria

- **Go:** One of the options can reliably execute the pipeline at least once per day during budget season with less than 30 minutes of setup.
- **No-Go:** All options require significant infrastructure investment (server, Docker, CI pipeline configuration) disproportionate to a 4-month personal project.

## Pivot Recommendation

If fully automated scheduling proves too heavy: use a hybrid approach -- manual trigger (`./scripts/pipeline.py run`) wrapped in a shell alias, with a daily calendar reminder. Accept "semi-automated" over "fully automated" to preserve the maintenance budget.

## Findings

_To be populated during Active phase._

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Planned | 2026-03-10 | _pending_ | Initial creation |

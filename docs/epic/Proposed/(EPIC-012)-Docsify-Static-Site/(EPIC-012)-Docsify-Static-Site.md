---
title: "Docsify Static Site for Briefing Presentation"
artifact: EPIC-012
status: Proposed
author: cristos
created: 2026-03-13
last-updated: 2026-03-13
parent-vision: VISION-001
success-criteria:
  - Briefings are browsable as a static site served via GitHub Pages
  - Docsify is vendored into the repository (no CDN dependency at runtime)
  - Site renders per-persona and per-meeting briefings with working navigation
  - Deployment is automated via GitHub Actions on push to main
depends-on:
  - EPIC-009
  - EPIC-010
  - EPIC-011
addresses: []
evidence-pool: ""
---

# Docsify Static Site for Briefing Presentation

## Goal / Objective

Publish the pipeline's interpretation outputs — per-meeting briefings, cumulative narratives, and upcoming-event briefs — as a browsable static site using docsify, served via GitHub Pages. This is the presentation layer that makes the analysis accessible to the stakeholders described in VISION-001. The site should work without external CDN dependencies (docsify vendored locally) and deploy automatically.

## Scope Boundaries

**In scope:**
- Vendor docsify assets into the repository (JS, CSS, fonts)
- Site structure and navigation for briefings (by meeting, by persona, cumulative)
- GitHub Pages deployment via GitHub Actions
- Minimal theming/configuration for readability
- Landing page with project context and navigation

**Out of scope:**
- Interactive budget dashboard or visualizations (EPIC-007)
- Content generation — this epic consumes outputs from EPICs 009/010/011, not creates them
- Custom docsify plugins or extensions beyond what's needed for navigation
- Authentication or access control — the site is public
- Search indexing beyond docsify's built-in client-side search

## Child Specs

- SPIKE-007: Docsify Vendoring and GitHub Pages — research spike to determine vendoring approach, directory layout, and GH Pages configuration
- _(Further specs TBD after spike completes)_

## Key Dependencies

- EPIC-009 (per-meeting interpretation outputs provide the content)
- EPIC-010 (cumulative narrative provides the rolling context)
- EPIC-011 (upcoming-event briefs provide the time-sensitive content)
- SPIKE-007 must complete before implementation specs are written

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-03-13 | _pending_ | Initial creation |

---
title: "Docsify Vendoring and GitHub Pages"
artifact: SPIKE-007
status: Planned
author: cristos
created: 2026-03-13
last-updated: 2026-03-13
question: "How should docsify be vendored into the repository, and what is the minimal configuration needed to serve briefing content via GitHub Pages?"
gate: Pre-implementation
risks-addressed:
  - Docsify CDN dependency creates availability and privacy risk for a public-interest site
  - Unknown whether docsify's markdown rendering handles the interpretation output format without modification
  - GitHub Pages deployment path (Actions vs. branch-based) affects repo structure
depends-on: []
evidence-pool: ""
---

# Docsify Vendoring and GitHub Pages

## Question

How should docsify be vendored into the repository, and what is the minimal configuration needed to serve briefing content via GitHub Pages?

Specific sub-questions:
1. **Vendoring approach:** What files need to be committed (docsify core JS, CSS, search plugin)? NPM download + commit, or direct asset download? What version?
2. **Directory layout:** Where should the site root live relative to the repo root? (`/site`, `/docs-site`, or a dedicated branch?)
3. **Content mapping:** How do docsify sidebars/navigation map to the briefing structure (by-meeting, by-persona, cumulative)? Does docsify natively handle the nested markdown structure in `data/interpretation/`?
4. **GitHub Pages config:** GitHub Actions deploy from a build step, or serve directly from a directory? Does the vendored-asset approach work with GH Pages, or does it need a build step?
5. **Rendering fidelity:** Do the existing interpretation markdown files render correctly in docsify without modification, or do they need frontmatter stripping, link rewriting, or structural changes?

## Go / No-Go Criteria

- **Go:** Docsify can be vendored in ≤ 5 files, serves the existing markdown with minor or no modifications, and GH Pages deployment can be configured with a single workflow file.
- **No-Go:** Docsify requires a build/bundling step that adds toolchain complexity, or the interpretation markdown requires non-trivial transformation to render.

## Pivot Recommendation

If docsify proves too heavyweight or incompatible:
- **Alternative A:** Plain HTML + GitHub Pages with a static site generator (e.g., mkdocs, which has similar single-page-app behavior but with a build step)
- **Alternative B:** Raw markdown browsing via GitHub's native rendering (no custom site, but zero infrastructure)

## Findings

_To be populated during Active phase._

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Planned | 2026-03-13 | 1e48d39 | Initial creation |

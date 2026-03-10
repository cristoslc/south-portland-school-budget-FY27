---
title: "Diligent Community Agenda Scraping"
artifact: SPIKE-002
status: Planned
author: cristos
created: 2026-03-10
last-updated: 2026-03-10
question: "Can we reliably extract meeting agenda text from the Diligent Community portal using a headless browser?"
gate: Pre-MVP
risks-addressed:
  - Diligent Community may use anti-scraping measures (CAPTCHA, bot detection)
  - Page structure may be too dynamic or session-dependent for reliable automated extraction
depends-on: []
evidence-pool: ""
---

# Diligent Community Agenda Scraping

## Question

Can we reliably extract meeting agenda text from the Diligent Community portal (southportland-gov.community.diligentoneplatform.com) using a headless browser? Specifically:

1. What is the page structure? Is agenda content rendered client-side or server-side?
2. Does the portal require authentication or use anti-bot measures?
3. Can we enumerate meetings programmatically (list page with date filtering)?
4. Is the agenda content in a parseable structure, or is it embedded in an iframe/PDF viewer?

## Go / No-Go Criteria

- **Go:** Playwright can load the meeting list page, navigate to a specific meeting, and extract agenda text as structured content (HTML with identifiable sections). No CAPTCHA or login required for public meetings.
- **No-Go:** Portal requires authentication, deploys bot detection that blocks headless browsers, or embeds agendas as non-parseable PDFs without text layers.

## Pivot Recommendation

If scraping fails: monitor the portal manually but reduce effort by setting a calendar reminder on known meeting dates and using a browser bookmarklet to extract/save the agenda text in one click. Alternatively, check if Diligent Community sends email notifications that could be parsed.

## Findings

_To be populated during Active phase._

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Planned | 2026-03-10 | _pending_ | Initial creation |

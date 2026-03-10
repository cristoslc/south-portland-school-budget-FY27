---
title: "Vimeo VTT Download via Playwright"
artifact: SPIKE-001
status: Complete
author: cristos
created: 2026-03-10
last-updated: 2026-03-10
question: "Can a Playwright script navigate to a Vimeo video page, intercept the auto-generated VTT caption URL from network requests, and download it?"
gate: Pre-MVP
risks-addressed:
  - Vimeo may block headless browsers or require login to access caption tracks
  - VTT URL pattern may be dynamic/signed and not interceptable from network requests
depends-on: []
evidence-pool: ""
---

# Vimeo VTT Download via Playwright

## Question

Can a Playwright script automate the VTT caption download that was previously done via the Claude Code browser MCP tools? Specifically:

1. Can Playwright load a Vimeo video page (e.g., `https://vimeo.com/1152242786`) without login?
2. Does the player's network traffic expose the auto-generated VTT caption URL?
3. Can we intercept and download that VTT file programmatically?
4. Does this work for the SPC-TV channel videos consistently across different meetings?

## Go / No-Go Criteria

- **Go:** Playwright can load a known SPC-TV video page, capture the VTT URL from network requests, and download a valid VTT file matching the existing transcript. Works for at least 2 different meeting videos.
- **No-Go:** Vimeo blocks headless browsers, requires authentication for caption access, or the VTT URL is not exposed in interceptable network traffic.

## Pivot Recommendation

If Playwright can't intercept the VTT URL: try the Vimeo API with a free-tier token as a fallback. If neither works: keep using the Claude Code browser MCP tools manually (the known-working approach) and accept that transcript download stays semi-automated.

## Findings

### Playwright: No-Go

Vimeo uses **Cloudflare Turnstile** bot detection on the player embed endpoint (`player.vimeo.com/video/{id}`). Headless Playwright gets a 401 on the initial request and all subsequent traffic is Cloudflare challenge flows. The player config endpoint (`/config`) returns 403 even with referer headers set. No VTT URLs are exposed in any interceptable network traffic.

**Playwright is not viable for Vimeo VTT download.**

### yt-dlp: Go

`yt-dlp` (already installed at `/opt/homebrew/bin/yt-dlp`, version 2026.02.21) downloads VTT captions with **zero authentication**:

```bash
yt-dlp --write-sub --sub-lang en-x-autogen --sub-format vtt --skip-download \
  -o "output.%(ext)s" "https://vimeo.com/{VIMEO_ID}"
```

**Tested on two SPC-TV videos:**
- `1152242786` (City Council 2026-01-06) -- 91 KB VTT, valid content
- `1169968145` (Budget Workshop 2026-03-02) -- 336 KB VTT, valid content

Both produced valid WEBVTT files with timestamped captions matching the `en-x-autogen` track. yt-dlp handles Vimeo's authentication internally using its own extractor (macOS API JSON endpoint), bypassing the Cloudflare-protected player.

### oEmbed API: useful for metadata

The public oEmbed endpoint (`vimeo.com/api/oembed.json?url=...`) returns video metadata (title, author, duration) without authentication. Useful for discovery/listing but does not expose text tracks.

### Channel listing: slow but possible

`yt-dlp --flat-playlist` can enumerate the SPC-TV channel, but it's slow (pagination). For the pipeline, it may be better to poll the oEmbed API against known/expected Vimeo IDs or scrape the channel page for new video IDs, then use yt-dlp for the actual VTT download.

### Recommendation

Use **yt-dlp** as the Vimeo connector in EPIC-001. It's a stable, maintained tool with a dedicated Vimeo extractor. No API token needed. The connector script is essentially a wrapper around the yt-dlp command with the right flags and output path conventions.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Planned | 2026-03-10 | _pending_ | Initial creation |
| Active | 2026-03-10 | _pending_ | Reframed from API to Playwright; beginning investigation |
| Complete | 2026-03-10 | _pending_ | Playwright blocked by Cloudflare; yt-dlp works perfectly |

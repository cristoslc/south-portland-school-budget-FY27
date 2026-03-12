---
title: "Upcoming-Event Brief Generator"
artifact: SPEC-022
status: Draft
author: cristos
created: 2026-03-12
last-updated: 2026-03-12
parent-epic: EPIC-011
linked-research: []
linked-adrs: []
depends-on:
  - SPEC-020
addresses: []
evidence-pool: ""
swain-do: required
---

# Upcoming-Event Brief Generator

## Problem Statement

Before each upcoming meeting, stakeholders need a forward-looking brief that synthesizes their cumulative understanding, new inter-meeting evidence, and the upcoming agenda into actionable preparation. The existing briefings in `dist/briefings/` are monolithic and static — they don't evolve with each meeting or prepare stakeholders for specific upcoming events. This spec produces the pipeline's most time-sensitive and directly actionable output.

## External Behavior

- **Input:** Cumulative interpretation (SPEC-020 format) + inter-meeting evidence events (SPEC-016 inter-meeting manifest) + upcoming meeting agenda (if available)
- **Output:** 14 brief documents (one per persona), written to `data/interpretation/briefs/<meeting-date>/`
- **Precondition:** Cumulative interpretation is current (reflects all meetings through the most recent)
- **Postcondition:** Briefs reference the upcoming meeting and surface persona-specific concerns
- **Invocation:** `python scripts/generate_briefs.py <upcoming-meeting-date> [--agenda <path>] [--persona PERSONA-NNN]`

## Acceptance Criteria

1. Given a cumulative interpretation and upcoming meeting agenda, when the generator runs, then it produces 14 briefs in `data/interpretation/briefs/<meeting-date>/`
2. Given a brief, when read, then it contains four sections: `since_last_meeting` (new evidence summary), `open_questions` (carried from cumulative), `agenda_implications` (per-persona reading of agenda items), and `watch_for` (specific things to listen for or ask about)
3. Given a brief for a persona with a superseded position in their cumulative, when the brief is generated, then it flags the shift and what to watch for at the upcoming meeting related to that shift
4. Given no available agenda for the upcoming meeting, when the generator runs, then it produces briefs based on cumulative state and inter-meeting evidence, with `agenda_implications` section noting "agenda not yet available"
5. Given a brief, when compared to the corresponding persona's cumulative interpretation, then it adds forward-looking value (questions, predictions, specific listening guidance) not present in the cumulative

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|

## Scope & Constraints

- Briefs are raw material in the data layer, not publication-ready — formatting for stakeholders is a downstream concern
- The generator reads cumulative state; it does not modify it
- Briefs have a real-world deadline: they must exist before the meeting they prepare for
- If the agenda is unavailable, the brief is still generated — it's less specific but still valuable
- Output directory uses the upcoming meeting date, not the generation date

## Implementation Approach

1. **Brief prompt template** — cumulative interpretation + inter-meeting evidence + agenda → forward-looking brief with four sections
2. **Agenda loader** — optional; reads agenda from bundle or provided path; graceful fallback if unavailable
3. **Inter-meeting evidence loader** — reads SPEC-016 inter-meeting manifest for events since the last folded meeting
4. **Generator script** — iterates over 14 personas, calls LLM, writes briefs to data layer
5. **Test with next upcoming meeting** — generate briefs for March 16 Open Conversation using cumulative state from meetings through March 9

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Draft | 2026-03-12 | 7207791 | Initial creation |

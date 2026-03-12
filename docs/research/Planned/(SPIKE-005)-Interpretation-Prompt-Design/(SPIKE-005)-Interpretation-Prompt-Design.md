---
title: "Interpretation Prompt Design"
artifact: SPIKE-005
status: Planned
author: cristos
created: 2026-03-12
last-updated: 2026-03-12
question: "What prompt structure produces consistently distinct, persona-specific interpretations across 14 diverse personas — avoiding generic analysis while maintaining factual grounding in evidence?"
gate: Pre-MVP
risks-addressed:
  - Generic or interchangeable outputs across personas
  - Hallucinated facts not grounded in meeting evidence
  - Prompt token budget exceeding context limits with persona definitions + full meeting transcript
depends-on: []
evidence-pool: ""
---

# Interpretation Prompt Design

## Question

What prompt structure produces consistently distinct, persona-specific interpretations across 14 diverse personas — avoiding generic analysis while maintaining factual grounding in evidence?

## Go / No-Go Criteria

- Interpretations for 3+ personas on the same meeting must demonstrate measurably distinct perspectives (different facts highlighted, different emotional valences, different questions raised)
- At least 80% of structured points reference specific evidence from the meeting bundle (timestamps, quotes, or document sections)
- Journey maps reflect the meeting's narrative arc (sequential beats), not just a list of topics discussed
- Unstructured reactions read as authentically voice-matched to the persona profile (a parent doesn't sound like a journalist; a student doesn't sound like a board insider)
- Total prompt fits within a single context window (meeting bundle + persona definition + output instructions)

## Pivot Recommendation

If single-pass prompting cannot produce distinct interpretations, pivot to a two-stage approach: first extract a persona-agnostic fact base from the meeting (key events, decisions, numbers, quotes), then run persona-specific interpretation as a second pass against the fact base. This trades latency for consistency and reduces the risk of different personas "seeing" different facts.

## Findings

_Populated during Active phase._

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Planned | 2026-03-12 | 7207791 | Initial creation |

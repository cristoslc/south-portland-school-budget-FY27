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

### Recommendation: Single-Pass Prompt (GO)

The single-pass approach passes all five go/no-go criteria. The two-stage fallback (extract facts then interpret) is not needed. Single-pass is recommended for production.

### Winning Prompt Structure

The effective prompt template uses four key design decisions:

1. **Persona-first ordering.** The persona definition is placed BEFORE the meeting content in the prompt. This primes the model to filter evidence through the persona's lens from the first sentence of transcript it encounters, rather than forming a neutral analysis that the persona merely decorates. This is the single most important factor in producing distinct outputs.

2. **Explicit selective attention.** The prompt asks the model to consider what the persona would SKIP or find irrelevant, not just what they'd highlight. This instruction ("Before generating output, mentally answer: What parts would they tune out, skim, or find irrelevant?") produces genuinely different fact selection across personas. In testing, 15 of 20 total structured points were unique to a single persona.

3. **Reaction audience mapping.** Each persona has a defined audience for the free-form reactions section (e.g., Maria tells "your partner, after the kids are in bed"; Tom tells "your neighbor, over the fence"; Jaylen tells "your friend at lunch"). This naturally produces voice differentiation without requiring explicit style instructions -- the audience determines register, vocabulary, and emotional openness.

4. **Mandatory source references.** Every structured point requires a timestamp or document reference. This was expected to feel mechanical, but in practice the citations integrate naturally and prevent hallucination. 100% of points across all three test personas were evidence-grounded.

### Three-Layer Output Schema

The prompt produces three complementary layers:

- **Structured points** (5-8 per interpretation): Each contains `fact`, `source_reference`, `emotional_valence` (8 possible values), `threat_level` (4 levels), and `open_question` (in persona voice). This layer is machine-parseable and supports aggregation across personas.

- **Journey map** (4-6 beats): Chronological emotional arc through the meeting, with `timestamp_range`, `beat_label`, `emotional_state`, `trigger`, and `internal_monologue`. This layer captures the temporal experience, not just topics.

- **Reactions** (2-3 paragraphs): Free-form persona-voice text, written as if recounting the meeting to a specific person in the persona's life. This layer captures voice, tone, and what the persona would lead with.

### Token Budget

Tested against the March 2, 2026 Budget Workshop I (3.5-hour meeting):

| Component | Tokens |
|-----------|--------|
| Prompt template + instructions | ~1,200 |
| Persona definition | ~500-700 |
| Fiscal context summary | ~300 |
| Meeting transcript (source digest) | ~15,000-20,000 |
| Supporting document extracts | ~2,000-3,000 |
| **Total input** | **~19,000-25,000** |
| **Output** | **~2,000-3,500** |
| **Round-trip total** | **~21,000-28,500** |

This fits comfortably in a 32K+ context window. For longer meetings, the source digest format (timestamped paragraphs, not raw VTT) keeps token count manageable.

### Quality Assessment

| Criterion | Result | Evidence |
|-----------|--------|----------|
| Distinct perspectives | PASS | 15/20 structured points unique to one persona; different emotional valence distributions; zero question overlap |
| Evidence grounding | PASS | 20/20 points cite specific timestamps or documents (100%) |
| Narrative journey maps | PASS | Three distinct emotional arcs following meeting chronology; no two personas peak at the same moment |
| Voice-matched reactions | PASS | Maria: parental, emotional, action-oriented. Tom: fiscal, sardonic, numbers-first. Jaylen: casual teen register, program-focused, slightly detached from adult concerns |
| Context window fit | PASS | ~25K tokens per call; 14 independent calls, not cumulative |

### Risks for Production Scale

1. **Younger personas** (PERSONA-013, PERSONA-014) have less behavioral specificity in their definitions. The prompt's effectiveness may degrade for personas with thinner profiles. Recommended: test all 14 before full pipeline commit.

2. **Negative valence bias.** All three test samples skew anxious/frustrated/alarmed, which is appropriate for the March 2 meeting (genuinely concerning content) but should be monitored across meetings with positive developments. The "reassured" valence was unused in all three samples.

3. **Transcript quality dependency.** The prompt should use cleaned source digests from the evidence pool, not raw auto-generated VTT captions. Proper noun errors in raw transcripts would propagate into interpretations.

4. **Meetings exceeding ~30K tokens** in digest form may require pre-summarization or section selection to stay within budget. This is a future concern, not a blocker for the current evidence pool.

### Artifacts Produced

- `test-bundle.md` -- Sources and personas selected for testing
- `prompt-template-v1.md` -- The complete prompt template with variable definitions and per-persona audience mappings
- `sample-maria.md` -- Sample interpretation for PERSONA-001 (Concerned Elementary Parent)
- `sample-tom.md` -- Sample interpretation for PERSONA-006 (Tax-Conscious Resident)
- `sample-student.md` -- Sample interpretation for PERSONA-012 (High School Student)
- `evaluation.md` -- Detailed evaluation against all five go/no-go criteria

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Planned | 2026-03-12 | 7207791 | Initial creation |

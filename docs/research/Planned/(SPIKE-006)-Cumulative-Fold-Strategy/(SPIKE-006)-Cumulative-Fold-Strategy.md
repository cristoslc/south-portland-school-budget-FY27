---
title: "Cumulative Fold Strategy"
artifact: SPIKE-006
status: Planned
author: cristos
created: 2026-03-12
last-updated: 2026-03-12
question: "How should cumulative per-persona narratives be structured and merged so that temporal narrative arcs are preserved without unbounded document growth?"
gate: Pre-MVP
risks-addressed:
  - Unbounded growth of cumulative documents after repeated folds
  - Loss of temporal narrative through repeated summarization
  - Silent supersession of earlier interpretations without audit trail
depends-on: []
evidence-pool: ""
---

# Cumulative Fold Strategy

## Question

How should cumulative per-persona narratives be structured and merged so that temporal narrative arcs are preserved without unbounded document growth?

## Go / No-Go Criteria

- Cumulative document after 5+ meeting folds remains under 4000 words per persona
- Temporal markers (when each persona's understanding shifted) are preserved through fold operations — not averaged or dropped
- Superseded interpretations are explicitly marked with date and replacement, not silently dropped
- Fold output can be diffed against prior version to identify what changed from the most recent meeting
- Fold is deterministic — running the same fold twice on the same input produces identical output

## Pivot Recommendation

If fold-in-place produces unwieldy documents or loses temporal fidelity, pivot to a log-structured approach: keep per-meeting interpretations as immutable records and generate a summary view on demand. This trades query-time computation for storage simplicity and perfect auditability — every interpretation is preserved verbatim. The summary view becomes a read-time concern rather than a write-time merge.

## Findings

### Recommended Approach: Log-Structured

After prototyping both fold-in-place and log-structured approaches, simulating 5 meetings with PERSONA-001 (Maria), and evaluating against all go/no-go criteria, the **log-structured approach** is recommended.

**Pivot recommendation confirmed**: As anticipated in the pivot section above, fold-in-place produces documents that risk exceeding the 4,000-word ceiling at scale, loses temporal fidelity through current_understanding overwrites, and compounds non-determinism across folds. The log-structured approach resolves all three risks.

### Go/No-Go Results

| Criterion | Fold-in-Place | Log-Structured |
|-----------|---------------|----------------|
| Under 4,000 words at 5+ folds | Marginal pass (fail projected at 14) | Pass (summary view ~530 words at 5 folds) |
| Temporal markers preserved | Partial pass (low resolution) | Pass (full granularity, immutable) |
| Supersessions explicit | Pass (paraphrased originals) | Pass (verbatim originals preserved) |
| Diffable | Partial pass (prose sections noisy) | Pass (record-vs-record diffing) |
| Deterministic | Fail (compounds across folds) | Fail (contained — does not compound) |

### Format Specification

**Storage**: One immutable interpretation record per persona per meeting, stored at `interpretations/{PERSONA-ID}/{meeting-date}.md`. Each record contains:
- YAML frontmatter: persona_id, meeting_date, meeting_type, prior_meeting reference
- `interpretation` section: What this meeting means to the persona (~200-400 words)
- `deltas` table: Structured list of changes (category: new_information | position_shift | supersession | thread_opened | thread_resolved)
- `emotional_register`: Brief emotional state note (1-2 sentences)

**Presentation**: A generated summary view produced on demand by processing all records in chronological order. Contains:
- `Current Understanding`: Regenerated synthesis (~150-300 words)
- `Timeline of Understanding Shifts`: One entry per meeting (derived from records)
- `Active Supersessions`: Table with from/to/when (derived from delta entries)
- `Open Threads` / `Resolved Threads`: Netted from thread_opened and thread_resolved deltas

### Growth Projections

| Meetings | Record Store (total) | Summary View | Per-Record Size |
|----------|---------------------|--------------|-----------------|
| 5 | ~2,000 words | ~530 words | 300-500 words |
| 10 | ~4,000 words | ~700 words | 300-500 words |
| 14 | ~5,500-7,000 words | ~700-900 words | 300-500 words |

The summary view remains well under 4,000 words at any meeting count because it is regenerated rather than accumulated. The record store grows linearly but is distributed across independent files.

At full scale (14 meetings x 14 personas), the project would contain ~196 interpretation records and 14 summary views. Total storage: ~77,000-98,000 words across all records. This is manageable for a file-based project of this scope.

### Implications for SPEC-020 and SPEC-021

**SPEC-020 (Per-Meeting Interpretation Pipeline)**: The log-structured approach simplifies the interpretation pipeline. Each meeting produces independent, immutable records — one per persona. The pipeline does not need to read or merge prior cumulative state. It needs only the persona definition and the meeting evidence to generate a record. This is a stateless write operation, which is simpler to implement, test, and debug than the stateful merge required by fold-in-place.

The delta table in each record requires the pipeline to be aware of the persona's prior state (to identify supersessions and thread resolutions), but this is a read-only dependency on the existing record store, not a read-modify-write cycle on a cumulative document.

**SPEC-021 (Cumulative Narrative Generation)**: The cumulative narrative becomes a read-time operation rather than a write-time merge. SPEC-021 should define:
1. The algorithm for processing records 1..N into a summary view (sequential scan, delta aggregation)
2. Caching strategy for the summary view (regenerate on demand vs. cache with invalidation on new record)
3. The summary view template (sections, word budget per section, compression rules for the timeline and thread sections at high meeting counts)

The summary view is the consumer-facing artifact. If it is wrong or stale, it can be regenerated without data loss. This architectural property — the summary is derived, not canonical — fundamentally changes the risk profile of the cumulative narrative system.

### Determinism Mitigation

Neither approach achieves strict determinism with LLM-generated prose. To bring the log-structured approach closer:
- Use structured/templated output formats for prose sections
- Pin LLM temperature to 0 for record creation
- Hash inputs (persona definition + meeting evidence) and verify output consistency across runs
- Accept that the summary view is a convenience artifact, not a deterministic output — the record store is the source of truth

### Supporting Artifacts

- `fold-in-place-prototype.md` — Fold-in-place format design and 3-meeting example
- `log-structured-prototype.md` — Log-structured format design, 3-meeting example, and generated summary view
- `simulation.md` — Full 5-meeting simulation of both approaches with metrics
- `evaluation.md` — Detailed criterion-by-criterion evaluation and recommendation

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Planned | 2026-03-12 | 7207791 | Initial creation |

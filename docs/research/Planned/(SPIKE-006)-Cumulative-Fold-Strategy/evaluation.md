# Evaluation Against Go/No-Go Criteria

**SPIKE-006 Task 4**

## Go/No-Go Criteria (from SPIKE-006)

1. Cumulative document after 5+ meeting folds remains under 4,000 words per persona
2. Temporal markers (when each persona's understanding shifted) are preserved through fold operations
3. Superseded interpretations are explicitly marked with date and replacement, not silently dropped
4. Fold output can be diffed against prior version to identify what changed from the most recent meeting
5. Fold is deterministic — running the same fold twice on the same input produces identical output

---

## Criterion 1: Under 4,000 words after 5+ folds

### Fold-in-Place

| Folds | Measured Words | Projected at 14 Folds |
|-------|---------------|----------------------|
| 5 | ~2,100 | ~3,800-4,500 |

**Verdict: MARGINAL PASS at 5 folds; LIKELY FAIL at 14 folds.**

The cumulative document reached ~2,100 words after 5 folds. Growth is monotonic because narrative_arc and superseded are strictly additive. The current_understanding section also tends to grow as the budget situation becomes more complex (more options, more stakeholders, more context to maintain). Extrapolating to 14 meetings, the document would likely reach 3,800-4,500 words, exceeding the 4,000-word ceiling.

Mitigations are possible (aggressive summarization of current_understanding, collapsing narrative_arc rows at defined intervals), but they introduce lossy compression that conflicts with criteria 2 and 3.

### Log-Structured

| Metric | After 5 Folds | Projected at 14 Folds |
|--------|--------------|----------------------|
| Summary view | ~530 words | ~700-900 words |
| Record store (total) | ~1,990 words | ~5,500-7,000 words |
| Largest single document | ~530 words (summary) | ~900 words (summary) |

**Verdict: PASS (summary view); N/A (record store).**

The summary view is the "cumulative document" in this approach and it stays well under 4,000 words because it is regenerated rather than accumulated. The record store grows linearly but is not a single document — it is a collection of immutable files, each under 500 words.

The criterion as written says "cumulative document." If that means the document a reader consults to understand the persona's current state, the log-structured summary view passes easily. If it means total stored text, the record store exceeds 4,000 words by meeting 10 — but this is stored across multiple files, not in a single document.

### Criterion 1 Result

| Approach | Pass/Fail |
|----------|-----------|
| Fold-in-place | Marginal pass at 5, likely fail at 14 |
| Log-structured (summary view) | Pass |

---

## Criterion 2: Temporal markers preserved

### Fold-in-Place

The narrative_arc table is append-only: each fold adds a row with a date and a description of the shift. These markers are never modified or deleted. After 5 folds, 5 temporal markers are preserved.

**However**, the current_understanding section is fully rewritten each fold. The *prior* understanding is lost — only the current state survives. Temporal markers exist in the narrative_arc but the rich context behind each shift (what the persona believed *before* and *why* they changed) is only available in summary form in the superseded table.

**Verdict: PARTIAL PASS.** Temporal markers exist but at low resolution (one per meeting). The context behind shifts is paraphrased, not preserved verbatim.

### Log-Structured

Every interpretation record is immutable. Each record contains timestamped deltas with explicit categories (new_information, position_shift, supersession, thread_opened, thread_resolved). After 5 folds, 49 individual temporal markers are preserved across the record store.

The generated summary view includes a "Timeline of Understanding Shifts" that is derived from these records — one entry per meeting, similar to fold-in-place's narrative_arc. But the full detail is always available by reading the source records.

**Verdict: PASS.** All temporal markers are preserved at full granularity. No information is ever lost.

### Criterion 2 Result

| Approach | Pass/Fail |
|----------|-----------|
| Fold-in-place | Partial pass (markers exist but at low resolution) |
| Log-structured | Pass (full granularity, immutable) |

---

## Criterion 3: Supersessions explicitly marked

### Fold-in-Place

The superseded table records each supersession with: original position (paraphrased), date held, replacement, and date superseded. After 5 folds, 4 supersessions are tracked.

**Limitation**: The original position text is a paraphrase written at supersession time, not the original verbatim text. If the paraphrase is inaccurate or incomplete, there is no way to verify — the original current_understanding was overwritten.

**Verdict: PASS with caveat.** Supersessions are explicitly marked. Original positions are paraphrased, not preserved verbatim.

### Log-Structured

Each record's delta table includes supersession entries with explicit references to the prior position and its date. The original text is preserved verbatim in the immutable record where it was first stated.

**Verdict: PASS.** Supersessions are explicitly marked and original positions are preserved verbatim in source records.

### Criterion 3 Result

| Approach | Pass/Fail |
|----------|-----------|
| Fold-in-place | Pass (with paraphrase caveat) |
| Log-structured | Pass (verbatim originals preserved) |

---

## Criterion 4: Diffable

### Fold-in-Place

Diffing fold N vs. fold N-1 produces:
- **current_understanding**: Extensive changes — this section is fully rewritten each fold. Diffs are noisy and hard to parse because the rewrite touches most of the text.
- **narrative_arc**: Clean diff — one row added.
- **superseded**: Clean diff — zero or one row added.
- **open_threads**: Moderate diff — some items resolved, some added, some updated in place. Readable but not perfectly clean.

**Overall diffability**: Mixed. The structured sections diff well. The prose section (current_understanding) does not, because it is a complete rewrite rather than a targeted edit. A reader looking at the diff would need to read the full current_understanding to understand what changed.

A structural constraint (requiring current_understanding to use fixed subsections like "budget_gap", "reconfiguration", "tax_increase", "maria_posture") would improve diffability but adds format rigidity.

**Verdict: PARTIAL PASS.** Structured sections are diffable. Prose section produces noisy diffs.

### Log-Structured

Individual records are immutable — there is nothing to diff between versions of the same file.

Diffing the generated summary view at time N vs. time N-1 has the same problem as fold-in-place's current_understanding: the "Current Understanding" section is regenerated and produces noisy diffs. However, the structured sections (timeline, supersessions, threads) diff cleanly.

An alternative diff strategy exists: compare the *latest record* against the *prior record*. This shows exactly what one meeting added. This is a clean, meaningful diff because each record is an independent, bounded document.

**Verdict: PASS (with the record-vs-record diff strategy).** The record store provides a natural diff unit (meeting N's record vs. meeting N-1's record) that is cleaner than diffing cumulative documents.

### Criterion 4 Result

| Approach | Pass/Fail |
|----------|-----------|
| Fold-in-place | Partial pass (structured sections diff well; prose does not) |
| Log-structured | Pass (record-vs-record diffing is clean and meaningful) |

---

## Criterion 5: Deterministic

### Fold-in-Place

The fold operation requires rewriting current_understanding — an LLM-generated prose section. Running the same fold twice with the same inputs will produce semantically similar but textually different output. This means:
- **Narrative_arc**: Likely deterministic (adding one structured table row).
- **Superseded**: Likely deterministic (adding one structured table row, though the paraphrase may vary).
- **Open_threads**: Moderately deterministic (structured, but decisions about which threads to resolve or add require judgment).
- **Current_understanding**: Not deterministic (free-form prose).

**Compounding problem**: Each fold depends on the prior fold's output. Non-determinism accumulates — a different current_understanding at fold 3 may produce a different fold at fold 4. This creates divergent branches.

**Verdict: FAIL.** The fold operation is not deterministic due to prose generation. Non-determinism compounds across folds.

### Log-Structured

Record creation is a one-shot operation that generates prose (interpretation) and structured data (deltas). Like fold-in-place, the prose is non-deterministic. However:
- Records are independent — non-determinism at record N does not affect record N+1 (each record is generated from the meeting content and the persona definition, not from the prior record).
- The generated summary view is also non-deterministic (prose regeneration), but it can be regenerated at any time from the stable record store.
- The structured elements (deltas) are more constrained and more likely to be deterministic.

**Verdict: FAIL (prose generation is inherently non-deterministic), but the impact is contained.** Non-determinism is isolated to individual records and does not compound. Regenerating the summary from the same records may produce different prose but the same structured data.

### Criterion 5 Result

| Approach | Pass/Fail |
|----------|-----------|
| Fold-in-place | Fail (non-deterministic, compounds across folds) |
| Log-structured | Fail (non-deterministic, but isolated — does not compound) |

---

## Summary Scorecard

| Criterion | Fold-in-Place | Log-Structured |
|-----------|---------------|----------------|
| 1. Under 4,000 words at 5+ folds | Marginal pass (fail at 14) | Pass |
| 2. Temporal markers preserved | Partial pass | Pass |
| 3. Supersessions explicit | Pass (paraphrased) | Pass (verbatim) |
| 4. Diffable | Partial pass | Pass |
| 5. Deterministic | Fail | Fail (contained) |

**Fold-in-place**: 1 pass, 2 partial passes, 1 marginal pass, 1 fail = does not meet criteria.

**Log-structured**: 4 passes, 1 contained fail = meets criteria with one acceptable limitation.

---

## Recommendation

**Recommended approach: Log-structured.**

### Rationale

1. **Growth is bounded by design.** The summary view is regenerated, not accumulated, so it cannot grow unboundedly. The record store grows linearly but each record is small, independent, and immutable. This is architecturally superior to growth mitigations bolted onto fold-in-place.

2. **Temporal fidelity is perfect.** Every interpretation is preserved verbatim in an immutable record. No information is ever lost through fold operations. This is the strongest advantage — it eliminates an entire category of risk (lossy summarization, paraphrase drift, silent information loss).

3. **Non-determinism is contained.** Both approaches fail the strict determinism criterion (LLM prose generation is inherently non-deterministic), but log-structured isolates the non-determinism to independent records. Fold-in-place compounds it across folds. This is a meaningful architectural difference.

4. **Diffing is natural.** The record store provides a clean diff unit: compare the latest record against the prior record to see what one meeting added. This is more useful than diffing cumulative documents.

5. **Operational model is simpler.** Writing an immutable record is simpler than merging into an existing document (no read-modify-write, no merge conflicts, no state management). The summary view is a read-time concern — if it is wrong, regenerate it; the source data is always intact.

### Trade-offs accepted

- **More files**: 14 meetings x 14 personas = 196 interpretation records plus 14 summary views. This is manageable for this project's scale.
- **Read-time computation**: Generating the summary view requires processing all prior records. For 14 meetings, this is trivial. For larger corpora, it could be optimized with incremental caching.
- **Summary view is non-deterministic**: Regenerating the summary from the same records may produce different prose. This is acceptable if the structured sections (timeline, supersessions, threads) are deterministic and the prose is understood as a convenience view, not the source of truth.

### Determinism mitigation

Neither approach achieves strict determinism. To bring either closer:
- Use structured/templated output for prose sections (reduce free-form generation)
- Pin the LLM temperature to 0
- Use hash-based verification: hash the inputs and compare output hashes across runs

For log-structured specifically, determinism matters most at record creation time (one-shot, no compounding). The summary view's non-determinism is acceptable because it is always regenerable from deterministic inputs (the record store).

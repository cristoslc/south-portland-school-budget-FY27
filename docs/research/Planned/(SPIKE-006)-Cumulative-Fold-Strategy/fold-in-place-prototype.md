# Fold-in-Place Format Prototype

**SPIKE-006 Task 1** | Persona: PERSONA-001 (Maria, Concerned Elementary Parent)

## Format Specification

The fold-in-place approach maintains a single cumulative document per persona. Each fold operation merges a new meeting interpretation into the existing document, updating sections in place. The document has four sections:

1. **current_understanding** — The persona's present-state beliefs, concerns, and positions as of the most recent fold. Written in present tense.
2. **narrative_arc** — A chronological timeline of key shifts in the persona's understanding. Each entry is timestamped and immutable once written; new folds append entries but never modify prior ones.
3. **superseded** — Explicitly records when a prior belief or position was replaced, with the date of the original position, the date of supersession, and what replaced it.
4. **open_threads** — Unresolved questions or pending decisions from the persona's perspective. Items are added as they arise and removed (moved to superseded or resolved in current_understanding) when answered.

### YAML Frontmatter Schema

```yaml
persona_id: PERSONA-001
persona_name: "Maria (Concerned Elementary Parent)"
last_folded_meeting: "2026-02-09"    # ISO date of most recent meeting folded
fold_count: 3                         # Number of meetings folded into this document
meetings_folded:                      # Ordered list of all meetings incorporated
  - "2026-01-12"
  - "2026-02-04"
  - "2026-02-09"
fold_version: 1                       # Format version for schema evolution
```

---

## After Meeting 1: January 12, 2026 (Regular Meeting)

```yaml
---
persona_id: PERSONA-001
persona_name: "Maria (Concerned Elementary Parent)"
last_folded_meeting: "2026-01-12"
fold_count: 1
meetings_folded:
  - "2026-01-12"
fold_version: 1
---
```

### current_understanding

Maria is aware that the school board has signaled "another difficult budget year" but has not yet been presented with specific numbers or proposals. The board chair announced an aggressive calendar of forums and workshops, which Maria sees as both a positive sign of transparency and a warning that significant changes may be coming. She is watching for details but currently has no concrete threat to respond to.

Her children's elementary experience remains unaffected so far. The meeting focused primarily on non-budget items (student reports, athletics, community belonging initiatives). The superintendent search running in parallel adds uncertainty — leadership transitions make her uneasy about who will advocate for elementary programs.

Maria's immediate posture: alert but not alarmed. She is marking the upcoming budget forums on her calendar and preparing to attend.

### narrative_arc

| Date | Shift |
|------|-------|
| 2026-01-12 | **Initial awareness.** Board signals difficult budget year ahead. No specifics yet. Maria enters monitoring mode. |

### superseded

_None. First fold — no prior positions to supersede._

### open_threads

- What is the actual size of the budget gap?
- Will elementary programs be targeted for cuts?
- How will the superintendent search affect budget priorities?
- What is the timeline for budget decisions?

---

## After Meeting 2: February 4, 2026 (Budget Forum) — Fold applied

```yaml
---
persona_id: PERSONA-001
persona_name: "Maria (Concerned Elementary Parent)"
last_folded_meeting: "2026-02-04"
fold_count: 2
meetings_folded:
  - "2026-01-12"
  - "2026-02-04"
fold_version: 1
---
```

### current_understanding

Maria now has the full picture of the budget crisis and it is worse than she feared. The district faces a **$7.2 million structural gap** — if nothing changes, the school portion of property taxes would increase 18.95%. The board has set a 6% ceiling, requiring massive cuts.

The three "big ideas" presented by Dr. Johanna Prince define her concern landscape:

1. **Elementary reconfiguration** ($1.5-2.2M savings) — reorganizing five K-4 neighborhood schools into grade-band campuses (pre-K-1 and 2-4). This directly threatens the school experience Maria values: her child's neighborhood school, familiar teachers, walkable commutes. This is now her primary worry.
2. **Grades 5-12 staffing efficiencies** ($1M) — increased class sizes at middle and high school. Less immediately relevant to her but concerning as a precedent.
3. **Operational efficiencies** ($1M) — shift changes, vendor contracts. Feels like the least objectionable category.

Even all three together leave a **$3M+ residual gap**. Maria understands this means additional cuts beyond the big ideas are inevitable.

She is particularly alarmed that the fund balance is depleted — there is no financial cushion. The root causes (declining enrollment to ~2,736 students, staffing-enrollment divergence, 12% health insurance increase) make the problem feel structural rather than temporary.

Maria's posture has shifted from monitoring to active concern. She is preparing specific questions for the next meeting and sharing information in parent group chats. She is cross-referencing the reconfiguration proposal against what she knows about her child's school.

### narrative_arc

| Date | Shift |
|------|-------|
| 2026-01-12 | **Initial awareness.** Board signals difficult budget year ahead. No specifics yet. Maria enters monitoring mode. |
| 2026-02-04 | **Alarm.** $7.2M gap revealed. Elementary reconfiguration proposed as largest savings lever. Maria shifts from monitoring to active concern. Begins sharing information with parent networks. |

### superseded

| Original Position | Date Held | Superseded By | Date Superseded |
|-------------------|-----------|---------------|-----------------|
| "Difficult year but no specifics yet — stay alert" | 2026-01-12 | Budget gap quantified at $7.2M; elementary reconfiguration is the primary savings mechanism | 2026-02-04 |

### open_threads

- ~~What is the actual size of the budget gap?~~ **Resolved 2026-02-04**: $7.2M structural gap.
- Will elementary programs be targeted for cuts? **Partially answered 2026-02-04**: Elementary reconfiguration is the single largest proposed savings lever ($1.5-2.2M). Specific school impacts not yet detailed.
- ~~How will the superintendent search affect budget priorities?~~ Remains open but deprioritized — the budget crisis dominates.
- ~~What is the timeline for budget decisions?~~ **Resolved 2026-02-04**: Board requested reconfiguration proposal for March 2 workshop. Decisions expected March-April for September 2026 implementation.
- **NEW**: Which specific schools would be reconfigured? Would her child's school become a grade-band campus or close?
- **NEW**: What are the transportation implications — would her child need to be bused to a different building?
- **NEW**: Has anyone studied the educational impact of grade-band vs. neighborhood schools?
- **NEW**: Are there revenue alternatives being pursued (state aid, grants, education foundation)?

---

## After Meeting 3: February 9, 2026 (Regular Meeting) — Fold applied

```yaml
---
persona_id: PERSONA-001
persona_name: "Maria (Concerned Elementary Parent)"
last_folded_meeting: "2026-02-09"
fold_count: 3
meetings_folded:
  - "2026-01-12"
  - "2026-02-04"
  - "2026-02-09"
fold_version: 1
---
```

### current_understanding

Maria's understanding has deepened and her emotional engagement has intensified. The budget crisis is now intertwined with broader community fears: ICE enforcement activity has caused children to miss school, and the teachers' union has made emotional public statements about staff impact. The human cost of the budget situation is becoming concrete.

Key updates to her understanding:

**On the budget ceiling**: Board member Feller publicly broke from the 6% tax increase ceiling, saying a higher increase may be necessary to avoid "draconian" cuts. Maria finds this both alarming (the 6% ceiling was already painful) and somewhat validating — it suggests the board recognizes that deep cuts to elementary programs may be unacceptable. She is recalibrating her expectations: the tax increase may land between 6% and the city council's guidance range of 3-6% (with most councilors gravitating toward 5-6%).

**On reconfiguration**: The board unanimously requested a formal reconfiguration proposal for the March 2 workshop. This confirms that reconfiguration is the leading cost-reduction strategy, not just one option among many. Maria is preparing to attend the March 2 workshop, which she now views as the pivotal meeting.

**On community voice**: The teachers' union president asked for meaningful engagement beyond surveys and urged a specific tax target from the city council. Multiple parents echoed concerns about being consulted too late. Maria shares this frustration — she wants evidence that parent input shapes outcomes, not just validates predetermined decisions.

**On immigration intersection**: The board unanimously endorsed the city council's immigration resolution. While not directly a budget issue, the ICE enforcement situation has created a community crisis that competes for emotional bandwidth and adds urgency to equity considerations in any school reconfiguration (particularly regarding Skillin school's role serving immigrant families).

Maria's posture: actively preparing for the March 2 workshop. She is formulating specific questions, coordinating with other parents, and paying close attention to which schools are likely to be affected by reconfiguration.

### narrative_arc

| Date | Shift |
|------|-------|
| 2026-01-12 | **Initial awareness.** Board signals difficult budget year ahead. No specifics yet. Maria enters monitoring mode. |
| 2026-02-04 | **Alarm.** $7.2M gap revealed. Elementary reconfiguration proposed as largest savings lever. Maria shifts from monitoring to active concern. Begins sharing information with parent networks. |
| 2026-02-09 | **Deepening engagement.** 6% ceiling may not hold (Feller break). Reconfiguration confirmed as leading strategy (unanimous request for formal proposal). Community anxiety compounds — ICE enforcement, union concerns. Maria shifts to active preparation for March 2 workshop. |

### superseded

| Original Position | Date Held | Superseded By | Date Superseded |
|-------------------|-----------|---------------|-----------------|
| "Difficult year but no specifics yet — stay alert" | 2026-01-12 | Budget gap quantified at $7.2M; elementary reconfiguration is the primary savings mechanism | 2026-02-04 |
| "6% tax ceiling is the operating constraint" | 2026-02-04 | Feller publicly broke from 6% ceiling; actual increase may be higher. Council guidance (Feb 10) clusters at 5-6% | 2026-02-09 |

### open_threads

- Will elementary programs be targeted for cuts? **Progressing**: Elementary reconfiguration confirmed as leading strategy; formal proposal due March 2. Specific school impacts still unknown.
- **NEW**: Which of the nine reconfiguration options will be presented March 2? Which schools become primary (pre-K-1) vs. intermediate (2-4)?
- What are the transportation implications for grade-band campuses?
- Has anyone studied the educational impact of grade-band vs. neighborhood schools?
- Are there revenue alternatives being pursued? **Updated 2026-02-09**: Union urged specific tax target from council; early retirement buyouts being explored but "pretty limited."
- **NEW**: Will the March 2 workshop include meaningful time for parent input, or will it be presentation-only?
- **NEW**: How does the Skillin school equity argument (Chair DeAngelis) affect which schools are candidates for reconfiguration or closure?
- **NEW**: What happens to RIF'd staff? Notification timeline?

---

## Format Observations

**Growth pattern**: After 3 folds, this document is approximately 1,400 words. The `current_understanding` section was fully rewritten each fold (net-new text, not appended). The `narrative_arc` grew by one row per fold. The `superseded` section grew by one row (not every fold produces a supersession). The `open_threads` section fluctuated — some resolved, some added, some updated in place.

**Projected growth**: At this rate, 5 folds would produce ~1,800-2,000 words. 10 folds would produce ~2,800-3,200 words. 14 folds (full meeting series) would produce ~3,500-4,200 words — near the 4,000-word ceiling. The main growth driver is `narrative_arc` (strictly additive) and `open_threads` (net growth if threads accumulate faster than they resolve).

**Temporal marker preservation**: The `narrative_arc` table is append-only and preserves all temporal markers. The `superseded` table provides explicit before/after with dates. The `current_understanding` section loses the temporal dimension on each rewrite — it reflects only the present state.

**Diffability**: The `current_understanding` section changes substantially each fold, making diffs noisy. The other three sections are structured (table rows), making diffs clean and meaningful. A hybrid approach might work: keep `current_understanding` stable in structure (same subsections each time) to improve diff readability.

**Determinism risk**: The `current_understanding` rewrite is the non-deterministic element — LLM-generated prose will vary across runs. The other sections are more constrained (table row additions) and more likely to be deterministic if the input interpretation is identical.

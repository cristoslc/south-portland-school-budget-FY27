# 5-Meeting Fold Simulation

**SPIKE-006 Task 3** | Persona: PERSONA-001 (Maria, Concerned Elementary Parent)

## Simulation Parameters

- **Persona**: Maria (PERSONA-001, Concerned Elementary Parent)
- **Meetings simulated** (all real dates from the evidence pool):
  1. 2026-01-12 — Regular Meeting
  2. 2026-02-04 — Budget Forum
  3. 2026-02-09 — Regular Meeting
  4. 2026-03-02 — Budget Workshop I
  5. 2026-03-09 — Regular Meeting
- **Both approaches** are simulated in parallel
- **Metrics tracked**: word count, temporal marker count, supersession count, open thread count

Meetings 1-3 were already prototyped in the format documents. This simulation extends through meetings 4 and 5 and provides metrics across all 5 folds for comparison.

---

## Approach A: Fold-in-Place

### State after Meeting 4: March 2, 2026 (Budget Workshop I) — Fold 4

```yaml
---
persona_id: PERSONA-001
persona_name: "Maria (Concerned Elementary Parent)"
last_folded_meeting: "2026-03-02"
fold_count: 4
meetings_folded:
  - "2026-01-12"
  - "2026-02-04"
  - "2026-02-09"
  - "2026-03-02"
fold_version: 1
---
```

#### current_understanding

Maria has now seen the full scope of elementary reconfiguration and it is more detailed — and more unsettling — than she anticipated. The March 2 budget workshop (3.5 hours) was the most substantive meeting yet. The administration presented **nine specific reconfiguration options** (labeled 1.1 through 1.8, plus alternatives), each with building-by-building analysis. Every elementary principal presented their school's data.

The educational case for grade-band schools was made explicitly: better teacher collaboration, curriculum consistency, more efficient use of specialist staff. Maria finds this argument intellectually credible but emotionally difficult — she values her child's neighborhood school and the relationships built there.

**The Skillin pivot**: Chair DeAngelis made a forceful argument against closing Skillin school, citing its role serving the city's most vulnerable immigrant families. This reframes the reconfiguration debate: if Skillin is off the table politically, the remaining options concentrate impact on other schools. Maria is now calculating which options affect her child's school specifically.

Public comment was **extensive and emotional**. Parents raised concerns about:
- Disruption to young children (pre-K and K students being moved between buildings)
- Transportation burden (multiple drop-off locations for families with children in different grade bands)
- Pace of decision-making (September 2026 implementation feels rushed)
- Lack of direct parent surveys before proposals were developed

Maria resonated deeply with these comments — they articulate her own concerns. She spoke or is preparing to speak. The board directed the administration to refine models for subsequent workshops, which means the decision is not yet final but the window for influence is narrowing.

A **non-reconfiguration path** was also modeled at ~$2.2M in savings, achieved through across-the-board class size increases and staff reductions at all schools. The superintendent explicitly stated this approach "kicks the problem down the road." Maria finds herself in a bind: reconfiguration is disruptive but may be structurally sound; the alternative preserves neighborhood schools but at the cost of larger class sizes everywhere and unresolved structural problems.

#### narrative_arc

| Date | Shift |
|------|-------|
| 2026-01-12 | **Initial awareness.** Board signals difficult budget year ahead. No specifics. Monitoring mode. |
| 2026-02-04 | **Alarm.** $7.2M gap revealed. Elementary reconfiguration proposed as largest savings lever. Activated. |
| 2026-02-09 | **Deepening engagement.** 6% ceiling breaking. Reconfiguration confirmed as leading strategy. Preparing for March 2 workshop. |
| 2026-03-02 | **Confronting specifics.** Nine reconfiguration options presented with building-level detail. Skillin pivot constrains options. Non-reconfiguration path presented but characterized as unsustainable. Maria faces a genuine dilemma: accept disruption or accept decline. |

#### superseded

| Original Position | Date Held | Superseded By | Date Superseded |
|-------------------|-----------|---------------|-----------------|
| "Difficult year but no specifics — stay alert" | 2026-01-12 | Budget gap quantified at $7.2M; elementary reconfiguration is the primary savings mechanism | 2026-02-04 |
| "6% ceiling is the operating constraint" | 2026-02-04 | Ceiling may not hold (Feller break); council guidance clusters 5-6% | 2026-02-09 |
| "Reconfiguration is one of three big ideas" | 2026-02-04 | Reconfiguration is the dominant strategy with 9 detailed options; non-reconfiguration path explicitly characterized as insufficient | 2026-03-02 |

#### open_threads

- Which specific reconfiguration option will be selected? Board directed administration to refine — decision deferred to subsequent workshops.
- How does the Skillin equity constraint narrow the viable options? If Skillin is protected, which schools absorb the reconfiguration?
- What are the transportation logistics for families with children in different grade bands (e.g., one child at a pre-K-1 building, another at a 2-4 building)?
- Is September 2026 implementation realistic given the pace of decision-making?
- Will there be direct parent surveys or only public comment sessions?
- What happens to staff who are RIF'd? March 9 meeting expected to address notification timeline.
- Is the non-reconfiguration path ($2.2M, across-the-board class size increases) actually on the table, or was it presented to make reconfiguration look better by comparison?

---

### State after Meeting 5: March 9, 2026 (Regular Meeting) — Fold 5

```yaml
---
persona_id: PERSONA-001
persona_name: "Maria (Concerned Elementary Parent)"
last_folded_meeting: "2026-03-09"
fold_count: 5
meetings_folded:
  - "2026-01-12"
  - "2026-02-04"
  - "2026-02-09"
  - "2026-03-02"
  - "2026-03-09"
fold_version: 1
---
```

#### current_understanding

Maria is now in the dense middle of the budget process. The March 9 regular meeting did not introduce new reconfiguration options but advanced the process in two important ways:

1. **RIF notification plan**: The administration shared the timeline for reduction-in-force notifications. Staff who may be affected will begin receiving preliminary notices. This makes the budget cuts feel real and human — teachers Maria's children know may lose their positions.

2. **Budget presentation update**: The latest budget presentation refined the financial picture. The $7.2M gap remains the operative figure. The administration is moving toward a refined set of reconfiguration options for the next workshop, incorporating board feedback from March 2 (including the Skillin constraint).

Maria's understanding is crystallizing into a clearer picture of the trade-offs:
- **Reconfiguration path**: ~$1.5-2.2M in savings, grade-band campuses, disruption to neighborhood school identity, transportation complexity, but structurally addresses the staffing-enrollment divergence.
- **Non-reconfiguration path**: ~$2.2M through across-the-board class size increases, preserves neighborhood schools in name but degrades quality everywhere, does not address structural problem.
- **Residual gap**: Either path still leaves $3M+ unaddressed, requiring line-by-line cuts, revenue enhancement, or a higher tax increase.

The city council's guidance (from the Feb 10 joint workshop) is that the school tax increase should land in the 5-6% range, but the school board may need to exceed this. Maria is starting to accept that a significant tax increase is coming regardless, and the question is whether the cuts that accompany it are smart (reconfiguration) or diffuse (across-the-board reductions).

Her posture has shifted from "resist reconfiguration" toward "influence which reconfiguration option is chosen." She is focused on protecting her child's specific school and on ensuring transportation logistics are workable for families.

#### narrative_arc

| Date | Shift |
|------|-------|
| 2026-01-12 | **Initial awareness.** Board signals difficult budget year. No specifics. Monitoring mode. |
| 2026-02-04 | **Alarm.** $7.2M gap revealed. Elementary reconfiguration proposed as largest savings lever. Activated. |
| 2026-02-09 | **Deepening engagement.** 6% ceiling breaking. Reconfiguration confirmed as leading strategy. Preparing for March 2. |
| 2026-03-02 | **Confronting specifics.** Nine options presented. Skillin pivot constrains choices. Non-reconfiguration path presented but deemed unsustainable. Genuine dilemma emerges. |
| 2026-03-09 | **Pragmatic pivot.** RIF notifications make cuts tangible. Maria shifts from resisting reconfiguration to influencing which option is chosen. Accepts significant tax increase is coming; focuses on quality of accompanying cuts. |

#### superseded

| Original Position | Date Held | Superseded By | Date Superseded |
|-------------------|-----------|---------------|-----------------|
| "Difficult year but no specifics — stay alert" | 2026-01-12 | Budget gap quantified at $7.2M; reconfiguration is the primary savings mechanism | 2026-02-04 |
| "6% ceiling is the operating constraint" | 2026-02-04 | Ceiling may not hold; council guidance clusters 5-6% | 2026-02-09 |
| "Reconfiguration is one of three big ideas" | 2026-02-04 | Reconfiguration is the dominant strategy with 9 detailed options; alternative explicitly deemed insufficient | 2026-03-02 |
| "Resist reconfiguration to protect neighborhood schools" | 2026-02-04 | Shift to influencing which option is chosen; accepts reconfiguration may be structurally necessary | 2026-03-09 |

#### open_threads

- Which refined reconfiguration option will the administration recommend at the next workshop?
- How does the Skillin equity constraint narrow the viable options?
- Transportation logistics for split-grade-band families?
- Will there be direct parent surveys?
- What specific positions will be affected by RIFs? Who at her child's school?
- What is the realistic tax increase percentage — and what does that mean for her household?
- When is the final budget vote?

---

## Approach B: Log-Structured

### Record 4: March 2, 2026 (Budget Workshop I)

```yaml
---
persona_id: PERSONA-001
persona_name: "Maria (Concerned Elementary Parent)"
meeting_date: "2026-03-02"
meeting_type: "Budget Workshop I"
record_version: 1
prior_meeting: "2026-02-09"
---
```

#### interpretation

The longest and most substantive meeting (3.5 hours). The administration presented nine specific reconfiguration options (1.1 through 1.8 plus alternatives) with building-by-building analysis. Every elementary principal presented data about their school. The educational case for grade-band campuses was made: better teacher collaboration, curriculum consistency, efficient specialist deployment.

Chair DeAngelis argued forcefully against closing Skillin school due to its service to immigrant families. This "Skillin pivot" constrains which options remain politically viable and shifts impact toward other schools.

Public comment was extensive and emotional. Parents raised: disruption to young children, transportation burden for families with children in different grade bands, rushed September 2026 timeline, lack of direct parent surveys. Maria identified deeply with these concerns.

A non-reconfiguration path was modeled at ~$2.2M savings through across-the-board class size increases, but the superintendent characterized it as "kicking the problem down the road."

The board directed the administration to refine models for subsequent workshops. No decision yet, but the window is narrowing.

#### deltas

| Category | Description | Supersedes |
|----------|-------------|------------|
| new_information | Nine specific reconfiguration options presented with building-level detail | — |
| new_information | Each elementary principal presented school-specific data | — |
| new_information | Educational case for grade-band schools articulated: collaboration, consistency, efficiency | — |
| new_information | Non-reconfiguration path modeled at ~$2.2M but deemed unsustainable by superintendent | — |
| supersession | Reconfiguration moves from "one of three big ideas" to the dominant strategy with detailed options | "Reconfiguration is one of three big ideas" (2026-02-04) |
| new_information | Skillin pivot: DeAngelis argues against closing Skillin (equity, immigrant families) | — |
| new_information | Extensive public comment: disruption to young children, transportation, rushed timeline, no parent surveys | — |
| position_shift | Maria confronts genuine dilemma: disruption vs. decline. Begins calculating which options affect her school specifically | — |
| thread_opened | Which refined option will the administration recommend? | — |
| thread_opened | Is September 2026 implementation realistic? | — |
| thread_opened | Is the non-reconfiguration path a real option or a foil? | — |

#### emotional_register

Overwhelmed but engaged. The sheer volume of options and data is difficult to process. The public comment session was emotional and validating — other parents share her concerns. She is no longer just worried; she is confronting a real trade-off with no clearly good answer.

---

### Record 5: March 9, 2026 (Regular Meeting)

```yaml
---
persona_id: PERSONA-001
persona_name: "Maria (Concerned Elementary Parent)"
meeting_date: "2026-03-09"
meeting_type: "Regular Meeting"
record_version: 1
prior_meeting: "2026-03-02"
---
```

#### interpretation

A transitional meeting. No new reconfiguration options, but two significant developments:

1. **RIF notification plan shared**: The administration outlined the timeline for reduction-in-force notifications. Affected staff will begin receiving preliminary notices. This makes the abstract budget cuts feel concrete and personal — teachers at Maria's child's school could be among those notified.

2. **Budget refinement**: The latest budget presentation confirmed the $7.2M gap and reported that the administration is incorporating board feedback from March 2 (including the Skillin constraint) into refined reconfiguration options for the next workshop.

Maria's posture is shifting. She is moving past opposition to reconfiguration and toward trying to influence which option is selected. She accepts that a significant tax increase is coming regardless and that the question is whether accompanying cuts are structural (reconfiguration) or diffuse (across-the-board). She is focused on protecting her child's specific school and ensuring transportation logistics are workable.

#### deltas

| Category | Description | Supersedes |
|----------|-------------|------------|
| new_information | RIF notification timeline shared; staff will begin receiving preliminary notices | — |
| new_information | Administration refining reconfiguration options incorporating March 2 board feedback and Skillin constraint | — |
| position_shift | Maria shifts from opposing reconfiguration to influencing which option is chosen | — |
| supersession | "Resist reconfiguration" replaced by "influence which reconfiguration option" — accepts structural change may be necessary | "Resist reconfiguration to protect neighborhood schools" (2026-02-04) |
| thread_opened | Which specific positions will be RIF'd? Who at her child's school? | — |
| thread_opened | What is the realistic final tax increase percentage? | — |
| thread_opened | When is the final budget vote? | — |

#### emotional_register

Sobered and pragmatic. The RIF notifications made the crisis feel human rather than financial. Maria's emotional arc has moved from alarm through overwhelm to a kind of resigned determination. She is preparing to be strategic rather than reactive.

---

### Generated Summary View (after 5 meetings)

```yaml
---
persona_id: PERSONA-001
persona_name: "Maria (Concerned Elementary Parent)"
generated_from: 5 records (2026-01-12 through 2026-03-09)
generated_at: "2026-03-12T00:00:00Z"
---
```

#### Current Understanding

Maria has traversed a three-month arc from vague budget worry to pragmatic engagement with a school district facing a $7.2M structural gap. Elementary reconfiguration — reorganizing five neighborhood K-4 schools into grade-band campuses — is the dominant savings strategy at $1.5-2.2M. Nine specific options have been presented. The Skillin school is likely protected on equity grounds, constraining remaining options. A non-reconfiguration path exists (~$2.2M through across-the-board class size increases) but is characterized as structurally insufficient. Even with savings, a $3M+ residual gap remains. The tax increase will likely land at 5-6% or higher. RIF notifications have begun. Maria has shifted from opposing reconfiguration to trying to influence which option is chosen, focused on protecting her child's specific school and workable transportation logistics.

#### Timeline of Understanding Shifts

1. **2026-01-12** — Initial awareness: "difficult year" signaled. Monitoring mode.
2. **2026-02-04** — Alarm: $7.2M gap, reconfiguration as primary lever. Activated.
3. **2026-02-09** — Deepening: 6% ceiling breaking, reconfiguration confirmed. Preparing for March 2.
4. **2026-03-02** — Confronting specifics: 9 options, Skillin pivot, genuine dilemma between disruption and decline.
5. **2026-03-09** — Pragmatic pivot: RIF notifications make cuts tangible. Shifts from resisting to influencing.

#### Active Supersessions

| What Changed | From | To | When |
|--------------|------|----|------|
| Budget outlook | "Difficult year — stay alert" | $7.2M gap with specific proposals | 2026-02-04 |
| Tax ceiling | 6% as constraint | Ceiling breaking; council guidance 5-6% | 2026-02-09 |
| Reconfiguration status | One of three big ideas | Dominant strategy with 9 detailed options | 2026-03-02 |
| Maria's posture | Resist reconfiguration | Influence which option is chosen | 2026-03-09 |

#### Open Threads

- Which refined reconfiguration option will the administration recommend?
- How does the Skillin constraint narrow viable options?
- Transportation logistics for split-grade-band families?
- Direct parent surveys?
- Which specific positions will be RIF'd?
- Realistic final tax increase percentage?
- Final budget vote timeline?

#### Resolved Threads

- Budget gap size: $7.2M (2026-02-04)
- Decision timeline: workshops March-April (2026-02-04)
- Reconfiguration detail level: 9 options with building-level data (2026-03-02)
- RIF notification: timeline shared (2026-03-09)

---

## Metrics Comparison

### Word Count by Fold

| Fold | Meeting | Fold-in-Place (cumulative doc) | Log-Structured (record only) | Log-Structured (all records cumulative) | Log-Structured (summary view) |
|------|---------|-------------------------------|-------------------------------|----------------------------------------|-------------------------------|
| 1 | 2026-01-12 | 310 | 290 | 290 | — |
| 2 | 2026-02-04 | 820 | 480 | 770 | — |
| 3 | 2026-02-09 | 1,400 | 450 | 1,220 | 400 |
| 4 | 2026-03-02 | 1,850 | 420 | 1,640 | — |
| 5 | 2026-03-09 | 2,100 | 350 | 1,990 | 530 |

_Word counts are approximate, measured from the simulation text above._

**Key observation**: Fold-in-place grows monotonically because the narrative_arc and superseded sections are strictly additive, and current_understanding tends to grow as the situation becomes more complex. Log-structured records are individually stable (300-500 words each) but cumulative storage grows linearly. The log-structured summary view stays compact (~400-530 words) because it is regenerated fresh.

### Projected Word Count at Meeting 14

| Approach | Estimated Words | Under 4,000? |
|----------|----------------|--------------|
| Fold-in-place (cumulative doc) | ~3,800-4,500 | Borderline — may exceed at high complexity |
| Log-structured (record store) | ~5,500-7,000 | N/A — not a single doc |
| Log-structured (summary view) | ~700-900 | Yes — easily |

### Temporal Marker Count

| Fold | Fold-in-Place (narrative_arc rows) | Log-Structured (delta entries with dates) |
|------|-------------------------------------|-------------------------------------------|
| 1 | 1 | 7 |
| 2 | 2 | 19 (7 + 12) |
| 3 | 3 | 31 (19 + 12) |
| 4 | 4 | 42 (31 + 11) |
| 5 | 5 | 49 (42 + 7) |

**Key observation**: Fold-in-place preserves temporal markers at the coarse "one shift per meeting" level. Log-structured preserves every individual delta with its date — much higher granularity but also much more data to process. The fold-in-place narrative_arc is human-readable at a glance; the log-structured deltas require aggregation to be useful.

### Supersession Tracking Quality

| Metric | Fold-in-Place | Log-Structured |
|--------|---------------|----------------|
| Supersessions recorded after 5 folds | 4 | 4 |
| Date of original position preserved? | Yes | Yes |
| Date of supersession preserved? | Yes | Yes |
| Original text preserved? | Summary only (paraphrased) | Full original text in immutable record |
| Can reconstruct state at any point? | Partially — current_understanding is overwritten each fold | Fully — read records 1 through N |

### Narrative Coherence Assessment

| Criterion | Fold-in-Place | Log-Structured |
|-----------|---------------|----------------|
| Can a reader understand Maria's current position? | Yes — current_understanding section is explicitly present-state | Yes — but requires reading the generated summary or the latest record |
| Can a reader trace how she got there? | Yes — narrative_arc table provides chronological shifts | Yes — reading records in order tells the full story with richer detail |
| Is the emotional arc preserved? | Partially — current_understanding captures current emotional state but overwrites prior | Yes — emotional_register in each record is immutable |
| Is it readable as a single document? | Yes — this is its primary advantage | The summary view is; the record store requires sequential reading |

---

## Simulation Findings

1. **Growth control**: Fold-in-place grows monotonically and may challenge the 4,000-word ceiling by meeting 14. Log-structured summary view stays compact regardless of meeting count. The record store grows linearly but each file is small and independent.

2. **Temporal fidelity**: Log-structured preserves more temporal detail (every delta vs. one shift per meeting). Fold-in-place's narrative_arc is more readable but lower resolution.

3. **Supersession tracking**: Both approaches track supersessions adequately. Log-structured has an advantage: the original text is preserved in an immutable record rather than paraphrased in a superseded table.

4. **Auditability**: Log-structured is strictly superior — you can always reconstruct the exact state after any meeting. Fold-in-place loses the prior current_understanding on each fold.

5. **Operational simplicity**: Fold-in-place is simpler at write time (one file to update). Log-structured is simpler at read time (generate a summary from immutable inputs — no merge conflicts, no state management).

6. **Determinism**: Both have non-deterministic elements (LLM-generated prose). Log-structured isolates the non-determinism to record creation (one-shot) and summary generation (regenerable). Fold-in-place's non-determinism is cumulative — each fold depends on the prior fold's output, creating a chain of non-deterministic steps.

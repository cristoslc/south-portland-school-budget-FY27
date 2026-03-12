# Log-Structured Format Prototype

**SPIKE-006 Task 2** | Persona: PERSONA-001 (Maria, Concerned Elementary Parent)

## Format Specification

The log-structured approach separates **storage** from **presentation**:

1. **Immutable interpretation records** — One file per persona per meeting. Once written, never modified. Each record captures the persona's interpretation of that specific meeting in isolation, plus delta annotations (what changed from the prior state).
2. **Generated summary view** — A read-time document produced by processing all interpretation records in chronological order. This view is never persisted (or if cached, is always regenerable). It answers "what does this persona currently believe?" without modifying source records.

### Storage Structure

```
interpretations/
  PERSONA-001/
    2026-01-12.md    # Immutable record for meeting 1
    2026-02-04.md    # Immutable record for meeting 2
    2026-02-09.md    # Immutable record for meeting 3
    ...
```

### Per-Meeting Record Schema

```yaml
---
persona_id: PERSONA-001
persona_name: "Maria (Concerned Elementary Parent)"
meeting_date: "2026-01-12"
meeting_type: "Regular Meeting"
record_version: 1
prior_meeting: null              # or ISO date of previous record
---
```

Each record has three fixed sections:

1. **interpretation** — What this meeting means to the persona. Written as if the persona is processing the meeting in real time. Present tense for this meeting's content.
2. **deltas** — Structured list of what changed relative to the persona's prior state. Each delta has: `category` (new_information | position_shift | supersession | thread_opened | thread_resolved), `description`, and optionally `supersedes` (reference to prior belief).
3. **emotional_register** — Brief note on the persona's emotional state after this meeting (1-2 sentences). Captures tone that might be lost in structured data.

---

## Interpretation Records

### Record 1: January 12, 2026 (Regular Meeting)

```yaml
---
persona_id: PERSONA-001
persona_name: "Maria (Concerned Elementary Parent)"
meeting_date: "2026-01-12"
meeting_type: "Regular Meeting"
record_version: 1
prior_meeting: null
---
```

#### interpretation

The school board has flagged that this will be "another difficult budget year" and announced an aggressive calendar of forums and workshops. No specific budget numbers or proposals were shared. The meeting's substance was largely non-budget: student reports, athletics, community belonging initiatives. The superintendent search was announced alongside budget planning.

For Maria, this is a signal to start paying attention. Her children's elementary experience is not yet threatened by anything concrete, but the board's tone suggests significant changes may be coming. She plans to attend the upcoming budget forums.

#### deltas

| Category | Description | Supersedes |
|----------|-------------|------------|
| new_information | Board signals "another difficult budget year" — no details | — |
| new_information | Aggressive calendar of forums and workshops announced | — |
| new_information | Superintendent search announced in parallel with budget process | — |
| thread_opened | What is the actual size of the budget gap? | — |
| thread_opened | Will elementary programs be targeted for cuts? | — |
| thread_opened | How will the superintendent search affect budget priorities? | — |
| thread_opened | What is the timeline for budget decisions? | — |

#### emotional_register

Alert but not alarmed. The lack of specifics prevents real anxiety, but the board's framing ("difficult") has activated her monitoring instincts. She is paying attention.

---

### Record 2: February 4, 2026 (Budget Forum)

```yaml
---
persona_id: PERSONA-001
persona_name: "Maria (Concerned Elementary Parent)"
meeting_date: "2026-02-04"
meeting_type: "Budget Forum"
record_version: 1
prior_meeting: "2026-01-12"
---
```

#### interpretation

This is the meeting where the budget crisis becomes real. Dr. Johanna Prince presented the full financial picture: the district faces a **$7.2 million structural gap**. Status-quo spending means an 18.95% tax increase on the school portion alone. The board has set a 6% ceiling, meaning roughly $7.2M in cuts or offsets are needed.

Three "big ideas" were proposed:

1. **Elementary reconfiguration** ($1.5-2.2M savings): Reorganizing five neighborhood K-4 schools into grade-band campuses (pre-K-1 and 2-4). This is the largest single savings lever and the most directly threatening to Maria's family. Her child's neighborhood school could be restructured or effectively closed.
2. **Grades 5-12 staffing efficiencies** ($1M): Class size increases at middle and high school.
3. **Operational efficiencies** ($1M): Vendor contracts, shift changes, supply reductions.

Even combined, these three initiatives leave a **$3M+ residual gap**. The fund balance is depleted — no financial cushion exists. Root causes are structural: declining enrollment (~2,736 students), staffing-enrollment divergence, and a 12% health insurance increase.

Maria is now directly confronting the possibility that her child's school experience will fundamentally change by September 2026.

#### deltas

| Category | Description | Supersedes |
|----------|-------------|------------|
| new_information | Budget gap quantified: $7.2M structural deficit | — |
| new_information | Status-quo scenario: 18.95% school tax increase | — |
| new_information | Board set 6% tax increase ceiling | — |
| new_information | Elementary reconfiguration proposed: grade-band campuses, $1.5-2.2M savings | — |
| new_information | Fund balance depleted — no cushion remains | — |
| new_information | Enrollment at decade low: ~2,736 students | — |
| new_information | Health insurance budgeted at 12% increase | — |
| new_information | Even all three "big ideas" leave a $3M+ residual gap | — |
| supersession | Vague "difficult year" replaced by concrete $7.2M gap with specific proposals | "difficult year — stay alert" (2026-01-12) |
| position_shift | Maria shifts from monitoring mode to active concern; begins sharing info in parent networks | — |
| thread_resolved | Budget gap size: $7.2M | thread: "What is the actual size of the budget gap?" |
| thread_resolved | Timeline: March 2 workshop for reconfiguration proposal; decisions March-April | thread: "What is the timeline for budget decisions?" |
| thread_opened | Which specific schools would be reconfigured? Would her child's school close? | — |
| thread_opened | What are the transportation implications of grade-band campuses? | — |
| thread_opened | Has anyone studied educational impact of grade-band vs. neighborhood schools? | — |
| thread_opened | Are there revenue alternatives (state aid, grants, education foundation)? | — |

#### emotional_register

Alarmed and activated. The numbers are worse than she expected. Elementary reconfiguration as the biggest savings lever makes this personal. She is now actively sharing information and preparing to advocate.

---

### Record 3: February 9, 2026 (Regular Meeting)

```yaml
---
persona_id: PERSONA-001
persona_name: "Maria (Concerned Elementary Parent)"
meeting_date: "2026-02-09"
meeting_type: "Regular Meeting"
record_version: 1
prior_meeting: "2026-02-04"
---
```

#### interpretation

The budget situation deepened on multiple fronts. Board member Feller publicly broke from the 6% tax increase ceiling, acknowledging a higher increase may be necessary to avoid "draconian" cuts. This is both frightening (the already-painful 6% may not be enough) and somewhat validating (the board may recognize that deep elementary cuts are unacceptable).

The board **unanimously** requested a formal reconfiguration proposal for the March 2 workshop. Reconfiguration is no longer one idea among many — it is the leading cost-reduction strategy. March 2 is now the pivotal meeting.

The meeting's emotional atmosphere was intensified by non-budget concerns: ICE enforcement activity has caused immigrant children to miss school. The teachers' union made emotional public statements about staff impacts and the RIF notification process. The board unanimously endorsed the city council's immigration resolution. Multiple public speakers (union leaders, parents) pushed for meaningful engagement beyond surveys.

The teachers' union president specifically urged a specific tax target from the city council — the same frustration Maria feels about decisions being made without adequate community input.

Chair DeAngelis made a pointed argument against closing Skillin school due to its service to vulnerable immigrant families. This introduces an equity dimension to the reconfiguration question that may constrain which options are politically viable.

#### deltas

| Category | Description | Supersedes |
|----------|-------------|------------|
| supersession | 6% ceiling may not hold; Feller broke publicly, suggesting higher increase needed | "6% ceiling is the operating constraint" (2026-02-04) |
| position_shift | Reconfiguration confirmed as leading strategy (unanimous request for formal proposal) — no longer one option among many | — |
| new_information | Board unanimously requested formal reconfiguration proposal for March 2 | — |
| new_information | Feller publicly broke from 6% ceiling, saying higher increase may be needed | — |
| new_information | ICE enforcement causing children to miss school; community anxiety rising | — |
| new_information | Board unanimously endorsed city council immigration resolution | — |
| new_information | Teachers' union asked for meaningful engagement beyond surveys; urged council tax target | — |
| new_information | Chair DeAngelis argued against closing Skillin due to equity (immigrant families) | — |
| new_information | Early retirement buyouts explored but "pretty limited" | — |
| position_shift | Maria shifts from active concern to active preparation for March 2 as pivotal meeting | — |
| thread_opened | Which of nine reconfiguration options will be presented March 2? | — |
| thread_opened | Will March 2 include meaningful time for parent input? | — |
| thread_opened | How does the Skillin equity argument affect which schools are candidates? | — |
| thread_opened | What happens to RIF'd staff? Notification timeline? | — |

#### emotional_register

Anxious and determined. The compounding crises (budget, immigration, community tension) make this feel like more than a budget exercise. Maria is preparing for March 2 with specific questions and coordinating with other parents. The stakes feel personal and immediate.

---

## Generated Summary View (after 3 meetings)

_This view is generated by processing records 1-3 in order. It is not stored — it is produced on demand._

```yaml
---
persona_id: PERSONA-001
persona_name: "Maria (Concerned Elementary Parent)"
generated_from: 3 records (2026-01-12 through 2026-02-09)
generated_at: "2026-03-12T00:00:00Z"
---
```

### Current Understanding

Maria faces a school district in crisis. A $7.2M structural budget gap requires massive cuts, with elementary reconfiguration (reorganizing five neighborhood schools into grade-band campuses) as the largest single savings lever at $1.5-2.2M. Even with all proposed savings, a $3M+ gap remains. The 6% tax increase ceiling may not hold — board member Feller has publicly broken from it. The board has unanimously directed the administration to present formal reconfiguration options at the March 2 workshop, which Maria views as the pivotal decision point. Community tensions are heightened by ICE enforcement activity and concerns about meaningful parent engagement in the decision process.

### Timeline of Understanding Shifts

1. **2026-01-12** — Initial awareness: "difficult budget year" signaled, no specifics. Monitoring mode.
2. **2026-02-04** — Alarm: $7.2M gap revealed, elementary reconfiguration proposed as primary savings lever. Activated — sharing information, preparing questions.
3. **2026-02-09** — Deepening engagement: 6% ceiling breaking, reconfiguration confirmed as leading strategy, community anxiety compounding. Preparing for March 2 as pivotal meeting.

### Active Supersessions

| What Changed | From | To | When |
|--------------|------|----|------|
| Budget outlook | "Difficult year — stay alert" | $7.2M gap with specific proposals | 2026-02-04 |
| Tax ceiling | 6% as operating constraint | Ceiling may not hold (Feller break) | 2026-02-09 |

### Open Threads

- Which specific schools would be reconfigured?
- Transportation implications of grade-band campuses?
- Educational impact evidence for grade-band vs. neighborhood models?
- Revenue alternatives being pursued?
- Which of nine reconfiguration options will be presented March 2?
- Will March 2 include meaningful parent input time?
- How does the Skillin equity argument affect which schools are candidates?
- What happens to RIF'd staff?

### Resolved Threads

- Budget gap size: $7.2M (resolved 2026-02-04)
- Decision timeline: March 2 workshop for proposal, decisions March-April (resolved 2026-02-04)

---

## Format Observations

**Growth pattern**: Each immutable record is ~300-500 words. The records never grow — they are write-once. The generated summary view is ~400 words after 3 meetings. The summary view grows modestly because it compresses rather than accumulates: the "Current Understanding" section is regenerated fresh each time, the "Timeline" adds one row per meeting, and threads are netted (resolved threads move to a separate section).

**Projected growth**: After 14 meetings, the record store would contain ~5,000-7,000 words total across 14 files. The generated summary view would be ~600-800 words regardless of meeting count, because the "Current Understanding" is always a fresh synthesis and the structured sections (timeline, supersessions, threads) grow linearly but remain compact.

**Temporal marker preservation**: Perfect. Every interpretation record is timestamped and immutable. The generated summary explicitly lists shifts chronologically. No temporal information is ever lost because the source records are never modified.

**Diffability**: Individual records are immutable — there is nothing to diff. The generated summary view changes with each new record, but because it is regenerated rather than edited, diffs compare two complete generated outputs. The structured sections (timeline, supersessions, threads) diff cleanly; the "Current Understanding" prose will show as a full replacement each time.

**Determinism**: Record creation is a one-shot operation (write once from a single meeting interpretation). The generated summary view is the non-deterministic element — regenerating it from the same records may produce different prose. However, the structured sections (timeline, supersessions, threads) are deterministic because they are extracted from structured delta entries in the records.

**Auditability**: Perfect. Every interpretation is preserved verbatim. You can always reconstruct exactly what was understood after any given meeting by reading records 1 through N.

**Storage trade-off**: More files (1 per meeting per persona = 14 meetings x 14 personas = 196 files for the full project). Each file is small. The generated summary is cheap to produce but requires reading all prior records.

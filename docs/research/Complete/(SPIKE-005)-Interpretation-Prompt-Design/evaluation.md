# Evaluation: Prompt Template v1 Against Go/No-Go Criteria

**Spike:** SPIKE-005 (Interpretation Prompt Design)
**Evaluated:** 2026-03-12
**Samples evaluated:** Maria (PERSONA-001), Tom (PERSONA-006), Jaylen (PERSONA-012)

---

## Criterion 1: Distinct Perspectives

**Requirement:** Interpretations for 3+ personas on the same meeting must demonstrate measurably distinct perspectives (different facts highlighted, different emotional valences, different questions raised).

### Fact Selection Overlap Analysis

| Fact/Topic | Maria | Tom | Jaylen |
|------------|-------|-----|--------|
| Nine reconfiguration options presented | Point 1 (alarmed) | Point 5 (skeptical) | -- |
| Skillin closure as top-ranked option | Point 2 (frustrated) | Point 5 (skeptical) | -- |
| Leadership scored Skillin highest on matrix | Point 2 | Point 5 | -- |
| Board took Skillin off the table | Point 2 | Point 5 | -- |
| No parent survey conducted | Point 3 (frustrated) | -- | -- |
| Transportation logistics unresolved | Point 4 (anxious) | -- | -- |
| Class sizes will increase | Point 5 (anxious) | -- | -- |
| September timeline too fast | Point 6 (alarmed) | -- | -- |
| Middle school merger precedent | Point 7 (cautiously optimistic) | -- | -- |
| 19%/6% tax increase framing | -- | Point 1 (alarmed) | -- |
| Enrollment down 300, staffing up 82 | -- | Point 2 (frustrated) | -- |
| Fund balance depleted | -- | Point 3 (frustrated) | -- |
| Per-pupil spending highest | -- | Point 4 (skeptical) | -- |
| $7.2M gap can't be closed by reconfig alone | -- | Point 6 (alarmed) | Point 3 (anxious) |
| Board members' $1K stipend | -- | Point 7 (neutral) | -- |
| 42 teaching positions cut | -- | -- | Point 1 (anxious) |
| Workshop was all elementary, not HS | -- | -- | Point 2 (frustrated) |
| Athletic complex debt payment | -- | -- | Point 4 (skeptical) |
| Student reps in superintendent search | -- | -- | Point 5 (empowered) |
| 80% of constituents have no kids in schools | -- | -- | Point 6 (neutral) |

**Overlap:** Only 2 topics appear in more than one persona's points (reconfiguration options/Skillin closure, and the residual $3M+ gap), and even these shared topics have different emotional valences and frame the issue differently:
- Maria sees Skillin closure through an equity/impact lens; Tom sees it through a fiscal efficiency lens
- Tom frames the residual gap as "who pays the difference"; Jaylen frames it as "what else gets cut at SPHS"

**15 of 20 total points are unique to a single persona.** This is strong distinctness.

**VERDICT: PASS**

### Emotional Valence Distribution

| Valence | Maria | Tom | Jaylen |
|---------|-------|-----|--------|
| alarmed | 2 | 2 | 0 |
| anxious | 2 | 0 | 2 |
| frustrated | 2 | 2 | 1 |
| skeptical | 0 | 2 | 1 |
| neutral | 0 | 1 | 1 |
| cautiously_optimistic | 1 | 0 | 0 |
| empowered | 0 | 0 | 1 |
| reassured | 0 | 0 | 0 |

Maria skews alarmed/anxious (parental fear). Tom skews frustrated/skeptical (fiscal distrust). Jaylen is more varied, mixing anxiety with empowerment and detachment. These distributions are coherent with persona profiles.

**VERDICT: PASS**

### Open Question Analysis

Maria's questions are concrete and personal: "Which option means my kid changes schools?" "Am I doing two different drop-offs?" "How can they say they've been transparent?"

Tom's questions are systemic and fiscal: "How did they hire 82 people while losing 300 kids?" "Are we getting more per kid?" "Who pays the difference?"

Jaylen's questions are program-specific and self-referential: "Does that mean AP classes get cut?" "When do they talk about the high school?" "Can I be one of those reps?"

No two personas ask similar questions. The question framing matches voice and concerns.

**VERDICT: PASS**

---

## Criterion 2: Evidence Grounding (80%+ Threshold)

**Requirement:** At least 80% of structured points reference specific evidence from the meeting bundle.

### Maria's Points (7 total)

| Point | Source reference | Grounded? |
|-------|----------------|-----------|
| 1 | [00:22--01:10], Source 012 | Yes |
| 2 | [02:06--02:11], Source 012 | Yes |
| 3 | [02:40--02:46] public comment | Yes |
| 4 | [01:08--01:10], [02:44--02:45] | Yes |
| 5 | [01:06--01:07], Synthesis | Yes |
| 6 | [02:45--03:15], Source 011 | Yes |
| 7 | [00:15--00:17] | Yes |

**7/7 grounded = 100%**

### Tom's Points (7 total)

| Point | Source reference | Grounded? |
|-------|----------------|-----------|
| 1 | [00:05--00:06] | Yes |
| 2 | [00:06], Source 010 | Yes |
| 3 | [00:05], Synthesis | Yes |
| 4 | Synthesis, Source 005 | Yes |
| 5 | [02:06--02:11], Source 012 | Yes |
| 6 | Synthesis, [01:06--01:10] | Yes |
| 7 | [00:04--00:05] | Yes |

**7/7 grounded = 100%**

### Jaylen's Points (6 total)

| Point | Source reference | Grounded? |
|-------|----------------|-----------|
| 1 | Synthesis, Source 011, [00:09--00:14] | Yes |
| 2 | [00:09--00:14], [00:14--02:11] | Yes |
| 3 | [00:05--00:06], Synthesis | Yes |
| 4 | Synthesis, Source 011 | Yes |
| 5 | Synthesis, Feb 9 decisions | Yes |
| 6 | [00:05] | Yes |

**6/6 grounded = 100%**

**All three personas at 100% evidence grounding.**

**VERDICT: PASS (20/20 = 100%, well above 80% threshold)**

---

## Criterion 3: Narrative-Arc Journey Maps

**Requirement:** Journey maps reflect the meeting's narrative arc (sequential beats), not just a list of topics discussed.

### Maria's Journey (6 beats)

Arc: Tense anticipation -> Overwhelmed -> Alarmed -> Cautiously relieved -> Validated -> Deflated

This is a genuine emotional arc with rising action (alarm at the matrix reveal), a turning point (board pushback on Skillin), rising relief during public comment (finding her people), and a deflating resolution (no commitments). The beats follow the meeting chronologically and each has a clear emotional trigger.

### Tom's Journey (5 beats)

Arc: Grim satisfaction -> Impatient -> Engaged/calculating -> Frustrated -> Disengaged/irritated

This arc reflects a different personality: Tom enters with validation (the numbers confirm what he suspected), grows impatient with non-financial content, engages when dollar figures appear, gets frustrated when fiscal logic is overridden by equity arguments, and tunes out during parent-dominated public comment. The arc is believable and distinct from Maria's.

### Jaylen's Journey (5 beats)

Arc: Surprised/concerned -> Disengaged -> Uneasy -> Uncomfortable/detached -> Deflated

This is the arc of someone realizing the issue affects them but not being the target audience. Jaylen starts surprised at the severity, loses interest during elementary presentations, reconnects when he realizes the gap affects all levels, feels alienated during parent testimony, and ends deflated by the lack of SPHS-specific information. This is a meaningfully different arc from both Maria and Tom.

### Cross-comparison

All three journey maps follow the meeting's chronological structure (opening -> presentations -> board discussion -> public comment -> closing). But each persona's emotional trajectory is distinct:
- Maria peaks emotionally during the options matrix and public comment
- Tom peaks during the opening numbers and the moment the board eliminates the highest-savings option
- Jaylen's emotional engagement dips in the middle and never fully recovers

None of the journey maps read as topic lists. Each tells a story.

**VERDICT: PASS**

---

## Criterion 4: Voice-Matched Reactions

**Requirement:** Unstructured reactions read as authentically voice-matched to the persona profile.

### Maria (Concerned Elementary Parent)

**Voice markers:**
- Conversational, emotional, specific to her family situation
- "I don't even know where to start" -- overwhelmed parent register
- "Nine different ways they could blow up the elementary schools" -- visceral, not analytical
- "Parents were... crying about their kids" -- she notices other parents
- "I'm going to be there. I'm going to every single one." -- action-oriented advocacy
- References specific details (bus rides, drop-off logistics) that map to her daily life
- Does NOT use fiscal jargon, per-pupil costs, or policy language

**Assessment:** Reads as a concerned, engaged parent venting to her partner after a long, stressful meeting. Vocabulary and emotional register match PERSONA-001 profile.

**VERDICT: PASS**

### Tom (Tax-Conscious Resident)

**Voice markers:**
- Matter-of-fact, numbers-first, slightly sardonic
- "Had to sit through another one of those school board things" -- weary obligation
- "Nineteen percent" isolated for emphasis -- bottom-line focus
- "They burned through almost six million dollars in reserves" -- fiscal accountability framing
- "Not one of them talked about what they'd be willing to pay" -- the core taxpayer complaint
- Uses percentage figures, dollar amounts, and multi-year trends fluently
- Does NOT reference specific children, schools by name, or educational philosophy

**Assessment:** Reads as a long-time homeowner giving his neighbor the fiscal summary. Sardonic but not hostile. The emphasis on "who pays" is consistent and distinct from Maria's emphasis on "who's impacted."

**VERDICT: PASS**

### Jaylen (High School Student)

**Voice markers:**
- Casual, teenage register with authentic rhythm
- "Dude, it was three and a half hours long. THREE AND A HALF." -- capitalization for emphasis, peer-to-peer speech
- "Parents were losing it. Like, lined up at the microphone crying" -- observational, slightly detached
- "Make it make sense" -- contemporary teen phrase, not coached
- "old people fighting about taxes" -- blunt, slightly dismissive, age-appropriate
- Reframes adult concerns through a student lens (AP classes, theater, cross-country coach)
- Does NOT use budget jargon, property tax calculations, or formal policy language
- Does reference social media norms ("I watched the recording")

**Assessment:** Reads as a politically aware 16-year-old explaining to a friend why this matters. The mixture of genuine concern (about programs) and social detachment (from parent drama) is age-appropriate. The voice is clearly different from both Maria and Tom.

**VERDICT: PASS**

---

## Criterion 5: Context Window Fit

**Requirement:** Total prompt fits within a single context window (meeting bundle + persona definition + output instructions).

**Estimated token usage:**
- Prompt template (system + instructions + output format): ~1,200 tokens
- Persona definition: ~500-700 tokens
- Fiscal context summary: ~300 tokens
- Meeting transcript digest (Source 004): ~15,000-20,000 tokens
- Supporting document extracts: ~2,000-3,000 tokens

**Total input: ~19,000-25,000 tokens**

**Output: ~2,000-3,500 tokens** (observed in samples)

**Total round-trip: ~21,000-28,500 tokens**

This fits comfortably in a 128K context window. Even a 32K context window would accommodate this. For 14 personas, these are 14 independent calls (not simultaneous), so context window is not cumulative.

**VERDICT: PASS**

---

## Summary

| Criterion | Result | Notes |
|-----------|--------|-------|
| 1. Distinct perspectives | **PASS** | 15/20 unique points; different emotional distributions; no question overlap |
| 2. 80%+ evidence grounding | **PASS** | 20/20 points grounded (100%) |
| 3. Narrative-arc journey maps | **PASS** | All three show distinct emotional arcs following meeting chronology |
| 4. Voice-matched reactions | **PASS** | Each persona has clearly different vocabulary, register, and emotional framing |
| 5. Context window fit | **PASS** | ~25K tokens per call; fits in 32K+ context window |

## Overall Assessment: **GO**

The single-pass prompt template v1 meets all five go/no-go criteria. The two-stage fallback approach (Task 5) is not needed.

### Strengths Observed

1. **Persona-first ordering works.** Placing the persona definition before meeting content produces genuinely different fact selection, not just different commentary on the same facts.
2. **The "what would they skip" instruction drives distinctness.** Tom's journey map explicitly shows him disengaging during principal presentations and parent testimony -- this selective attention is what makes the output feel real.
3. **Reaction audience mapping produces natural voice.** Writing to "your partner after the kids are in bed" vs. "your neighbor over the fence" vs. "your friend at lunch" produces markedly different registers without requiring explicit style instructions.
4. **Source references don't feel forced.** The timestamp and document citations integrate naturally into the structured points format without making the output feel like a research paper.

### Risks for Production

1. **Transcript quality.** The auto-generated captions contain errors (especially proper nouns). The prompt should use the cleaned source digest rather than raw VTT to avoid propagating transcription errors into interpretations.
2. **Persona definitions with less behavioral specificity** (e.g., PERSONA-014, Elementary Student) may produce less distinct output. The younger personas have less developed internal monologue patterns. Testing across all 14 will be needed.
3. **Longer meetings may require summarization.** The March 2 transcript is ~15K-20K tokens in digest form. If a meeting generates a 30K+ token digest, a pre-summarization step may be needed to stay within budget.
4. **The "empowered" and "reassured" valences are underused.** All three samples skew negative. This may be appropriate for this particular meeting (which was genuinely concerning) but should be monitored across different meeting types to ensure the prompt doesn't produce uniformly anxious interpretations.

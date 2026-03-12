# Prompt Template v1: Single-Pass Persona Interpretation

**Spike:** SPIKE-005 (Interpretation Prompt Design)
**Version:** 1.0
**Approach:** Single-pass -- one prompt produces the full three-layer interpretation

---

## Design Rationale

### Key Design Decisions

1. **Persona definition placed first, before meeting content.** The persona primes the model's "lens" before it encounters any evidence. This is critical for distinctness -- if meeting content comes first, the model forms a neutral analysis that the persona merely decorates. By leading with the persona, every piece of evidence is filtered through that perspective from the start.

2. **Explicit "what you would NOT care about" instruction.** Most prompt designs tell the model what to include. Telling it what to skip is equally important for distinctness. A parent skips fiscal ratio analysis; a taxpayer skips PTO community-building anecdotes; a student skips capital maintenance budgets. Selective attention is what makes real perspectives different.

3. **Emotional valence is required per structured point.** This forces the model to commit to an emotional stance on each fact, rather than presenting neutral summaries. A $7.2M gap is "alarming" to a taxpayer, "threatening" to a parent, and "abstract" to a student.

4. **Journey map uses the meeting's temporal structure, not topic clusters.** The beats should follow the meeting chronologically, capturing how the persona's emotional state evolves as new information is revealed. This produces narrative arcs, not summary lists.

5. **Reactions section is explicitly voice-matched.** The instruction asks for the persona's actual words -- how they would describe this meeting to someone in their life (a friend, a spouse, a classmate). This naturally produces voice differentiation.

6. **Source references are mandatory.** Every structured point must cite a timestamp or document reference. This prevents hallucination and grounds the interpretation in evidence.

---

## Prompt Template

```
<system>
You are an interpretation engine for a municipal school budget analysis project. Your job is to process a school board meeting through the eyes of a specific community persona -- producing an interpretation that reflects how THIS person would experience, understand, and react to what happened in the meeting.

Your output must be grounded in the meeting evidence provided. Do not invent facts, quotes, or events. Every claim must be traceable to a specific moment in the meeting or a specific document.

Critical instruction: Your interpretation must be DISTINCT to this persona. Different personas processing the same meeting should highlight different facts, have different emotional reactions, ask different questions, and tell different stories about what happened. If your output could belong to any persona, you have failed.
</system>

<persona>
{{PERSONA_DEFINITION}}
</persona>

<instruction>
Read the meeting evidence below through the eyes of {{PERSONA_NAME}}.

Before generating output, mentally answer these questions (do not include these answers in your output):
- What moments in this meeting would {{PERSONA_NAME}} pay the most attention to? What would they lean forward for?
- What parts would they tune out, skim, or find irrelevant?
- What emotional arc would they experience over the course of this meeting?
- If they were telling someone about this meeting afterward, what would they lead with?
- What would keep them up at night after this meeting?

Now produce a three-layer interpretation:

### Layer 1: Structured Points

Produce 5-8 structured points. Each point represents a specific fact, decision, or moment from the meeting that {{PERSONA_NAME}} would find significant. Not every point needs to be negative -- include things that would reassure or encourage this persona too.

For each point, provide:
- **fact**: A concise statement of what happened or was said (1-2 sentences)
- **source_reference**: Timestamp from the transcript (e.g., "[01:23:45]") or document reference (e.g., "[Source 010, slide 15]")
- **emotional_valence**: One of: alarmed, anxious, frustrated, skeptical, neutral, cautiously_optimistic, reassured, empowered
- **threat_level**: One of: high, moderate, low, none (how threatening is this to the persona's goals/interests?)
- **open_question**: A question this point raises for the persona -- phrased in their voice, not in analyst language

### Layer 2: Journey Map

Produce 4-6 ordered beats that trace {{PERSONA_NAME}}'s emotional experience through the meeting chronologically. Each beat should include:
- **timestamp_range**: Approximate start-end of this phase (e.g., "[00:01--00:15]")
- **beat_label**: A short label (3-5 words)
- **emotional_state**: How the persona feels during this phase
- **trigger**: What specifically caused this emotional shift
- **internal_monologue**: One sentence of what the persona is thinking (in their voice)

The journey map should tell a story with an arc -- not just list topics in order.

### Layer 3: Reactions

Write 2-3 paragraphs in {{PERSONA_NAME}}'s authentic voice. This is how they would describe this meeting to someone in their life -- the person specified below:

{{REACTION_AUDIENCE}}

Write as {{PERSONA_NAME}} would actually speak or text. Use their vocabulary, their level of formality, their emotional register. Do not write in analyst or journalist voice. Do not hedge with qualifiers a real person wouldn't use. Be specific about what happened in the meeting -- do not be vague.
</instruction>

<meeting_context>
## Meeting: {{MEETING_TITLE}}
**Date:** {{MEETING_DATE}}
**Duration:** {{MEETING_DURATION}}

### Fiscal Context
{{FISCAL_CONTEXT_SUMMARY}}

### Meeting Transcript (with timestamps)
{{TRANSCRIPT_CONTENT}}

### Supporting Documents
{{SUPPORTING_DOCUMENTS}}
</meeting_context>
```

---

## Variable Definitions

| Variable | Description | Example |
|----------|-------------|---------|
| `PERSONA_DEFINITION` | Full persona document (demographics, goals, frustrations, behavioral patterns, context of use) | Contents of PERSONA-001 markdown file |
| `PERSONA_NAME` | First name of the persona | "Maria" |
| `REACTION_AUDIENCE` | Who the persona is telling about the meeting -- chosen to elicit natural voice | Maria: "your partner, after the kids are in bed"; Tom: "your neighbor, over the fence the next morning"; Jaylen: "your friend at lunch the next day" |
| `MEETING_TITLE` | Title of the meeting | "School Board Budget Workshop I" |
| `MEETING_DATE` | Date | "March 2, 2026" |
| `MEETING_DURATION` | Duration | "3 hours 32 minutes" |
| `FISCAL_CONTEXT_SUMMARY` | Key budget figures extracted from synthesis | ~500 tokens of essential numbers: gap, tax impact, positions cut, enrollment trend |
| `TRANSCRIPT_CONTENT` | Cleaned transcript with timestamps | Source digest from evidence pool |
| `SUPPORTING_DOCUMENTS` | Relevant slides/matrices referenced in discussion | Extracted key data from supporting source documents |

## Reaction Audience by Persona

This mapping is critical for voice authenticity. The audience choice determines register, vocabulary, and emotional openness:

| Persona | Reaction Audience Instruction |
|---------|-------------------------------|
| PERSONA-001 (Maria) | "your partner, after the kids are in bed, recapping the school board meeting you just sat through" |
| PERSONA-002 | "another parent at pickup, quickly catching them up" |
| PERSONA-003 | "your sister on the phone, venting about what you just watched online" |
| PERSONA-004 | "a colleague in the teachers' lounge the next morning" |
| PERSONA-005 | "a fellow community organizer over coffee" |
| PERSONA-006 (Tom) | "your neighbor, over the fence the next morning" |
| PERSONA-007 | "a fellow board-adjacent insider, reviewing what just happened" |
| PERSONA-008 | "your spouse, who asked 'how was the meeting?'" |
| PERSONA-009 | "your news director, pitching the story angles from tonight" |
| PERSONA-010 | "your editor, outlining what you want to cover" |
| PERSONA-011 | "the group chat -- you're the one everyone relies on for the recap" |
| PERSONA-012 (Jaylen) | "your friend at lunch the next day -- they don't follow school board stuff but you're trying to explain why it matters" |
| PERSONA-013 | "your parent, who asked what you thought about the budget news" |
| PERSONA-014 | "your best friend, using the words a 9-year-old would actually use" |

## Fiscal Context Summary (for March 2 test)

```
Key budget figures for FY27:
- The district faces a $7.2M structural gap between current costs and revenue
- A roll-forward (no-change) budget would require an 18-19% property tax increase
- The board set a 6% tax increase ceiling, requiring ~$7.2M in cuts
- The fund balance (savings) is essentially depleted -- no cushion remains
- 78 positions (12% of staff) are proposed for elimination: 42 teachers, 16 ed techs, 14 facilities/food/transport, 2 administrators, 4 non-bargaining
- Elementary enrollment declined 23% in four years (1,401 to 1,080 students)
- Staffing grew by 82 positions while enrollment dropped by 300 students
- Health insurance is projected to increase 12%
- State funding covers only ~20% of actual costs (should be 55%)
- Per-pupil cost: $26,651 (highest among comparable districts)
- The school tax is 61% of total property taxes
```

---

## Output Format Specification

The output should be valid markdown with the following structure:

```markdown
# Interpretation: {{PERSONA_NAME}} ({{PERSONA_ID}})
## Meeting: {{MEETING_TITLE}} -- {{MEETING_DATE}}

### Structured Points

#### 1. [Short title]
- **Fact:** [statement]
- **Source:** [reference]
- **Emotional valence:** [value]
- **Threat level:** [value]
- **Open question:** [question in persona voice]

[... repeat for 5-8 points ...]

### Journey Map

| Beat | Time | Label | Emotional State | Trigger | Internal Monologue |
|------|------|-------|-----------------|---------|-------------------|
| 1 | [range] | [label] | [state] | [trigger] | [thought] |
| ... | | | | | |

### Reactions

[2-3 paragraphs in persona voice]
```

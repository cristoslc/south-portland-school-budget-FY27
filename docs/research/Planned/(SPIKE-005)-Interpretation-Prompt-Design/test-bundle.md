# Test Bundle: March 2, 2026 Budget Workshop I

**Spike:** SPIKE-005 (Interpretation Prompt Design)
**Prepared:** 2026-03-12

---

## Meeting Under Test

**School Board Budget Workshop I -- March 2, 2026**
- Duration: 3 hours 32 minutes
- Format: Public workshop with administration presentations + board Q&A + public comment
- Attendance: Full house; all board members present (DeAngelis, Dowling, Feller, Holman, Richardson, Rish, Smith)

## Sources Included in Test Bundle

### Primary Source

| Source | Path | Notes |
|--------|------|-------|
| Meeting transcript (VTT) | `data/school-board/meetings/2026-03-02-budget-workshop-1/transcript.en-x-autogen.vtt` | Auto-generated captions, ~17,800 lines. No speaker attribution. Proper noun errors likely. |
| Source digest (evidence pool) | `docs/evidence-pools/school-board-budget-meetings/sources/004-budget-workshop-1-2026-03-02.md` | Timestamped, cleaned transcript with paragraph groupings. |

### Supporting Budget Documents

| Source | Path | Relevance |
|--------|------|-----------|
| Workshop slides digest | `docs/evidence-pools/fy27-budget-documents/sources/010-workshop-slides-2026-03-02.md` | Presentation slides referenced during the meeting |
| Reconfiguration models & matrix | `docs/evidence-pools/fy27-budget-documents/sources/012-models-and-matrix-2026-03-02.md` | Nine elementary reconfiguration options with scoring matrix |
| Budget forum slides (Feb 4) | `docs/evidence-pools/fy27-budget-documents/sources/007-budget-forum-slides-2026-02-04.md` | Background context on the $7.2M gap and "big ideas" |

### Synthesis Documents

| Source | Path | Relevance |
|--------|------|-----------|
| School board meetings synthesis | `docs/evidence-pools/school-board-budget-meetings/synthesis.md` | Cross-meeting thematic analysis covering Jan 12 -- Mar 2 |
| FY27 budget documents synthesis | `docs/evidence-pools/fy27-budget-documents/synthesis.md` | Fiscal context: $7.2M gap, 78 position cuts, reconfiguration options |

## Personas Selected for Testing

| Persona | Archetype | Rationale for Selection |
|---------|-----------|----------------------|
| **Maria** (PERSONA-001) | Concerned Elementary Parent | Directly impacted by reconfiguration proposals. Represents the dominant voice in public comment. Tests whether the prompt can capture parental anxiety, transportation concerns, and desire for transparency. |
| **Tom** (PERSONA-006) | Tax-Conscious Resident | Not directly impacted by school reconfiguration. Cares about the bottom line ($7.2M gap, 6% ceiling, mil rate). Tests whether the prompt produces a genuinely different lens -- fiscal efficiency vs. programmatic impact. |
| **Jaylen** (PERSONA-012) | High School Student | Neither directly impacted by elementary changes nor a taxpayer. Interested in what this means for SPHS programs. Tests the hardest case: a persona who must find relevance in a meeting primarily about elementary schools. |

These three personas were chosen to maximize distinctness: they occupy different positions on the stakeholder spectrum (direct impact, indirect fiscal interest, tangential programmatic concern), have different information-consumption patterns, and should produce visibly different emotional valences when encountering the same meeting content.

## Key Meeting Content for Interpretation

The March 2 workshop covered:

1. **Opening statements by Chair DeAngelis** [00:01--00:07]: Acknowledged community emails, addressed the $7M "not a deficit" framing, noted declining enrollment of 300 students alongside an increase of 82 staff, stated 19% status-quo tax increase, emphasized the board represents all residents including the 80%+ without children in schools.

2. **Superintendent Entwistle's framing** [00:09--00:14]: Positioned this as first of four March workshops, emphasized sequential deliberation, noted that the elementary focus tonight does not represent all organizational review.

3. **Principal presentations** [00:14--00:22]: Each of the five elementary principals presented demographics and enrollment data for their schools. Key data: enrollment declined from 1,401 (2021-22) to 1,080 (2025-26); significant demographic variation across schools (Skillin: highest multilingual %, Dyer/Brown: different profiles).

4. **Reconfiguration options presentation** [00:22--01:10]: Nine models presented with a scoring matrix. Options ranged from reconfigure-no-closure (1.1, 1.2) to close-and-reconfigure (1.3--1.8). Leadership's top three: Option 1.7 (close Skillin, ~$19.6M 5-year savings, score 46), Option 1.3 (close Kaler/Dyer, $16.4M, score 40), Option 1.8 (close Skillin but keep others PreK-4, $18.8M, score 38).

5. **Board discussion** [01:10--02:11]: Member Feller asked about long-term enrollment; Member Holman asked about portables and capital costs; Member Smith raised the "busing" historical parallel; Chair DeAngelis made an extended argument against closing Skillin based on equity -- noting that at least four board members opposed it, effectively taking Options 1.7 and 1.8 off the table.

6. **Public comment** [02:11--03:25]: Approximately 20+ speakers. Dominant themes: concern about disruption to young children, transportation burden for families with children in multiple grade bands, loss of neighborhood school community, pace of decision-making, lack of parent surveys, equity implications of closing schools serving marginalized populations. Several speakers referenced the Boundaries and Configurations Committee process from prior years.

7. **Closing** [03:25--03:32]: Board directed administration to refine models (excluding Skillin closure) for subsequent workshops. No votes taken.

## Token Budget Estimate

For prompt design testing, the input bundle will be composed from:
- **Meeting context**: The source digest (004) is the most token-efficient representation of the transcript. Estimated ~15,000--20,000 tokens.
- **Supporting fiscal context**: Key figures from the synthesis documents. Estimated ~2,000--3,000 tokens (extracted, not full documents).
- **Persona definition**: Each persona document is ~500--700 tokens.
- **Prompt template + output instructions**: Estimated ~1,000--1,500 tokens.

**Total estimated input**: ~19,000--25,000 tokens per interpretation call. Well within a 128K+ context window. Even with a generous output allocation of ~3,000--5,000 tokens, this leaves substantial headroom.

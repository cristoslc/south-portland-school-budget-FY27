# South Portland 2026 School Budget Analysis

Independent analysis of the South Portland School Department's proposed FY27 (2026-2027) budget. The district faces an **$8.4 million structural gap** and has proposed **eliminating 78 positions** and **closing one elementary school** to bridge it. This project translates the raw budget into forms that residents can actually use.

This is a research project, not a software application. The outputs are documents, not code.

## Start Here: Budget Briefings

The `dist/briefings/` folder contains ready-to-read briefings -- the main output of this project.

| Briefing | Audience |
|----------|----------|
| [General Budget Briefing](dist/briefings/general-budget-briefing.md) | Anyone -- covers the full budget picture |
| [Maria (Concerned Elementary Parent)](dist/briefings/persona-001-maria-concerned-elementary-parent.md) | Parents worried about school closures and classroom impact |
| [David (Pragmatic Elementary Parent)](dist/briefings/persona-002-david-pragmatic-elementary-parent.md) | Parents focused on logistics -- redistricting, transportation, transitions |
| [Jess (Anxious Pre-K Parent)](dist/briefings/persona-003-jess-anxious-prek-parent.md) | Incoming families navigating uncertainty |
| [Marcus (High School Teacher)](dist/briefings/persona-004-marcus-high-school-teacher.md) | Teachers facing staffing cuts and workload changes |
| [Priya (Equity-Focused Community Member)](dist/briefings/persona-005-priya-equity-focused-community-member.md) | Advocates tracking how cuts affect underserved students |
| [Tom (Tax-Conscious Resident)](dist/briefings/persona-006-tom-tax-conscious-resident.md) | Taxpayers evaluating the fiscal picture and mil rate impact |
| [Linda (School Board Insider)](dist/briefings/persona-007-linda-school-board-insider.md) | Board members and governance participants |
| [Rachel (Disruption-Averse Parent)](dist/briefings/persona-008-rachel-disruption-averse-parent.md) | Parents prioritizing stability and minimal disruption |

## Research Documentation

The `docs/` folder contains the research artifacts behind the briefings.

### Evidence Pools

Primary source research, organized by topic. Each pool has a manifest, individual source notes, and a thematic synthesis.

- **[FY27 Budget Documents](docs/evidence-pools/fy27-budget-documents/synthesis.md)** -- Meeting packets, presentations, and spreadsheets from the district (12 sources, Dec 2025 - Mar 2026)
- **[School Board Budget Meetings](docs/evidence-pools/school-board-budget-meetings/synthesis.md)** -- Transcripts and analysis of board meetings where the budget was discussed (4 meetings, Jan - Mar 2026)
- **[City Council Meetings 2026](docs/evidence-pools/city-council-meetings-2026/synthesis.md)** -- Council meeting transcripts covering budget-adjacent municipal context (7 meetings, Jan - Mar 2026)

### Personas

Eight [validated stakeholder personas](docs/persona/list-persona.md) representing the range of people affected by this budget. Each persona defines key questions, information needs, and concerns that guided the briefing content.

### User Journeys

Four [draft user journeys](docs/journey/list-journey.md) mapping how different stakeholders move from initial awareness to informed participation:

- Understanding what's changing at my kid's school
- Evaluating the budget as a fiscal document
- Tracing equity through the budget
- Navigating the budget as a governance participant

### Vision

The [project vision](docs/vision/Active/(VISION-001)-SP-Budget-Analysis/(VISION-001)-SP-Budget-Analysis.md) defines scope, audience, success metrics, and non-goals.

## Raw Data

The `data/` folder contains source materials -- meeting transcripts (VTT), budget PDFs, presentation slides, and agendas. See [`data/README.md`](data/README.md) for a full inventory with dates and source links. Binary files (PDFs, spreadsheets, VTTs) are gitignored; the data README serves as the manifest.

## Scripts

Utility scripts in `scripts/` for data processing:

- `parse_vtt.py` -- Parse Vimeo auto-generated transcript files
- `build_evidence_pool.py` -- Build structured evidence pools from source documents
- `add_key_points.py` -- Extract and annotate key points from sources

## Timeline

This analysis covers the FY27 budget as proposed through March 2026. Key upcoming dates:

- **Mar 16** -- Open Conversation with District Leadership
- **Mar 23** -- Budget Workshop II
- **Mar 30** -- Budget Workshop III
- **Apr 14** -- City Council Budget Workshop #1

The budget process typically runs March through June, ending with a public referendum vote.

## How This Project Is Built

This project uses [swain](https://github.com/cristoslc/swain), an AI-agent skill framework designed for software product development -- not municipal government or civic advocacy. Swain provides structured workflows for things like vision documents, user personas, evidence pools, and implementation specs. Repurposing it for school budget analysis means the terminology and artifact structure can feel odd: budget stakeholders are modeled as "user personas," meeting transcripts go through "evidence pool" pipelines, and briefings are treated as product deliverables. It works, but if you browse the `docs/` folder and wonder why a budget analysis project has software-style artifacts, that's why.

## Disclaimer

This is an independent, volunteer analysis. It is not affiliated with or endorsed by the South Portland School Department or City of South Portland.

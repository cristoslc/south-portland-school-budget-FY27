---
title: "Evaluating the Budget as a Fiscal Document"
artifact: JOURNEY-002
status: Validated
author: cristos
created: 2026-03-10
last-updated: 2026-03-11
parent-vision: VISION-001
linked-personas:
  - PERSONA-002
  - PERSONA-006
depends-on: []
---

# Evaluating the Budget as a Fiscal Document

## Persona

**David** (Pragmatic Elementary Parent, PERSONA-002) is the primary actor — comfortable with financial documents, wants to understand the budget holistically and verify claims against data. **Tom** (Tax-Conscious Resident, PERSONA-006) follows a parallel but narrower path — focused on the bottom line and tax impact, engaging through local media rather than primary sources.

## Goal

Assess the FY27 school budget's fiscal soundness — revenue sources, cost drivers, spending efficiency, and tax impact — and form an informed position on whether it represents responsible stewardship.

## Steps / Stages

### 1. Trigger

David sees the budget headline (3.33% increase, $8.4M gap, 78 position cuts) and wants to understand the full picture. He's not alarmed — he knows budgets are hard — but he wants to verify the framing.

Tom sees the same headline through the lens of his tax bill. His first question: "How much more will this cost me?"

### 2. Acquiring the Data

David downloads the superintendent's budget presentation (PDF), the meeting packet, and the models-and-matrix spreadsheet. He looks for the full proposed budget book — it doesn't exist yet (scheduled for March 23 workshop).

Tom reads the Sentry or Forecaster summary. He may glance at the budget page but won't download the full packet.

> **PP-01:** The detailed line-item budget has not been published as of the superintendent's presentation. The March 9 presentation is a high-level summary. David can't do a proper analysis without the cost center detail.

### 3. Building Context

David looks for year-over-year trends: how has the budget changed over 3-5 years? Per-pupil spending compared to similar districts? Staffing ratios over time? He finds some of this in presentations (per-pupil comparison, staff-to-student ratio history) but it's scattered across multiple PDFs from different meetings.

Tom wants to know: what's the mil rate impact? What does a 6% school tax increase mean on a $300K home? This basic calculation is not in any published document.

> **PP-02:** Historical trend data is scattered across multiple presentations. There is no single longitudinal view. Budget categories shift between years, making apples-to-apples comparison difficult.

> **PP-03:** The per-household tax impact is not calculated in published materials. Taxpayers must derive it themselves or rely on journalistic estimates.

### 4. Analyzing Cost Drivers

David digs into the cost structure: 80% personnel, contractual wage increases at 6-8% actual, health insurance at +12%, fund balance depleted. He identifies the staff-to-student ratio divergence (5.26:1 to 4.14:1) as the structural problem. He compares South Portland's $26,651 per-pupil cost to peers.

He wants to understand the audit findings — material weakness in reconciliations, $400K in misallocated grants, six finance directors in five years. These are red flags for fiscal management.

> **PP-04:** The audit findings are buried in one meeting packet (February 9). There's no public-facing summary of what went wrong, what's being fixed, and whether the corrective actions are working.

### 5. Evaluating the Proposal

David assesses whether the $8.4M in cuts is the right number and the right mix. He compares the reconfiguration options by their matrix scores and 5-year savings. He notices the superintendent chose Option 1.4 (Dyer closure, $12.8M savings, score 20/46) over Option 1.7 (Skillin closure, $19.6M savings, score 46/46) — a $6.8M difference over 5 years. He wants to understand that trade-off explicitly.

Tom evaluates simpler: is the increase below what he considers reasonable (at or near inflation)? Are administrators being cut proportionally to teachers? He focuses on the director-level FTE trend (10.8 → 14 → 13 → 11).

> **PP-05:** The no-closure alternative (Option 1.2) was never fully costed. The counterfactual — what deeper across-the-board cuts look like without closing a school — is undefined. David can't evaluate "is closure necessary?" without seeing the alternative.

### 6. Forming a Position

David builds a view: the cuts are painful but the structural problem is real. He may disagree on specific choices (why Dyer over Skillin? why not more administrative reduction?) but he understands the constraints. He shares observations privately with a board member he knows.

Tom decides whether to vote yes or no on the June referendum. His calculus: is the increase acceptable given his fixed income? Do the cuts show the district is tightening its belt? Is there enough accountability?

> **PP-06:** The referendum is a binary yes/no on the entire combined city/school budget. There's no way to approve the school budget at a lower number or to approve the city side but not the school side. The choice architecture doesn't match the granularity of taxpayer preferences.

```mermaid
journey
    title Evaluating the Budget as a Fiscal Document
    section Trigger
      See budget headline: 3: Data-Driven Realist
      Calculate tax bill impact: 2: Fiscal Watchdog
    section Acquiring the Data
      Download budget presentation PDF: 4: Data-Driven Realist
      Look for full budget book: 1: Data-Driven Realist
      Read newspaper summary: 3: Fiscal Watchdog
    section Building Context
      Find per-pupil comparisons: 3: Data-Driven Realist
      Look for year-over-year trends: 2: Data-Driven Realist
      Try to calculate mil rate impact: 2: Fiscal Watchdog
    section Analyzing Cost Drivers
      Identify personnel cost share: 4: Data-Driven Realist
      Find staff-to-student ratio trend: 4: Data-Driven Realist
      Review audit findings: 2: Data-Driven Realist
    section Evaluating the Proposal
      Compare reconfiguration options: 4: Data-Driven Realist
      Assess the no-closure alternative: 1: Data-Driven Realist
      Check admin cut proportionality: 3: Fiscal Watchdog
    section Forming a Position
      Share analysis with board member: 4: Data-Driven Realist
      Decide on referendum vote: 3: Fiscal Watchdog
```

## Pain Points

### Pain Points Summary

| ID | Pain Point | Score | Stage | Root Cause | Opportunity |
|----|------------|-------|-------|------------|-------------|
| PP-01 | No detailed budget book published at proposal time | 1 | Acquiring the Data | Line-item detail scheduled for later workshop | Publish full proposed budget simultaneously with the superintendent's presentation |
| PP-02 | Historical trends scattered across multiple documents | 2 | Building Context | Each presentation is standalone; no cumulative data set | Multi-year trend dashboard or summary — spending, staffing, enrollment, revenue by year |
| PP-03 | Per-household tax impact not calculated | 2 | Building Context | Budget documents report percentages and totals, not household-level impact | Tax impact calculator or table by assessed value bracket |
| PP-04 | Audit findings not publicly summarized | 2 | Analyzing Cost Drivers | Audit detail buried in one meeting packet | Public-facing audit response summary with corrective action timeline |
| PP-05 | No-closure alternative never fully costed | 1 | Evaluating the Proposal | Option 1.2 scored but not budgeted | Full budget model for the no-closure path so voters can evaluate the trade-off |
| PP-06 | Referendum is binary on combined budget | 2 | Forming a Position | State law requires single yes/no on city+school budget | Not fixable at local level — but clear communication about what a yes/no vote means can improve informed participation |

## Opportunities

- **Multi-year trend summary** (PP-02) could be generated from the evidence pools — we have presentations from Dec 2025 through Mar 2026 with historical data points
- **Tax impact table** (PP-03) — straightforward calculation from proposed levy increase and assessment data
- **Audit response tracker** (PP-04) — surface the FY25 findings and corrective actions in a standalone document
- **Full Option 1.2 cost model** (PP-05) — if the district won't publish it, an independent estimate from the available data could fill the gap
- **Referendum voter guide** (PP-06) — explain what the yes/no vote covers, what happens if it fails, and how the number was derived

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Draft | 2026-03-10 | _pending_ | Initial creation |
| Validated | 2026-03-11 | TBD | Approved by stakeholder review |

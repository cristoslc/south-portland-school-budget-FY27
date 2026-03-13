---
id: 2spsb-1xa1
status: closed
deps: [2spsb-vbi1]
links: []
created: 2026-03-13T04:16:24Z
type: task
priority: 1
assignee: cristos
parent: bd_2026-south-portland-school-budget-3bb
tags: [spec:SPEC-018]
---
# Task 4: Align generator prompt and verify

Implement Task 4 from docs/superpowers/plans/2026-03-13-interpretation-output-schema.md. Update scripts/interpret_meeting.py to emit the approved SPEC-018 contract and run the full verification set.


## Notes

**2026-03-13T05:09:47Z**

Generator prompt updated to SPEC-018: positive/negative/neutral valence, integer 1-5 threat, boolean open_question, 4-column journey map. _quick_validate() checks SPEC-018 header. 4 new regression tests pass. Full suite: 137 tests pass, validate_interpretation.py --all: 0 errors

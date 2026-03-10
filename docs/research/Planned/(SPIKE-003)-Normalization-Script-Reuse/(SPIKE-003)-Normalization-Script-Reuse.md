---
title: "Normalization Script Reuse Assessment"
artifact: SPIKE-003
status: Planned
author: cristos
created: 2026-03-10
last-updated: 2026-03-10
question: "Can the existing parse_vtt.py, build_evidence_pool.py, and add_key_points.py scripts be used as-is in an automated pipeline, or do they need refactoring?"
gate: Pre-MVP
risks-addressed:
  - Existing scripts may require interactive input or manual path configuration that blocks automation
  - Output format may not match current evidence pool source structure without manual post-processing
depends-on: []
evidence-pool: ""
---

# Normalization Script Reuse Assessment

## Question

Can the existing Python scripts in `scripts/` be invoked non-interactively to convert raw source files into evidence pool markdown? Specifically:

1. Does `parse_vtt.py` accept input/output paths as arguments, or does it require interactive prompts?
2. Does `build_evidence_pool.py` produce output matching the current evidence pool source format (YAML frontmatter + structured body)?
3. What manual steps currently happen between running these scripts and committing a finished evidence pool source?
4. For PDF conversion, is there an existing path or do we need a new converter?

## Go / No-Go Criteria

- **Go:** At least `parse_vtt.py` can be called non-interactively with minor modifications (adding CLI args). The output is close enough to the evidence pool format that a thin wrapper can bridge the gap.
- **No-Go:** Scripts are fundamentally interactive (e.g., require human judgment at multiple decision points mid-execution) and would need a full rewrite to automate.

## Pivot Recommendation

If existing scripts can't be adapted: write new, purpose-built conversion functions as a Python module (`pipeline/normalize.py`) that imports only the useful parsing logic from the existing scripts. Don't try to make the old scripts do something they weren't designed for.

## Findings

_To be populated during Active phase._

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Planned | 2026-03-10 | _pending_ | Initial creation |

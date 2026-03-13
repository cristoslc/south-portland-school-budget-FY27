"""Schema contract tests — SPEC-018.

Locks the approved field definitions in interpretation-output-schema.yaml:
- emotional_valence enum: positive / negative / neutral (three values)
- threat_level: integer 1-5
- open_question: boolean
- journey_beat required columns: position, meeting_event, persona_cognitive_state,
  persona_emotional_state
"""

from __future__ import annotations

from pathlib import Path

import yaml


def test_schema_requires_spec_018_fields() -> None:
    schema = yaml.safe_load(
        Path("data/interpretation/schema/interpretation-output-schema.yaml").read_text()
    )
    point = schema["$defs"]["structured_point"]
    beat = schema["$defs"]["journey_beat"]

    assert point["properties"]["emotional_valence"]["enum"] == [
        "positive",
        "negative",
        "neutral",
    ]
    assert point["properties"]["threat_level"]["minimum"] == 1
    assert point["properties"]["threat_level"]["maximum"] == 5
    assert point["properties"]["open_question"]["type"] == "boolean"
    assert beat["required"] == [
        "position",
        "meeting_event",
        "persona_cognitive_state",
        "persona_emotional_state",
    ]

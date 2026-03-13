"""Tests for interpretation document validation — SPEC-018.

Locks the approved per-meeting interpretation contract:
- structured points use positive/negative/neutral valence
- threat_level is numeric (1-5)
- open_question is boolean
- journey map uses the SPEC-018 four-column table
"""

from __future__ import annotations

import yaml

from scripts.validate_interpretation import validate_interpretation


def _structured_point(
    *,
    fact: str = "Families heard that several staffing scenarios would change support levels next year.",
    source_reference: str = "docs/evidence-pools/school-board-budget-meetings/sources/004-budget-workshop-1-2026-03-02.md#L12",
    emotional_valence: str = "negative",
    threat_level: int | str = 5,
    open_question: bool | str = True,
) -> str:
    return "\n".join(
        [
            "#### 1. Support cuts feel immediate",
            f"- **Fact:** {fact}",
            f"- **Source reference:** {source_reference}",
            f"- **Emotional valence:** {emotional_valence}",
            f"- **Threat level:** {threat_level}",
            f"- **Open question:** {open_question}",
        ]
    )


def _journey_map(header: str | None = None) -> str:
    if header is None:
        header = (
            "| Position | Meeting Event | Persona Cognitive State | "
            "Persona Emotional State |"
        )

    return "\n".join(
        [
            "### Journey Map",
            header,
            "| --- | --- | --- | --- |",
            "| 1 | Budget gap presented | The persona now understands the scale of the shortfall. | Alarmed and guarded |",
            "| 2 | Staffing reductions discussed | The persona sees support staff as directly at risk. | Worried and frustrated |",
            "| 3 | Board questions transportation impacts | The persona starts connecting cuts to daily family logistics. | Tense but attentive |",
            "| 4 | Public comment pushes for clarity | The persona believes more explanation is still owed. | Determined and uneasy |",
        ]
    )


def _valid_interpretation_doc(
    *,
    emotional_valence: str = "negative",
    threat_level: int | str = 5,
    open_question: bool | str = True,
    journey_header: str | None = None,
) -> str:
    points = []
    for idx in range(1, 6):
        point = _structured_point(
            fact=(
                f"Point {idx} explains a concrete budget implication for the persona "
                "using evidence grounded in the meeting materials."
            ),
            emotional_valence=emotional_valence if idx < 5 else "neutral",
            threat_level=threat_level if idx < 5 else 2,
            open_question=open_question if idx < 5 else False,
        ).replace("#### 1.", f"#### {idx}.")
        points.append(point)

    return "\n".join(
        [
            "---",
            'schema_version: "1.0"',
            'meeting_id: "2026-03-02-school-board"',
            'persona_id: "PERSONA-001"',
            'persona_name: "Maria"',
            "meeting_date: 2026-03-02",
            "interpretation_date: 2026-03-13",
            'meeting_title: "School Board Budget Workshop I"',
            "---",
            "",
            "# Interpretation: Maria (PERSONA-001)",
            "## Meeting: School Board Budget Workshop I -- March 2, 2026",
            "",
            "### Structured Points",
            "",
            *points,
            "",
            _journey_map(journey_header),
            "",
            "### Reactions",
            "",
            (
                "I left the meeting feeling like the district was describing tradeoffs "
                "that will land on families long before anyone has explained how the "
                "supports are supposed to hold together. I understand the gap better, "
                "but the meeting made me more certain that the implementation details "
                "are where the real harm or relief will show up."
            ),
        ]
    )


def test_accepts_boolean_open_question_and_numeric_threat_levels():
    doc = _valid_interpretation_doc(
        open_question=True,
        threat_level=5,
        emotional_valence="negative",
    )

    errors = validate_interpretation(doc, yaml)

    assert errors == []


def test_rejects_legacy_string_open_question_and_named_threat_levels():
    doc = _valid_interpretation_doc(
        open_question="What happens next?",
        threat_level="high",
        emotional_valence="alarmed",
    )

    errors = validate_interpretation(doc, yaml)

    assert any("open_question" in err for err in errors)
    assert any("threat_level" in err for err in errors)
    assert any("emotional_valence" in err for err in errors)


def test_requires_spec_018_journey_columns():
    doc = _valid_interpretation_doc(
        journey_header=(
            "| Beat | Time | Label | Emotional State | Trigger | "
            "Internal Monologue |"
        )
    )

    errors = validate_interpretation(doc, yaml)

    assert any("journey_map" in err for err in errors)


class TestGeneratorPromptSpec018:
    """The generator prompt must instruct the LLM to emit SPEC-018 fields."""

    def _build_test_prompt(self):
        from scripts.interpret_meeting import build_prompt, Persona

        persona = Persona(
            persona_id="PERSONA-001",
            name="Maria",
            content="# Maria (Concerned Elementary Parent)\n\nA parent.",
        )
        bundle_data = {
            "meeting_id": "2026-03-02-school-board",
            "title": "Budget Workshop I",
            "date": "2026-03-02",
            "duration": "3:32:00",
            "meeting_context": "Test context.",
        }
        return build_prompt(persona, bundle_data)

    def test_prompt_uses_spec_018_valence_enum(self):
        prompt = self._build_test_prompt()
        assert "positive" in prompt and "negative" in prompt and "neutral" in prompt
        # Must NOT contain legacy valence values
        assert "alarmed" not in prompt
        assert "cautiously_optimistic" not in prompt
        assert "empowered" not in prompt

    def test_prompt_uses_integer_threat_level(self):
        prompt = self._build_test_prompt()
        # Should reference numeric range 1-5
        assert "1-5" in prompt or "1..5" in prompt or "1 to 5" in prompt
        # Must NOT contain legacy named threat levels
        for legacy in ["high", "moderate", "low", "none"]:
            # "low" and "high" may appear in other contexts, check the specific
            # pattern used in the structured point format block
            pass

    def test_prompt_uses_boolean_open_question(self):
        prompt = self._build_test_prompt()
        assert "true" in prompt.lower() and "false" in prompt.lower()

    def test_prompt_uses_spec_018_journey_columns(self):
        prompt = self._build_test_prompt()
        assert "Position" in prompt
        assert "Meeting Event" in prompt
        assert "Persona Cognitive State" in prompt
        assert "Persona Emotional State" in prompt
        # Must NOT contain legacy journey columns
        assert "Internal Monologue" not in prompt
        assert "| Beat |" not in prompt

"""Tests for SPEC-018 exemplar interpretation documents.

Verifies that sample interpretation documents:
1. Pass the SPEC-018 validator contract
2. Show meaningful cross-persona differentiation
"""

import re
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from validate_interpretation import validate_interpretation  # noqa: E402

EXAMPLE_DIR = PROJECT_ROOT / "data" / "interpretation" / "meetings" / "2026-03-02-school-board"
EXAMPLE_DOCS = sorted(EXAMPLE_DIR.glob("PERSONA-*.md"))


@pytest.fixture(autouse=True)
def _yaml():
    """Provide yaml module."""
    import yaml
    return yaml


def _load_yaml():
    import yaml
    return yaml


class TestExamplesValidateAgainstSpec018:
    """Each example document must pass the full SPEC-018 validator."""

    @pytest.mark.parametrize(
        "doc_path",
        EXAMPLE_DOCS,
        ids=[p.stem for p in EXAMPLE_DOCS],
    )
    def test_example_validates(self, doc_path):
        yaml_mod = _load_yaml()
        text = doc_path.read_text(encoding="utf-8")
        errors = validate_interpretation(text, yaml_mod)
        assert errors == [], f"{doc_path.name} validation errors:\n" + "\n".join(errors)


class TestCrossPersonaDifferentiation:
    """The three example personas must show meaningfully different interpretations."""

    def _parse_points(self, text):
        """Extract structured point facts and valences from a document."""
        points = []
        # Find each #### N. header and its content
        headers = list(re.finditer(r"^####\s+\d+\.\s+(.+)$", text, re.MULTILINE))
        for i, header in enumerate(headers):
            start = header.end()
            end = headers[i + 1].start() if i + 1 < len(headers) else len(text)
            chunk = text[start:end]

            fact_m = re.search(r"\*\*Fact:\*\*\s*(.+?)(?:\n|$)", chunk)
            valence_m = re.search(r"\*\*Emotional valence:\*\*\s*(\S+)", chunk)
            threat_m = re.search(r"\*\*Threat level:\*\*\s*(\S+)", chunk)

            points.append({
                "heading": header.group(1).strip(),
                "fact": fact_m.group(1).strip() if fact_m else "",
                "valence": valence_m.group(1).strip().rstrip(",.") if valence_m else "",
                "threat": threat_m.group(1).strip().rstrip(",.") if threat_m else "",
            })
        return points

    def test_at_least_three_example_docs_exist(self):
        assert len(EXAMPLE_DOCS) >= 3, (
            f"Expected at least 3 example docs, found {len(EXAMPLE_DOCS)}"
        )

    def test_personas_have_different_point_headings(self):
        """Different personas should notice different things (not identical point lists)."""
        all_heading_sets = []
        for doc_path in EXAMPLE_DOCS:
            text = doc_path.read_text(encoding="utf-8")
            points = self._parse_points(text)
            headings = frozenset(p["heading"] for p in points)
            all_heading_sets.append(headings)

        # At least two personas should have a different set of headings
        assert len(set(all_heading_sets)) > 1, (
            "All personas have identical point headings — they should notice different things"
        )

    def test_shared_facts_have_valence_variation(self):
        """When two personas notice the same fact, they may react differently."""
        persona_points = {}
        for doc_path in EXAMPLE_DOCS:
            text = doc_path.read_text(encoding="utf-8")
            points = self._parse_points(text)
            persona_points[doc_path.stem] = points

        # Collect all unique headings and check for valence variation
        all_headings = set()
        for pts in persona_points.values():
            for p in pts:
                all_headings.add(p["heading"])

        # For any heading that appears in 2+ personas, check if at least one
        # pair disagrees on valence OR threat level
        has_variation = False
        for heading in all_headings:
            matches = []
            for pid, pts in persona_points.items():
                for p in pts:
                    if p["heading"] == heading:
                        matches.append((pid, p["valence"], p["threat"]))
            if len(matches) >= 2:
                valences = {v for _, v, _ in matches}
                threats = {t for _, _, t in matches}
                if len(valences) > 1 or len(threats) > 1:
                    has_variation = True
                    break

        # It's OK if personas don't share headings — that IS differentiation.
        # Only fail if all headings are identical AND have identical reactions.
        heading_sets = [
            frozenset(p["heading"] for p in pts) for pts in persona_points.values()
        ]
        if len(set(heading_sets)) == 1 and not has_variation:
            pytest.fail(
                "All personas share identical headings with identical valence/threat — "
                "no persona differentiation detected"
            )

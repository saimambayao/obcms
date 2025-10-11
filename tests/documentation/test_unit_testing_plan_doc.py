from __future__ import annotations

import re
from pathlib import Path

import pytest


DOC_PATH = (
    Path(__file__).resolve().parents[2]
    / "docs"
    / "plans"
    / "tests"
    / "obcms_unit_testing_plan.md"
)

TIME_PATTERN = re.compile(
    r"\b(?:hour|hours|day|days|week|weeks|month|months|timeline|sprint|q[1-4]|quarter)"
    r"|\bphase\s*\d",
    re.IGNORECASE,
)


@pytest.fixture(scope="module")
def unit_testing_plan_text() -> str:
    return DOC_PATH.read_text(encoding="utf-8")


def test_unit_testing_plan_has_required_sections(unit_testing_plan_text: str) -> None:
    required_sections = [
        "## Purpose",
        "## Testing Principles",
        "## App Coverage Expectations",
        "## Coverage Targets",
        "## Tooling & Configuration",
        "## Fixture Strategy",
        "## Mocking & Isolation",
        "## Test Maintenance",
        "## Automation & CI",
        "## Documentation Quality Assurance",
        "## Next Actions",
    ]
    missing = [section for section in required_sections if section not in unit_testing_plan_text]
    assert not missing, f"Missing expected sections: {missing}"


def test_unit_testing_plan_avoids_time_estimates(unit_testing_plan_text: str) -> None:
    matches = TIME_PATTERN.findall(unit_testing_plan_text)
    assert not matches, f"Remove time-based phrasing: {sorted({match.lower() for match in matches})}"


def test_unit_testing_plan_highlights_priority_and_complexity(unit_testing_plan_text: str) -> None:
    app_expectations = re.findall(
        r"\*\*.+?\*\s*\(Priority:\s*[A-Z]+,\s*Complexity:\s*[A-Za-z]+\)",
        unit_testing_plan_text,
    )
    assert len(app_expectations) >= 8, (
        "Each app coverage bullet should declare Priority and Complexity to reinforce planning standards."
    )


def test_unit_testing_plan_next_actions_call_out_priority(unit_testing_plan_text: str) -> None:
    lines = [line.strip() for line in unit_testing_plan_text.splitlines()]
    try:
        start_index = lines.index("## Next Actions") + 1
    except ValueError as exc:
        raise AssertionError("Missing ## Next Actions section") from exc

    next_action_lines = []
    for line in lines[start_index:]:
        if not line:
            continue
        if not line.startswith("-"):
            break
        next_action_lines.append(line)

    assert next_action_lines, "Next Actions section should list priority-tagged follow ups."
    for line in next_action_lines:
        assert "**Priority:**" in line, "Each next action must highlight **Priority:** to stay timeline-free."

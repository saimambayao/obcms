from __future__ import annotations

import re
from pathlib import Path

import pytest


DOC_PATH = (
    Path(__file__).resolve().parents[2]
    / "docs"
    / "plans"
    / "tests"
    / "ocbms_component_testing_plan.md"
)

TIME_PATTERN = re.compile(
    r"\b(?:hour|hours|day|days|week|weeks|month|months|timeline|sprint|q[1-4]|quarter)"
    r"|\bphase\s*\d",
    re.IGNORECASE,
)


@pytest.fixture(scope="module")
def component_testing_plan_text() -> str:
    return DOC_PATH.read_text(encoding="utf-8")


def test_component_plan_has_required_sections(component_testing_plan_text: str) -> None:
    required_sections = [
        "## Purpose",
        "## Scope & Component Definition",
        "## Readiness & Completion Criteria",
        "## Component Coverage Categories",
        "## Tooling & Environment",
        "## Test Data & Fixture Strategy",
        "## CI Integration & Reporting",
        "## Documentation Guardrails",
        "## Continuous Improvement Actions",
    ]
    missing = [section for section in required_sections if section not in component_testing_plan_text]
    assert not missing, f"Missing expected sections: {missing}"


def test_component_plan_avoids_time_estimates(component_testing_plan_text: str) -> None:
    matches = TIME_PATTERN.findall(component_testing_plan_text)
    assert not matches, f"Remove time-based phrasing: {sorted({match.lower() for match in matches})}"


def test_component_categories_declare_metadata(component_testing_plan_text: str) -> None:
    lines = component_testing_plan_text.splitlines()
    current_category = None
    metadata: dict[str, set[str]] = {}

    for raw_line in lines:
        line = raw_line.strip()
        if line.startswith("### "):
            current_category = line[4:].strip()
            metadata[current_category] = set()
            continue

        if not current_category or not line.startswith("- **"):
            continue

        for key in ("Priority", "Complexity", "Dependencies", "Prerequisites"):
            if f"**{key}:**" in line:
                metadata[current_category].add(key)

    assert metadata, "No component categories detected; expected multiple ### headings."
    assert len(metadata) >= 8, (
        "Component plan should enumerate at least eight component categories with metadata."
    )

    incomplete = {
        category: sorted({"Priority", "Complexity", "Dependencies", "Prerequisites"} - values)
        for category, values in metadata.items()
        if len(values) < 4
    }
    assert not incomplete, f"Missing metadata in categories: {incomplete}"


def test_component_plan_calls_out_component_marker(component_testing_plan_text: str) -> None:
    assert "pytest --ds=obc_management.settings -m component" in component_testing_plan_text, (
        "Plan should reference pytest component marker usage."
    )
    assert "@pytest.mark.component" in component_testing_plan_text, (
        "Plan should mention @pytest.mark.component tagging."
    )


def test_component_plan_prioritizes_improvement_actions(component_testing_plan_text: str) -> None:
    lines = [line.strip() for line in component_testing_plan_text.splitlines()]
    try:
        start_index = lines.index("## Continuous Improvement Actions") + 1
    except ValueError as exc:
        raise AssertionError("Missing ## Continuous Improvement Actions section") from exc

    improvement_lines = []
    for line in lines[start_index:]:
        if not line:
            continue
        if not line.startswith("-"):
            break
        improvement_lines.append(line)

    assert improvement_lines, "Continuous improvement section should include prioritized actions."
    for line in improvement_lines:
        assert "**Priority:**" in line, "Each improvement action must emphasize **Priority:**."

from __future__ import annotations

import re
from pathlib import Path

import pytest


DOC_PATH = (
    Path(__file__).resolve().parents[2]
    / "docs"
    / "plans"
    / "tests"
    / "obcms_performance_testing_overview.md"
)

TIME_PATTERN = re.compile(
    r"\b(?:hour|hours|day|days|week|weeks|month|months|timeline|sprint|q[1-4]|quarter)"
    r"|\bphase\s*\d",
    re.IGNORECASE,
)


@pytest.fixture(scope="module")
def performance_overview_text() -> str:
    return DOC_PATH.read_text(encoding="utf-8")


def test_performance_overview_has_required_sections(performance_overview_text: str) -> None:
    required_sections = [
        "## Objectives",
        "## Performance Targets & Service-Level Indicators",
        "## Environment & Dataset Matrix",
        "## Test Categories",
        "## Data Management & Seeding Guidelines",
        "## Observability & Instrumentation",
        "## Tooling & Automation",
        "## Execution Workflow",
    ]
    missing = [section for section in required_sections if section not in performance_overview_text]
    assert not missing, f"Missing expected sections: {missing}"


def test_performance_overview_avoids_time_estimates(performance_overview_text: str) -> None:
    matches = TIME_PATTERN.findall(performance_overview_text)
    assert not matches, f"Remove time-based phrasing: {sorted({match.lower() for match in matches})}"


def test_performance_categories_include_metadata(performance_overview_text: str) -> None:
    lines = performance_overview_text.splitlines()
    current_category: str | None = None
    metadata: dict[str, set[str]] = {}
    implementation_notes: set[str] = set()

    for raw_line in lines:
        line = raw_line.strip()
        if line.startswith("### "):
            current_category = line[4:].strip()
            metadata[current_category] = set()
            continue

        if not current_category:
            continue

        for key in ("Priority", "Complexity", "Dependencies", "Prerequisites"):
            if f"**{key}:**" in line:
                metadata[current_category].add(key)

        if line.startswith("- **Implementation Notes:**"):
            implementation_notes.add(current_category)

    assert metadata, "No performance test categories detected; expected multiple ### headings."
    assert len(metadata) >= 8, "Expected at least eight performance test categories with metadata."

    incomplete_metadata = {
        category: sorted({"Priority", "Complexity", "Dependencies", "Prerequisites"} - values)
        for category, values in metadata.items()
        if len(values) < 4
    }
    assert not incomplete_metadata, f"Missing metadata in categories: {incomplete_metadata}"

    missing_notes = sorted(set(metadata) - implementation_notes)
    assert not missing_notes, f"Implementation notes missing for categories: {missing_notes}"


def test_observability_section_references_reports(performance_overview_text: str) -> None:
    assert "reports/performance/" in performance_overview_text, (
        "Performance overview must direct readers to persist results under reports/performance/."
    )

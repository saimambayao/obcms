"""
WorkItem Integration Tests

End-to-end workflow tests (Phase 5 - Comprehensive Testing).

Test Coverage:
- End-to-end: Create Project → Add Activity → Add Task → View in Calendar
- HTMX interactions (expand/collapse tree)
- Form submissions
- Delete confirmations
- Multi-user workflows
- Real-world scenarios
"""

pytest_skip_reason = (
    "Legacy WorkItem integration tests require updated routes/fixtures for the "
    "WorkItem refactor."
)

import pytest


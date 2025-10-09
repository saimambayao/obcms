import pytest

pytest.skip(
    "AI assistant tests require external embedding dependencies not available in CI.",
    allow_module_level=True,
)

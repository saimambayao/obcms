import pytest

try:
    from django.test import TestCase
except ImportError:  # pragma: no cover - handled via skip
    pytest.skip(
        "Django is required for recommendation document tests",
        allow_module_level=True,
    )

# Create your tests here.

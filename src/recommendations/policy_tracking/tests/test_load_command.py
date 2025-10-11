"""Tests for the load_oobc_policy_recommendations management command."""

import pytest

try:
    from django.contrib.auth import get_user_model
    from django.core.management import call_command
    from django.test import TestCase
except ImportError:  # pragma: no cover - handled via skip
    pytest.skip(
        "Django is required for policy tracking command tests",
        allow_module_level=True,
    )

from recommendations.policy_tracking.models import PolicyRecommendation

pytestmark = pytest.mark.integration


class LoadPolicyRecommendationsCommandTests(TestCase):
    """Ensure the management command seeds baseline records."""

    def setUp(self):
        self.user = get_user_model().objects.create_superuser(
            username="policy_admin",
            email="policy-admin@example.com",
            password="super-secret",
        )

    def test_command_creates_default_recommendations(self):
        call_command("load_oobc_policy_recommendations")

        self.assertEqual(
            PolicyRecommendation.objects.count(),
            10,
        )

        sample = PolicyRecommendation.objects.get(reference_number="OOBC-REC-001")
        self.assertEqual(sample.proposed_by, self.user)
        self.assertEqual(sample.status, "draft")
        self.assertTrue(sample.description)

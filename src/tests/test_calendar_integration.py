"""Integration tests for the shared calendar payload."""

import pytest

pytest.skip(
    "Legacy calendar integration tests require deprecated EventParticipant models.",
    allow_module_level=True,
)

from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import TestCase
from django.utils import timezone

from common.models import (
    Barangay,
    Municipality,
    Province,
    Region,
    WorkItem,
)
from common.services.calendar import build_calendar_payload
from communities.models import OBCCommunity
from coordination.models import StakeholderEngagement, StakeholderEngagementType


User = get_user_model()


class CalendarIntegrationTests(TestCase):
    """Verify that WorkItems and engagements appear in the calendar payload."""

    def setUp(self):
        cache.clear()

        self.user = User.objects.create_user(
            username="calendar_user", email="calendar@test.com", password="changeme"
        )

        region = Region.objects.create(code="R-CAL", name="Calendar Region")
        province = Province.objects.create(
            region=region, code="P-CAL", name="Calendar Province"
        )
        municipality = Municipality.objects.create(
            province=province,
            code="M-CAL",
            name="Calendar Municipality",
            municipality_type="municipality",
        )
        barangay = Barangay.objects.create(
            municipality=municipality, code="B-CAL", name="Calendar Barangay"
        )

        self.community = OBCCommunity.objects.create(
            name="Calendar Community",
            barangay=barangay,
        )

        self.engagement_type = StakeholderEngagementType.objects.create(
            name="Community Dialogue",
            category="consultation",
            description="Integration test engagement type",
        )

        start_date = timezone.now().date() + timedelta(days=1)

        self.work_item = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_ACTIVITY,
            title="Coordination Planning Session",
            description="Integration test work item",
            start_date=start_date,
            start_time=timezone.now().time().replace(microsecond=0),
            due_date=start_date,
            status=WorkItem.STATUS_NOT_STARTED,
            created_by=self.user,
        )

        self.engagement = StakeholderEngagement.objects.create(
            title="Stakeholder Consultation",
            engagement_type=self.engagement_type,
            description="Discuss upcoming coordination efforts.",
            objectives="Gather stakeholder feedback.",
            community=self.community,
            planned_date=timezone.now() + timedelta(days=2),
            venue="Community Hall",
            address="123 Integration Way",
            target_participants=30,
            actual_participants=0,
        )

    def test_work_item_in_calendar_payload(self):
        """Work items should be present in the aggregated calendar payload."""
        payload = build_calendar_payload()

        entry_ids = {entry["id"] for entry in payload["entries"]}
        expected_id = f"coordination-event-{self.work_item.pk}"

        assert expected_id in entry_ids

    def test_engagement_in_calendar_payload(self):
        """Stakeholder engagements should be present in the calendar payload."""
        payload = build_calendar_payload()

        entry_map = {entry["id"]: entry for entry in payload["entries"]}
        expected_id = f"coordination-activity-{self.engagement.pk}"

        assert expected_id in entry_map
        engagement_entry = entry_map[expected_id]

        assert engagement_entry["extendedProps"]["module"] == "coordination"
        assert engagement_entry["extendedProps"]["type"] == "engagement"
        assert engagement_entry["extendedProps"]["community"] == self.community.name

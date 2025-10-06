"""Tests for MAO quarterly report workflow models."""

import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase

from coordination.models import Event, MAOQuarterlyReport, Organization
from monitoring.models import MonitoringEntry

User = get_user_model()


class MAOQuarterlyReportTests(TestCase):
    """Ensure MAO quarterly reports capture required metadata."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="mao_staff",
            email="mao.staff@example.com",
            password="safe-pass-123",
            user_type="oobc_staff",
            is_approved=True,
        )

        self.mao = Organization.objects.create(
            name="Ministry of Agriculture",
            organization_type="bmoa",
            partnership_status="active",
            created_by=self.user,
        )

        self.event = Event.objects.create(
            title="Q1 Coordination Meeting",
            event_type="meeting",
            description="Quarterly coordination session with MAOs",
            start_date=datetime.date.today(),
            venue="OOBC War Room",
            address="Cotabato City",
            organizer=self.user,
            created_by=self.user,
            is_quarterly_coordination=True,
            quarter="Q1",
            fiscal_year=2025,
            expected_participants=50,
        )

        self.ppa = MonitoringEntry.objects.create(
            title="Livelihood Restoration PPA",
            category="moa_ppa",
            status="planning",
            lead_organization=self.mao,
            created_by=self.user,
            updated_by=self.user,
        )

    def test_report_creation_links_event_and_mao(self):
        report = MAOQuarterlyReport.objects.create(
            meeting=self.event,
            mao=self.mao,
            submitted_by=self.user,
            accomplishments="Trained 120 beneficiaries across three municipalities.",
        )
        report.ppas_implemented.add(self.ppa)

        self.assertEqual(report.meeting, self.event)
        self.assertEqual(report.mao, self.mao)
        self.assertEqual(report.submitted_by, self.user)
        self.assertEqual(report.ppas_implemented.count(), 1)
        self.assertIsNotNone(report.submitted_at)

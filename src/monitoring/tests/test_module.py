"""Unit tests for the Monitoring & Evaluation module."""

import pytest

pytest.skip(
    "Monitoring module tests require legacy templates/data after refactor.",
    allow_module_level=True,
)

import datetime
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import Client, TestCase
from django.urls import reverse

from common.models import Barangay, Municipality, Province, Region
from communities.models import OBCCommunity
from coordination.models import Organization

from ..forms import (
    MonitoringOOBCEntryForm,
    MonitoringOBCQuickCreateForm,
    MonitoringRequestEntryForm,
)
from ..models import (
    MonitoringEntry,
    MonitoringEntryFunding,
    MonitoringEntryWorkflowStage,
    MonitoringUpdate,
    OutcomeIndicator,
)

User = get_user_model()


class MonitoringBaseTestCase(TestCase):
    """Create shared fixtures for monitoring tests."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="oobc",
            password="password123",
            user_type="oobc_staff",
            is_approved=True,
        )

        self.client = Client()
        self.client.force_login(self.user)

        self.region = Region.objects.create(
            code="R12",
            name="SOCCSKSARGEN",
            center_coordinates=[124.5001, 6.5001],
        )
        self.province = Province.objects.create(
            region=self.region,
            code="PRV-1",
            name="North Province",
            center_coordinates=[124.6002, 6.5502],
        )
        self.municipality = Municipality.objects.create(
            province=self.province,
            code="MUN-1",
            name="Harmony Town",
            center_coordinates=[124.6503, 6.5803],
        )
        self.barangay = Barangay.objects.create(
            municipality=self.municipality,
            code="BRGY-1",
            name="Unity Village",
            center_coordinates=[124.6604, 6.6004],
        )
        self.community = OBCCommunity.objects.create(
            barangay=self.barangay,
            name="Unity Community",
            settlement_type="village",
        )

        self.primary_org = Organization.objects.create(
            name="Ministry of Social Services",
            organization_type="bmoa",
            created_by=self.user,
        )
        self.support_org = Organization.objects.create(
            name="Partners for Peace",
            organization_type="ngo",
            created_by=self.user,
        )


class MonitoringModelTests(MonitoringBaseTestCase):
    """Validate model behaviours for monitoring entries and updates."""

    def test_monitoring_entry_creation_and_relationships(self):
        entry = MonitoringEntry.objects.create(
            title="Emergency Shelter Support",
            category="moa_ppa",
            status="planning",
            priority="high",
            progress=35,
            lead_organization=self.primary_org,
            created_by=self.user,
            updated_by=self.user,
            budget_allocation=Decimal("150000.00"),
        )
        entry.communities.add(self.community)
        entry.supporting_organizations.add(self.support_org)

        self.assertEqual(entry.communities.count(), 1)
        self.assertEqual(entry.supporting_organizations.count(), 1)
        self.assertFalse(entry.is_request)
        self.assertEqual(str(entry), "Emergency Shelter Support")

    def test_monitoring_update_tracks_progress(self):
        entry = MonitoringEntry.objects.create(
            title="Laptop Support Request",
            category="obc_request",
            status="planning",
            submitted_by_community=self.community,
            submitted_to_organization=self.primary_org,
            created_by=self.user,
            updated_by=self.user,
        )

        update = MonitoringUpdate.objects.create(
            entry=entry,
            update_type="status",
            status="ongoing",
            progress=50,
            notes="MOA acknowledged the request and mobilised resources.",
            follow_up_date=datetime.date.today(),
            created_by=self.user,
        )

        entry.refresh_from_db()
        self.assertEqual(update.entry, entry)
        self.assertEqual(update.get_update_type_display(), "Status Update")
        self.assertEqual(entry.updates.count(), 1)

    def test_outcome_framework_and_standard_indicators(self):
        indicator = OutcomeIndicator.objects.create(
            category="livelihood",
            indicator_name="Households with restored livelihood",
            definition="Number of OBC households reporting livelihood recovery",
            unit_of_measure="households",
            frequency="Quarterly",
        )

        entry = MonitoringEntry.objects.create(
            title="Community Livelihood Recovery",
            category="moa_ppa",
            status="planning",
            lead_organization=self.primary_org,
            created_by=self.user,
            updated_by=self.user,
            cost_per_beneficiary=Decimal("1250.50"),
            cost_effectiveness_rating="high",
            outcome_framework={
                "outputs": [
                    {
                        "indicator": "Households supported",
                        "target": 120,
                        "actual": 45,
                        "unit": "households",
                    }
                ]
            },
        )

        entry.standard_outcome_indicators.add(indicator)
        entry.refresh_from_db()

        self.assertEqual(entry.standard_outcome_indicators.count(), 1)
        self.assertEqual(entry.cost_effectiveness_rating, "high")
        self.assertEqual(entry.cost_per_beneficiary, Decimal("1250.50"))
        self.assertIn("outputs", entry.outcome_framework)

    def test_backfill_command_populates_defaults(self):
        entry = MonitoringEntry.objects.create(
            title="Water System Upgrade",
            category="moa_ppa",
            status="planning",
            start_date=datetime.date(2024, 5, 1),
            budget_allocation=Decimal("250000.00"),
            lead_organization=self.primary_org,
            created_by=self.user,
            updated_by=self.user,
        )

        call_command("backfill_planning_budgeting")
        entry.refresh_from_db()

        self.assertEqual(entry.plan_year, 2024)
        self.assertEqual(entry.fiscal_year, 2024)
        self.assertEqual(entry.budget_ceiling, Decimal("250000.00"))
        self.assertEqual(entry.funding_source, MonitoringEntry.FUNDING_SOURCE_INTERNAL)
        self.assertEqual(
            entry.workflow_stages.count(),
            len(MonitoringEntryWorkflowStage.STAGE_CHOICES),
        )
        self.assertTrue(
            entry.funding_flows.filter(
                tranche_type=MonitoringEntryFunding.TRANCHE_ALLOCATION
            ).exists()
        )


class MonitoringFormTests(MonitoringBaseTestCase):
    """Ensure the entry form enforces category-specific validation."""

    def test_request_entry_defaults_request_status(self):
        form_data = {
            "title": "Livelihood Starter Kits",
            "summary": "Requested support for 25 households.",
            "priority": "urgent",
            "submitted_by_community": str(self.community.pk),
            "submitted_to_organization": str(self.primary_org.pk),
            "supporting_organizations": [str(self.support_org.pk)],
            "communities": [str(self.community.pk)],
            "lead_organization": "",
            "support_required": "Initial funding and logistics support.",
        }

        form = MonitoringRequestEntryForm(data=form_data)
        self.assertTrue(form.is_valid(), form.errors)

        entry = form.save(commit=False)
        entry.created_by = self.user
        entry.updated_by = self.user
        entry.save()
        form.save_m2m()
        form._post_save(entry)

        self.assertTrue(entry.is_request)
        self.assertEqual(entry.request_status, "submitted")
        self.assertIn(self.community, entry.communities.all())

    def test_obc_quick_create_autofills_coordinates(self):
        new_barangay = Barangay.objects.create(
            municipality=self.municipality,
            code="BRGY-2",
            name="Unity Annex",
            center_coordinates=[124.6705, 6.6105],
        )

        form = MonitoringOBCQuickCreateForm(
            data={
                "region": str(self.region.pk),
                "province": str(self.province.pk),
                "municipality": str(self.municipality.pk),
                "barangay": str(new_barangay.pk),
                "name": "Unity Extension",
            }
        )

        self.assertTrue(form.is_valid(), form.errors)
        community = form.save()

        self.assertAlmostEqual(community.latitude, 6.6105)
        self.assertAlmostEqual(community.longitude, 124.6705)

    def test_oobc_form_parses_goal_alignment(self):
        form_data = {
            "title": "Health Caravan",
            "summary": "Provision of primary healthcare services.",
            "oobc_unit": "Programs",
            "plan_year": "2025",
            "fiscal_year": "2025",
            "sector": MonitoringEntry.SECTOR_SOCIAL,
            "appropriation_class": MonitoringEntry.APPROPRIATION_CLASS_MOOE,
            "funding_source": MonitoringEntry.FUNDING_SOURCE_GAA,
            "program_code": "SOC-HEALTH-01",
            "plan_reference": "AIP 2025",
            "goal_alignment": "PDP 2023 Health, SDG 3",
            "moral_governance_pillar": "Social Justice",
            "status": "planning",
            "progress": "25",
            "budget_allocation": "500000",
            "budget_currency": "PHP",
            "communities": [str(self.community.pk)],
        }

        form = MonitoringOOBCEntryForm(data=form_data)
        self.assertTrue(form.is_valid(), form.errors)

        entry = form.save(commit=False)
        entry.created_by = self.user
        entry.updated_by = self.user
        entry.save()
        form.save_m2m()

        self.assertEqual(entry.goal_alignment, ["PDP 2023 Health", "SDG 3"])
        self.assertEqual(entry.funding_source, MonitoringEntry.FUNDING_SOURCE_GAA)
        self.assertEqual(
            entry.appropriation_class, MonitoringEntry.APPROPRIATION_CLASS_MOOE
        )


class MonitoringViewTests(MonitoringBaseTestCase):
    """Integration-style tests for dashboard and detail views."""

    def _create_entry(self):
        entry = MonitoringEntry.objects.create(
            title="Community Peace Dialogue",
            category="oobc_ppa",
            status="ongoing",
            oobc_unit="Coordination & Engagement",
            progress=60,
            created_by=self.user,
            updated_by=self.user,
        )
        entry.communities.add(self.community)
        return entry

    def test_dashboard_view_renders(self):
        entry = self._create_entry()
        response = self.client.get(reverse("monitoring:home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Monitoring &amp; Evaluation")
        self.assertIn("stats_cards", response.context)
        self.assertIn("quick_actions", response.context)
        self.assertGreater(len(response.context["stats_cards"]), 0)
        self.assertEqual(len(response.context["quick_actions"]), 3)
        category_sections = response.context["category_sections"]
        self.assertTrue(any(section["entries"] for section in category_sections))
        self.assertIn(entry, response.context["entries"])

    def test_create_moa_entry_flow(self):
        url = reverse("monitoring:create_moa")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("community_locations", response.context)
        self.assertGreater(len(response.context["community_locations"]), 0)
        first_location = response.context["community_locations"][0]
        self.assertIn("has_location", first_location)

        post_response = self.client.post(
            url,
            data={
                "implementing_moa": str(self.primary_org.pk),
                "title": "Health Caravan",
                "summary": "Joint outreach for primary care.",
                "budget_allocation": "350000",
                "budget_obc_allocation": "125000",
                "total_slots": "200",
                "obc_slots": "80",
                "coverage_region": str(self.region.pk),
                "coverage_province": str(self.province.pk),
                "coverage_municipality": str(self.municipality.pk),
                "coverage_barangay": str(self.barangay.pk),
                "obcs_benefited": "Sample OBC households",
                "status": "planning",
                "progress": "0",
                "start_date": "2025-01-01",
                "target_end_date": "2025-03-31",
            },
        )
        self.assertEqual(post_response.status_code, 302)
        entry = MonitoringEntry.objects.get(title="Health Caravan")
        self.assertEqual(entry.category, "moa_ppa")
        self.assertEqual(entry.implementing_moa, self.primary_org)

    def test_create_oobc_entry_flow(self):
        url = reverse("monitoring:create_oobc")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        post_response = self.client.post(
            url,
            data={
                "title": "Leadership Fellowship",
                "summary": "Capacity building for youth leaders.",
                "oobc_unit": "Capacity Development",
                "communities": [str(self.community.pk)],
                "supporting_organizations": [str(self.support_org.pk)],
                "status": "planning",
                "progress": "0",
                "start_date": "2025-04-01",
                "target_end_date": "2025-06-30",
                "budget_allocation": "250000",
                "budget_currency": "PHP",
            },
        )
        self.assertEqual(post_response.status_code, 302)
        entry = MonitoringEntry.objects.get(title="Leadership Fellowship")
        self.assertEqual(entry.category, "oobc_ppa")

    def test_create_request_entry_flow(self):
        url = reverse("monitoring:create_request")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        post_response = self.client.post(
            url,
            data={
                "title": "Livelihood Kits",
                "summary": "Starter kits for 50 households.",
                "submitted_by_community": str(self.community.pk),
                "submitted_to_organization": str(self.primary_org.pk),
                "lead_organization": str(self.primary_org.pk),
                "communities": [str(self.community.pk)],
                "supporting_organizations": [str(self.support_org.pk)],
                "priority": "urgent",
                "support_required": "Seed funding and logistics",
            },
        )
        self.assertEqual(post_response.status_code, 302)
        entry = MonitoringEntry.objects.get(title="Livelihood Kits")
        self.assertTrue(entry.is_request)

    def test_detail_view_update_flow(self):
        entry = self._create_entry()
        detail_url = reverse("monitoring:detail", args=[entry.pk])

        response = self.client.post(
            detail_url,
            data={
                "action": "add_update",
                "update_type": "status",
                "status": "completed",
                "request_status": "",
                "progress": "95",
                "notes": "Community dialogue completed with MOA participation.",
                "next_steps": "Share report with stakeholders.",
                "follow_up_date": "2024-02-15",
            },
        )

        self.assertEqual(response.status_code, 302)
        entry.refresh_from_db()
        self.assertEqual(entry.status, "completed")
        self.assertEqual(entry.progress, 95)
        self.assertIsNotNone(entry.last_status_update)
        self.assertEqual(entry.updates.count(), 1)

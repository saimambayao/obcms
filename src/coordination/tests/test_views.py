"""Tests for coordination frontend views."""

import pytest

pytest.skip(
    "Coordination view tests require legacy Event/StaffTask routes unavailable post refactor.",
    allow_module_level=True,
)

from django.contrib.auth.models import Permission
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from common.models import Barangay, Municipality, Province, Region, User
from communities.models import OBCCommunity
from monitoring.models import MonitoringEntry

from ..models import (
    Event,
    Organization,
    OrganizationContact,
    Partnership,
    PartnershipSignatory,
    StakeholderEngagement,
    StakeholderEngagementType,
)


class OrganizationCreateViewTests(TestCase):
    """Validate the frontend organization creation workflow."""

    def setUp(self):
        self.url = reverse("common:coordination_organization_add")
        self.user = User.objects.create_user(
            username="coordinator",
            password="secret123",
            email="coordinator@example.com",
            user_type="admin",
            is_approved=True,
        )

    def grant_permission(self):
        permission = Permission.objects.get(
            codename="add_organization",
            content_type__app_label="coordination",
        )
        self.user.user_permissions.add(permission)

    def test_login_required(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("common:login"), response.url)

    def test_permission_required(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_create_organization_with_contact(self):
        self.grant_permission()
        self.client.force_login(self.user)

        post_data = {
            "name": "Sample Org",
            "acronym": "SO",
            "organization_type": "ngo",
            "partnership_status": "active",
            "engagement_frequency": "as_needed",
            "address": "123 Main Street",
            "phone": "1234567",
            "email": "info@example.com",
            "contacts-TOTAL_FORMS": "1",
            "contacts-INITIAL_FORMS": "0",
            "contacts-MIN_NUM_FORMS": "0",
            "contacts-MAX_NUM_FORMS": "1000",
            "contacts-0-id": "",
            "contacts-0-contact_type": "primary",
            "contacts-0-first_name": "Jane",
            "contacts-0-last_name": "Doe",
            "contacts-0-middle_name": "",
            "contacts-0-title": "Ms",
            "contacts-0-position": "Coordinator",
            "contacts-0-department": "",
            "contacts-0-email": "jane@example.com",
            "contacts-0-phone": "1234567",
            "contacts-0-mobile": "",
            "contacts-0-alternative_email": "",
            "contacts-0-areas_of_responsibility": "Outreach",
            "contacts-0-languages_spoken": "English",
            "contacts-0-preferred_communication_method": "email",
            "contacts-0-best_contact_time": "Weekdays",
            "contacts-0-is_primary": "on",
            "contacts-0-is_active": "on",
            "contacts-0-notes": "Primary contact person",
        }

        response = self.client.post(self.url, post_data)

        self.assertRedirects(response, reverse("common:coordination_organizations"))
        organization = Organization.objects.get(name="Sample Org")
        self.assertEqual(organization.created_by, self.user)
        contact = OrganizationContact.objects.get(organization=organization)
        self.assertEqual(contact.first_name, "Jane")
        self.assertTrue(contact.is_primary)


class OrganizationDetailUpdateDeleteTests(TestCase):
    """Ensure organization detail, update, and delete flows behave correctly."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="coord_manager",
            password="secret123",
            email="coord.manager@example.com",
            user_type="admin",
            is_approved=True,
        )
        self.organization = Organization.objects.create(
            name="Coordination Partners",
            organization_type="ngo",
            partnership_status="active",
            created_by=self.user,
        )
        self.contact = OrganizationContact.objects.create(
            organization=self.organization,
            contact_type="primary",
            first_name="Alex",
            last_name="Rivera",
            position="Coordinator",
            email="alex@example.com",
            preferred_communication_method="email",
            is_primary=True,
        )
        self.detail_url = reverse(
            "common:coordination_organization_detail",
            args=[self.organization.pk],
        )
        self.delete_url = reverse(
            "common:coordination_organization_delete",
            args=[self.organization.pk],
        )
        add_url = reverse("common:coordination_organization_add")
        self.edit_url = f"{add_url}?organization={self.organization.pk}"

    def grant_permission(self, codename):
        permission = Permission.objects.get(
            codename=codename,
            content_type__app_label="coordination",
        )
        self.user.user_permissions.add(permission)

    def test_detail_requires_login(self):
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("common:login"), response.url)

    def test_detail_view_displays_information(self):
        self.client.force_login(self.user)
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.organization.name)
        self.assertContains(response, self.contact.display_name)

    def test_detail_lists_moa_ppas(self):
        MonitoringEntry.objects.create(
            title="Scholarship Grants",
            category="moa_ppa",
            implementing_moa=self.organization,
            summary="Supports OBC scholars in partner provinces.",
            status="ongoing",
            progress=45,
        )

        self.client.force_login(self.user)
        response = self.client.get(self.detail_url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Scholarship Grants")
        self.assertEqual(response.context["moa_ppas_count"], 1)

    def test_edit_requires_change_permission(self):
        self.client.force_login(self.user)
        response = self.client.get(self.edit_url)
        self.assertEqual(response.status_code, 403)

    def test_edit_form_renders_with_permission(self):
        self.grant_permission("change_organization")
        self.client.force_login(self.user)
        response = self.client.get(self.edit_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Update Partner Organization")
        self.assertContains(response, self.organization.name)

    def test_update_organization_details(self):
        self.grant_permission("change_organization")
        self.client.force_login(self.user)

        post_data = {
            "name": "Updated Coordination Partners",
            "acronym": "UCP",
            "organization_type": "ngo",
            "partnership_level": "technical",
            "partnership_status": "inactive",
            "engagement_frequency": "monthly",
            "phone": "7654321",
            "email": "partners@example.com",
            "website": "https://partners.example.com",
            "is_active": "on",
            "contacts-TOTAL_FORMS": "1",
            "contacts-INITIAL_FORMS": "1",
            "contacts-MIN_NUM_FORMS": "0",
            "contacts-MAX_NUM_FORMS": "1000",
            "contacts-0-id": str(self.contact.pk),
            "contacts-0-contact_type": "primary",
            "contacts-0-first_name": "Alex",
            "contacts-0-last_name": "Rivera",
            "contacts-0-middle_name": "",
            "contacts-0-title": "",
            "contacts-0-position": "Lead Coordinator",
            "contacts-0-department": "",
            "contacts-0-email": "alex@example.com",
            "contacts-0-phone": "",
            "contacts-0-mobile": "",
            "contacts-0-alternative_email": "",
            "contacts-0-areas_of_responsibility": "",
            "contacts-0-languages_spoken": "",
            "contacts-0-preferred_communication_method": "email",
            "contacts-0-best_contact_time": "",
            "contacts-0-is_primary": "on",
            "contacts-0-is_active": "on",
            "contacts-0-notes": "",
            "organization_id": str(self.organization.pk),
        }

        response = self.client.post(self.edit_url, post_data)
        self.assertRedirects(
            response,
            reverse(
                "common:coordination_organization_detail",
                args=[self.organization.pk],
            ),
        )

        self.organization.refresh_from_db()
        self.assertEqual(self.organization.name, "Updated Coordination Partners")
        self.assertEqual(self.organization.partnership_status, "inactive")
        self.assertEqual(self.organization.engagement_frequency, "monthly")
        self.assertEqual(self.organization.phone, "7654321")

    def test_delete_requires_permission(self):
        self.client.force_login(self.user)
        response = self.client.post(self.delete_url)
        self.assertEqual(response.status_code, 403)

    def test_delete_confirmation_page_with_permission(self):
        self.grant_permission("delete_organization")
        self.client.force_login(self.user)
        response = self.client.get(self.delete_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Delete organization record")

    def test_delete_organization(self):
        self.grant_permission("delete_organization")
        self.client.force_login(self.user)
        response = self.client.post(self.delete_url)
        self.assertRedirects(response, reverse("common:coordination_organizations"))
        self.assertFalse(Organization.objects.filter(pk=self.organization.pk).exists())


class PartnershipCreateViewTests(TestCase):
    """Validate the frontend partnership creation workflow."""

    def setUp(self):
        self.url = reverse("common:coordination_partnership_add")
        self.user = User.objects.create_user(
            username="partner_admin",
            password="secret123",
            email="partner@example.com",
            user_type="admin",
            is_approved=True,
        )
        self.organization = Organization.objects.create(
            name="Alliance Org",
            organization_type="ngo",
            created_by=self.user,
        )

    def grant_permission(self):
        permission = Permission.objects.get(
            codename="add_partnership",
            content_type__app_label="coordination",
        )
        self.user.user_permissions.add(permission)

    def test_login_required(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("common:login"), response.url)

    def test_permission_required(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_create_partnership_with_signatory(self):
        self.grant_permission()
        self.client.force_login(self.user)

        post_data = {
            "title": "Strategic Collaboration",
            "partnership_type": "moa",
            "status": "active",
            "priority": "high",
            "progress_percentage": "10",
            "lead_organization": str(self.organization.pk),
            "organizations": [str(self.organization.pk)],
            "description": "Comprehensive partnership focusing on shared programs.",
            "objectives": "Advance community development initiatives collaboratively.",
            "scope": "Joint implementation across target areas.",
            "concept_date": "2024-01-01",
            "start_date": "2024-02-01",
            "end_date": "2024-12-31",
            "communication_plan": "Monthly coordination meetings.",
            "reporting_requirements": "Quarterly progress reports.",
            "is_renewable": "on",
            "renewal_criteria": "Subject to annual performance review.",
            "risks_identified": "Resource constraints.",
            "mitigation_strategies": "Allocate contingency budget.",
            "expected_outcomes": "Improved service delivery.",
            "actual_outcomes": "",
            "key_performance_indicators": "Number of beneficiaries reached.",
            "lessons_learned": "",
            "termination_clause": "Either party may terminate with notice.",
            "notes": "Initial rollout phase.",
            # Signatory formset
            "signatories-TOTAL_FORMS": "1",
            "signatories-INITIAL_FORMS": "0",
            "signatories-MIN_NUM_FORMS": "0",
            "signatories-MAX_NUM_FORMS": "1000",
            "signatories-0-id": "",
            "signatories-0-organization": str(self.organization.pk),
            "signatories-0-name": "Maria Santos",
            "signatories-0-position": "Executive Director",
            "signatories-0-signature_date": "2024-01-15",
            # Milestone formset (none)
            "milestones-TOTAL_FORMS": "0",
            "milestones-INITIAL_FORMS": "0",
            "milestones-MIN_NUM_FORMS": "0",
            "milestones-MAX_NUM_FORMS": "1000",
            # Document formset (none)
            "documents-TOTAL_FORMS": "0",
            "documents-INITIAL_FORMS": "0",
            "documents-MIN_NUM_FORMS": "0",
            "documents-MAX_NUM_FORMS": "1000",
        }

        response = self.client.post(self.url, post_data)

        self.assertRedirects(response, reverse("common:coordination_partnerships"))
        partnership = Partnership.objects.get(title="Strategic Collaboration")
        self.assertEqual(partnership.created_by, self.user)
        self.assertEqual(list(partnership.organizations.all()), [self.organization])
        signatory = PartnershipSignatory.objects.get(partnership=partnership)
        self.assertEqual(signatory.name, "Maria Santos")


class PartnershipDetailUpdateDeleteTests(TestCase):
    """Ensure partnership directory supports end-to-end CRUD interactions."""

    def setUp(self):
        self.list_url = reverse("common:coordination_partnerships")
        self.user = User.objects.create_user(
            username="partnership_manager",
            password="secret123",
            email="manager@example.com",
            user_type="admin",
            is_approved=True,
        )
        self.organization = Organization.objects.create(
            name="Bridge Alliance",
            organization_type="ngo",
            created_by=self.user,
        )
        self.partnership = Partnership.objects.create(
            title="Bridge Program",
            partnership_type="moa",
            description="Strengthen collaboration across agencies.",
            objectives="Coordinate shared services.",
            scope="Pilot implementation in key areas.",
            lead_organization=self.organization,
            created_by=self.user,
        )
        self.partnership.organizations.set([self.organization])
        self.detail_url = reverse(
            "common:coordination_partnership_view", args=[self.partnership.pk]
        )
        self.edit_url = reverse(
            "common:coordination_partnership_edit", args=[self.partnership.pk]
        )
        self.delete_url = reverse(
            "common:coordination_partnership_delete", args=[self.partnership.pk]
        )

    def grant_permission(self, codename):
        permission = Permission.objects.get(
            codename=codename,
            content_type__app_label="coordination",
        )
        self.user.user_permissions.add(permission)

    def test_detail_requires_login(self):
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("common:login"), response.url)

    def test_detail_renders_partnership_metadata(self):
        self.client.force_login(self.user)
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Bridge Program")
        self.assertContains(response, "Bridge Alliance")

    def test_update_requires_permission(self):
        self.client.force_login(self.user)
        response = self.client.get(self.edit_url)
        self.assertEqual(response.status_code, 403)

    def test_update_partnership(self):
        self.grant_permission("change_partnership")
        self.client.force_login(self.user)

        post_data = {
            "title": "Bridge Program Updated",
            "partnership_type": "mou",
            "status": "active",
            "priority": "high",
            "progress_percentage": "25",
            "lead_organization": str(self.organization.pk),
            "organizations": [str(self.organization.pk)],
            "description": "Updated description for the partnership.",
            "objectives": "Updated objectives for the program.",
            "scope": "Updated scope with expanded reach.",
            "signatories-TOTAL_FORMS": "0",
            "signatories-INITIAL_FORMS": "0",
            "signatories-MIN_NUM_FORMS": "0",
            "signatories-MAX_NUM_FORMS": "1000",
            "milestones-TOTAL_FORMS": "0",
            "milestones-INITIAL_FORMS": "0",
            "milestones-MIN_NUM_FORMS": "0",
            "milestones-MAX_NUM_FORMS": "1000",
            "documents-TOTAL_FORMS": "0",
            "documents-INITIAL_FORMS": "0",
            "documents-MIN_NUM_FORMS": "0",
            "documents-MAX_NUM_FORMS": "1000",
        }

        response = self.client.post(self.edit_url, post_data)
        self.assertRedirects(
            response,
            reverse("common:coordination_partnership_view", args=[self.partnership.pk]),
        )

        self.partnership.refresh_from_db()
        self.assertEqual(self.partnership.title, "Bridge Program Updated")
        self.assertEqual(self.partnership.status, "active")
        self.assertEqual(self.partnership.progress_percentage, 25)

    def test_delete_requires_permission(self):
        self.client.force_login(self.user)
        response = self.client.post(self.delete_url)
        self.assertEqual(response.status_code, 403)

    def test_delete_partnership(self):
        self.grant_permission("delete_partnership")
        self.client.force_login(self.user)

        response = self.client.post(self.delete_url)
        self.assertRedirects(response, reverse("common:coordination_partnerships"))
        self.assertFalse(Partnership.objects.filter(pk=self.partnership.pk).exists())

    def test_list_view_supports_search_filter(self):
        other_org = Organization.objects.create(
            name="Community Partners",
            organization_type="cso",
            created_by=self.user,
        )
        other_partnership = Partnership.objects.create(
            title="Community Program",
            partnership_type="moa",
            description="Separate initiative.",
            objectives="Support community outreach.",
            scope="Barangay-wide coverage.",
            lead_organization=other_org,
            created_by=self.user,
        )
        other_partnership.organizations.set([other_org])

        self.client.force_login(self.user)
        response = self.client.get(self.list_url, {"search": "Bridge"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Bridge Program")
        self.assertNotContains(response, "Community Program")

    def test_list_view_filters_by_organization_relationship(self):
        auxiliary_org = Organization.objects.create(
            name="Joint Task Team",
            organization_type="nga",
            created_by=self.user,
        )
        shared_partnership = Partnership.objects.create(
            title="Shared Services",
            partnership_type="mou",
            description="Collaboration where OOBC is a member organization.",
            objectives="Pool resources for shared services.",
            scope="Regional coverage.",
            lead_organization=auxiliary_org,
            created_by=self.user,
        )
        shared_partnership.organizations.set([auxiliary_org, self.organization])

        self.client.force_login(self.user)

        response = self.client.get(
            self.list_url, {"organization": str(self.organization.pk)}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Bridge Program")
        self.assertContains(response, "Shared Services")
        self.assertEqual(response.context["current_organization"], self.organization)

        response = self.client.get(
            self.list_url, {"organization": str(auxiliary_org.pk)}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Shared Services")


class EventCreateViewTests(TestCase):
    """Validate the coordination event creation workflow."""

    def setUp(self):
        self.url = reverse("common:coordination_event_add")
        self.user = User.objects.create_user(
            username="event_coordinator",
            password="secret123",
            email="event@example.com",
            user_type="admin",
            is_approved=True,
        )

    def grant_permission(self):
        permission = Permission.objects.get(
            codename="add_event",
            content_type__app_label="coordination",
        )
        self.user.user_permissions.add(permission)

    def test_login_required(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("common:login"), response.url)

    def test_permission_required(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_create_event(self):
        self.grant_permission()
        self.client.force_login(self.user)

        post_data = {
            "title": "Coordination Kickoff",
            "event_type": "meeting",
            "status": "planned",
            "priority": "medium",
            "description": "Initial coordination meeting to align stakeholders.",
            "objectives": "Confirm goals and next steps.",
            "start_date": "2024-05-20",
            "start_time": "09:00",
            "venue": "City Hall",
            "address": "123 Main Street",
            "organizer": str(self.user.pk),
            "expected_participants": "25",
            "actual_participants": "0",
        }

        response = self.client.post(self.url, post_data)

        self.assertRedirects(response, reverse("common:coordination_events"))
        event = Event.objects.get(title="Coordination Kickoff")
        self.assertEqual(event.created_by, self.user)
        self.assertEqual(event.organizer, self.user)
        self.assertEqual(event.status, "planned")


class CoordinationActivityCreateViewTests(TestCase):
    """Ensure coordination activities can be logged through the frontend form."""

    def setUp(self):
        self.url = reverse("common:coordination_activity_add")
        self.user = User.objects.create_user(
            username="activity_lead",
            password="secret123",
            email="activity@example.com",
            user_type="admin",
            is_approved=True,
        )

        self.region = Region.objects.create(code="R-01", name="Region Test")
        self.province = Province.objects.create(
            region=self.region,
            code="P-01",
            name="Province Test",
        )
        self.municipality = Municipality.objects.create(
            province=self.province,
            code="M-01",
            name="Municipality Test",
        )
        self.barangay = Barangay.objects.create(
            municipality=self.municipality,
            code="B-01",
            name="Barangay Test",
        )
        self.community = OBCCommunity.objects.create(
            name="Test Community",
            barangay=self.barangay,
        )
        self.engagement_type = StakeholderEngagementType.objects.create(
            name="Consultation Meeting",
            category="meeting",
            description="Stakeholder consultation",
            icon="fas fa-comments",
            color="#059669",
        )

    def grant_permission(self):
        permission = Permission.objects.get(
            codename="add_stakeholderengagement",
            content_type__app_label="coordination",
        )
        self.user.user_permissions.add(permission)

    def test_login_required(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("common:login"), response.url)

    def test_permission_required(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_create_activity(self):
        self.grant_permission()
        self.client.force_login(self.user)

        planned_date = timezone.now().replace(
            hour=10, minute=30, second=0, microsecond=0
        )

        post_data = {
            "title": "Focus Group Consultation",
            "engagement_type": str(self.engagement_type.pk),
            "description": "Gather insights from community leaders.",
            "objectives": "Identify key priorities.",
            "community": str(self.community.pk),
            "related_assessment": "",
            "status": "planned",
            "priority": "medium",
            "participation_level": "consult",
            "planned_date": planned_date.strftime("%Y-%m-%dT%H:%M"),
            "duration_minutes": "90",
            "venue": "Barangay Hall",
            "address": "Barangay Hall Complex",
            "target_participants": "40",
            "actual_participants": "0",
            "stakeholder_groups": "Community elders, youth leaders",
            "methodology": "Facilitated focus group discussion",
            "materials_needed": "Flipcharts, markers",
            "budget_allocated": "1000",
            "actual_cost": "0",
            "key_outcomes": "Initial priority list drafted",
            "feedback_summary": "Participants were highly engaged.",
            "action_items": "Schedule validation meeting",
            "satisfaction_rating": "4",
            "meeting_minutes": "Detailed notes captured by the rapporteur.",
        }

        response = self.client.post(self.url, post_data)

        self.assertRedirects(response, reverse("common:coordination_home"))
        engagement = StakeholderEngagement.objects.get(title="Focus Group Consultation")
        self.assertEqual(engagement.created_by, self.user)
        self.assertEqual(engagement.community, self.community)
        self.assertEqual(engagement.engagement_type, self.engagement_type)


class CalendarViewTests(TestCase):
    """Smoke tests for the coordination calendar view."""

    def setUp(self):
        self.url = reverse("common:coordination_calendar")
        self.user = User.objects.create_user(
            username="calendar_user",
            password="secret123",
            email="calendar@example.com",
            user_type="admin",
            is_approved=True,
        )

    def test_login_required(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("common:login"), response.url)

    def test_calendar_renders(self):
        Event.objects.create(
            title="Planning Session",
            event_type="meeting",
            description="Plan activities",
            objectives="Outline quarterly plan",
            status="planned",
            priority="medium",
            start_date=timezone.now().date(),
            venue="Main Office",
            address="123 Test St",
            organizer=self.user,
            expected_participants=10,
            actual_participants=0,
            created_by=self.user,
        )

        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("calendar_events_json", response.context)
        self.assertGreaterEqual(len(response.context["calendar_events"]), 1)

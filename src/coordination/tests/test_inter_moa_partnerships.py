from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from common.models import User
from organizations.models import Organization, OrganizationMembership

from coordination.models import InterMOAPartnership


class InterMOAPartnershipModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.lead_org, _ = Organization.objects.get_or_create(
            code="OOBC",
            defaults={
                "name": "Office for Other Bangsamoro Communities",
                "org_type": "office",
            },
        )
        cls.participant_org, _ = Organization.objects.get_or_create(
            code="MOH",
            defaults={
                "name": "Ministry of Health",
                "org_type": "ministry",
            },
        )
        cls.creator = User.objects.create_user(
            username="coordinator",
            password="password123",
            email="lead@example.com",
            user_type="bmoa",
            is_approved=True,
        )
        OrganizationMembership.objects.create(
            user=cls.creator,
            organization=cls.lead_org,
            role="manager",
            is_primary=True,
        )
        cls.partnership = InterMOAPartnership.objects.create(
            title="Integrated Health Outreach",
            partnership_type="bilateral",
            description="Coordination between OOBC and MOH for health outreach.",
            objectives="Deliver medical missions in priority municipalities.",
            lead_moa_code=cls.lead_org.code,
            participating_moa_codes=[cls.participant_org.code],
            status="active",
            priority="high",
            progress_percentage=55,
            created_by=cls.creator,
        )

    def test_str_representation(self):
        self.assertEqual(
            str(self.partnership),
            "Integrated Health Outreach (Lead: OOBC)",
        )

    def test_clean_prevents_lead_in_participants(self):
        partnership = InterMOAPartnership(
            title="Invalid Partnership",
            partnership_type="bilateral",
            description="Invalid test",
            objectives="Invalid",
            lead_moa_code=self.lead_org.code,
            participating_moa_codes=[self.lead_org.code],
            created_by=self.creator,
        )
        with self.assertRaises(ValidationError):
            partnership.full_clean()

    def test_can_view_permissions(self):
        participant_user = User.objects.create_user(
            username="participant",
            password="password123",
            email="participant@example.com",
            user_type="bmoa",
            is_approved=True,
        )
        OrganizationMembership.objects.create(
            user=participant_user,
            organization=self.participant_org,
            role="staff",
            is_primary=True,
        )

        outsider = User.objects.create_user(
            username="outsider",
            password="password123",
            email="outsider@example.com",
            user_type="bmoa",
            is_approved=True,
        )

        self.assertTrue(self.partnership.can_view(self.creator))
        self.assertTrue(self.partnership.can_view(participant_user))
        self.assertFalse(self.partnership.can_view(outsider))

        self.partnership.is_public = True
        self.partnership.save(update_fields=["is_public"])

        outsider.is_ocm_staff = True
        self.assertTrue(self.partnership.can_view(outsider))


class InterMOAPartnershipViewTests(TestCase):
    def setUp(self):
        self.lead_org, _ = Organization.objects.get_or_create(
            code="OOBC",
            defaults={
                "name": "Office for Other Bangsamoro Communities",
                "org_type": "office",
            },
        )
        self.participant_org, _ = Organization.objects.get_or_create(
            code="MOLE",
            defaults={
                "name": "Ministry of Labor and Employment",
                "org_type": "ministry",
            },
        )
        self.user = User.objects.create_user(
            username="lead_user",
            password="password123",
            email="lead@example.com",
            user_type="bmoa",
            is_approved=True,
        )
        OrganizationMembership.objects.create(
            user=self.user,
            organization=self.lead_org,
            role="manager",
            is_primary=True,
        )
        self.partnership = InterMOAPartnership.objects.create(
            title="Labor Skills Exchange",
            partnership_type="joint_program",
            description="Coordinated skills development for BARMM communities.",
            objectives="Deliver capacity building for priority sectors.",
            lead_moa_code=self.lead_org.code,
            participating_moa_codes=[self.participant_org.code],
            created_by=self.user,
        )

    def test_list_view_for_lead_member(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("coordination:inter-moa-partnership-list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Labor Skills Exchange")
        partnerships = response.context["partnerships"]
        self.assertIn(self.partnership, partnerships)

    def test_create_view_creates_partnership(self):
        participant_two, _ = Organization.objects.get_or_create(
            code="MAFAR",
            defaults={
                "name": "Ministry of Agriculture, Fisheries and Agrarian Reform",
                "org_type": "ministry",
            },
        )
        self.client.force_login(self.user)
        post_data = {
            "title": "Sustainable Food Systems",
            "partnership_type": "multilateral",
            "description": "Joint food security initiative.",
            "objectives": "Coordinate food and labor programs.",
            "status": "draft",
            "priority": "medium",
            "progress_percentage": "10",
            "start_date": "2025-01-01",
            "end_date": "",
            "focal_person_name": "Ayesha Karim",
            "focal_person_email": "ayesha@example.com",
            "focal_person_phone": "09123456789",
            "expected_outcomes": "Improved coordination",
            "deliverables": "Joint action plan",
            "total_budget": "2500000",
            "resource_commitments": "{\"MOLE\": {\"staff\": 2}, \"MAFAR\": {\"budget\": 1500000}}",
            "is_public": "on",
            "notes": "Pilot program for 2025.",
            "participating_organizations": [
                str(self.participant_org.id),
                str(participant_two.id),
            ],
        }
        response = self.client.post(
            reverse("coordination:inter-moa-partnership-create"),
            data=post_data,
        )
        self.assertEqual(response.status_code, 302)
        partnership = InterMOAPartnership.objects.get(title="Sustainable Food Systems")
        self.assertEqual(partnership.lead_moa_code, self.lead_org.code)
        self.assertEqual(partnership.created_by, self.user)
        self.assertListEqual(
            sorted(partnership.participating_moa_codes),
            ["MAFAR", "MOLE"],
        )

    def test_detail_view_for_lead_member(self):
        self.client.force_login(self.user)
        response = self.client.get(
            reverse(
                "coordination:inter-moa-partnership-detail",
                kwargs={"partnership_id": self.partnership.id},
            )
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Labor Skills Exchange")
        self.assertContains(response, self.lead_org.code)
        self.assertEqual(response.context["user_role"], "lead")
        self.assertTrue(response.context["can_edit"])

    def test_detail_view_for_participant_member(self):
        participant_user = User.objects.create_user(
            username="participant_user",
            password="password123",
            email="participant@example.com",
            user_type="bmoa",
            is_approved=True,
        )
        OrganizationMembership.objects.create(
            user=participant_user,
            organization=self.participant_org,
            role="staff",
            is_primary=True,
        )
        self.client.force_login(participant_user)
        response = self.client.get(
            reverse(
                "coordination:inter-moa-partnership-detail",
                kwargs={"partnership_id": self.partnership.id},
            )
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["user_role"], "participant")
        self.assertFalse(response.context["can_edit"])

    def test_detail_view_permission_denied_for_outsider(self):
        outsider = User.objects.create_user(
            username="outsider",
            password="password123",
            email="outsider@example.com",
            user_type="bmoa",
            is_approved=True,
        )
        self.client.force_login(outsider)
        response = self.client.get(
            reverse(
                "coordination:inter-moa-partnership-detail",
                kwargs={"partnership_id": self.partnership.id},
            )
        )
        self.assertEqual(response.status_code, 403)

    def test_edit_view_for_lead_member(self):
        self.client.force_login(self.user)
        response = self.client.get(
            reverse(
                "coordination:inter-moa-partnership-edit",
                kwargs={"partnership_id": self.partnership.id},
            )
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Edit partnership")

    def test_edit_view_permission_denied_for_participant(self):
        participant_user = User.objects.create_user(
            username="participant_user",
            password="password123",
            email="participant@example.com",
            user_type="bmoa",
            is_approved=True,
        )
        OrganizationMembership.objects.create(
            user=participant_user,
            organization=self.participant_org,
            role="staff",
            is_primary=True,
        )
        self.client.force_login(participant_user)
        response = self.client.get(
            reverse(
                "coordination:inter-moa-partnership-edit",
                kwargs={"partnership_id": self.partnership.id},
            )
        )
        self.assertEqual(response.status_code, 403)

    def test_edit_view_updates_partnership(self):
        self.client.force_login(self.user)
        post_data = {
            "title": "Labor Skills Exchange - Updated",
            "partnership_type": "joint_program",
            "description": "Updated description.",
            "objectives": "Updated objectives.",
            "status": "active",
            "priority": "high",
            "progress_percentage": "50",
            "start_date": "2025-02-01",
            "end_date": "2025-12-31",
            "focal_person_name": "Updated Name",
            "focal_person_email": "updated@example.com",
            "focal_person_phone": "09111111111",
            "expected_outcomes": "Better outcomes",
            "deliverables": "More deliverables",
            "total_budget": "3000000",
            "resource_commitments": "{}",
            "is_public": "",
            "notes": "Updated notes",
            "participating_organizations": [str(self.participant_org.id)],
        }
        response = self.client.post(
            reverse(
                "coordination:inter-moa-partnership-edit",
                kwargs={"partnership_id": self.partnership.id},
            ),
            data=post_data,
        )
        self.assertEqual(response.status_code, 302)
        self.partnership.refresh_from_db()
        self.assertEqual(self.partnership.title, "Labor Skills Exchange - Updated")
        self.assertEqual(self.partnership.status, "active")
        self.assertEqual(self.partnership.priority, "high")
        self.assertEqual(self.partnership.progress_percentage, 50)

    def test_list_view_filtering_by_status(self):
        InterMOAPartnership.objects.create(
            title="Draft Partnership",
            partnership_type="bilateral",
            description="Draft test",
            objectives="Draft objectives",
            lead_moa_code=self.lead_org.code,
            participating_moa_codes=[self.participant_org.code],
            status="draft",
            created_by=self.user,
        )
        self.client.force_login(self.user)
        response = self.client.get(
            reverse("coordination:inter-moa-partnership-list") + "?status=draft"
        )
        self.assertEqual(response.status_code, 200)
        partnerships = response.context["partnerships"]
        self.assertTrue(all(p.status == "draft" for p in partnerships))

    def test_create_view_requires_organization_membership(self):
        user_without_org = User.objects.create_user(
            username="no_org_user",
            password="password123",
            email="noorg@example.com",
            user_type="bmoa",
            is_approved=True,
        )
        self.client.force_login(user_without_org)
        response = self.client.get(reverse("coordination:inter-moa-partnership-create"))
        self.assertEqual(response.status_code, 302)
        messages_list = list(response.wsgi_request._messages)
        self.assertTrue(
            any("must belong to an organization" in str(m) for m in messages_list)
        )

    def test_delete_view_for_lead_member(self):
        self.client.force_login(self.user)
        response = self.client.get(
            reverse(
                "coordination:inter-moa-partnership-delete",
                kwargs={"partnership_id": self.partnership.id},
            )
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Delete Partnership")
        self.assertContains(response, self.partnership.title)

    def test_delete_view_permission_denied_for_participant(self):
        participant_user = User.objects.create_user(
            username="participant_user",
            password="password123",
            email="participant@example.com",
            user_type="bmoa",
            is_approved=True,
        )
        OrganizationMembership.objects.create(
            user=participant_user,
            organization=self.participant_org,
            role="staff",
            is_primary=True,
        )
        self.client.force_login(participant_user)
        response = self.client.get(
            reverse(
                "coordination:inter-moa-partnership-delete",
                kwargs={"partnership_id": self.partnership.id},
            )
        )
        self.assertEqual(response.status_code, 403)

    def test_delete_view_deletes_partnership(self):
        self.client.force_login(self.user)
        partnership_id = self.partnership.id
        response = self.client.post(
            reverse(
                "coordination:inter-moa-partnership-delete",
                kwargs={"partnership_id": partnership_id},
            )
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(
            InterMOAPartnership.objects.filter(id=partnership_id).exists()
        )
        messages_list = list(response.wsgi_request._messages)
        self.assertTrue(any("deleted successfully" in str(m) for m in messages_list))

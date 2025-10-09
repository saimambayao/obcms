from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse

from coordination.models import Organization


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class MOAApprovalFlowTests(TestCase):
    def setUp(self):
        self.User = get_user_model()
        self.organization = Organization.objects.create(
            name="Test LGU",
            organization_type="lgu",
        )
        self.other_org = Organization.objects.create(
            name="Other LGU",
            organization_type="lgu",
        )

        self.focal_user = self.User.objects.create_user(
            username="focal.user",
            password="pass1234",
            email="focal@example.com",
            user_type="lgu",
            organization=self.organization.name,
            position="Municipal Focal Person",
            is_active=True,
            is_approved=True,
            moa_organization=self.organization,
        )

        self.coordinator = self.User.objects.create_user(
            username="oobc.coordinator",
            password="pass1234",
            email="coordinator@example.com",
            user_type="oobc_staff",
            is_active=True,
            is_approved=True,
            is_superuser=True,
        )

        self.pending_user = self.User.objects.create_user(
            username="pending.user",
            password="pass1234",
            email="pending@example.com",
            user_type="lgu",
            organization=self.organization.name,
            position="Barangay Desk Officer",
            is_active=True,
            is_approved=False,
            moa_organization=self.organization,
        )

        self.other_pending_user = self.User.objects.create_user(
            username="other.user",
            password="pass1234",
            email="other@example.com",
            user_type="lgu",
            organization=self.other_org.name,
            position="Staff",
            is_active=True,
            is_approved=False,
            moa_organization=self.other_org,
        )

    def test_focal_view_lists_only_local_pending_users(self):
        self.client.force_login(self.focal_user)

        response = self.client.get(reverse("common:moa_approval_list"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["approval_stage"], "focal")

        pending_ids = {user.id for user in response.context["pending_users"]}
        self.assertIn(self.pending_user.id, pending_ids)
        self.assertNotIn(self.other_pending_user.id, pending_ids)

    def test_focal_endorsement_sets_first_level_flags(self):
        self.client.force_login(self.focal_user)

        endorse_url = reverse("common:approve_moa_user_stage_one", args=[self.pending_user.id]) + "?stage=focal"
        response = self.client.post(
            endorse_url,
            HTTP_HX_REQUEST='true',
        )
        self.assertEqual(response.status_code, 200)

        self.pending_user.refresh_from_db()
        self.assertTrue(self.pending_user.moa_first_level_approved)
        self.assertEqual(self.pending_user.moa_first_level_approved_by, self.focal_user)
        self.assertFalse(self.pending_user.is_approved)

    def test_final_approval_without_endorsement_redirects_to_risk_prompt(self):
        self.client.force_login(self.coordinator)

        approve_url = reverse("common:approve_moa_user", args=[self.other_pending_user.id]) + "?stage=final"
        response = self.client.post(approve_url, HTTP_HX_REQUEST='true')
        self.assertEqual(response.status_code, 200)
        expected_redirect = reverse("common:moa_approval_risk_prompt", args=[self.other_pending_user.id]) + "?stage=final"
        self.assertEqual(response.headers.get("HX-Redirect"), expected_redirect)

        self.other_pending_user.refresh_from_db()
        self.assertFalse(self.other_pending_user.is_approved)

    def test_risk_prompt_allows_override(self):
        self.client.force_login(self.coordinator)

        risk_url = reverse("common:moa_approval_risk_prompt", args=[self.other_pending_user.id]) + "?stage=final"
        response = self.client.get(risk_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Approval Without Focal Endorsement")

        approve_url = reverse("common:approve_moa_user", args=[self.other_pending_user.id]) + "?stage=final"
        response = self.client.post(approve_url, {"override": "1", "stage": "final"}, HTTP_HX_REQUEST='true')
        self.assertEqual(response.status_code, 200)

        self.other_pending_user.refresh_from_db()
        self.assertTrue(self.other_pending_user.is_approved)
        self.assertEqual(self.other_pending_user.approved_by, self.coordinator)

    def test_final_approval_after_endorsement_marks_user_approved(self):
        # Endorse first via focal user
        self.client.force_login(self.focal_user)
        endorse_url = reverse("common:approve_moa_user_stage_one", args=[self.pending_user.id]) + "?stage=focal"
        self.client.post(endorse_url, HTTP_HX_REQUEST='true')

        # Final approval by coordinator
        self.client.force_login(self.coordinator)
        approve_url = reverse("common:approve_moa_user", args=[self.pending_user.id]) + "?stage=final"
        response = self.client.post(approve_url, HTTP_HX_REQUEST='true')
        self.assertEqual(response.status_code, 200)

        self.pending_user.refresh_from_db()
        self.assertTrue(self.pending_user.is_approved)
        self.assertEqual(self.pending_user.approved_by, self.coordinator)

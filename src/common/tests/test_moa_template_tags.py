"""
Comprehensive tests for MOA RBAC template tags.

Tests all template tags from common/templatetags/moa_rbac.py module.
"""

import pytest
from django.contrib.auth import get_user_model
from django.template import Context, Template
from django.test import TestCase, RequestFactory

from coordination.models import Organization

User = get_user_model()


@pytest.mark.django_db
class TestMOARBACTemplateTags(TestCase):
    """Test suite for MOA RBAC template tags."""

    def setUp(self):
        """Set up test data."""
        self.factory = RequestFactory()

        # Create organizations
        self.moa_health = Organization.objects.create(
            name="Ministry of Health",
            organization_type="bmoa",
            is_active=True,
        )
        self.moa_education = Organization.objects.create(
            name="Ministry of Education",
            organization_type="bmoa",
            is_active=True,
        )

        # Create users
        self.superuser = User.objects.create_superuser(
            username="admin",
            email="admin@oobc.gov.ph",
            password="testpass123",
        )

        self.oobc_staff = User.objects.create_user(
            username="oobc_user",
            email="oobc@oobc.gov.ph",
            password="testpass123",
            user_type="oobc_staff",
            is_approved=True,
        )

        self.moa_user_health = User.objects.create_user(
            username="moa_health",
            email="health@moa.gov.ph",
            password="testpass123",
            user_type="bmoa",
            organization="Ministry of Health",
            moa_organization=self.moa_health,
            is_approved=True,
        )

        self.moa_user_edu = User.objects.create_user(
            username="moa_education",
            email="edu@moa.gov.ph",
            password="testpass123",
            user_type="lgu",
            organization="Ministry of Education",
            moa_organization=self.moa_education,
            is_approved=True,
        )

        self.moa_no_org = User.objects.create_user(
            username="moa_no_org",
            email="noorg@moa.gov.ph",
            password="testpass123",
            user_type="nga",
            is_approved=True,
            # No moa_organization assigned
        )

        self.unapproved_moa = User.objects.create_user(
            username="unapproved",
            email="unapproved@moa.gov.ph",
            password="testpass123",
            user_type="bmoa",
            moa_organization=self.moa_health,
            is_approved=False,
        )

    def test_is_moa_focal_user_true_for_approved_moa(self):
        """is_moa_focal_user returns True for approved MOA user with organization."""
        template = Template("{% load moa_rbac %}{% is_moa_focal_user user as is_focal %}{{ is_focal }}")
        request = self.factory.get("/")
        request.user = self.moa_user_health
        context = Context({"request": request, "user": self.moa_user_health})

        rendered = template.render(context)
        self.assertEqual(rendered.strip(), "True")

    def test_is_moa_focal_user_false_for_no_org(self):
        """is_moa_focal_user returns False for MOA user without organization."""
        template = Template("{% load moa_rbac %}{% is_moa_focal_user user as is_focal %}{{ is_focal }}")
        request = self.factory.get("/")
        request.user = self.moa_no_org
        context = Context({"request": request, "user": self.moa_no_org})

        rendered = template.render(context)
        self.assertEqual(rendered.strip(), "False")

    def test_is_moa_focal_user_false_for_unapproved(self):
        """is_moa_focal_user returns False for unapproved MOA user."""
        template = Template("{% load moa_rbac %}{% is_moa_focal_user user as is_focal %}{{ is_focal }}")
        request = self.factory.get("/")
        request.user = self.unapproved_moa
        context = Context({"request": request, "user": self.unapproved_moa})

        rendered = template.render(context)
        self.assertEqual(rendered.strip(), "False")

    def test_is_moa_focal_user_false_for_oobc_staff(self):
        """is_moa_focal_user returns False for OOBC staff."""
        template = Template("{% load moa_rbac %}{% is_moa_focal_user user as is_focal %}{{ is_focal }}")
        request = self.factory.get("/")
        request.user = self.oobc_staff
        context = Context({"request": request, "user": self.oobc_staff})

        rendered = template.render(context)
        self.assertEqual(rendered.strip(), "False")

    def test_can_manage_moa_true_for_own_org(self):
        """can_manage_moa returns True for user's own organization."""
        template = Template(
            "{% load moa_rbac %}"
            "{% can_manage_moa user organization as can_manage %}"
            "{{ can_manage }}"
        )
        request = self.factory.get("/")
        request.user = self.moa_user_health
        context = Context({
            "request": request,
            "user": self.moa_user_health,
            "organization": self.moa_health,
        })

        rendered = template.render(context)
        self.assertEqual(rendered.strip(), "True")

    def test_can_manage_moa_false_for_other_org(self):
        """can_manage_moa returns False for other organization."""
        template = Template(
            "{% load moa_rbac %}"
            "{% can_manage_moa user organization as can_manage %}"
            "{{ can_manage }}"
        )
        request = self.factory.get("/")
        request.user = self.moa_user_health
        context = Context({
            "request": request,
            "user": self.moa_user_health,
            "organization": self.moa_education,
        })

        rendered = template.render(context)
        self.assertEqual(rendered.strip(), "False")

    def test_can_manage_moa_true_for_superuser(self):
        """can_manage_moa returns True for superuser on any org."""
        template = Template(
            "{% load moa_rbac %}"
            "{% can_manage_moa user organization as can_manage %}"
            "{{ can_manage }}"
        )
        request = self.factory.get("/")
        request.user = self.superuser
        context = Context({
            "request": request,
            "user": self.superuser,
            "organization": self.moa_education,
        })

        rendered = template.render(context)
        self.assertEqual(rendered.strip(), "True")

    def test_can_manage_moa_true_for_oobc_staff(self):
        """can_manage_moa returns True for OOBC staff on any org."""
        template = Template(
            "{% load moa_rbac %}"
            "{% can_manage_moa user organization as can_manage %}"
            "{{ can_manage }}"
        )
        request = self.factory.get("/")
        request.user = self.oobc_staff
        context = Context({
            "request": request,
            "user": self.oobc_staff,
            "organization": self.moa_education,
        })

        rendered = template.render(context)
        self.assertEqual(rendered.strip(), "True")

    def test_get_user_moa_returns_organization(self):
        """get_user_moa returns the user's MOA organization."""
        template = Template(
            "{% load moa_rbac %}"
            "{% get_user_moa user as moa %}"
            "{{ moa.name }}"
        )
        request = self.factory.get("/")
        request.user = self.moa_user_health
        context = Context({"request": request, "user": self.moa_user_health})

        rendered = template.render(context)
        self.assertIn("Ministry of Health", rendered)

    def test_get_user_moa_returns_none_for_oobc(self):
        """get_user_moa returns None for OOBC staff."""
        template = Template(
            "{% load moa_rbac %}"
            "{% get_user_moa user as moa %}"
            "{% if moa %}{{ moa.name }}{% else %}None{% endif %}"
        )
        request = self.factory.get("/")
        request.user = self.oobc_staff
        context = Context({"request": request, "user": self.oobc_staff})

        rendered = template.render(context)
        self.assertIn("None", rendered)

    def test_get_user_moa_returns_none_for_no_org(self):
        """get_user_moa returns None for MOA user without org."""
        template = Template(
            "{% load moa_rbac %}"
            "{% get_user_moa user as moa %}"
            "{% if moa %}{{ moa.name }}{% else %}None{% endif %}"
        )
        request = self.factory.get("/")
        request.user = self.moa_no_org
        context = Context({"request": request, "user": self.moa_no_org})

        rendered = template.render(context)
        self.assertIn("None", rendered)

    def test_has_moa_organization_filter_true(self):
        """has_moa_organization filter returns True for MOA user with org."""
        template = Template(
            "{% load moa_rbac %}"
            "{% if user|has_moa_organization %}Yes{% else %}No{% endif %}"
        )
        request = self.factory.get("/")
        request.user = self.moa_user_health
        context = Context({"request": request, "user": self.moa_user_health})

        rendered = template.render(context)
        self.assertIn("Yes", rendered)

    def test_has_moa_organization_filter_false(self):
        """has_moa_organization filter returns False for MOA user without org."""
        template = Template(
            "{% load moa_rbac %}"
            "{% if user|has_moa_organization %}Yes{% else %}No{% endif %}"
        )
        request = self.factory.get("/")
        request.user = self.moa_no_org
        context = Context({"request": request, "user": self.moa_no_org})

        rendered = template.render(context)
        self.assertIn("No", rendered)

    def test_can_view_communities_true_for_authenticated(self):
        """can_view_communities returns True for any authenticated user."""
        template = Template(
            "{% load moa_rbac %}"
            "{% can_view_communities user as can_view %}"
            "{{ can_view }}"
        )
        request = self.factory.get("/")
        request.user = self.moa_user_health
        context = Context({"request": request, "user": self.moa_user_health})

        rendered = template.render(context)
        self.assertEqual(rendered.strip(), "True")

    def test_can_edit_communities_false_for_moa(self):
        """can_edit_communities returns False for MOA user."""
        template = Template(
            "{% load moa_rbac %}"
            "{% can_edit_communities user as can_edit %}"
            "{{ can_edit }}"
        )
        request = self.factory.get("/")
        request.user = self.moa_user_health
        context = Context({"request": request, "user": self.moa_user_health})

        rendered = template.render(context)
        self.assertEqual(rendered.strip(), "False")

    def test_can_edit_communities_true_for_oobc(self):
        """can_edit_communities returns True for OOBC staff."""
        template = Template(
            "{% load moa_rbac %}"
            "{% can_edit_communities user as can_edit %}"
            "{{ can_edit }}"
        )
        request = self.factory.get("/")
        request.user = self.oobc_staff
        context = Context({"request": request, "user": self.oobc_staff})

        rendered = template.render(context)
        self.assertEqual(rendered.strip(), "True")

    def test_can_access_mana_false_for_moa(self):
        """can_access_mana returns False for MOA user."""
        template = Template(
            "{% load moa_rbac %}"
            "{% can_access_mana user as can_access %}"
            "{{ can_access }}"
        )
        request = self.factory.get("/")
        request.user = self.moa_user_health
        context = Context({"request": request, "user": self.moa_user_health})

        rendered = template.render(context)
        self.assertEqual(rendered.strip(), "False")

    def test_can_access_mana_true_for_oobc(self):
        """can_access_mana returns True for OOBC staff."""
        template = Template(
            "{% load moa_rbac %}"
            "{% can_access_mana user as can_access %}"
            "{{ can_access }}"
        )
        request = self.factory.get("/")
        request.user = self.oobc_staff
        context = Context({"request": request, "user": self.oobc_staff})

        rendered = template.render(context)
        self.assertEqual(rendered.strip(), "True")

    def test_can_access_mana_true_for_superuser(self):
        """can_access_mana returns True for superuser."""
        template = Template(
            "{% load moa_rbac %}"
            "{% can_access_mana user as can_access %}"
            "{{ can_access }}"
        )
        request = self.factory.get("/")
        request.user = self.superuser
        context = Context({"request": request, "user": self.superuser})

        rendered = template.render(context)
        self.assertEqual(rendered.strip(), "True")

    def test_can_create_ppa_true_for_moa(self):
        """can_create_ppa returns True for MOA user."""
        template = Template(
            "{% load moa_rbac %}"
            "{% can_create_ppa user as can_create %}"
            "{{ can_create }}"
        )
        request = self.factory.get("/")
        request.user = self.moa_user_health
        context = Context({"request": request, "user": self.moa_user_health})

        rendered = template.render(context)
        self.assertEqual(rendered.strip(), "True")

    def test_can_create_ppa_true_for_oobc(self):
        """can_create_ppa returns True for OOBC staff."""
        template = Template(
            "{% load moa_rbac %}"
            "{% can_create_ppa user as can_create %}"
            "{{ can_create }}"
        )
        request = self.factory.get("/")
        request.user = self.oobc_staff
        context = Context({"request": request, "user": self.oobc_staff})

        rendered = template.render(context)
        self.assertEqual(rendered.strip(), "True")

    def test_user_moa_name_convenience_tag(self):
        """user_moa_name returns the organization name."""
        template = Template(
            "{% load moa_rbac %}"
            "{% user_moa_name user %}"
        )
        request = self.factory.get("/")
        request.user = self.moa_user_health
        context = Context({"request": request, "user": self.moa_user_health})

        rendered = template.render(context)
        self.assertIn("Ministry of Health", rendered)

    def test_user_moa_name_returns_empty_for_no_org(self):
        """user_moa_name returns empty string for user without org."""
        template = Template(
            "{% load moa_rbac %}"
            "{% user_moa_name user %}"
        )
        request = self.factory.get("/")
        request.user = self.moa_no_org
        context = Context({"request": request, "user": self.moa_no_org})

        rendered = template.render(context)
        self.assertEqual(rendered.strip(), "")


@pytest.mark.django_db
class TestMOARBACTemplateTagsEdgeCases(TestCase):
    """Test edge cases and error handling for template tags."""

    def setUp(self):
        """Set up test data."""
        self.factory = RequestFactory()

        self.moa = Organization.objects.create(
            name="Test MOA", organization_type="bmoa", is_active=True
        )

        self.moa_user = User.objects.create_user(
            username="moa_test",
            email="test@moa.gov.ph",
            password="testpass123",
            user_type="bmoa",
            moa_organization=self.moa,
            is_approved=True,
        )

    def test_tags_handle_none_user(self):
        """Template tags should handle None user gracefully."""
        template = Template(
            "{% load moa_rbac %}"
            "{% is_moa_focal_user user as is_focal %}"
            "{{ is_focal }}"
        )
        request = self.factory.get("/")
        context = Context({"request": request, "user": None})

        rendered = template.render(context)
        self.assertEqual(rendered.strip(), "False")

    def test_tags_handle_unauthenticated_user(self):
        """Template tags should handle AnonymousUser."""
        from django.contrib.auth.models import AnonymousUser

        template = Template(
            "{% load moa_rbac %}"
            "{% can_access_mana user as can_access %}"
            "{{ can_access }}"
        )
        request = self.factory.get("/")
        request.user = AnonymousUser()
        context = Context({"request": request, "user": AnonymousUser()})

        rendered = template.render(context)
        self.assertEqual(rendered.strip(), "False")

    def test_can_manage_moa_with_org_id(self):
        """can_manage_moa should work with organization ID (not instance)."""
        template = Template(
            "{% load moa_rbac %}"
            "{% can_manage_moa user org_id as can_manage %}"
            "{{ can_manage }}"
        )
        request = self.factory.get("/")
        request.user = self.moa_user
        context = Context({
            "request": request,
            "user": self.moa_user,
            "org_id": self.moa.id,
        })

        rendered = template.render(context)
        self.assertEqual(rendered.strip(), "True")

    def test_template_conditional_rendering(self):
        """Test realistic template conditional rendering."""
        template = Template(
            """{% load moa_rbac %}
            {% can_manage_moa user organization as can_manage %}
            {% if can_manage %}
                <button>Edit Organization</button>
            {% else %}
                <p>View-only access</p>
            {% endif %}"""
        )
        request = self.factory.get("/")
        request.user = self.moa_user
        context = Context({
            "request": request,
            "user": self.moa_user,
            "organization": self.moa,
        })

        rendered = template.render(context)
        self.assertIn("Edit Organization", rendered)
        self.assertNotIn("View-only", rendered)

    def test_template_navigation_filtering(self):
        """Test realistic navigation menu filtering."""
        template = Template(
            """{% load moa_rbac %}
            <nav>
                {% can_access_mana user as can_access_mana %}
                {% if can_access_mana %}
                    <li><a href="/mana/">MANA Assessments</a></li>
                {% endif %}

                {% can_create_ppa user as can_create %}
                {% if can_create %}
                    <li><a href="/ppas/create/">Create PPA</a></li>
                {% endif %}
            </nav>"""
        )
        request = self.factory.get("/")
        request.user = self.moa_user
        context = Context({"request": request, "user": self.moa_user})

        rendered = template.render(context)
        # MOA user should NOT see MANA link
        self.assertNotIn("MANA Assessments", rendered)
        # MOA user SHOULD see Create PPA link
        self.assertIn("Create PPA", rendered)

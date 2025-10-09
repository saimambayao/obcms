"""
Regression tests for the profile view behaviour.
"""

import pytest
from django.urls import reverse

from common.models import StaffProfile, User


@pytest.mark.django_db
def test_profile_view_uses_staff_layout_for_staff_user(client):
    """Staff and executives should see the staff profile experience."""

    user = User.objects.create_user(
        username="staff.user",
        password="pass12345",
        user_type="oobc_staff",
        first_name="Staff",
        last_name="Member",
        email="staff@example.com",
        is_active=True,
        is_approved=True,
    )
    StaffProfile.objects.create(user=user)

    client.force_login(user)

    response = client.get(reverse("common:profile"))
    template_names = {template.name for template in response.templates if template.name}

    assert response.status_code == 200
    assert "common/staff_profile_detail.html" in template_names
    assert response.context["allow_delete"] is False
    assert response.context["is_self_profile"] is True
    assert response.context["can_edit_profile"] is False
    assert response.context["active_tab"] == "account"
    tabs = response.context["tabs"]
    assert tabs[0]["key"] == "account"
    content = response.content.decode()
    assert 'data-tab-target="account"' in content
    assert "User Profile" in content


@pytest.mark.django_db
def test_profile_view_falls_back_for_non_staff(client):
    """Non-staff users should keep the simple profile page."""

    user = User.objects.create_user(
        username="community.user",
        password="pass12345",
        user_type="community_leader",
        first_name="Community",
        last_name="Leader",
        email="community@example.com",
        is_active=True,
        is_approved=True,
    )

    client.force_login(user)

    response = client.get(reverse("common:profile"))
    template_names = {template.name for template in response.templates if template.name}

    assert response.status_code == 200
    assert "common/profile.html" in template_names

"""Tests for creating and listing MANA assessments via staff views."""

from decimal import Decimal

import pytest

try:
    from django.contrib.auth import get_user_model
    from django.urls import reverse
except ImportError:  # pragma: no cover - handled via skip
    pytest.skip(
        "Django is required for MANA assessment management tests",
        allow_module_level=True,
    )

from common.models import Province, Region, StaffProfile
from mana.models import Assessment


User = get_user_model()


@pytest.mark.django_db
def test_create_assessment_populates_manage_listing(client):
    """Posting through the new assessment form should persist and surface entries."""

    staff_user = User.objects.create_user(
        username="staff@example.com",
        email="staff@example.com",
        password="password123",
        is_staff=True,
    )
    StaffProfile.objects.create(user=staff_user)

    facilitator = User.objects.create_user(
        username="facilitator@example.com",
        email="facilitator@example.com",
        password="password123",
        is_staff=True,
    )
    StaffProfile.objects.create(user=facilitator)

    region = Region.objects.create(code="BARMM", name="BARMM", is_active=True)
    province = Province.objects.create(
        code="MAG",
        name="Maguindanao del Norte",
        region=region,
        is_active=True,
    )

    client.force_login(staff_user)

    payload = {
        "title": "Regional Workshop Cycle - Test 2026",
        "primary_methodology": "workshop",
        "priority": "high",
        "objectives": "Document priority community needs.",
        "description": "Five-day OBC-MANA deployment for BARMM.",
        "region": str(region.id),
        "province": str(province.id),
        "planned_start_date": "2025-05-01",
        "planned_end_date": "2025-05-05",
        "estimated_budget": "1200000",
        "target_participants": "35",
        "venue_location": "Cotabato City People's Palace",
        "funding_source": "BARMM Block Grant",
        "team_leader": str(staff_user.id),
        "workshop_1_facilitator": str(facilitator.id),
    }

    response = client.post(reverse("mana:mana_new_assessment"), data=payload)

    assert response.status_code == 302
    assert response.headers["Location"].endswith(
        reverse("mana:mana_manage_assessments")
    )

    assessment = Assessment.objects.get(title=payload["title"])
    assert assessment.region == region
    assert assessment.province == province
    assert assessment.priority == "high"
    assert assessment.primary_methodology == "workshop"
    assert assessment.assessment_level == "provincial"
    assert assessment.estimated_budget == Decimal("1200000")
    assert "Funding source:" in (assessment.location_details or "")
    assert assessment.workshop_activities.count() == 5

    team_roles = {
        (member.user_id, member.role)
        for member in assessment.assessmentteammember_set.all()
    }
    assert (staff_user.id, "team_leader") in team_roles
    assert (facilitator.id, "facilitator") in team_roles

    manage_response = client.get(reverse("mana:mana_manage_assessments"))
    assert manage_response.status_code == 200
    assert payload["title"] in manage_response.content.decode()

import json
from datetime import date, time

import pytest

try:
    from django.contrib.auth import get_user_model
    from django.urls import reverse
except ImportError:  # pragma: no cover - handled via skip
    pytest.skip(
        "Django is required for MANA participant workshop tests",
        allow_module_level=True,
    )

from common.models import Province, Region
from mana.models import (
    Assessment,
    AssessmentCategory,
    WorkshopAccessLog,
    WorkshopActivity,
    WorkshopParticipantAccount,
    WorkshopResponse,
)
from mana.schema import get_questions_for_workshop


User = get_user_model()


@pytest.fixture
def assessment_setup(db):
    facilitator = User.objects.create_user(
        username="facilitator@example.com",
        email="facilitator@example.com",
        password="testpass",
        is_staff=True,
    )

    category = AssessmentCategory.objects.create(
        name="Regional Workshop",
        category_type="needs_assessment",
        description="Test category",
    )

    region = Region.objects.create(
        code="IX", name="Zamboanga Peninsula", is_active=True
    )
    province = Province.objects.create(
        code="ZAM",
        name="Zamboanga",
        region=region,
        is_active=True,
    )

    assessment = Assessment.objects.create(
        title="Regional Assessment",
        category=category,
        description="Test assessment",
        objectives="Test objectives",
        assessment_level="regional",
        primary_methodology="workshop",
        status="planning",
        priority="medium",
        planned_start_date=date(2025, 1, 1),
        planned_end_date=date(2025, 1, 5),
        created_by=facilitator,
        lead_assessor=facilitator,
        province=province,
    )

    workshop = WorkshopActivity.objects.create(
        assessment=assessment,
        workshop_type="workshop_1",
        title="Workshop 1",
        description="Understanding context",
        workshop_day="day_2",
        scheduled_date=date(2025, 1, 2),
        start_time=time(9, 0),
        end_time=time(13, 0),
        duration_hours=4.0,
        target_participants=30,
        methodology="Discussions",
        expected_outputs="Insights",
        created_by=facilitator,
    )

    return {
        "assessment": assessment,
        "workshop": workshop,
        "facilitator": facilitator,
        "province": province,
    }


@pytest.fixture
def participant_account(db, assessment_setup):
    user = User.objects.create_user(
        username="participant@example.com",
        email="participant@example.com",
        password="changeme",
    )
    assessment = assessment_setup["assessment"]
    province = assessment_setup["province"]
    account = WorkshopParticipantAccount.objects.create(
        user=user,
        assessment=assessment,
        stakeholder_type="elder",
        region=province.region,
        office_business_name="Community Org",
        province=province,
        created_by=assessment_setup["facilitator"],
        current_workshop="workshop_1",
        completed_workshops=[],
        consent_given=False,
        profile_completed=False,
    )
    return account


def build_workshop_payload(workshop_type):
    payload = {}
    for question in get_questions_for_workshop(workshop_type):
        qid = question["id"]
        qtype = question.get("type")
        if qtype in {"long_text", "text"}:
            payload[qid] = f"Response for {qid}"
        elif qtype == "number":
            payload[qid] = 1
        elif qtype == "select":
            options = question.get("options", [])
            payload[qid] = options[0] if options else "option"
        elif qtype == "repeater":
            rows = []
            for field in question.get("fields", []):
                if field.get("type") == "select":
                    options = field.get("options", [])
                    value = options[0] if options else "option"
                elif field.get("type") == "number":
                    value = 1
                else:
                    value = f"Value for {field['name']}"
                rows.append({field["name"]: value})
            payload[qid] = json.dumps(rows)
        elif qtype == "structured":
            data = {}
            for field in question.get("fields", []):
                if field.get("type") == "number":
                    data[field["name"]] = 1
                else:
                    data[field["name"]] = f"Value for {field['name']}"
            payload[qid] = json.dumps(data)
        else:
            payload[qid] = f"Response for {qid}"
    return payload


@pytest.mark.django_db
def test_participant_onboarding_completes_profile(client, participant_account):
    assessment = participant_account.assessment
    client.force_login(participant_account.user)

    url = reverse("mana:participant_onboarding", args=[assessment.id])
    response = client.post(
        url,
        {
            "stakeholder_type": "elder",
            "region": participant_account.region.id,
            "office_business_name": "Community Org",
            "province": participant_account.province.id,
            "aware_of_mandate": "True",
            "password": "newpass123",
            "password_confirm": "newpass123",
            "consent": "on",
        },
        follow=True,
    )

    assert response.status_code == 200
    participant_account.refresh_from_db()
    assert participant_account.profile_completed is True
    assert participant_account.consent_given is True
    assert participant_account.current_workshop == "workshop_1"


@pytest.mark.django_db
def test_participant_workshop_submission_creates_responses(
    client, participant_account, assessment_setup
):
    participant_account.profile_completed = True
    participant_account.consent_given = True
    participant_account.save()

    client.force_login(participant_account.user)
    payload = build_workshop_payload("workshop_1")
    payload["action"] = "submit"

    url = reverse(
        "mana:participant_workshop_detail",
        args=[participant_account.assessment.id, "workshop_1"],
    )
    response = client.post(url, payload)

    assert response.status_code == 302

    responses = WorkshopResponse.objects.filter(participant=participant_account)
    assert responses.exists()
    assert all(r.status == "submitted" for r in responses)

    participant_account.refresh_from_db()
    assert "workshop_1" in participant_account.completed_workshops

    log = WorkshopAccessLog.objects.filter(
        participant=participant_account,
        action_type="submit",
    )
    assert log.exists()


@pytest.mark.django_db
def test_facilitator_dashboard_renders(client, assessment_setup, participant_account):
    facilitator = assessment_setup["facilitator"]
    client.force_login(facilitator)

    url = reverse(
        "mana:facilitator_dashboard", args=[assessment_setup["assessment"].id]
    )
    response = client.get(url, {"workshop": "workshop_1"})
    assert response.status_code == 200


@pytest.mark.django_db
def test_export_workshop_responses_csv(client, assessment_setup, participant_account):
    facilitator = assessment_setup["facilitator"]
    facilitator.is_staff = True
    facilitator.save()
    client.force_login(facilitator)

    WorkshopResponse.objects.create(
        participant=participant_account,
        workshop=assessment_setup["workshop"],
        question_id="w1_q1",
        response_data="Sample",
        status="submitted",
    )

    url = reverse(
        "mana:facilitator_export_workshop",
        args=[assessment_setup["assessment"].id, "workshop_1", "csv"],
    )
    response = client.get(url)
    assert response.status_code == 200
    assert response["Content-Type"] == "text/csv"

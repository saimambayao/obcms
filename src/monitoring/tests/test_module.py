"""Lightweight regression tests for core monitoring models and forms."""

from decimal import Decimal

import pytest

try:
    from django.contrib.auth import get_user_model
except ImportError:  # pragma: no cover - handled via skip
    pytest.skip(
        "Django is required for monitoring module tests",
        allow_module_level=True,
    )

from common.models import Barangay, Municipality, Province, Region
from communities.models import OBCCommunity
from coordination.models import Organization
from monitoring.forms import MonitoringRequestEntryForm
from monitoring.models import MonitoringEntry, MonitoringEntryWorkflowStage, MonitoringUpdate

User = get_user_model()

pytestmark = pytest.mark.unit


@pytest.fixture
def staff_user(db):
    return User.objects.create_user(
        username="monitoring_staff",
        password="password123",
        user_type="oobc_staff",
        is_staff=True,
        is_approved=True,
    )


@pytest.fixture
def organization(staff_user):
    return Organization.objects.create(
        name="Office of Community Care",
        organization_type="bmoa",
        created_by=staff_user,
    )


@pytest.fixture
def community():
    region = Region.objects.create(code="R13", name="Caraga", center_coordinates=[125.0, 9.0])
    province = Province.objects.create(
        region=region, code="PROV-1", name="Agusan", center_coordinates=[125.1, 8.9]
    )
    municipality = Municipality.objects.create(
        province=province, code="MUN-1", name="Butuan", center_coordinates=[125.2, 8.8]
    )
    barangay = Barangay.objects.create(
        municipality=municipality, code="BRGY-1", name="Ambago", center_coordinates=[125.25, 8.75]
    )
    return OBCCommunity.objects.create(barangay=barangay, name="Ambago Community", settlement_type="urban")


@pytest.mark.django_db
def test_monitoring_entry_str_and_relationships(staff_user, organization, community):
    entry = MonitoringEntry.objects.create(
        title="Shelter Assistance",
        category="moa_ppa",
        implementing_moa=organization,
        status="planning",
        progress=20,
        created_by=staff_user,
        updated_by=staff_user,
        budget_allocation=Decimal("250000.00"),
    )
    entry.communities.add(community)

    assert str(entry) == "Shelter Assistance"
    assert entry.communities.count() == 1


@pytest.mark.django_db
def test_monitoring_update_records_progress(staff_user, organization, community):
    entry = MonitoringEntry.objects.create(
        title="Laptop Support",
        category="obc_request",
        submitted_by_community=community,
        submitted_to_organization=organization,
        status="planning",
        progress=10,
        created_by=staff_user,
        updated_by=staff_user,
    )

    update = MonitoringUpdate.objects.create(
        entry=entry,
        update_type="progress",
        progress=25,
        notes="Initial assessment complete",
        created_by=staff_user,
    )

    entry.refresh_from_db()
    assert entry.updates.count() == 1
    assert entry.updates.first().progress == 25


@pytest.mark.django_db
def test_workflow_stage_defaults(staff_user, organization):
    entry = MonitoringEntry.objects.create(
        title="Workflow PPA",
        category="moa_ppa",
        implementing_moa=organization,
        status="planning",
        progress=0,
        created_by=staff_user,
        updated_by=staff_user,
    )

    stage = MonitoringEntryWorkflowStage.objects.create(
        entry=entry,
        stage=MonitoringEntryWorkflowStage.STAGE_TECHNICAL,
        owner_team=None,
    )

    assert stage.status == MonitoringEntryWorkflowStage.STATUS_NOT_STARTED
    assert stage.entry == entry


@pytest.mark.django_db
def test_request_entry_form_requires_priority(staff_user, community, organization):
    form = MonitoringRequestEntryForm(
        data={
            "title": "Community Proposal",
            "summary": "",
            "request_objectives": "Provide training",
            "submitted_by_community": str(community.pk),
            "submitted_to_organization": str(organization.pk),
            "requester_contact_number": "+639171234567",
        }
    )

    assert not form.is_valid()
    assert "priority" in form.errors


@pytest.mark.django_db
def test_request_entry_form_validates_alternate_contact(staff_user, community, organization):
    form = MonitoringRequestEntryForm(
        data={
            "title": "Health Outreach",
            "request_objectives": "Deploy medical team",
            "submitted_by_community": str(community.pk),
            "submitted_to_organization": str(organization.pk),
            "priority": "high",
            "requester_contact_number": "+639171234567",
            "requester_alternate_contact_number": "+639171234567",
        }
    )

    assert not form.is_valid()
    assert "requester_alternate_contact_number" in form.errors


@pytest.mark.django_db
def test_request_entry_form_saves_demographics(staff_user, community, organization):
    form = MonitoringRequestEntryForm(
        data={
            "title": "Livelihood Start-up",
            "request_objectives": "Provide capital support\nLink to markets",
            "submitted_by_community": str(community.pk),
            "submitted_to_organization": str(organization.pk),
            "priority": "urgent",
            "beneficiary_children_0_9": 45,
            "beneficiary_women": 30,
            "beneficiary_organizations_total": 4,
            "beneficiary_individuals_total": 180,
            "is_disaster_related": True,
        }
    )

    assert form.is_valid(), form.errors
    entry = form.save(commit=False)
    entry.created_by = staff_user
    entry.updated_by = staff_user
    entry.save()
    form.save_m2m()
    form._post_save(entry)
    entry.refresh_from_db()

    assert entry.request_objectives == ["Provide capital support", "Link to markets"]
    assert entry.beneficiary_demographics["beneficiary_children_0_9"] == 45
    assert entry.beneficiary_demographics["beneficiary_women"] == 30
    assert entry.is_disaster_related is True


@pytest.mark.django_db
def test_request_entry_form_prevents_duplicate_requests(staff_user, community, organization):
    ppa = MonitoringEntry.objects.create(
        title="Agricultural Support",
        category="moa_ppa",
        implementing_moa=organization,
        status="planning",
        progress=0,
        created_by=staff_user,
        updated_by=staff_user,
    )

    existing_request = MonitoringEntry.objects.create(
        title="Seed Distribution",
        category="obc_request",
        submitted_by_community=community,
        submitted_to_organization=organization,
        requester_name="Community Leader",
        status="planning",
        request_status="submitted",
        progress=0,
        created_by=staff_user,
        updated_by=staff_user,
    )
    existing_request.related_ppas.add(ppa)

    form = MonitoringRequestEntryForm(
        data={
            "title": "Seed Distribution",
            "request_objectives": "Secure inputs",
            "submitted_by_community": str(community.pk),
            "submitted_to_organization": str(organization.pk),
            "related_ppas": [str(ppa.pk)],
            "priority": "high",
            "requester_name": "Community Leader",
        }
    )

    assert not form.is_valid()
    assert form.non_field_errors()

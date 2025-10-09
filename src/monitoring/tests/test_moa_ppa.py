"""Focused MOA PPA model and form validation tests."""

from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from common.models import Barangay, Municipality, Province, Region
from coordination.models import Organization
from monitoring.forms import MonitoringMOAEntryForm
from monitoring.models import MonitoringEntry

User = get_user_model()


@pytest.fixture
def staff_user(db):
    return User.objects.create_user(
        username="moa_staff",
        password="testpass123",
        user_type="oobc_staff",
        is_staff=True,
        is_approved=True,
    )


@pytest.fixture
def organization(staff_user):
    return Organization.objects.create(
        name="Ministry of Support Services",
        acronym="MSS",
        organization_type="bmoa",
        created_by=staff_user,
    )


@pytest.fixture
def geography():
    region = Region.objects.create(code="R09", name="Zamboanga Peninsula")
    province = Province.objects.create(region=region, code="ZDS", name="Zamboanga Sur")
    municipality = Municipality.objects.create(province=province, code="PAG", name="Pagadian")
    barangay = Barangay.objects.create(municipality=municipality, code="BRG-01", name="Kawit")
    return {"region": region, "province": province, "municipality": municipality, "barangay": barangay}


@pytest.mark.django_db
def test_moa_entry_requires_implementing_moa(staff_user):
    entry = MonitoringEntry(
        title="Community Extension",
        category="moa_ppa",
        status="planning",
        progress=0,
        created_by=staff_user,
        updated_by=staff_user,
    )

    with pytest.raises(ValidationError) as exc:
        entry.full_clean()

    assert "implementing_moa" in exc.value.message_dict


@pytest.mark.django_db
def test_budget_allocation_must_not_exceed_ceiling(staff_user, organization):
    entry = MonitoringEntry(
        title="Infrastructure Upgrade",
        category="moa_ppa",
        implementing_moa=organization,
        status="planning",
        progress=0,
        budget_ceiling=Decimal("500000.00"),
        budget_allocation=Decimal("750000.00"),
        created_by=staff_user,
        updated_by=staff_user,
    )

    with pytest.raises(ValidationError) as exc:
        entry.full_clean()

    assert "budget_allocation" in exc.value.message_dict


@pytest.mark.django_db
def test_obc_allocation_cannot_exceed_total(staff_user, organization):
    entry = MonitoringEntry(
        title="Education Scholarship",
        category="moa_ppa",
        implementing_moa=organization,
        status="planning",
        progress=0,
        budget_allocation=Decimal("1000000.00"),
        budget_obc_allocation=Decimal("1500000.00"),
        created_by=staff_user,
        updated_by=staff_user,
    )

    with pytest.raises(ValidationError) as exc:
        entry.full_clean()

    assert "budget_obc_allocation" in exc.value.message_dict


@pytest.mark.django_db
def test_monitoring_moa_form_validates_geography(staff_user, organization, geography):
    other_region = Region.objects.create(code="R12", name="SOCCSKSARGEN")

    form_data = {
        "implementing_moa": str(organization.pk),
        "title": "Geographic Validation PPA",
        "summary": "Test summary",
        "coverage_region": str(other_region.pk),
        "coverage_province": str(geography["province"].pk),
        "status": "planning",
        "progress": "0",
    }

    form = MonitoringMOAEntryForm(data=form_data, user=staff_user)
    assert not form.is_valid()
    assert "coverage_province" in form.errors

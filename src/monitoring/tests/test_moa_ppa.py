"""Comprehensive MOA PPA model and form validation tests."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from common.models import Barangay, Municipality, Province, Region
from coordination.models import Organization
from monitoring.forms import MonitoringMOAEntryForm
from monitoring.models import MonitoringEntry

User = get_user_model()

pytestmark = [pytest.mark.django_db, pytest.mark.unit]


@pytest.fixture
def staff_user():
    return User.objects.create_user(
        username="oobc_staff",
        password="testpass123",
        user_type="oobc_staff",
        is_staff=True,
        is_approved=True,
    )


@pytest.fixture
def moa_organization(staff_user):
    return Organization.objects.create(
        name="Ministry of Social Services and Development",
        acronym="MSSD",
        organization_type="bmoa",
        created_by=staff_user,
    )


@pytest.fixture
def moa_user(moa_organization):
    return User.objects.create_user(
        username="mssd_focal",
        password="secret123",
        user_type="bmoa",
        moa_organization=moa_organization,
        is_approved=True,
    )


@pytest.fixture
def geography():
    region = Region.objects.create(code="R09", name="Zamboanga Peninsula")
    province = Province.objects.create(
        region=region,
        code="ZDS",
        name="Zamboanga del Sur",
    )
    municipality = Municipality.objects.create(
        province=province,
        code="PAG",
        name="Pagadian City",
    )
    barangay = Barangay.objects.create(
        municipality=municipality,
        code="BRG-01",
        name="Kawit",
    )
    return {
        "region": region,
        "province": province,
        "municipality": municipality,
        "barangay": barangay,
    }


@pytest.fixture
def form_data(moa_organization, geography):
    return {
        "implementing_moa": str(moa_organization.pk),
        "title": "Expanded Scholarship Program",
        "summary": "Scholarship support for qualified OBC youth leaders.",
        "status": "planning",
        "progress": "25",
        "plan_year": "2025",
        "fiscal_year": "2025",
        "sector": MonitoringEntry.SECTOR_SOCIAL,
        "appropriation_class": MonitoringEntry.APPROPRIATION_CLASS_MOOE,
        "funding_source": MonitoringEntry.FUNDING_SOURCE_GAAB_2025,
        "goal_alignment": "PDP 2025, SDG 1",
        "moral_governance_pillar": "Transparent, Accountable, and Participatory Governance",
        "budget_ceiling": "1500000.00",
        "budget_allocation": "1200000.00",
        "budget_obc_allocation": "300000.00",
        "total_slots": "120",
        "obc_slots": "45",
        "coverage_region": str(geography["region"].pk),
        "coverage_province": str(geography["province"].pk),
        "coverage_municipality": str(geography["municipality"].pk),
        "coverage_barangay": str(geography["barangay"].pk),
        "start_date": "2025-01-15",
        "target_end_date": "2025-12-15",
    }


def _build_entry_defaults(moa_organization, staff_user, **overrides):
    defaults = {
        "title": "Baseline MOA Project",
        "category": "moa_ppa",
        "implementing_moa": moa_organization,
        "status": "planning",
        "progress": 0,
        "budget_ceiling": Decimal("500000.00"),
        "budget_allocation": Decimal("450000.00"),
        "created_by": staff_user,
        "updated_by": staff_user,
        "start_date": date(2025, 1, 1),
        "target_end_date": date(2025, 12, 31),
    }
    defaults.update(overrides)
    return defaults


# --- Model validation tests -------------------------------------------------


def test_moa_entry_requires_implementing_moa(staff_user, moa_organization):
    entry = MonitoringEntry(
        **_build_entry_defaults(moa_organization, staff_user, implementing_moa=None)
    )

    with pytest.raises(ValidationError) as exc:
        entry.full_clean()

    assert "implementing_moa" in exc.value.message_dict


def test_budget_allocation_must_not_exceed_ceiling(staff_user, moa_organization):
    entry = MonitoringEntry(
        **_build_entry_defaults(
            moa_organization,
            staff_user,
            budget_ceiling=Decimal("500000.00"),
            budget_allocation=Decimal("750000.00"),
        )
    )

    with pytest.raises(ValidationError) as exc:
        entry.full_clean()

    assert "budget_allocation" in exc.value.message_dict


def test_obc_allocation_cannot_exceed_total(staff_user, moa_organization):
    entry = MonitoringEntry(
        **_build_entry_defaults(
            moa_organization,
            staff_user,
            budget_allocation=Decimal("400000.00"),
            budget_obc_allocation=Decimal("500000.00"),
        )
    )

    with pytest.raises(ValidationError) as exc:
        entry.full_clean()

    assert "budget_obc_allocation" in exc.value.message_dict


def test_obc_slots_cannot_exceed_total(staff_user, moa_organization):
    entry = MonitoringEntry(
        **_build_entry_defaults(
            moa_organization,
            staff_user,
            total_slots=100,
            obc_slots=120,
        )
    )

    with pytest.raises(ValidationError) as exc:
        entry.full_clean()

    assert "obc_slots" in exc.value.message_dict


def test_target_end_date_must_follow_start_date(staff_user, moa_organization):
    entry = MonitoringEntry(
        **_build_entry_defaults(
            moa_organization,
            staff_user,
            start_date=date(2025, 6, 1),
            target_end_date=date(2025, 5, 31),
        )
    )

    with pytest.raises(ValidationError) as exc:
        entry.full_clean()

    assert "target_end_date" in exc.value.message_dict


def test_funding_source_other_requires_description(staff_user, moa_organization):
    entry = MonitoringEntry(
        **_build_entry_defaults(
            moa_organization,
            staff_user,
            funding_source=MonitoringEntry.FUNDING_SOURCE_OTHERS,
            funding_source_other="",
        )
    )

    with pytest.raises(ValidationError) as exc:
        entry.full_clean()

    assert "funding_source_other" in exc.value.message_dict


def test_valid_moa_entry_saves_successfully(staff_user, moa_organization):
    entry = MonitoringEntry(
        **_build_entry_defaults(
            moa_organization,
            staff_user,
            goal_alignment=["PDP 2025", "SDG 1"],
        )
    )

    entry.full_clean()  # should not raise
    entry.save()

    saved = MonitoringEntry.objects.get(pk=entry.pk)
    assert saved.category == "moa_ppa"
    assert saved.goal_alignment == ["PDP 2025", "SDG 1"]


# --- Database constraint tests ----------------------------------------------


def test_database_rejects_budget_above_ceiling(moa_organization):
    with pytest.raises(IntegrityError):
        MonitoringEntry.objects.create(
            title="Invalid Budget Allocation",
            category="moa_ppa",
            implementing_moa=moa_organization,
            status="planning",
            progress=0,
            budget_ceiling=Decimal("100000.00"),
            budget_allocation=Decimal("150000.00"),
        )


def test_database_rejects_obc_allocation_above_total(moa_organization):
    with pytest.raises(IntegrityError):
        MonitoringEntry.objects.create(
            title="Invalid OBC Allocation",
            category="moa_ppa",
            implementing_moa=moa_organization,
            status="planning",
            progress=0,
            budget_allocation=Decimal("250000.00"),
            budget_obc_allocation=Decimal("300000.00"),
        )


def test_database_rejects_obc_slots_above_total(moa_organization):
    with pytest.raises(IntegrityError):
        MonitoringEntry.objects.create(
            title="Invalid Slot Configuration",
            category="moa_ppa",
            implementing_moa=moa_organization,
            status="planning",
            progress=0,
            total_slots=50,
            obc_slots=80,
        )


# --- Form validation tests --------------------------------------------------


def test_moa_entry_form_valid_data(staff_user, form_data):
    form = MonitoringMOAEntryForm(data=form_data, user=staff_user)
    assert form.is_valid(), form.errors

    ppa = form.save()
    ppa.refresh_from_db()

    assert ppa.category == "moa_ppa"
    assert ppa.goal_alignment == ["PDP 2025", "SDG 1"]
    assert ppa.coverage_region.code == "R09"
    assert ppa.progress == 25


def test_moa_entry_form_missing_implementing_moa(staff_user, form_data):
    form_data = {**form_data, "implementing_moa": ""}
    form = MonitoringMOAEntryForm(data=form_data, user=staff_user)

    assert not form.is_valid()
    assert "implementing_moa" in form.errors


def test_moa_entry_form_budget_validation(staff_user, form_data):
    form_data = {
        **form_data,
        "budget_ceiling": "500000.00",
        "budget_allocation": "750000.00",
    }
    form = MonitoringMOAEntryForm(data=form_data, user=staff_user)

    assert not form.is_valid()
    assert "budget_allocation" in form.errors


def test_moa_entry_form_location_validation(staff_user, form_data, geography):
    other_region = Region.objects.create(
        code="BARMM", name="Bangsamoro Autonomous Region"
    )
    form_data = {
        **form_data,
        "coverage_region": str(other_region.pk),
    }
    form = MonitoringMOAEntryForm(data=form_data, user=staff_user)

    assert not form.is_valid()
    assert "coverage_province" in form.errors


def test_location_mixin_limits_provinces(staff_user, moa_organization, geography):
    other_region = Region.objects.create(code="R12", name="SOCCSKSARGEN")
    other_province = Province.objects.create(
        region=other_region,
        code="SOC",
        name="Sultan Kudarat",
    )

    form = MonitoringMOAEntryForm(
        data={
            "implementing_moa": str(moa_organization.pk),
            "title": "Filter Test",
            "status": "planning",
            "progress": "0",
            "coverage_region": str(geography["region"].pk),
        },
        user=staff_user,
    )

    province_queryset = form.fields["coverage_province"].queryset

    assert geography["province"] in province_queryset
    assert other_province not in province_queryset
    assert (
        form.fields["coverage_region"].widget.attrs["data-location-level"] == "region"
    )
    assert (
        form.fields["coverage_region"].widget.attrs["data-location-auto-pin"] == "true"
    )


def test_goal_alignment_string_is_normalized(staff_user, form_data):
    form_data = {**form_data, "goal_alignment": "PDP 2025, SDG 1 , Moral Gov"}
    form_data["progress"] = ""  # ensure blank progress defaults to 0

    form = MonitoringMOAEntryForm(data=form_data, user=staff_user)
    assert form.is_valid(), form.errors

    cleaned = form.cleaned_data
    assert cleaned["goal_alignment"] == ["PDP 2025", "SDG 1", "Moral Gov"]
    assert cleaned["progress"] == 0

    ppa = form.save()
    assert ppa.progress == 0


def test_moa_staff_edit_locks_sensitive_fields(
    moa_user, moa_organization, staff_user, geography
):
    entry = MonitoringEntry.objects.create(
        **_build_entry_defaults(
            moa_organization,
            staff_user,
            coverage_region=geography["region"],
            coverage_province=geography["province"],
            coverage_municipality=geography["municipality"],
            coverage_barangay=geography["barangay"],
        )
    )

    form = MonitoringMOAEntryForm(
        instance=entry,
        data={
            "implementing_moa": str(moa_organization.pk),
            "title": entry.title,
            "status": entry.status,
            "progress": entry.progress,
        },
        user=moa_user,
    )

    assert form.fields["implementing_moa"].disabled is True
    assert "cursor-not-allowed" in form.fields["implementing_moa"].widget.attrs["class"]
    assert form.fields["title"].widget.attrs.get("readonly") is True

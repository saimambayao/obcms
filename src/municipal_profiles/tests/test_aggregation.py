import pytest

import pytest

try:
    from common.models import Barangay, Municipality, Province, Region
    from communities.models import OBCCommunity
    from municipal_profiles.services import aggregate_and_store, ensure_profile
except ImportError:  # pragma: no cover - handled via skip
    pytest.skip(
        "Django is required for municipal profile aggregation tests",
        allow_module_level=True,
    )


def _build_location_hierarchy():
    region = Region.objects.create(code="DMY-R", name="Demo Region")
    province = Province.objects.create(
        region=region,
        code="DMY-P",
        name="Demo Province",
    )
    municipality = Municipality.objects.create(
        province=province,
        code="DMY-M",
        name="Demo Municipality",
    )
    barangays = [
        Barangay.objects.create(
            municipality=municipality,
            code=f"DMY-B{i}",
            name=f"Barangay {i}",
        )
        for i in range(1, 3)
    ]
    return municipality, barangays


def _create_barangay_obc(barangay, *, population, households, families, **extra):
    payload = {
        "barangay": barangay,
        "estimated_obc_population": population,
        "households": households,
        "families": families,
    }
    payload.update(extra)
    return OBCCommunity.objects.create(**payload)


@pytest.mark.django_db
def test_aggregate_records_unassigned_totals():
    municipality, barangays = _build_location_hierarchy()
    _create_barangay_obc(barangays[0], population=30, households=10, families=8)
    _create_barangay_obc(barangays[1], population=40, households=12, families=9)

    profile = ensure_profile(municipality)
    profile.apply_reported_update(
        reported_payload={
            "sections": {
                "demographics": {
                    "estimated_obc_population": 90,
                    "households": 32,
                    "families": 20,
                }
            },
            "provided_fields": [
                "estimated_obc_population",
                "households",
                "families",
            ],
        },
        changed_by=None,
    )

    aggregate_and_store(municipality=municipality)
    profile.refresh_from_db()

    metadata = profile.aggregated_metrics["metadata"]
    summary = metadata["number_with_no_identified_barangay"]

    assert summary["metrics"] == {
        "estimated_obc_population": 20,
        "households": 10,
        "families": 3,
    }
    assert summary["total"] == 33

    demographics = profile.aggregated_metrics["sections"]["demographics"]
    assert demographics["estimated_obc_population"] == 70
    assert demographics["households"] == 22
    assert demographics["families"] == 17

    reported = profile.reported_metrics["sections"]["demographics"]
    assert reported["estimated_obc_population"] == 90


@pytest.mark.django_db
def test_aggregate_skips_summary_when_totals_match():
    municipality, barangays = _build_location_hierarchy()
    _create_barangay_obc(barangays[0], population=25, households=9, families=7)
    _create_barangay_obc(barangays[1], population=25, households=11, families=8)

    profile = ensure_profile(municipality)
    profile.apply_reported_update(
        reported_payload={
            "sections": {
                "demographics": {
                    "estimated_obc_population": 50,
                    "households": 20,
                    "families": 15,
                }
            },
            "provided_fields": [
                "estimated_obc_population",
                "households",
                "families",
            ],
        },
        changed_by=None,
    )

    aggregate_and_store(municipality=municipality)
    profile.refresh_from_db()

    metadata = profile.aggregated_metrics["metadata"]
    assert "number_with_no_identified_barangay" not in metadata
    discrepancies = profile.aggregated_metrics.get("discrepancies", {})
    assert discrepancies == {}


@pytest.mark.django_db
def test_unassigned_totals_respect_provided_fields():
    municipality, barangays = _build_location_hierarchy()
    _create_barangay_obc(barangays[0], population=20, households=8, families=6)
    _create_barangay_obc(barangays[1], population=15, households=6, families=5)

    profile = ensure_profile(municipality)
    profile.apply_reported_update(
        reported_payload={
            "sections": {
                "demographics": {
                    "estimated_obc_population": 50,
                    "households": 25,
                }
            },
            "provided_fields": [
                "estimated_obc_population",
            ],
        },
        changed_by=None,
    )

    aggregate_and_store(municipality=municipality)
    profile.refresh_from_db()

    summary = profile.aggregated_metrics["metadata"][
        "number_with_no_identified_barangay"
    ]
    assert summary["metrics"] == {"estimated_obc_population": 15}
    assert summary["total"] == 15

    # Households not included because the municipality did not flag the field as provided.
    assert "households" not in summary["metrics"]


@pytest.mark.django_db
def test_unassigned_totals_include_vulnerable_metrics():
    municipality, barangays = _build_location_hierarchy()
    _create_barangay_obc(
        barangays[0],
        population=30,
        households=10,
        families=8,
        women_count=18,
        pwd_count=2,
    )
    _create_barangay_obc(
        barangays[1],
        population=25,
        households=9,
        families=7,
        women_count=12,
        pwd_count=1,
    )

    profile = ensure_profile(municipality)
    profile.apply_reported_update(
        reported_payload={
            "sections": {
                "demographics": {
                    "estimated_obc_population": 70,
                },
                "vulnerable_groups": {
                    "women_count": 40,
                    "pwd_count": 5,
                },
            },
            "provided_fields": [
                "estimated_obc_population",
                "women_count",
                "pwd_count",
            ],
        },
        changed_by=None,
    )

    aggregate_and_store(municipality=municipality)
    profile.refresh_from_db()

    summary = profile.aggregated_metrics["metadata"][
        "number_with_no_identified_barangay"
    ]
    assert summary["metrics"] == {
        "estimated_obc_population": 15,
        "women_count": 10,
        "pwd_count": 2,
    }
    assert summary["total"] == 27

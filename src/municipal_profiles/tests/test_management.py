import pytest

try:
    from django.core.management import call_command

    from communities.models import OBCCommunity
    from municipal_profiles.models import MunicipalOBCProfile
except ImportError:  # pragma: no cover - handled via skip
    pytest.skip(
        "Django is required for municipal profile management command tests",
        allow_module_level=True,
    )


@pytest.mark.django_db
def test_seed_dummy_obc_data_command_populates_demo_records():
    call_command("seed_dummy_obc_data", "--tag", "TST")

    profile = MunicipalOBCProfile.objects.select_related("municipality").get(
        municipality__code="TST-M1"
    )

    demographics = profile.aggregated_metrics["sections"]["demographics"]
    vulnerable = profile.aggregated_metrics["sections"]["vulnerable_groups"]
    summary = profile.aggregated_metrics["metadata"][
        "number_with_no_identified_barangay"
    ]

    assert demographics["estimated_obc_population"] == 355
    assert demographics["households"] == 74
    assert demographics["families"] == 63

    assert vulnerable["women_count"] == 168
    assert vulnerable["pwd_count"] == 14

    assert summary["metrics"]["estimated_obc_population"] == 60
    assert summary["metrics"]["women_count"] == 20
    assert summary["metrics"]["pwd_count"] == 5
    assert summary["total"] == 110

    communities = OBCCommunity.objects.filter(
        barangay__municipality=profile.municipality
    )
    assert communities.count() == 3
    assert all(c.priority_needs for c in communities)

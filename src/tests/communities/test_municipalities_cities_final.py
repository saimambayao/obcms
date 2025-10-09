"""Regression tests for FAQ statistics on municipalities and cities."""

import pytest
from django.core.cache import cache

from common.ai_services.chat.faq_handler import get_faq_handler
from common.models import Barangay, Municipality, Province, Region
from communities.models import OBCCommunity


@pytest.fixture
def municipality_stats_dataset(db):
    """Set up geographic data supporting municipality/city FAQ answers."""
    cache.clear()

    region = Region.objects.create(code="R-FAQ", name="FAQ Region")
    province = Province.objects.create(region=region, code="P-FAQ", name="FAQ Province")

    municipality_alpha = Municipality.objects.create(
        province=province,
        code="M-ALPHA",
        name="Alpha",
        municipality_type="municipality",
    )
    municipality_beta = Municipality.objects.create(
        province=province,
        code="M-BETA",
        name="Beta",
        municipality_type="municipality",
    )
    municipality_gamma = Municipality.objects.create(
        province=province,
        code="C-GAMMA",
        name="Gamma City",
        municipality_type="independent_city",
    )

    barangay_alpha = Barangay.objects.create(
        municipality=municipality_alpha,
        code="B-ALPHA",
        name="Barangay Alpha",
    )
    barangay_beta = Barangay.objects.create(
        municipality=municipality_beta,
        code="B-BETA",
        name="Barangay Beta",
    )
    barangay_gamma = Barangay.objects.create(
        municipality=municipality_gamma,
        code="B-GAMMA",
        name="Barangay Gamma",
    )

    OBCCommunity.objects.create(name="Alpha Community", barangay=barangay_alpha)
    OBCCommunity.objects.create(name="Beta Community", barangay=barangay_beta)
    OBCCommunity.objects.create(name="Gamma Community", barangay=barangay_gamma)

    faq_handler = get_faq_handler()
    stats = faq_handler.update_stats_cache()

    return {
        "stats": stats,
        "municipality_total": Municipality.objects.filter(
            municipality_type="municipality"
        ).count(),
        "city_total": Municipality.objects.exclude(
            municipality_type="municipality"
        ).count(),
    }


@pytest.mark.django_db
def test_municipality_stats_string_contains_count(municipality_stats_dataset):
    """The FAQ stats should include the correct municipality total."""
    stats = municipality_stats_dataset["stats"]
    municipality_total = municipality_stats_dataset["municipality_total"]

    assert "municipalities_only" in stats
    assert f"There are {municipality_total} municipalities" in stats["municipalities_only"]


@pytest.mark.django_db
def test_city_stats_string_contains_count(municipality_stats_dataset):
    """The FAQ stats should include the correct city total."""
    stats = municipality_stats_dataset["stats"]
    city_total = municipality_stats_dataset["city_total"]

    assert "cities_only" in stats
    assert f"There are {city_total} cities" in stats["cities_only"]

"""Tests for municipality-related FAQ responses in the chat assistant."""

import pytest
from django.contrib.auth import get_user_model
from django.core.cache import cache

from common.ai_services.chat.chat_engine import ConversationalAssistant
from common.ai_services.chat.faq_handler import get_faq_handler
from common.models import Barangay, Municipality, Province, Region
from communities.models import OBCCommunity


User = get_user_model()


@pytest.fixture
def chat_user(db):
    """Create a user for storing chat history."""
    return User.objects.create_user(
        username="chat_user", email="chat.user@example.com", password="pass1234"
    )


@pytest.fixture
def faq_dataset(db):
    """Populate minimal geographic data for FAQ statistics."""
    cache.clear()

    region = Region.objects.create(code="R-TST", name="Test Region")
    province = Province.objects.create(
        region=region,
        code="P-TST",
        name="Test Province",
    )

    municipality_a = Municipality.objects.create(
        province=province,
        code="MUN-001",
        name="Lakeview",
        municipality_type="municipality",
    )
    municipality_b = Municipality.objects.create(
        province=province,
        code="MUN-002",
        name="Riverside",
        municipality_type="municipality",
    )
    municipality_city = Municipality.objects.create(
        province=province,
        code="CITY-001",
        name="Metrofield",
        municipality_type="component_city",
    )

    barangay_a = Barangay.objects.create(
        municipality=municipality_a,
        code="BRGY-001",
        name="Barangay One",
    )
    barangay_b = Barangay.objects.create(
        municipality=municipality_a,
        code="BRGY-002",
        name="Barangay Two",
    )
    barangay_c = Barangay.objects.create(
        municipality=municipality_city,
        code="BRGY-003",
        name="Barangay Three",
    )

    # Populate communities so that community totals differ from municipality totals
    OBCCommunity.objects.create(name="Community Alpha", barangay=barangay_a)
    OBCCommunity.objects.create(name="Community Beta", barangay=barangay_b)
    OBCCommunity.objects.create(name="Community Gamma", barangay=barangay_c)

    faq_handler = get_faq_handler()
    faq_handler.update_stats_cache()

    return {
        "municipality_count": Municipality.objects.filter(
            municipality_type="municipality"
        ).count(),
        "city_count": Municipality.objects.exclude(
            municipality_type="municipality"
        ).count(),
        "community_count": OBCCommunity.objects.count(),
    }


@pytest.mark.django_db
def test_chat_returns_municipality_count(chat_user, faq_dataset):
    """Ensure the assistant answers with the municipality-only count."""
    assistant = ConversationalAssistant()

    result = assistant.chat(chat_user.id, "How many municipalities")

    response = result["response"]
    expected_count = faq_dataset["municipality_count"]

    assert result["intent"] == "faq"
    assert f"There are {expected_count} municipalities" in response
    # Ensure community totals are not erroneously returned
    assert str(faq_dataset["community_count"]) not in response


@pytest.mark.django_db
def test_chat_returns_city_count(chat_user, faq_dataset):
    """Ensure the assistant answers with the city-only count."""
    assistant = ConversationalAssistant()

    result = assistant.chat(chat_user.id, "How many cities")

    response = result["response"]
    expected_count = faq_dataset["city_count"]

    assert result["intent"] == "faq"
    assert f"There are {expected_count} cities" in response

from types import SimpleNamespace
from unittest import mock

import pytest

try:
    from django.contrib.auth import get_user_model
except ImportError:  # pragma: no cover - handled via skip
    pytest.skip(
        "Django is required for municipal profile serializer tests",
        allow_module_level=True,
    )

from common.models import Municipality, Province, Region
from municipal_profiles.models import MunicipalOBCProfile
from municipal_profiles.serializers import MunicipalOBCProfileSerializer
from municipal_profiles.services import ensure_profile

User = get_user_model()


def _build_municipality():
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
    return municipality


@pytest.mark.django_db
def test_serializer_update_invokes_reported_update_and_persists_flags():
    municipality = _build_municipality()
    profile = ensure_profile(municipality)
    user = User.objects.create_user(
        username="serializer-user",
        password="pass123",
        email="serializer@example.com",
        user_type="oobc_staff",
        is_approved=True,
    )

    request = SimpleNamespace(user=user)
    payload = {
        "municipality": municipality.pk,
        "reported_metrics": {
            "sections": {
                "demographics": {
                    "estimated_obc_population": 120,
                },
            },
            "provided_fields": ["estimated_obc_population"],
        },
        "reported_notes": "Quarterly update",
        "history_note": "Submitted via portal",
        "is_locked": True,
    }
    serializer = MunicipalOBCProfileSerializer(
        instance=profile,
        data=payload,
        context={"request": request},
        partial=True,
    )
    serializer.is_valid(raise_exception=True)

    with mock.patch.object(profile, "apply_reported_update") as mocked_update:
        serializer.save()

    profile.refresh_from_db()
    assert profile.reported_notes == "Quarterly update"
    assert profile.is_locked is True

    mocked_update.assert_called_once()
    mocked_update.assert_called_once_with(
        reported_payload=payload["reported_metrics"],
        changed_by=user,
        note="Submitted via portal",
        update_notes=True,
    )

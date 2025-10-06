"""Common template context helpers."""

from django.urls import NoReverseMatch, reverse
from django.conf import settings


def location_api(request):
    """Expose the location-data API endpoint to templates."""

    try:
        api_url = reverse("common_api:location-data")
    except NoReverseMatch:
        api_url = ""
    return {
        "LOCATION_DATA_API_URL": api_url,
    }


def feature_flags(request):
    """Expose feature flags to templates."""
    return {
        "USE_UNIFIED_CALENDAR": getattr(settings, "USE_UNIFIED_CALENDAR", False),
        "USE_WORKITEM_MODEL": getattr(settings, "USE_WORKITEM_MODEL", False),
    }

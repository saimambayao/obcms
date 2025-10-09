"""URL configuration used for monitoring API endpoint tests."""

from django.urls import include, path

urlpatterns = [
    path(
        "api/monitoring/",
        include(("monitoring.api_urls", "monitoring_api"), namespace="monitoring_api"),
    ),
]

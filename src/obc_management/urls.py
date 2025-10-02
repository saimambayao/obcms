"""
URL configuration for obc_management project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

# Import admin customizations
from . import admin as admin_customizations
from common.admin_views import group_changelist_view
from common.views.health import health_check, readiness_check

# API docs import removed - documentation now backend-only

# Main API router
api_router = DefaultRouter()

urlpatterns = [
    # Health check endpoints (no authentication required)
    path("health/", health_check, name="health"),
    path("ready/", readiness_check, name="readiness"),
    # Custom admin views (must come before admin.site.urls)
    path("admin/auth/group/", group_changelist_view, name="custom_group_changelist"),
    path("admin/", admin.site.urls),
    # Main application URLs
    path("", include("common.urls")),
    path("communities/", include("communities.urls")),
    path("monitoring/", include("monitoring.urls")),
    # Project Central (Integrated Project Management)
    path("project-central/", include("project_central.urls")),
    # Documents and MANA
    path(
        "documents/",
        include(("recommendations.documents.urls", "documents"), namespace="documents"),
    ),
    path("mana/workshops/", include(("mana.urls", "mana"), namespace="mana")),
    # =========================================================================
    # API ENDPOINTS (Versioned)
    # =========================================================================
    # API v1 (Current stable version)
    path("api/v1/", include("api.v1.urls")),

    # Legacy API endpoints (deprecated - will be migrated to v1)
    # TODO: Migrate these to api/v1/ and add deprecation warnings
    path(
        "api/administrative/",
        include(("common.api_urls", "common_api"), namespace="common_api"),
    ),
    path("api/communities/", include("communities.api_urls")),
    path("api/municipal-profiles/", include("municipal_profiles.api_urls")),
    path("api/mana/", include("mana.api_urls")),
    path("api/coordination/", include("coordination.api_urls")),
    path("api/policies/", include("recommendations.policies.api_urls")),
    path("api/policy-tracking/", include("recommendations.policy_tracking.api_urls")),
    # Browsable API authentication
    path("api-auth/", include("rest_framework.urls")),
    path(
        "", lambda request: redirect("common:dashboard")
    ),  # Redirect root to dashboard
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

    # Debug toolbar disabled for now

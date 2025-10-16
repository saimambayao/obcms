"""
URL configuration for obc_management project.

DUAL-MODE ARCHITECTURE:
- OBCMS Mode: Single-tenant URLs (/dashboard/, /communities/, etc.)
- BMMS Mode: Multi-tenant URLs (/moa/{ORG_CODE}/dashboard/, etc.)

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect
from django.views.generic import RedirectView
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

# Import admin customizations
from . import admin as admin_customizations
from common.admin_views import group_changelist_view
from common.views.health import health_check
from .views.health import liveness_probe, readiness_probe

# Import multi-tenant URL configuration
from .urls.multi_tenant_urls import (
    get_multi_tenant_urlpatterns,
    get_admin_urlpatterns,
    get_api_urlpatterns,
    get_utility_urlpatterns,
    get_organization_urlpatterns,
)

# API docs import removed - documentation now backend-only

# Main API router
api_router = DefaultRouter()

# =========================================================================
# MULTI-TENANT URL CONFIGURATION
# =========================================================================
# Automatically generates URL patterns based on BMMS_MODE setting
# - OBCMS Mode: Single-tenant URLs (current structure)
# - BMMS Mode: Multi-tenant URLs with organization context

urlpatterns = []

# 1. Admin and Health URLs (same for both modes)
urlpatterns += get_admin_urlpatterns()

# 2. Multi-tenant application URLs (dynamic based on mode)
urlpatterns += get_multi_tenant_urlpatterns()

# 3. Organization management URLs (BMMS mode only)
urlpatterns += get_organization_urlpatterns()

# 4. Utility URLs (redirects, etc.)
urlpatterns += get_utility_urlpatterns()

# 5. API URLs (same for both modes)
urlpatterns += get_api_urlpatterns()

# 6. Legacy root redirect (maintains existing behavior)
urlpatterns.append(
    path("", lambda request: redirect("common:dashboard"))
)

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

    # Debug toolbar disabled for now

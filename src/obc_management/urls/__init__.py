"""
URL Configuration Package for OBCMS/BMMS Multi-tenant Architecture

This package provides dual-mode URL configuration supporting both:
- OBCMS Mode: Single-tenant URLs (/dashboard/, /communities/, etc.)
- BMMS Mode: Multi-tenant URLs (/moa/{ORG_CODE}/dashboard/, etc.)
"""

from .multi_tenant_urls import (
    get_multi_tenant_urlpatterns,
    get_obcms_urlpatterns,
    get_bmms_urlpatterns,
    get_admin_urlpatterns,
    get_api_urlpatterns,
    get_utility_urlpatterns,
    get_organization_urlpatterns,
    switch_organization,
    validate_organization,
    current_organization,
    generate_url,
    get_current_organization_code,
)

__all__ = [
    'get_multi_tenant_urlpatterns',
    'get_obcms_urlpatterns',
    'get_bmms_urlpatterns',
    'get_admin_urlpatterns',
    'get_api_urlpatterns',
    'get_utility_urlpatterns',
    'get_organization_urlpatterns',
    'switch_organization',
    'validate_organization',
    'current_organization',
    'generate_url',
    'get_current_organization_code',
]
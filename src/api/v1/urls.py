"""
API v1 URL Configuration.

This module organizes all API endpoints under a versioned namespace (v1).
Future versions can be added (v2, v3) without breaking existing clients.

Versioning Strategy:
- URL-based versioning (/api/v1/, /api/v2/)
- Each version maintains backward compatibility within its major version
- Breaking changes require new major version
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

# Create router for viewsets
router = DefaultRouter()

# TODO: Register viewsets here as they are migrated to versioned API
# Example:
# from communities.api.views import CommunityViewSet
# router.register(r'communities', CommunityViewSet, basename='community')

urlpatterns = [
    # Router URLs (for viewsets)
    path('', include(router.urls)),

    # Authentication endpoints (JWT)
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Legacy API endpoints (to be migrated to viewsets)
    # TODO: Move these to proper viewsets
    # path('communities/', include('communities.api.urls')),
    # path('mana/', include('mana.api.urls')),
    # path('coordination/', include('coordination.api.urls')),
]

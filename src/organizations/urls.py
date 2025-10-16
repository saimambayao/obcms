"""
URL configuration for organizations app.

Provides URL patterns for:
- Organization switching interface
- Organization management views
- API endpoints for organization operations
- Membership management
"""

from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from . import views

app_name = 'organizations'

# URL patterns for organization management
urlpatterns = [
    # Organization switching interface
    path('switcher/', views.organization_switcher, name='switcher'),
    path('switch/<str:organization_code>/', views.switch_organization, name='switch'),

    # Organization management
    path('', views.OrganizationListView.as_view(), name='list'),
    path('<slug:code>/', views.OrganizationDetailView.as_view(), name='detail'),

    # Membership management
    path('my-memberships/', views.my_memberships, name='my_memberships'),
    path('set-primary/<int:organization_id>/', views.set_primary_organization, name='set_primary'),
]

# API URL patterns for organizations
api_urlpatterns = [
    # API endpoints for organization switching
    path('api/v1/organizations/my-organizations/', views.api_my_organizations, name='api_my_organizations'),
    path('api/v1/organizations/switch/', views.api_switch_organization, name='api_switch'),
]
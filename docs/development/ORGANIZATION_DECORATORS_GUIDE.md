# Organization Decorators Usage Guide

**Status:** Phase 4 Complete - View Decorators
**BMMS Phase:** Embedded Architecture - View Layer
**Related:** Phase 3 (Middleware), Phase 5 (Model Migration)

## Overview

This guide covers the organization-aware decorators, mixins, and permissions for BMMS multi-tenant support. These components enforce organization context and access control at the view layer.

### Key Components

1. **Function-Based View Decorators** (`common.decorators.organization`)
   - `@require_organization` - Validates organization context
   - `@organization_param()` - Loads organization from URL parameters

2. **Class-Based View Mixins** (`common.mixins.organization`)
   - `OrganizationRequiredMixin` - CBV organization validation

3. **DRF Permissions** (`common.permissions.organization`)
   - `OrganizationAccessPermission` - API access control

### Architecture

```
Request Flow:
1. OrganizationContextMiddleware sets request.organization
2. View decorator/mixin validates organization access
3. OrganizationScopedManager filters queryset
4. Template receives organization in context
```

**Modes:**
- **OBCMS Mode:** Single organization (OOBC), transparent operation
- **BMMS Mode:** Multi-tenant with OrganizationMembership validation

---

## Function-Based Views

### @require_organization

Validates that `request.organization` exists and user has access.

**Usage:**

```python
from django.contrib.auth.decorators import login_required
from common.decorators.organization import require_organization

@login_required
@require_organization
def community_list(request):
    """List communities for current organization."""
    # request.organization is guaranteed to exist
    # Queryset auto-filtered by OrganizationScopedManager
    communities = OBCCommunity.objects.all()

    return render(request, 'communities/list.html', {
        'communities': communities,
        'organization': request.organization,
    })
```

**Behavior:**

| Mode | User Type | Behavior |
|------|-----------|----------|
| OBCMS | All | Transparent (organization = OOBC) |
| BMMS | Superuser | Always granted access |
| BMMS | Regular User | Validates OrganizationMembership |
| Both | No organization | Returns HTTP 403 Forbidden |

**Error Response:**

```http
HTTP 403 Forbidden
Organization context required but not found.
```

### @organization_param()

Loads organization from URL parameter and validates access.

**Usage:**

```python
from django.contrib.auth.decorators import login_required
from common.decorators.organization import organization_param

@login_required
@organization_param('org_code')
def organization_dashboard(request, org_code):
    """Dashboard for specific organization."""
    # request.organization loaded from URL parameter
    # User access validated

    stats = {
        'communities': OBCCommunity.objects.count(),
        'assessments': Assessment.objects.count(),
    }

    return render(request, 'dashboard.html', {
        'organization': request.organization,
        'stats': stats,
    })
```

**URL Pattern:**

```python
from django.urls import path
from . import views

urlpatterns = [
    path('org/<str:org_code>/dashboard/', views.organization_dashboard),
]
```

**Parameters:**

- `param_name` (default: `'org_code'`) - URL parameter name

**Features:**

- Case-insensitive organization code lookup
- Returns 404 if organization not found
- Validates user membership (BMMS mode)
- Sets `request.organization` for the view

---

## Class-Based Views

### OrganizationRequiredMixin

Validates organization context in `dispatch()` method for CBVs.

**Usage:**

```python
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from common.mixins.organization import OrganizationRequiredMixin

class CommunityListView(OrganizationRequiredMixin, LoginRequiredMixin, ListView):
    """List communities for current organization."""
    model = OBCCommunity
    template_name = 'communities/list.html'
    context_object_name = 'communities'

    def get_queryset(self):
        # Auto-filtered by OrganizationScopedManager
        return super().get_queryset()
```

**Important:** Must be placed **FIRST** in the inheritance chain:

```python
# Correct
class MyView(OrganizationRequiredMixin, LoginRequiredMixin, ListView):
    pass

# Wrong - mixin runs too late
class MyView(LoginRequiredMixin, OrganizationRequiredMixin, ListView):
    pass
```

### Mixin Methods

#### get_organization()

Safely access current organization:

```python
class CommunityDetailView(OrganizationRequiredMixin, DetailView):
    model = OBCCommunity

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        org = self.get_organization()
        context['can_edit'] = org.code == 'OOBC'
        return context
```

#### get_context_data()

Automatically adds `organization` to template context:

```html
<!-- Template automatically has 'organization' variable -->
<h1>{{ organization.name }}</h1>
<p>Organization Code: {{ organization.code }}</p>
```

### Optional Organization

Make organization optional for specific views:

```python
class PublicListView(OrganizationRequiredMixin, ListView):
    model = MyModel
    require_organization = False  # Allow without organization
```

---

## API Views (Django REST Framework)

### OrganizationAccessPermission

Validates organization context for API views.

**ViewSet Usage:**

```python
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from common.permissions.organization import OrganizationAccessPermission

class CommunityViewSet(viewsets.ModelViewSet):
    """API endpoint for communities."""
    serializer_class = CommunitySerializer
    permission_classes = [IsAuthenticated, OrganizationAccessPermission]

    def get_queryset(self):
        # Auto-filtered by OrganizationScopedManager
        return OBCCommunity.objects.all()
```

**APIView Usage:**

```python
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from common.permissions.organization import OrganizationAccessPermission

class CommunityStatsAPIView(APIView):
    """API endpoint for community statistics."""
    permission_classes = [IsAuthenticated, OrganizationAccessPermission]

    def get(self, request):
        # request.organization validated by permission class
        stats = {
            'total': OBCCommunity.objects.count(),
            'organization': request.organization.code,
        }
        return Response(stats)
```

### Permission Checks

#### has_permission()

Validates organization context and membership:

```python
# Automatic validation:
# 1. request.organization exists
# 2. User is authenticated
# 3. User has OrganizationMembership (BMMS mode)
# 4. Superusers always granted access
```

#### has_object_permission()

Prevents cross-organization data access:

```python
# Validates:
# - Object's organization matches request.organization
# - Blocks cross-org access attempts
# - Logs warning for security monitoring
```

**Example:**

```python
# User in OOBC tries to access MOA1 community
# Permission denied, logged:
# "User john attempted cross-org access: request org=OOBC, object org=MOA1"
```

---

## Complete Examples

### Example 1: Community Management

**Function-Based View:**

```python
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from common.decorators.organization import require_organization
from communities.models import OBCCommunity
from communities.forms import CommunityForm

@login_required
@require_organization
def community_create(request):
    """Create new community."""
    if request.method == 'POST':
        form = CommunityForm(request.POST)
        if form.is_valid():
            community = form.save(commit=False)
            # Organization auto-set by OrganizationScopedModel
            community.save()
            return redirect('community_list')
    else:
        form = CommunityForm()

    return render(request, 'communities/create.html', {
        'form': form,
        'organization': request.organization,
    })

@login_required
@require_organization
def community_edit(request, pk):
    """Edit existing community."""
    # get_object_or_404 auto-filters by organization
    community = get_object_or_404(OBCCommunity, pk=pk)

    if request.method == 'POST':
        form = CommunityForm(request.POST, instance=community)
        if form.is_valid():
            form.save()
            return redirect('community_detail', pk=pk)
    else:
        form = CommunityForm(instance=community)

    return render(request, 'communities/edit.html', {
        'form': form,
        'community': community,
        'organization': request.organization,
    })
```

**Class-Based View:**

```python
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from common.mixins.organization import OrganizationRequiredMixin
from communities.models import OBCCommunity
from communities.forms import CommunityForm

class CommunityListView(OrganizationRequiredMixin, LoginRequiredMixin, ListView):
    """List all communities for current organization."""
    model = OBCCommunity
    template_name = 'communities/list.html'
    context_object_name = 'communities'
    paginate_by = 20

class CommunityDetailView(OrganizationRequiredMixin, LoginRequiredMixin, DetailView):
    """Show community details."""
    model = OBCCommunity
    template_name = 'communities/detail.html'
    context_object_name = 'community'

class CommunityCreateView(OrganizationRequiredMixin, LoginRequiredMixin, CreateView):
    """Create new community."""
    model = OBCCommunity
    form_class = CommunityForm
    template_name = 'communities/create.html'

    def form_valid(self, form):
        # Organization auto-set by OrganizationScopedModel
        return super().form_valid(form)

class CommunityUpdateView(OrganizationRequiredMixin, LoginRequiredMixin, UpdateView):
    """Update existing community."""
    model = OBCCommunity
    form_class = CommunityForm
    template_name = 'communities/edit.html'
```

### Example 2: API Endpoint

```python
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from common.permissions.organization import OrganizationAccessPermission
from communities.models import OBCCommunity
from communities.serializers import CommunitySerializer

class CommunityViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing communities.

    All operations are automatically scoped to request.organization.
    """
    serializer_class = CommunitySerializer
    permission_classes = [IsAuthenticated, OrganizationAccessPermission]

    def get_queryset(self):
        # Auto-filtered by OrganizationScopedManager
        return OBCCommunity.objects.all()

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get community statistics for current organization."""
        queryset = self.get_queryset()

        stats = {
            'total': queryset.count(),
            'active': queryset.filter(status='active').count(),
            'pending': queryset.filter(status='pending').count(),
            'organization': request.organization.code,
        }

        return Response(stats)

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve a community."""
        community = self.get_object()

        # Cross-org access already prevented by permission class
        community.status = 'active'
        community.save()

        return Response({'status': 'approved'})
```

---

## Migration Guide

### Converting Existing Views

#### Before (No Organization Context):

```python
@login_required
def community_list(request):
    communities = OBCCommunity.objects.all()
    return render(request, 'list.html', {'communities': communities})
```

#### After (Organization-Aware):

```python
@login_required
@require_organization
def community_list(request):
    # Queryset auto-filtered by organization
    communities = OBCCommunity.objects.all()
    return render(request, 'list.html', {
        'communities': communities,
        'organization': request.organization,
    })
```

**Changes Required:**
1. Add `@require_organization` decorator
2. Update template to show organization (optional)
3. No queryset changes needed (auto-filtered)

### Converting CBVs

#### Before:

```python
class CommunityListView(LoginRequiredMixin, ListView):
    model = OBCCommunity
```

#### After:

```python
class CommunityListView(OrganizationRequiredMixin, LoginRequiredMixin, ListView):
    model = OBCCommunity
```

**Changes Required:**
1. Add `OrganizationRequiredMixin` as FIRST mixin
2. No other changes needed

### Converting API Views

#### Before:

```python
class CommunityViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = OBCCommunity.objects.all()
```

#### After:

```python
class CommunityViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, OrganizationAccessPermission]
    queryset = OBCCommunity.objects.all()
```

**Changes Required:**
1. Add `OrganizationAccessPermission` to `permission_classes`
2. No queryset changes needed

---

## Testing

### Testing Decorators

```python
from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from common.decorators.organization import require_organization
from organizations.models import Organization, OrganizationMembership

class DecoratorTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='test', password='test')
        self.org = Organization.objects.create(code='OOBC', name='OOBC')

    def test_decorator_with_organization(self):
        @require_organization
        def test_view(request):
            return HttpResponse('OK')

        request = self.factory.get('/')
        request.user = self.user
        request.organization = self.org

        response = test_view(request)
        self.assertEqual(response.status_code, 200)
```

### Testing Mixins

```python
from django.test import TestCase, RequestFactory
from django.views.generic import ListView
from common.mixins.organization import OrganizationRequiredMixin

class TestView(OrganizationRequiredMixin, ListView):
    model = User

class MixinTest(TestCase):
    def test_mixin_with_organization(self):
        request = self.factory.get('/')
        request.user = self.user
        request.organization = self.org

        view = TestView.as_view()
        response = view(request)

        self.assertEqual(response.status_code, 200)
```

---

## Troubleshooting

### Common Issues

#### 1. "Organization context required but not found"

**Cause:** OrganizationContextMiddleware not enabled or running too late

**Solution:**
```python
# src/obc_management/settings/base.py
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'organizations.middleware.OrganizationContextMiddleware',  # Add here
    ...
]
```

#### 2. "User denied access to organization"

**Cause:** User lacks OrganizationMembership in BMMS mode

**Solution:**
```python
# Create membership
OrganizationMembership.objects.create(
    user=user,
    organization=org,
    role='member',
    is_active=True
)
```

#### 3. Mixin runs too late

**Cause:** OrganizationRequiredMixin not first in inheritance chain

**Solution:**
```python
# Correct order
class MyView(OrganizationRequiredMixin, LoginRequiredMixin, ListView):
    pass
```

#### 4. Cross-organization access

**Cause:** Attempting to access objects from different organization

**Solution:** Ensure all queries use `request.organization` context

---

## Reference

### Related Documentation

- [Phase 3: Middleware Enhancement](../plans/bmms/implementation/tasks/phase3_middleware_enhancement.txt)
- [Phase 5: Model Migration](../plans/bmms/implementation/tasks/phase5_communities_migration.txt)
- [BMMS Embedded Architecture](../plans/bmms/implementation/EMBEDDED_ARCHITECTURE.md)
- [Organization Context Middleware](../../src/organizations/middleware.py)

### Configuration

**Environment Variable:**
```bash
# .env
BMMS_MODE=obcms  # or 'bmms' for multi-tenant
```

**Settings:**
```python
# src/obc_management/settings/base.py
BMMS_MODE = env('BMMS_MODE', default='obcms')
DEFAULT_ORGANIZATION_CODE = 'OOBC'
```

---

**Phase 4 Status:** Complete
**Next Phase:** Phase 5 - Model Migration (Communities App)

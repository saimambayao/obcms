# Organization Middleware Migration Guide

**Purpose:** Guide for updating existing codebase to use OrganizationMiddleware

**Target Audience:** Developers implementing BMMS Phase 1

---

## Overview

This guide helps you migrate existing OBCMS code to use the new OrganizationMiddleware for multi-tenant data isolation.

---

## Migration Phases

### Phase 1: Middleware Registration (Day 1)

#### Step 1.1: Update settings.py

```python
# src/obc_management/settings/base.py

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "common.middleware.DeprecatedURLRedirectMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "axes.middleware.AxesMiddleware",
    "auditlog.middleware.AuditlogMiddleware",

    # ✅ ADD THIS LINE
    "common.middleware.organization.OrganizationMiddleware",

    "common.middleware.AuditMiddleware",
    "common.middleware.APILoggingMiddleware",
    "common.middleware.DeprecationLoggingMiddleware",
    "common.middleware.MANAAccessControlMiddleware",
    "mana.middleware.ManaWorkshopContextMiddleware",
    "mana.middleware.ManaParticipantAccessMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
```

#### Step 1.2: Test Middleware Registration

```bash
cd src/
python manage.py check
python manage.py runserver

# Test in browser - should work without errors
# Check logs for "OrganizationMiddleware initialized"
```

---

### Phase 2: URL Pattern Updates (Week 1)

#### Step 2.1: Identify Organization-Scoped URLs

URLs that need organization context:
- Planning module: `/planning/ppas/`, `/planning/strategic-plans/`
- Budget module: `/budget/preparation/`, `/budget/execution/`
- Monitoring module: `/monitoring/ppas/`, `/monitoring/moas/`
- Coordination module: `/coordination/partnerships/`

#### Step 2.2: Update URL Patterns

**Before:**
```python
# src/planning/urls.py
urlpatterns = [
    path('ppas/', views.ppa_list, name='ppa_list'),
    path('ppas/<uuid:pk>/', views.ppa_detail, name='ppa_detail'),
]
```

**After:**
```python
# src/planning/urls.py
urlpatterns = [
    # Organization-scoped URLs
    path('moa/<str:org_code>/ppas/',
         views.ppa_list,
         name='ppa_list'),
    path('moa/<str:org_code>/ppas/<uuid:pk>/',
         views.ppa_detail,
         name='ppa_detail'),
]
```

#### Step 2.3: Update URL References in Templates

**Before:**
```html
<a href="{% url 'ppa_list' %}">PPAs</a>
```

**After:**
```html
<a href="{% url 'ppa_list' org_code=request.organization.acronym %}">
    PPAs
</a>
```

---

### Phase 3: View Updates (Week 1-2)

#### Pattern 1: Simple List View

**Before:**
```python
def ppa_list(request):
    ppas = PPA.objects.all()
    return render(request, 'planning/ppa_list.html', {
        'ppas': ppas,
    })
```

**After:**
```python
from common.middleware.organization import requires_organization

@requires_organization
def ppa_list(request):
    # Organization automatically set by middleware
    org = request.organization

    # Filter by organization
    ppas = PPA.objects.filter(implementing_moa=org)

    return render(request, 'planning/ppa_list.html', {
        'organization': org,
        'ppas': ppas,
    })
```

#### Pattern 2: Detail View with Permission Check

**Before:**
```python
def ppa_detail(request, pk):
    ppa = get_object_or_404(PPA, pk=pk)

    # Manual permission check
    if not request.user.can_view_ppa(ppa):
        raise PermissionDenied

    return render(request, 'planning/ppa_detail.html', {
        'ppa': ppa,
    })
```

**After:**
```python
from common.middleware.organization import requires_organization_access

@requires_organization_access
def ppa_detail(request, pk):
    # Organization access already verified
    org = request.organization

    # Filter by organization for safety
    ppa = get_object_or_404(
        PPA,
        pk=pk,
        implementing_moa=org
    )

    return render(request, 'planning/ppa_detail.html', {
        'organization': org,
        'ppa': ppa,
    })
```

#### Pattern 3: Create View with Organization Assignment

**Before:**
```python
def ppa_create(request):
    if request.method == 'POST':
        form = PPAForm(request.POST)
        if form.is_valid():
            ppa = form.save(commit=False)
            # Manually set organization
            ppa.implementing_moa = request.user.moa_organization
            ppa.save()
            return redirect('ppa_detail', pk=ppa.pk)
    else:
        form = PPAForm()

    return render(request, 'planning/ppa_form.html', {
        'form': form,
    })
```

**After:**
```python
from common.middleware.organization import requires_organization_access

@requires_organization_access
def ppa_create(request):
    org = request.organization

    if request.method == 'POST':
        form = PPAForm(request.POST, organization=org)
        if form.is_valid():
            ppa = form.save(commit=False)
            # Use request.organization
            ppa.implementing_moa = org
            ppa.save()
            return redirect('ppa_detail',
                          org_code=org.acronym,
                          pk=ppa.pk)
    else:
        form = PPAForm(organization=org)

    return render(request, 'planning/ppa_form.html', {
        'organization': org,
        'form': form,
    })
```

---

### Phase 4: Form Updates (Week 2)

#### Update Forms to Accept Organization

**Before:**
```python
class PPAForm(forms.ModelForm):
    class Meta:
        model = PPA
        fields = ['name', 'description', 'implementing_moa']
```

**After:**
```python
class PPAForm(forms.ModelForm):
    def __init__(self, *args, organization=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.organization = organization

        # Hide implementing_moa field (auto-set)
        if 'implementing_moa' in self.fields:
            self.fields['implementing_moa'].widget = forms.HiddenInput()

        # Limit related fields to organization
        if organization and 'related_ppa' in self.fields:
            self.fields['related_ppa'].queryset = PPA.objects.filter(
                implementing_moa=organization
            )

    class Meta:
        model = PPA
        fields = ['name', 'description', 'implementing_moa']
```

---

### Phase 5: Template Updates (Week 2-3)

#### Update Base Template

```html
<!-- src/templates/base.html -->
<!DOCTYPE html>
<html>
<head>
    <title>OBCMS - {{ request.organization.name|default:"Home" }}</title>
</head>
<body>
    <!-- Organization Header -->
    {% if request.organization %}
    <div class="org-header">
        <h1>{{ request.organization.name }}</h1>
        <span class="org-code">{{ request.organization.acronym }}</span>

        {% if request.is_ocm_user %}
            <span class="badge badge-info">OCM - Read Only</span>
        {% endif %}

        {% if request.can_switch_org %}
            <a href="{% url 'organization_switch' %}">
                Switch Organization
            </a>
        {% endif %}
    </div>
    {% endif %}

    <!-- Content -->
    {% block content %}{% endblock %}
</body>
</html>
```

#### Update Navigation with Organization Links

```html
<!-- src/templates/components/navbar.html -->
<nav>
    {% if request.organization %}
        {% with org_code=request.organization.acronym %}
            <a href="{% url 'dashboard' org_code=org_code %}">
                Dashboard
            </a>
            <a href="{% url 'ppa_list' org_code=org_code %}">
                PPAs
            </a>
            <a href="{% url 'budget_home' org_code=org_code %}">
                Budget
            </a>
        {% endwith %}
    {% else %}
        <a href="{% url 'organization_select' %}">
            Select Organization
        </a>
    {% endif %}
</nav>
```

---

### Phase 6: API Updates (Week 3)

#### Update DRF ViewSets

**Before:**
```python
class PPAViewSet(viewsets.ModelViewSet):
    queryset = PPA.objects.all()
    serializer_class = PPASerializer
```

**After:**
```python
class PPAViewSet(viewsets.ModelViewSet):
    serializer_class = PPASerializer

    def get_queryset(self):
        org = self.request.organization

        if not org:
            return PPA.objects.none()

        # OCM users see all
        if self.request.is_ocm_user:
            return PPA.objects.all()

        # Others filtered by organization
        return PPA.objects.filter(implementing_moa=org)

    def perform_create(self, serializer):
        # Auto-set organization on create
        serializer.save(implementing_moa=self.request.organization)
```

---

### Phase 7: Model Manager Updates (Week 3-4)

#### Create Organization-Scoped Manager

```python
# src/common/managers.py
from django.db import models
from common.middleware.organization import get_current_organization

class OrganizationScopedManager(models.Manager):
    """Manager that automatically filters by current organization."""

    def get_queryset(self):
        qs = super().get_queryset()
        org = get_current_organization()

        if org:
            return qs.filter(moa_organization=org)

        return qs
```

#### Apply to Models

```python
# src/planning/models.py
from common.managers import OrganizationScopedManager

class PPA(models.Model):
    name = models.CharField(max_length=255)
    implementing_moa = models.ForeignKey(
        'coordination.Organization',
        on_delete=models.PROTECT
    )

    # Organization-scoped manager
    objects = OrganizationScopedManager()

    # Unfiltered access (admin, superuser)
    all_objects = models.Manager()
```

---

## Verification Checklist

### After Each Phase

- [ ] Run `python manage.py check` - No errors
- [ ] Run tests: `pytest`
- [ ] Check logs for security events
- [ ] Test with different user roles:
  - [ ] Superuser - Can access all orgs
  - [ ] OCM user - Read-only all orgs
  - [ ] OOBC staff - Can switch orgs
  - [ ] MOA staff - Restricted to own org
- [ ] Verify data isolation (MOA A can't see MOA B)

---

## Common Migration Issues

### Issue 1: Organization Not Set

**Symptom:**
```python
org = request.organization  # None
```

**Solution:**
```python
# Add fallback handling
org = request.organization
if not org:
    return render(request, 'error/no_org.html')
```

### Issue 2: Circular Import

**Symptom:**
```
ImportError: cannot import name 'Organization' from partially initialized module
```

**Solution:**
```python
# Use lazy import in functions
def get_organization():
    from coordination.models import Organization
    return Organization.objects.get(...)
```

### Issue 3: URL Reverse Failed

**Symptom:**
```
NoReverseMatch: Reverse for 'ppa_list' with keyword arguments '{'org_code': 'oobc'}' not found
```

**Solution:**
```python
# Check URL pattern name and parameters
# Ensure org_code parameter is in URL pattern
path('moa/<str:org_code>/ppas/', views.ppa_list, name='ppa_list')
```

---

## Testing Migration

### Unit Tests

```python
from django.test import TestCase
from coordination.models import Organization
from common.models import User

class OrganizationMiddlewareTest(TestCase):
    def setUp(self):
        # Create test organizations
        self.org_a = Organization.objects.create(
            name="Ministry A",
            acronym="ministry-a",
            organization_type="bmoa"
        )
        self.org_b = Organization.objects.create(
            name="Ministry B",
            acronym="ministry-b",
            organization_type="bmoa"
        )

        # Create MOA staff for org_a
        self.moa_staff = User.objects.create_user(
            username="moa_staff",
            password="testpass123"
        )
        self.moa_staff.is_moa_staff = True
        self.moa_staff.moa_organization = self.org_a
        self.moa_staff.save()

    def test_moa_staff_restricted_to_own_org(self):
        """MOA staff should only access their organization."""
        self.client.force_login(self.moa_staff)

        # Should access own org
        response = self.client.get(f'/moa/{self.org_a.acronym}/ppas/')
        self.assertEqual(response.status_code, 200)

        # Should NOT access other org
        response = self.client.get(f'/moa/{self.org_b.acronym}/ppas/')
        self.assertEqual(response.status_code, 403)
```

---

## Rollback Plan

If issues arise during migration:

### Immediate Rollback

1. **Comment out middleware in settings.py**
```python
# MIDDLEWARE = [
#     ...
#     # "common.middleware.organization.OrganizationMiddleware",  # ❌ DISABLED
#     ...
# ]
```

2. **Restart server**
```bash
python manage.py runserver
```

3. **Investigate issue in logs**

### Gradual Rollback

Keep old URLs alongside new ones temporarily:

```python
urlpatterns = [
    # New organization-scoped URLs
    path('moa/<str:org_code>/ppas/', views.ppa_list, name='ppa_list_org'),

    # Old URLs (temporary, redirect to org-scoped)
    path('ppas/', views.ppa_list_redirect, name='ppa_list'),
]
```

---

## Migration Timeline

### Week 1
- Day 1: Register middleware, test
- Day 2-3: Update URL patterns for planning module
- Day 4-5: Update views for planning module

### Week 2
- Day 1-2: Update forms and templates
- Day 3-5: Update budget module URLs/views

### Week 3
- Day 1-3: Update API endpoints
- Day 4-5: Update monitoring module

### Week 4
- Day 1-2: Create organization-scoped managers
- Day 3-5: Final testing and verification

---

## Success Criteria

Migration is complete when:

- [ ] All URL patterns use `/moa/<org_code>/` format
- [ ] All views use `request.organization`
- [ ] All forms accept organization parameter
- [ ] All templates show organization context
- [ ] All API endpoints filter by organization
- [ ] All models use organization-scoped managers
- [ ] All tests pass with different user roles
- [ ] Zero cross-organization data leaks
- [ ] Security logs show proper access control

---

## Support Resources

- **Implementation Guide:** `docs/improvements/ORGANIZATION_MIDDLEWARE_IMPLEMENTATION.md`
- **Security Guide:** `docs/improvements/ORGANIZATION_MIDDLEWARE_SECURITY.md`
- **Quick Reference:** `docs/improvements/ORGANIZATION_MIDDLEWARE_QUICK_REFERENCE.md`
- **BMMS Plan:** `docs/plans/bmms/TRANSITION_PLAN.md`

---

**Document Version:** 1.0
**Last Updated:** 2025-10-13
**Next Review:** After Week 1 completion

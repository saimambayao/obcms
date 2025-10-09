# MOA RBAC Usage Guide

**Audience:** OBCMS Developers
**Last Updated:** 2025-10-08
**Status:** Complete

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Using Decorators in Views](#using-decorators-in-views)
3. [Using Mixins in Class-Based Views](#using-mixins-in-class-based-views)
4. [Using Template Tags](#using-template-tags)
5. [Admin Interface](#admin-interface)
6. [Testing Your Code](#testing-your-code)
7. [Common Patterns](#common-patterns)
8. [Troubleshooting](#troubleshooting)

---

## Quick Start

The MOA RBAC system provides three layers of permission control:

1. **View Layer** - Decorators and mixins for Django views
2. **Model Layer** - Permission methods on User model
3. **Template Layer** - Template tags for conditional rendering

**Key Principle:** Always implement **all three layers** for production security.

---

## Using Decorators in Views

### Import Decorators

```python
from common.utils.moa_permissions import (
    moa_view_only,
    moa_can_edit_organization,
    moa_can_edit_ppa,
    moa_can_edit_work_item,
    moa_no_access,
)
```

### 1. View-Only Access (Communities Module)

Use `@moa_view_only` for resources that MOA users can view but not modify:

```python
from common.utils.moa_permissions import moa_view_only
from django.shortcuts import render
from communities.models import OBCCommunity

@moa_view_only
def community_list(request):
    """
    List OBC communities (view-only for MOA users).

    MOA users can GET but not POST/PUT/DELETE.
    """
    communities = OBCCommunity.objects.filter(is_active=True)
    return render(request, 'communities/community_list.html', {
        'communities': communities
    })
```

**Behavior:**
- MOA users: GET allowed, POST/PUT/DELETE blocked (403)
- OOBC staff: All methods allowed
- Superusers: All methods allowed

### 2. Organization Management

Use `@moa_can_edit_organization` to restrict organization editing to own MOA:

```python
from common.utils.moa_permissions import moa_can_edit_organization
from django.shortcuts import render, get_object_or_404
from coordination.models import Organization

@moa_can_edit_organization
def organization_update(request, pk):
    """
    Update organization details.

    MOA users can only edit their own organization.
    """
    organization = get_object_or_404(Organization, pk=pk)

    # Process form submission...

    return render(request, 'coordination/organization_form.html', {
        'organization': organization
    })
```

**Behavior:**
- MOA user editing own org: Allowed
- MOA user editing other org: 403 PermissionDenied
- OOBC staff: Can edit any org
- Superusers: Can edit any org

### 3. PPA Management

Use `@moa_can_edit_ppa` to restrict PPA access to own MOA's PPAs:

```python
from common.utils.moa_permissions import moa_can_edit_ppa
from monitoring.models import MonitoringEntry

@moa_can_edit_ppa
def ppa_update(request, pk):
    """
    Update PPA details.

    MOA users can only edit PPAs from their organization.
    """
    ppa = get_object_or_404(MonitoringEntry, pk=pk)

    # Form processing...

    return render(request, 'monitoring/ppa_form.html', {
        'ppa': ppa
    })
```

### 4. No Access (MANA Module)

Use `@moa_no_access` to completely block MOA users:

```python
from common.utils.moa_permissions import moa_no_access

@moa_no_access
def assessment_list(request):
    """
    List MANA assessments.

    MOA users are completely blocked (OOBC internal module).
    """
    assessments = Assessment.objects.all()
    return render(request, 'mana/assessment_list.html', {
        'assessments': assessments
    })
```

**Behavior:**
- MOA users: 403 PermissionDenied (all methods)
- OOBC staff: Full access
- Superusers: Full access

---

## Using Mixins in Class-Based Views

### Import Mixins

```python
from common.mixins import (
    MOAFilteredQuerySetMixin,
    MOAOrganizationAccessMixin,
    MOAPPAAccessMixin,
    MOAViewOnlyMixin,
)
```

### 1. Auto-Filtered List Views

Use `MOAFilteredQuerySetMixin` to automatically filter querysets for MOA users:

```python
from django.views.generic import ListView
from common.mixins import MOAFilteredQuerySetMixin
from monitoring.models import MonitoringEntry

class PPAListView(MOAFilteredQuerySetMixin, ListView):
    """
    List PPAs (auto-filtered for MOA users).

    MOA users see only their organization's PPAs.
    OOBC staff see all PPAs.
    """
    model = MonitoringEntry
    template_name = 'monitoring/ppa_list.html'
    context_object_name = 'ppas'
    moa_filter_field = 'implementing_moa'  # Field to filter by
    paginate_by = 20

    def get_queryset(self):
        qs = super().get_queryset()
        # Additional filtering
        qs = qs.filter(category='moa_ppa').order_by('-created_at')
        return qs
```

**Mixin Configuration:**
- `moa_filter_field` - Field name to filter (defaults to 'implementing_moa')
- Set to `None` to disable filtering

### 2. Organization Detail Views

Use `MOAOrganizationAccessMixin` for organization detail/update views:

```python
from django.views.generic import UpdateView
from common.mixins import MOAOrganizationAccessMixin
from coordination.models import Organization

class OrganizationUpdateView(MOAOrganizationAccessMixin, UpdateView):
    """
    Update organization (MOA users can only edit own org).
    """
    model = Organization
    form_class = OrganizationForm
    template_name = 'coordination/organization_form.html'

    def get_queryset(self):
        qs = super().get_queryset()
        # Additional filtering if needed
        return qs
```

**Behavior:**
- Automatically checks `get_object()` against user's MOA organization
- Raises 403 if MOA user tries to access other organization

### 3. PPA Detail Views

Use `MOAPPAAccessMixin` for PPA detail/update views:

```python
from django.views.generic import DetailView
from common.mixins import MOAPPAAccessMixin
from monitoring.models import MonitoringEntry

class PPADetailView(MOAPPAAccessMixin, DetailView):
    """
    PPA detail view (MOA users can only view own PPAs).
    """
    model = MonitoringEntry
    template_name = 'monitoring/ppa_detail.html'
    context_object_name = 'ppa'
```

### 4. View-Only Restrictions

Use `MOAViewOnlyMixin` to restrict MOA users to GET requests:

```python
from django.views.generic import ListView
from common.mixins import MOAViewOnlyMixin, MOAFilteredQuerySetMixin

class CommunityListView(MOAViewOnlyMixin, MOAFilteredQuerySetMixin, ListView):
    """
    Community list (MOA users have view-only access).
    """
    model = OBCCommunity
    template_name = 'communities/community_list.html'
    moa_filter_field = None  # No filtering - all users see all communities
```

**Behavior:**
- MOA users can GET but not POST/PUT/DELETE
- Raises 403 on write operations from MOA users

### Combining Multiple Mixins

Mixins can be combined for comprehensive protection:

```python
class OrganizationDetailView(
    MOAOrganizationAccessMixin,  # Restrict to own org
    MOAViewOnlyMixin,            # Block write operations
    DetailView
):
    """
    Organization detail view.

    - MOA users can only view their own organization
    - MOA users cannot edit (view-only)
    - OOBC staff can view and edit all organizations
    """
    model = Organization
    template_name = 'coordination/organization_detail.html'
```

---

## Using Template Tags

### Load Template Tags

```django
{% load moa_rbac %}
```

### 1. Check MOA Focal User Status

```django
{% load moa_rbac %}

{% is_moa_focal_user user as is_focal %}
{% if is_focal %}
    <div class="alert alert-info">
        <p>You are logged in as an MOA focal user for {{ user.moa_organization.name }}</p>
    </div>
{% endif %}
```

### 2. Check Organization Management Permission

```django
{% load moa_rbac %}

{% can_manage_moa user organization as can_manage %}
{% if can_manage %}
    <a href="{% url 'organization_edit' organization.pk %}" class="btn btn-primary">
        Edit Organization
    </a>
{% else %}
    <p class="text-muted">You cannot edit this organization</p>
{% endif %}
```

### 3. Check PPA Management Permission

```django
{% load moa_rbac %}

{% can_manage_ppa user ppa as can_manage %}
{% if can_manage %}
    <div class="ppa-actions">
        <a href="{% url 'ppa_edit' ppa.pk %}" class="btn btn-sm btn-primary">
            <i class="fas fa-edit"></i> Edit PPA
        </a>
        <button class="btn btn-sm btn-danger" data-ppa-id="{{ ppa.pk }}">
            <i class="fas fa-trash"></i> Delete PPA
        </button>
    </div>
{% else %}
    <p class="text-muted">
        <i class="fas fa-lock"></i>
        {% if user.is_moa_staff %}
            You can only manage PPAs for {{ user.moa_organization.name }}.
        {% else %}
            You do not have permission to manage this PPA.
        {% endif %}
    </p>
{% endif %}
```

### 4. Filter PPAs by User's MOA

```django
{% load moa_rbac %}

{% filter_user_ppas user all_ppas as user_ppas %}
<h3>Your PPAs ({{ user_ppas.count }})</h3>
<ul>
    {% for ppa in user_ppas %}
        <li>{{ ppa.title }} - {{ ppa.status }}</li>
    {% endfor %}
</ul>
```

### 5. Get User's MOA Organization

```django
{% load moa_rbac %}

{% get_user_moa user as moa %}
{% if moa %}
    <div class="user-org-info">
        <strong>Your Organization:</strong> {{ moa.name }}
        <br>
        <small>{{ moa.organization_type }}</small>
    </div>
{% else %}
    <div class="alert alert-warning">
        No MOA organization assigned. Contact administrator.
    </div>
{% endif %}
```

### 6. Check Budget View Permission

```django
{% load moa_rbac %}

{% can_view_ppa_budget user ppa as can_view_budget %}
{% if can_view_budget %}
    <div class="budget-section">
        <h4>Budget Information</h4>
        <p>Allocation: ₱{{ ppa.budget_allocation|floatformat:2 }}</p>
        <p>Expenditure: ₱{{ ppa.actual_expenditure|floatformat:2 }}</p>
        <p>Remaining: ₱{{ ppa.remaining_budget|floatformat:2 }}</p>
    </div>
{% else %}
    <p class="text-muted">Budget information is restricted</p>
{% endif %}
```

### 7. Filter Navigation Menu

```django
{% load moa_rbac %}

<nav class="sidebar">
    <ul>
        {# All authenticated users can view communities #}
        {% can_view_communities user as can_view %}
        {% if can_view %}
            <li>
                <a href="{% url 'communities:community_list' %}">
                    <i class="fas fa-users"></i> OBC Communities
                </a>
            </li>
        {% endif %}

        {# Only OOBC staff can access MANA #}
        {% can_access_mana user as can_access_mana %}
        {% if can_access_mana %}
            <li>
                <a href="{% url 'mana:assessment_list' %}">
                    <i class="fas fa-clipboard-check"></i> MANA Assessments
                </a>
            </li>
        {% endif %}

        {# MOA and OOBC staff can create PPAs #}
        {% can_create_ppa user as can_create %}
        {% if can_create %}
            <li>
                <a href="{% url 'monitoring:ppa_create' %}">
                    <i class="fas fa-plus"></i> Create New PPA
                </a>
            </li>
        {% endif %}

        {# MOA users see their organization #}
        {% if user|has_moa_organization %}
            <li>
                <a href="{% url 'coordination:my_organization' %}">
                    <i class="fas fa-building"></i> My Organization
                </a>
            </li>
        {% endif %}
    </ul>
</nav>
```

### 8. Using Filter Tags

```django
{% load moa_rbac %}

{# Simple boolean filter #}
{% if user|has_moa_organization %}
    <p>You are linked to: {% user_moa_name user %}</p>
{% else %}
    <p class="alert alert-warning">
        No MOA organization assigned. Please contact your administrator.
    </p>
{% endif %}
```

---

## Admin Interface

### Assigning MOA Organization to Users

1. Navigate to Django Admin: `/admin/`
2. Go to **Users** section
3. Edit the MOA user account
4. Scroll to **MOA Access** fieldset
5. Select the organization from **MOA Organization** dropdown (autocomplete enabled)
6. Save the user

**Important:** Only assign `moa_organization` to users with `user_type` in `['bmoa', 'lgu', 'nga']`.

### Viewing MOA Focal Users

1. Navigate to **Coordination > Organizations**
2. Find an MOA/LGU/NGA organization
3. Click to edit
4. Scroll down to see **MOA Focal Users (System Users)** inline

The inline shows:
- Username (linked to user admin)
- User type
- Email and contact number
- Approval and active status

**Note:** Cannot add users via inline. Must assign `moa_organization` in User admin.

---

## Testing Your Code

### Running MOA RBAC Tests

```bash
cd src

# Test permission decorators and functions
python manage.py test common.tests.test_moa_permissions

# Test view mixins
python manage.py test common.tests.test_moa_mixins

# Test template tags
python manage.py test common.tests.test_moa_template_tags

# Run all MOA RBAC tests
python manage.py test common.tests.test_moa_permissions common.tests.test_moa_mixins common.tests.test_moa_template_tags
```

### Writing Your Own Tests

Example test for a protected view:

```python
from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from coordination.models import Organization

User = get_user_model()

class MyViewTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        self.moa = Organization.objects.create(
            name="Test MOA",
            organization_type="bmoa"
        )

        self.moa_user = User.objects.create_user(
            username="moa_test",
            password="testpass123",
            user_type="bmoa",
            moa_organization=self.moa,
            is_approved=True
        )

    def test_moa_user_can_view_own_org(self):
        """MOA user can view their own organization."""
        request = self.factory.get('/orgs/{}/'.format(self.moa.pk))
        request.user = self.moa_user

        response = my_view(request, pk=self.moa.pk)
        self.assertEqual(response.status_code, 200)
```

---

## Common Patterns

### Pattern 1: Protecting a View Function

```python
from common.utils.moa_permissions import moa_can_edit_ppa
from django.shortcuts import render, get_object_or_404

@moa_can_edit_ppa
def ppa_update(request, pk):
    ppa = get_object_or_404(MonitoringEntry, pk=pk)

    if request.method == 'POST':
        form = PPAForm(request.POST, instance=ppa)
        if form.is_valid():
            form.save()
            return redirect('ppa_detail', pk=ppa.pk)
    else:
        form = PPAForm(instance=ppa)

    return render(request, 'monitoring/ppa_form.html', {
        'form': form,
        'ppa': ppa
    })
```

### Pattern 2: Protecting a Class-Based View

```python
from django.views.generic import UpdateView
from common.mixins import MOAPPAAccessMixin

class PPAUpdateView(MOAPPAAccessMixin, UpdateView):
    model = MonitoringEntry
    form_class = PPAForm
    template_name = 'monitoring/ppa_form.html'
    success_url = reverse_lazy('ppa_list')
```

### Pattern 3: Conditional Template Rendering

```django
{% load moa_rbac %}

<div class="ppa-detail">
    <h1>{{ ppa.title }}</h1>

    {% can_manage_ppa user ppa as can_manage %}

    {# Show edit/delete buttons only if user can manage #}
    {% if can_manage %}
        <div class="ppa-actions">
            <a href="{% url 'ppa_edit' ppa.pk %}">Edit</a>
            <a href="{% url 'ppa_delete' ppa.pk %}">Delete</a>
        </div>
    {% else %}
        <p class="text-muted">View-only access</p>
    {% endif %}

    {# Budget information - restricted #}
    {% can_view_ppa_budget user ppa as can_view_budget %}
    {% if can_view_budget %}
        <div class="budget-info">
            <strong>Budget:</strong> ₱{{ ppa.budget_allocation }}
        </div>
    {% endif %}
</div>
```

---

## Troubleshooting

### Issue 1: MOA User Cannot Access Their Own Organization

**Symptoms:** MOA user gets 403 when trying to view/edit their organization

**Solution:**
1. Check if `user.moa_organization` is set (Admin > Users)
2. Verify organization ID matches
3. Check if user is approved (`is_approved=True`)
4. Check if organization is active (`is_active=True`)

```python
# Debug in Django shell
from django.contrib.auth import get_user_model
User = get_user_model()

user = User.objects.get(username='moa_test')
print(f"MOA Org: {user.moa_organization}")
print(f"Is Approved: {user.is_approved}")
print(f"User Type: {user.user_type}")
```

### Issue 2: Template Tag Returns Wrong Value

**Symptoms:** Template tag always returns False

**Solution:**
1. Verify `{% load moa_rbac %}` is present in template
2. Check context has `request` available
3. Verify user is authenticated
4. Check template tag syntax

```django
{# Correct syntax #}
{% load moa_rbac %}
{% can_manage_moa user organization as can_manage %}
{{ can_manage }}

{# WRONG - missing 'as' clause #}
{% can_manage_moa user organization %}
```

### Issue 3: Permission Denied When It Shouldn't Be

**Symptoms:** OOBC staff gets 403 on MOA-protected view

**Solution:**
1. Check decorator order (decorators apply bottom-to-top)
2. Verify `user.user_type == 'oobc_staff'`
3. Check if `is_approved=True`

```python
# Correct decorator order
@login_required  # Top
@moa_can_edit_ppa  # Bottom
def my_view(request, pk):
    pass

# WRONG - login_required should be outermost
@moa_can_edit_ppa
@login_required
def my_view(request, pk):
    pass
```

### Issue 4: Tests Failing

**Symptoms:** MOA RBAC tests fail unexpectedly

**Solution:**
1. Ensure test user has `is_approved=True`
2. Ensure organization is created before user
3. Check foreign key relationship is set correctly

```python
# Good test setup
def setUp(self):
    # 1. Create organization first
    self.moa = Organization.objects.create(
        name="Test MOA",
        organization_type="bmoa"
    )

    # 2. Create user with moa_organization
    self.moa_user = User.objects.create_user(
        username="moa_test",
        password="testpass123",
        user_type="bmoa",
        moa_organization=self.moa,  # Set FK
        is_approved=True  # Important!
    )
```

---

## Additional Resources

- **Design Document:** [MOA_RBAC_DESIGN.md](../improvements/MOA_RBAC_DESIGN.md)
- **Implementation Status:** [MOA_RBAC_IMPLEMENTATION_STATUS.md](../improvements/MOA_RBAC_IMPLEMENTATION_STATUS.md)
- **Test Files:**
  - `src/common/tests/test_moa_permissions.py`
  - `src/common/tests/test_moa_mixins.py`
  - `src/common/tests/test_moa_template_tags.py`

---

**Questions?** Contact the development team or consult the main design document.

# MOA Role-Based Access Control (RBAC) Design

**Status:** Design Phase
**Priority:** CRITICAL
**Created:** 2025-10-08
**Author:** System Architect

---

## Executive Summary

This document specifies a comprehensive Role-Based Access Control (RBAC) system for Ministry/Agency/Office (MOA) focal users in the OBCMS platform. The design enables MOA users to view OBC data, manage their organization profiles, and track their PPAs while maintaining strict isolation from OOBC internal operations.

**Key Design Decisions:**
- Add `moa_organization` ForeignKey to User model (requires migration)
- Implement defense-in-depth permission checks (view, model, template)
- Use Django's permission system with custom decorators
- Auto-filter QuerySets based on user's MOA organization
- Provide explicit permission denial messages

---

## Table of Contents

1. [Access Tier Specifications](#access-tier-specifications)
2. [Database Schema Changes](#database-schema-changes)
3. [Permission Architecture](#permission-architecture)
4. [Implementation Components](#implementation-components)
5. [View Protection Patterns](#view-protection-patterns)
6. [Template Permission Checks](#template-permission-checks)
7. [Testing Strategy](#testing-strategy)
8. [Security Considerations](#security-considerations)
9. [Migration Plan](#migration-plan)

---

## Access Tier Specifications

### Tier 1: View-Only Access

**What MOA users CAN VIEW:**

#### 1.1 OBC Communities Database (communities app)
- **Models:** `OBCCommunity`, `Barangay`, `Municipality`, `Province`, `Region`
- **Operations:** Read-only (GET requests)
- **UI:** Browse, search, filter, view details
- **Restrictions:** NO create, edit, delete
- **Purpose:** MOA users need to see which OBC communities exist for planning

#### 1.2 Policy Recommendations (policy_tracking app)
- **Models:** `PolicyRecommendation`
- **Filtering:** ONLY recommendations where `implementing_organizations` includes user's MOA
- **Operations:** Read-only
- **UI:** View recommendations tagged to their MOA
- **Restrictions:** Cannot create, edit, or view recommendations for other MOAs
- **Purpose:** See policy guidance relevant to their ministry

### Tier 2: View and Edit Access

**What MOA users CAN EDIT:**

#### 2.1 Organization Profile (coordination app)
- **Model:** `Organization`
- **Scope:** Own MOA organization only (`organization.id == user.moa_organization_id`)
- **Operations:** Read, update (NOT delete)
- **Fields Editable:**
  - Contact information (address, phone, email, website)
  - Key personnel (head, focal person, staff count)
  - Mandate and functions
  - Partnership information
  - Operational details
- **Purpose:** MOA maintains their own profile information

#### 2.2 MOA PPAs (monitoring app)
- **Model:** `MonitoringEntry`
- **Filtering:** `implementing_moa == user.moa_organization`
- **Operations:** Full CRUD (Create, Read, Update, Delete)
- **Related Objects:**
  - Create/edit MonitoringEntryFunding (funding tranches)
  - Create/edit MonitoringUpdate (progress updates)
  - Create/edit MonitoringEntryWorkflowStage (workflow stages)
  - Create/edit outcome indicators
- **Purpose:** MOA tracks their own PPAs and progress

#### 2.3 Work Items (common app)
- **Model:** `WorkItem`
- **Filtering:** `related_ppa.implementing_moa == user.moa_organization` OR `ppa_category == 'moa_ppa'` (via isolation fields)
- **Operations:** Full CRUD
- **Scope:** Work items linked to their MOA PPAs
- **Purpose:** MOA manages execution tasks for their projects

#### 2.4 Calendar Events (common app)
- **Models:** `CalendarResource`, `CalendarResourceBooking`
- **Filtering:** Events linked to their work items or MOA PPAs
- **Operations:** Create, read, update bookings
- **Purpose:** Schedule activities related to their PPAs

#### 2.5 Budget Tracking (monitoring app)
- **Fields:** `budget_allocation`, `actual_expenditure`, `funding_flows`
- **Scope:** Within their own MOA PPAs
- **Operations:** View, update budget data
- **Purpose:** Track financial execution of their PPAs

### Tier 3: No Access

**What MOA users CANNOT ACCESS:**

1. **MANA Assessments** (`mana.models.Assessment`) - Internal OOBC assessment tool
2. **Other MOAs' Organizations** - Cannot view or edit other MOA profiles
3. **Other MOAs' PPAs** - Cannot see PPAs implemented by other ministries
4. **OOBC Internal Modules:**
   - Staff management (except viewing staff profiles)
   - Internal coordination workflows
   - Admin panels (except basic profile management)
5. **User Approval** - Cannot approve other users (only OOBC staff)
6. **System Administration** - No access to Django admin for sensitive models

---

## Database Schema Changes

### Migration: Add moa_organization Foreign Key

**File:** `src/common/migrations/0031_add_moa_organization_fk.py`

```python
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0030_backfill_work_item_isolation_data'),
        ('coordination', '0015_auto_20250108_1234'),  # Replace with actual latest
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='moa_organization',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='moa_staff_users',
                to='coordination.organization',
                help_text='MOA organization this user belongs to (for MOA staff only)',
                verbose_name='MOA Organization'
            ),
        ),
        migrations.AddIndex(
            model_name='user',
            index=models.Index(fields=['user_type', 'moa_organization'], name='auth_user_type_moa_idx'),
        ),
    ]
```

### Data Migration: Backfill moa_organization from organization CharField

**File:** `src/common/migrations/0032_backfill_moa_organization.py`

```python
from django.db import migrations


def backfill_moa_organization(apps, schema_editor):
    """
    Backfill moa_organization FK from organization CharField.

    Matches MOA users to their Organization by name (case-insensitive).
    Logs warnings for users who cannot be matched.
    """
    User = apps.get_model('common', 'User')
    Organization = apps.get_model('coordination', 'Organization')

    moa_user_types = ['bmoa', 'lgu', 'nga']
    moa_users = User.objects.filter(user_type__in=moa_user_types, organization__isnull=False)

    matched_count = 0
    unmatched_count = 0

    for user in moa_users:
        if not user.organization:
            continue

        # Try to find matching organization (case-insensitive)
        try:
            org = Organization.objects.get(name__iexact=user.organization)
            user.moa_organization = org
            user.save(update_fields=['moa_organization'])
            matched_count += 1
        except Organization.DoesNotExist:
            unmatched_count += 1
            print(f"WARNING: Could not find organization for user {user.username}: '{user.organization}'")
        except Organization.MultipleObjectsReturned:
            # Multiple matches, take first
            org = Organization.objects.filter(name__iexact=user.organization).first()
            user.moa_organization = org
            user.save(update_fields=['moa_organization'])
            matched_count += 1
            print(f"WARNING: Multiple organizations matched for user {user.username}: '{user.organization}'. Using first match.")

    print(f"Backfill complete: {matched_count} users matched, {unmatched_count} users unmatched")


def reverse_backfill(apps, schema_editor):
    """Reverse migration: clear moa_organization FK."""
    User = apps.get_model('common', 'User')
    User.objects.filter(moa_organization__isnull=False).update(moa_organization=None)


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0031_add_moa_organization_fk'),
    ]

    operations = [
        migrations.RunPython(backfill_moa_organization, reverse_backfill),
    ]
```

### Updated User Model

**File:** `src/common/models.py`

```python
class User(AbstractUser):
    """Custom User model for the OBC Management System."""

    # ... existing fields ...

    organization = models.CharField(
        max_length=255,
        blank=True,
        help_text="Name of the organization (legacy field, kept for backward compatibility)"
    )

    # NEW FIELD
    moa_organization = models.ForeignKey(
        'coordination.Organization',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='moa_staff_users',
        help_text='MOA organization this user belongs to (for MOA staff only)',
        verbose_name='MOA Organization'
    )

    # ... existing properties ...

    @property
    def is_moa_staff(self):
        """Check if user is MOA staff (any type)."""
        return self.user_type in ['bmoa', 'lgu', 'nga']

    # NEW METHOD
    def owns_moa_organization(self, org_id):
        """Check if user's MOA organization matches the given org_id."""
        if not self.is_moa_staff or not self.moa_organization:
            return False
        return str(self.moa_organization.id) == str(org_id)

    # NEW METHOD
    def owns_moa_ppa(self, ppa_id):
        """Check if PPA belongs to user's MOA organization."""
        if not self.is_moa_staff or not self.moa_organization:
            return False

        from monitoring.models import MonitoringEntry
        try:
            ppa = MonitoringEntry.objects.get(pk=ppa_id)
            return ppa.implementing_moa == self.moa_organization
        except MonitoringEntry.DoesNotExist:
            return False

    # NEW METHOD
    def owns_work_item(self, work_item_id):
        """Check if work item belongs to user's MOA organization."""
        if not self.is_moa_staff or not self.moa_organization:
            return False

        from common.work_item_model import WorkItem
        try:
            work_item = WorkItem.objects.get(pk=work_item_id)
            # Check if work item is linked to MOA PPA
            if hasattr(work_item, 'related_ppa') and work_item.related_ppa:
                return work_item.related_ppa.implementing_moa == self.moa_organization
            return False
        except WorkItem.DoesNotExist:
            return False
```

---

## Permission Architecture

### Defense-in-Depth Strategy

OBCMS implements **three layers** of permission checks:

1. **View Layer** - Decorators on view functions/classes
2. **Model Layer** - Validation in save/delete methods
3. **Template Layer** - Conditional rendering based on permissions

**Critical:** All three layers MUST be implemented for production security.

### Permission Module Structure

```
src/common/permissions/
├── __init__.py
├── decorators.py          # View decorators
├── mixins.py              # View mixins
├── checks.py              # Permission check functions
└── templatetags/
    └── moa_permissions.py # Template permission tags
```

---

## Implementation Components

### 1. Permission Decorators

**File:** `src/common/permissions/decorators.py`

```python
"""Permission decorators for MOA RBAC."""

from functools import wraps
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404


def moa_view_only(model_name=None):
    """
    Decorator: Allow MOA users view-only access.

    Usage:
        @moa_view_only('OBCCommunity')
        def community_list(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if request.user.is_moa_staff:
                # Allow GET requests only
                if request.method not in ['GET', 'HEAD', 'OPTIONS']:
                    raise PermissionDenied(
                        f"MOA users have view-only access to {model_name or 'this resource'}. "
                        "You cannot create, edit, or delete."
                    )
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def moa_can_edit_organization(view_func):
    """
    Decorator: Allow MOA users to edit their own organization only.

    Usage:
        @moa_can_edit_organization
        def organization_update(request, pk):
            ...
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_moa_staff:
            org_id = kwargs.get('pk') or kwargs.get('organization_id')
            if org_id and not request.user.owns_moa_organization(org_id):
                raise PermissionDenied(
                    "You can only edit your own MOA organization. "
                    f"This organization does not belong to {request.user.moa_organization}."
                )
        return view_func(request, *args, **kwargs)
    return wrapper


def moa_can_edit_ppa(view_func):
    """
    Decorator: Allow MOA users to edit their own MOA PPAs only.

    Usage:
        @moa_can_edit_ppa
        def ppa_update(request, pk):
            ...
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_moa_staff:
            ppa_id = kwargs.get('pk') or kwargs.get('entry_id')
            if ppa_id:
                from monitoring.models import MonitoringEntry
                ppa = get_object_or_404(MonitoringEntry, pk=ppa_id)
                if ppa.implementing_moa != request.user.moa_organization:
                    raise PermissionDenied(
                        "You can only edit PPAs implemented by your MOA. "
                        f"This PPA belongs to {ppa.implementing_moa}."
                    )
        return view_func(request, *args, **kwargs)
    return wrapper


def moa_can_edit_work_item(view_func):
    """
    Decorator: Allow MOA users to edit work items for their PPAs only.

    Usage:
        @moa_can_edit_work_item
        def work_item_update(request, pk):
            ...
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_moa_staff:
            work_item_id = kwargs.get('pk') or kwargs.get('work_item_id')
            if work_item_id and not request.user.owns_work_item(work_item_id):
                raise PermissionDenied(
                    "You can only edit work items for your MOA's PPAs."
                )
        return view_func(request, *args, **kwargs)
    return wrapper


def moa_no_access(resource_name='this resource'):
    """
    Decorator: Block MOA users from accessing a view entirely.

    Usage:
        @moa_no_access('MANA Assessments')
        def assessment_list(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if request.user.is_moa_staff:
                raise PermissionDenied(
                    f"MOA users do not have access to {resource_name}. "
                    "This module is restricted to OOBC staff only."
                )
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator
```

### 2. QuerySet Filtering Mixin

**File:** `src/common/permissions/mixins.py`

```python
"""Permission mixins for class-based views."""

from django.core.exceptions import PermissionDenied
from django.db.models import Q


class MOAFilteredQuerySetMixin:
    """
    Mixin for ListView/DetailView that auto-filters querysets for MOA users.

    Usage:
        class PPAListView(MOAFilteredQuerySetMixin, ListView):
            model = MonitoringEntry
            moa_filter_field = 'implementing_moa'
    """
    moa_filter_field = None
    moa_allow_view_only = False

    def get_queryset(self):
        qs = super().get_queryset()

        if self.request.user.is_moa_staff and self.moa_filter_field:
            # Filter to user's MOA only
            filter_kwargs = {
                self.moa_filter_field: self.request.user.moa_organization
            }
            qs = qs.filter(**filter_kwargs)

        return qs

    def dispatch(self, request, *args, **kwargs):
        """Check view-only permissions for MOA users."""
        if request.user.is_moa_staff and not self.moa_allow_view_only:
            # Check if this is a write operation
            if request.method not in ['GET', 'HEAD', 'OPTIONS']:
                raise PermissionDenied(
                    "MOA users have view-only access to this resource."
                )
        return super().dispatch(request, *args, **kwargs)


class MOAOrganizationAccessMixin:
    """
    Mixin for restricting organization access to MOA's own organization.

    Usage:
        class OrganizationUpdateView(MOAOrganizationAccessMixin, UpdateView):
            model = Organization
    """

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)

        if self.request.user.is_moa_staff:
            if obj != self.request.user.moa_organization:
                raise PermissionDenied(
                    "You can only access your own MOA organization."
                )

        return obj


class MOAPPAAccessMixin:
    """
    Mixin for restricting PPA access to MOA's own PPAs.

    Usage:
        class PPAUpdateView(MOAPPAAccessMixin, UpdateView):
            model = MonitoringEntry
    """

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)

        if self.request.user.is_moa_staff:
            if obj.implementing_moa != self.request.user.moa_organization:
                raise PermissionDenied(
                    f"You can only access PPAs implemented by {self.request.user.moa_organization}."
                )

        return obj
```

### 3. Permission Template Tags

**File:** `src/common/templatetags/moa_permissions.py`

```python
"""Template tags for MOA permission checks."""

from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def user_can_edit_organization(context, organization):
    """Check if current user can edit the organization."""
    user = context['request'].user

    if user.is_superuser:
        return True
    if user.is_oobc_staff:
        return True
    if user.is_moa_staff:
        return user.moa_organization == organization

    return False


@register.simple_tag(takes_context=True)
def user_can_edit_ppa(context, ppa):
    """Check if current user can edit the PPA."""
    user = context['request'].user

    if user.is_superuser:
        return True
    if user.is_oobc_staff:
        return True
    if user.is_moa_staff:
        return ppa.implementing_moa == user.moa_organization

    return False


@register.simple_tag(takes_context=True)
def user_can_view_ppa(context, ppa):
    """Check if current user can view the PPA."""
    user = context['request'].user

    if user.is_superuser or user.is_oobc_staff:
        return True
    if user.is_moa_staff:
        # MOA can view their own PPAs
        return ppa.implementing_moa == user.moa_organization

    return False


@register.simple_tag(takes_context=True)
def user_can_delete_ppa(context, ppa):
    """Check if current user can delete the PPA."""
    user = context['request'].user

    if user.is_superuser:
        return True
    if user.is_oobc_staff:
        return True
    if user.is_moa_staff:
        # MOA can delete their own PPAs
        return ppa.implementing_moa == user.moa_organization

    return False


@register.simple_tag(takes_context=True)
def user_can_create_ppa(context):
    """Check if current user can create PPAs."""
    user = context['request'].user

    # OOBC staff and MOA staff can create PPAs
    return user.is_oobc_staff or user.is_moa_staff


@register.simple_tag(takes_context=True)
def user_can_view_community(context, community):
    """Check if current user can view OBC community details."""
    user = context['request'].user

    # Communities are viewable by all authenticated users
    # (this is a public dataset for planning purposes)
    return user.is_authenticated


@register.simple_tag(takes_context=True)
def user_can_access_mana(context):
    """Check if current user can access MANA module."""
    user = context['request'].user

    # MANA is OOBC staff only
    return user.is_oobc_staff or user.is_superuser


@register.filter
def has_moa_organization(user):
    """Check if user has an assigned MOA organization."""
    return user.is_moa_staff and user.moa_organization is not None
```

---

## View Protection Patterns

### Example 1: Communities ListView (View-Only for MOA)

**File:** `src/communities/views.py`

```python
from django.views.generic import ListView
from common.permissions.decorators import moa_view_only
from .models import OBCCommunity


@moa_view_only('OBC Communities')
def community_list(request):
    """List all OBC communities (view-only for MOA users)."""
    communities = OBCCommunity.objects.filter(is_active=True)
    return render(request, 'communities/community_list.html', {
        'communities': communities
    })
```

### Example 2: Organization UpdateView (MOA Edits Own Only)

**File:** `src/coordination/views.py`

```python
from django.views.generic import UpdateView
from django.urls import reverse_lazy
from common.permissions.mixins import MOAOrganizationAccessMixin
from .models import Organization
from .forms import OrganizationForm


class OrganizationUpdateView(MOAOrganizationAccessMixin, UpdateView):
    """Update organization details (MOA can edit own organization only)."""
    model = Organization
    form_class = OrganizationForm
    template_name = 'coordination/organization_form.html'
    success_url = reverse_lazy('coordination:organization_detail')

    def get_queryset(self):
        qs = super().get_queryset()

        # Filter to user's MOA organization if MOA staff
        if self.request.user.is_moa_staff:
            qs = qs.filter(id=self.request.user.moa_organization.id)

        return qs
```

### Example 3: PPA ListView (Auto-Filtered for MOA)

**File:** `src/monitoring/views.py`

```python
from django.views.generic import ListView
from common.permissions.mixins import MOAFilteredQuerySetMixin
from .models import MonitoringEntry


class PPAListView(MOAFilteredQuerySetMixin, ListView):
    """List PPAs (auto-filtered to MOA's own PPAs)."""
    model = MonitoringEntry
    template_name = 'monitoring/ppa_list.html'
    context_object_name = 'ppas'
    moa_filter_field = 'implementing_moa'
    paginate_by = 20

    def get_queryset(self):
        qs = super().get_queryset()

        # Additional filtering
        qs = qs.filter(category='moa_ppa').order_by('-updated_at')

        return qs
```

### Example 4: MANA Module (No Access for MOA)

**File:** `src/mana/views.py`

```python
from django.views.generic import ListView
from common.permissions.decorators import moa_no_access
from .models import Assessment


@moa_no_access('MANA Assessments')
def assessment_list(request):
    """List MANA assessments (blocked for MOA users)."""
    assessments = Assessment.objects.all()
    return render(request, 'mana/assessment_list.html', {
        'assessments': assessments
    })
```

---

## Template Permission Checks

### Example 1: PPA Detail Page

**File:** `src/templates/monitoring/ppa_detail.html`

```django
{% load moa_permissions %}

<div class="ppa-detail">
    <h1>{{ ppa.title }}</h1>

    <div class="ppa-actions">
        {% user_can_edit_ppa ppa as can_edit %}
        {% user_can_delete_ppa ppa as can_delete %}

        {% if can_edit %}
        <a href="{% url 'monitoring:ppa_update' ppa.id %}" class="btn btn-primary">
            <i class="fas fa-edit"></i> Edit PPA
        </a>
        {% endif %}

        {% if can_delete %}
        <a href="{% url 'monitoring:ppa_delete' ppa.id %}" class="btn btn-danger">
            <i class="fas fa-trash"></i> Delete PPA
        </a>
        {% endif %}

        {% if not can_edit %}
        <p class="text-muted">
            <i class="fas fa-info-circle"></i>
            {% if user.is_moa_staff %}
                You can only edit PPAs implemented by {{ user.moa_organization }}.
            {% else %}
                You do not have permission to edit this PPA.
            {% endif %}
        </p>
        {% endif %}
    </div>

    <!-- PPA Details -->
    <div class="ppa-content">
        ...
    </div>
</div>
```

### Example 2: Navigation Menu Filtering

**File:** `src/templates/common/base.html`

```django
{% load moa_permissions %}

<nav class="sidebar">
    <ul>
        {% if user.is_oobc_staff %}
            <!-- Full navigation for OOBC -->
            <li><a href="{% url 'mana:assessment_list' %}">MANA Assessments</a></li>
            <li><a href="{% url 'coordination:organization_list' %}">All Organizations</a></li>
            <li><a href="{% url 'monitoring:ppa_list' %}">All PPAs</a></li>
            <li><a href="{% url 'common:staff_management' %}">Staff Management</a></li>

        {% elif user.is_moa_staff %}
            <!-- Limited navigation for MOA -->
            <li>
                <a href="{% url 'communities:community_list' %}">
                    <i class="fas fa-users"></i> OBC Communities (View Only)
                </a>
            </li>
            <li>
                <a href="{% url 'monitoring:my_ppa_list' %}">
                    <i class="fas fa-project-diagram"></i> My MOA PPAs
                </a>
            </li>
            <li>
                <a href="{% url 'common:my_work_items' %}">
                    <i class="fas fa-tasks"></i> My Work Items
                </a>
            </li>
            <li>
                <a href="{% url 'coordination:my_organization' %}">
                    <i class="fas fa-building"></i> My Organization Profile
                </a>
            </li>
            <li>
                <a href="{% url 'policy_tracking:my_recommendations' %}">
                    <i class="fas fa-file-alt"></i> My Policy Recommendations
                </a>
            </li>

            {% user_has_moa_organization user as has_org %}
            {% if not has_org %}
            <li class="alert alert-warning">
                <i class="fas fa-exclamation-triangle"></i>
                Your account is not linked to an MOA organization. Contact administrator.
            </li>
            {% endif %}
        {% endif %}
    </ul>
</nav>
```

---

## Testing Strategy

### Unit Tests

**File:** `src/common/tests/test_moa_permissions.py`

```python
"""Unit tests for MOA RBAC system."""

from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied

from coordination.models import Organization
from monitoring.models import MonitoringEntry
from common.permissions.decorators import (
    moa_view_only,
    moa_can_edit_organization,
    moa_can_edit_ppa,
)

User = get_user_model()


class MOAPermissionDecoratorTests(TestCase):
    """Test MOA permission decorators."""

    def setUp(self):
        """Create test users and organizations."""
        self.factory = RequestFactory()

        # Create MOA organizations
        self.moa_health = Organization.objects.create(
            name='Ministry of Health',
            organization_type='bmoa'
        )
        self.moa_education = Organization.objects.create(
            name='Ministry of Education',
            organization_type='bmoa'
        )

        # Create MOA user
        self.moa_user = User.objects.create_user(
            username='moa_focal',
            password='testpass123',
            user_type='bmoa',
            organization='Ministry of Health',
            moa_organization=self.moa_health,
            is_approved=True
        )

        # Create OOBC user
        self.oobc_user = User.objects.create_user(
            username='oobc_staff',
            password='testpass123',
            user_type='oobc_staff',
            is_approved=True
        )

    def test_moa_view_only_allows_get(self):
        """MOA users can make GET requests."""
        @moa_view_only('Test Resource')
        def test_view(request):
            return "OK"

        request = self.factory.get('/test/')
        request.user = self.moa_user

        result = test_view(request)
        self.assertEqual(result, "OK")

    def test_moa_view_only_blocks_post(self):
        """MOA users cannot make POST requests."""
        @moa_view_only('Test Resource')
        def test_view(request):
            return "OK"

        request = self.factory.post('/test/')
        request.user = self.moa_user

        with self.assertRaises(PermissionDenied):
            test_view(request)

    def test_moa_can_edit_own_organization(self):
        """MOA users can edit their own organization."""
        @moa_can_edit_organization
        def test_view(request, pk):
            return "OK"

        request = self.factory.post('/org/update/')
        request.user = self.moa_user

        result = test_view(request, pk=self.moa_health.id)
        self.assertEqual(result, "OK")

    def test_moa_cannot_edit_other_organization(self):
        """MOA users cannot edit other MOA organizations."""
        @moa_can_edit_organization
        def test_view(request, pk):
            return "OK"

        request = self.factory.post('/org/update/')
        request.user = self.moa_user

        with self.assertRaises(PermissionDenied):
            test_view(request, pk=self.moa_education.id)

    def test_oobc_user_bypasses_moa_restrictions(self):
        """OOBC users are not restricted by MOA decorators."""
        @moa_can_edit_organization
        def test_view(request, pk):
            return "OK"

        request = self.factory.post('/org/update/')
        request.user = self.oobc_user

        # Should not raise PermissionDenied
        result = test_view(request, pk=self.moa_education.id)
        self.assertEqual(result, "OK")


class MOAUserModelMethodTests(TestCase):
    """Test User model MOA permission methods."""

    def setUp(self):
        """Create test data."""
        self.moa_health = Organization.objects.create(
            name='Ministry of Health',
            organization_type='bmoa'
        )

        self.moa_user = User.objects.create_user(
            username='moa_focal',
            password='testpass123',
            user_type='bmoa',
            moa_organization=self.moa_health,
            is_approved=True
        )

        self.ppa = MonitoringEntry.objects.create(
            title='Health Training Program',
            category='moa_ppa',
            implementing_moa=self.moa_health,
            created_by=self.moa_user
        )

    def test_owns_moa_organization_true(self):
        """User owns their assigned MOA organization."""
        self.assertTrue(self.moa_user.owns_moa_organization(self.moa_health.id))

    def test_owns_moa_organization_false(self):
        """User does not own other MOA organizations."""
        other_moa = Organization.objects.create(
            name='Ministry of Education',
            organization_type='bmoa'
        )
        self.assertFalse(self.moa_user.owns_moa_organization(other_moa.id))

    def test_owns_moa_ppa_true(self):
        """User owns PPA implemented by their MOA."""
        self.assertTrue(self.moa_user.owns_moa_ppa(self.ppa.id))

    def test_owns_moa_ppa_false(self):
        """User does not own PPA from other MOA."""
        other_moa = Organization.objects.create(
            name='Ministry of Education',
            organization_type='bmoa'
        )
        other_ppa = MonitoringEntry.objects.create(
            title='Education Program',
            category='moa_ppa',
            implementing_moa=other_moa,
            created_by=self.moa_user
        )
        self.assertFalse(self.moa_user.owns_moa_ppa(other_ppa.id))
```

### Integration Tests

**File:** `src/tests/integration/test_moa_workflows.py`

```python
"""Integration tests for MOA user workflows."""

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

from coordination.models import Organization
from monitoring.models import MonitoringEntry

User = get_user_model()


class MOAUserWorkflowTests(TestCase):
    """Test complete workflows for MOA users."""

    def setUp(self):
        """Create test environment."""
        self.client = Client()

        # Create MOA organization
        self.moa = Organization.objects.create(
            name='Ministry of Health',
            organization_type='bmoa'
        )

        # Create MOA user
        self.moa_user = User.objects.create_user(
            username='moa_focal',
            password='testpass123',
            user_type='bmoa',
            moa_organization=self.moa,
            is_approved=True
        )

        # Login as MOA user
        self.client.login(username='moa_focal', password='testpass123')

    def test_moa_can_view_communities(self):
        """MOA user can view OBC communities."""
        response = self.client.get(reverse('communities:community_list'))
        self.assertEqual(response.status_code, 200)

    def test_moa_cannot_create_community(self):
        """MOA user cannot create OBC communities."""
        response = self.client.post(reverse('communities:community_create'), {
            'name': 'Test Community'
        })
        self.assertEqual(response.status_code, 403)  # Forbidden

    def test_moa_can_create_ppa(self):
        """MOA user can create PPAs for their MOA."""
        response = self.client.post(reverse('monitoring:ppa_create'), {
            'title': 'Health Training',
            'category': 'moa_ppa',
            'implementing_moa': self.moa.id,
            'status': 'planning',
        })
        self.assertIn(response.status_code, [200, 201, 302])  # Success or redirect

    def test_moa_can_edit_own_ppa(self):
        """MOA user can edit their own MOA's PPA."""
        ppa = MonitoringEntry.objects.create(
            title='Health Training',
            category='moa_ppa',
            implementing_moa=self.moa,
            created_by=self.moa_user
        )

        response = self.client.post(reverse('monitoring:ppa_update', args=[ppa.id]), {
            'title': 'Updated Health Training',
            'category': 'moa_ppa',
            'implementing_moa': self.moa.id,
            'status': 'ongoing',
        })
        self.assertIn(response.status_code, [200, 302])

    def test_moa_cannot_edit_other_moa_ppa(self):
        """MOA user cannot edit another MOA's PPA."""
        other_moa = Organization.objects.create(
            name='Ministry of Education',
            organization_type='bmoa'
        )
        other_ppa = MonitoringEntry.objects.create(
            title='Education Program',
            category='moa_ppa',
            implementing_moa=other_moa,
            created_by=self.moa_user
        )

        response = self.client.post(reverse('monitoring:ppa_update', args=[other_ppa.id]), {
            'title': 'Hacked Title',
        })
        self.assertEqual(response.status_code, 403)  # Forbidden
```

---

## Security Considerations

### 1. Defense in Depth

**Implementation Requirements:**
- ✅ **View-level checks** - Decorators on every view function
- ✅ **Model-level checks** - Validation in `save()` and `delete()` methods
- ✅ **Template-level checks** - Hide unauthorized UI elements
- ✅ **QuerySet filtering** - Auto-filter data by default

**Security Principle:** Fail closed - deny access unless explicitly allowed.

### 2. Audit Logging

All MOA user actions MUST be logged for compliance:

```python
# In views.py
import logging

moa_audit_logger = logging.getLogger('moa_audit')

@moa_can_edit_ppa
def ppa_update(request, pk):
    ppa = get_object_or_404(MonitoringEntry, pk=pk)

    # Log MOA user action
    moa_audit_logger.info(
        f"MOA user {request.user.username} ({request.user.moa_organization}) "
        f"updated PPA {ppa.id}: {ppa.title}"
    )

    # ... handle form submission ...
```

**Logging Configuration (`settings/base.py`):**
```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'moa_audit_file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'moa_audit.log',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'moa_audit': {
            'handlers': ['moa_audit_file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
```

### 3. Session Security

**Recommendations:**
- Use HTTPS in production (SSL/TLS)
- Set secure cookies: `SESSION_COOKIE_SECURE = True`
- Enable CSRF protection (Django default)
- Implement session timeout for MOA users (30 minutes)

```python
# settings/production.py
SESSION_COOKIE_AGE = 1800  # 30 minutes for MOA users
SESSION_SAVE_EVERY_REQUEST = True  # Refresh session on activity
```

### 4. SQL Injection Prevention

Django ORM protects against SQL injection by default. **Always use:**

```python
# ✅ GOOD - Parameterized query
MonitoringEntry.objects.filter(implementing_moa=user.moa_organization)

# ❌ BAD - Never use raw SQL with user input
cursor.execute(f"SELECT * FROM monitoring WHERE moa_id = {user_input}")
```

### 5. Permission Elevation Prevention

**Critical:** MOA users must NEVER be able to:
- Approve other users
- Change their own `user_type`
- Assign themselves to other MOA organizations
- Escalate to `is_superuser` or `is_staff`

**Implementation:** Remove these fields from MOA-accessible forms:

```python
# src/common/forms.py
class MOAUserProfileForm(forms.ModelForm):
    """Profile form for MOA users (restricted fields)."""

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'contact_number']
        # Exclude: user_type, is_superuser, is_staff, is_approved, moa_organization
```

---

## Migration Plan

### Phase 1: Foundation (Priority: CRITICAL)

**Dependencies:** None
**Complexity:** Moderate

**Tasks:**
1. ✅ Create migration `0031_add_moa_organization_fk.py`
2. ✅ Create data migration `0032_backfill_moa_organization.py`
3. ✅ Update `User` model with new methods (`owns_moa_organization`, etc.)
4. ✅ Test migrations in development environment
5. ✅ Verify backfill accuracy (check unmatched users)

**Validation:**
```bash
cd src
python manage.py makemigrations
python manage.py migrate
python manage.py shell
>>> from django.contrib.auth import get_user_model
>>> User = get_user_model()
>>> moa_users = User.objects.filter(user_type__in=['bmoa', 'lgu', 'nga'])
>>> for u in moa_users:
...     print(f"{u.username}: {u.moa_organization}")
```

### Phase 2: Permission Utilities (Priority: CRITICAL)

**Dependencies:** Phase 1 complete
**Complexity:** Moderate

**Tasks:**
1. ✅ Create `src/common/permissions/` module
2. ✅ Implement decorators (`decorators.py`)
3. ✅ Implement mixins (`mixins.py`)
4. ✅ Implement template tags (`templatetags/moa_permissions.py`)
5. ✅ Write unit tests for all utilities

**Validation:**
```bash
pytest src/common/tests/test_moa_permissions.py -v
```

### Phase 3: View Protection (Priority: HIGH)

**Dependencies:** Phase 2 complete
**Complexity:** Moderate

**Tasks by Module:**

**3.1 Communities Module (View-Only)**
- Apply `@moa_view_only` to:
  - `community_list`
  - `community_detail`
  - `barangay_detail`
  - `municipality_detail`
- Test: MOA can view, cannot create/edit/delete

**3.2 Coordination Module (Edit Own Organization)**
- Apply `@moa_can_edit_organization` to:
  - `organization_update`
- Apply `MOAOrganizationAccessMixin` to:
  - `OrganizationUpdateView`
- Filter organization list to show only user's MOA
- Test: MOA can edit own, cannot edit others

**3.3 Monitoring Module (Edit Own PPAs)**
- Apply `@moa_can_edit_ppa` to:
  - `ppa_create`
  - `ppa_update`
  - `ppa_delete`
- Apply `MOAPPAAccessMixin` to:
  - `PPAUpdateView`
  - `PPADetailView`
- Use `MOAFilteredQuerySetMixin` for:
  - `PPAListView` (filter by `implementing_moa`)
- Test: MOA can CRUD own PPAs, cannot access others

**3.4 MANA Module (No Access)**
- Apply `@moa_no_access` to:
  - `assessment_list`
  - `assessment_create`
  - `assessment_detail`
  - All MANA views
- Test: MOA gets 403 Forbidden

**3.5 Common Module (Work Items)**
- Apply `@moa_can_edit_work_item` to:
  - `work_item_update`
  - `work_item_delete`
- Filter work items by `related_ppa.implementing_moa`
- Test: MOA can edit work items for their PPAs only

### Phase 4: Template Updates (Priority: HIGH)

**Dependencies:** Phase 3 complete
**Complexity:** Simple

**Tasks:**
1. ✅ Update base template navigation (`base.html`)
2. ✅ Update PPA templates with permission checks
3. ✅ Update organization templates
4. ✅ Add permission denial messages
5. ✅ Hide unauthorized buttons/links

**Files to Update:**
- `src/templates/common/base.html`
- `src/templates/monitoring/ppa_detail.html`
- `src/templates/monitoring/ppa_list.html`
- `src/templates/coordination/organization_detail.html`
- `src/templates/communities/community_detail.html`

### Phase 5: Model-Level Security (Priority: MEDIUM)

**Dependencies:** Phases 1-4 complete
**Complexity:** Moderate

**Tasks:**
1. ✅ Add validation to `MonitoringEntry.save()`
2. ✅ Add validation to `MonitoringEntry.delete()`
3. ✅ Add validation to `Organization.save()`
4. ✅ Add pre-save signals for permission enforcement

**Example Implementation:**
```python
# src/monitoring/models.py
class MonitoringEntry(models.Model):
    # ... existing fields ...

    def save(self, *args, **kwargs):
        """Validate MOA user can only save their own PPAs."""
        # Get current user from thread-local storage or kwargs
        user = kwargs.pop('user', None)

        if user and user.is_moa_staff:
            if self.implementing_moa != user.moa_organization:
                raise PermissionDenied(
                    f"MOA users can only save PPAs for {user.moa_organization}"
                )

        super().save(*args, **kwargs)
```

### Phase 6: Testing & Verification (Priority: HIGH)

**Dependencies:** Phases 1-5 complete
**Complexity:** Moderate

**Tasks:**
1. ✅ Unit tests (permission utilities)
2. ✅ Integration tests (complete workflows)
3. ✅ Security tests (privilege escalation attempts)
4. ✅ Manual testing (user acceptance)

**Test Coverage Goals:**
- Unit tests: 100% coverage of permission utilities
- Integration tests: All MOA workflows covered
- Security tests: All attack vectors tested

### Phase 7: Documentation & Training (Priority: MEDIUM)

**Dependencies:** Phases 1-6 complete
**Complexity:** Simple

**Tasks:**
1. ✅ User guide for MOA focal users
2. ✅ Admin guide for managing MOA accounts
3. ✅ Developer guide for extending RBAC
4. ✅ Training sessions for MOA focal users

---

## Deployment Checklist

**Pre-Deployment:**
- [ ] All migrations tested in staging
- [ ] Backfill script validated (no unmatched users)
- [ ] Unit tests passing (100% coverage)
- [ ] Integration tests passing
- [ ] Security tests passing
- [ ] Code review completed
- [ ] Documentation updated

**Deployment Steps:**
1. [ ] Backup production database
2. [ ] Apply migrations (`0031`, `0032`)
3. [ ] Verify `moa_organization` populated correctly
4. [ ] Deploy updated codebase
5. [ ] Restart application servers
6. [ ] Run smoke tests (MOA user login, view communities, edit PPA)
7. [ ] Monitor error logs (first 24 hours)

**Post-Deployment:**
- [ ] Verify MOA users can access their PPAs
- [ ] Verify MOA users blocked from MANA
- [ ] Verify MOA users can edit own organization
- [ ] Collect feedback from MOA focal users
- [ ] Address any permission issues

---

## Appendix A: Complete Code Artifacts

### Migration 0031: Add moa_organization FK

**Location:** `src/common/migrations/0031_add_moa_organization_fk.py`

[See "Database Schema Changes" section above]

### Migration 0032: Backfill Data

**Location:** `src/common/migrations/0032_backfill_moa_organization.py`

[See "Database Schema Changes" section above]

### Permission Decorators

**Location:** `src/common/permissions/decorators.py`

[See "Implementation Components" section above]

### Permission Mixins

**Location:** `src/common/permissions/mixins.py`

[See "Implementation Components" section above]

### Template Tags

**Location:** `src/common/templatetags/moa_permissions.py`

[See "Implementation Components" section above]

---

## Appendix B: Security Audit Checklist

**Authorization Checks:**
- [ ] All community views protected (view-only)
- [ ] Organization views restricted (own MOA only)
- [ ] PPA views filtered (own MOA only)
- [ ] Work item views filtered (related PPAs)
- [ ] MANA views blocked (403)
- [ ] Admin interface restricted (no access)

**Data Isolation:**
- [ ] QuerySets auto-filtered by `implementing_moa`
- [ ] Form submissions validated
- [ ] Model save() validates ownership
- [ ] No cross-MOA data leakage

**Session Security:**
- [ ] HTTPS enforced (production)
- [ ] Secure cookies enabled
- [ ] CSRF protection active
- [ ] Session timeout configured

**Audit Logging:**
- [ ] MOA actions logged
- [ ] Failed permission checks logged
- [ ] Login/logout events logged
- [ ] Data modification tracked

---

## Appendix C: MOA User Guide

### Getting Started as an MOA User

**1. Login**
- Navigate to OBCMS login page
- Enter your credentials
- You will be redirected to MOA Dashboard

**2. Your Dashboard**

**What You Can Do:**
- View OBC communities (read-only)
- Manage your MOA organization profile
- Create and track your MOA's PPAs
- View policy recommendations for your MOA
- Manage work items for your PPAs

**What You Cannot Do:**
- Access MANA assessments (OOBC internal)
- Edit other MOAs' data
- Approve user accounts
- Access system administration

**3. Managing Your Organization**
- Navigate to "My Organization"
- Update contact information
- Update mandate and functions
- Update key personnel
- Changes are saved automatically

**4. Managing PPAs**
- Navigate to "My MOA PPAs"
- Click "Create New PPA"
- Fill in PPA details
- Submit for approval workflow
- Track progress and update status

**5. Need Help?**
- Contact OOBC support: support@oobc.gov.ph
- View help documentation: /help/moa-guide
- Report issues: /support/tickets

---

**END OF DOCUMENT**

**Next Steps:**
1. Review design with OOBC stakeholders
2. Obtain approval for database migration
3. Begin Phase 1 implementation (migrations)
4. Proceed through phases sequentially
5. Conduct security audit before production deployment

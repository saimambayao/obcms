# Django Permission Best Practices for OBCMS RBAC Implementation

**Document Type:** Research & Implementation Guide
**Created:** 2025-10-13
**Last Updated:** 2025-10-13
**Status:** Complete

---

## Executive Summary

This document provides comprehensive research on Django's permission system and best practices for implementing Role-Based Access Control (RBAC) in OBCMS. Based on analysis of the existing codebase and Django best practices, this guide provides practical recommendations for the RBAC implementation.

**Key Findings:**
- OBCMS already has a sophisticated custom permission system (MOA RBAC)
- Django's built-in permissions are used minimally (mainly in tests)
- Custom decorators, mixins, and model methods are the primary permission mechanism
- DRF permissions are implemented in budget execution module

---

## Table of Contents

1. [Current OBCMS Permission Infrastructure](#current-obcms-permission-infrastructure)
2. [Django's Built-in Permission Features](#djangos-built-in-permission-features)
3. [Best Practices for Custom Permissions](#best-practices-for-custom-permissions)
4. [RBAC Implementation Recommendations](#rbac-implementation-recommendations)
5. [Code Examples](#code-examples)
6. [Testing Strategies](#testing-strategies)

---

## Current OBCMS Permission Infrastructure

### 1. **Existing Permission Systems**

OBCMS has THREE distinct permission layers already implemented:

#### A. **MOA RBAC System** (✅ COMPLETE)

**Location:** `/Users/saidamenmambayao/Library/Mobile Documents/com~apple~CloudDocs/BTA/OOBC/obcms/src/common/`

**Components:**
- **User Model Extensions** (`models.py`):
  - `is_moa_staff` property
  - `is_oobc_staff` property
  - `owns_moa_organization(org)` method
  - `can_edit_ppa(ppa)` method
  - `can_view_ppa(ppa)` method
  - `can_delete_ppa(ppa)` method
  - `can_edit_work_item(work_item)` method

- **Custom Decorators** (`utils/permissions.py`):
  - `@moa_view_only` - View-only access
  - `@moa_can_edit_organization` - Organization editing
  - `@moa_can_edit_ppa` - PPA editing
  - `@moa_no_access` - Complete block

- **Custom Mixins** (`mixins.py`):
  - `MOAFilteredQuerySetMixin` - Auto-filter querysets
  - `MOAOrganizationAccessMixin` - Org access control
  - `MOAPPAAccessMixin` - PPA access control
  - `MOAViewOnlyMixin` - Read-only restrictions

- **Template Tags** (`templatetags/moa_rbac.py`):
  - `{% can_manage_moa user org as can_manage %}`
  - `{% can_manage_ppa user ppa as can_manage %}`
  - `{% filter_user_ppas user all_ppas as user_ppas %}`

**Documentation:**
- [MOA RBAC Quick Reference](/Users/saidamenmambayao/Library/Mobile Documents/com~apple~CloudDocs/BTA/OOBC/obcms/docs/improvements/MOA_RBAC_QUICK_REFERENCE.md)
- [MOA RBAC Usage Guide](/Users/saidamenmambayao/Library/Mobile Documents/com~apple~CloudDocs/BTA/OOBC/obcms/docs/development/MOA_RBAC_USAGE.md)

#### B. **Budget Execution Permissions** (✅ COMPLETE)

**Location:** `/Users/saidamenmambayao/Library/Mobile Documents/com~apple~CloudDocs/BTA/OOBC/obcms/src/budget_execution/permissions.py`

**Components:**
- **Permission Checkers:**
  - `is_budget_officer(user)` - Budget Officers group
  - `is_finance_director(user)` - Finance Directors group
  - `is_finance_staff(user)` - Finance Staff group
  - `can_disburse(user)` - Disbursement Officers

- **Function Decorators:**
  - `@budget_officer_required`
  - `@finance_director_required`
  - `@finance_staff_required`
  - `@disbursement_officer_required`

- **Class-Based View Mixins:**
  - `BudgetOfficerMixin`
  - `FinanceDirectorMixin`
  - `FinanceStaffMixin`
  - `DisbursementOfficerMixin`

- **DRF Permission Classes:**
  - `CanReleaseAllotment` (Budget officers)
  - `CanApproveAllotment` (Finance directors)
  - `CanCreateObligation` (Finance staff+)
  - `CanRecordDisbursement` (Disbursement privileges)

**Pattern:** Uses **Django Groups** (`user.groups.filter(name='Group Name')`)

#### C. **MANA Access Control Middleware** (✅ ACTIVE)

**Location:** `/Users/saidamenmambayao/Library/Mobile Documents/com~apple~CloudDocs/BTA/OOBC/obcms/src/common/middleware/access_control.py`

**Purpose:** Restrict MANA Participants/Facilitators to specific URLs

**Pattern:** Uses **Django Permissions** (`user.has_perm("mana.can_access_regional_mana")`)

**Allowed Access:**
- Provincial OBC management
- Regional MANA pages
- Own profile
- Logout

### 2. **Django Built-in Permission Usage**

**Current Usage:** MINIMAL (mostly in tests)

**Evidence from codebase:**

```python
# From coordination/tests/test_coordination_notes.py
permission = Permission.objects.get(
    codename='add_coordinationnote',
    content_type__app_label='coordination'
)

# From mana/facilitator_views.py
permission = Permission.objects.get(codename="can_facilitate_workshop")
participant.user.user_permissions.add(permission)
```

**Pattern:** Django's built-in `Permission` model is used primarily for:
1. Test setup (granting permissions to test users)
2. MANA workshop role assignment (facilitator permissions)
3. Not used for general authorization checks

---

## Django's Built-in Permission Features

### 1. **Permission Model** (`django.contrib.auth.models.Permission`)

**Structure:**
```python
Permission(
    name='Can add log entry',        # Human-readable name
    content_type=ContentType,        # Model this permission applies to
    codename='add_logentry'          # Permission identifier
)
```

**Auto-generated Permissions:**

For each model, Django automatically creates 4 permissions:
- `add_<modelname>` - Can create instances
- `change_<modelname>` - Can update instances
- `delete_<modelname>` - Can delete instances
- `view_<modelname>` - Can view instances

### 2. **Custom Model-Level Permissions**

**Define in Model Meta:**

```python
class BudgetAllocation(models.Model):
    # ... fields ...

    class Meta:
        permissions = [
            ('approve_budget', 'Can approve budget allocations'),
            ('override_limits', 'Can override budget limits'),
            ('view_financial_reports', 'Can view financial reports'),
        ]
```

**Benefits:**
- ✅ Registered in Django admin
- ✅ Queryable via `Permission.objects.get(codename='approve_budget')`
- ✅ Checkable via `user.has_perm('app_label.approve_budget')`

### 3. **Permission Checking Methods**

#### A. **User-level checks:**

```python
# Single permission
user.has_perm('app_label.permission_codename')

# Multiple permissions (AND)
user.has_perms(['app_label.perm1', 'app_label.perm2'])

# Object-level permission (requires custom backend)
user.has_perm('app_label.change_document', obj=document)
```

#### B. **View-level decorators:**

```python
from django.contrib.auth.decorators import permission_required

@permission_required('polls.add_poll', raise_exception=True)
def create_poll(request):
    ...

@permission_required(['polls.add_poll', 'polls.change_poll'])
def manage_poll(request, pk):
    ...
```

#### C. **Template checks:**

```django
{% if perms.polls.add_poll %}
    <a href="{% url 'create_poll' %}">Create Poll</a>
{% endif %}

{% if perms.polls %}
    <p>You have permissions in the polls app</p>
{% endif %}
```

### 4. **Groups** (`django.contrib.auth.models.Group`)

**Purpose:** Bundle permissions for role assignment

```python
# Create group
budget_officers = Group.objects.create(name='Budget Officers')

# Assign permissions
permissions = Permission.objects.filter(
    codename__in=['approve_budget', 'release_allotment']
)
budget_officers.permissions.set(permissions)

# Assign user to group
user.groups.add(budget_officers)

# Check group membership
if user.groups.filter(name='Budget Officers').exists():
    # User is a budget officer
```

**Best Practice Pattern (from budget_execution):**

```python
def is_budget_officer(user):
    if not user.is_authenticated:
        return False

    # Check group membership
    if user.groups.filter(name='Budget Officers').exists():
        return True

    # Fallback to superuser
    if user.is_superuser:
        return True

    return False
```

### 5. **Object-Level Permissions** (Advanced)

**Django's built-in `has_perm()` supports object-level checks:**

```python
user.has_perm('myapp.change_document', obj=document)
```

**Requires Custom Authentication Backend:**

```python
# backends.py
class ObjectPermissionBackend:
    def has_perm(self, user, perm, obj=None):
        if obj is None:
            return False  # Delegate to default backend

        # Custom logic
        if perm == 'myapp.change_document':
            return obj.owner == user or user.is_superuser

        return False

# settings.py
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',  # Default
    'myapp.backends.ObjectPermissionBackend',     # Custom
]
```

**OBCMS Alternative (Current Pattern):**

Instead of custom backend, OBCMS uses **model methods**:

```python
# From common/models.py User model
def can_edit_ppa(self, ppa):
    """Check if user can edit the given PPA."""
    if self.is_superuser or self.is_oobc_staff:
        return True
    if self.is_moa_staff:
        return ppa.implementing_moa == self.moa_organization
    return False
```

**This pattern is SIMPLER and more maintainable than custom backends.**

---

## Best Practices for Custom Permissions

### 1. **Three-Layer Permission Architecture** (✅ OBCMS Current Pattern)

**Layer 1: Model-Level Logic**

```python
class User(AbstractUser):
    @property
    def is_moa_staff(self):
        return self.user_type in ['bmoa', 'lgu', 'nga']

    def can_edit_ppa(self, ppa):
        if self.is_superuser or self.is_oobc_staff:
            return True
        if self.is_moa_staff:
            return ppa.implementing_moa == self.moa_organization
        return False
```

**Layer 2: View-Level Protection**

```python
# Decorator for function views
@moa_can_edit_ppa
def ppa_update(request, pk):
    ppa = get_object_or_404(MonitoringEntry, pk=pk)
    # ... logic ...

# Mixin for class-based views
class PPAUpdateView(MOAPPAAccessMixin, UpdateView):
    model = MonitoringEntry
    # ... config ...
```

**Layer 3: Template-Level Hiding**

```django
{% can_manage_ppa user ppa as can_manage %}
{% if can_manage %}
    <a href="{% url 'ppa_update' ppa.pk %}">Edit</a>
{% endif %}
```

**Why This Works:**
- ✅ Model methods provide single source of truth
- ✅ View decorators/mixins enforce security
- ✅ Templates provide UX (don't show unavailable actions)
- ✅ Easy to test each layer independently

### 2. **Decorator Pattern** (✅ Recommended)

**Function-Based Views:**

```python
from functools import wraps
from django.core.exceptions import PermissionDenied

def budget_officer_required(view_func):
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        if not is_budget_officer(request.user):
            raise PermissionDenied(
                "You must be a Budget Officer to access this page."
            )
        return view_func(request, *args, **kwargs)
    return wrapped_view

@budget_officer_required
def release_allotment(request, pk):
    # ... logic ...
```

**Benefits:**
- ✅ Clean, reusable
- ✅ Works with `@login_required`
- ✅ Clear error messages
- ✅ Testable in isolation

### 3. **Mixin Pattern** (✅ Recommended for CBVs)

**Class-Based Views:**

```python
class BudgetOfficerMixin:
    def dispatch(self, request, *args, **kwargs):
        if not is_budget_officer(request.user):
            raise PermissionDenied(
                "You must be a Budget Officer to access this page."
            )
        return super().dispatch(request, *args, **kwargs)

class AllotmentReleaseView(BudgetOfficerMixin, UpdateView):
    model = BudgetAllotment
    # ... config ...
```

**Benefits:**
- ✅ Composable (multiple mixins)
- ✅ Consistent with Django CBV patterns
- ✅ Easy to override in subclasses

### 4. **DRF Permission Classes** (✅ For APIs)

**Django REST Framework:**

```python
from rest_framework.permissions import BasePermission

class IsBudgetOfficer(BasePermission):
    message = "You must be a Budget Officer to perform this action."

    def has_permission(self, request, view):
        return is_budget_officer(request.user)

    def has_object_permission(self, request, view, obj):
        # Object-level check
        return is_budget_officer(request.user)

# Usage in ViewSet
class AllotmentViewSet(viewsets.ModelViewSet):
    permission_classes = [IsBudgetOfficer]
    # ... config ...
```

**Benefits:**
- ✅ Consistent with DRF patterns
- ✅ Works with API throttling, authentication
- ✅ Clear separation of concerns

### 5. **Group-Based Permissions** (✅ Recommended)

**When to use Django Groups:**

✅ **Use Groups When:**
- Roles are organization-wide (e.g., "Budget Officers", "Finance Directors")
- Multiple permissions should be bundled
- Permissions can be managed in Django admin
- Role assignment is relatively static

❌ **Don't Use Groups When:**
- Permissions are object-specific (e.g., "Can edit MY PPA")
- Permissions depend on relationships (e.g., MOA membership)
- Permissions change frequently based on context

**OBCMS Pattern:**

Budget module uses **Groups** (global roles):
```python
user.groups.filter(name='Budget Officers').exists()
```

MOA module uses **User properties** (contextual roles):
```python
user.is_moa_staff and user.moa_organization == ppa.implementing_moa
```

### 6. **Permission Naming Conventions**

**Follow Django Conventions:**

```python
class Meta:
    permissions = [
        # Format: (codename, human_readable_description)
        ('approve_budget', 'Can approve budget allocations'),
        ('override_limit', 'Can override budget limits'),
        ('view_financial_report', 'Can view financial reports'),
    ]
```

**Naming Rules:**
- ✅ Use verb_noun format (`approve_budget`, `view_report`)
- ✅ Keep codenames concise but clear
- ✅ Make descriptions user-friendly (shown in admin)
- ✅ Prefix app-specific permissions (`mana.can_facilitate_workshop`)

---

## RBAC Implementation Recommendations

### Recommendation 1: **Extend Existing MOA RBAC Pattern** (✅ Preferred)

**For BMMS implementation, follow the proven MOA RBAC pattern:**

1. **Define User Type Properties:**

```python
# In common/models.py User model
@property
def is_ministry_staff(self):
    """Check if user is Ministry staff (BMMS)."""
    return self.user_type == 'ministry_staff'

@property
def ministry_organization(self):
    """Get user's ministry organization."""
    return self.moa_organization  # Reuse existing field
```

2. **Add Permission Methods:**

```python
def can_edit_ministry_budget(self, budget):
    """Check if user can edit ministry budget."""
    if self.is_superuser:
        return True
    if self.is_ministry_staff:
        return budget.ministry == self.ministry_organization
    return False
```

3. **Create Decorators:**

```python
# In common/utils/bmms_permissions.py
def ministry_budget_access(view_func):
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        budget = get_object_or_404(MinistryBudget, pk=kwargs['pk'])
        if not request.user.can_edit_ministry_budget(budget):
            raise PermissionDenied(
                "You can only edit your ministry's budget."
            )
        return view_func(request, *args, **kwargs)
    return wrapped_view
```

4. **Create Mixins:**

```python
# In common/mixins.py
class MinistryBudgetAccessMixin:
    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if not self.request.user.can_edit_ministry_budget(obj):
            raise PermissionDenied(
                "You can only access your ministry's budget."
            )
        return obj
```

### Recommendation 2: **Use Groups for Fixed Roles** (✅ Recommended)

**For roles like Finance Director, Budget Officer:**

1. **Define Groups in Migration:**

```python
# In planning/migrations/XXXX_create_budget_groups.py
from django.db import migrations

def create_groups(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')

    # Create Ministry Finance Director group
    finance_group = Group.objects.create(name='Ministry Finance Directors')

    # Assign permissions
    permissions = Permission.objects.filter(
        codename__in=['approve_budget', 'override_limit']
    )
    finance_group.permissions.set(permissions)

class Migration(migrations.Migration):
    dependencies = [...]
    operations = [
        migrations.RunPython(create_groups),
    ]
```

2. **Check Group Membership:**

```python
def is_ministry_finance_director(user):
    if not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    return user.groups.filter(name='Ministry Finance Directors').exists()
```

### Recommendation 3: **Model-Level Custom Permissions** (✅ For Complex Logic)

**Define in Model Meta:**

```python
class MinistryBudget(models.Model):
    # ... fields ...

    class Meta:
        permissions = [
            ('approve_ministry_budget', 'Can approve ministry budgets'),
            ('reallocate_funds', 'Can reallocate funds between programs'),
            ('view_all_ministry_budgets', 'Can view all ministry budgets (OCM)'),
            ('override_budget_limits', 'Can override budget limits'),
        ]
```

**Check in Views:**

```python
if not request.user.has_perm('planning.approve_ministry_budget'):
    raise PermissionDenied("You cannot approve budgets.")
```

### Recommendation 4: **OCM Read-Only Access** (✅ CRITICAL)

**For Office of the Chief Minister (OCM) aggregated access:**

1. **Create OCM-specific permission:**

```python
class Meta:
    permissions = [
        ('view_aggregated_data', 'Can view aggregated ministry data (OCM)'),
    ]
```

2. **Assign to OCM Group:**

```python
ocm_group = Group.objects.get(name='OCM Analysts')
permission = Permission.objects.get(codename='view_aggregated_data')
ocm_group.permissions.add(permission)
```

3. **Filter Querysets in Views:**

```python
class MinistryBudgetListView(ListView):
    def get_queryset(self):
        qs = super().get_queryset()

        if self.request.user.has_perm('planning.view_aggregated_data'):
            # OCM can see all
            return qs.all()
        elif self.request.user.is_ministry_staff:
            # Ministry staff see only their own
            return qs.filter(ministry=self.request.user.ministry_organization)
        else:
            return qs.none()
```

### Recommendation 5: **Audit Logging Integration** (✅ CRITICAL)

**OBCMS already has AuditLog model** (`common/models.py`):

```python
class AuditLog(models.Model):
    action = models.CharField(choices=[('create', 'Create'), ('update', 'Update'), ('delete', 'Delete')])
    user = models.ForeignKey('common.User', ...)
    content_type = models.ForeignKey(ContentType, ...)
    object_id = models.UUIDField(...)
    changes = models.JSONField(default=dict)
    ip_address = models.GenericIPAddressField(...)
    # ...
```

**Integrate with Permissions:**

```python
@finance_director_required
def approve_budget(request, pk):
    budget = get_object_or_404(MinistryBudget, pk=pk)

    # Perform action
    old_status = budget.status
    budget.status = 'approved'
    budget.approved_by = request.user
    budget.save()

    # Log action
    AuditLog.objects.create(
        action='update',
        user=request.user,
        content_object=budget,
        changes={
            'old_status': old_status,
            'new_status': 'approved',
            'approved_by': request.user.id,
        },
        ip_address=request.META.get('REMOTE_ADDR'),
        user_agent=request.META.get('HTTP_USER_AGENT', ''),
        notes=f"Budget approved by {request.user.get_full_name()}",
    )
```

---

## Code Examples

### Example 1: Complete RBAC Implementation for Ministry Budget

```python
# ========== MODELS ==========
# planning/models.py

class MinistryBudget(models.Model):
    ministry = models.ForeignKey('coordination.Organization', on_delete=models.PROTECT)
    fiscal_year = models.PositiveIntegerField()
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    status = models.CharField(max_length=20, choices=[
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ])
    created_by = models.ForeignKey('common.User', on_delete=models.PROTECT)
    approved_by = models.ForeignKey('common.User', null=True, on_delete=models.SET_NULL, related_name='+')

    class Meta:
        permissions = [
            ('approve_ministry_budget', 'Can approve ministry budgets'),
            ('view_all_ministry_budgets', 'Can view all ministry budgets (OCM)'),
        ]

# ========== USER MODEL EXTENSION ==========
# common/models.py

class User(AbstractUser):
    # ... existing fields ...

    def can_view_ministry_budget(self, budget):
        """Check if user can view ministry budget."""
        # OCM can view all
        if self.has_perm('planning.view_all_ministry_budgets'):
            return True
        # Ministry staff can view own
        if self.is_ministry_staff:
            return budget.ministry == self.ministry_organization
        # Superusers can view all
        if self.is_superuser:
            return True
        return False

    def can_edit_ministry_budget(self, budget):
        """Check if user can edit ministry budget."""
        if self.is_superuser:
            return True
        # Only own ministry and not approved
        if self.is_ministry_staff:
            return (
                budget.ministry == self.ministry_organization and
                budget.status in ['draft', 'rejected']
            )
        return False

    def can_approve_ministry_budget(self, budget):
        """Check if user can approve ministry budget."""
        if self.is_superuser:
            return True
        # Finance directors with permission
        return self.has_perm('planning.approve_ministry_budget')

# ========== PERMISSIONS ==========
# planning/permissions.py

from functools import wraps
from django.core.exceptions import PermissionDenied

def ministry_budget_view_access(view_func):
    """Decorator to check if user can view ministry budget."""
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        budget = get_object_or_404(MinistryBudget, pk=kwargs['pk'])
        if not request.user.can_view_ministry_budget(budget):
            raise PermissionDenied(
                "You can only view your ministry's budget."
            )
        return view_func(request, *args, **kwargs)
    return wrapped_view

def ministry_budget_edit_access(view_func):
    """Decorator to check if user can edit ministry budget."""
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        budget = get_object_or_404(MinistryBudget, pk=kwargs['pk'])
        if not request.user.can_edit_ministry_budget(budget):
            raise PermissionDenied(
                "You can only edit your ministry's draft/rejected budgets."
            )
        return view_func(request, *args, **kwargs)
    return wrapped_view

class MinistryBudgetApprovalMixin:
    """Mixin to check if user can approve budget."""
    def dispatch(self, request, *args, **kwargs):
        budget = self.get_object()
        if not request.user.can_approve_ministry_budget(budget):
            raise PermissionDenied(
                "You do not have permission to approve budgets."
            )
        return super().dispatch(request, *args, **kwargs)

# ========== VIEWS ==========
# planning/views.py

@login_required
@ministry_budget_view_access
def budget_detail(request, pk):
    """View ministry budget details."""
    budget = get_object_or_404(MinistryBudget, pk=pk)
    return render(request, 'planning/budget_detail.html', {
        'budget': budget,
        'can_edit': request.user.can_edit_ministry_budget(budget),
        'can_approve': request.user.can_approve_ministry_budget(budget),
    })

class MinistryBudgetListView(ListView):
    """List ministry budgets (filtered by permission)."""
    model = MinistryBudget
    template_name = 'planning/budget_list.html'

    def get_queryset(self):
        qs = super().get_queryset()

        if self.request.user.has_perm('planning.view_all_ministry_budgets'):
            # OCM can see all
            return qs.all()
        elif self.request.user.is_ministry_staff:
            # Ministry staff see only their own
            return qs.filter(ministry=self.request.user.ministry_organization)
        else:
            return qs.none()

class MinistryBudgetApproveView(MinistryBudgetApprovalMixin, UpdateView):
    """Approve ministry budget."""
    model = MinistryBudget
    fields = []  # No fields to edit

    def form_valid(self, form):
        budget = form.instance
        budget.status = 'approved'
        budget.approved_by = self.request.user

        # Audit log
        AuditLog.objects.create(
            action='update',
            user=self.request.user,
            content_object=budget,
            changes={'status': 'approved'},
            ip_address=self.request.META.get('REMOTE_ADDR'),
        )

        return super().form_valid(form)

# ========== TEMPLATES ==========
# planning/templates/planning/budget_detail.html

{% if can_edit %}
    <a href="{% url 'planning:budget_update' budget.pk %}" class="btn btn-primary">
        Edit Budget
    </a>
{% endif %}

{% if can_approve %}
    <form method="post" action="{% url 'planning:budget_approve' budget.pk %}">
        {% csrf_token %}
        <button type="submit" class="btn btn-success">Approve Budget</button>
    </form>
{% endif %}
```

### Example 2: DRF API Permissions

```python
# planning/api_permissions.py

from rest_framework.permissions import BasePermission

class IsMinistryStaffOrOCM(BasePermission):
    """
    Permission class for Ministry Budget API.

    - OCM can view all
    - Ministry staff can view/edit own
    - Others blocked
    """

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        # OCM can view all
        if request.user.has_perm('planning.view_all_ministry_budgets'):
            return True

        # Ministry staff can access their own
        if request.user.is_ministry_staff:
            return True

        return False

    def has_object_permission(self, request, view, obj):
        # OCM can view all
        if request.user.has_perm('planning.view_all_ministry_budgets'):
            return request.method in ['GET', 'HEAD', 'OPTIONS']

        # Ministry staff can view/edit own
        if request.user.is_ministry_staff:
            if obj.ministry != request.user.ministry_organization:
                return False

            if request.method in ['GET', 'HEAD', 'OPTIONS']:
                return True

            # Can edit only draft/rejected
            return obj.status in ['draft', 'rejected']

        return False

# planning/api.py

class MinistryBudgetViewSet(viewsets.ModelViewSet):
    """API for Ministry Budgets."""
    queryset = MinistryBudget.objects.all()
    serializer_class = MinistryBudgetSerializer
    permission_classes = [IsMinistryStaffOrOCM]

    def get_queryset(self):
        qs = super().get_queryset()

        if self.request.user.has_perm('planning.view_all_ministry_budgets'):
            # OCM sees all
            return qs
        elif self.request.user.is_ministry_staff:
            # Ministry staff see own
            return qs.filter(ministry=self.request.user.ministry_organization)

        return qs.none()
```

---

## Testing Strategies

### 1. **Unit Tests for Permission Checkers**

```python
# planning/tests/test_permissions.py

from django.test import TestCase
from django.contrib.auth import get_user_model
from coordination.models import Organization
from planning.models import MinistryBudget

User = get_user_model()

class MinistryBudgetPermissionTests(TestCase):
    def setUp(self):
        self.ministry_a = Organization.objects.create(
            name="Ministry of Education",
            organization_type="bmoa"
        )
        self.ministry_b = Organization.objects.create(
            name="Ministry of Health",
            organization_type="bmoa"
        )

        self.budget_a = MinistryBudget.objects.create(
            ministry=self.ministry_a,
            fiscal_year=2025,
            amount=1000000,
            status='draft',
        )

        self.user_a = User.objects.create_user(
            username='ministry_a_staff',
            user_type='ministry_staff',
            ministry_organization=self.ministry_a,
        )

        self.user_b = User.objects.create_user(
            username='ministry_b_staff',
            user_type='ministry_staff',
            ministry_organization=self.ministry_b,
        )

        self.ocm_user = User.objects.create_user(
            username='ocm_analyst',
            user_type='cm_office',
        )
        # Grant OCM permission
        ocm_perm = Permission.objects.get(codename='view_all_ministry_budgets')
        self.ocm_user.user_permissions.add(ocm_perm)

    def test_ministry_staff_can_view_own_budget(self):
        """Ministry staff can view their own budget."""
        self.assertTrue(self.user_a.can_view_ministry_budget(self.budget_a))

    def test_ministry_staff_cannot_view_other_budget(self):
        """Ministry staff cannot view other ministry's budget."""
        self.assertFalse(self.user_b.can_view_ministry_budget(self.budget_a))

    def test_ocm_can_view_all_budgets(self):
        """OCM can view all ministry budgets."""
        self.assertTrue(self.ocm_user.can_view_ministry_budget(self.budget_a))

    def test_ministry_staff_can_edit_own_draft(self):
        """Ministry staff can edit their own draft budget."""
        self.assertTrue(self.user_a.can_edit_ministry_budget(self.budget_a))

    def test_ministry_staff_cannot_edit_approved(self):
        """Ministry staff cannot edit approved budget."""
        self.budget_a.status = 'approved'
        self.budget_a.save()
        self.assertFalse(self.user_a.can_edit_ministry_budget(self.budget_a))
```

### 2. **Integration Tests for Views**

```python
# planning/tests/test_views.py

from django.test import TestCase, Client
from django.urls import reverse

class MinistryBudgetViewTests(TestCase):
    def setUp(self):
        # ... same setup as above ...
        self.client = Client()

    def test_ministry_staff_can_access_own_budget(self):
        """Ministry staff can access their own budget detail page."""
        self.client.login(username='ministry_a_staff', password='password')
        response = self.client.get(
            reverse('planning:budget_detail', args=[self.budget_a.pk])
        )
        self.assertEqual(response.status_code, 200)

    def test_ministry_staff_blocked_from_other_budget(self):
        """Ministry staff blocked from other ministry's budget."""
        self.client.login(username='ministry_b_staff', password='password')
        response = self.client.get(
            reverse('planning:budget_detail', args=[self.budget_a.pk])
        )
        self.assertEqual(response.status_code, 403)  # PermissionDenied

    def test_ocm_can_access_all_budgets(self):
        """OCM can access all budgets."""
        self.client.login(username='ocm_analyst', password='password')
        response = self.client.get(reverse('planning:budget_list'))
        self.assertEqual(response.status_code, 200)
        # Should see all budgets
        self.assertContains(response, 'Ministry of Education')
        self.assertContains(response, 'Ministry of Health')
```

### 3. **API Permission Tests**

```python
# planning/tests/test_api.py

from rest_framework.test import APITestCase
from rest_framework import status

class MinistryBudgetAPITests(APITestCase):
    def setUp(self):
        # ... same setup ...

    def test_ministry_staff_can_list_own_budgets(self):
        """Ministry staff can list their own budgets via API."""
        self.client.force_authenticate(user=self.user_a)
        response = self.client.get('/api/planning/budgets/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['ministry'], self.ministry_a.id)

    def test_ministry_staff_cannot_access_other_budget(self):
        """Ministry staff cannot access other ministry's budget via API."""
        self.client.force_authenticate(user=self.user_b)
        response = self.client.get(f'/api/planning/budgets/{self.budget_a.pk}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_ocm_can_list_all_budgets_readonly(self):
        """OCM can list all budgets but cannot edit."""
        self.client.force_authenticate(user=self.ocm_user)

        # Can list all
        response = self.client.get('/api/planning/budgets/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # Both budgets

        # Cannot edit
        response = self.client.patch(
            f'/api/planning/budgets/{self.budget_a.pk}/',
            {'amount': 2000000}
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
```

---

## Summary & Action Items

### ✅ What OBCMS Already Has (Leverage These)

1. **MOA RBAC System** - Proven pattern for organization-scoped permissions
2. **Budget Execution Permissions** - Group-based role permissions
3. **User Model Methods** - Object-level permission checks
4. **Custom Decorators & Mixins** - View protection
5. **Template Tags** - Conditional rendering
6. **Audit Logging** - Complete audit trail infrastructure

### 📋 Recommendations for BMMS RBAC

1. **Extend MOA RBAC Pattern**
   - Add `is_ministry_staff` property
   - Create ministry budget permission methods
   - Build decorators/mixins following same pattern

2. **Use Django Groups for Fixed Roles**
   - Ministry Finance Directors
   - Budget Approvers
   - OCM Analysts

3. **Use Model Permissions for Complex Logic**
   - Object-level checks (ministry ownership)
   - Contextual permissions (draft vs approved)
   - Hierarchical access (OCM aggregation)

4. **Integrate Audit Logging**
   - Log all budget approvals
   - Track permission changes
   - Record access attempts

5. **Test Comprehensively**
   - Unit tests for permission checkers
   - Integration tests for views
   - API permission tests

### 🚫 What NOT to Do

❌ Don't use Django's object-level permission backends (too complex)
❌ Don't rely on template-only hiding (security by obscurity)
❌ Don't create permissions for simple property checks
❌ Don't bypass existing MOA RBAC infrastructure

### 📚 Additional Resources

**OBCMS Documentation:**
- [MOA RBAC Quick Reference](/Users/saidamenmambayao/Library/Mobile Documents/com~apple~CloudDocs/BTA/OOBC/obcms/docs/improvements/MOA_RBAC_QUICK_REFERENCE.md)
- [MOA RBAC Usage Guide](/Users/saidamenmambayao/Library/Mobile Documents/com~apple~CloudDocs/BTA/OOBC/obcms/docs/development/MOA_RBAC_USAGE.md)
- [Budget Execution Permissions](/Users/saidamenmambayao/Library/Mobile Documents/com~apple~CloudDocs/BTA/OOBC/obcms/src/budget_execution/permissions.py)

**Django Documentation:**
- [Django Permissions](https://docs.djangoproject.com/en/4.2/topics/auth/default/#permissions-and-authorization)
- [Custom Permissions](https://docs.djangoproject.com/en/4.2/topics/auth/customizing/#custom-permissions)
- [DRF Permissions](https://www.django-rest-framework.org/api-guide/permissions/)

---

**Document Status:** ✅ COMPLETE
**Next Steps:** Use this guide when implementing BMMS Phase 1 RBAC system

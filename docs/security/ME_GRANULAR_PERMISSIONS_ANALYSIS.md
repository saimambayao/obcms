# M&E Granular Permission Structure Analysis

**Date**: 2025-10-13
**Status**: Analysis Complete
**Priority**: HIGH

## Executive Summary

This document analyzes the current M&E (Monitoring & Evaluation) permission structure and proposes a granular permission hierarchy to enable fine-grained access control for different M&E operations.

---

## 1. Current Permission Structure

### 1.1 Meta Permissions in MonitoringEntry Model

**Finding**: ❌ **NO Meta permissions defined**

```python
# File: src/monitoring/models.py (lines 820-854)
class Meta:
    ordering = ["-updated_at", "-created_at"]
    verbose_name = "Monitoring Entry"
    verbose_name_plural = "Monitoring Entries"
    constraints = [...]  # DB constraints only, no permissions
```

**Issue**: The `MonitoringEntry` model lacks Django Meta `permissions` definitions. This means:
- No default Django permissions for view/add/change/delete
- No custom model-level permissions defined
- Relies entirely on RBAC feature-based permissions

### 1.2 Current RBAC Feature Structure

**Existing Feature**: `monitoring_access` (Added in migration 0045)

```python
# File: src/common/migrations/0045_add_monitoring_access_feature.py
Feature:
  - feature_key: 'monitoring_access'
  - name: 'Monitoring & Evaluation Module Access'
  - description: 'Access to M&E dashboards, metrics, and analytics'
  - module: 'monitoring'
  - category: 'module'

Permission:
  - codename: 'view_monitoring'
  - name: 'View M&E Module'
  - permission_type: 'view'
  - description: 'Can view monitoring and evaluation dashboards'
```

**Access Control**:
- ✅ Executive Director: **GRANTED** `view_monitoring`
- ✅ Deputy Executive Director: **GRANTED** `view_monitoring`
- ❌ OOBC Staff: **DENIED** (correctly restricted)

### 1.3 Permission Enforcement Points

#### A. Template Level (Navbar)

```django
<!-- File: src/templates/common/navbar.html -->
{% has_feature_access user 'monitoring_access' as can_access_monitoring %}
{% if can_access_monitoring %}
    <!-- Show M&E menu -->
{% endif %}
```

**Uses**: Custom template tag `has_feature_access` from RBAC system

#### B. View Level (Decorator Pattern)

```python
# File: src/monitoring/views.py
@login_required
def monitoring_dashboard(request):
    """Render the consolidated Monitoring & Evaluation workspace."""
    # Restrict access for MANA participants
    if hasattr(request.user, 'participant_profile'):
        raise PermissionDenied(...)
    # ... rest of view
```

**Current Pattern**:
- ✅ `@login_required` - Authentication required
- ❌ **NO RBAC decorator** - Permission check is manual, inline
- ❌ **NO granular permissions** - Single access level

#### C. MOA Staff Decorators

Three specialized decorators exist for MOA users:

```python
# File: src/common/utils/moa_permissions.py

1. @moa_can_edit_ppa
   - Checks: pk or entry_id in URL kwargs
   - Logic: request.user.can_edit_ppa(ppa)
   - Enforces: MOA users can only edit their own MOA PPAs

2. @moa_view_only
   - Checks: HTTP method
   - Logic: Block POST/PUT/PATCH/DELETE for MOA users
   - Enforces: GET/HEAD/OPTIONS only

3. @moa_no_access
   - Checks: user.is_moa_staff
   - Logic: Raise PermissionDenied for all MOA users
   - Enforces: Complete module lockout
```

**Usage in Monitoring Views**:
```python
@moa_can_edit_ppa  # Lines 2908, 3000, 3048
@login_required
@require_POST
def enable_workitem_tracking(request, pk):
    # WorkItem operations restricted to own MOA
```

---

## 2. View Operation Analysis

### 2.1 Read-Only vs Edit Operations

**Dashboard Views (Read-Only)**:
```python
@login_required
def monitoring_dashboard(request):           # Line 417
def monitoring_entry_detail(request, pk):    # Line 686
def moa_ppas_dashboard(request):             # Line 963
def oobc_initiatives_dashboard(request):     # Line 1707
def obc_requests_dashboard(request):         # Line 2070
```

**Create Operations**:
```python
@login_required
def create_moa_entry(request):               # Line 811
def create_oobc_entry(request):              # Line 873
def create_request_entry(request):           # Line 897
```

**Edit Operations (with MOA restrictions)**:
```python
@moa_can_edit_ppa
@login_required
@require_POST
def enable_workitem_tracking(request, pk):   # Line 2908
def disable_workitem_tracking(request, pk):  # Line 3000
def distribute_budget(request, pk):          # Line 3048
```

**Bulk Operations**:
```python
@login_required
def import_moa_data(request):                # Line 1404
def export_moa_data(request):                # Line 1483
def generate_moa_report(request):            # Line 1551
def bulk_update_moa_status(request):         # Line 1610
```

### 2.2 Permission Hierarchy Observed

**Current implicit hierarchy**:
1. **Module Access** (`monitoring_access.view_monitoring`)
   - Gates: Dashboard access, menu visibility
   - Users: Executives only

2. **Organization Ownership** (`@moa_can_edit_ppa`)
   - Gates: Edit PPA operations
   - Users: MOA staff (own PPAs only), OOBC staff (all)

3. **HTTP Method** (`@moa_view_only`)
   - Gates: POST/PUT/DELETE operations
   - Users: Blocks MOA from write operations

4. **Complete Lockout** (`@moa_no_access`)
   - Gates: MANA integration, OOBC internals
   - Users: MOA completely blocked

---

## 3. Template Tag Analysis

### 3.1 Custom Permission Checks

**Template Tag**: `can_access_oobc_initiatives`
```python
# File: src/common/templatetags/moa_rbac.py (line 216)
@register.filter(name="can_access_oobc_initiatives")
def can_access_oobc_initiatives(user):
    """Return True if the user can view OOBC initiatives."""
    user = _get_authenticated_user(user)
    if not user:
        return False
    return _has_staff_or_superpowers(user)  # Superuser OR is_oobc_staff
```

**Template Tag**: `can_access_me_analytics`
```python
# File: src/common/templatetags/moa_rbac.py (line 225)
@register.filter(name="can_access_me_analytics")
def can_access_me_analytics(user):
    """Return True if the user can view M&E analytics dashboards."""
    user = _get_authenticated_user(user)
    if not user:
        return False
    return _has_staff_or_superpowers(user)  # Superuser OR is_oobc_staff
```

**Helper Function**:
```python
def _has_staff_or_superpowers(user):
    """Helper that checks for superuser or OOBC staff privileges."""
    return bool(
        getattr(user, "is_superuser", False)
        or getattr(user, "is_oobc_staff", False)
    )
```

**Usage in Templates**:
```django
<!-- Desktop Navbar (line 236) -->
{% if user|can_access_oobc_initiatives %}
    <a href="{% url 'monitoring:oobc_initiatives_dashboard' %}">
        OOBC Initiatives
    </a>
{% endif %}

<!-- Desktop Navbar (line 252) -->
{% if user|can_access_me_analytics %}
    <a href="{% url 'monitoring:monitoring_dashboard' %}">
        M&E Analytics
    </a>
{% endif %}

<!-- Mobile Navbar (line 579) -->
{% if user|can_access_oobc_initiatives %}
    <!-- Mobile OOBC Initiatives link -->
{% endif %}

<!-- Mobile Navbar (line 589) -->
{% if user|can_access_me_analytics %}
    <!-- Mobile M&E Analytics link -->
{% endif %}
```

**Analysis**:
- ✅ Consistent enforcement: Desktop + Mobile
- ✅ Clear separation: OOBC Initiatives vs M&E Analytics
- ❌ Hardcoded logic: Not using RBAC feature system
- ❌ No granularity: Binary access (all or nothing)

---

## 4. Proposed Granular Permission Structure

### 4.1 Feature Hierarchy

**Root Feature**: `monitoring_access` (existing)

**Proposed Sub-Features**:

```python
# Level 1: Module Access (Read-Only)
monitoring_access
  ├── monitoring_access.view_dashboard      # View M&E dashboards
  ├── monitoring_access.view_ppas           # View PPA list
  ├── monitoring_access.view_analytics      # View analytics/metrics
  └── monitoring_access.view_reports        # View generated reports

# Level 2: Data Management (Edit)
monitoring_access.manage_ppas
  ├── monitoring_access.create_moa_ppa      # Create MOA PPAs
  ├── monitoring_access.edit_moa_ppa        # Edit MOA PPAs
  ├── monitoring_access.delete_moa_ppa      # Delete MOA PPAs
  ├── monitoring_access.create_oobc_ppa     # Create OOBC initiatives
  ├── monitoring_access.edit_oobc_ppa       # Edit OOBC initiatives
  └── monitoring_access.delete_oobc_ppa     # Delete OOBC initiatives

# Level 3: Advanced Operations
monitoring_access.advanced
  ├── monitoring_access.approve_ppa         # Approve PPAs (executives)
  ├── monitoring_access.manage_workitems    # Enable/disable WorkItem tracking
  ├── monitoring_access.distribute_budget   # Budget distribution operations
  ├── monitoring_access.bulk_operations     # Import/export/bulk update
  └── monitoring_access.manage_funding      # Funding flow management

# Level 4: Analytics & Reporting
monitoring_access.analytics
  ├── monitoring_access.view_oobc_initiatives  # OOBC Initiatives dashboard
  ├── monitoring_access.view_me_analytics      # M&E Analytics dashboard
  ├── monitoring_access.export_data            # Export M&E data
  └── monitoring_access.generate_reports       # Generate custom reports

# Level 5: OBC Requests (Separate Permission Domain)
obc_requests
  ├── obc_requests.view_requests            # View OBC requests
  ├── obc_requests.manage_requests          # Edit/update requests
  ├── obc_requests.review_requests          # Review and approve
  └── obc_requests.prioritize_requests      # Priority queue management
```

### 4.2 Permission Types by Feature

**RBAC Permission Model Structure**:
```python
# Feature: monitoring_access.view_ppas
Permissions:
  - view_ppa_list       (type: 'view')    # Can see PPA list
  - view_ppa_detail     (type: 'view')    # Can see PPA details
  - view_ppa_budget     (type: 'view')    # Can see budget info
  - view_ppa_workitems  (type: 'view')    # Can see work items

# Feature: monitoring_access.manage_ppas
Permissions:
  - create_ppa          (type: 'create')  # Can create new PPAs
  - edit_ppa            (type: 'edit')    # Can edit PPAs
  - delete_ppa          (type: 'delete')  # Can delete PPAs
  - change_ppa_status   (type: 'custom')  # Can change status

# Feature: monitoring_access.advanced
Permissions:
  - approve_ppa         (type: 'approve') # Can approve PPAs
  - manage_workitems    (type: 'custom')  # WorkItem operations
  - distribute_budget   (type: 'custom')  # Budget ops
  - bulk_update         (type: 'custom')  # Bulk operations
```

### 4.3 Role Permission Matrix

**Recommended Permission Assignments**:

| Role | View Dashboard | View PPAs | Create PPA | Edit PPA | Approve PPA | Advanced Ops | Analytics |
|------|---------------|-----------|------------|----------|-------------|--------------|-----------|
| **Executive Director** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Deputy Executive Director** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **OOBC Manager** | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ | ✅ |
| **OOBC Staff** | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **MOA Admin** | ✅ | ✅ (own) | ✅ (own) | ✅ (own) | ❌ | ❌ | ❌ |
| **MOA Manager** | ✅ | ✅ (own) | ✅ (own) | ✅ (own) | ❌ | ❌ | ❌ |
| **MOA Staff** | ✅ | ✅ (own) | ❌ | ❌ | ❌ | ❌ | ❌ |
| **MOA Viewer** | ✅ | ✅ (own) | ❌ | ❌ | ❌ | ❌ | ❌ |

**Legend**:
- ✅ = Full access
- ✅ (own) = Access to own organization's data only
- ❌ = No access

### 4.4 Organization-Scoped Permissions

**Multi-Tenant Permission Logic**:

```python
def user_has_permission(user, permission_code, ppa=None):
    """
    Check if user has permission with organization scoping.

    Args:
        user: User instance
        permission_code: e.g., 'monitoring_access.edit_ppa'
        ppa: Optional MonitoringEntry for object-level check

    Returns:
        bool: True if user has permission
    """
    # 1. Check direct user permissions (highest priority)
    direct_perm = user.direct_permissions.filter(
        permission__feature__feature_key=permission_code.split('.')[0],
        permission__codename=permission_code.split('.')[1],
        is_active=True,
        is_granted=True,
    ).first()

    if direct_perm:
        if direct_perm.is_expired:
            return False
        # Check organization scope
        if ppa and direct_perm.organization:
            return ppa.implementing_moa == direct_perm.organization
        return True

    # 2. Check role-based permissions
    user_roles = user.user_roles.filter(
        is_active=True,
    ).select_related('role')

    for user_role in user_roles:
        if user_role.is_expired:
            continue

        role = user_role.role
        role_perms = role.get_all_permissions()  # Includes parent role perms

        # Check if permission exists in role
        has_perm = Permission.objects.filter(
            id__in=role_perms,
            feature__feature_key=permission_code.split('.')[0],
            codename=permission_code.split('.')[1],
            is_active=True,
        ).exists()

        if has_perm:
            # Check organization scope
            if ppa and user_role.organization:
                return ppa.implementing_moa == user_role.organization
            return True

    # 3. Fallback to MOA ownership check (legacy)
    if ppa and user.is_moa_staff:
        return user.can_edit_ppa(ppa)

    return False
```

---

## 5. Implementation Recommendations

### 5.1 Migration Strategy

**Phase 1: Create New Features and Permissions**
```python
# Migration: 0046_add_granular_monitoring_permissions.py

def add_granular_permissions(apps, schema_editor):
    Feature = apps.get_model('common', 'Feature')
    Permission = apps.get_model('common', 'Permission')

    # Get existing root feature
    monitoring_root = Feature.objects.get(feature_key='monitoring_access')

    # Create view sub-features
    view_dashboard = Feature.objects.create(
        feature_key='monitoring_access.view_dashboard',
        name='View M&E Dashboard',
        description='Access to M&E dashboards and metrics',
        module='monitoring',
        category='view',
        parent=monitoring_root,
        is_active=True,
        sort_order=10,
    )

    view_ppas = Feature.objects.create(
        feature_key='monitoring_access.view_ppas',
        name='View PPAs',
        description='View PPA list and details',
        module='monitoring',
        category='view',
        parent=monitoring_root,
        is_active=True,
        sort_order=20,
    )

    # Create manage sub-features
    manage_ppas = Feature.objects.create(
        feature_key='monitoring_access.manage_ppas',
        name='Manage PPAs',
        description='Create, edit, delete PPAs',
        module='monitoring',
        category='manage',
        parent=monitoring_root,
        is_active=True,
        sort_order=30,
    )

    # Create permissions for each feature
    Permission.objects.create(
        feature=view_ppas,
        codename='view_ppa_list',
        name='View PPA List',
        permission_type='view',
        is_active=True,
    )

    Permission.objects.create(
        feature=manage_ppas,
        codename='create_ppa',
        name='Create PPA',
        permission_type='create',
        is_active=True,
    )

    # ... create remaining permissions
```

**Phase 2: Update View Decorators**
```python
# File: src/common/decorators/monitoring.py (NEW)

from functools import wraps
from django.core.exceptions import PermissionDenied
from common.services.rbac_service import user_has_permission

def require_monitoring_permission(permission_code, ppa_kwarg='pk'):
    """
    Decorator: Require specific monitoring permission.

    Args:
        permission_code: e.g., 'monitoring_access.edit_ppa'
        ppa_kwarg: URL kwarg name for PPA ID (for object-level checks)
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Get PPA if specified
            ppa = None
            if ppa_kwarg in kwargs:
                from monitoring.models import MonitoringEntry
                ppa_id = kwargs.get(ppa_kwarg)
                ppa = MonitoringEntry.objects.filter(pk=ppa_id).first()

            # Check permission
            if not user_has_permission(request.user, permission_code, ppa):
                raise PermissionDenied(
                    f"You do not have permission: {permission_code}"
                )

            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


# Usage in views.py
@login_required
@require_monitoring_permission('monitoring_access.view_dashboard')
def monitoring_dashboard(request):
    # ...

@login_required
@require_monitoring_permission('monitoring_access.edit_ppa', ppa_kwarg='pk')
def enable_workitem_tracking(request, pk):
    # ...
```

**Phase 3: Update Template Tags**
```python
# File: src/common/templatetags/monitoring_permissions.py (NEW)

from django import template
from common.services.rbac_service import user_has_permission

register = template.Library()

@register.filter(name="can_access_monitoring_dashboard")
def can_access_monitoring_dashboard(user):
    """Check if user can access M&E dashboard."""
    return user_has_permission(user, 'monitoring_access.view_dashboard')

@register.filter(name="can_manage_ppas")
def can_manage_ppas(user):
    """Check if user can manage PPAs."""
    return user_has_permission(user, 'monitoring_access.manage_ppas')

@register.simple_tag
def can_edit_ppa(user, ppa):
    """Check if user can edit specific PPA."""
    return user_has_permission(user, 'monitoring_access.edit_ppa', ppa)
```

**Phase 4: Backwards Compatibility**
```python
# Keep existing decorators working during transition
@moa_can_edit_ppa  # OLD - Will be deprecated
@require_monitoring_permission('monitoring_access.edit_ppa')  # NEW
@login_required
def some_view(request, pk):
    # Both decorators work, new one takes precedence
```

### 5.2 Testing Strategy

**Unit Tests**:
```python
# File: src/monitoring/tests/test_permissions.py

class MonitoringPermissionTests(TestCase):
    def setUp(self):
        # Create users with different roles
        self.executive = User.objects.create(...)
        self.oobc_staff = User.objects.create(...)
        self.moa_admin = User.objects.create(...)

        # Create PPAs
        self.oobc_ppa = MonitoringEntry.objects.create(...)
        self.moa_ppa = MonitoringEntry.objects.create(...)

    def test_executive_can_view_all_ppas(self):
        """Executives can view all PPAs."""
        self.assertTrue(
            user_has_permission(
                self.executive,
                'monitoring_access.view_ppas',
                self.oobc_ppa
            )
        )
        self.assertTrue(
            user_has_permission(
                self.executive,
                'monitoring_access.view_ppas',
                self.moa_ppa
            )
        )

    def test_moa_admin_can_only_view_own_ppas(self):
        """MOA admins can only view their organization's PPAs."""
        self.assertTrue(
            user_has_permission(
                self.moa_admin,
                'monitoring_access.view_ppas',
                self.moa_ppa
            )
        )
        self.assertFalse(
            user_has_permission(
                self.moa_admin,
                'monitoring_access.view_ppas',
                self.oobc_ppa
            )
        )

    def test_oobc_staff_cannot_access_monitoring(self):
        """OOBC staff cannot access M&E module."""
        self.assertFalse(
            user_has_permission(
                self.oobc_staff,
                'monitoring_access.view_dashboard'
            )
        )
```

**Integration Tests**:
```python
class MonitoringViewPermissionTests(TestCase):
    def test_dashboard_access_control(self):
        """Test dashboard access based on permissions."""
        # Executive can access
        self.client.force_login(self.executive)
        response = self.client.get('/monitoring/dashboard/')
        self.assertEqual(response.status_code, 200)

        # OOBC staff cannot access
        self.client.force_login(self.oobc_staff)
        response = self.client.get('/monitoring/dashboard/')
        self.assertEqual(response.status_code, 403)
```

---

## 6. Benefits of Granular Permissions

### 6.1 Security Improvements

✅ **Principle of Least Privilege**
- Users only get permissions they need
- Reduces attack surface
- Easier to audit access

✅ **Organization Data Isolation**
- MOA A cannot see MOA B data
- OCM gets read-only aggregated access
- Clear permission boundaries

✅ **Audit Trail**
- Track who can do what
- Permission change history
- Compliance-ready

### 6.2 Operational Benefits

✅ **Fine-Grained Control**
- Separate view from edit
- Progressive access levels
- Role-specific capabilities

✅ **Flexibility**
- Easy to add new permissions
- Temporary permission grants
- Emergency access procedures

✅ **BMMS-Ready**
- Scales to 44 MOAs
- Multi-tenant architecture
- OCM oversight built-in

### 6.3 User Experience

✅ **Clear Access Boundaries**
- Users know what they can do
- No confusing permission errors
- Role-appropriate UI

✅ **Progressive Disclosure**
- Show only relevant features
- Hide inaccessible options
- Context-aware menus

---

## 7. Migration Checklist

### 7.1 Database Changes

- [ ] Create migration `0046_add_granular_monitoring_permissions.py`
- [ ] Add sub-features under `monitoring_access`
- [ ] Create permissions for each feature
- [ ] Assign permissions to existing roles
- [ ] Test permission inheritance

### 7.2 Code Changes

- [ ] Create `src/common/decorators/monitoring.py`
- [ ] Implement `@require_monitoring_permission` decorator
- [ ] Update all monitoring views with new decorators
- [ ] Create `src/common/templatetags/monitoring_permissions.py`
- [ ] Update templates to use new permission checks
- [ ] Deprecate legacy permission checks (keep for compatibility)

### 7.3 Testing

- [ ] Write unit tests for permission checks
- [ ] Write integration tests for view access
- [ ] Test MOA data isolation
- [ ] Test executive access
- [ ] Test permission inheritance
- [ ] Test permission expiration
- [ ] Load test permission queries

### 7.4 Documentation

- [ ] Update RBAC documentation
- [ ] Create permission matrix reference
- [ ] Document new decorators and template tags
- [ ] Update deployment guide
- [ ] Create rollback procedure

---

## 8. Conclusion

The current M&E permission structure is **binary** (all-or-nothing access via `monitoring_access` feature) with **implicit** organization-scoped checks via decorators.

**Key Findings**:
1. ❌ No Meta permissions in MonitoringEntry model
2. ❌ No granular RBAC permissions beyond `view_monitoring`
3. ✅ Good decorator pattern for MOA restrictions (`@moa_can_edit_ppa`)
4. ✅ Template tags exist but hardcoded (`can_access_oobc_initiatives`)
5. ❌ No separation between view/edit/approve operations

**Recommended Implementation**:
- Create hierarchical feature structure under `monitoring_access`
- Implement granular permissions: view, create, edit, delete, approve, advanced
- Apply organization-scoped permission checks
- Use RBAC-based decorators instead of hardcoded logic
- Maintain backwards compatibility during migration

This approach provides **fine-grained access control** while maintaining **organization data isolation** and **BMMS scalability**.

---

**Next Steps**:
1. Review and approve permission structure
2. Implement Phase 1 migration (features + permissions)
3. Update views with new decorators
4. Update templates with new permission checks
5. Test thoroughly before deployment

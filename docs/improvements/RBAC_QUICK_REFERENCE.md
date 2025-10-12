# RBAC Quick Reference Guide

**Last Updated:** 2025-10-13
**Status:** Active

---

## Quick Start

### 1. Check if User Can Access a Feature

```python
from common.services import RBACService

# In a view
def my_view(request):
    if not RBACService.has_feature_access(
        request.user,
        'communities.barangay_obc',
        organization=request.organization
    ):
        raise PermissionDenied("No access to Barangay OBC")

    # ... view logic ...
```

### 2. Get All User Permissions

```python
from common.services import RBACService

# Get all permission IDs for a user
permission_ids = RBACService.get_user_permissions(
    user,
    organization=organization
)
```

### 3. Get Accessible Features for User

```python
from common.services import RBACService

# Get list of Feature objects user can access
features = RBACService.get_accessible_features(
    user,
    organization=organization
)

for feature in features:
    print(f"{feature.name}: {feature.url_pattern}")
```

---

## Models Quick Reference

### Feature
```python
from common.rbac_models import Feature

# Get feature
feature = Feature.objects.get(feature_key='communities.barangay_obc')

# Check if active
if feature.is_active:
    # ...

# Get parent feature
parent = feature.parent

# Get all permissions for feature
perms = feature.permissions.filter(is_active=True)
```

### Permission
```python
from common.rbac_models import Permission

# Get permission
perm = Permission.objects.get(
    feature__feature_key='communities.barangay_obc',
    codename='view'
)

# Full permission key
print(perm.full_permission_key)  # "communities.barangay_obc.view"
```

### Role
```python
from common.rbac_models import Role

# Get role
role = Role.objects.get(slug='oobc-staff')

# Get all permissions (including inherited)
all_perms = role.get_all_permissions()

# Check if system role
if role.is_system_role:
    # Cannot be deleted
    pass
```

### UserRole
```python
from common.rbac_models import UserRole

# Assign role to user
user_role = UserRole.objects.create(
    user=user,
    role=role,
    organization=organization,  # or None for system roles
    assigned_by=request.user
)

# Check if active and not expired
if user_role.is_active and not user_role.is_expired:
    # Role is valid
    pass
```

### UserPermission
```python
from common.rbac_models import UserPermission

# Grant direct permission to user
user_perm = UserPermission.objects.create(
    user=user,
    permission=permission,
    organization=organization,
    is_granted=True,  # True = grant, False = deny
    reason="Temporary elevated access for project",
    granted_by=request.user
)

# Deny permission (overrides role permissions)
user_perm_deny = UserPermission.objects.create(
    user=user,
    permission=permission,
    is_granted=False,  # Explicit denial
    reason="Security restriction",
    granted_by=request.user
)
```

---

## Common Queries

### Get All Features in a Module
```python
features = Feature.objects.filter(
    module='communities',
    is_active=True
).order_by('sort_order')
```

### Get Top-Level Navigation Features
```python
nav_features = Feature.objects.filter(
    category='navigation',
    is_active=True,
    parent__isnull=True
).order_by('sort_order')
```

### Get User's Active Roles
```python
from django.utils import timezone

user_roles = UserRole.objects.filter(
    user=user,
    is_active=True
).filter(
    models.Q(expires_at__isnull=True) |
    models.Q(expires_at__gt=timezone.now())
)
```

### Get Organization-Specific Roles
```python
org_roles = Role.objects.filter(
    scope='organization',
    is_active=True
)
```

### Check if User Has Direct Permission
```python
has_direct = UserPermission.objects.filter(
    user=user,
    permission=permission,
    is_active=True,
    is_granted=True
).exists()
```

---

## Permission Types

### Standard Permission Types

| Type | Codename | Description |
|------|----------|-------------|
| View | `view` | Can view/read the feature |
| Create | `create` | Can create new items |
| Edit | `edit` | Can edit existing items |
| Delete | `delete` | Can delete items |
| Approve | `approve` | Can approve submissions |
| Export | `export` | Can export data |

### Example: Check Specific Permission Type
```python
from common.rbac_models import Permission

# Get "edit" permission for feature
edit_perm = Permission.objects.get(
    feature__feature_key='communities.barangay_obc',
    codename='edit'
)
```

---

## Role Hierarchy

### System Roles (Global Access)

| Role | Level | Scope | Description |
|------|-------|-------|-------------|
| OOBC Admin | 5 | System | Full system access |
| OOBC Manager | 4 | System | Management access |
| OOBC Staff | 3 | System | Standard staff access |
| OOBC Viewer | 2 | System | Read-only access |
| OCM Analyst | 2 | System | Read-only aggregated |

### Organization Roles (MOA-Scoped)

| Role | Level | Scope | Description |
|------|-------|-------|-------------|
| MOA Admin | 4 | Organization | MOA administrator |
| MOA Manager | 3 | Organization | MOA manager |
| MOA Staff | 2 | Organization | MOA staff |
| MOA Viewer | 1 | Organization | MOA viewer |

---

## Caching

### Cache Keys Pattern
```
rbac:user:{user_id}:feature:{feature_key}:org:{org_id}
rbac:user:{user_id}:feature:{feature_key}  # No org context
```

### Clear User Cache
```python
from common.services import RBACService

# Clear all cache for user
RBACService.clear_cache(user_id=user.id)

# Clear cache for specific feature
RBACService.clear_cache(
    user_id=user.id,
    feature_key='communities.barangay_obc'
)
```

### Cache Timeout
- Default: 5 minutes (300 seconds)
- Configurable in `RBACService.CACHE_TIMEOUT`

---

## Management Commands

### Populate RBAC System
```bash
# Run all migration steps
python manage.py migrate_rbac_system --all

# Or run step by step:
python manage.py migrate_rbac_system --create-features
python manage.py migrate_rbac_system --create-roles
python manage.py migrate_rbac_system --assign-users
```

---

## Common Patterns

### Pattern 1: View Protection
```python
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from common.services import RBACService

@login_required
def protected_view(request):
    if not RBACService.has_feature_access(
        request.user,
        'feature.key',
        organization=request.organization
    ):
        raise PermissionDenied

    # ... view logic ...
```

### Pattern 2: Template Conditional
```django
{% if user.is_authenticated %}
    {# Check feature access in view and pass to template #}
    {% if can_edit %}
        <a href="{% url 'edit' %}">Edit</a>
    {% endif %}
{% endif %}
```

### Pattern 3: API Permission Check
```python
from rest_framework.decorators import api_view
from rest_framework.response import Response
from common.services import RBACService

@api_view(['GET'])
def api_endpoint(request):
    if not RBACService.has_feature_access(
        request.user,
        'api.endpoint',
        organization=request.organization
    ):
        return Response(
            {'error': 'Permission denied'},
            status=403
        )

    # ... API logic ...
```

### Pattern 4: Bulk Permission Check
```python
from common.services import RBACService

# Get all user permissions once
user_perms = RBACService.get_user_permissions(
    request.user,
    organization
)

# Check multiple features efficiently
features_to_check = [
    'communities.barangay_obc',
    'communities.municipal_obc',
    'communities.provincial_obc'
]

for feature_key in features_to_check:
    feature = Feature.objects.get(feature_key=feature_key)
    has_access = feature.permissions.filter(
        id__in=user_perms,
        is_active=True
    ).exists()

    if has_access:
        print(f"User has access to {feature.name}")
```

---

## Troubleshooting

### Problem: Permission check returns False unexpectedly

**Check:**
1. Is user authenticated?
2. Is feature active?
3. Does user have role with permission?
4. Is role active and not expired?
5. Is permission active?
6. Check cache (try with `use_cache=False`)

**Debug:**
```python
from common.services import RBACService

# Get all user permissions
perms = RBACService.get_user_permissions(user, organization)
print(f"User has {len(perms)} permissions")

# Check accessible features
features = RBACService.get_accessible_features(user, organization)
print(f"User can access {len(features)} features")

# Check specific feature without cache
has_access = RBACService.has_feature_access(
    user,
    'feature.key',
    organization,
    use_cache=False  # Bypass cache
)
```

### Problem: User can access wrong organization's data

**Check:**
1. Is organization context set correctly?
2. Is UserRole linked to correct organization?
3. Are organization filters applied in queries?

**Fix:**
```python
# Ensure organization context
organization = request.organization

# Or get from user
if user.is_moa_staff:
    organization = user.moa_organization

# Always pass organization to RBAC checks
has_access = RBACService.has_feature_access(
    user,
    'feature.key',
    organization=organization  # Required!
)
```

### Problem: Cache not invalidating

**Solution:**
```python
from common.services import RBACService

# Clear all RBAC cache
RBACService.clear_cache()

# Or for specific user
RBACService.clear_cache(user_id=user.id)
```

---

## Best Practices

### ✅ DO

1. **Always check permissions in views**
   ```python
   if not RBACService.has_feature_access(...):
       raise PermissionDenied
   ```

2. **Always include organization context for MOA users**
   ```python
   has_access = RBACService.has_feature_access(
       user, 'feature.key', organization=org
   )
   ```

3. **Use caching for frequently checked permissions**
   ```python
   # Cache enabled by default
   has_access = RBACService.has_feature_access(
       user, 'feature.key', use_cache=True
   )
   ```

4. **Invalidate cache when permissions change**
   ```python
   # After role assignment
   RBACService.clear_cache(user_id=user.id)
   ```

5. **Use direct permissions sparingly**
   ```python
   # Only for one-off grants or overrides
   UserPermission.objects.create(
       user=user,
       permission=perm,
       reason="Specific reason required"
   )
   ```

### ❌ DON'T

1. **Don't check permissions only in templates**
   - Always protect views first
   - Templates are just UI hiding, not security

2. **Don't skip organization context for MOA users**
   - MOA users MUST have organization context
   - Missing context = potential data leak

3. **Don't create duplicate features**
   - Check if feature exists first
   - Reuse existing feature keys

4. **Don't delete system roles**
   - System roles have `is_system_role=True`
   - Protected from deletion

5. **Don't bypass RBAC for "convenience"**
   - Always use RBACService methods
   - Don't query permissions directly without context

---

## Next Steps

- **Admin Interface:** Phase 2 - Build UI for role/permission management
- **Template Tags:** Create `{% load rbac_tags %}` for templates
- **Middleware:** Auto-check feature access based on URLs
- **Testing:** Comprehensive test suite for all scenarios

---

## Support

- **Documentation:** `/docs/improvements/PHASE1_RBAC_FOUNDATION_COMPLETE.md`
- **Architecture:** `/docs/improvements/NAVBAR_RBAC_ANALYSIS.md`
- **Best Practices:** `/docs/development/DJANGO_PERMISSIONS_RBAC_BEST_PRACTICES.md`
- **Source Code:** `/src/common/rbac_models.py`, `/src/common/services/rbac_service.py`

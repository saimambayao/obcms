# RBAC Backend Quick Reference

**Quick access guide for RBAC (Role-Based Access Control) backend views, forms, and URLs**

## 📋 Quick Access

### Files Created:
- `src/common/views/rbac_management.py` - RBAC views (500+ lines)
- `src/common/forms/rbac_forms.py` - RBAC forms (450+ lines)

### Files Modified:
- `src/common/urls.py` - Added RBAC URL patterns
- `src/common/forms/__init__.py` - Exported RBAC forms

## URL Patterns

```python
# User permissions management
path('rbac/users/', user_permissions_list, name='rbac_users')
path('rbac/user/<int:user_id>/permissions/', user_permissions_detail, name='rbac_user_permissions')

# Role assignment/removal (HTMX)
path('rbac/user/<int:user_id>/roles/assign/', user_role_assign, name='rbac_assign_role')
path('rbac/user/<int:user_id>/roles/<uuid:role_id>/remove/', user_role_remove, name='rbac_remove_role')

# Feature toggles (HTMX)
path('rbac/user/<int:user_id>/features/<uuid:feature_id>/toggle/', user_feature_toggle, name='rbac_toggle_feature')

# Bulk operations
path('rbac/bulk-assign/', bulk_assign_roles, name='rbac_bulk_assign')

# Configuration
path('rbac/roles/', role_list, name='rbac_roles')
path('rbac/features/', feature_list, name='rbac_features')
```

## View Functions

### user_permissions_list()
```python
# Paginated user list with role/permission info
GET /rbac/users/

Features:
- Search by name/email
- Filter by user type, role, organization
- HTMX partial updates
- 20 users per page

Permission: oobc_management.manage_user_permissions
```

### user_role_assign()
```python
# Assign role to user (HTMX)
POST /rbac/user/<user_id>/roles/assign/

Form Data:
- role: UUID (required)
- organization: UUID (optional)
- expires_at: datetime (optional)

Returns:
- HTMX success message + target refresh
- HTMX error message on validation failure

Permission: oobc_management.assign_user_roles
```

### user_feature_toggle()
```python
# Toggle feature access (HTMX)
POST /rbac/user/<user_id>/features/<feature_id>/toggle/

Form Data:
- is_granted: boolean
- organization: UUID (optional)
- expires_at: datetime (optional)
- reason: string (optional)

Permission: oobc_management.manage_feature_access
```

### bulk_assign_roles()
```python
# Bulk role assignment
POST /rbac/bulk-assign/

Form Data:
- users: List[int] (required)
- role: UUID (required)
- organization: UUID (optional)
- expires_at: datetime (optional)

Returns: Success/skip counts

Permission: oobc_management.assign_user_roles
```

## Forms

### UserRoleAssignmentForm
```python
from common.forms.rbac_forms import UserRoleAssignmentForm

form = UserRoleAssignmentForm(
    request.POST,
    request_user=request.user
)

Fields:
- role: ModelChoiceField (required)
- organization: ModelChoiceField (optional)
- expires_at: DateTimeField (optional)

Validation:
- Org required for org-scoped roles
- System roles cannot have org context
- Expiration must be future
```

### BulkRoleAssignmentForm
```python
from common.forms.rbac_forms import BulkRoleAssignmentForm

form = BulkRoleAssignmentForm(
    request.POST,
    request_user=request.user
)

Fields:
- users: ModelMultipleChoiceField (required)
- role: ModelChoiceField (required)
- organization: ModelChoiceField (optional)
- expires_at: DateTimeField (optional)
```

### FeatureToggleForm
```python
from common.forms.rbac_forms import FeatureToggleForm

form = FeatureToggleForm(
    request.POST,
    request_user=request.user,
    feature=feature_obj
)

Fields:
- is_granted: BooleanField (default: True)
- organization: ModelChoiceField (optional)
- expires_at: DateTimeField (optional)
- reason: CharField (optional)
```

## HTMX Helpers

### htmx_response()
```python
from common.views.rbac_management import htmx_response

# Smart template selection
return htmx_response(request, {
    'htmx': 'partials/user_list.html',
    'full': 'rbac/user_permissions_list.html'
}, context)
```

### htmx_success_message()
```python
from common.views.rbac_management import htmx_success_message

return htmx_success_message(
    "Role assigned successfully",
    target='#user-roles-list'
)

# Generates:
# HX-Trigger: {"showMessage": {"type": "success", "message": "..."}, "refreshTarget": "..."}
```

### htmx_error_message()
```python
from common.views.rbac_management import htmx_error_message

return htmx_error_message(
    "Validation failed",
    status=400
)

# Generates:
# HX-Trigger: {"showMessage": {"type": "error", "message": "..."}}
```

## Common Patterns

### 1. Assign Role with Org Context
```python
from common.rbac_models import Role, UserRole
from common.services.rbac_service import RBACService

role = Role.objects.get(slug='moa-manager')

UserRole.objects.create(
    user=user,
    role=role,
    organization=user.moa_organization,
    assigned_by=request.user
)

RBACService.clear_cache(user_id=user.id)
```

### 2. Enable Feature for User
```python
from common.rbac_models import Feature, UserPermission

feature = Feature.objects.get(feature_key='mana.regional_overview')
view_perm = feature.permissions.filter(permission_type='view').first()

UserPermission.objects.create(
    user=user,
    permission=view_perm,
    is_granted=True,
    granted_by=request.user,
    reason="Temporary access"
)

RBACService.clear_cache(user_id=user.id)
```

### 3. Bulk Role Assignment
```python
with transaction.atomic():
    for user in users:
        if not UserRole.objects.filter(
            user=user, role=role, is_active=True
        ).exists():
            UserRole.objects.create(
                user=user,
                role=role,
                organization=organization,
                assigned_by=request.user
            )
            RBACService.clear_cache(user_id=user.id)
```

## HTMX Frontend Examples

### Role Assignment Form
```html
<form hx-post="{% url 'common:rbac_assign_role' user.id %}"
      hx-target="#user-roles-list"
      hx-swap="innerHTML">
    <select name="role" class="form-select">
        {% for role in roles %}
        <option value="{{ role.id }}">{{ role.name }}</option>
        {% endfor %}
    </select>
    <button type="submit" class="btn btn-primary">Assign</button>
</form>
```

### Role Removal Button
```html
<button hx-post="{% url 'common:rbac_remove_role' user.id role.id %}"
        hx-confirm="Remove {{ role.name }} role?"
        hx-target="#user-roles-list"
        hx-swap="innerHTML"
        class="btn btn-danger btn-sm">
    Remove
</button>
```

### Feature Toggle Switch
```html
<input type="checkbox"
       {% if user_has_feature %}checked{% endif %}
       hx-post="{% url 'common:rbac_toggle_feature' user.id feature.id %}"
       hx-target="#user-features-list"
       hx-trigger="change"
       class="toggle-switch">
```

## Permission Checks

### Required Permissions:
```python
# Manage all user permissions
'oobc_management.manage_user_permissions'

# Assign/remove roles
'oobc_management.assign_user_roles'

# Toggle features
'oobc_management.manage_feature_access'

# View RBAC config
'oobc_management.view_rbac_config'
```

### Who Has Access:
- ✅ **Superusers**: Full RBAC management
- ✅ **OOBC Executives**: Full RBAC management
- ✅ **OOBC Staff**: Organization-scoped access
- ✅ **MOA Admins**: Their organization only

## Cache Management

### When to Clear:
```python
# After role assignment
RBACService.clear_cache(user_id=user.id)

# After permission change
RBACService.clear_cache(user_id=user.id, feature_key='communities.barangay')

# After bulk operations
for user in affected_users:
    RBACService.clear_cache(user_id=user.id)
```

### Cache Key Format:
```
rbac:user:{user_id}:feature:{feature_key}
rbac:user:{user_id}:feature:{feature_key}:org:{org_id}
```

## Error Handling

### Form Validation:
```python
if not form.is_valid():
    errors = '<br>'.join([
        f"{field}: {', '.join(errs)}"
        for field, errs in form.errors.items()
    ])
    return htmx_error_message(f"Validation errors:<br>{errors}", 400)
```

### Transaction Safety:
```python
try:
    with transaction.atomic():
        UserRole.objects.create(...)
        RBACService.clear_cache(user_id=user.id)
    return htmx_success_message("Success")
except Exception as e:
    return htmx_error_message(f"Failed: {str(e)}", 500)
```

## Integration with User Approvals

### Approval Flow with Role Assignment:
```python
def approve_moa_user(request, user_id):
    user = get_object_or_404(User, pk=user_id)

    # Approve user
    user.is_approved = True
    user.approved_by = request.user
    user.save()

    # Auto-assign role based on user type
    if user.user_type == 'bmoa':
        role = Role.objects.get(slug='moa-staff')
        UserRole.objects.create(
            user=user,
            role=role,
            organization=user.moa_organization,
            assigned_by=request.user
        )
        RBACService.clear_cache(user_id=user.id)

    return redirect('common:moa_approval_list')
```

## Next Steps (Frontend)

### Templates to Create:
1. `src/templates/common/rbac/user_permissions_list.html`
2. `src/templates/common/rbac/user_permissions_detail.html`
3. `src/templates/common/rbac/role_list.html`
4. `src/templates/common/rbac/feature_list.html`
5. `src/templates/common/rbac/partials/user_list.html`
6. `src/templates/common/rbac/partials/role_form.html`
7. `src/templates/common/rbac/partials/feature_toggle.html`

### UI Components:
- Role assignment modal (HTMX)
- Feature toggle switches
- Bulk assignment interface
- Permission matrix

## Related Documentation

- [RBAC Implementation Complete](./RBAC_BACKEND_IMPLEMENTATION_COMPLETE.md)
- [RBAC Models](../../src/common/rbac_models.py)
- [RBAC Service](../../src/common/services/rbac_service.py)
- [RBAC Decorators](../../src/common/decorators/rbac.py)

---

**Last Updated**: 2025-10-13
**Status**: Backend Complete, Frontend Pending

# RBAC Views Quick Reference

**Quick access guide for RBAC backend views implementation**

## View Functions Summary

### Dashboard & Listing

| View | URL Pattern | URL Name | Template |
|------|-------------|----------|----------|
| `rbac_dashboard` | `/rbac/` | `common:rbac_dashboard` | `common/rbac/dashboard.html` |
| `rbac_users_list` | `/rbac/users/list/` | `common:rbac_users_list` | `common/rbac/partials/users_grid.html` |
| `user_permissions_list` | `/rbac/users/` | `common:rbac_users` | `common/rbac/user_permissions_list.html` |
| `user_permissions_detail` | `/rbac/user/<id>/permissions/` | `common:rbac_user_permissions` | `common/rbac/user_permissions_detail.html` |

### Role Management (HTMX)

| View | URL Pattern | URL Name | Method | Template |
|------|-------------|----------|--------|----------|
| `rbac_role_assignment_form` | `/rbac/user/<id>/roles/form/` | `common:rbac_role_assignment_form` | GET | `common/rbac/partials/role_assignment_form.html` |
| `user_role_assign` | `/rbac/user/<id>/roles/assign/` | `common:rbac_role_assign` | POST | HTMX response |
| `user_role_remove` | `/rbac/user/<id>/roles/<role_id>/remove/` | `common:rbac_user_role_remove` | POST | HTMX response |

### Permission Management (HTMX)

| View | URL Pattern | URL Name | Method | Template |
|------|-------------|----------|--------|----------|
| `rbac_permission_grant_form` | `/rbac/user/<id>/permissions/grant/form/` | `common:rbac_permission_grant_form` | GET | `common/rbac/partials/permission_grant_form.html` |
| `rbac_permission_grant` | `/rbac/user/<id>/permissions/grant/` | `common:rbac_permission_grant` | POST | HTMX response |
| `rbac_permission_remove` | `/rbac/user/<id>/permissions/<perm_id>/remove/` | `common:rbac_permission_remove` | POST | HTMX response |

### Feature Toggles (HTMX)

| View | URL Pattern | URL Name | Method | Template |
|------|-------------|----------|--------|----------|
| `user_feature_toggle` | `/rbac/user/<id>/features/<feat_id>/toggle/` | `common:rbac_feature_toggle` | POST | HTMX response |

### Bulk Operations (HTMX)

| View | URL Pattern | URL Name | Method | Template |
|------|-------------|----------|--------|----------|
| `rbac_bulk_assign_form` | `/rbac/bulk/assign/form/` | `common:rbac_bulk_assign_form` | GET | `common/rbac/partials/bulk_assign_modal.html` |
| `bulk_assign_roles` | `/rbac/bulk/assign/` | `common:rbac_bulk_assign` | POST | HTMX response |
| `rbac_bulk_remove_roles` | `/rbac/bulk/remove/` | `common:rbac_bulk_remove_roles` | POST | HTMX response |

### Configuration Views

| View | URL Pattern | URL Name | Template |
|------|-------------|----------|----------|
| `role_list` | `/rbac/roles/` | `common:rbac_roles` | `common/rbac/role_list.html` |
| `feature_list` | `/rbac/features/` | `common:rbac_features` | `common/rbac/feature_list.html` |

## Permission Requirements

| View Function | Required Permission |
|---------------|-------------------|
| `rbac_dashboard` | `oobc_management.manage_user_permissions` |
| `rbac_users_list` | `oobc_management.manage_user_permissions` |
| `user_permissions_list` | `oobc_management.manage_user_permissions` |
| `user_permissions_detail` | `oobc_management.manage_user_permissions` |
| `rbac_role_assignment_form` | `oobc_management.manage_user_permissions` |
| `user_role_assign` | `oobc_management.assign_user_roles` |
| `user_role_remove` | `oobc_management.assign_user_roles` |
| `user_feature_toggle` | `oobc_management.manage_feature_access` |
| `rbac_permission_grant_form` | `oobc_management.manage_user_permissions` |
| `rbac_permission_grant` | `oobc_management.manage_user_permissions` |
| `rbac_permission_remove` | `oobc_management.manage_user_permissions` |
| `rbac_bulk_assign_form` | `oobc_management.assign_user_roles` |
| `bulk_assign_roles` | `oobc_management.assign_user_roles` |
| `rbac_bulk_remove_roles` | `oobc_management.assign_user_roles` |
| `role_list` | `oobc_management.view_rbac_config` |
| `feature_list` | `oobc_management.view_rbac_config` |

## HTMX Integration Examples

### Loading User Permissions Modal
```html
<button hx-get="{% url 'common:rbac_user_permissions' user.id %}"
        hx-target="#rbac-modal-content"
        hx-swap="innerHTML"
        onclick="openRbacModal()">
    View Permissions
</button>
```

### Assigning a Role
```html
<button hx-get="{% url 'common:rbac_role_assignment_form' user.id %}"
        hx-target="#rbac-modal-content"
        hx-swap="innerHTML"
        onclick="openRbacModal()">
    Assign Role
</button>
```

### Removing a Role
```html
<button hx-delete="{% url 'common:rbac_user_role_remove' user.id role.id %}"
        hx-confirm="Remove role from this user?"
        hx-target="#rbac-modal-content"
        hx-swap="innerHTML">
    Remove Role
</button>
```

### Feature Toggle
```html
<input type="checkbox"
       hx-post="{% url 'common:rbac_feature_toggle' user.id feature.id %}"
       hx-trigger="change"
       hx-swap="none">
```

### Filtering Users
```html
<input type="text"
       hx-get="{% url 'common:rbac_users_list' %}"
       hx-trigger="keyup changed delay:500ms"
       hx-target="#users-grid"
       hx-include="#user-type-filter, #organization-filter">
```

### Bulk Role Assignment
```javascript
// Get selected user IDs
const userIds = Array.from(
    document.querySelectorAll('.user-checkbox:checked')
).map(cb => cb.value);

// Load bulk assignment form
htmx.ajax('GET',
    '{% url "common:rbac_bulk_assign_form" %}?user_ids=' + userIds.join(','),
    { target: '#rbac-modal-content' }
);
```

## Common Code Patterns

### HTMX Success Response
```python
from common.views.rbac_management import htmx_success_message

return htmx_success_message(
    "Operation completed successfully",
    target='#refresh-target'
)
```

### HTMX Error Response
```python
from common.views.rbac_management import htmx_error_message

return htmx_error_message(
    "Operation failed: error details",
    status=400
)
```

### Template Selection (HTMX vs Full)
```python
from common.views.rbac_management import htmx_response

template = {
    'htmx': 'common/rbac/partials/user_list.html',
    'full': 'common/rbac/user_permissions_list.html',
}

return htmx_response(request, template, context)
```

### Organization Context Filtering
```python
from common.services.rbac_service import RBACService

organization = RBACService.get_user_organization_context(request)

if organization:
    queryset = queryset.filter(
        Q(organization=organization) | Q(scope='system')
    )
```

### Cache Invalidation
```python
from common.services.rbac_service import RBACService

# After permission/role change
RBACService.clear_cache(user_id=user.id)
```

### Audit Logging
```python
from common.auditlog_config import log_model_change

log_model_change(
    request,
    user,
    'update',
    changes={'role_assigned': role.name}
)
```

## Testing Examples

### Test Dashboard View
```python
def test_rbac_dashboard(client, admin_user):
    client.force_login(admin_user)
    response = client.get(reverse('common:rbac_dashboard'))
    assert response.status_code == 200
    assert 'total_users' in response.context
    assert 'active_roles' in response.context
```

### Test Role Assignment
```python
def test_assign_role(client, admin_user, test_user, test_role):
    client.force_login(admin_user)
    response = client.post(
        reverse('common:rbac_role_assign', args=[test_user.id]),
        {'role': test_role.id}
    )
    assert response.status_code == 200
    assert UserRole.objects.filter(
        user=test_user,
        role=test_role,
        is_active=True
    ).exists()
```

### Test Permission Grant
```python
def test_grant_permission(client, admin_user, test_user, permission):
    client.force_login(admin_user)
    response = client.post(
        reverse('common:rbac_permission_grant', args=[test_user.id]),
        {
            'permission': permission.id,
            'reason': 'Test grant'
        }
    )
    assert response.status_code == 200
    assert UserPermission.objects.filter(
        user=test_user,
        permission=permission,
        is_active=True
    ).exists()
```

## Troubleshooting

### View Not Found (404)
- Check URL name matches template reference
- Verify view is imported in `common/urls.py`
- Run `python manage.py show_urls | grep rbac` to verify

### Permission Denied (403)
- Check user has required permission
- Verify RBAC decorator is correct
- Check organization context filtering

### HTMX Not Working
- Verify HTMX library is loaded in template
- Check `hx-target` selector exists in DOM
- Inspect browser console for errors
- Verify HTMX headers in response

### Cache Issues
- Ensure `RBACService.clear_cache()` is called after mutations
- Check Redis/cache backend is running
- Verify cache keys are correct

## Quick Commands

```bash
# Check Django configuration
python manage.py check

# List all RBAC URLs
python manage.py show_urls | grep rbac

# Create test data
python manage.py shell
>>> from common.rbac_models import Role, Permission, Feature
>>> # Create test roles, permissions, features

# Run RBAC tests
pytest src/common/tests/test_rbac*.py -v

# Check permission assignments
python manage.py shell
>>> from common.models import User
>>> user = User.objects.get(username='testuser')
>>> from common.services.rbac_service import RBACService
>>> RBACService.get_user_permissions(user)
```

## See Also

- [RBAC Backend Implementation Complete](./RBAC_BACKEND_VIEWS_IMPLEMENTATION_COMPLETE.md)
- [RBAC Frontend Implementation](./RBAC_FRONTEND_IMPLEMENTATION_COMPLETE.md)
- [RBAC Quick Reference](./RBAC_QUICK_REFERENCE.md)
- [OBCMS UI Standards](../ui/OBCMS_UI_STANDARDS_MASTER.md)

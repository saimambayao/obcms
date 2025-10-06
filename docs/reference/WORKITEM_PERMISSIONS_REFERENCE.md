# WorkItem Permissions Reference Card

**Quick reference for developers working with WorkItem permissions**

## Permission Function

### Usage
```python
from common.views.work_items import get_work_item_permissions

permissions = get_work_item_permissions(request.user, work_item)

if permissions['can_edit']:
    # Allow edit
    pass

if permissions['can_delete']:
    # Allow delete
    pass
```

### Return Value
```python
{
    'can_edit': bool,    # True if user can edit work item
    'can_delete': bool,  # True if user can delete work item
}
```

## Permission Logic Flow

```
┌─────────────────────────────────────────────────────────────┐
│              get_work_item_permissions(user, work_item)      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │ Is user the      │
                    │ creator?         │
                    │ (created_by)     │
                    └──────────────────┘
                              │
                      Yes ────┤──── No
                              │
                    ┌─────────▼─────────┐
                    │ ✅ can_edit: True  │
                    │ ✅ can_delete: True│
                    └────────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │ Is superuser?    │
                    └──────────────────┘
                              │
                      Yes ────┤──── No
                              │
                    ┌─────────▼─────────┐
                    │ ✅ can_edit: True  │
                    │ ✅ can_delete: True│
                    └────────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │ Check Django     │
                    │ permissions      │
                    └──────────────────┘
                              │
              ┌───────────────┴───────────────┐
              ▼                               ▼
    ┌──────────────────┐          ┌──────────────────┐
    │ has_perm         │          │ has_perm         │
    │ 'change_workitem'│          │ 'delete_workitem'│
    └──────────────────┘          └──────────────────┘
              │                               │
              ▼                               ▼
    ┌──────────────────┐          ┌──────────────────┐
    │ is_staff AND     │          │ is_staff AND     │
    │ has permission?  │          │ has permission?  │
    └──────────────────┘          └──────────────────┘
              │                               │
              ▼                               ▼
         can_edit                        can_delete
              │                               │
              └───────────────┬───────────────┘
                              ▼
                    ┌──────────────────┐
                    │ Is user assigned │
                    │ to work item?    │
                    └──────────────────┘
                              │
                      Yes ────┤──── No
                              │
                              ▼
                    ┌──────────────────┐
                    │ can_edit = True  │
                    └──────────────────┘
                              │
                              ▼
                    ┌──────────────────────┐
                    │ Return permissions   │
                    └──────────────────────┘
```

## Permission Scenarios

### Scenario 1: Work Item Owner
```python
# User A creates work item
work_item = WorkItem.objects.create(
    title="My Task",
    created_by=user_a,
    ...
)

# User A checks permissions
perms = get_work_item_permissions(user_a, work_item)
# Result: {'can_edit': True, 'can_delete': True}
```

### Scenario 2: Superuser
```python
# Any work item
work_item = WorkItem.objects.get(pk=some_id)

# Superuser checks permissions
perms = get_work_item_permissions(superuser, work_item)
# Result: {'can_edit': True, 'can_delete': True}
```

### Scenario 3: Staff with Change Permission
```python
# Grant permission
user_b.user_permissions.add(
    Permission.objects.get(codename='change_workitem')
)
user_b.is_staff = True
user_b.save()

# Check permissions on any work item
perms = get_work_item_permissions(user_b, work_item)
# Result: {'can_edit': True, 'can_delete': False}
```

### Scenario 4: Staff with Both Permissions
```python
# Grant both permissions
user_c.user_permissions.add(
    Permission.objects.get(codename='change_workitem'),
    Permission.objects.get(codename='delete_workitem')
)
user_c.is_staff = True
user_c.save()

# Check permissions on any work item
perms = get_work_item_permissions(user_c, work_item)
# Result: {'can_edit': True, 'can_delete': True}
```

### Scenario 5: Assigned User
```python
# Work item created by User A
work_item = WorkItem.objects.create(
    title="Collaborative Task",
    created_by=user_a,
    ...
)

# User B is assigned
work_item.assignees.add(user_b)

# User B checks permissions
perms = get_work_item_permissions(user_b, work_item)
# Result: {'can_edit': True, 'can_delete': False}
```

### Scenario 6: Regular User (No Access)
```python
# Work item created by User A
work_item = WorkItem.objects.create(
    title="Private Task",
    created_by=user_a,
    ...
)

# User C (not owner, not assigned, not staff) checks permissions
perms = get_work_item_permissions(user_c, work_item)
# Result: {'can_edit': False, 'can_delete': False}
```

## Django Permissions

### Permission Codes
- **Change Permission:** `common.change_workitem`
- **Delete Permission:** `common.delete_workitem`

### Granting Permissions via Admin
1. Navigate to `/admin/auth/user/{user_id}/change/`
2. Scroll to "User permissions" section
3. Add:
   - `common | work item | Can change work item`
   - `common | work item | Can delete work item`
4. Ensure user has `is_staff = True`

### Granting Permissions via Code
```python
from django.contrib.auth.models import Permission

# Get permissions
change_perm = Permission.objects.get(codename='change_workitem')
delete_perm = Permission.objects.get(codename='delete_workitem')

# Grant to user
user.user_permissions.add(change_perm, delete_perm)
user.is_staff = True
user.save()
```

### Creating Permission Groups
```python
from django.contrib.auth.models import Group, Permission

# Create group
work_item_managers = Group.objects.create(name='Work Item Managers')

# Add permissions
work_item_managers.permissions.add(
    Permission.objects.get(codename='change_workitem'),
    Permission.objects.get(codename='delete_workitem')
)

# Add users to group
user.groups.add(work_item_managers)
```

## View Implementation

### Detail View
```python
@login_required
def work_item_detail(request, pk):
    work_item = get_object_or_404(WorkItem, pk=pk)

    # Get permissions
    permissions = get_work_item_permissions(request.user, work_item)

    context = {
        'work_item': work_item,
        'can_edit': permissions['can_edit'],
        'can_delete': permissions['can_delete'],
    }

    return render(request, 'work_items/work_item_detail.html', context)
```

### Edit View
```python
@login_required
def work_item_edit(request, pk):
    work_item = get_object_or_404(WorkItem, pk=pk)

    # Check permissions
    permissions = get_work_item_permissions(request.user, work_item)
    if not permissions['can_edit']:
        raise PermissionDenied('You do not have permission to edit this work item.')

    # ... rest of edit logic
```

### Delete View
```python
@login_required
def work_item_delete(request, pk):
    work_item = get_object_or_404(WorkItem, pk=pk)

    # Check permissions
    permissions = get_work_item_permissions(request.user, work_item)
    if not permissions['can_delete']:
        if request.method == 'DELETE':
            # HTMX response
            return HttpResponse(status=403, headers={
                'HX-Trigger': json.dumps({
                    'showToast': {
                        'message': 'Permission denied',
                        'level': 'error'
                    }
                })
            })
        else:
            # Regular response
            raise PermissionDenied('You do not have permission to delete this work item.')

    # ... rest of delete logic
```

## Template Usage

```html
<!-- work_item_detail.html -->

{% if can_edit %}
<a href="{% url 'common:work_item_edit' work_item.pk %}"
   class="btn btn-primary">
    <i class="fas fa-edit"></i> Edit
</a>
{% endif %}

{% if can_delete %}
<a href="{% url 'common:work_item_delete' work_item.pk %}"
   class="btn btn-danger">
    <i class="fas fa-trash"></i> Delete
</a>
{% endif %}
```

## Testing Permissions

### Test Case: Owner
```python
def test_owner_has_full_permissions(self):
    user = User.objects.create_user('owner')
    work_item = WorkItem.objects.create(
        title="Test",
        created_by=user
    )

    perms = get_work_item_permissions(user, work_item)

    self.assertTrue(perms['can_edit'])
    self.assertTrue(perms['can_delete'])
```

### Test Case: Assigned User
```python
def test_assigned_user_can_edit_not_delete(self):
    owner = User.objects.create_user('owner')
    assignee = User.objects.create_user('assignee')

    work_item = WorkItem.objects.create(
        title="Test",
        created_by=owner
    )
    work_item.assignees.add(assignee)

    perms = get_work_item_permissions(assignee, work_item)

    self.assertTrue(perms['can_edit'])
    self.assertFalse(perms['can_delete'])
```

### Test Case: Staff with Permissions
```python
def test_staff_with_permissions(self):
    staff = User.objects.create_user('staff', is_staff=True)
    staff.user_permissions.add(
        Permission.objects.get(codename='change_workitem'),
        Permission.objects.get(codename='delete_workitem')
    )

    work_item = WorkItem.objects.create(
        title="Test",
        created_by=User.objects.create_user('other')
    )

    perms = get_work_item_permissions(staff, work_item)

    self.assertTrue(perms['can_edit'])
    self.assertTrue(perms['can_delete'])
```

### Test Case: Unauthorized User
```python
def test_unauthorized_user_denied(self):
    owner = User.objects.create_user('owner')
    other = User.objects.create_user('other')

    work_item = WorkItem.objects.create(
        title="Test",
        created_by=owner
    )

    perms = get_work_item_permissions(other, work_item)

    self.assertFalse(perms['can_edit'])
    self.assertFalse(perms['can_delete'])
```

## Troubleshooting

### User Can't Edit Work Items

**Check:**
1. Is user the owner? (`work_item.created_by == user`)
2. Is user assigned? (`user in work_item.assignees.all()`)
3. Is user staff? (`user.is_staff == True`)
4. Does user have permission? (`user.has_perm('common.change_workitem')`)

**Solution:**
```python
# Grant permission
from django.contrib.auth.models import Permission

user.is_staff = True
user.user_permissions.add(
    Permission.objects.get(codename='change_workitem')
)
user.save()
```

### User Can Edit But Not Delete

**This is expected behavior for assigned users.**

**Solution (if user should be able to delete):**
```python
user.user_permissions.add(
    Permission.objects.get(codename='delete_workitem')
)
user.save()
```

### Permission Denied Error in View

**Cause:** User lacks required permission

**Solution:**
1. Verify user is logged in
2. Check user role (owner, assignee, staff)
3. Grant appropriate permissions
4. Contact administrator if necessary

## Best Practices

### 1. Always Check Permissions Before Operations
```python
# ✅ GOOD
permissions = get_work_item_permissions(request.user, work_item)
if permissions['can_edit']:
    # Perform edit
    pass

# ❌ BAD
# Perform edit without checking
```

### 2. Use Consistent Error Messages
```python
# ✅ GOOD
raise PermissionDenied('You do not have permission to edit this work item.')

# ❌ BAD
raise Exception('No!')
```

### 3. Handle HTMX Requests Separately
```python
# ✅ GOOD
if request.method == 'DELETE':
    # HTMX-specific response
    return HttpResponse(status=403, headers={...})
else:
    # Regular response
    raise PermissionDenied(...)
```

### 4. Test All Permission Scenarios
- Test owner access
- Test superuser access
- Test staff with permissions
- Test assigned users
- Test unauthorized users

### 5. Document Permission Requirements
```python
@login_required
def work_item_edit(request, pk):
    """
    Edit work item.

    Permissions required:
    - Owner (created_by)
    - Superuser
    - Staff with 'change_workitem' permission
    - Assigned user
    """
    pass
```

## Related Documentation

- [WorkItem Permission Fix](/docs/improvements/WORKITEM_PERMISSION_FIX.md)
- [Django Permissions Guide](https://docs.djangoproject.com/en/5.0/topics/auth/default/)
- [WorkItem Model](/src/common/work_item_model.py)
- [WorkItem Views](/src/common/views/work_items.py)

## Quick Commands

```bash
# Check if user has permission
python manage.py shell
>>> from django.contrib.auth.models import User
>>> user = User.objects.get(username='testuser')
>>> user.has_perm('common.change_workitem')

# Grant permission
>>> from django.contrib.auth.models import Permission
>>> perm = Permission.objects.get(codename='change_workitem')
>>> user.user_permissions.add(perm)
>>> user.is_staff = True
>>> user.save()

# List user permissions
>>> user.get_all_permissions()
```

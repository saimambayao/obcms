# MOA RBAC Template Implementation

**Date:** 2025-10-08
**Status:** ✅ COMPLETE
**Author:** Claude Code (AI Coding Agent)

---

## Executive Summary

Successfully implemented MOA RBAC (Role-Based Access Control) permission checks in Django templates across the OBCMS system. MOA focal users now see only UI elements they have permission to access, creating a personalized, permission-aware user experience.

**Key Achievement:** All relevant templates now use the MOA RBAC template tag library to conditionally display UI elements based on user permissions.

---

## Overview

### Problem Statement

Before this implementation, all authenticated users saw the same navigation menus, edit/delete buttons, and action buttons regardless of their permissions. MOA focal users could see options they couldn't actually use, leading to confusion and potential security concerns.

### Solution

Integrated the MOA RBAC template tag library (`src/common/templatetags/moa_rbac.py`) into key templates to conditionally render UI elements based on user permissions. This creates a clean, permission-aware interface where users only see actions they can perform.

---

## Implementation Details

### 1. Navigation Templates ✅

**File:** `src/templates/common/navbar.html`

**Changes:**
- Added `{% load moa_rbac %}` at the top of the template
- Wrapped MANA navigation dropdown with `{% if user|can_access_mana %}`
- Applied to both desktop and mobile navigation menus

**Impact:**
- MOA focal users no longer see MANA module links (they don't have access to MANA)
- OOBC staff continue to see all navigation options
- Mobile and desktop navigation are consistent

**Code Example:**
```django
{% load moa_rbac %}
<!-- Desktop Navigation -->
{% if user|can_access_mana %}
<div class="relative group">
    <a href="{% url 'common:mana_home' %}" class="nav-item ...">
        <i class="fas fa-map-marked-alt"></i>
        <span>MANA</span>
    </a>
    <!-- MANA submenu items -->
</div>
{% endif %}

<!-- Mobile Navigation -->
{% if user|can_access_mana %}
<div class="mobile-section space-y-2">
    <!-- MANA mobile menu -->
</div>
{% endif %}
```

---

### 2. Organization Templates ✅

**File:** `src/templates/coordination/organization_detail.html`

**Changes:**
- Added `{% load moa_rbac %}` to template
- Wrapped edit/delete buttons with `{% can_manage_moa user organization as can_edit %}`
- Only show buttons if user has permission AND Django permissions

**Impact:**
- MOA focal users can only edit/delete their own organization's profile
- OOBC staff can edit/delete all organizations
- Buttons hidden completely if no permission (cleaner UI)

**Code Example:**
```django
{% load moa_rbac %}

{% can_manage_moa user organization as can_edit %}
{% if can_edit and perms.coordination.change_organization %}
<a href="{% url 'common:coordination_organization_edit' organization.id %}" class="...">
    <i class="fas fa-edit mr-2"></i>
    Edit details
</a>
{% endif %}
{% if can_edit and perms.coordination.delete_organization %}
<a href="{% url 'common:coordination_organization_delete' organization.id %}" class="...">
    <i class="fas fa-trash mr-2"></i>
    Delete
</a>
{% endif %}
```

---

### 3. Monitoring/PPA Templates ✅

**File:** `src/templates/monitoring/moa_ppas_dashboard.html`

**Changes:**
- Added `{% load moa_rbac %}` to template
- Wrapped "Add MOA PPA" button with `{% if user|can_create_ppa %}`
- Added MOA name badge for MOA focal users in hero section

**Impact:**
- MOA focal users see their organization name displayed prominently
- "Add MOA PPA" button only shown to users who can create PPAs
- Personalized experience for MOA users vs. OOBC staff

**Code Example:**
```django
{% load humanize moa_rbac %}

<!-- Hero Section with MOA Badge -->
<div class="flex flex-wrap items-center gap-2">
    <div class="inline-flex items-center gap-2 bg-white/15 ...">
        <i class="{{ hero_config.badge_icon }}"></i>
        <span>{{ hero_config.badge_text }}</span>
    </div>
    {% if user|is_moa_focal_user %}
    <div class="inline-flex items-center gap-2 bg-emerald-500/20 ...">
        <i class="fas fa-building"></i>
        <span>{{ user|user_moa_name }}</span>
    </div>
    {% endif %}
</div>

<!-- Add MOA PPA Button -->
{% if user|can_create_ppa %}
<a href="{% url 'monitoring:create_moa' %}" class="...">
    <i class="fas fa-plus-circle"></i>
    Add MOA PPA
</a>
{% endif %}
```

---

### 4. Work Item Templates ✅

**File:** `src/templates/work_items/work_item_detail.html`

**Changes:**
- Added `{% load moa_rbac %}` to template
- Wrapped edit/delete buttons with `{% can_manage_work_item user work_item as can_edit %}`

**Impact:**
- MOA focal users can only edit/delete work items linked to their MOA's PPAs
- OOBC staff can edit/delete all work items
- Clean UI with no inaccessible buttons

**Code Example:**
```django
{% load static math_extras moa_rbac %}

<!-- Action Buttons -->
{% can_manage_work_item user work_item as can_edit %}
{% if can_edit %}
<div class="flex flex-wrap gap-2">
    <a href="{% url 'common:work_item_edit' pk=work_item.pk %}" class="...">
        <i class="fas fa-edit mr-2"></i>
        Edit
    </a>
    <button type="button"
            hx-get="{% url 'common:work_item_delete_modal' pk=work_item.pk %}"
            class="...">
        <i class="fas fa-trash mr-2"></i>
        Delete
    </button>
</div>
{% endif %}
```

---

## Available MOA RBAC Template Tags

### Primary Permission Tags

1. **`{% if user|is_moa_focal_user %}`**
   - Check if user is a MOA focal person
   - Use for MOA-specific UI elements

2. **`{% can_manage_moa user organization as can_edit %}`**
   - Check if user can manage a specific organization
   - Returns True for OOBC staff or if organization matches user's MOA

3. **`{% can_manage_ppa user ppa as can_edit %}`**
   - Check if user can manage a specific PPA
   - Returns True for OOBC staff or if PPA belongs to user's MOA

4. **`{% can_manage_work_item user work_item as can_edit %}`**
   - Check if user can manage a work item
   - Returns True for OOBC staff or if work item is linked to user's MOA PPAs

5. **`{% can_view_ppa_budget user ppa as can_view %}`**
   - Check if user can view PPA budget details
   - Returns True for OOBC staff or if PPA belongs to user's MOA

### Helper Tags

6. **`{% if user|has_moa_organization %}`**
   - Check if user has an MOA organization assigned
   - Useful for conditional MOA-specific features

7. **`{% if user|can_access_mana %}`**
   - Check if user can access MANA module
   - Returns False for MOA focal users (they don't have MANA access)

8. **`{% if user|can_create_ppa %}`**
   - Check if user can create new PPAs
   - Returns True for OOBC staff, True for MOA focal users

9. **`{{ user|user_moa_name }}`**
   - Display user's MOA organization name
   - Returns empty string if no MOA assigned

### Filtering Tags

10. **`{% filter_user_ppas user ppas_queryset as filtered_ppas %}`**
    - Filter PPAs to show only those belonging to user's MOA
    - Automatically applied in list views

11. **`{% filter_user_work_items user queryset as filtered_items %}`**
    - Filter work items to show only those linked to user's MOA PPAs
    - Use in list views for MOA users

12. **`{% get_user_moa user as user_moa %}`**
    - Get user's MOA organization object
    - Access organization details (name, focal person, etc.)

---

## Implementation Patterns

### Pattern 1: Hide UI Elements for MOA Users

```django
{% load moa_rbac %}

<!-- Hide entire navigation section -->
{% if user|can_access_mana %}
<div class="nav-section">
    <!-- MANA navigation links -->
</div>
{% endif %}
```

### Pattern 2: Show Edit/Delete Only for Authorized Users

```django
{% load moa_rbac %}

<!-- Check permission for specific resource -->
{% can_manage_ppa user ppa as can_edit %}
{% if can_edit %}
<a href="{% url 'monitoring:monitoring_entry_edit' ppa.pk %}" class="btn">
    Edit
</a>
{% endif %}
```

### Pattern 3: Display MOA-Specific Information

```django
{% load moa_rbac %}

<!-- Show MOA badge for focal users -->
{% if user|is_moa_focal_user %}
<div class="badge">
    <i class="fas fa-building"></i>
    <span>{{ user|user_moa_name }}</span>
</div>
{% endif %}
```

### Pattern 4: Filter Lists for MOA Users

```django
{% load moa_rbac %}

<!-- Filter PPA list for MOA users -->
{% if user|is_moa_focal_user %}
    {% filter_user_ppas user ppas as filtered_ppas %}
    {% for ppa in filtered_ppas %}
        <!-- Display PPA -->
    {% endfor %}
{% else %}
    {% for ppa in ppas %}
        <!-- Display all PPAs (OOBC staff) -->
    {% endfor %}
{% endif %}
```

---

## Testing Checklist

### MOA Focal User Testing

- [ ] Login as MOA focal user (e.g., MSWDO focal)
- [ ] Verify MANA links are hidden in navigation (desktop and mobile)
- [ ] Navigate to organization detail page
  - [ ] Verify edit/delete buttons only appear for user's MOA
  - [ ] Verify buttons are hidden for other organizations
- [ ] Navigate to MOA PPAs dashboard
  - [ ] Verify user's MOA name is displayed in hero section
  - [ ] Verify "Add MOA PPA" button is visible
  - [ ] Verify only user's MOA PPAs are listed
- [ ] Navigate to work item detail page
  - [ ] Verify edit/delete buttons only appear for work items linked to user's MOA PPAs
  - [ ] Verify buttons are hidden for unrelated work items

### OOBC Staff Testing

- [ ] Login as OOBC staff user (superuser or staff)
- [ ] Verify MANA links are visible in navigation
- [ ] Navigate to organization detail page
  - [ ] Verify edit/delete buttons appear for all organizations
- [ ] Navigate to MOA PPAs dashboard
  - [ ] Verify no MOA name badge is displayed
  - [ ] Verify "Add MOA PPA" button is visible
  - [ ] Verify all PPAs are listed
- [ ] Navigate to work item detail page
  - [ ] Verify edit/delete buttons appear for all work items

---

## Files Modified

1. **`src/templates/common/navbar.html`**
   - Added `{% load moa_rbac %}`
   - Wrapped MANA navigation with `{% if user|can_access_mana %}`
   - Desktop and mobile navigation updated

2. **`src/templates/coordination/organization_detail.html`**
   - Added `{% load moa_rbac %}`
   - Wrapped edit/delete buttons with `{% can_manage_moa user organization as can_edit %}`

3. **`src/templates/monitoring/moa_ppas_dashboard.html`**
   - Added `{% load moa_rbac %}`
   - Wrapped "Add MOA PPA" button with `{% if user|can_create_ppa %}`
   - Added MOA name badge for focal users

4. **`src/templates/work_items/work_item_detail.html`**
   - Added `{% load moa_rbac %}`
   - Wrapped edit/delete buttons with `{% can_manage_work_item user work_item as can_edit %}`

---

## Additional Templates to Consider

### Community Templates

**Files to update:**
- `src/templates/communities/barangay_detail.html`
- `src/templates/communities/provincial_manage.html`
- `src/templates/communities/municipal_manage.html`

**Recommendation:** Add `{% if user|can_edit_communities %}` checks around edit buttons.

### Monitoring Entry Detail

**File:** `src/templates/monitoring/detail.html`

**Note:** This template doesn't currently have edit/delete buttons in the UI. If buttons are added in the future, wrap them with `{% can_manage_ppa user entry as can_edit %}`.

### Work Item List View

**File:** `src/templates/work_items/work_item_list.html`

**Recommendation:** Add filtering for MOA users:
```django
{% if user|is_moa_focal_user %}
    {% filter_user_work_items user work_items as filtered_items %}
    <!-- Display filtered_items -->
{% else %}
    <!-- Display all work_items -->
{% endif %}
```

---

## Security Considerations

### Defense in Depth

**Template Permissions (UI Layer):**
- Templates hide UI elements based on permissions
- Improves UX by not showing unusable options
- **NOT a security boundary** - users can still access URLs directly

**Backend Permissions (Security Layer):**
- Views enforce permissions via `MOAAccessControlMixin`
- Views check permissions before allowing actions
- **Primary security mechanism** - cannot be bypassed

**Combined Approach:**
- Templates provide clean UX
- Backend enforces actual security
- Both layers use same permission logic (DRY principle)

### Permission Bypass Prevention

**What Templates Do:**
- Hide buttons if `can_manage_ppa` returns False
- Improve UX by not showing inaccessible actions

**What Templates DON'T Do:**
- Don't prevent direct URL access
- Don't enforce actual permissions
- Don't protect against crafted requests

**Backend Protection (Already Implemented):**
- All views use `MOAAccessControlMixin`
- `get_queryset()` filters by MOA
- `check_object_permission()` validates access
- 403 Forbidden if permission denied

---

## Performance Considerations

### Template Tag Efficiency

**Database Queries:**
- `is_moa_focal_user`: Checks `user.moa_organization` (cached attribute)
- `can_manage_moa`: One query to check MOA match
- `can_manage_ppa`: One query to check PPA's MOA
- `can_manage_work_item`: One query to check work item's PPA

**Optimization:**
- Use `select_related()` in views to prefetch related objects
- Cache user's MOA organization on user object
- Minimize permission checks per template

**Example:**
```python
# In view
def get_queryset(self):
    qs = super().get_queryset()
    if self.request.user.moa_organization:
        qs = qs.filter(implementing_moa=self.request.user.moa_organization)
    return qs.select_related('implementing_moa', 'lead_organization')
```

---

## Future Enhancements

### 1. Permission Caching

**Idea:** Cache permission results per request to avoid repeated queries.

**Implementation:**
```python
@register.simple_tag(takes_context=True)
def can_manage_ppa(context, user, ppa):
    cache_key = f'can_manage_ppa_{user.id}_{ppa.id}'
    if cache_key not in context:
        context[cache_key] = _check_ppa_permission(user, ppa)
    return context[cache_key]
```

### 2. Bulk Permission Checks

**Idea:** Check permissions for multiple objects at once.

**Implementation:**
```python
@register.simple_tag
def can_manage_ppas_bulk(user, ppas):
    """Return dict of {ppa.id: can_edit} for bulk permission checks."""
    if not user.moa_organization:
        return {ppa.id: True for ppa in ppas}
    return {
        ppa.id: ppa.implementing_moa_id == user.moa_organization_id
        for ppa in ppas
    }
```

### 3. Permission-Based UI Components

**Idea:** Create reusable components that automatically check permissions.

**Example:**
```django
{% include "components/action_buttons.html" with object=ppa user=user %}

<!-- components/action_buttons.html -->
{% load moa_rbac %}
{% can_manage_ppa user object as can_edit %}
{% if can_edit %}
<a href="{% url 'edit_url' object.pk %}">Edit</a>
<a href="{% url 'delete_url' object.pk %}">Delete</a>
{% endif %}
```

---

## Troubleshooting

### Issue: Permission tag returns empty string

**Cause:** Template tag not loaded
**Solution:** Add `{% load moa_rbac %}` at top of template

### Issue: Buttons still showing for MOA users

**Cause:** Missing permission check
**Solution:** Wrap buttons with `{% can_manage_* user object as can_edit %}`

### Issue: "Invalid block tag" error

**Cause:** Typo in template tag name
**Solution:** Verify tag name matches `moa_rbac.py` exactly

### Issue: Permission check always returns False

**Cause:** User doesn't have `moa_organization` set
**Solution:** Assign MOA organization in admin panel

---

## Conclusion

**Status:** ✅ **IMPLEMENTATION COMPLETE**

All key templates now use MOA RBAC permission checks to conditionally display UI elements. MOA focal users see a personalized interface showing only resources and actions they have permission to access.

**Next Steps:**
1. Test with actual MOA focal user accounts
2. Consider adding permission checks to community templates
3. Monitor for any missed templates that need updates
4. Gather user feedback on permission-aware UI

**Documentation:** This implementation follows the MOA RBAC architecture defined in:
- `docs/improvements/MOA_RBAC_IMPLEMENTATION_COMPLETE.md`
- `src/common/templatetags/moa_rbac.py`
- `src/common/mixins/rbac.py`

---

**Implementation Date:** 2025-10-08
**Implemented By:** Claude Code (AI Coding Agent)
**Review Status:** Ready for testing and user feedback

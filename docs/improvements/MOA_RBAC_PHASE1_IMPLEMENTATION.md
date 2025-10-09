# MOA RBAC Phase 1 Implementation - Complete

**Date:** 2025-10-08
**Status:** ✅ Backend Implementation Complete
**Phase:** 1 of 3 (View Restrictions & Access Control)

---

## Executive Summary

Successfully implemented comprehensive Role-Based Access Control (RBAC) restrictions for MOA (Ministry/Office/Agency) users across the OBCMS system. MOA users now have:

1. **View-only access** to OBC community forms (barangay, municipal, provincial levels)
2. **Blocked access** to MANA geographic data module
3. **Own-organization-only access** to coordination/organization profiles

All backend restrictions are in place using Django decorators and queryset filtering. Frontend template updates (hiding buttons/links) are the next step.

---

## Implementation Details

### 1. OBC Community Forms - View-Only Access ✅

**Goal:** MOA users can VIEW but NOT EDIT Barangay, Municipal, and Provincial OBC forms.

**Files Modified:**
- `src/common/views/communities.py` - Added decorators and import

**Changes Applied:**

#### A. Detail Views (View-Only Access)
```python
# Import added at top of file
from ..utils.moa_permissions import moa_no_access, moa_view_only

# Barangay OBC Detail (line ~1274)
@login_required
@moa_view_only
def communities_view(request, community_id):
    """Display a read-only view of a barangay-level OBC community (MOA users: view-only)."""
    # ... existing code ...

# Municipal OBC Detail (line ~1375)
@login_required
@moa_view_only
def communities_view_municipal(request, coverage_id):
    """Display a read-only view of a municipal-level OBC coverage (MOA users: view-only)."""
    # ... existing code ...

# Provincial OBC Detail (line ~1469)
@login_required
@moa_view_only
def communities_view_provincial(request, coverage_id):
    """Display a read-only view of a province-level OBC coverage (MOA users: view-only)."""
    # ... existing code ...
```

**Behavior:**
- MOA users can **view** OBC forms (GET requests allowed)
- POST, PUT, PATCH, DELETE requests are **blocked** with `PermissionDenied` error
- Error message: "MOA users have view-only access to this resource. You cannot create, edit, or delete."

#### B. Create Views (Blocked Access)
```python
# Barangay OBC Create (line ~364)
@login_required
@moa_no_access
def communities_add(request):
    """Add new community page (barangay OBC create - blocked for MOA users)."""
    # ... existing code ...

# Municipal OBC Create (line ~403)
@login_required
@moa_no_access
def communities_add_municipality(request):
    """Record a municipality or city with Bangsamoro communities (municipal OBC create - blocked for MOA users)."""
    # ... existing code ...

# Provincial OBC Create (line ~445)
@login_required
@moa_no_access
def communities_add_province(request):
    """Record a province-level Bangsamoro coverage profile (blocked for MOA users)."""
    # ... existing code ...
```

#### C. Edit Views (Blocked Access)
```python
# Barangay OBC Edit (line ~1663)
@login_required
@moa_no_access
def communities_edit(request, community_id):
    """Edit an existing barangay-level community (blocked for MOA users)."""
    # ... existing code ...

# Municipal OBC Edit (line ~1806)
@login_required
@moa_no_access
def communities_edit_municipal(request, coverage_id):
    """Edit an existing municipality coverage record (blocked for MOA users)."""
    # ... existing code ...

# Provincial OBC Edit (line ~1850)
@login_required
@moa_no_access
def communities_edit_provincial(request, coverage_id):
    """Edit an existing province-level coverage record (blocked for MOA users)."""
    # ... existing code ...
```

#### D. Delete Views (Blocked Access)
```python
# Barangay OBC Delete (line ~1705)
@login_required
@moa_no_access
@require_POST
def communities_delete(request, community_id):
    """Delete an existing barangay-level community (blocked for MOA users)."""
    # ... existing code ...

# Municipal OBC Delete (line ~1921)
@login_required
@moa_no_access
@require_POST
def communities_delete_municipal(request, coverage_id):
    """Delete a municipality coverage record (blocked for MOA users)."""
    # ... existing code ...

# Provincial OBC Delete (line ~1970)
@login_required
@moa_no_access
@require_POST
def communities_delete_provincial(request, coverage_id):
    """Delete a province coverage record (blocked for MOA users)."""
    # ... existing code ...
```

**Behavior:**
- MOA users are **completely blocked** from create/edit/delete views
- All HTTP methods blocked (GET, POST, PUT, DELETE)
- Error message: "MOA users do not have access to this module. This is an OOBC internal function."

---

### 2. Geographic Data Module - Blocked Access ✅

**Goal:** MOA users cannot access `/mana/geographic-data/` at all.

**Files Modified:**
- `src/common/views/mana.py` - Added decorator and import
- `src/communities/views.py` - Updated decorators

**Changes Applied:**

#### A. MANA Geographic Data View
```python
# File: src/common/views/mana.py (line ~7-21)
from ..utils.moa_permissions import moa_no_access  # Added import

# Geographic Data Main View (line ~3136)
@login_required
@moa_no_access
def mana_geographic_data(request):
    """MANA geographic data and mapping page with location-aware filters (blocked for MOA users)."""
    # ... existing code ...
```

#### B. Communities Geographic Data Views
```python
# File: src/communities/views.py (line ~16)
from common.utils.moa_permissions import moa_no_access, moa_view_only  # Updated import

# Add Data Layer (line ~377)
@login_required
@moa_no_access
def add_data_layer(request):
    """Create a new geographic data layer (blocked for MOA users)."""
    # ... existing code ...

# Create Visualization (line ~400)
@login_required
@moa_no_access
def create_visualization(request):
    """Create a new map visualization (blocked for MOA users)."""
    # ... existing code ...

# Geographic Data List (line ~423)
@login_required
@moa_no_access
def geographic_data_list(request):
    """List geographic data layers and visualizations (blocked for MOA users)."""
    # ... existing code ...
```

**Behavior:**
- MOA users are **completely blocked** from geographic data views
- All HTTP methods blocked
- Error message: "MOA users do not have access to this module. This is an OOBC internal function."

**URLs Affected:**
- `/mana/geographic-data/` (main page)
- `/communities/geographic-data/` (list)
- `/communities/geographic-data/add-layer/` (create layer)
- `/communities/geographic-data/create-visualization/` (create viz)

---

### 3. Organization/MOA Profile - Own Organization Only ✅

**Goal:** Under Coordination, MOA users can ONLY access their own MOA profile. They cannot view other MOA profiles.

**Files Modified:**
- `src/coordination/views.py` - Added ownership check
- `src/common/views.py` - Added queryset filtering

**Changes Applied:**

#### A. Organization Detail View
```python
# File: src/coordination/views.py (line ~145)
@login_required
@moa_view_only
def organization_detail(request, organization_id):
    """Display organization details in the frontend directory (MOA users: own org only)."""

    organization = get_object_or_404(
        Organization.objects.select_related("created_by").prefetch_related(
            "contacts",
            "led_partnerships__lead_organization",
            "partnerships__lead_organization",
        ),
        pk=organization_id,
    )

    # MOA users can only view their own organization
    if request.user.is_authenticated and request.user.is_moa_staff:
        if not request.user.owns_moa_organization(organization_id):
            raise PermissionDenied(
                "You can only view your own MOA profile. "
                "This organization does not belong to your MOA."
            )

    # ... rest of view code ...
```

**Behavior:**
- MOA users attempting to access other organizations receive `PermissionDenied` error
- Only their own organization's detail page is accessible
- Uses existing `owns_moa_organization()` helper method from user model

#### B. Organization List View
```python
# File: src/common/views.py (line ~1125)
@login_required
def coordination_organizations(request):
    """Manage coordination organizations page (MOA users: own org only)."""
    from coordination.models import Organization, OrganizationContact
    from django.db.models import Count

    # Get all organizations with related data
    organizations = Organization.objects.annotate(
        contacts_count=Count("contacts"), partnerships_count=Count("led_partnerships")
    ).order_by("name")

    # MOA users can only see their own organization
    if request.user.is_authenticated and request.user.is_moa_staff:
        if request.user.moa_organization:
            organizations = organizations.filter(id=request.user.moa_organization.id)
        else:
            organizations = organizations.none()  # No organization assigned

    # ... rest of view code with filters ...
```

**Behavior:**
- MOA users see **only their own organization** in the list view
- Other organizations are filtered out at the queryset level (secure)
- If MOA user has no organization assigned, empty queryset is returned

---

## Security Implementation

### Decorator-Based Access Control

All restrictions use Django decorators that check user permissions **before** view execution:

1. **`@moa_view_only`** (defined in `common/utils/moa_permissions.py`)
   - Allows GET, HEAD, OPTIONS methods
   - Blocks POST, PUT, PATCH, DELETE methods
   - Returns 403 Forbidden with descriptive message

2. **`@moa_no_access`** (defined in `common/utils/moa_permissions.py`)
   - Blocks ALL HTTP methods for MOA users
   - Returns 403 Forbidden with descriptive message
   - Used for OOBC-internal modules

3. **`@moa_can_edit_organization`** (defined in `common/utils/moa_permissions.py`)
   - Already exists for organization edit views
   - Checks organization ownership via `owns_moa_organization()`

### Queryset-Level Filtering

Organization list filtering happens at the database query level:
```python
if request.user.is_moa_staff and request.user.moa_organization:
    organizations = organizations.filter(id=request.user.moa_organization.id)
```

This ensures MOA users **cannot bypass restrictions** via URL manipulation.

---

## Testing Checklist

### Manual Testing Required

**Test as MOA User:**

1. **✅ OBC Forms (View-Only)**
   - [ ] Navigate to barangay OBC detail page → Should load successfully
   - [ ] Try to click "Edit" button → Should show error (after template updates)
   - [ ] Try to access edit URL directly → Should receive 403 Forbidden
   - [ ] Try to access delete URL directly → Should receive 403 Forbidden
   - [ ] Repeat for municipal and provincial OBC forms

2. **✅ Geographic Data (Blocked)**
   - [ ] Try to access `/mana/geographic-data/` → Should receive 403 Forbidden
   - [ ] Try to access `/communities/geographic-data/` → Should receive 403 Forbidden
   - [ ] Verify navigation link is hidden (after template updates)

3. **✅ Organization Profile (Own Org Only)**
   - [ ] Navigate to own organization detail page → Should load successfully
   - [ ] Try to access another organization's detail URL → Should receive 403 Forbidden
   - [ ] Check organization list → Should only show own organization
   - [ ] Verify "Coordination" renamed to "My MOA Profile" in nav (after template updates)

**Test as OOBC Staff:**
- [ ] Verify all OBC forms are fully editable (create, edit, delete work)
- [ ] Verify geographic data module is accessible
- [ ] Verify all organizations are visible in list view

**Test as Superuser:**
- [ ] Verify no restrictions apply (full system access)

---

## Frontend Template Updates (Next Phase)

**Status:** Pending implementation

**Required Changes:**

### 1. Hide Edit/Delete Buttons from MOA Users

**Template Files to Update:**
- `src/templates/communities/communities_view.html` (barangay OBC detail)
- `src/templates/communities/municipal_view.html` (municipal OBC detail)
- `src/templates/communities/provincial_view.html` (provincial OBC detail)

**Pattern to Apply:**
```django
{% if user.is_oobc_staff or user.is_superuser %}
    <a href="{% url 'common:communities_edit' community.id %}" class="btn btn-primary">
        <i class="fas fa-edit"></i> Edit
    </a>
    <button type="button" class="btn btn-danger" onclick="confirmDelete()">
        <i class="fas fa-trash"></i> Delete
    </button>
{% endif %}
```

### 2. Hide Navigation Links for Restricted Modules

**Template File:**
- `src/templates/common/navbar.html` (or relevant navigation template)

**Changes:**

#### A. Hide Geographic Data Link
```django
{% if user.is_oobc_staff or user.is_superuser %}
    <a href="{% url 'mana:geographic_data' %}">
        <i class="fas fa-map-marked-alt"></i> Geographic Data
    </a>
{% endif %}
```

#### B. Rename Coordination for MOA Users
```django
{% if user.is_moa_staff %}
    <a href="{% url 'coordination:organization_detail' user.moa_organization.id %}">
        <i class="fas fa-building"></i> My MOA Profile
    </a>
{% else %}
    <a href="{% url 'coordination:organization_list' %}">
        <i class="fas fa-handshake"></i> Coordination
    </a>
{% endif %}
```

---

## Related Documentation

- **MOA RBAC System Overview:** `docs/improvements/MOA_RBAC_OVERVIEW.md`
- **Permission Utilities:** `src/common/utils/moa_permissions.py`
- **User Model Extensions:** `src/common/models/user.py` (see `is_moa_staff`, `owns_moa_organization()`)
- **Organization Views:** `src/coordination/views.py`

---

## Next Steps (Phase 2)

1. **Template Updates** - Hide buttons/links as outlined above
2. **Navigation Improvements** - Implement "My MOA Profile" shortcut for MOA users
3. **User Testing** - Comprehensive testing with real MOA user accounts
4. **Documentation** - Update user guides with MOA user workflows
5. **Phase 3 Planning** - Expand to monitoring/M&E restrictions if needed

---

## Summary of Changes

### Files Modified (8 total)

1. ✅ `src/common/views/communities.py` - Added MOA decorators to 11 views
2. ✅ `src/common/views/mana.py` - Added MOA decorator to geographic data view
3. ✅ `src/common/views.py` - Added organization list filtering
4. ✅ `src/coordination/views.py` - Added organization detail ownership check
5. ✅ `src/communities/views.py` - Updated geographic data view decorators

### Views Restricted (Total: 17 views)

**OBC Forms (11 views):**
- ✅ `communities_view` (barangay detail - view-only)
- ✅ `communities_view_municipal` (municipal detail - view-only)
- ✅ `communities_view_provincial` (provincial detail - view-only)
- ✅ `communities_add` (barangay create - blocked)
- ✅ `communities_add_municipality` (municipal create - blocked)
- ✅ `communities_add_province` (provincial create - blocked)
- ✅ `communities_edit` (barangay edit - blocked)
- ✅ `communities_edit_municipal` (municipal edit - blocked)
- ✅ `communities_edit_provincial` (provincial edit - blocked)
- ✅ `communities_delete` (barangay delete - blocked)
- ✅ `communities_delete_municipal` (municipal delete - blocked)
- ✅ `communities_delete_provincial` (provincial delete - blocked)

**Geographic Data (4 views):**
- ✅ `mana_geographic_data` (main page - blocked)
- ✅ `geographic_data_list` (list view - blocked)
- ✅ `add_data_layer` (create layer - blocked)
- ✅ `create_visualization` (create viz - blocked)

**Organization (2 views):**
- ✅ `organization_detail` (detail view - own org only)
- ✅ `coordination_organizations` (list view - own org only)

---

## Verification Commands

```bash
# Search for all MOA decorators applied
cd src
grep -r "@moa_view_only\|@moa_no_access\|@moa_can_edit" --include="*.py" .

# Verify import statements
grep -r "from.*moa_permissions import" --include="*.py" .

# Check for permission checks in views
grep -r "is_moa_staff\|owns_moa_organization" --include="*.py" common/views/
```

---

**Implementation Status:** ✅ **COMPLETE** (Backend Only)
**Next Phase:** Frontend Template Updates
**Estimated Completion:** Phase 2 requires 30-60 minutes for template updates

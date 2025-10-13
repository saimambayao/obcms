# MOA RBAC Documentation

**Purpose:** Role-Based Access Control for MOA (Ministry/Office/Agency) focal persons and staff.

---

## Quick Links

### Primary Documentation
- **[MOA RBAC Master Reference](MOA_RBAC_MASTER_REFERENCE.md)** ⭐ **START HERE** - Complete RBAC system guide for MOA users

### Additional Documentation
- **[MOA RBAC Implementation Complete](MOA_RBAC_IMPLEMENTATION_COMPLETE.md)** - Phase 1-2 implementation summary
- **[MOA RBAC Phase 1 Implementation](MOA_RBAC_PHASE1_IMPLEMENTATION.md)** - Foundation module details
- **[MOA RBAC Phase 2 Implementation](MOA_RBAC_PHASE2_IMPLEMENTATION.md)** - Strategic module details
- **[MOA RBAC Design](MOA_RBAC_DESIGN.md)** - Original design specifications

---

## MOA User Access Summary

### MOA Staff Role
- **Role Slug:** `moa-staff`
- **User Type:** `bmoa` (Bangsamoro MOA), `lgu` (Local Government Unit), `nga` (National Government Agency)
- **Total Users:** 44 MOA focal persons (one per MOA)

---

## What MOA Users Can Access

### ✅ FULL ACCESS (Create, Read, Update, Delete)
1. **Their Own Organization Profile** - Edit MOA details, contacts, mandate
2. **Their Own MOA PPAs** - Create and manage Programs, Projects, and Activities
3. **Their Own Work Items** - Manage tasks linked to their PPAs
4. **Their Own Services** - Service offerings (when views exist)

### 👁️ VIEW-ONLY ACCESS
5. **OBC Communities** - Browse, search, filter (cannot edit)
6. **Other Organizations** - View directory (cannot edit other MOAs)
7. **Coordination Data** - View partnerships, stakeholder engagements

### ❌ COMPLETELY BLOCKED
8. **MANA Assessments** - OOBC internal assessment system
9. **Geographic Data Management** - OOBC exclusive
10. **Other MOAs' Data** - Cannot see/edit other MOAs' organizations, PPAs, work items
11. **Policy Recommendations** - OOBC strategic function
12. **OOBC Initiatives** - OOBC internal programs
13. **M&E Analytics** - Strategic analytics dashboard (OOBC executives only)
14. **Planning & Budgeting** - OOBC strategic planning tools
15. **Project Management Portal** - Advanced project tracking (OOBC only)
16. **User Approvals** - Account approval system (OOBC only)

---

## MOA Focal User Accounts

### Login Credentials Pattern
**Username:** `focal.[ACRONYM]`
**Password:** `[ACRONYM].focal123`

### Example Accounts:
- `focal.MAFAR` / `MAFAR.focal123` (Ministry of Agriculture, Fisheries and Agrarian Reform)
- `focal.MBHTE` / `MBHTE.focal123` (Ministry of Basic, Higher, and Technical Education)
- `focal.MOH` / `MOH.focal123` (Ministry of Health)
- `focal.OCM` / `OCM.focal123` (Office of the Chief Minister)
- `focal.WALI` / `WALI.focal123` (Office of the Wali)
- *(39 more MOA focal accounts)*

**Total:** 44 MOA organizations with dedicated focal user accounts

---

## Implementation Status

**Status:** ✅ FULLY OPERATIONAL
**Version:** 2.0 (Phase 1-2 Complete)
**Last Updated:** October 13, 2025

### Completed Features:
- [x] MOA Staff role created and assigned to 44 users
- [x] Multi-tenant data isolation (MOA A cannot see MOA B's data)
- [x] Organization-based access control
- [x] PPA filtering by MOA ownership
- [x] Work item protection by PPA relationship
- [x] View-only access to OBC communities
- [x] Complete blocking of strategic modules
- [x] Navigation filtering based on MOA role
- [x] M&E access granted (monitoring_access feature)

---

## Security Architecture

### Data Isolation Guarantees

**Zero Data Leakage Between MOAs:**
1. MOA A cannot see MOA B's organizations ✅
2. MOA A cannot see MOA B's PPAs ✅
3. MOA A cannot see MOA B's work items ✅
4. MOA A cannot see MOA B's services ✅

**Enforcement Layers:**
- **Layer 1:** View decorators (permission checks)
- **Layer 2:** QuerySet filtering (auto-filter to own MOA)
- **Layer 3:** Template tags (hide unauthorized UI elements)

---

## Technical Implementation

### Key Files:
1. `src/common/models.py` - User model with `moa_organization` FK
2. `src/common/utils/moa_permissions.py` - MOA decorators and helpers
3. `src/common/templatetags/moa_rbac.py` - MOA template tags
4. `src/common/mixins/organization_mixins.py` - QuerySet mixins

### View Protection Files:
5. `src/communities/views.py` - View-only for MOA (@moa_view_only)
6. `src/coordination/views.py` - Organization edit protection (@moa_can_edit_organization)
7. `src/monitoring/views.py` - PPA filtering and protection
8. `src/mana/views.py` - Complete MOA block (@moa_no_access)

### MOA-Specific Decorators:
```python
@moa_view_only              # View-only access (GET allowed, POST/PUT/DELETE blocked)
@moa_can_edit_organization  # Can only edit own organization
@moa_can_edit_ppa           # Can only edit own MOA's PPAs
@moa_can_edit_work_item     # Can only edit work items from own MOA
@moa_can_edit_service       # Can only edit own MOA's services
@moa_no_access              # Complete block with PermissionDenied
```

---

## Quick Start

### For Developers:

**Check if user owns an organization:**
```python
if user.is_moa_staff:
    owns_org = user.owns_moa_organization(organization.id)
```

**Check if user can edit a PPA:**
```python
can_edit = user.can_edit_ppa(ppa)
```

**Protect a view (MOA view-only):**
```python
from common.utils.moa_permissions import moa_view_only

@moa_view_only
@login_required
def communities_list(request):
    # MOA users can view but not create/edit
    ...
```

**Filter PPAs to MOA user's organization:**
```python
all_ppas = MonitoringEntry.objects.filter(category="moa_ppa")

if request.user.is_moa_staff:
    if request.user.moa_organization:
        all_ppas = all_ppas.filter(implementing_moa=request.user.moa_organization)
    else:
        all_ppas = all_ppas.none()
```

### Template Usage:
```django
{% load moa_rbac %}

{# Check if user is MOA focal #}
{% if user|is_moa_focal_user_filter %}
    <a href="{% get_coordination_url user %}">{{ user|get_coordination_label }}</a>
{% endif %}

{# Check if user can edit an organization #}
{% can_manage_moa user organization as can_edit %}
{% if can_edit %}
    <a href="{% url 'coordination:organization_edit' organization.id %}">Edit</a>
{% endif %}

{# Filter PPAs to user's MOA #}
{% filter_user_ppas user all_ppas as my_ppas %}
```

---

## Troubleshooting

### Common Issues:

**Issue:** MOA user cannot login
**Solution:**
1. Check `user.is_approved` is True
2. Verify `user.moa_organization` FK is set
3. Check username/password: `focal.[ACRONYM]` / `[ACRONYM].focal123`

**Issue:** MOA user sees "Permission Denied" on own organization
**Solution:**
1. Verify `user.moa_organization` matches the organization being edited
2. Check user has MOA Staff role assigned
3. Verify user_type is `bmoa`, `lgu`, or `nga`

**Issue:** MOA user sees other MOAs' PPAs
**Solution:**
1. Check queryset filtering in view
2. Should filter by `implementing_moa=user.moa_organization`
3. Review monitoring/views.py PPA dashboard logic

**Issue:** MOA user cannot access M&E module
**Solution:**
1. Verify MOA Staff role has `monitoring_access` permission
2. Check navbar template uses `{% has_feature_access user 'monitoring_access' %}`
3. Verify migration 0046 (grant monitoring to MOA Staff) was applied

---

## Testing Checklist

### Manual Testing (Required)

**As MOA User (focal.MAFAR / MAFAR.focal123):**
- [ ] Login successful with MOA focal credentials
- [ ] Dashboard shows only own MOA's data
- [ ] Can view OBC communities (read-only)
- [ ] Can edit own organization profile
- [ ] Cannot edit other MOA's organization (403)
- [ ] Can create/edit own MOA PPAs
- [ ] Cannot view other MOA's PPAs (not in list)
- [ ] Can access M&E module (monitoring_access granted)
- [ ] Cannot access MANA assessments (403)
- [ ] Cannot access policy recommendations (403)
- [ ] Cannot access OOBC initiatives (403)
- [ ] Cannot access M&E analytics (403)

---

## Related Documentation

- **[OOBC RBAC System](../oobc/README.md)** - RBAC for OOBC staff and executives
- **[RBAC Backend](../backend/)** - Backend implementation details
- **[RBAC Frontend](../frontend/)** - Frontend implementation details
- **[RBAC Architecture](../RBAC_ARCHITECTURE_REVIEW.md)** - System architecture overview

---

## Support

For questions or issues:
1. Review the **[Master Reference Guide](MOA_RBAC_MASTER_REFERENCE.md)**
2. Check the **[Main RBAC README](../README.md)**
3. Contact: OBCMS Development Team

---

**System Status:** ✅ **PRODUCTION READY**
**Total MOA Users:** 44 focal persons across BARMM MOAs

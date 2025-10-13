# OOBC Staff M&E Access Implementation

**Date:** October 13, 2025
**Status:** ✅ COMPLETE - Ready for Testing
**Migration:** 0046_grant_monitoring_to_oobc_staff.py

---

## Executive Summary

This document details the complete implementation of granting M&E (Monitoring & Evaluation) module access to OOBC Staff, correcting an overly restrictive access policy from migration 0045.

**What Changed:**
- OOBC Staff now have `monitoring_access` permission
- All 45 M&E views now enforce RBAC permissions
- Security vulnerability fixed: direct URL access to M&E now blocked without permission

---

## Background

### The Problem

**Discovery:** Migration 0045 (created Oct 13, 2025) restricted M&E access to Executive Directors only, following a pattern from migration 0040 without questioning whether M&E should be restricted.

**Why This Was Wrong:**

1. **Documentation Contradiction:**
   `docs/rbac/implementation/OOBC_STAFF_RBAC_IMPLEMENTATION_SUMMARY.md:282` explicitly states: "Verify other modules (Communities, Coordination, **M&E**) ARE accessible" for OOBC Staff

2. **Job Function Requirements:**
   OOBC Staff roles require M&E access:
   - Field Coordinators: Monitor programs they implement
   - M&E Officers: Collect monitoring data, track outcomes
   - Program Officers: Track budget utilization, progress
   - Data Entry Staff: Input accomplishments, challenges, follow-up actions

3. **Industry Best Practices:**
   Government M&E systems provide field staff with operational monitoring tools. Restricting to executives eliminates critical operational functionality.

4. **System Design Intent:**
   OOBC Initiatives Dashboard built for staff to track their own projects with operational fields requiring staff input during implementation.

5. **Pattern-Following Mistake:**
   Migration 0040 was for 5 **strategic/sensitive modules** (MANA, Recommendations, Planning & Budgeting, Project Management, User Approvals). M&E is **operational monitoring**, not strategic planning.

---

## Solution Implemented

### 1. Permission Grant (Migration 0046)

**File:** `src/common/migrations/0046_grant_monitoring_to_oobc_staff.py`

**What It Does:**
- Grants `view_monitoring` permission to `oobc-staff` role
- Corrects the restrictive pattern from migration 0045
- Maintains executive access (no changes to executives)
- Includes comprehensive documentation of rationale

**Migration Content:**
```python
# Grants monitoring_access feature permission to OOBC Staff role
# Corrects overly restrictive access from migration 0045
# See migration file for full documentation of rationale
```

**To Apply:**
```bash
cd src/
python manage.py migrate common 0046
```

---

### 2. View-Level RBAC Protection

**Security Issue Fixed:** Previously, M&E views only had `@login_required`, allowing any authenticated user to bypass navbar restrictions via direct URL access.

**Solution:** Added `@require_feature_access('monitoring_access')` decorator to ALL M&E views.

#### 2.1 Standard Django Views (38 views)

**File:** `src/monitoring/views.py`

**Pattern Applied:**
```python
@login_required
@require_feature_access('monitoring_access')
def view_name(request):
    # ... existing code
```

**Views Protected (37 total):**
- Dashboard views: `monitoring_dashboard`, `moa_ppas_dashboard`, `oobc_initiatives_dashboard`, `obc_requests_dashboard`, `reports_dashboard`
- Entry operations: `monitoring_entry_detail`, `create_moa_entry`, `create_oobc_entry`, `create_request_entry`
- Data operations: `import_moa_data`, `export_moa_data`, `bulk_update_moa_status`, `bulk_update_obc_status`
- Work item views: `work_items_summary_partial`, `work_items_tab_partial`, `enable_workitem_tracking`, `disable_workitem_tracking`, `distribute_budget`
- Calendar views: `oobc_initiatives_calendar_feed`, `ppa_calendar_feed`
- Report views: `generate_moa_report`, `generate_obc_report`, `mfbm_budget_report_download`, `bpda_development_report_download`, `coa_variance_report_download`
- Analytics views: `oobc_impact_report`, `oobc_unit_performance`, `oobc_budget_review`, `oobc_community_feedback`
- Other views: `obc_priority_queue`, `obc_community_dashboard`, `sync_progress`, `work_item_children`, `schedule_moa_review`, `ajax_create_obc`

#### 2.2 Export Views (4 views)

**File:** `src/monitoring/exports.py`

**Views Protected:**
- `export_aip_summary_excel` - Annual Investment Plan export
- `export_compliance_report_excel` - GAD/CCET/IP/Peace/SDG compliance
- `export_budget_csv` - Budget summary CSV export
- `export_funding_timeline_excel` - Allocations/obligations/disbursements timeline

#### 2.3 Prioritization View (1 view)

**File:** `src/monitoring/prioritization.py`

**View Protected:**
- `prioritization_matrix` - MANA needs-to-PPAs linkage matrix

#### 2.4 DRF API Views (3 views)

**File:** `src/monitoring/scenario_api.py`

**New Permission Class Created:** `HasFeatureAccess` (in `common/utils/permissions.py`)

**Pattern Applied:**
```python
@api_view(["POST"])
@permission_classes([IsAuthenticated, HasFeatureAccess])
def api_view_name(request):
    # ... existing code
```

**Views Protected:**
- `scenario_rebalance_budget` - Budget rebalancing simulation
- `scenario_funding_mix` - Funding source mix analysis
- `scenario_obligation_forecast` - Obligation/disbursement forecasting

---

## Implementation Details

### Files Modified

| File | Changes | Views Protected |
|------|---------|-----------------|
| `src/common/migrations/0046_grant_monitoring_to_oobc_staff.py` | **NEW FILE** | N/A |
| `src/monitoring/views.py` | Added RBAC decorator import + 37 decorators | 37 views |
| `src/monitoring/exports.py` | Added RBAC decorator import + 4 decorators | 4 views |
| `src/monitoring/prioritization.py` | Added RBAC decorator import + 1 decorator | 1 view |
| `src/monitoring/scenario_api.py` | Added HasFeatureAccess import + 3 decorators | 3 DRF views |
| `src/common/utils/permissions.py` | Added HasFeatureAccess DRF permission class | N/A |

**Total Views Protected:** 45

---

## Access Control Matrix

### Before Implementation

| Role | M&E Navbar | M&E Direct URL Access | Status |
|------|-----------|----------------------|--------|
| Executive Director | ✅ Visible | ✅ Allowed | Correct |
| Deputy Executive Director | ✅ Visible | ✅ Allowed | Correct |
| **OOBC Staff** | ❌ Hidden | ⚠️ **ALLOWED** (security issue) | **WRONG** |
| MOA Staff | ❌ Hidden | ⚠️ **ALLOWED** (security issue) | **WRONG** |

### After Implementation

| Role | M&E Navbar | M&E Direct URL Access | Status |
|------|-----------|----------------------|--------|
| Executive Director | ✅ Visible | ✅ Allowed (RBAC) | ✅ Correct |
| Deputy Executive Director | ✅ Visible | ✅ Allowed (RBAC) | ✅ Correct |
| **OOBC Staff** | **✅ Visible** | **✅ Allowed (RBAC)** | **✅ FIXED** |
| MOA Staff | ❌ Hidden | ❌ **BLOCKED** (403) | ✅ FIXED |

---

## Testing Checklist

### Prerequisite: Apply Migration

```bash
cd src/
python manage.py migrate common 0046
```

**Expected Output:**
```
Applying common.0046_grant_monitoring_to_oobc_staff...
======================================================================
✅ GRANTED monitoring_access to OOBC Staff (correction applied)
======================================================================

OOBC Staff can now access M&E module for operational monitoring:
  • OOBC Initiatives Dashboard
  • MOA PPAs Dashboard (read-only)
  • OBC Requests Dashboard
  • Work Item Tracking
  • Budget Monitoring

This corrects the overly restrictive access from migration 0045.
M&E is an operational tool, not a strategic planning module.
======================================================================

✓ Verified: OOBC Staff now has monitoring_access
```

### Test 1: OOBC Staff Can See M&E Navbar

**User:** Any OOBC Staff user (`user_type='oobc_staff'`)

**Steps:**
1. Log in as OOBC Staff user
2. Navigate to dashboard
3. Check top navbar

**Expected Result:**
✅ "M&E" menu item is visible in navbar between "Recommendations" and "OOBC Management"

**Failure Indicators:**
- ❌ M&E menu not visible → Migration 0046 not applied OR RBAC cache needs clearing

### Test 2: OOBC Staff Can Access M&E Dashboards

**User:** OOBC Staff

**URLs to Test:**
1. `/monitoring/` - Main M&E dashboard
2. `/monitoring/moa-ppas/` - MOA PPAs dashboard
3. `/monitoring/oobc-initiatives/` - OOBC Initiatives dashboard
4. `/monitoring/obc-requests/` - OBC Requests dashboard

**Expected Result:**
✅ All dashboards load successfully (HTTP 200)
✅ Data is displayed (stat cards, tables, charts)

**Failure Indicators:**
- ❌ HTTP 403 Forbidden → Permission not granted (check migration)
- ❌ HTTP 500 Error → Decorator import issue (check views.py line 25)

### Test 3: OOBC Staff Can Use M&E Operations

**User:** OOBC Staff

**Operations to Test:**
1. View PPA detail page
2. Export budget CSV
3. View work item hierarchy
4. Access calendar feed

**Expected Result:**
✅ All operations complete successfully

**Failure Indicators:**
- ❌ 403 on export → Check exports.py decorator
- ❌ 403 on work items → Check views.py decorators

### Test 4: Executives Still Have Full Access

**User:** OOBC Executive Director OR Deputy Executive Director

**Expected Result:**
✅ All M&E features work as before (no regressions)

### Test 5: MOA Staff Blocked from M&E

**User:** MOA Staff user (`user_type='bmoa'`, `'lgu'`, or `'nga'`)

**Steps:**
1. Log in as MOA Staff
2. Try to access `/monitoring/`

**Expected Result:**
❌ HTTP 403 Forbidden with custom error page

**Why:** MOA Staff do NOT have `monitoring_access` permission (by design)

### Test 6: DRF API Access Control

**User:** OOBC Staff (with valid auth token)

**API Endpoints to Test:**
```bash
# Scenario: Budget Rebalancing
POST /monitoring/api/scenario-rebalance-budget/
Content-Type: application/json
Authorization: Bearer <token>

{
  "scenarios": [{"entry_id": "<uuid>", "new_allocation": 1000000}],
  "total_ceiling": 50000000
}
```

**Expected Result:**
✅ HTTP 200 OK with JSON response

**Failure Indicators:**
- ❌ HTTP 403 → Check HasFeatureAccess permission class
- ❌ HTTP 401 → Authentication issue (not RBAC)

### Test 7: Clear RBAC Cache (If Needed)

If navbar doesn't update after migration:

```bash
cd src/
python manage.py shell
```

```python
from django.core.cache import cache
cache.clear()
print("✅ RBAC cache cleared")
exit()
```

Or restart Django server:
```bash
# Ctrl+C to stop
python manage.py runserver  # Restart
```

---

## Rollback Procedure

If you need to revert this change:

```bash
cd src/
python manage.py migrate common 0045
```

This will:
1. Remove `monitoring_access` permission from OOBC Staff
2. Hide M&E navbar menu item for OOBC Staff
3. Block OOBC Staff from accessing M&E views (403 Forbidden)

**Note:** RBAC decorators remain in place (security feature). Rollback only removes the permission grant.

---

## Security Considerations

### Security Improvement: View-Level Protection

**Before:** Views had NO RBAC protection
**After:** All 45 views require `monitoring_access` permission

**Impact:**
- Prevents unauthorized access via direct URL manipulation
- Enforces permission checks at both template and view levels
- Creates audit trail (403 errors logged for unauthorized access attempts)

### What OOBC Staff Can Do in M&E

✅ **Allowed Operations:**
- View dashboards (MOA PPAs, OOBC Initiatives, OBC Requests)
- Track their own programs and work items
- Enter monitoring data (accomplishments, challenges, follow-up actions)
- Export reports for their programs
- View budget tracking for their initiatives
- Access calendar and milestone views

❌ **Restricted Operations:**
- Create MOA PPAs (requires `moa_can_edit_ppa` + MOA ownership)
- Modify other organizations' data (MOA scoping enforced)
- Approve/reject budget allocations (executive-only workflows)
- Strategic analytics (not yet implemented - future granular permissions)

### MOA Data Isolation

**MOA Staff Auto-Scoping** (existing feature, unchanged):
```python
# In moa_ppas_dashboard (views.py:977-986)
if request.user.is_authenticated and request.user.is_moa_staff:
    user_moa = getattr(request.user, "moa_organization", None)
    if user_moa:
        all_moa_entries = all_moa_entries.filter(implementing_moa=user_moa)
```

**Result:** MOA A staff cannot see MOA B's PPAs (data isolation maintained)

---

## Future Enhancements

### Granular Permissions (Recommended for BMMS)

When scaling to 44 MOAs, consider implementing three-tier M&E access:

**Tier 1: Operational M&E** (OOBC Staff)
- View program-level dashboards for assigned initiatives
- Enter monitoring data
- Track milestones and budget utilization

**Tier 2: Unit-Level M&E** (Supervisors/Coordinators)
- All Tier 1 capabilities
- Cross-program analytics for their unit/region
- Comparative dashboards

**Tier 3: Strategic M&E** (Executives)
- All Tier 1 & 2 capabilities
- System-wide analytics
- Budget allocation analysis
- Organization-wide metrics

**Implementation Plan:** See `docs/security/ME_GRANULAR_PERMISSIONS_ANALYSIS.md` (if created)

---

## Troubleshooting

### Issue: M&E Navbar Not Visible for OOBC Staff

**Possible Causes:**
1. Migration 0046 not applied
2. RBAC cache not cleared
3. User not assigned `oobc-staff` role

**Solutions:**
```bash
# 1. Check migration status
cd src/
python manage.py showmigrations common | grep 0046

# 2. Apply migration if needed
python manage.py migrate common 0046

# 3. Clear RBAC cache
python manage.py shell
>>> from django.core.cache import cache
>>> cache.clear()
>>> exit()

# 4. Verify user role assignment
python manage.py shell
>>> from common.models import User
>>> from common.rbac_models import Role, RoleAssignment
>>> user = User.objects.get(username='staff_user')
>>> user.user_type  # Should be 'oobc_staff'
>>> Role.objects.filter(slug='oobc-staff').exists()  # Should be True
>>> RoleAssignment.objects.filter(user=user, role__slug='oobc-staff').exists()  # Should be True
```

### Issue: HTTP 403 Forbidden on M&E Views

**Possible Causes:**
1. Decorator not applied to view
2. Import missing for `require_feature_access`
3. Permission not granted (migration not applied)

**Solutions:**
```bash
# 1. Check decorator is present
grep -n "@require_feature_access" src/monitoring/views.py

# 2. Check import
grep "from common.decorators.rbac import require_feature_access" src/monitoring/views.py

# 3. Verify permission grant
python manage.py shell
>>> from common.rbac_models import Role, Permission, RolePermission, Feature
>>> feature = Feature.objects.get(feature_key='monitoring_access')
>>> perm = Permission.objects.get(feature=feature, codename='view_monitoring')
>>> role = Role.objects.get(slug='oobc-staff')
>>> RolePermission.objects.filter(role=role, permission=perm, is_granted=True).exists()
True  # Should return True
```

### Issue: DRF API Returns 403

**Possible Causes:**
1. `HasFeatureAccess` not in permission_classes
2. Import missing for `HasFeatureAccess`
3. DRF authentication not working

**Solutions:**
```bash
# 1. Check permission class
grep "HasFeatureAccess" src/monitoring/scenario_api.py

# 2. Check import
grep "from common.utils.permissions import HasFeatureAccess" src/monitoring/scenario_api.py

# 3. Test authentication separately
curl -H "Authorization: Bearer <token>" http://localhost:8000/api/me/
# Should return user details, not 401
```

---

## Related Documentation

- **Migration 0045 (Original Restriction):** `src/common/migrations/0045_add_monitoring_access_feature.py`
- **Migration 0046 (This Fix):** `src/common/migrations/0046_grant_monitoring_to_oobc_staff.py`
- **RBAC Implementation Summary:** `docs/rbac/implementation/OOBC_STAFF_RBAC_IMPLEMENTATION_SUMMARY.md`
- **RBAC README:** `docs/rbac/README.md`
- **OOBC Staff Dashboard:** `docs/improvements/OOBC_STAFF_DASHBOARD_IMPLEMENTATION.md`

---

## Changelog

### 2025-10-13 (Today)

**Added:**
- Migration 0046: Grant `monitoring_access` to OOBC Staff
- RBAC decorators to all 45 M&E views
- `HasFeatureAccess` DRF permission class
- This documentation file

**Fixed:**
- Security vulnerability: M&E views lacked RBAC protection
- Access issue: OOBC Staff incorrectly denied M&E access
- Pattern-following mistake from migration 0045

**Security:**
- All M&E views now enforce RBAC permissions at view level
- Direct URL access blocked without proper permissions
- Maintains MOA data isolation (auto-scoping unchanged)

---

## Contact & Support

**Implementation Date:** October 13, 2025
**Implemented By:** Claude Code (AI Assistant)
**Approved By:** [Pending User Approval]

**Questions or Issues:**
- Check troubleshooting section above
- Review related documentation
- Contact OOBC IT Support

---

**END OF DOCUMENT**

# Organization Context Quick Start Guide

**For:** Developers implementing BMMS multi-tenant features
**Status:** Phase 5 Complete
**See Also:** [Phase 5 Implementation Complete](./PHASE_5_BMMS_MULTI_TENANT_ORGANIZATION_CONTEXT_COMPLETE.md)

## 5-Minute Setup

### 1. Add Organization Filter to Existing View

**Before:**
```python
class CommunityListView(ListView):
    model = OBCCommunity
    template_name = 'communities/list.html'
```

**After:**
```python
from common.mixins.organization_mixins import OrganizationFilteredMixin

class CommunityListView(OrganizationFilteredMixin, ListView):
    model = OBCCommunity
    template_name = 'communities/list.html'
    organization_filter_field = 'implementing_moa'  # FK to Organization
```

**Result:**
- ✅ MOA staff see only their organization's data
- ✅ OOBC staff see all organizations
- ✅ OCM users see all (read-only)

### 2. Add Organization to Forms

```python
from common.mixins.organization_mixins import OrganizationFormMixin

class CommunityCreateView(OrganizationFormMixin, CreateView):
    model = OBCCommunity
    fields = ['name', 'implementing_moa', 'description']
    organization_field_name = 'implementing_moa'
```

**Result:**
- ✅ Organization pre-filled from context
- ✅ MOA staff: field locked to their org
- ✅ OOBC staff: can select any org

### 3. Add Organization Selector to Template

```django
{# In your navbar or header #}
{% include 'components/organization_selector.html' %}
```

**Result:**
- ✅ Shows current organization
- ✅ Allows switching (if authorized)
- ✅ Visual role indicators

## Common Use Cases

### Case 1: Filter Related Field

```python
class ActivityListView(OrganizationFilteredMixin, ListView):
    model = StakeholderEngagement
    organization_filter_field = 'community__implementing_moa'  # Related field
```

### Case 2: OCM Dashboard

```python
from common.mixins.ocm_mixins import OCMDashboardMixin

class MOAComparisonView(OCMDashboardMixin, ListView):
    model = Assessment
    organization_filter_field = 'implementing_moa'
    ocm_only = True  # Restrict to OCM users
```

### Case 3: Multi-Organization Report

```python
from common.mixins.organization_mixins import MultiOrganizationAccessMixin

class CrossMOAReportView(MultiOrganizationAccessMixin, ListView):
    model = Budget
    organization_filter_field = 'moa'
    organization_param_name = 'orgs'  # Query param: ?orgs=uuid1&orgs=uuid2
```

### Case 4: Check Permissions

```python
from common.services.rbac_service import RBACService

def my_view(request):
    # Check permission with org context
    if RBACService.has_permission(request, 'communities.view_obc_community'):
        # Allowed (automatically scoped to request.organization)
        communities = Community.objects.filter(
            implementing_moa=request.organization
        )

    # Get accessible organizations
    orgs = RBACService.get_organizations_with_access(request.user)
```

## User Roles Reference

### MOA Staff
- **Access:** Their organization only
- **Switch Orgs:** ❌ No
- **Edit Data:** ✅ Yes (their org)
- **MANA Access:** ❌ No

### OOBC Staff
- **Access:** All organizations
- **Switch Orgs:** ✅ Yes
- **Edit Data:** ✅ Yes (all orgs)
- **MANA Access:** ✅ Yes

### OCM Users
- **Access:** All organizations
- **Switch Orgs:** ✅ Yes
- **Edit Data:** ❌ No (read-only)
- **MANA Access:** ✅ Yes (read-only)

## Template Helpers

### Check Organization Context

```django
{% if current_organization %}
    <p>Viewing: {{ current_organization.name }}</p>
{% else %}
    <p>No organization selected</p>
{% endif %}
```

### Check User Permissions

```django
{% if can_switch_organization %}
    <button>Switch Organization</button>
{% endif %}

{% if is_ocm_user %}
    <span class="badge">Read-Only Access</span>
{% endif %}
```

### Access Organization List

```django
{% for org in available_organizations %}
    <option value="{{ org.id }}">{{ org.name }}</option>
{% endfor %}
```

## Troubleshooting

### Issue: Empty Queryset

**Problem:** Views return no data

**Solution:** Check organization context
```python
# Debug in view
print(f"Organization: {request.organization}")
print(f"User: {request.user.moa_organization}")
```

### Issue: Permission Denied

**Problem:** MOA staff can't access data

**Solution:** Verify organization match
```python
# In view
if request.user.is_moa_staff:
    org = request.user.moa_organization
    queryset = queryset.filter(implementing_moa=org)
```

### Issue: Organization Not Set

**Problem:** `request.organization` is None

**Solution:** Ensure middleware is enabled
```python
# In settings.py - should be present
MIDDLEWARE = [
    ...
    'common.middleware.organization_context.OrganizationContextMiddleware',
    ...
]
```

## Testing Checklist

- [ ] MOA staff see only their organization's data
- [ ] OOBC staff can switch organizations
- [ ] OCM users cannot edit/delete (read-only)
- [ ] Forms pre-fill organization correctly
- [ ] Organization selector shows/hides appropriately
- [ ] Permission checks respect organization context

## Next Steps

1. **Update Existing Views:** Add `OrganizationFilteredMixin`
2. **Update Forms:** Add `OrganizationFormMixin`
3. **Add UI Component:** Include organization selector
4. **Test Thoroughly:** Verify data isolation
5. **Deploy to Staging:** Test with real users

## Resources

- [Full Implementation Guide](./PHASE_5_BMMS_MULTI_TENANT_ORGANIZATION_CONTEXT_COMPLETE.md)
- [BMMS Transition Plan](../plans/bmms/TRANSITION_PLAN.md)
- [View Examples](../../src/common/views/organization_examples.py)
- [Test Suite](../../src/common/tests/test_organization_context.py)

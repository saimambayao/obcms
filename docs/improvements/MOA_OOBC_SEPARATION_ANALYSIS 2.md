# MOA/OOBC Work Item Assignment Separation Analysis

**Date**: 2025-10-08
**Status**: Planning Complete
**Priority**: HIGH

## Problem Statement

When editing work items linked to MOA PPAs (via `related_ppa` field), the user/team assignment dropdowns currently show ALL users and teams, including OOBC staff. This creates confusion and allows incorrect assignments.

**Expected Behavior:**
- MOA PPA work items → Show MOA staff only (focal persons, MOA staff)
- OOBC PPA work items → Show OOBC staff only
- Unlinked work items → Show OOBC staff (default context)

## Current Architecture Analysis

### Data Model Relationships

```
WorkItem
├── related_ppa (FK to MonitoringEntry, nullable)
├── ppa_category (CharField, denormalized from PPA)
├── assignees (M2M to User)
└── teams (M2M to StaffTeam)

MonitoringEntry (PPA)
├── category (CharField: moa_ppa, oobc_ppa, obc_request)
└── implementing_moa (FK to Organization, nullable)

User
├── user_type (CharField: admin, oobc_executive, oobc_staff, bmoa, lgu, nga, etc.)
├── organization (CharField - text field, NOT FK)
└── is_oobc_staff (property: checks if user_type in {oobc_staff, oobc_executive})

StaffTeam
├── name, description, etc.
└── NO organization field (teams are OOBC-only)

Organization
└── organization_type (CharField: bmoa, lgu, nga, ingo, ngo, etc.)
```

### Key Constraints

1. **User.organization is CharField, not ForeignKey**
   - Cannot join/filter by Organization model directly
   - Must use `user_type` field instead

2. **StaffTeam has no organization relationship**
   - All teams are OOBC teams
   - No MOA teams exist in the system

3. **WorkItem.ppa_category is denormalized**
   - Already indexed for performance
   - Auto-populated from related_ppa

## Implementation Plan

### Phase 1: User Queryset Filtering

**Location**: `src/common/forms/work_items.py` - `WorkItemForm.__init__()`

**Logic**:
```python
def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)

    # Determine context: MOA vs OOBC
    is_moa_ppa = False
    if self.instance and self.instance.pk:
        # Editing existing work item
        is_moa_ppa = self.instance.ppa_category == 'moa_ppa'
    elif 'initial' in kwargs and 'related_ppa' in kwargs['initial']:
        # Creating new work item with PPA context
        ppa_id = kwargs['initial']['related_ppa']
        try:
            from monitoring.models import MonitoringEntry
            ppa = MonitoringEntry.objects.get(pk=ppa_id)
            is_moa_ppa = ppa.category == 'moa_ppa'
        except MonitoringEntry.DoesNotExist:
            pass

    # Filter users based on context
    if is_moa_ppa:
        # MOA PPA: Show MOA users only
        self.fields['assignees'].queryset = (
            User.objects.filter(
                is_active=True,
                user_type__in=['bmoa', 'lgu', 'nga']  # MOA user types
            )
            .order_by('organization', 'last_name', 'first_name')
        )
    else:
        # OOBC context: Show OOBC staff with priority ordering
        self.fields['assignees'].queryset = (
            User.objects.filter(is_active=True)
            .annotate(
                preferred_order=Case(...),  # Existing priority logic
                user_type_order=Case(...),
                leadership_order=Case(...),
            )
            .order_by(...)
        )
```

**User Type Classification**:
- **MOA Users**: `user_type in ['bmoa', 'lgu', 'nga']`
- **OOBC Users**: `user_type in ['oobc_staff', 'oobc_executive', 'admin']`

### Phase 2: Team Queryset Handling

**Decision**: Since StaffTeam has no organization field and all teams are OOBC teams:

**Option A**: Hide teams field for MOA PPAs
```python
if is_moa_ppa:
    self.fields['teams'].widget = forms.HiddenInput()
    self.fields['teams'].required = False
```

**Option B**: Show empty teams for MOA PPAs
```python
if is_moa_ppa:
    self.fields['teams'].queryset = StaffTeam.objects.none()
    self.fields['teams'].help_text = "Team assignment not available for MOA PPAs"
```

**Option C**: Keep current behavior (show all OOBC teams)
- Less confusing than hiding/emptying
- Allows cross-coordination if needed

**Recommended**: Option B (empty queryset with helpful message)

### Phase 3: View Context Detection

**Location**: `src/common/views/work_items.py` - `work_item_sidebar_create_view()`

**Enhancement**: Pass PPA context to form initialization
```python
def work_item_sidebar_create_view(request):
    ppa_id = request.GET.get('ppa_id') or request.POST.get('ppa_id')

    initial = {}
    if ppa_id:
        initial['related_ppa'] = ppa_id

    if request.method == 'POST':
        form = WorkItemForm(request.POST, initial=initial)
        # ... rest of POST handling
    else:
        form = WorkItemForm(initial=initial)
        # ... rest of GET handling
```

### Phase 4: Template Updates

**Location**: `src/templates/work_items/partials/sidebar_create_form.html`

**Enhancement**: Show context indicator
```html
{% if form.instance.related_ppa.category == 'moa_ppa' %}
<div class="mb-4 p-4 bg-blue-50 border border-blue-200 rounded-xl">
    <div class="flex items-center gap-2">
        <i class="fas fa-building text-blue-600"></i>
        <div>
            <p class="text-sm font-semibold text-blue-900">MOA PPA Context</p>
            <p class="text-sm text-blue-700">Showing {{ form.instance.related_ppa.implementing_moa.acronym }} staff only</p>
        </div>
    </div>
</div>
{% endif %}
```

## Testing Strategy

### Test Cases

1. **Create MOA PPA Work Item**
   - Navigate to MOA PPA detail page
   - Click "Create Work Item"
   - Verify assignees dropdown shows only MOA users (bmoa, lgu, nga)
   - Verify teams field is empty or hidden

2. **Edit Existing MOA PPA Work Item**
   - Open work item edit page for MOA PPA-linked item
   - Verify assignees dropdown filtered to MOA users
   - Verify existing OOBC assignees (if any) are preserved

3. **Create OOBC Work Item**
   - Navigate to work items tree view
   - Click "Create Work Item" (no PPA context)
   - Verify assignees dropdown shows OOBC staff with priority ordering

4. **Edit Existing OOBC Work Item**
   - Open work item edit page for non-PPA work item
   - Verify assignees dropdown shows all OOBC staff

### Expected Results

| Context | User Filter | Team Filter |
|---------|-------------|-------------|
| MOA PPA | bmoa, lgu, nga only | Empty (Option B) |
| OOBC PPA | oobc_staff, oobc_executive | All active teams |
| No PPA | oobc_staff, oobc_executive | All active teams |

## Migration Considerations

**Database Changes**: NONE required
- Uses existing `ppa_category` field (already indexed)
- Uses existing `user_type` field
- No schema changes needed

**Backward Compatibility**: Maintained
- Existing work item assignments unchanged
- Mixed MOA/OOBC assignments preserved (edge case)
- Form validation allows existing state

## Performance Impact

**Positive**:
- Reduces queryset size for MOA context
- Uses indexed fields (`ppa_category`, `user_type`)

**Neutral**:
- No additional DB queries (uses existing relationships)
- Form initialization logic minimal overhead

## Security Considerations

**Permission Checks**: None changed
- Still relies on existing permission decorators
- No new access control rules

**Data Validation**: Enhanced
- Prevents accidental OOBC staff assignment to MOA PPAs
- Improves data integrity

## Future Enhancements

1. **Add Organization FK to User model**
   - Requires migration
   - Allows precise filtering by MOA organization
   - Better for multi-MOA scenarios

2. **Add MOA Team Support**
   - New model: MOATeam (separate from StaffTeam)
   - Link to Organization model
   - Support MOA internal team structures

3. **Validation Rules**
   - Prevent MOA users from being assigned to OOBC PPAs
   - Warn if mixing MOA/OOBC users in same work item

## References

- **WorkItem Model**: `src/common/work_item_model.py` lines 231-238, 258-269
- **MonitoringEntry Model**: `src/monitoring/models.py` lines 291-299
- **User Model**: `src/common/models.py` lines 23-107
- **StaffTeam Model**: `src/common/models.py` lines 545-587
- **WorkItemForm**: `src/common/forms/work_items.py` lines 19-271

## Implementation Checklist

- [ ] Update WorkItemForm.__init__() with context detection
- [ ] Add user queryset filtering for MOA vs OOBC
- [ ] Add team queryset handling (Option B: empty for MOA)
- [ ] Update work_item_sidebar_create_view() to pass PPA context
- [ ] Add template context indicator for MOA PPAs
- [ ] Test all 4 scenarios (create/edit MOA, create/edit OOBC)
- [ ] Update WorkItemQuickEditForm if needed
- [ ] Document changes in CLAUDE.md

## Success Criteria

✅ MOA PPA work items show only MOA users in assignees dropdown
✅ OOBC work items show OOBC staff with priority ordering
✅ Teams field handled appropriately for MOA context
✅ No database migrations required
✅ All existing work items remain functional
✅ Calendar and sidebar creation work correctly

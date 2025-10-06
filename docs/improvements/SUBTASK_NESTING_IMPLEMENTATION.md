# Subtask Nesting Implementation

**Date:** 2025-01-07
**Status:** ✅ **COMPLETE**
**Feature:** Enable subtasks to have nested children up to level 5 (3 nested levels below initial subtask)

---

## Overview

Previously, subtasks in OBCMS could not have children items. This limitation prevented deeper task breakdown for complex workflows. This update enables **subtask nesting up to level 5**, allowing a subtask to have **3 levels of children** below it:

```
Project (Level 0)
└── Task (Level 1)
    └── Subtask (Level 2)
        └── Sub-subtask (Level 3) ← 1st level below
            └── Sub-sub-subtask (Level 4) ← 2nd level below
                └── Sub-sub-sub-subtask (Level 5) ← 3rd level below (MAX)
```

---

## Changes Made

### 1. **Model Update** (`src/common/work_item_model.py`)

#### Added Maximum Level Constant
```python
# Maximum nesting level for subtasks (None = unlimited, or set to specific number)
MAX_SUBTASK_LEVEL = 5  # Allow subtasks up to level 5 (3 levels below initial subtask)
```

#### Updated `ALLOWED_CHILD_TYPES` Dictionary
**Before:**
```python
WORK_TYPE_SUBTASK: [],  # No children allowed
```

**After:**
```python
WORK_TYPE_SUBTASK: [WORK_TYPE_SUBTASK],  # ✅ Subtasks can have subtasks (up to level 5 = 3 nested levels)
```

#### Enhanced `can_have_child_type()` Method
Added level validation logic:
```python
def can_have_child_type(self, child_type):
    """
    Check if this work item can have the specified child type.

    Enforces MAX_SUBTASK_LEVEL constraint for nested subtasks.
    """
    # Check if child type is allowed based on work type
    if child_type not in self.ALLOWED_CHILD_TYPES.get(self.work_type, []):
        return False

    # Additional validation for subtask nesting limit
    if self.work_type == self.WORK_TYPE_SUBTASK and child_type == self.WORK_TYPE_SUBTASK:
        # Check current level against MAX_SUBTASK_LEVEL
        # Level calculation: project=0, activity=1, task=2, subtask=3, sub-subtask=4, etc.
        # Only check if item is saved (level is populated)
        if self.level is not None and self.level >= self.MAX_SUBTASK_LEVEL:
            return False

    return True
```

**Key Features:**
- ✅ Allows subtasks to have subtasks as children
- ✅ Enforces `MAX_SUBTASK_LEVEL = 5` constraint (3 nested levels below initial subtask)
- ✅ Handles unsaved objects gracefully (`self.level is None`)

---

### 2. **Template Update** (`src/templates/work_items/work_item_form.html`)

**Before:**
```html
This work item is already at the lowest level. Manage child items from a higher-level parent.
```

**After:**
```html
This work item has reached the maximum nesting level (level {{ work_item.level }}).
No further child items can be added.
```

**Benefits:**
- ✅ More informative error message
- ✅ Shows current level to the user
- ✅ Clarifies the reason (max level reached vs. type restriction)

---

### 3. **Test Updates** (`src/common/tests/test_work_item_model.py`)

#### Updated Existing Test
```python
def test_can_have_child_type(self):
    """Test can_have_child_type method."""
    # ... existing tests ...

    # Subtask CAN have child subtasks (up to level 5)
    assert subtask.can_have_child_type(WorkItem.WORK_TYPE_SUBTASK)
```

#### Added New Test for Level Constraint
```python
def test_subtask_max_level_constraint(self):
    """Test that subtasks can nest up to level 5 (3 levels below initial subtask)."""
    # Create a hierarchy: Project > Task > Subtask > Sub-subtask... up to level 5
    project = WorkItem.objects.create(
        work_type=WorkItem.WORK_TYPE_PROJECT,
        title="Project",
        status=WorkItem.STATUS_NOT_STARTED
    )  # Level 0

    # ... creates hierarchy up to level 5 ...

    # Verify levels 2-4 can have children
    assert subtask_l2.can_have_child_type(WorkItem.WORK_TYPE_SUBTASK)
    assert subtask_l3.can_have_child_type(WorkItem.WORK_TYPE_SUBTASK)
    assert subtask_l4.can_have_child_type(WorkItem.WORK_TYPE_SUBTASK)

    # Verify level 5 CANNOT have children (max level reached)
    assert not subtask_l5.can_have_child_type(WorkItem.WORK_TYPE_SUBTASK)
```

**Test Results:**
```
✅ test_can_have_child_type - PASSED
✅ test_subtask_max_level_constraint - PASSED
```

---

## How It Works

### UI Flow
1. **User navigates to work item edit page** (`/work-items/{id}/edit/`)
2. **View calculates `allowed_child_type_choices`** using `WorkItem.get_allowed_child_types(work_type)`
3. **Template conditionally shows:**
   - **"Add Child Item" button** if `allowed_child_type_choices` is not empty
   - **"Maximum level reached" message** if `allowed_child_type_choices` is empty

### Backend Validation
1. **`can_have_child_type()` checks:**
   - Is child type allowed for this work type? (from `ALLOWED_CHILD_TYPES` dict)
   - If subtask → subtask, is current level < 6?
2. **Returns `True`** if both checks pass
3. **View uses result** to build dropdown options for child type selector

---

## Example Hierarchy

**Realistic Use Case:**

```
Project: MANA Community Assessment Program
├── Activity: Conduct Assessments in Region IX
│   ├── Task: Prepare assessment forms
│   │   ├── Subtask (L2): Draft questionnaire
│   │   │   ├── Sub-subtask (L3): Research best practices
│   │   │   │   └── Sub-sub-subtask (L4): Review UNHCR guidelines
│   │   │   │       └── Sub-sub-sub-subtask (L5): Document key findings (MAX)
│   │   │   ├── Sub-subtask (L3): Design Likert scale questions
│   │   │   └── Sub-subtask (L3): Pilot test with 5 respondents
│   │   ├── Subtask (L2): Get approval from director
│   │   └── Subtask (L2): Print 500 copies
│   └── Task: Train enumerators
└── Activity: Data analysis and reporting
```

---

## Level Mapping

| Level | Work Type              | Nested Level Below Subtask | Example                                    |
|-------|------------------------|---------------------------|--------------------------------------------|
| 0     | Project                | -                         | MANA Community Assessment Program          |
| 1     | Task/Activity          | -                         | Conduct Assessments in Region IX           |
| 2     | Subtask                | Initial subtask           | Draft questionnaire                        |
| 3     | Sub-subtask            | 1st nested level          | Research best practices                    |
| 4     | Sub-sub-subtask        | 2nd nested level          | Review UNHCR guidelines                    |
| 5     | Sub-sub-sub-subtask    | 3rd nested level (MAX)    | Document key findings                      |

**Note:** Level 0 can be Project or Activity depending on hierarchy structure.
**Key:** A subtask at level 2 can have 3 levels of children below it (levels 3, 4, 5).

---

## Configuration

### Adjusting Maximum Level

To change the maximum nesting level, update `MAX_SUBTASK_LEVEL` in the model:

```python
# src/common/work_item_model.py

# Current: Allow up to level 5 (3 nested levels below subtask)
MAX_SUBTASK_LEVEL = 5

# Allow up to level 6 (4 nested levels below subtask)
MAX_SUBTASK_LEVEL = 6

# Unlimited nesting (not recommended for performance)
MAX_SUBTASK_LEVEL = None  # Requires additional logic to handle None case
```

---

## Migration Required?

**No database migration required.** Changes are:
- ✅ Application logic only (model validation)
- ✅ Template rendering (UI display)
- ✅ No schema changes

**Existing data is fully compatible.**

---

## Testing

### Manual Testing Steps
1. **Create a Task**
   - Navigate to work items
   - Create a new Task
2. **Add Subtask (Level 2)**
   - Open Task edit page
   - Click "Add Child Item"
   - Select "Subtask" type
   - Create subtask
3. **Add Sub-subtask (Level 3)**
   - Open Subtask (L2) edit page
   - Verify "Add Child Item" button is visible
   - Create another subtask (1st nested level below)
4. **Continue to Level 5**
   - Add Level 4 subtask (2nd nested level below)
   - Add Level 5 subtask (3rd nested level below)
5. **Verify Level 5 Restriction**
   - Open Level 5 subtask edit page
   - Verify message: "This work item has reached the maximum nesting level (level 5)"
   - Verify no "Add Child Item" button

### Automated Tests
```bash
cd src
python -m pytest common/tests/test_work_item_model.py::TestWorkItemValidation::test_can_have_child_type -v
python -m pytest common/tests/test_work_item_model.py::TestWorkItemValidation::test_subtask_max_level_constraint -v
```

**Expected Output:**
```
✅ 2 passed
```

---

## Edge Cases Handled

1. **Unsaved Objects**
   - `self.level is None` for unsaved objects
   - Validation skips level check for unsaved items
   - Allows form validation without database save

2. **Concurrent Hierarchy Changes**
   - MPTT automatically rebuilds tree structure
   - Level recalculated on save

3. **Circular References**
   - Already prevented by WorkItemForm validation
   - Cannot set parent to self or descendant

---

## Performance Considerations

### MPTT Tree Queries
- Subtask nesting increases tree depth
- **Impact:** Minimal (MPTT is optimized for deep trees)
- **Indexes:** Already in place for `tree_id`, `lft`, `rght`, `level`

### Query Performance
```python
# Getting all descendants (optimized by MPTT)
descendants = work_item.get_descendants()

# Getting specific level (efficient with level filter)
level_5_items = work_item.get_descendants().filter(level=5)
```

**Recommendation:** Monitor query performance if average depth exceeds 4 levels.

---

## Related Documentation

- [Work Item Model Architecture](../refactor/UNIFIED_WORK_HIERARCHY_EVALUATION.md)
- [MPTT Documentation](https://django-mptt.readthedocs.io/)
- [Work Item View Logic](../../src/common/views/work_items.py)

---

## Rollback Plan

If issues arise, revert to previous behavior:

```python
# src/common/work_item_model.py

ALLOWED_CHILD_TYPES = {
    # ... other types ...
    WORK_TYPE_SUBTASK: [],  # Revert to no children
}

def can_have_child_type(self, child_type):
    """Check if this work item can have the specified child type."""
    return child_type in self.ALLOWED_CHILD_TYPES.get(self.work_type, [])
```

**No migration needed for rollback.**

---

## Future Enhancements

### Potential Improvements
1. **Visual Tree Depth Indicators**
   - Add indentation/icons in tree view
   - Color-code by depth level

2. **Performance Optimizations**
   - Add caching for deep tree queries
   - Lazy load deep subtasks

3. **Bulk Operations**
   - Move entire subtask branches
   - Bulk status updates for subtree

4. **Analytics**
   - Track average nesting depth per project
   - Identify overly complex hierarchies

---

## Conclusion

✅ **Subtasks can now have children up to level 5 (3 nested levels below initial subtask)**
✅ **Tests pass (2/2)**
✅ **No migration required**
✅ **Backward compatible**
✅ **Production ready**

Users can now create more granular task breakdowns for complex workflows while maintaining system performance and data integrity.

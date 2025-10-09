# Test Plan: Work Item Creation from PPA Page Fix

## Problem Fixed
Work items created from PPA detail page didn't appear in the Work Items Hierarchy table because they weren't being auto-parented to the PPA's execution_project.

## Fix Applied
Modified `src/common/views/work_items.py` line 1061-1069 to:
- Auto-set `parent = related_ppa.execution_project` when creating from PPA
- Ensure work items appear immediately in the hierarchy

## Testing Steps

### 1. Verify PPA has execution_project
```python
from monitoring.models import MonitoringEntry

# Get the PPA (ID from URL: 4b820757-a697-455c-94cd-f4d2997d1f02)
ppa = MonitoringEntry.objects.get(pk='4b820757-a697-455c-94cd-f4d2997d1f02')
print(f"PPA: {ppa.title}")
print(f"Has execution_project: {ppa.execution_project is not None}")
if ppa.execution_project:
    print(f"Execution project: {ppa.execution_project.title}")
    print(f"Execution project ID: {ppa.execution_project.id}")
    print(f"Existing children: {ppa.execution_project.get_children().count()}")
```

### 2. Create Test Work Item (simulating form submission)
```python
from common.work_item_model import WorkItem
from django.contrib.auth import get_user_model

User = get_user_model()
admin = User.objects.filter(is_superuser=True).first()

# Create work item with PPA link
work_item = WorkItem(
    title="Test Work Item - PPA Fix Verification",
    work_type=WorkItem.WORK_TYPE_ACTIVITY,
    status=WorkItem.STATUS_NOT_STARTED,
    priority=WorkItem.PRIORITY_MEDIUM,
    description="Testing auto-parent to execution_project fix",
    created_by=admin
)

# Link to PPA
work_item.related_ppa = ppa

# Apply fix: auto-parent to execution_project if exists
if ppa.execution_project and not work_item.parent:
    work_item.parent = ppa.execution_project
    print(f"✅ Auto-parented to execution_project: {ppa.execution_project.id}")

# Populate isolation fields
work_item.populate_isolation_fields()

# Save
work_item.save()

print(f"✅ Work item created: {work_item.id}")
print(f"   - Parent: {work_item.parent}")
print(f"   - Related PPA: {work_item.related_ppa}")
print(f"   - PPA Category: {work_item.ppa_category}")
print(f"   - Implementing MOA: {work_item.implementing_moa}")
```

### 3. Verify Work Item Appears in Hierarchy Query
```python
# Simulate the query from monitoring/views.py _build_workitem_context
execution_project = ppa.execution_project

# Get immediate children (should now include our test work item)
work_items = execution_project.get_children().select_related("created_by")

print(f"\n📊 Work Items Hierarchy (execution_project children):")
print(f"Total count: {work_items.count()}")
for wi in work_items:
    print(f"  - {wi.get_work_type_display()}: {wi.title}")
    print(f"    ID: {wi.id}, Parent: {wi.parent_id}")
```

### 4. Verify in Database Directly
```python
# Check database state
from django.db import connection

cursor = connection.cursor()
cursor.execute("""
    SELECT
        id,
        work_type,
        title,
        parent_id,
        related_ppa_id,
        ppa_category,
        implementing_moa_id
    FROM common_work_item
    WHERE related_ppa_id = %s
    ORDER BY created_at DESC
    LIMIT 5
""", [str(ppa.id)])

print("\n🗄️  Database Query Results (recent work items for this PPA):")
for row in cursor.fetchall():
    print(f"  - {row[1]}: {row[2]}")
    print(f"    Parent ID: {row[3]}, Related PPA: {row[4]}")
```

### 5. Clean Up Test Data
```python
# Delete test work item
work_item.delete()
print(f"✅ Test work item deleted")
```

## Expected Results

✅ **BEFORE FIX:**
- Work item created with `related_ppa` set
- `parent` field was NULL (orphaned)
- Did NOT appear in execution_project.get_children()
- Table showed "0 items displayed"

✅ **AFTER FIX:**
- Work item created with `related_ppa` set
- `parent` field AUTO-SET to execution_project
- DOES appear in execution_project.get_children()
- Table shows work item immediately

## Testing in Browser

1. Navigate to: http://localhost:8000/monitoring/entry/4b820757-a697-455c-94cd-f4d2997d1f02/
2. Click "Work Items" tab
3. Click "Add Work Item" button
4. Fill in form:
   - Type: Activity
   - Title: "Browser Test - PPA Work Item"
   - Status: Not Started
   - Priority: Medium
5. Click "Create Work Item"
6. ✅ **Verify:** Work item appears immediately in hierarchy table
7. ✅ **Verify:** Table count updates from "0 items displayed" to "1 item displayed"

## Rollback Plan

If fix causes issues:
```bash
git checkout src/common/views/work_items.py
```

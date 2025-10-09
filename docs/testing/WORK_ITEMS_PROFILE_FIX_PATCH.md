# Work Items Profile Page - Code Patch

**File**: `src/common/views/management.py`
**Function**: `build_staff_profile_detail_context` (lines 204-305)

---

## Change 1: Recent Work Items Query (Lines 267-270)

### BEFORE (Current - Restrictive)
```python
recent_tasks = (
    WorkItem.objects.filter(work_type="task", assignees=profile.user)
    .prefetch_related("teams", "assignees")
    .order_by("-updated_at")[:10]
)
```

### AFTER (Fixed - Inclusive)
```python
recent_tasks = (
    WorkItem.objects.filter(assignees=profile.user)
    .prefetch_related("teams", "assignees")
    .order_by("-updated_at")[:10]
)
```

**Change**: Remove `work_type="task",` from the filter

---

## Change 2: Status Distribution Query (Lines 276-281)

### BEFORE (Current - Restrictive)
```python
tasks_by_status = {
    label: profile.user.assigned_work_items.filter(
        work_type="task", status=status
    ).count()
    for status, label in WorkItem.STATUS_CHOICES
}
```

### AFTER (Fixed - Inclusive)
```python
tasks_by_status = {
    label: profile.user.assigned_work_items.filter(
        status=status
    ).count()
    for status, label in WorkItem.STATUS_CHOICES
}
```

**Change**: Remove `work_type="task",` from the filter

---

## Unified Diff Format

```diff
--- a/src/common/views/management.py
+++ b/src/common/views/management.py
@@ -265,7 +265,7 @@ def build_staff_profile_detail_context(
     )

     recent_tasks = (
-        WorkItem.objects.filter(work_type="task", assignees=profile.user)
+        WorkItem.objects.filter(assignees=profile.user)
         .prefetch_related("teams", "assignees")
         .order_by("-updated_at")[:10]
     )
@@ -274,7 +274,7 @@ def build_staff_profile_detail_context(

     tasks_by_status = {
         label: profile.user.assigned_work_items.filter(
-            work_type="task", status=status
+            status=status
         ).count()
         for status, label in WorkItem.STATUS_CHOICES
     }
```

---

## Quick Apply Commands

### Option 1: Manual Edit
1. Open `src/common/views/management.py` in your editor
2. Go to line 268
3. Remove `work_type="task", ` from the filter
4. Go to line 277
5. Remove `work_type="task", ` from the filter
6. Save the file

### Option 2: Using sed (macOS/Linux)
```bash
cd /Users/saidamenmambayao/Library/Mobile\ Documents/com~apple~CloudDocs/BTA/OOBC/obcms

# Backup the file first
cp src/common/views/management.py src/common/views/management.py.backup

# Apply the changes
sed -i '' 's/WorkItem.objects.filter(work_type="task", assignees=profile.user)/WorkItem.objects.filter(assignees=profile.user)/g' src/common/views/management.py

sed -i '' 's/profile.user.assigned_work_items.filter(\n            work_type="task", status=status/profile.user.assigned_work_items.filter(\n            status=status/g' src/common/views/management.py
```

### Option 3: Interactive Python Fix
```bash
cd /Users/saidamenmambayao/Library/Mobile\ Documents/com~apple~CloudDocs/BTA/OOBC/obcms

python3 << 'EOF'
import re

# Read the file
with open('src/common/views/management.py', 'r') as f:
    content = f.read()

# Apply fix 1: Remove work_type filter from recent_tasks query
content = content.replace(
    'WorkItem.objects.filter(work_type="task", assignees=profile.user)',
    'WorkItem.objects.filter(assignees=profile.user)'
)

# Apply fix 2: Remove work_type filter from tasks_by_status query
content = re.sub(
    r'profile\.user\.assigned_work_items\.filter\(\s*work_type="task",\s*status=status',
    'profile.user.assigned_work_items.filter(\n            status=status',
    content
)

# Write back
with open('src/common/views/management.py', 'w') as f:
    f.write(content)

print("✅ Changes applied successfully!")
EOF
```

---

## Verification

### After applying the fix, verify the changes:

```bash
cd /Users/saidamenmambayao/Library/Mobile\ Documents/com~apple~CloudDocs/BTA/OOBC/obcms

# Check the changes
grep -n "recent_tasks = (" src/common/views/management.py -A 3

# Expected output:
# 267:    recent_tasks = (
# 268:        WorkItem.objects.filter(assignees=profile.user)
# 269:        .prefetch_related("teams", "assignees")
# 270:        .order_by("-updated_at")[:10]

grep -n "tasks_by_status = {" src/common/views/management.py -A 3

# Expected output:
# 276:    tasks_by_status = {
# 277:        label: profile.user.assigned_work_items.filter(
# 278:            status=status
# 279:        ).count()
```

---

## Testing Steps

1. **Apply the fix** using one of the methods above
2. **Restart Django server**:
   ```bash
   cd src
   python manage.py runserver
   ```
3. **Navigate to**: `http://localhost:8000/profile/?tab=tasks`
4. **Verify**:
   - "Assigned tasks" section shows work items (e.g., "Draeganess")
   - Status distribution shows correct counts (not all zeros)
   - Calendar still displays work items correctly

---

## Rollback (If Needed)

If the fix causes issues, restore the backup:

```bash
cd /Users/saidamenmambayao/Library/Mobile\ Documents/com~apple~CloudDocs/BTA/OOBC/obcms

# Restore from backup
mv src/common/views/management.py.backup src/common/views/management.py

# Restart server
cd src
python manage.py runserver
```

---

**Status**: Ready to apply
**Risk**: Low (query simplification, no schema changes)
**Testing Required**: Manual verification on `/profile/?tab=tasks`

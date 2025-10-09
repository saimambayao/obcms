# Work Item Edit Button - Quick Test Guide

## 🎯 Quick Test (5 minutes)

### Prerequisites
- Server running: `cd src && ./manage.py runserver`
- Browser DevTools Console open (F12)

### Test on Monitoring Page

**URL:** http://localhost:8000/monitoring/entry/860b79c9-b46c-4ec5-86e3-6e5a34a13b43/

1. **Click "Work Items" tab**
2. **Click any work item row** (View Details button)
3. **Sidebar slides in** with work item details
4. **Click blue "Edit" button**

**Expected Results:**

✅ **Console shows:**
```
[Work Item Edit] Detected PPA sidebar container
[Work Item Edit] Loading edit form: {workItemId: "...", targetId: "ppa-sidebar-content", ...}
[Work Item Edit] Edit form loaded successfully
```

✅ **UI shows:**
- Edit form appears in sidebar
- Form fields populated with work item data
- No page reload
- No HTMX errors

❌ **If it fails:**
```
[Work Item Edit] Target element not found: ppa-sidebar-content
Toast: "Error loading edit form"
```

---

## 🔍 What Was Fixed?

**Before:**
- Edit button used `hx-target="closest div.space-y-4"` → wrong element
- HTMX couldn't find target → `targetError`

**After:**
- Edit button uses `onclick="handleWorkItemEditClick(this)"` → JavaScript function
- Function detects correct sidebar container (`#ppa-sidebar-content`)
- Uses `htmx.ajax()` programmatically → correct target

---

## 📋 Files Changed

1. `src/templates/work_items/partials/sidebar_detail.html` - Edit button
2. `src/static/monitoring/js/workitem_integration.js` - JavaScript function
3. `src/templates/work_items/work_item_list.html` - Same function (inline)

---

## 🐛 Troubleshooting

### Issue: Console shows "Could not detect sidebar container"

**Cause:** Sidebar container ID has changed or doesn't exist

**Fix:** Check if `#ppa-sidebar-content` exists in DOM:
```javascript
console.log(document.getElementById('ppa-sidebar-content'));
```

### Issue: "Failed to load edit form" toast

**Cause:** HTMX request failed (404, 500, etc.)

**Fix:** Check Network tab for failed request, verify URL is correct

### Issue: Edit form doesn't appear

**Cause:** HTMX swap target is wrong

**Fix:** Verify console logs show correct `targetId`, check if element exists

---

## 📊 Test Checklist

- [ ] Monitoring page: Edit button works ✅
- [ ] Work Items page: Edit button works ✅
- [ ] Calendar page: Edit button works (if applicable)
- [ ] Console shows correct container detection
- [ ] No HTMX errors in console
- [ ] Smooth transition from detail to edit view
- [ ] Form fields populated correctly

---

## 📝 Next Steps

1. **Test on production data** - Verify with real PPAs
2. **Test on different browsers** - Chrome, Firefox, Safari
3. **Test on mobile** - Sidebar responsive behavior
4. **Consider centralizing function** - Create shared utility file

---

## 📖 Full Documentation

- **Implementation Details:** `/docs/improvements/WORK_ITEM_EDIT_BUTTON_FIX.md`
- **Summary:** `/docs/improvements/WORK_ITEM_EDIT_BUTTON_IMPLEMENTATION_SUMMARY.md`

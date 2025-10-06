# Calendar Width Expansion - Quick Test Guide

**Quick verification guide for calendar width expansion functionality.**

---

## 30-Second Visual Test

### Desktop (≥ 1024px)

1. **Open:** Advanced Modern Calendar
2. **Check icon:** Should show **chevron-left (←)**
3. **Click toggle:** Icon changes to **chevron-right (→)**
4. **Watch calendar:** Smoothly expands to full width (300ms animation)
5. **Click toggle again:** Icon changes to **chevron-left (←)**, calendar contracts

**Expected:** Smooth animations, no flicker, icon always correct.

### Mobile (< 1024px)

1. **Open:** Advanced Modern Calendar
2. **Check icon:** Should show **bars (☰)**
3. **Click toggle:** Icon changes to **times (×)**, sidebar slides in
4. **Click backdrop:** Sidebar closes, icon changes to **bars (☰)**

**Expected:** Smooth overlay, backdrop visible, calendar width unchanged.

---

## 60-Second Automated Test

### Run in Browser Console

1. Open Advanced Modern Calendar
2. Press **F12** (DevTools)
3. Go to **Console** tab
4. Paste this URL:

```javascript
fetch('https://raw.githubusercontent.com/tech-bangsamoro/obcms/main/docs/testing/verify_calendar_expansion.js')
  .then(r => r.text())
  .then(eval);
```

**Or** copy-paste the full script from `docs/testing/verify_calendar_expansion.js`

5. Press **Enter**
6. Review results

**Expected Output:**
```
🎉 ALL TESTS PASSED!
  Pass:  15
  Fail:  0
  Warn:  0
```

---

## Quick Debug Commands

### Check Current State

```javascript
const icon = document.getElementById('sidebarToggleIcon');
const container = document.querySelector('.calendar-container');

console.log('Icon:', icon.className);
console.log('Sidebar collapsed:', container.classList.contains('sidebar-collapsed'));
console.log('Grid columns:', getComputedStyle(container).gridTemplateColumns);
console.log('Calendar width:', document.querySelector('#calendar').offsetWidth + 'px');
```

### Test Toggle

```javascript
document.getElementById('toggleSidebarBtn').click();
setTimeout(() => {
    console.log('After toggle:');
    console.log('Icon:', document.getElementById('sidebarToggleIcon').className);
    console.log('Calendar width:', document.querySelector('#calendar').offsetWidth + 'px');
}, 400);
```

---

## Expected States Quick Reference

| Viewport | Initial Icon | After Toggle | Calendar Width Change |
|----------|--------------|--------------|----------------------|
| Desktop  | ← (chevron-left) | → (chevron-right) | Expands ~280px |
| Mobile   | ☰ (bars)     | × (times)    | No change (full width) |

---

## Common Issues

| Symptom | Likely Cause | Quick Fix |
|---------|-------------|-----------|
| Icon shows ☰ on desktop | JavaScript timing issue | Reload page |
| Calendar doesn't expand | `updateSize()` not called | Check console errors |
| Sidebar stuck | CSS class not toggled | Inspect element classes |

---

## Full Documentation

- **[Complete Testing Guide](CALENDAR_WIDTH_EXPANSION_TESTING_GUIDE.md)** - Comprehensive procedures
- **[Visual States Reference](CALENDAR_VISUAL_STATES_REFERENCE.md)** - Expected visual states
- **[Debug Snippet](CALENDAR_DEBUG_SNIPPET.md)** - Enhanced logging code
- **[Automated Script](verify_calendar_expansion.js)** - Full test automation

---

**Status:** Ready for Testing
**Last Updated:** 2025-10-06

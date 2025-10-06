# Calendar Fix - Step-by-Step Implementation Guide

**Version:** 1.0
**Date:** 2025-10-06
**Status:** READY TO IMPLEMENT
**Estimated Complexity:** Moderate (architectural changes, but well-defined)

---

## Quick Reference

**Problem:** Calendar is too narrow despite using grid layout
**Root Cause:** FullCalendar initializes before grid dimensions stabilize
**Solution:** Explicit dimensions + delayed initialization + proper height config

**Files to Modify:**
1. `src/templates/common/calendar_modern.html` (HTML structure + initialization)
2. `src/static/common/css/calendar-modern.css` (Layout CSS)
3. `src/static/common/js/calendar-modern.js` (FullCalendar config)

---

## Step 1: Backup Current Implementation

**PRIORITY: CRITICAL**

```bash
# Create backup branch
git checkout -b calendar-narrow-fix

# Backup files
cp src/templates/common/calendar_modern.html \
   src/templates/common/calendar_modern.html.backup

cp src/static/common/css/calendar-modern.css \
   src/static/common/css/calendar-modern.css.backup

cp src/static/common/js/calendar-modern.js \
   src/static/common/js/calendar-modern.js.backup

git add .
git commit -m "Backup before calendar architecture changes"
```

---

## Step 2: Update HTML Structure

**File:** `src/templates/common/calendar_modern.html`

### 2.1: Update Main Layout Container

**Find this section (around line 89-90):**
```html
{# Three-Column Layout: Sidebar | Calendar | Detail Panel #}
<div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
```

**Replace with:**
```html
{# Two-Column Layout: Sidebar | Calendar (Grid with explicit dimensions) #}
<div class="calendar-main-layout">
```

### 2.2: Update Sidebar Classes

**Find this section (around line 93):**
```html
<aside id="leftSidebar" class="lg:col-span-3 space-y-6">
```

**Replace with:**
```html
<aside id="leftSidebar" class="calendar-sidebar">
```

**Note:** Keep all the sidebar content unchanged, just update the outer `<aside>` class.

### 2.3: Update Calendar Container

**Find this section (around line 184-189):**
```html
{# Main Calendar Area #}
<main class="lg:col-span-9">
    <div class="bg-white rounded-2xl shadow-lg border border-gray-200 p-6">
        <div id="calendar"></div>
    </div>
</main>
```

**Replace with:**
```html
{# Main Calendar Area #}
<main class="calendar-main-container">
    <div class="calendar-card-wrapper">
        <div id="calendar" class="calendar-element"></div>
    </div>
</main>
```

### 2.4: Update Initialization Script

**Find the initialization script (around line 248-283):**
```html
<script>
(function() {
    'use strict';

    // Initialize modern calendar with OBCMS configuration
    window.modernCalendar = new ModernCalendar({
        calendarEl: document.getElementById('calendar'),
        // ... rest of config
    });

    console.log('✅ Modern Calendar initialized');

})();
</script>
```

**Replace with:**
```html
<script>
(function() {
    'use strict';

    // Wait for DOM and layout to be ready
    document.addEventListener('DOMContentLoaded', function() {
        // Double RAF ensures layout calculations are complete
        requestAnimationFrame(() => {
            requestAnimationFrame(() => {
                console.log('🚀 Initializing Modern Calendar with proper timing...');

                // Verify container has dimensions
                const calendarEl = document.getElementById('calendar');
                const rect = calendarEl.getBoundingClientRect();
                console.log('📐 Calendar container dimensions:', {
                    width: rect.width,
                    height: rect.height
                });

                if (rect.width === 0 || rect.height === 0) {
                    console.error('❌ Calendar container has zero dimensions!');
                    console.error('Check CSS: .calendar-element should have width and height');
                } else {
                    console.log('✅ Container sized correctly, initializing calendar...');
                }

                // Initialize modern calendar with OBCMS configuration
                window.modernCalendar = new ModernCalendar({
                    calendarEl: calendarEl,
                    miniCalendarEl: document.getElementById('miniCalendar'),
                    eventsFeedUrl: '{% url "common:work_items_calendar_feed" %}',
                    createUrl: '{% url "common:work_item_create" %}',
                    detailPanelEl: document.getElementById('eventDetailPanel'),
                    detailContentEl: document.getElementById('eventDetailContent'),
                    detailBackdropEl: document.getElementById('detailPanelBackdrop'),
                    modalEl: document.getElementById('eventModal'),
                    modalContentEl: document.getElementById('modalContent'),

                    // View persistence
                    storageKey: 'obcms_calendar_view_mode',

                    // Default view
                    defaultView: 'dayGridMonth',

                    // Callbacks
                    onEventClick: function(info) {
                        console.log('Event clicked:', info.event.title);
                    },

                    onViewChange: function(view) {
                        console.log('View changed to:', view.type);
                    }
                });

                console.log('✅ Modern Calendar initialized successfully');
            });
        });
    });

})();
</script>
```

---

## Step 3: Update CSS Layout

**File:** `src/static/common/css/calendar-modern.css`

### 3.1: Add Layout Classes at the Top

**Add after the header comment (around line 8), before view switcher styles:**

```css
/* ============================================
   CALENDAR LAYOUT ARCHITECTURE
   Fixed-height grid with explicit dimensions
   Reference: docs/improvements/UI/CALENDAR_ARCHITECTURE_CLEAN.md
   ============================================ */

/* Main Layout Container: Grid with explicit dimensions */
.calendar-main-layout {
    display: grid;
    grid-template-columns: 320px 1fr;
    gap: 1.5rem; /* 24px */
    height: calc(100vh - 220px); /* Adjust based on header height */
    width: 100%;
    margin: 0;
    padding: 0;
}

/* Sidebar: Fixed width, scrollable */
.calendar-sidebar {
    width: 320px;
    height: 100%;
    overflow-y: auto;
    overflow-x: hidden;
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
    animation: slideInLeft 0.3s ease-out; /* Keep existing animation */
}

/* Calendar Main Container: Fills remaining grid space */
.calendar-main-container {
    width: 100%;
    height: 100%;
    min-width: 0; /* Allow grid to shrink if needed */
    display: flex;
    flex-direction: column;
}

/* Calendar Card Wrapper: White background card */
.calendar-card-wrapper {
    width: 100%;
    height: 100%;
    background: white;
    border-radius: 1rem;
    padding: 1.5rem;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05),
                0 1px 3px rgba(0, 0, 0, 0.1);
    border: 1px solid #E5E7EB;
    display: flex;
    flex-direction: column;
    overflow: hidden; /* Prevent calendar from overflowing card */
}

/* Calendar Element: CRITICAL - Must have explicit dimensions */
.calendar-element {
    width: 100%;
    height: 100%;
    flex: 1;
    min-height: 600px; /* Fallback minimum */
    position: relative;
}

/* ============================================
   RESPONSIVE: Tablet and Mobile
   ============================================ */

/* Tablet: Stack sidebar and calendar */
@media (max-width: 1024px) {
    .calendar-main-layout {
        grid-template-columns: 1fr; /* Single column */
        height: auto; /* Allow natural height */
        gap: 0; /* Remove gap, sidebar is overlay */
    }

    .calendar-sidebar {
        position: fixed;
        inset-y: 0;
        left: 0;
        width: 320px;
        transform: translateX(-100%);
        transition: transform 0.3s ease;
        background: white;
        z-index: 60;
        box-shadow: 4px 0 15px rgba(0, 0, 0, 0.1);
        padding: 1.5rem;
    }

    .calendar-sidebar.open {
        transform: translateX(0);
    }

    .calendar-main-container {
        width: 100%;
        height: calc(100vh - 200px); /* Adjust for mobile header */
    }

    /* Sidebar toggle button (add to template if not exists) */
    .sidebar-toggle {
        position: fixed;
        bottom: 1.5rem;
        left: 1.5rem;
        z-index: 70;
        background: linear-gradient(135deg, #3B82F6 0%, #10B981 100%);
        color: white;
        width: 56px;
        height: 56px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
        cursor: pointer;
        transition: all 0.2s ease;
    }

    .sidebar-toggle:hover {
        box-shadow: 0 6px 20px rgba(59, 130, 246, 0.5);
        transform: translateY(-2px);
    }
}

/* Mobile: Further adjustments */
@media (max-width: 640px) {
    .calendar-main-layout {
        height: auto;
    }

    .calendar-main-container {
        height: calc(100vh - 170px);
    }

    .calendar-card-wrapper {
        padding: 1rem;
    }

    .calendar-element {
        min-height: 500px;
    }
}
```

### 3.2: Update Existing Calendar Container Styles

**Find this section (around line 318-321):**
```css
#calendar {
    min-height: 600px;
}
```

**Replace with:**
```css
/* Legacy ID selector (use .calendar-element class instead) */
#calendar {
    /* Styles moved to .calendar-element class above */
}
```

### 3.3: Remove Conflicting Responsive Styles (if any)

**Check the tablet adjustments section (around line 409-450).**

**If it contains sidebar positioning, verify it matches Step 3.1.**
If there are conflicts, prioritize the new styles from Step 3.1.

---

## Step 4: Update FullCalendar Configuration

**File:** `src/static/common/js/calendar-modern.js`

### 4.1: Update initMainCalendar Method

**Find the initMainCalendar method (around line 67-130):**

**Update the FullCalendar.Calendar configuration:**

```javascript
initMainCalendar() {
    if (!this.options.calendarEl) {
        console.error('❌ Calendar element not found');
        return;
    }

    const self = this;

    // Log container dimensions for debugging
    const rect = this.options.calendarEl.getBoundingClientRect();
    console.log('📐 Initializing calendar with container dimensions:', {
        width: rect.width,
        height: rect.height
    });

    this.calendar = new FullCalendar.Calendar(this.options.calendarEl, {
        initialView: this.currentView,

        // ============================================
        // SIZING CONFIGURATION (UPDATED)
        // ============================================

        // Use 'parent' to fill container exactly
        height: 'parent',

        // Disable aspectRatio (we control height via CSS)
        aspectRatio: undefined,

        // Expand rows to fill available height
        expandRows: true,

        // Handle window resize automatically
        handleWindowResize: true,

        // Debounce resize events (performance)
        windowResizeDelay: 100,

        // ============================================
        // TOOLBAR & VIEW CONFIGURATION
        // ============================================

        headerToolbar: {
            left: 'prev,next',
            center: 'title',
            right: '' // View buttons in separate UI
        },

        dayMaxEvents: 4,
        moreLinkClick: 'popover',
        eventDisplay: 'block',
        displayEventTime: true,
        displayEventEnd: false,

        // Multi-month year view configuration
        multiMonthMaxColumns: 3,
        multiMonthMinWidth: 300,

        // ============================================
        // DATA & INTERACTIONS (UNCHANGED)
        // ============================================

        // Events source
        events: function(info, successCallback, failureCallback) {
            self.fetchEvents(info, successCallback, failureCallback);
        },

        // Event click handler
        eventClick: function(info) {
            info.jsEvent.preventDefault();
            self.handleEventClick(info);
        },

        // Event content rendering
        eventContent: function(arg) {
            return self.buildEventContent(arg);
        },

        // Event mounting (for attributes and tooltips)
        eventDidMount: function(info) {
            self.setupEventAttributes(info);
        },

        // Date click handler
        dateClick: function(info) {
            self.handleDateClick(info);
        },

        // View change handler
        datesSet: function(dateInfo) {
            if (self.options.onViewChange) {
                self.options.onViewChange(dateInfo);
            }
            self.updateMiniCalendarDate(dateInfo.start);
        }
    });

    this.calendar.render();

    // Log calendar dimensions after render
    setTimeout(() => {
        const calendarRect = this.calendar.el.getBoundingClientRect();
        console.log('📐 Calendar rendered with dimensions:', {
            width: calendarRect.width,
            height: calendarRect.height
        });
    }, 100);

    console.log('✅ Main calendar rendered');
}
```

**Key Changes:**
- `height: 'parent'` (changed from `'auto'`)
- `aspectRatio: undefined` (disable aspect ratio)
- `expandRows: true` (fill available height)
- `handleWindowResize: true` (auto-adjust on resize)
- `windowResizeDelay: 100` (debounce for performance)

---

## Step 5: Test the Implementation

### 5.1: Visual Verification

**Open the calendar page:**
```bash
cd src
./manage.py runserver
# Navigate to: http://localhost:8000/oobc-management/staff/calendar/
```

**Check these items:**

1. **Desktop (1920px):**
   - [ ] Calendar fills width between sidebar and right edge
   - [ ] Calendar height fills viewport (minus header)
   - [ ] No horizontal scrollbar
   - [ ] No white space on right side

2. **Resize browser window:**
   - [ ] Calendar smoothly adjusts width
   - [ ] No jumpy transitions
   - [ ] Maintains proper aspect at all sizes

3. **Tablet (768px):**
   - [ ] Sidebar becomes overlay (or stacks)
   - [ ] Calendar expands to full width
   - [ ] Toggle button appears (if implemented)

4. **Mobile (375px):**
   - [ ] Calendar is full width
   - [ ] Minimum height maintained
   - [ ] All views work properly

### 5.2: Console Verification

**Open browser DevTools Console, look for:**

```
🚀 Initializing Modern Calendar with proper timing...
📐 Calendar container dimensions: { width: 1480, height: 852 }
✅ Container sized correctly, initializing calendar...
📐 Initializing calendar with container dimensions: { width: 1480, height: 852 }
✅ Main calendar rendered
📐 Calendar rendered with dimensions: { width: 1480, height: 852 }
✅ Mini calendar rendered
✅ Modern Calendar initialized successfully
```

**Expected dimensions (1920px viewport):**
- Container width: ~1480px (viewport - sidebar - padding - gaps)
- Container height: ~850px (viewport - header - padding)

**If you see width: 0 or height: 0:**
- Check CSS: `.calendar-element` has proper styles
- Check initialization timing: Double RAF is running
- Check grid: `.calendar-main-layout` has `grid-template-columns: 320px 1fr`

### 5.3: Dimension Checks (DevTools)

**Inspect calendar container:**

```javascript
// In browser console:
const el = document.getElementById('calendar');
const rect = el.getBoundingClientRect();
console.log('Container:', rect.width, 'x', rect.height);

const parent = el.parentElement;
const parentRect = parent.getBoundingClientRect();
console.log('Parent:', parentRect.width, 'x', parentRect.height);
```

**Expected:**
- Container and parent should have same dimensions
- Width should be ~80% of viewport (after sidebar)
- Height should be ~80% of viewport (after header)

### 5.4: View Switching

**Test all views:**
- [ ] Month view: Calendar fills container
- [ ] Week view: Calendar fills container
- [ ] Day view: Calendar fills container
- [ ] Year view: Grid layout adjusts, all months visible

---

## Step 6: Troubleshooting

### Issue 1: Calendar Still Narrow

**Check:**
1. CSS classes applied correctly (`.calendar-main-layout`, `.calendar-element`)
2. Grid columns set to `320px 1fr` (not spans)
3. FullCalendar config has `height: 'parent'`
4. Initialization using double RAF

**Debug:**
```javascript
// In browser console:
const layout = document.querySelector('.calendar-main-layout');
console.log('Grid columns:', window.getComputedStyle(layout).gridTemplateColumns);
// Expected: "320px 1fr" or "320px 1528px" (calculated)
```

### Issue 2: Calendar Height Too Short

**Check:**
1. `.calendar-main-layout` has `height: calc(100vh - 220px)` (adjust offset)
2. `.calendar-element` has `height: 100%` and `flex: 1`
3. FullCalendar config has `expandRows: true`

**Adjust height offset:**
```css
/* If header is taller/shorter, adjust offset: */
.calendar-main-layout {
    height: calc(100vh - 240px); /* Increase if header is taller */
}
```

### Issue 3: Calendar Doesn't Resize

**Check:**
1. `handleWindowResize: true` in FullCalendar config
2. No JavaScript errors in console
3. Calendar initialized successfully

**Force resize:**
```javascript
// In browser console:
window.modernCalendar.calendar.updateSize();
```

### Issue 4: Zero Dimensions Error

**Error:** "Calendar container has zero dimensions!"

**Fix:**
1. Verify CSS file loaded (check Network tab)
2. Check `.calendar-element` class exists on `#calendar` div
3. Try increasing RAF delay:
   ```javascript
   requestAnimationFrame(() => {
       requestAnimationFrame(() => {
           setTimeout(() => {
               // Initialize calendar here
           }, 50); // Add 50ms extra delay
       });
   });
   ```

---

## Step 7: Commit Changes

**After successful testing:**

```bash
# Check what changed
git status
git diff src/templates/common/calendar_modern.html
git diff src/static/common/css/calendar-modern.css
git diff src/static/common/js/calendar-modern.js

# Stage changes
git add src/templates/common/calendar_modern.html
git add src/static/common/css/calendar-modern.css
git add src/static/common/js/calendar-modern.js

# Commit with descriptive message
git commit -m "Fix calendar narrow width issue

- Update HTML structure: Grid with explicit dimensions (320px 1fr)
- Update CSS: Add .calendar-main-layout with fixed height
- Update FullCalendar config: height: 'parent', expandRows: true
- Update initialization: Double RAF for layout stabilization
- Add auto-resize: handleWindowResize: true

Resolves narrow calendar issue by ensuring FullCalendar initializes
after grid layout calculations are complete and parent container has
concrete dimensions.

Reference: docs/improvements/UI/CALENDAR_ARCHITECTURE_CLEAN.md"

# Push to remote
git push origin calendar-narrow-fix
```

---

## Step 8: Documentation Updates

**After successful implementation, update these docs:**

1. **`docs/ui/OBCMS_UI_COMPONENTS_STANDARDS.md`**
   - Add "Calendar Layout Pattern" section
   - Document `.calendar-main-layout` structure

2. **`docs/development/README.md`**
   - Add reference to calendar architecture guide

3. **`CLAUDE.md`**
   - Update "Instant UI & Smooth User Experience" section
   - Add calendar initialization best practices

---

## Rollback Plan

**If implementation fails, rollback is simple:**

```bash
# Restore backup files
cp src/templates/common/calendar_modern.html.backup \
   src/templates/common/calendar_modern.html

cp src/static/common/css/calendar-modern.css.backup \
   src/static/common/css/calendar-modern.css

cp src/static/common/js/calendar-modern.js.backup \
   src/static/common/js/calendar-modern.js

# Or revert commit
git revert HEAD

# Or checkout previous commit
git checkout HEAD~1 -- src/templates/common/calendar_modern.html
git checkout HEAD~1 -- src/static/common/css/calendar-modern.css
git checkout HEAD~1 -- src/static/common/js/calendar-modern.js
```

---

## Summary Checklist

**Before starting:**
- [ ] Read `CALENDAR_ARCHITECTURE_CLEAN.md` (architecture overview)
- [ ] Review `CALENDAR_ARCHITECTURE_DIAGRAMS.md` (visual diagrams)
- [ ] Create backup branch
- [ ] Backup current files

**Implementation:**
- [ ] Step 1: Backup files ✅
- [ ] Step 2: Update HTML structure (template)
- [ ] Step 3: Update CSS layout (modern.css)
- [ ] Step 4: Update FullCalendar config (modern.js)

**Testing:**
- [ ] Step 5: Test on desktop (1920px, 1366px)
- [ ] Step 5: Test on tablet (768px)
- [ ] Step 5: Test on mobile (375px)
- [ ] Step 5: Test window resize
- [ ] Step 5: Test view switching
- [ ] Step 5: Check console logs

**Completion:**
- [ ] Step 6: Troubleshoot any issues
- [ ] Step 7: Commit changes
- [ ] Step 8: Update documentation
- [ ] Deploy to staging
- [ ] Final production deployment

---

**Total Estimated Time:** 1-2 hours (including testing)
**Complexity:** Moderate (architectural changes, but well-defined)
**Risk:** Low (can rollback easily)

**Questions?** Refer to:
- `docs/improvements/UI/CALENDAR_ARCHITECTURE_CLEAN.md` - Full architecture
- `docs/improvements/UI/CALENDAR_ARCHITECTURE_DIAGRAMS.md` - Visual diagrams
- FullCalendar Sizing Docs - https://fullcalendar.io/docs/sizing

# Advanced Modern Calendar - Visual Verification Checklist

**Date:** 2025-01-06
**Template:** `src/templates/common/calendar_advanced_modern.html`
**URL:** `/calendar/advanced-modern/`

## Pre-Testing Setup

1. **Start Development Server:**
   ```bash
   cd /path/to/obcms/src
   source ../venv/bin/activate
   ./manage.py runserver
   ```

2. **Navigate to Calendar:**
   - URL: `http://localhost:8000/calendar/advanced-modern/`
   - Or click: Dashboard → Calendar → Advanced Modern View

3. **Browser DevTools:**
   - Open Chrome DevTools (F12)
   - Enable Device Toolbar (Ctrl+Shift+M)
   - Clear browser cache (Ctrl+Shift+Delete)

## Visual Verification Steps

### 1. Breadcrumb Navigation ✅

**Expected:**
```
Home > Calendar > Advanced Modern View
```

**Check:**
- [ ] Breadcrumb appears below navbar
- [ ] Home icon links to dashboard
- [ ] "Calendar" links to work item list
- [ ] "Advanced Modern View" is bold (current page)
- [ ] Chevron icons between items
- [ ] Hover states work on links

**Screenshot Location:** `docs/testing/screenshots/calendar_breadcrumb.png`

---

### 2. Calendar Height - Desktop (1920x1080)

**Expected:**
- Calendar fills from breadcrumb to bottom of viewport
- Footer visible by scrolling down
- No empty white space below calendar
- No vertical scrollbar on calendar itself

**Check:**
- [ ] Calendar container height = `calc(100vh - 106px)`
- [ ] Navbar: 64px
- [ ] Breadcrumb: ~42px
- [ ] Calendar fills remaining space
- [ ] Footer appears below calendar (scroll to see)

**DevTools Measurement:**
1. Inspect `<div class="calendar-container">`
2. Verify computed height ≈ viewport height - 106px
3. Example: 1080px viewport → 974px calendar container

**Screenshot Location:** `docs/testing/screenshots/calendar_fullheight_desktop.png`

---

### 3. Calendar Height - Laptop (1440x900)

**Expected:**
- Calendar still fills available space
- No overflow or empty space
- Footer visible by scrolling

**Check:**
- [ ] Calendar container height = viewport - 106px
- [ ] No fixed 650px constraint
- [ ] Responsive to window resize

**DevTools Measurement:**
- 900px viewport → 794px calendar container

**Screenshot Location:** `docs/testing/screenshots/calendar_fullheight_laptop.png`

---

### 4. Calendar Height - Mobile (375x667 - iPhone SE)

**Expected:**
- Sidebar hidden by default (overlay mode)
- Calendar fills mobile viewport
- Touch scrolling works

**Check:**
- [ ] Sidebar toggle button visible
- [ ] Calendar responsive
- [ ] No horizontal scroll
- [ ] Footer accessible via scroll

**Screenshot Location:** `docs/testing/screenshots/calendar_mobile.png`

---

### 5. Sidebar Toggle - Desktop

**Expected:**
- Click toggle: Sidebar collapses to left
- Click again: Sidebar expands
- Calendar resizes smoothly
- FullCalendar re-renders to fill space

**Check:**
- [ ] Toggle button shows bars icon when sidebar open
- [ ] Shows times icon when sidebar closed
- [ ] Smooth 300ms transition
- [ ] Grid template columns: `280px 1fr 0px` → `0px 1fr 0px`
- [ ] Calendar events remain visible

**Screenshot Location:** `docs/testing/screenshots/calendar_sidebar_toggle.png`

---

### 6. Sidebar Toggle - Mobile

**Expected:**
- Click toggle: Sidebar slides in from left (overlay)
- Backdrop appears (semi-transparent)
- Click backdrop or X: Sidebar closes

**Check:**
- [ ] Sidebar appears as overlay (not pushing content)
- [ ] Backdrop visible
- [ ] Click outside closes sidebar
- [ ] Close button (X) works

**Screenshot Location:** `docs/testing/screenshots/calendar_mobile_sidebar.png`

---

### 7. Detail Panel - Desktop

**Expected:**
- Click event: Detail panel slides in from right
- Calendar resizes to accommodate
- Grid columns: `280px 1fr 0px` → `280px 1fr 380px`
- Close button works

**Check:**
- [ ] Detail panel width: 380px
- [ ] Smooth transition
- [ ] Event details display correctly
- [ ] "View Full Details" button works (HTMX modal)
- [ ] Close button (X) works
- [ ] Backdrop click closes panel

**Screenshot Location:** `docs/testing/screenshots/calendar_detail_panel.png`

---

### 8. Footer Visibility

**Expected:**
- Footer appears after calendar (may need scroll)
- "BANGSAMORO KA, SAAN KA MAN!" visible
- Footer content readable

**Check:**
- [ ] Scroll down to see footer
- [ ] Footer not hidden or cut off
- [ ] Footer background: gray-800
- [ ] Footer text: white
- [ ] Mosque icon visible

**Screenshot Location:** `docs/testing/screenshots/calendar_footer.png`

---

### 9. View Mode Switching

**Expected:**
- Click Month/Week/Day/Year buttons
- Calendar changes view
- Height remains consistent
- No layout shift

**Check:**
- [ ] Month view: Grid layout
- [ ] Week view: TimeGrid with hours
- [ ] Day view: Single day timeGrid
- [ ] Year view: Multi-month grid
- [ ] Active button highlighted (white background)
- [ ] Calendar fills available height in all views

**Screenshot Location:** `docs/testing/screenshots/calendar_view_modes.png`

---

### 10. Mini Calendar Interaction

**Expected:**
- Click date in mini calendar
- Main calendar jumps to that date
- Selected date highlighted in mini calendar

**Check:**
- [ ] Mini calendar renders current month
- [ ] Today highlighted (blue)
- [ ] Click date: Main calendar navigates
- [ ] Selected date highlighted (green)
- [ ] Previous/Next month buttons work

**Screenshot Location:** `docs/testing/screenshots/calendar_mini_calendar.png`

---

### 11. Event Type Filters

**Expected:**
- Checkboxes for Projects, Activities, Tasks, Coordination
- Uncheck: Events of that type disappear
- Check: Events reappear
- Smooth transition

**Check:**
- [ ] All checkboxes checked by default
- [ ] Uncheck "Projects": Blue events disappear
- [ ] Uncheck "Activities": Green events disappear
- [ ] Uncheck "Tasks": Purple events disappear
- [ ] Uncheck "Coordination": Teal events disappear
- [ ] Calendar refetches events on filter change

**Screenshot Location:** `docs/testing/screenshots/calendar_filters.png`

---

### 12. Loading States

**Expected:**
- Initial load: Spinner appears
- Spinner disappears when calendar renders
- No flash of unstyled content

**Check:**
- [ ] Loading spinner visible on page load
- [ ] Spinner centers in calendar area
- [ ] Spinner disappears after calendar renders
- [ ] No layout shift during load

**Screenshot Location:** `docs/testing/screenshots/calendar_loading.png`

---

## DevTools Inspection Checklist

### CSS Measurements

**Desktop (1920x1080):**
```
.calendar-container
  ├── height: calc(100vh - 106px) ≈ 974px
  ├── grid-template-columns: 280px 1fr 0px
  └── grid-template-rows: auto 1fr

.calendar-main
  ├── display: flex
  ├── flex-direction: column
  └── grid-row: 2 / 3

#calendar
  ├── flex: 1
  ├── min-height: 0
  └── computed height: ~850px (fills parent)

.fc (FullCalendar root)
  ├── height: 100% (fills #calendar)
  └── computed height: ~850px
```

**Check in DevTools:**
- [ ] `.calendar-container` computed height matches `100vh - 106px`
- [ ] `#calendar` has `flex: 1` applied
- [ ] `.fc` height is `100%` not `650px`
- [ ] No fixed pixel heights in computed styles

---

### JavaScript Console Checks

**Expected Console Logs:**
```
Rendering FullCalendar... {containerHeight: 850, containerWidth: 1500, view: "dayGridMonth"}
FullCalendar rendered successfully {calendarExists: true, ...}
Loading spinner hidden
```

**Check:**
- [ ] No JavaScript errors
- [ ] FullCalendar renders successfully
- [ ] Event fetch succeeds
- [ ] No 404 errors for static files

---

## Responsive Breakpoint Testing

### Desktop (≥1024px)

**Check:**
- [ ] Sidebar visible by default
- [ ] Grid layout: `280px 1fr 0px`
- [ ] Toggle collapses sidebar in-place
- [ ] Detail panel opens to right

### Tablet (768px - 1023px)

**Check:**
- [ ] Sidebar hidden by default
- [ ] Toggle shows sidebar as overlay
- [ ] Calendar fills width
- [ ] Footer visible

### Mobile (≤767px)

**Check:**
- [ ] Sidebar overlay mode
- [ ] Header buttons stack vertically
- [ ] View mode buttons full width
- [ ] Navigation buttons responsive
- [ ] Detail panel full width when open

---

## Performance Checks

### Initial Load

**Metrics:**
- [ ] First Contentful Paint (FCP): < 1.5s
- [ ] Largest Contentful Paint (LCP): < 2.5s
- [ ] Time to Interactive (TTI): < 3.5s
- [ ] Total Blocking Time (TBT): < 300ms

**DevTools → Performance:**
1. Start recording
2. Reload page
3. Stop recording
4. Check metrics

### Memory Usage

**Metrics:**
- [ ] Initial memory: < 50MB
- [ ] After 10 view changes: < 100MB
- [ ] No memory leaks

**DevTools → Memory:**
1. Take heap snapshot (initial)
2. Change views 10 times
3. Take heap snapshot (after)
4. Compare sizes

---

## Accessibility Testing

### Keyboard Navigation

**Check:**
- [ ] Tab through all interactive elements
- [ ] Enter opens detail panel
- [ ] Escape closes detail panel
- [ ] Arrow keys navigate mini calendar
- [ ] Focus visible on all elements

### Screen Reader (NVDA/JAWS)

**Check:**
- [ ] Breadcrumb navigation announced
- [ ] "Calendar" landmark announced
- [ ] Event details readable
- [ ] Button labels announced
- [ ] Loading states announced

---

## Browser Compatibility

**Test in:**
- [ ] Chrome 120+
- [ ] Firefox 120+
- [ ] Safari 17+
- [ ] Edge 120+

**Check:**
- [ ] Layout consistent across browsers
- [ ] No CSS rendering issues
- [ ] JavaScript works in all browsers

---

## Known Issues & Workarounds

### Issue 1: Footer Below Viewport

**Behavior:** Footer requires scroll to see (expected)

**Workaround:** This is intentional. Calendar fills viewport, footer appears below.

**Future Enhancement:** Add sticky footer toggle if needed.

---

### Issue 2: FullCalendar Flash on Load

**Behavior:** Brief moment where calendar is empty before rendering

**Workaround:** Loading spinner covers this.

**Future Enhancement:** Server-side rendering of initial calendar state.

---

## Sign-Off Checklist

**Before marking as verified:**
- [ ] All visual checks passed
- [ ] All DevTools measurements correct
- [ ] No console errors
- [ ] Responsive on all breakpoints
- [ ] Accessibility verified
- [ ] Performance metrics acceptable
- [ ] Browser compatibility confirmed

**Verified By:** _________________
**Date:** _________________
**Browser/OS:** _________________

---

## Regression Testing

**After future changes, re-verify:**
1. Calendar height still fills viewport
2. Breadcrumb still appears
3. Footer still visible
4. No fixed heights re-introduced

**Last Regression Test:** _________________

---

## Appendix: Expected Screenshots

All screenshots should be saved in `docs/testing/screenshots/` with descriptive names:

1. `calendar_breadcrumb.png` - Breadcrumb navigation
2. `calendar_fullheight_desktop.png` - Full height on desktop
3. `calendar_fullheight_laptop.png` - Full height on laptop
4. `calendar_mobile.png` - Mobile view
5. `calendar_sidebar_toggle.png` - Sidebar toggle animation
6. `calendar_mobile_sidebar.png` - Mobile sidebar overlay
7. `calendar_detail_panel.png` - Detail panel open
8. `calendar_footer.png` - Footer visibility
9. `calendar_view_modes.png` - Different view modes
10. `calendar_mini_calendar.png` - Mini calendar interaction
11. `calendar_filters.png` - Event type filters
12. `calendar_loading.png` - Loading state

---

**End of Verification Checklist**

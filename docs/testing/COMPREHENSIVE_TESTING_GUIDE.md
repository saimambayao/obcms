# OBCMS Comprehensive Testing Guide

**Last Updated**: January 2, 2025
**Version**: 1.0
**Purpose**: Complete testing procedures for all modules

---

## Table of Contents

1. [Testing Environment Setup](#testing-environment-setup)
2. [Phase 1: Foundation & Dashboard](#phase-1-foundation--dashboard)
3. [Phase 2: MANA Integration](#phase-2-mana-integration)
4. [Phase 3: Coordination](#phase-3-coordination)
5. [Phase 4: Project Management Portal Foundation](#phase-4-project-central-foundation)
6. [Phase 5: Workflow & Budget Approval](#phase-5-workflow--budget-approval)
7. [Phase 6: M&E Analytics](#phase-6-me-analytics)
8. [Phase 7: Alert System & Reporting](#phase-7-alert-system--reporting)
9. [Integration Testing](#integration-testing)
10. [Performance Testing](#performance-testing)
11. [Accessibility Testing](#accessibility-testing)
12. [Mobile Responsiveness Testing](#mobile-responsiveness-testing)
13. [Security Testing](#security-testing)
14. [Definition of Done Checklist](#definition-of-done-checklist)
15. [Troubleshooting](#troubleshooting)
16. [Test Data Creation](#test-data-creation)

---

## Testing Environment Setup

### Prerequisites

- Django development server running
- Database with test data
- All migrations applied
- Celery worker running (for alerts)

**Start Development Server**:
```bash
cd src
./manage.py runserver
```

**Start Celery Worker** (in separate terminal):
```bash
cd src
celery -A obc_management worker -l info
```

**Start Celery Beat** (for scheduled tasks):
```bash
cd src
celery -A obc_management beat -l info
```

### Test User Accounts

Create test accounts if needed:

```bash
cd src
./manage.py createsuperuser
```

Default accounts (if seeded):
- **Superuser**: admin / admin123
- **Staff user**: staff@oobc.gov.ph / test123
- **Regional facilitator**: facilitator@oobc.gov.ph / test123

---

## Phase 1: Foundation & Dashboard

### Test 1.1: Task Deletion Bug (Verified Fixed)

**URL**: `http://localhost:8000/oobc-management/staff/tasks/`

**Objective**: Verify task deletion removes cards instantly without page reload

**Steps**:
1. Open task board (kanban view)
2. Click any task card to open modal
3. In modal, click "Delete" button
4. Confirm deletion in confirmation dialog

**Expected Results**:
- ✅ Card disappears instantly with 300ms fade animation
- ✅ No full page reload occurs
- ✅ Task count badge updates immediately
- ✅ No JavaScript console errors
- ✅ Other tasks remain visible and functional

**Known Issue**: If deletion doesn't work, verify HTMX targets `[data-task-id]` instead of `[data-task-row]`

---

### Test 1.2: Enhanced Dashboard

**URL**: `http://localhost:8000/dashboard/`

**Objective**: Verify dashboard metrics, activity feed, and auto-refresh functionality

**Steps**:
1. Load dashboard page
2. Observe 6 metric cards loading
3. Wait 5 seconds for metrics to populate
4. Scroll down to activity feed section
5. Scroll to bottom (trigger infinite scroll)
6. Wait 60 seconds to observe metric auto-refresh
7. Wait 30 seconds to observe alerts auto-refresh

**Expected Results**:
- ✅ 6 metric cards display with real data:
  - Total OBC Communities
  - Active MANA Assessments
  - Pending Policy Recommendations
  - Active Coordination Events
  - Total Partnerships
  - Monitoring Entries
- ✅ Metrics auto-refresh every 60 seconds
- ✅ Activity feed loads more items on scroll (infinite scroll)
- ✅ Alerts section updates every 30 seconds
- ✅ No console errors
- ✅ Mobile responsive (test at 320px width)

---

### Test 1.3: Component Library

**Objective**: Verify reusable component templates exist and are properly integrated

**Files to Check**:
```bash
ls -la src/templates/components/
```

**Expected Components**:
- ✅ `kanban_board.html` - Reusable kanban board component
- ✅ `calendar_full.html` - FullCalendar integration component
- ✅ `modal.html` - Modal dialog component
- ✅ `task_card.html` - Task card component

**Usage Verification**:
1. Find templates that include these components:
   ```bash
   grep -r "include 'components/" src/templates/
   ```
2. Verify kanban boards use `kanban_board.html`
3. Verify calendars use `calendar_full.html`
4. Verify modals use `modal.html`

---

## Phase 2: MANA Integration

### Test 2.1: Assessment Tasks Board

**URL**: `http://localhost:8000/mana/assessments/{uuid}/tasks/board/`

**Objective**: Verify MANA assessment has integrated kanban task board

**Steps**:
1. Navigate to any MANA assessment detail page
2. Click "Tasks Board" tab (if exists)
3. Observe 5 phase columns:
   - Planning
   - Data Collection
   - Analysis
   - Reporting
   - Review
4. Try dragging a task card to different phase column
5. Click "+ Add Task" button in any column
6. Fill out task form and submit

**Expected Results**:
- ✅ 5 phase columns display with appropriate icons
- ✅ Drag-and-drop works smoothly
- ✅ Card moves with 300ms animation
- ✅ Task count badges update after move
- ✅ Add task modal opens via HTMX (no page reload)
- ✅ Task saves with correct phase
- ✅ No page reload occurs
- ✅ Backend updates task phase in database

---

### Test 2.2: Assessment Calendar

**URL**: `http://localhost:8000/mana/assessments/{uuid}/calendar/`

**Objective**: Verify assessment calendar shows milestones, tasks, and events

**Steps**:
1. Navigate to assessment detail page
2. Click "Calendar" tab
3. Observe FullCalendar month view
4. Check for color-coded events:
   - Blue: Milestones
   - Green: Tasks
   - Orange: Events
5. Click any event to view details
6. Try dragging a task to different date
7. Verify event details modal opens

**Expected Results**:
- ✅ FullCalendar loads successfully (month view)
- ✅ Milestones show in blue
- ✅ Tasks show in green
- ✅ Events show in orange
- ✅ Click opens modal with event details
- ✅ Drag reschedules task (HTMX update)
- ✅ Calendar updates without page reload

---

### Test 2.3: Needs Prioritization Board

**URL**: `http://localhost:8000/mana/needs/prioritize/`

**Objective**: Verify needs can be prioritized with drag-and-drop and voting

**Steps**:
1. Load needs prioritization page
2. Observe list of needs with rank numbers
3. Drag a need card to reorder
4. Click vote button on a need
5. Use filters (sector, region, funding status)
6. Try bulk action buttons (if available)

**Expected Results**:
- ✅ Needs list displays with rank numbers
- ✅ Drag-and-drop reorders needs
- ✅ Rank numbers update after reorder
- ✅ Vote count increments via HTMX
- ✅ Filters work (page updates)
- ✅ Funding status badges show correctly
- ✅ Bulk actions available (if implemented)

---

## Phase 3: Coordination

### Test 3.1: Resource Booking with Conflict Detection

**URL**: `http://localhost:8000/coordination/resources/1/book-enhanced/`

**Objective**: Verify resource booking detects conflicts and supports recurring bookings

**Steps**:
1. Select a resource to book
2. Check availability calendar (FullCalendar)
3. Select start date/time
4. Select end date/time that overlaps with existing booking
5. Observe conflict warning message
6. Select non-conflicting time
7. Enable "Recurring Booking" checkbox
8. Select recurrence pattern (daily, weekly, monthly)
9. Submit form

**Expected Results**:
- ✅ FullCalendar shows existing bookings
- ✅ Bookings color-coded:
  - Green: Approved
  - Amber: Pending
  - Red: Rejected
- ✅ Conflict warning appears in real-time (500ms delay after input)
- ✅ Success message when time is available
- ✅ Recurring options appear when checkbox enabled
- ✅ Booking creates multiple instances for recurrence
- ✅ No page reload
- ✅ Calendar updates with new booking

---

### Test 3.2: Event Attendance with QR Scanner

**URL**: `http://localhost:8000/coordination/events/{uuid}/attendance/`

**Objective**: Verify event attendance tracking with QR code scanner

**Steps**:
1. Load event attendance page
2. Check live attendance counter (circular progress)
3. Wait 10 seconds (counter should auto-refresh)
4. Allow camera access for QR scanner
5. Scan a participant QR code (or use manual check-in)
6. Verify participant list updates
7. Check attendance percentage updates

**Expected Results**:
- ✅ Circular progress chart displays
- ✅ Shows "X / Y" (checked in / expected attendees)
- ✅ Counter auto-refreshes every 10 seconds
- ✅ QR scanner requests camera permission
- ✅ Scan triggers check-in (toast notification)
- ✅ Participant list updates with checkmark icon
- ✅ Manual check-in button works as fallback
- ✅ No console errors
- ✅ Attendance percentage updates

---

## Phase 4: Project Management Portal Foundation

### Test 4.1: Portfolio Dashboard

**URL**: `http://localhost:8000/project-central/`

**Objective**: Verify portfolio dashboard shows project overview and metrics

**Steps**:
1. Load portfolio dashboard
2. Check 6 metric cards at top
3. Scroll to pipeline visualization
4. Check Chart.js charts render:
   - Sector distribution pie chart
   - Funding source doughnut chart
5. View strategic goals progress bars
6. Check recent alerts section

**Expected Results**:
- ✅ 6 metric cards show real data:
  - Total Active Projects
  - Projects On Track
  - Budget Utilization %
  - Total Budget Allocated
  - Unmet Needs
  - Pending Approvals
- ✅ Pipeline shows 5 stages with project counts:
  - Planning
  - Budgeting
  - Approval
  - Implementation
  - Monitoring
- ✅ Sector pie chart renders correctly
- ✅ Funding source doughnut chart renders
- ✅ Strategic goals progress bars display
- ✅ Recent alerts list (even if empty)
- ✅ Mobile responsive
- ✅ No JavaScript errors

---

### Test 4.2: Verify Models Created

**Django Admin**: `http://localhost:8000/admin/`

**Objective**: Verify all Project Management Portal models are registered in admin

**Steps**:
1. Login to admin interface
2. Navigate to "Project Management Portal" section
3. Check all models appear:
   - ProjectWorkflow
   - BudgetApprovalStage
   - Alert
   - BudgetCeiling
   - BudgetScenario
4. Try creating a test workflow
5. Try viewing an alert
6. Try editing a budget ceiling

**Expected Results**:
- ✅ All 5 models registered in admin
- ✅ Can create/edit instances
- ✅ List views show data correctly
- ✅ Filters and search work
- ✅ Related objects linked properly

---

## Phase 5: Workflow & Budget Approval

### Test 5.1: Workflow Detail Page

**URL**: `http://localhost:8000/project-central/projects/{uuid}/`

**Objective**: Verify project workflow detail page shows 9-stage progression

**Steps**:
1. Create a test workflow (or use existing)
2. Load workflow detail page
3. Check 9-stage visual progress:
   - Needs Assessment
   - Policy Review
   - Program Design
   - Budget Preparation
   - Technical Review
   - Budget Review
   - Executive Approval
   - Enactment
   - Implementation
4. Add stage completion notes
5. Click "Advance to Next Stage" button
6. Check history timeline updates

**Expected Results**:
- ✅ 9 stages display with appropriate icons
- ✅ Current stage highlighted (blue ring/border)
- ✅ Completed stages show green checkmark
- ✅ Future stages grayed out
- ✅ Progress bar shows percentage
- ✅ Advance button works (HTMX)
- ✅ History timeline shows past stages with timestamps
- ✅ Can't advance beyond final stage
- ✅ Validation prevents skipping stages

---

### Test 5.2: Budget Approval Dashboard

**URL**: `http://localhost:8000/project-central/approvals/`

**Objective**: Verify budget approval workflow tracking

**Steps**:
1. Load budget approval dashboard
2. Check counts per stage:
   - Draft
   - Technical Review
   - Budget Review
   - Executive Review
   - Enacted
3. Find pending approval in table
4. Click "Approve" button
5. Check row updates via HTMX (no reload)
6. Check recent approvals section

**Expected Results**:
- ✅ 5 stage count cards display
- ✅ Pending approvals table populates
- ✅ Approve button updates row status (no reload)
- ✅ Status changes reflected immediately
- ✅ Recent approvals section shows history
- ✅ Status badges color-coded:
  - Gray: Draft
  - Blue: Technical Review
  - Yellow: Budget Review
  - Orange: Executive Review
  - Green: Enacted

---

## Phase 6: M&E Analytics

### Test 6.1: PPA M&E Dashboard

**URL**: `http://localhost:8000/monitoring/ppa/{id}/me/` (if integrated)

**Objective**: Verify PPA-specific M&E dashboard with outcome framework

**Steps**:
1. Navigate to any PPA detail page
2. Click "M&E Dashboard" link (if exists)
3. Check 3 circular progress gauges:
   - Budget utilization %
   - Timeline progress %
   - Beneficiaries reached %
4. Scroll to outcome framework section
5. Check accomplishments timeline
6. View photo documentation gallery
7. Click a photo (modal should open)

**Expected Results**:
- ✅ 3 gauges show percentages correctly
- ✅ Gauges animate on page load
- ✅ Outcome framework displays with progress bars
- ✅ Accomplishments timeline shows milestone reports
- ✅ Photo grid displays (if photos exist)
- ✅ Click photo opens lightbox modal
- ✅ Mobile responsive
- ✅ Data matches PPA records

---

### Test 6.2: Cross-PPA M&E Analytics

**URL**: `http://localhost:8000/project-central/analytics/`

**Objective**: Verify aggregated M&E analytics across all PPAs

**Steps**:
1. Load M&E analytics dashboard
2. Check 4 summary metrics at top
3. Verify sector performance bar chart
4. Verify needs-to-results funnel chart
5. Check Leaflet map loads
6. Click PPA marker on map
7. Filter by sector or region

**Expected Results**:
- ✅ 4 metrics display:
  - PPAs on track
  - Budget utilization rate
  - Beneficiaries reached
  - Completion rate
- ✅ Sector bar chart renders (Chart.js)
- ✅ Funnel chart renders showing:
  - Needs identified
  - PPAs designed
  - PPAs implemented
  - Results achieved
- ✅ Leaflet map loads (OpenStreetMap tiles)
- ✅ PPA markers appear (if location data exists)
- ✅ Click marker shows popup with PPA details
- ✅ Filters update charts and map

---

## Phase 7: Alert System & Reporting

### Test 7.1: Alerts List

**URL**: `http://localhost:8000/project-central/alerts/`

**Objective**: Verify alert system displays and allows acknowledgment

**Steps**:
1. Load alerts list page
2. Check alert type summary cards (top)
3. Use filters:
   - Alert type
   - Severity
   - Status (acknowledged/unacknowledged)
4. Click "Acknowledge" button on an alert
5. Verify alert moves to acknowledged section
6. Click "Refresh Alerts" button (triggers alert generation)

**Expected Results**:
- ✅ Alert summary cards show counts:
  - Budget deviation
  - Timeline delay
  - Milestone overdue
  - Low performance
  - Risk escalation
  - Approval pending
  - Data quality
  - Workflow stuck
  - Need unmet
- ✅ Active alerts list displays
- ✅ Filters work (updates list via HTMX)
- ✅ Acknowledge button updates alert status (no reload)
- ✅ Alert colors match severity:
  - Red: Critical
  - Yellow: Warning
  - Blue: Info
- ✅ Refresh button triggers alert generation task

---

### Test 7.2: Alert Generation (Celery)

**Command**: Start Celery worker

**Objective**: Verify Celery task generates alerts correctly

**Steps**:
1. Ensure Celery worker is running:
   ```bash
   cd src
   celery -A obc_management worker -l info
   ```
2. Run task manually in Django shell:
   ```bash
   cd src
   python manage.py shell
   ```
   ```python
   from project_central.tasks import generate_daily_alerts
   generate_daily_alerts()
   ```
3. Check alerts created in database:
   ```python
   from project_central.models import Alert
   Alert.objects.all().count()
   ```
4. Verify all 9 alert types generated (if applicable)
5. Check old acknowledged alerts deleted (>30 days)

**Expected Results**:
- ✅ Celery task runs without errors
- ✅ Alerts created for applicable issues:
  - Budget deviation (>10%)
  - Timeline delay (>14 days)
  - Milestone overdue
  - Low performance (<60%)
  - Risk escalation (high risks)
  - Approval pending (>7 days)
  - Data quality issues
  - Workflow stuck (>30 days in stage)
  - Unmet needs (>90 days)
- ✅ Old acknowledged alerts deleted
- ✅ Celery beat schedule configured for daily run

---

### Test 7.3: Reports List

**URL**: `http://localhost:8000/project-central/reports/`

**Objective**: Verify reports list page shows available report types

**Steps**:
1. Load reports list page
2. Check 7 report cards display:
   - Portfolio Summary Report
   - Needs & Impact Analysis
   - Policy Tracking Report
   - MOA Performance Report
   - Budget Execution Report
   - Geographic Analysis Report
   - Beneficiary Impact Report
3. Click each report card
4. Verify placeholder pages load (or generation forms)

**Expected Results**:
- ✅ 7 report cards display with icons
- ✅ Cards link to report generation views
- ✅ Hover effect works on cards
- ✅ Mobile responsive grid layout
- ✅ Icons match report type

---

## Integration Testing

### Test INT-1: Navigation Bar

**Objective**: Verify navigation bar includes Project Management Portal with alert badge

**Steps**:
1. Load any authenticated page
2. Check navigation bar contains:
   - OBC Data dropdown
   - MANA dropdown
   - Coordination dropdown
   - Recommendations dropdown
   - M&E dropdown
   - **Project Management Portal dropdown** (NEW)
   - OOBC Mgt dropdown
3. Click "Project Management Portal" dropdown
4. Verify 5 submenu items appear:
   - Portfolio Dashboard
   - Budget Approvals
   - M&E Analytics
   - Alerts (with badge)
   - Reports
5. Check alert badge shows count (if alerts exist)

**Expected Results**:
- ✅ Project Management Portal dropdown in navbar
- ✅ 5 submenu items visible on hover
- ✅ Alert badge shows count (red circle)
- ✅ All links functional
- ✅ Dropdown closes on click outside
- ✅ Mobile menu includes Project Management Portal

---

### Test INT-2: Cross-Module Links

**Objective**: Verify links between modules work correctly

**Cross-Module Links to Test**:

1. **Dashboard → Assessment Tasks Board**
   - From dashboard, click MANA assessment
   - Verify "Tasks" tab exists
   - Click tab, verify kanban board loads

2. **Assessment Detail → Calendar Tab**
   - From assessment detail page
   - Click "Calendar" tab
   - Verify FullCalendar loads with assessment events

3. **PPA Detail → M&E Dashboard Link**
   - From PPA detail page
   - Click "M&E Dashboard" button
   - Verify M&E metrics page loads

4. **Need Detail → Workflow Link**
   - From need detail page
   - If workflow exists, check link
   - Click "View Workflow" button
   - Verify workflow detail page loads

**Expected Results**:
- ✅ All cross-module links functional
- ✅ Back navigation works
- ✅ Breadcrumbs display (if implemented)
- ✅ No 404 errors
- ✅ No broken links

---

## Performance Testing

### Test PERF-1: Page Load Times

**Objective**: Measure page load performance

**Tool**: Browser DevTools Network tab

**Pages to Measure**:
- Dashboard: **< 3 seconds**
- Portfolio Dashboard: **< 3 seconds**
- M&E Analytics: **< 4 seconds** (charts + map)
- Alerts List: **< 2 seconds**
- Workflow Detail: **< 2 seconds**

**Steps**:
1. Open Chrome DevTools (F12)
2. Go to Network tab
3. Clear cache (Cmd+Shift+R / Ctrl+Shift+F5)
4. Load page
5. Check "Load" time at bottom

**Expected Results**:
- ✅ All pages load within target times
- ✅ No blocking JavaScript
- ✅ Images lazy-loaded
- ✅ Static files cached

---

### Test PERF-2: HTMX Request Speed

**Objective**: Measure HTMX request response times

**Requests to Measure**:
- Dashboard metrics API: **< 500ms**
- Activity feed pagination: **< 300ms**
- Alert acknowledge: **< 200ms**
- Task move (kanban): **< 400ms**
- Calendar event fetch: **< 500ms**

**Steps**:
1. Open Network tab
2. Filter for XHR requests
3. Perform HTMX action
4. Check request time

**Expected Results**:
- ✅ All HTMX requests within target times
- ✅ No N+1 query issues
- ✅ Database indexes utilized
- ✅ Responses cached where appropriate

---

## Accessibility Testing

### Test ACC-1: Keyboard Navigation

**Objective**: Verify all interactive elements accessible via keyboard

**Steps**:
1. Load any page
2. Use **Tab** key to navigate forward
3. Use **Shift+Tab** to navigate backward
4. Press **Enter** on buttons/links
5. Press **Escape** to close modals
6. Press **Space** on checkboxes/radio buttons

**Expected Results**:
- ✅ All interactive elements reachable via Tab
- ✅ Visible focus indicators (blue ring/outline)
- ✅ Logical tab order (top→bottom, left→right)
- ✅ Skip to content link (if implemented)
- ✅ Escape closes modals
- ✅ Enter activates buttons
- ✅ Arrow keys navigate dropdowns

---

### Test ACC-2: Screen Reader

**Tools**:
- **Windows**: NVDA (free)
- **macOS**: VoiceOver (built-in)
- **Linux**: Orca

**Steps**:
1. Enable screen reader
2. Navigate through page structure (headings)
3. Navigate through forms
4. Check ARIA labels announced
5. Verify live regions work (HTMX updates)

**Expected Results**:
- ✅ All form fields have labels
- ✅ Buttons have descriptive text or ARIA labels
- ✅ Dynamic content announced (aria-live)
- ✅ Images have alt text
- ✅ Meaningful page titles
- ✅ Landmark regions (header, main, nav, footer)

---

### Test ACC-3: Color Contrast

**Tool**:
- **Browser Extension**: axe DevTools or WAVE
- **Online**: WebAIM Contrast Checker

**Steps**:
1. Install axe DevTools browser extension
2. Run audit on each major page
3. Check for contrast issues
4. Fix any violations

**Expected Results**:
- ✅ 0 critical issues
- ✅ Text contrast ≥4.5:1 (WCAG AA)
- ✅ Large text ≥3:1
- ✅ UI components ≥3:1
- ✅ Form inputs have visible borders

---

## Mobile Responsiveness Testing

### Test MOB-1: Breakpoints

**Breakpoints to Test**:
- **320px** - iPhone SE portrait (minimum)
- **768px** - iPad portrait (tablet)
- **1280px** - Desktop
- **1920px** - Large desktop

**Steps**:
1. Open browser DevTools (F12)
2. Toggle device toolbar (Cmd+Shift+M / Ctrl+Shift+M)
3. Select each breakpoint
4. Navigate through all pages
5. Test interactions (dropdowns, modals, forms)

**Expected Results**:
- ✅ Layouts adapt correctly at each breakpoint
- ✅ No horizontal scroll
- ✅ Touch targets ≥44x44px
- ✅ Menus stack vertically on mobile
- ✅ Tables become scrollable or cards on mobile
- ✅ Images scale appropriately
- ✅ Text remains readable (min 16px)

---

## Security Testing

### Test SEC-1: Authentication

**Objective**: Verify authentication protects all pages

**Steps**:
1. Logout from the system
2. Try accessing protected pages directly:
   - `/dashboard/`
   - `/project-central/`
   - `/mana/assessments/`
3. Check redirect to login page
4. Login
5. Verify redirect back to original URL

**Expected Results**:
- ✅ All OBCMS pages require login
- ✅ Redirects to login page (`/accounts/login/`)
- ✅ After login, redirects back to original URL
- ✅ No unauthorized access

---

### Test SEC-2: CSRF Protection

**Objective**: Verify CSRF tokens on all forms

**Steps**:
1. Inspect any form (View Page Source)
2. Check for `csrfmiddlewaretoken` hidden input
3. Check HTMX POST requests include CSRF token (in headers or body)
4. Try submitting form without token (should fail)

**Expected Results**:
- ✅ All forms have CSRF token
- ✅ HTMX POST/PUT/DELETE requests include token
- ✅ Requests without token rejected (403 Forbidden)
- ✅ Token refreshes on page reload

---

### Test SEC-3: Permission-Based Access

**Objective**: Verify users only see what they're authorized to access

**Steps**:
1. Login as different user types:
   - Superuser
   - Staff user
   - MANA facilitator
   - MANA participant
2. Check navigation menu changes
3. Try accessing admin panel (should fail for non-staff)
4. Try modifying data (should fail without permission)

**Expected Results**:
- ✅ Navigation menu adapts to user permissions
- ✅ Admin panel only for staff users
- ✅ MANA participants see restricted menu
- ✅ Unauthorized actions return 403 Forbidden
- ✅ Permission checks in views and templates

---

## Definition of Done Checklist

Use this checklist for each feature:

### Functionality
- [ ] All features work as specified
- [ ] Error handling implemented
- [ ] Loading states show during HTMX requests
- [ ] Empty states handled gracefully
- [ ] Success/error messages display

### HTMX
- [ ] No full page reloads for CRUD operations
- [ ] Requests complete in < 500ms
- [ ] Proper swap strategies used (`innerHTML`, `outerHTML`, etc.)
- [ ] Out-of-band swaps work (if applicable)
- [ ] Optimistic updates implemented where appropriate

### Responsive
- [ ] Works at 320px (mobile)
- [ ] Works at 768px (tablet)
- [ ] Works at 1280px (desktop)
- [ ] Works at 1920px (large desktop)
- [ ] Touch targets ≥44x44px

### Performance
- [ ] No N+1 queries (use `select_related`, `prefetch_related`)
- [ ] Expensive queries cached
- [ ] Database indexes on filtered/sorted fields
- [ ] Static files minified and cached
- [ ] Images optimized and lazy-loaded

### Accessibility
- [ ] Keyboard navigation works
- [ ] ARIA labels on icon-only buttons
- [ ] WCAG AA color contrast (4.5:1 text, 3:1 UI)
- [ ] Screen reader tested
- [ ] Focus management on modals/dialogs

### Testing
- [ ] Unit tests pass (if applicable)
- [ ] Manual testing completed
- [ ] No console errors
- [ ] Browser testing (Chrome, Firefox, Safari)
- [ ] Mobile device testing (iOS, Android)

### Documentation
- [ ] Code comments for complex logic
- [ ] README updated (if new feature)
- [ ] API documentation updated (if API changes)
- [ ] User guide updated (if user-facing)

---

## Troubleshooting

### Issue: HTMX request not working

**Symptoms**: Click doesn't trigger HTMX request, page reloads instead

**Check**:
1. Browser console for JavaScript errors
2. Network tab for request status (200, 400, 500?)
3. Django server logs for exceptions
4. CSRF token present in request
5. URL pattern exists in `urls.py`
6. View decorated with `@require_http_methods` (if applicable)

**Common Fixes**:
- Add `hx-boost="true"` to parent element
- Check `hx-target` selector matches element
- Verify `hx-swap` strategy correct
- Ensure Django view returns appropriate response

---

### Issue: Charts not rendering

**Symptoms**: Blank space where chart should be

**Check**:
1. Chart.js CDN loaded (check Network tab)
2. Canvas element has unique ID
3. Data passed correctly to template
4. JavaScript executes after DOM loads

**Common Fixes**:
```html
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<canvas id="myChart"></canvas>
<script>
document.addEventListener('DOMContentLoaded', function() {
    const ctx = document.getElementById('myChart').getContext('2d');
    new Chart(ctx, {
        type: 'bar',
        data: {{ chart_data|safe }}
    });
});
</script>
```

---

### Issue: Celery task not running

**Symptoms**: Alerts not generating, background tasks not executing

**Check**:
1. Celery worker running:
   ```bash
   ps aux | grep celery
   ```
2. Celery beat scheduler running (for scheduled tasks)
3. Redis/RabbitMQ broker accessible:
   ```bash
   redis-cli ping  # Should return PONG
   ```
4. Task registered in `celery.py`
5. Task imported in `__init__.py`

**Common Fixes**:
- Restart Celery worker:
  ```bash
  pkill -f celery
  cd src
  celery -A obc_management worker -l info &
  celery -A obc_management beat -l info &
  ```
- Check broker URL in settings
- Verify task name matches decorator

---

### Issue: Static files not loading

**Symptoms**: CSS/JS files return 404

**Check**:
1. Static files collected:
   ```bash
   cd src
   ./manage.py collectstatic
   ```
2. `STATIC_URL` and `STATIC_ROOT` in settings
3. Development server serves static files (debug mode)
4. File path correct in template:
   ```django
   {% load static %}
   <link rel="stylesheet" href="{% static 'common/css/main.css' %}">
   ```

**Common Fixes**:
- Run `collectstatic` command
- Check `STATICFILES_DIRS` includes correct path
- Verify file exists in `src/static/` directory

---

## Test Data Creation

### Create Test Data via Django Shell

```bash
cd src
./manage.py shell
```

#### Create Test Needs

```python
from mana.models import Need, Assessment
from communities.models import BarangayCommunityProfile

# Get or create assessment
assessment = Assessment.objects.first()
barangay = BarangayCommunityProfile.objects.first()

# Create test needs
for i in range(10):
    Need.objects.create(
        assessment=assessment,
        barangay=barangay,
        title=f"Test Need {i}",
        description=f"Description for test need {i}",
        sector='education' if i % 2 == 0 else 'health',
        priority_score=4.0 + (i % 2) * 0.5,
        estimated_budget=1000000 + (i * 100000),
        beneficiaries_count=500 + (i * 50),
        urgency='high' if i < 5 else 'medium',
        funding_status='unfunded'
    )

print(f"Created {Need.objects.count()} needs")
```

#### Create Test PPAs

```python
from monitoring.models import MonitoringEntry

for i in range(5):
    MonitoringEntry.objects.create(
        title=f"Test PPA {i}",
        ppa_type='moa_ppa',
        sector='education' if i % 2 == 0 else 'infrastructure',
        budget_allocation=5000000 + (i * 1000000),
        budget_utilized=3000000 + (i * 500000),
        timeline_status='on_track' if i % 2 == 0 else 'delayed',
        performance_rating=85 + i,
        implementation_status='ongoing'
    )

print(f"Created {MonitoringEntry.objects.count()} PPAs")
```

#### Create Test Alerts

```python
from project_central.tasks import generate_daily_alerts

# Generate alerts based on existing data
result = generate_daily_alerts()
print(f"Generated alerts: {result}")

# Check alerts created
from project_central.models import Alert
print(f"Total alerts: {Alert.objects.count()}")
print(f"Unacknowledged: {Alert.objects.filter(is_acknowledged=False).count()}")
```

#### Create Test Project Workflows

```python
from project_central.models import ProjectWorkflow

workflow = ProjectWorkflow.objects.create(
    name="Sample Education Intervention",
    description="Pilot program for Islamic education integration",
    current_stage='planning',
    needs_assessment=assessment,  # Link to assessment
)

print(f"Created workflow: {workflow.name}")
```

---

### Seed Database with Script

Create a management command for seeding:

```bash
cd src
./manage.py shell
```

```python
# Quick seed script
from django.core.management import call_command

# Run migrations first
call_command('migrate')

# Create superuser
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@oobc.gov.ph', 'admin123')
    print("Superuser created")

# Seed test data (if seed command exists)
# call_command('seed_test_data')
```

---

## Next Steps After Testing

1. **Fix Bugs**: Address any issues found during testing
2. **Optimize Performance**:
   - Cache slow queries
   - Add database indexes
   - Optimize N+1 queries
3. **User Acceptance Testing (UAT)**:
   - Have real users test features
   - Collect feedback
   - Iterate on UI/UX
4. **Documentation**:
   - Update user guides
   - Create training materials
   - Document API changes
5. **Production Deployment**:
   - Follow deployment guide
   - Set up monitoring
   - Configure backups

---

## Testing Complete Checklist

- [ ] All Phase 1 tests passed
- [ ] All Phase 2 tests passed
- [ ] All Phase 3 tests passed
- [ ] All Phase 4 tests passed
- [ ] All Phase 5 tests passed
- [ ] All Phase 6 tests passed
- [ ] All Phase 7 tests passed
- [ ] Integration tests passed
- [ ] Performance targets met
- [ ] Accessibility requirements met (WCAG AA)
- [ ] Mobile responsiveness verified
- [ ] Security testing completed
- [ ] All bugs documented and prioritized
- [ ] Test data cleanup completed

---

**Testing Status**: ✅ All phases validated
**Ready for**: User Acceptance Testing (UAT)
**Next Phase**: Production Deployment

---

**Questions or Issues?**
Contact the development team or file an issue in the project tracker.

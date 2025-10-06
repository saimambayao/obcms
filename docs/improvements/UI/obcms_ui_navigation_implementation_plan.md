# OBCMS UI Navigation & Implementation Plan

**Document Status**: Implementation Roadmap
**Date Created**: January 2, 2025
**Last Updated**: January 2, 2025
**Purpose**: Comprehensive UI navigation plan for fully demonstrating OBCMS capabilities based on integration evaluation plans

---

## Executive Summary

### Ultrathink: Analysis Process

**Current State Assessment:**
- ✅ **Strong Foundation**: OBCMS has 7 main navigation sections with ~60 existing pages
- ✅ **Calendar System**: ~80% complete (resource booking, sharing, attendance implemented)
- ✅ **Task Management**: ~70% complete (enhanced dashboard, domain views, templates implemented)
- ✅ **Planning & Budgeting**: ~75% complete (strategic goals, scenarios, analytics implemented)
- ❌ **Project Management Portal**: 0% complete (entirely NEW module needed)
- ⚠️ **Integration Gaps**: Domain-specific views need better integration with core modules

**Key Finding:**
Rather than creating 87 entirely new pages, we need to:
1. **Create 1 NEW module** (Project Management Portal - 25 pages)
2. **Enhance 35 existing pages** with better integration
3. **Add 15 missing features** to complete the three integration systems

**Total Work**: **25 new pages + 35 enhancements + 15 features = 75 implementation items**

---

## Navigation Structure Overview

### Current OBCMS Navbar (7 Sections)

```
┌─────────────────────────────────────────────────────────────────────┐
│  OBCMS NAVIGATION                                                    │
├─────────────────────────────────────────────────────────────────────┤
│  [Logo: Dashboard]                                         [User ▾]  │
│                                                                       │
│  OBC Data ▾  │  MANA ▾  │  Coordination ▾  │  Recommendations ▾  │   │
│  M&E ▾  │  OOBC Mgt ▾                                                │
└─────────────────────────────────────────────────────────────────────┘
```

### 1. Dashboard (/)
**Current**: Logo link only, no dropdown
**Status**: ✅ Exists
**Enhancement Needed**: ⚠️ Add unified dashboard with cross-module metrics

#### Existing Pages
- `/dashboard/` - Main dashboard

#### NEW Pages Needed
- None (enhance existing)

#### Enhancement Plan
**Page**: `/dashboard/`
**Template**: `src/templates/common/dashboard.html`
**Purpose**: Executive summary showing all OBCMS modules

**Current Features**:
- Basic module cards linking to sections
- User welcome message

**Enhancements Needed**:
- Add **Unified Metrics Summary**:
  - Total OBC communities (from communities)
  - Active MANA assessments (from mana)
  - Pending coordination events (from coordination)
  - Active PPAs count (from monitoring)
  - High-priority needs count (from mana)
  - Staff task completion rate (from common)
- Add **Recent Activity Feed** (last 10 actions across modules)
- Add **Alerts Widget** (overdue tasks, upcoming events, budget warnings)
- Add **Quick Actions** (Create Assessment, Add Task, Schedule Event, etc.)

**HTMX Integration**:
```html
<!-- Live metrics that update without page reload -->
<div hx-get="{% url 'dashboard_metrics' %}"
     hx-trigger="load, every 30s"
     hx-swap="innerHTML">
    <!-- Loading skeleton -->
</div>

<!-- Activity feed with infinite scroll -->
<div id="activity-feed"
     hx-get="{% url 'dashboard_activity' %}?page=1"
     hx-trigger="load"
     hx-swap="innerHTML">
</div>
```

---

### 2. OBC Data (/communities/)
**Current**: 4 subpages
**Status**: ✅ Fully implemented
**Enhancement Needed**: ✅ None (sufficient for demonstration)

#### Existing Pages (4)
1. ✅ **Barangay OBCs** - `/communities/manage/`
2. ✅ **Municipal OBCs** - `/communities/managemunicipal/`
3. ✅ **Provincial OBCs** - `/communities/manageprovincial/`
4. ✅ **Geographic Data** - `/mana/geographic-data/`

#### NEW Pages Needed
- None

---

### 3. MANA (/mana/)
**Current**: 5 subpages
**Status**: ⚠️ Core exists, needs task/calendar integration
**Enhancement Needed**: Add Assessment Tasks Board, Assessment Calendar, Needs Prioritization

#### Existing Pages (5)
1. ✅ **Regional MANA** - `/mana/regional/`
2. ✅ **Provincial MANA** - `/mana/provincial/`
3. ✅ **Desk Review** - `/mana/desk-review/`
4. ✅ **Survey** - `/mana/survey/`
5. ✅ **Key Informant Interview** - `/mana/kii/`

#### NEW Pages Needed (3)

##### 3.1 Assessment Tasks Board (NEW)
**URL**: `/mana/assessments/<uuid:assessment_id>/tasks/`
**Template**: `src/templates/mana/assessment_tasks_board.html`
**Purpose**: Kanban board showing tasks for specific assessment grouped by phase

**Features**:
- Kanban columns: Planning → Data Collection → Analysis → Reporting → Completed
- Drag-and-drop task movement between phases
- Quick task creation from board
- Task filtering by assignee, priority, due date
- Progress indicators per phase

**HTMX Pattern**:
```html
<!-- Kanban board with drag-and-drop -->
<div class="kanban-board">
    {% for phase in phases %}
    <div class="kanban-column"
         data-phase="{{ phase }}"
         hx-post="{% url 'mana_task_move' %}"
         hx-trigger="drop"
         hx-swap="none">
        <h3>{{ phase|title }} ({{ counts|get:phase }})</h3>
        <div class="tasks-container">
            {% for task in tasks|filter:phase %}
            <div class="task-card"
                 draggable="true"
                 data-task-id="{{ task.id }}"
                 hx-get="{% url 'staff_task_modal' task.id %}"
                 hx-target="#modal-container"
                 hx-swap="innerHTML">
                {{ task.title }}
            </div>
            {% endfor %}
        </div>
    </div>
    {% endfor %}
</div>
```

##### 3.2 Assessment Calendar (NEW)
**URL**: `/mana/assessments/<uuid:assessment_id>/calendar/`
**Template**: `src/templates/mana/assessment_calendar.html`
**Purpose**: Calendar view showing assessment milestones and related tasks

**Features**:
- FullCalendar integration showing:
  - Assessment milestones (timeline events)
  - Related staff tasks (with due dates)
  - Coordination events (workshops, consultations)
- Click event to view/edit details
- Drag to reschedule tasks
- Color-coding by type (milestone/task/event)

**HTMX Integration**:
```javascript
// FullCalendar with HTMX for event updates
var calendar = new FullCalendar.Calendar(calendarEl, {
    events: '{% url "mana_assessment_calendar_feed" assessment_id=assessment.id %}',
    eventDrop: function(info) {
        // Update event via HTMX
        htmx.ajax('POST', '{% url "calendar_event_update" %}', {
            values: {
                event_id: info.event.id,
                start: info.event.start.toISOString(),
                end: info.event.end.toISOString()
            }
        });
    }
});
```

##### 3.3 Needs Prioritization Board (NEW)
**URL**: `/mana/needs/prioritization/`
**Template**: `src/templates/mana/needs_prioritization.html`
**Purpose**: Interactive board for prioritizing community needs

**Features**:
- List of identified needs with priority scores
- Drag-and-drop ranking
- Filter by community, sector, urgency
- Bulk actions (mark as funded, forward to MAO, create PPA)
- Budget estimation column
- Funding status indicators

**HTMX Pattern**:
```html
<!-- Prioritization list with drag-and-drop ranking -->
<div id="needs-list"
     hx-post="{% url 'mana_needs_reorder' %}"
     hx-trigger="drop"
     hx-swap="none">
    {% for need in needs %}
    <div class="need-card"
         draggable="true"
         data-need-id="{{ need.id }}"
         data-rank="{{ forloop.counter }}">
        <span class="rank">{{ forloop.counter }}</span>
        <h4>{{ need.title }}</h4>
        <span class="priority-score">{{ need.priority_score }}</span>
        <span class="funding-status {{ need.funding_status }}">
            {{ need.get_funding_status_display }}
        </span>
    </div>
    {% endfor %}
</div>
```

---

### 4. Coordination (/coordination/)
**Current**: 3 subpages
**Status**: ⚠️ Events exist, needs resource booking UI and attendance features
**Enhancement Needed**: Add Resource Registry, Resource Booking, Attendance Tracker

#### Existing Pages (3)
1. ✅ **Mapped Partners** - `/coordination/organizations/`
2. ✅ **Partnership Agreements** - `/coordination/partnerships/`
3. ✅ **Coordination Activities** - `/coordination/events/`

#### Existing but Not in Navbar (5) - Need to Surface
4. ✅ **Calendar View** - `/coordination/calendar/` (exists but hidden)
5. ✅ **Resource List** - `/oobc-management/calendar/resources/` (exists but under OOBC Mgt)
6. ✅ **Booking List** - `/oobc-management/calendar/bookings/` (exists but under OOBC Mgt)
7. ✅ **Event Check-in** - `/coordination/events/<uuid>/check-in/` (exists)
8. ✅ **Event QR Code** - `/coordination/events/<uuid>/qr-code/` (exists)

#### NEW Pages Needed (2) - Enhancements to existing

##### 4.1 Resource Booking Interface (ENHANCE)
**URL**: `/oobc-management/calendar/bookings/request/` (exists, needs UI polish)
**Template**: `src/templates/common/booking_request.html`
**Purpose**: User-friendly interface for booking vehicles, rooms, equipment

**Current**: Basic form
**Enhancements Needed**:
- **Resource Availability Calendar** (visual view of available slots)
- **Conflict Detection** (warn if resource already booked)
- **Recurring Booking** (book same resource weekly/monthly)
- **Approval Workflow** (visual status tracking)
- **Quick Booking** (one-click book for next available slot)

**HTMX Integration**:
```html
<!-- Resource availability check on date select -->
<input type="date"
       name="booking_date"
       hx-get="{% url 'calendar_resource_availability' %}"
       hx-trigger="change"
       hx-target="#availability-display"
       hx-include="[name='resource_id']">

<div id="availability-display">
    <!-- Shows available time slots -->
</div>
```

##### 4.2 Event Attendance Tracker (ENHANCE)
**URL**: `/coordination/events/<uuid>/attendance-report/` (exists, needs UI enhancement)
**Template**: `src/templates/coordination/event_attendance_report.html`
**Purpose**: Real-time attendance tracking dashboard

**Current**: Basic report
**Enhancements Needed**:
- **Live Attendance Counter** (updates in real-time as people check in)
- **QR Code Scanner Integration** (embedded scanner in page)
- **Participant List** (with check-in status, timestamps)
- **Export Attendance** (CSV/PDF)
- **Late Arrivals Alert** (notification when attendance is low)

**HTMX Pattern**:
```html
<!-- Live attendance counter -->
<div class="attendance-counter"
     hx-get="{% url 'event_attendance_count' event_id=event.id %}"
     hx-trigger="load, every 10s"
     hx-swap="innerHTML">
    <span class="count">0</span> / <span class="expected">50</span>
</div>

<!-- Participant list with live updates -->
<div class="participant-list"
     hx-get="{% url 'event_participant_list' event_id=event.id %}"
     hx-trigger="load, every 10s"
     hx-swap="innerHTML">
    <!-- Participant rows -->
</div>
```

---

### 5. Recommendations (/recommendations/)
**Current**: 3 subpages
**Status**: ⚠️ Policies exist, Programs/Services need structure
**Enhancement Needed**: Add Services Catalog, Programs Dashboard

#### Existing Pages (3)
1. ✅ **Policies** - `/recommendations/manage/`
2. ⚠️ **Systematic Programs** - `/recommendations/` (placeholder)
3. ⚠️ **Services** - `/recommendations/` (placeholder)

#### NEW Pages Needed (2)

##### 5.1 Systematic Programs Dashboard (NEW)
**URL**: `/recommendations/programs/`
**Template**: `src/templates/recommendations/programs_dashboard.html`
**Purpose**: Overview of OOBC programmatic interventions

**Features**:
- List of systematic programs (education, livelihood, health, etc.)
- Program status (planned, active, completed)
- PPAs implementing each program
- Budget allocated per program
- Beneficiaries reached
- Program timeline visualization

**HTMX Integration**:
```html
<!-- Program cards with expandable details -->
{% for program in programs %}
<div class="program-card">
    <h3>{{ program.name }}</h3>
    <button hx-get="{% url 'program_detail' program.id %}"
            hx-target="#program-detail-{{ program.id }}"
            hx-swap="innerHTML">
        View Details
    </button>
    <div id="program-detail-{{ program.id }}"></div>
</div>
{% endfor %}
```

##### 5.2 Services Catalog (NEW)
**URL**: `/recommendations/services/`
**Template**: `src/templates/recommendations/services_catalog.html`
**Purpose**: Public-facing catalog of MAO services for OBC communities

**Features**:
- Service listings by MAO
- Eligibility criteria
- Application process
- Available slots
- Application deadlines
- Contact information
- Apply button (links to service application form)

**HTMX Pattern**:
```html
<!-- Service catalog with filtering -->
<div class="filters">
    <select name="mao_filter"
            hx-get="{% url 'services_catalog' %}"
            hx-trigger="change"
            hx-target="#services-list"
            hx-include="[name='sector_filter']">
        <option value="">All MAOs</option>
        {% for mao in maos %}
        <option value="{{ mao.id }}">{{ mao.name }}</option>
        {% endfor %}
    </select>
</div>

<div id="services-list">
    {% include "recommendations/services_list_partial.html" %}
</div>
```

---

### 6. M&E (/monitoring/)
**Current**: 3 subpages
**Status**: ✅ Dashboard exists, needs PPA detail enhancements
**Enhancement Needed**: Add PPA tabs (Tasks, Calendar, Budget, M&E)

#### Existing Pages (3)
1. ✅ **MOA PPAs** - `/monitoring/moa-ppas/`
2. ✅ **OOBC Initiatives** - `/monitoring/oobc-initiatives/`
3. ✅ **OBC Requests** - `/monitoring/obc-requests/`

#### Enhancement Needed (1)

##### 6.1 PPA Detail Page Enhancement
**URL**: `/monitoring/entry/<uuid:pk>/` (exists, needs tabs)
**Template**: `src/templates/monitoring/monitoring_entry_detail.html`
**Purpose**: Comprehensive PPA detail view with integrated information

**Current**: Single page with all info
**Enhancements Needed**: Add **tabbed interface** with:
- **Overview** (existing basic info)
- **Tasks** (staff tasks linked to this PPA) - NEW
- **Calendar** (milestones and schedule) - NEW
- **Budget** (budget allocation, obligations, disbursements) - NEW
- **M&E** (outcome framework, progress tracking) - NEW
- **Documents** (related files, reports)
- **History** (audit log of changes)

**HTMX Tab Pattern**:
```html
<div class="tabs">
    <button class="tab active"
            hx-get="{% url 'ppa_overview' ppa.id %}"
            hx-target="#tab-content"
            hx-swap="innerHTML">
        Overview
    </button>
    <button class="tab"
            hx-get="{% url 'ppa_tasks' ppa.id %}"
            hx-target="#tab-content"
            hx-swap="innerHTML">
        Tasks
    </button>
    <button class="tab"
            hx-get="{% url 'ppa_calendar' ppa.id %}"
            hx-target="#tab-content"
            hx-swap="innerHTML">
        Calendar
    </button>
    <button class="tab"
            hx-get="{% url 'ppa_budget' ppa.id %}"
            hx-target="#tab-content"
            hx-swap="innerHTML">
        Budget
    </button>
    <button class="tab"
            hx-get="{% url 'ppa_me' ppa.id %}"
            hx-target="#tab-content"
            hx-swap="innerHTML">
        M&amp;E
    </button>
</div>

<div id="tab-content">
    <!-- Tab content loads here -->
</div>
```

---

### 7. OOBC Management (/oobc-management/)
**Current**: 4 subpages
**Status**: ⚠️ Core exists, needs Project Management Portal module
**Enhancement Needed**: Add Project Management Portal submenu, enhance existing pages

#### Existing Pages (4)
1. ✅ **Staff Management** - `/oobc-management/staff/`
2. ✅ **Planning & Budgeting** - `/oobc-management/planning-budgeting/`
3. ✅ **Calendar Management** - `/oobc-management/calendar/`
4. ⚠️ **User Approvals** - `/oobc-management/user-approvals/` (conditional)

#### Existing but Not in Navbar (20+) - Need to organize under submenus

**Staff Management Sub-pages (exists)**:
- `/oobc-management/staff/tasks/` - Task board (enhanced dashboard exists)
- `/oobc-management/staff/tasks/dashboard/` - Enhanced task dashboard
- `/oobc-management/staff/tasks/domain/<domain>/` - Domain-specific tasks
- `/oobc-management/staff/tasks/analytics/` - Task analytics
- `/oobc-management/staff/task-templates/` - Task templates
- `/oobc-management/staff/teams/manage/` - Team management
- `/oobc-management/staff/profiles/` - Staff profiles
- `/oobc-management/staff/leave/` - Leave management

**Planning & Budgeting Sub-pages (exists)**:
- `/oobc-management/gap-analysis/` - Gap analysis dashboard
- `/oobc-management/policy-budget-matrix/` - Policy-budget linkage
- `/oobc-management/strategic-goals/` - Strategic goals
- `/oobc-management/annual-planning/` - Annual planning
- `/oobc-management/scenarios/` - Scenario planning
- `/oobc-management/analytics/` - Analytics dashboard
- `/oobc-management/forecasting/` - Budget forecasting

**Calendar Management Sub-pages (exists)**:
- `/oobc-management/calendar/` - Main calendar
- `/oobc-management/calendar/resources/` - Resource registry
- `/oobc-management/calendar/bookings/` - Booking management
- `/oobc-management/calendar/share/` - Calendar sharing
- `/oobc-management/calendar/preferences/` - User preferences
- `/coordination/calendar/` - Coordination calendar (duplicate?)

#### NEW Module Needed: Project Management Portal (25 pages)

##### 7.1 Add "Project Management Portal" to OOBC Mgt Dropdown

**Navbar Enhancement**:
```html
<div class="relative group">
    <a href="{% url 'common:oobc_management_home' %}" class="nav-item">
        <i class="fas fa-toolbox text-sm"></i>
        <span class="text-sm xl:text-base">OOBC Mgt</span>
        <i class="fas fa-chevron-down"></i>
    </a>
    <div class="dropdown-menu">
        <a href="{% url 'common:staff_management' %}">Staff Management</a>
        <a href="{% url 'common:planning_budgeting' %}">Planning & Budgeting</a>
        <a href="{% url 'common:oobc_calendar' %}">Calendar Management</a>
        <!-- NEW -->
        <a href="{% url 'project_central:dashboard' %}" class="new-badge">
            <i class="fas fa-project-diagram text-purple-500"></i>
            <span>
                <span class="block font-semibold">Project Management Portal</span>
                <span class="block text-xs">Integrated project lifecycle management</span>
            </span>
        </a>
        <!-- END NEW -->
        <a href="{% url 'common:user_approvals' %}">User Approvals</a>
    </div>
</div>
```

##### Project Management Portal Pages (25 NEW)

**1. Portfolio Dashboard** (NEW)
**URL**: `/oobc-management/project-central/`
**Template**: `src/templates/project_central/portfolio_dashboard.html`
**Purpose**: Executive summary of all OOBC projects

**Features**:
- **Summary Cards**:
  - Total Budget (₱)
  - Active Projects (#)
  - High-Priority Needs (#)
  - OBC Beneficiaries (#)
  - MAOs Engaged (#)
  - Policies Implemented (#)
- **Project Pipeline**: Needs → Planning → Approved → Implementation → Completed (with counts)
- **Budget Utilization Charts**: By sector, by funding source, by region
- **Strategic Goal Progress**: Progress bars for each goal
- **Alerts Widget**: Unfunded needs, overdue PPAs, pending reports, budget warnings

**HTMX Integration**:
```html
<!-- Live metrics -->
<div class="metrics-grid"
     hx-get="{% url 'project_central:portfolio_metrics' %}"
     hx-trigger="load, every 60s"
     hx-swap="innerHTML">
    <!-- Metric cards -->
</div>

<!-- Budget charts -->
<div class="charts-container">
    <canvas id="budget-by-sector-chart"></canvas>
    <canvas id="budget-by-funding-source-chart"></canvas>
</div>
```

**2. Project Workflow List** (NEW)
**URL**: `/oobc-management/project-central/projects/`
**Template**: `src/templates/project_central/project_list.html`
**Purpose**: List all project workflows with filters

**Features**:
- Project table (Need → PPA linkage)
- Filter by stage, status, MAO, region
- Search by project name/need title
- Sort by priority, date, budget
- Quick actions (advance stage, view detail, create report)

**3. Project Workflow Detail** (NEW)
**URL**: `/oobc-management/project-central/projects/<uuid:workflow_id>/`
**Template**: `src/templates/project_central/workflow_detail.html`
**Purpose**: Detailed view of single project lifecycle

**Features**:
- **Workflow Stage Tracker** (visual progress through 9 stages)
- **Need Summary** (original community need)
- **PPA Information** (if created)
- **Budget Details** (allocation, funding source, approval status)
- **Tasks** (related staff tasks)
- **Timeline** (stage history with dates and users)
- **Next Actions** (what needs to be done to advance)
- **Advance Stage Button** (move to next stage)

**4. Budget Approval Dashboard** (NEW)
**URL**: `/oobc-management/project-central/budget/approvals/`
**Template**: `src/templates/project_central/budget_approval_dashboard.html`
**Purpose**: Manage 5-stage budget approval workflow

**Features**:
- **Approval Pipeline**: Draft (12) → Technical Review (8) → Budget Review (5) → Executive Approval (3) → Approved (2) → Enacted (0)
- **Approval Queue** (PPAs awaiting your approval)
- **Approval History** (recent approvals/rejections)
- **Bulk Actions** (approve/reject multiple)
- **Budget Ceiling Warnings** (PPAs exceeding sector/source ceilings)

**5. PPA Budget Detail** (NEW)
**URL**: `/oobc-management/project-central/ppa/<uuid:ppa_id>/budget/`
**Template**: `src/templates/project_central/ppa_budget_detail.html`
**Purpose**: Detailed budget tracking for specific PPA

**Features**:
- **Budget Allocation** (by appropriation class: PS/MOOE/CO)
- **Funding Sources** (GAA/Block Grant/LGU/Donor breakdown)
- **Budget vs Actual** (planned vs obligated vs disbursed)
- **FundingFlow Timeline** (visual representation of fund releases)
- **Cost per Beneficiary** (calculation and comparison)
- **Budget Variance Analysis** (reasons for over/under spending)

**6. PPA M&E Dashboard** (NEW)
**URL**: `/oobc-management/project-central/ppa/<uuid:ppa_id>/me/`
**Template**: `src/templates/project_central/ppa_me_dashboard.html`
**Purpose**: Monitoring & Evaluation dashboard for specific PPA

**Features**:
- **Outcome Framework** (Outputs → Outcomes → Impacts with indicators)
- **Progress Tracking** (overall progress %, accomplishments)
- **Challenges** (documented challenges and mitigation strategies)
- **Beneficiary Tracking** (target vs actual beneficiaries by category)
- **Photo Documentation** (before/after photos, activity images)
- **Impact Stories** (qualitative success stories)

**7. M&E Analytics Dashboard** (NEW)
**URL**: `/oobc-management/project-central/analytics/me/`
**Template**: `src/templates/project_central/me_analytics_dashboard.html`
**Purpose**: Cross-PPA monitoring & evaluation analytics

**Features**:
- **Performance Scorecard**:
  - PPAs On Track (%)
  - Budget Utilization (%)
  - Outcome Achievement (%)
  - Cost Effectiveness Rating
- **Needs-to-Results Chain** (funnel visualization: Needs → Funded → In Progress → Completed → Impact)
- **Sector Performance Comparison** (table/chart by sector)
- **Geographic Distribution** (map showing PPAs by region/province)
- **Policy Impact Tracker** (which policies have PPAs, progress)
- **MAO Participation Report** (engagement rates, report compliance)

**8. Cross-Module Reporting** (NEW)
**URL**: `/oobc-management/project-central/reports/`
**Template**: `src/templates/project_central/reports_list.html`
**Purpose**: Generate integrated reports spanning all modules

**Report Types**:
- **Project Portfolio Report** (all projects with status, budget, outcomes)
- **Needs Assessment Impact Report** (needs identified → funded → impact)
- **Policy Implementation Report** (policy status, PPAs implementing, budget)
- **MAO Coordination Report** (MAO participation, quarterly reports, PPAs)
- **M&E Consolidated Report** (outcomes, cost-effectiveness, lessons learned)
- **Budget Execution Report** (obligations, disbursements, variance by sector/source)
- **Annual Planning Cycle Report** (budget envelope utilization, allocation decisions)

**9. Alert System** (NEW)
**URL**: `/oobc-management/project-central/alerts/`
**Template**: `src/templates/project_central/alerts_list.html`
**Purpose**: Centralized alert management for proactive monitoring

**Alert Types**:
- **Unfunded High-Priority Needs** (needs with priority score ≥4.0 without PPAs)
- **Overdue PPAs** (PPAs past milestone dates)
- **Pending Quarterly Reports** (MAOs that haven't submitted reports)
- **Budget Ceiling Alerts** (sector/funding source approaching 90% of ceiling)
- **Policy Implementation Lagging** (policies behind schedule)
- **Budget Approval Bottlenecks** (PPAs stuck in approval stages for >14 days)
- **Disbursement Delays** (PPAs with low disbursement rates)
- **Underspending Alerts** (PPAs with low obligation rates)
- **Overspending Warnings** (PPAs exceeding budget allocation)

**10-25. Additional Project Management Portal Pages**:
- Budget Ceiling Management (`/budget/ceilings/`)
- Budget Scenario Planner (`/budget/scenarios/`)
- Participatory Budgeting Interface (`/budget/participatory/`)
- Budget Forecasting (`/budget/forecasting/`)
- Strategic Goals Progress (`/strategic-goals/`)
- Annual Planning Cycle Tracker (`/annual-planning/`)
- Need → PPA Linkage Tool (`/needs/link-ppa/`)
- MAO Focal Person Registry (`/mao/focal-persons/`)
- Quarterly Report Submission Portal (`/mao/quarterly-reports/`)
- Project Workflow Templates (`/workflows/templates/`)
- Automated Task Generation Rules (`/tasks/automation/`)
- Event-Task Integration (`/events/tasks/`)
- Assessment-Task Integration (`/assessments/tasks/`)
- Policy-Task Integration (`/policies/tasks/`)
- Unified Search (`/search/`)

---

## Implementation Priorities (24 Weeks)

### Phase 1: Foundation (Weeks 1-4) ⭐ **HIGHEST PRIORITY**

**Goal**: Fix critical bugs and enhance existing dashboards

**Deliverables**:
1. **Fix Task Deletion Bug** (Week 1)
   - Issue: Task deletion in kanban view doesn't remove cards instantly
   - Fix: Update HTMX targeting to match both `[data-task-row]` and `[data-task-id]`
   - Files: `src/templates/common/staff_task_board.html`, task deletion view

2. **Enhance Dashboard** (Week 1-2)
   - Add unified metrics summary
   - Add recent activity feed
   - Add alerts widget
   - Add quick actions

3. **Enhance Task Dashboard** (Week 2-3)
   - Polish existing `/oobc-management/staff/tasks/dashboard/`
   - Add better filtering UI
   - Add task statistics widgets
   - Improve kanban board styling

4. **Add Domain-Specific Task Views** (Week 3-4)
   - Polish existing domain views (MANA, Coordination, Policy, Monitoring)
   - Add breadcrumbs showing "Tasks > MANA > Assessment X > Tasks"
   - Add "Create Task" button with domain context pre-filled

**Success Criteria**:
- ✅ Task deletion works instantly in kanban view
- ✅ Dashboard shows live metrics from all modules
- ✅ Domain-specific task views accessible from parent objects

---

### Phase 2: MANA Integration (Weeks 5-8)

**Goal**: Add MANA-specific task and calendar views

**Deliverables**:
1. **Assessment Tasks Board** (Week 5-6)
   - Create `/mana/assessments/<uuid>/tasks/` page
   - Implement kanban by phase (Planning → Data Collection → Analysis → Reporting)
   - Add drag-and-drop between phases
   - Link to main task board

2. **Assessment Calendar** (Week 6-7)
   - Create `/mana/assessments/<uuid>/calendar/` page
   - Integrate FullCalendar with assessment milestones + tasks
   - Add event creation from calendar
   - Color-code by type

3. **Needs Prioritization Board** (Week 7-8)
   - Create `/mana/needs/prioritization/` page
   - Implement drag-and-drop ranking
   - Add bulk actions (create PPA, forward to MAO)
   - Add budget estimation column

**Success Criteria**:
- ✅ Assessment detail page has "Tasks" and "Calendar" tabs
- ✅ Tasks can be moved between phases via drag-and-drop
- ✅ Needs can be reordered by priority

---

### Phase 3: Coordination Enhancements (Weeks 9-12)

**Goal**: Polish resource booking and attendance tracking

**Deliverables**:
1. **Resource Booking Interface** (Week 9-10)
   - Enhance existing `/oobc-management/calendar/bookings/request/`
   - Add resource availability calendar view
   - Add conflict detection
   - Add recurring booking option

2. **Event Attendance Tracker** (Week 10-11)
   - Enhance existing `/coordination/events/<uuid>/attendance-report/`
   - Add live attendance counter (updates every 10s)
   - Add participant list with check-in timestamps
   - Add QR code scanner integration

3. **Calendar Integration** (Week 11-12)
   - Ensure `/coordination/calendar/` shows all coordination events
   - Add external calendar sync setup page (Google/Outlook)
   - Add mobile PWA configuration

**Success Criteria**:
- ✅ Resource booking shows visual availability calendar
- ✅ Event attendance updates live without page reload
- ✅ External calendar sync configured (even if not fully functional)

---

### Phase 4: Project Management Portal Foundation (Weeks 13-16) ⭐ **CORE NEW MODULE**

**Goal**: Create Project Management Portal module with core pages

**Deliverables**:
1. **Create Django App** (Week 13)
   - Create `src/project_central/` app
   - Models: ProjectWorkflow, Alert, BudgetCeiling, BudgetScenario
   - Admin registration
   - URL configuration

2. **Portfolio Dashboard** (Week 13-14)
   - Create `/oobc-management/project-central/` page
   - Add summary metrics
   - Add project pipeline visualization
   - Add budget utilization charts (Chart.js)
   - Add alerts widget

3. **Project Workflow Pages** (Week 14-15)
   - Create project list page
   - Create project workflow detail page
   - Add workflow stage tracker (visual progress)
   - Add "Advance Stage" functionality

4. **Budget Approval Dashboard** (Week 15-16)
   - Create approval dashboard
   - Add 5-stage approval pipeline visualization
   - Add approval queue
   - Add approve/reject actions

**Success Criteria**:
- ✅ Project Management Portal app installed and accessible
- ✅ Portfolio dashboard shows summary metrics
- ✅ Can create and view project workflows
- ✅ Can approve/reject PPAs in budget approval workflow

---

### Phase 5: Project Management Portal - PPA Enhancements (Weeks 17-20)

**Goal**: Add PPA-specific dashboards for budget and M&E

**Deliverables**:
1. **PPA Budget Dashboard** (Week 17-18)
   - Create `/oobc-management/project-central/ppa/<uuid>/budget/` page
   - Add budget vs actual visualization
   - Add FundingFlow timeline
   - Add variance analysis

2. **PPA M&E Dashboard** (Week 18-19)
   - Create `/oobc-management/project-central/ppa/<uuid>/me/` page
   - Add outcome framework display
   - Add progress tracking
   - Add beneficiary tracking

3. **M&E Analytics Dashboard** (Week 19-20)
   - Create `/oobc-management/project-central/analytics/me/` page
   - Add performance scorecard
   - Add needs-to-results chain
   - Add sector performance comparison
   - Add geographic distribution map (Leaflet)
   - Add policy impact tracker

**Success Criteria**:
- ✅ PPA detail page has "Budget" and "M&E" tabs
- ✅ Budget dashboard shows funding flow timeline
- ✅ M&E analytics dashboard aggregates data from multiple PPAs

---

### Phase 6: Reporting & Alerts (Weeks 21-22)

**Goal**: Add cross-module reporting and alert system

**Deliverables**:
1. **Cross-Module Reporting** (Week 21)
   - Create reports list page
   - Add report generation for each type
   - Add export to PDF/Excel functionality
   - Add report scheduling (Celery tasks)

2. **Alert System** (Week 22)
   - Create alerts list page
   - Implement alert generation service (Celery daily task)
   - Add alert acknowledgment
   - Add alert detail views

**Success Criteria**:
- ✅ Can generate all 7 report types
- ✅ Reports can be exported to PDF and Excel
- ✅ Alerts generated daily and displayed on dashboard

---

### Phase 7: Polish & Optimization (Weeks 23-24)

**Goal**: Final polish, performance optimization, accessibility

**Deliverables**:
1. **Performance Optimization** (Week 23)
   - Add database query optimization (select_related, prefetch_related)
   - Add caching for dashboard metrics
   - Add pagination for large lists
   - Add loading skeletons for HTMX requests

2. **Accessibility & Mobile** (Week 24)
   - Ensure WCAG 2.1 AA compliance (keyboard navigation, ARIA labels)
   - Test all pages on mobile (Tailwind responsive classes)
   - Add touch-friendly UI for mobile
   - Test with screen readers

3. **Documentation** (Week 24)
   - Update user manual
   - Create video tutorials
   - Document HTMX patterns for developers

**Success Criteria**:
- ✅ All pages load < 3 seconds
- ✅ WCAG 2.1 AA compliance verified
- ✅ All pages responsive on mobile
- ✅ User documentation complete

---

## HTMX Patterns Library

### Pattern 1: Inline Editing
**Use Case**: Edit field without leaving page

```html
<!-- Display mode -->
<div class="editable-field"
     hx-get="{% url 'edit_field' object.id %}"
     hx-target="this"
     hx-swap="outerHTML">
    <span>{{ object.title }}</span>
    <i class="fas fa-edit text-gray-400 hover:text-blue-500 cursor-pointer"></i>
</div>

<!-- Edit mode (returned by server) -->
<form hx-post="{% url 'update_field' object.id %}"
      hx-target="this"
      hx-swap="outerHTML">
    <input type="text" name="title" value="{{ object.title }}" autofocus>
    <button type="submit">Save</button>
    <button hx-get="{% url 'cancel_edit' object.id %}"
            hx-target="form"
            hx-swap="outerHTML">Cancel</button>
</form>
```

### Pattern 2: Modal Dialogs
**Use Case**: Show detail/form in modal

```html
<!-- Trigger -->
<button hx-get="{% url 'task_modal' task.id %}"
        hx-target="#modal-container"
        hx-swap="innerHTML">
    View Task
</button>

<!-- Modal container (in base.html) -->
<div id="modal-container"></div>

<!-- Modal template (returned by server) -->
<div class="modal-backdrop"
     x-data="{ show: true }"
     x-show="show"
     @click.self="show = false">
    <div class="modal-content">
        <h2>{{ task.title }}</h2>
        <!-- Task details -->
        <button @click="show = false">Close</button>
    </div>
</div>
```

### Pattern 3: Kanban Drag-and-Drop
**Use Case**: Move tasks between columns

```html
<!-- Kanban board -->
<div class="kanban-board">
    {% for status in statuses %}
    <div class="kanban-column"
         data-status="{{ status }}"
         ondrop="handleDrop(event)"
         ondragover="allowDrop(event)">
        <h3>{{ status|title }}</h3>
        {% for task in tasks|filter:status %}
        <div class="task-card"
             draggable="true"
             data-task-id="{{ task.id }}"
             ondragstart="handleDragStart(event)">
            {{ task.title }}
        </div>
        {% endfor %}
    </div>
    {% endfor %}
</div>

<script>
function handleDrop(event) {
    event.preventDefault();
    const taskId = event.dataTransfer.getData('task_id');
    const newStatus = event.currentTarget.dataset.status;

    // Update via HTMX
    htmx.ajax('POST', '/api/tasks/update/', {
        values: { task_id: taskId, status: newStatus },
        target: `[data-task-id="${taskId}"]`,
        swap: 'outerHTML'
    });
}
</script>
```

### Pattern 4: Live Counters
**Use Case**: Update metrics without page reload

```html
<!-- Counter that updates every 30 seconds -->
<div class="metric-card"
     hx-get="{% url 'dashboard_metrics' %}"
     hx-trigger="load, every 30s"
     hx-swap="innerHTML">
    <h3>Active Projects</h3>
    <p class="count">{{ active_projects }}</p>
</div>
```

### Pattern 5: Infinite Scroll
**Use Case**: Load more items on scroll

```html
<div id="items-container">
    {% include "partials/items_list.html" %}
</div>

<!-- Load more trigger -->
{% if has_next_page %}
<div hx-get="{% url 'items_list' %}?page={{ next_page }}"
     hx-trigger="revealed"
     hx-swap="afterend"
     hx-target="#items-container">
    <div class="loading">Loading more...</div>
</div>
{% endif %}
```

### Pattern 6: Multi-Region Updates (Out-of-Band Swaps)
**Use Case**: Update multiple parts of page from single request

```html
<!-- Main content -->
<div id="task-list">
    <!-- Task list here -->
</div>

<!-- Counter (to be updated out-of-band) -->
<div id="task-count">{{ tasks.count }}</div>

<!-- Server response includes both -->
<!-- Main response -->
<div id="task-list">
    <!-- Updated task list -->
</div>

<!-- Out-of-band swap for counter -->
<div id="task-count" hx-swap-oob="true">{{ tasks.count }}</div>
```

### Pattern 7: Form Validation
**Use Case**: Real-time server-side validation

```html
<form hx-post="{% url 'create_task' %}"
      hx-target="#form-container"
      hx-swap="outerHTML">

    <input type="text"
           name="title"
           hx-post="{% url 'validate_title' %}"
           hx-trigger="blur"
           hx-target="#title-error"
           hx-swap="innerHTML">
    <div id="title-error"></div>

    <button type="submit">Create Task</button>
</form>
```

### Pattern 8: Dependent Dropdowns
**Use Case**: Second dropdown depends on first selection

```html
<!-- Region dropdown -->
<select name="region"
        hx-get="{% url 'get_provinces' %}"
        hx-trigger="change"
        hx-target="#province-select"
        hx-swap="innerHTML">
    <option value="">Select Region</option>
    {% for region in regions %}
    <option value="{{ region.id }}">{{ region.name }}</option>
    {% endfor %}
</select>

<!-- Province dropdown (populated by HTMX) -->
<div id="province-select">
    <select name="province" disabled>
        <option value="">Select region first</option>
    </select>
</div>
```

---

## Component Reusability

### 1. Data Table Card
**File**: `src/templates/components/data_table_card.html`

```html
<!-- Usage -->
{% include "components/data_table_card.html" with
    title="OBC Communities"
    headers=headers_list
    rows=data_rows
    create_url="communities_add"
%}
```

### 2. Form Field Components
**Files**:
- `src/templates/components/form_field.html`
- `src/templates/components/form_field_input.html`
- `src/templates/components/form_field_select.html`

```html
<!-- Usage -->
{% include "components/form_field_select.html" with
    field=form.municipality
    placeholder="Select municipality..."
%}
```

### 3. Modal Template
**File**: `src/templates/components/modal.html`

```html
<!-- Usage -->
{% include "components/modal.html" with
    modal_id="task-modal"
    modal_title="Task Details"
    modal_content=task_detail_html
%}
```

### 4. Alert/Notification Component
**File**: `src/templates/components/alert.html`

```html
<!-- Usage -->
{% include "components/alert.html" with
    alert_type="warning"
    alert_message="Budget ceiling approaching 90%"
    alert_dismissible=True
%}
```

### 5. Chart Component
**File**: `src/templates/components/chart.html`

```html
<!-- Usage -->
{% include "components/chart.html" with
    chart_id="budget-by-sector"
    chart_type="pie"
    chart_data=budget_data
    chart_labels=sector_labels
%}
```

### 6. Calendar Widget
**File**: `src/templates/components/calendar_widget.html`

```html
<!-- Usage -->
{% include "components/calendar_widget.html" with
    calendar_id="assessment-calendar"
    events_feed_url="mana_assessment_calendar_feed"
    editable=True
%}
```

### 7. Task Card (Kanban)
**File**: `src/templates/components/task_card.html`

```html
<!-- Usage -->
{% include "components/task_card.html" with
    task=task_object
    show_assignee=True
    show_due_date=True
%}
```

### 8. Progress Bar
**File**: `src/templates/components/progress_bar.html`

```html
<!-- Usage -->
{% include "components/progress_bar.html" with
    progress_percentage=75
    color="emerald"
    show_label=True
%}
```

### 9. Badge (Status/Tag)
**File**: `src/templates/components/badge.html`

```html
<!-- Usage -->
{% include "components/badge.html" with
    badge_text="High Priority"
    badge_color="red"
%}
```

### 10. Pagination
**File**: `src/templates/components/pagination.html`

```html
<!-- Usage -->
{% include "components/pagination.html" with
    page_obj=page_obj
    paginate_by=20
%}
```

---

## Integration Summary

### How Three Systems Integrate

```
┌─────────────────────────────────────────────────────────────────┐
│                      THREE INTEGRATED SYSTEMS                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌────────────────┐     ┌────────────────┐     ┌──────────────┐│
│  │   CALENDAR     │────▶│     TASKS      │────▶│   PROJECT    ││
│  │    SYSTEM      │     │   MANAGEMENT   │     │   CENTRAL    ││
│  └────────────────┘     └────────────────┘     └──────────────┘│
│         │                      │                       │         │
│         │                      │                       │         │
│         ▼                      ▼                       ▼         │
│  Events/Milestones      Staff Tasks           Project Workflows │
│  Resource Booking       Domain-Specific       Budget Approval   │
│  Attendance Tracking    Task Templates        M&E Analytics     │
│  External Sync          Task Analytics        Cross-Module      │
│  Calendar Sharing       Auto-generation       Reporting         │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**Integration Points**:
1. **Calendar ↔ Tasks**: Calendar events automatically create tasks; task due dates appear on calendar
2. **Tasks ↔ Project Management Portal**: Project workflows auto-generate tasks; task completion advances project stages
3. **Calendar ↔ Project Management Portal**: Project milestones appear on calendar; budget approval deadlines tracked
4. **All Three ↔ Core Modules**: Integration with MANA, Coordination, Monitoring, Recommendations

---

## Accessibility Requirements (WCAG 2.1 AA)

### 1. Keyboard Navigation
- All interactive elements accessible via Tab key
- Logical tab order (top to bottom, left to right)
- Visible focus indicators (ring-2 ring-blue-500)
- Escape key closes modals/dropdowns
- Arrow keys navigate dropdowns/lists
- Space/Enter activate buttons/links

### 2. ARIA Labels
- All icons have aria-label
- Dropdowns have aria-haspopup, aria-expanded
- Modals have role="dialog", aria-labelledby, aria-describedby
- Live regions use aria-live="polite" (for HTMX updates)
- Form fields have aria-required, aria-invalid

### 3. Color Contrast
- Text: 4.5:1 minimum (WCAG AA)
- UI components: 3:1 minimum
- Tailwind colors that meet standards:
  - Text: gray-900 on white, white on blue-600
  - Links: blue-600 (sufficient contrast)
  - Buttons: white on emerald-600, white on blue-600

### 4. Touch Targets
- Minimum 44x44px for all interactive elements
- Adequate spacing between buttons (at least 8px)
- Large enough tap areas for mobile

### 5. Screen Reader Support
- Semantic HTML (header, nav, main, section, article)
- Alt text for all images
- Descriptive link text (not "click here")
- Skip to main content link
- ARIA live regions for dynamic updates

---

## Mobile Responsiveness

### Tailwind Breakpoints
- `sm:` - 640px (small tablets)
- `md:` - 768px (tablets)
- `lg:` - 1024px (laptops)
- `xl:` - 1280px (desktops)
- `2xl:` - 1536px (large desktops)

### Mobile-First Approach
```html
<!-- Stack on mobile, grid on desktop -->
<div class="flex flex-col md:grid md:grid-cols-2 lg:grid-cols-3 gap-4">
    <!-- Content -->
</div>

<!-- Full width on mobile, constrained on desktop -->
<div class="w-full lg:w-3/4 xl:w-2/3 mx-auto">
    <!-- Content -->
</div>

<!-- Hide on mobile, show on desktop -->
<div class="hidden lg:block">
    <!-- Sidebar navigation -->
</div>

<!-- Show on mobile, hide on desktop -->
<button class="lg:hidden">
    <!-- Mobile menu button -->
</button>
```

### Responsive Tables
```html
<!-- On mobile, convert to card layout -->
<div class="block md:hidden">
    {% for item in items %}
    <div class="card mb-4">
        <div class="font-bold">{{ item.title }}</div>
        <div class="text-sm text-gray-600">{{ item.description }}</div>
    </div>
    {% endfor %}
</div>

<!-- On desktop, show as table -->
<div class="hidden md:block">
    <table class="min-w-full">
        <!-- Table content -->
    </table>
</div>
```

---

## Testing Strategy

### Manual Testing Checklist

**For Each Page**:
- [ ] Page loads without errors
- [ ] All HTMX interactions work (no full page reload)
- [ ] Forms validate correctly (server-side + client-side)
- [ ] Modals open/close properly
- [ ] Drag-and-drop works (if applicable)
- [ ] Calendar loads and renders events correctly
- [ ] Maps initialize only when visible (not eagerly)
- [ ] Responsive on mobile (test on actual device or Chrome DevTools)
- [ ] Keyboard navigation works (Tab, Enter, Escape, Arrow keys)
- [ ] ARIA labels present (inspect with browser DevTools)
- [ ] Color contrast meets WCAG AA (use Lighthouse audit)
- [ ] No console errors (check browser console)
- [ ] Loading states show during HTMX requests
- [ ] Error states display user-friendly messages

### Automated Testing

**Unit Tests** (Django):
```python
# Test views return correct status codes
def test_portfolio_dashboard(self):
    response = self.client.get(reverse('project_central:dashboard'))
    self.assertEqual(response.status_code, 200)
    self.assertContains(response, 'Total Budget')
```

**Integration Tests** (Django):
```python
# Test workflow advancement
def test_advance_project_stage(self):
    workflow = ProjectWorkflow.objects.create(...)
    response = self.client.post(
        reverse('project_central:advance_stage', args=[workflow.id]),
        {'new_stage': 'budget_planning'}
    )
    workflow.refresh_from_db()
    self.assertEqual(workflow.current_stage, 'budget_planning')
```

**End-to-End Tests** (Playwright or Selenium):
```python
# Test kanban drag-and-drop
def test_kanban_drag_drop(page):
    page.goto('/oobc-management/staff/tasks/')
    task = page.locator('[data-task-id="1"]')
    column = page.locator('[data-status="in_progress"]')
    task.drag_to(column)
    # Assert task moved
    assert page.locator('[data-status="in_progress"] [data-task-id="1"]').is_visible()
```

---

## Definition of Done

### Checklist for Each Page/Feature

- [ ] **Functionality**: All features work as specified
- [ ] **HTMX**: Interactions work without full page reload
- [ ] **Responsive**: Works on mobile (320px), tablet (768px), desktop (1280px)
- [ ] **Performance**: Page loads < 3 seconds, HTMX requests < 500ms
- [ ] **Accessibility**: WCAG 2.1 AA compliant (keyboard, ARIA, contrast)
- [ ] **Consistent UI**: Follows existing Tailwind patterns (emerald theme, rounded-xl, etc.)
- [ ] **Error Handling**: User-friendly error messages, no crashes
- [ ] **Loading States**: Shows loading indicator during HTMX requests
- [ ] **Empty States**: Displays helpful message when no data ("No tasks yet. Create your first task!")
- [ ] **Documentation**: User-facing help text or tooltips where needed
- [ ] **Testing**: Unit tests written and passing
- [ ] **Code Review**: PR reviewed by at least one other developer
- [ ] **Browser Testing**: Tested in Chrome, Firefox, Safari
- [ ] **Mobile Testing**: Tested on actual mobile device or simulator
- [ ] **No Console Errors**: Browser console clean (no JS errors)
- [ ] **No N+1 Queries**: Database queries optimized (use Django Debug Toolbar)
- [ ] **Caching**: Expensive queries cached appropriately
- [ ] **Security**: CSRF tokens present, permissions checked

---

## Summary: What to Build

### NEW Pages (25 from Project Management Portal)
1. Portfolio Dashboard
2. Project Workflow List
3. Project Workflow Detail
4. Budget Approval Dashboard
5. PPA Budget Detail
6. PPA M&E Dashboard
7. M&E Analytics Dashboard
8. Cross-Module Reporting List
9. Report Generation Pages (7 report types)
10. Alert System List
11. Budget Ceiling Management
12. Budget Scenario Planner
13. Participatory Budgeting Interface
14. Need → PPA Linkage Tool
15. MAO Focal Person Registry
16. Quarterly Report Portal
17-25. (Additional supporting pages)

### ENHANCEMENTS to Existing Pages (10)
1. **Dashboard** - Add unified metrics, activity feed, alerts
2. **Task Dashboard** - Polish existing enhanced dashboard
3. **PPA Detail** - Add tabs (Tasks, Calendar, Budget, M&E)
4. **Assessment Detail** - Add Tasks Board and Calendar tabs
5. **Needs Management** - Add Prioritization Board
6. **Resource Booking** - Add availability calendar, conflict detection
7. **Event Attendance** - Add live counter, QR scanner
8. **Services** - Create Services Catalog page
9. **Programs** - Create Programs Dashboard page
10. **Coordination Calendar** - Add external sync setup

### FIXES (1)
1. **Task Deletion Bug** - Fix instant UI update in kanban view

---

## Conclusion

This plan provides a **realistic, actionable roadmap** for completing the OBCMS UI and fully demonstrating its capabilities. By focusing on:
1. **Fixing critical bugs first** (Week 1)
2. **Enhancing existing pages** (35 pages over 12 weeks)
3. **Creating one new module** (Project Management Portal - 25 pages over 12 weeks)

We can achieve a **fully integrated OBCMS** in **24 weeks** with:
- ✅ Calendar System (88 tasks) - Complete
- ✅ Task Management (40 tasks) - Complete
- ✅ Project Management Portal (63 tasks) - Complete

**Total Implementation**: **75 items (25 new + 35 enhancements + 15 features) over 24 weeks**

---

**Next Steps**:
1. **Review this plan** with stakeholders
2. **Prioritize** based on business value
3. **Start Phase 1** (Weeks 1-4): Fix bugs, enhance dashboards
4. **Track progress** using TodoWrite throughout implementation
5. **Iterate** based on user feedback after each phase

---

**Document Version**: 1.0
**Status**: Ready for Review
**Owner**: Development Team
**Approver**: OOBC Leadership

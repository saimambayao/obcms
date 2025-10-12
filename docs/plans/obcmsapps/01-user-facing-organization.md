# OBCMS User-Facing Organization

**Document:** 01-user-facing-organization.md
**Last Updated:** 2025-10-12
**Purpose:** Complete guide to how users navigate and interact with OBCMS

---

## Table of Contents

1. [Navigation Structure Overview](#navigation-structure-overview)
2. [Main Navigation Menu](#main-navigation-menu)
3. [Role-Based Navigation](#role-based-navigation)
4. [Breadcrumb Navigation](#breadcrumb-navigation)
5. [User Menu & Profile](#user-menu--profile)
6. [Mobile Navigation](#mobile-navigation)
7. [Quick Action Sections](#quick-action-sections)
8. [URL Routing Structure](#url-routing-structure)

---

## Navigation Structure Overview

The OBCMS features a **role-based navigation system** that dynamically adapts based on user permissions and roles. The system serves three main user types:

1. **OOBC Staff** - Full system access (6 main modules)
2. **MOA Focal Users** - Simplified menu (organization profile + M&E reporting)
3. **MANA Participants/Facilitators** - Limited to workshop and assessment features

**Template Location:** `src/templates/common/navbar.html`

---

## Main Navigation Menu

### Logo & Branding
- **Icon:** Mosque icon (fas fa-mosque)
- **Title:** "OBC Management System"
- **Link:** Returns to main dashboard (`common:dashboard`)

### Navigation Color Scheme
- **Primary:** Blue-to-Teal gradient (`bg-bangsamoro`)
- **Text:** White on dark background
- **Hover:** Light green (`text-green-200`)

---

## 1. OBC Data Module

**Icon:** Users (fas fa-users)
**URL:** `common:communities_home`
**Description:** Central repository for Other Bangsamoro Community profiles and demographic data

### Sub-Navigation

#### 1.1 Barangay OBCs
- **URL:** `common:communities_manage`
- **Icon:** Blue map marker (fas fa-map-marker-alt)
- **Description:** Manage barangay-level profiles and data
- **Features:**
  - Comprehensive 11-section community profiles
  - 13 ethnolinguistic group tracking
  - Stakeholder management (leaders, Imams, elders)
  - Infrastructure and livelihood data

#### 1.2 Municipal OBCs
- **URL:** `common:communities_manage_municipal`
- **Icon:** Indigo city (fas fa-city)
- **Description:** View municipal coverage snapshots and trends
- **Features:**
  - Auto-aggregated data from barangays
  - Population reconciliation tracking
  - Coverage statistics and analysis

#### 1.3 Provincial OBCs
- **URL:** `common:communities_manage_provincial`
- **Icon:** Emerald flag (fas fa-flag)
- **Description:** View provincial coverage and OBC statistics
- **Features:**
  - Province-level aggregation
  - Submission workflow for MANA participants
  - Regional trend analysis

#### 1.4 Geographic Data 🔒
- **URL:** `common:mana_geographic_data`
- **Icon:** Purple map (fas fa-map)
- **Description:** Manage geographic layers and spatial datasets
- **Visibility:** Staff/Superuser only (`can_access_geographic_data`)
- **Features:**
  - 6 layer types (point, line, polygon, raster, heatmap, cluster)
  - GeoJSON data storage (NO PostGIS)
  - Interactive map visualizations
  - Leaflet.js integration

---

## 2. MANA Module (Mapping and Needs Assessment)

**Icon:** Map (fas fa-map-marked-alt)
**URL:** `common:mana_home`
**Visibility:** 🔒 Staff/Superuser only (`can_access_mana_filter`)

### Sub-Navigation

#### 2.1 Regional MANA
- **URL:** `common:mana_regional_overview`
- **Icon:** Sky globe (fas fa-globe-asia)
- **Description:** Access regional mapping layers and insights
- **Features:**
  - Region IX, X, XI, XII dashboards
  - Cross-province analysis
  - Aggregate findings visualization

#### 2.2 Provincial MANA
- **URL:** `common:mana_provincial_overview`
- **Icon:** Amber map (fas fa-map)
- **Description:** Review provincial dashboards and summaries
- **Features:**
  - Province-specific assessment data
  - Participant tracking
  - Submission progress monitoring

#### 2.3 Desk Review
- **URL:** `common:mana_desk_review`
- **Icon:** Purple book (fas fa-book-open)
- **Description:** Launch document-based assessments
- **Features:**
  - Secondary data analysis
  - Document review workflows
  - Research synthesis

#### 2.4 Survey
- **URL:** `common:mana_survey_module`
- **Icon:** Green clipboard (fas fa-clipboard-list)
- **Description:** Capture structured field survey data
- **Features:**
  - Digital survey forms
  - Offline data collection
  - Real-time submission tracking

#### 2.5 Key Informant Interview (KII)
- **URL:** `common:mana_kii`
- **Icon:** Rose comments (fas fa-comments)
- **Description:** Document KII findings and transcripts
- **Features:**
  - Interview scheduling
  - Transcript management
  - Qualitative analysis tools

**Note:** MANA Participants access sequential workshops separately at `/mana/workshops/assessments/{id}/participant/`

---

## 3. Coordination Module

**Icon:** Handshake (fas fa-handshake)
**URL:** Dynamic - `common:coordination_home` (OOBC) OR Organization detail (MOA Users)
**Label:** Dynamic - "Coordination" (OOBC) / "MOA Profile" (MOA Users)

### Sub-Navigation (OOBC Staff Only)

#### 3.1 Mapped Partners
- **URL:** `common:coordination_organizations`
- **Icon:** Cyan users-cog (fas fa-users-cog)
- **Description:** Directory of partner organizations and contacts
- **Features:**
  - 13 organization types (BMOA, LGU, NGA, NGO, CSO, etc.)
  - Contact management
  - Focal person tracking
  - Partnership level indicators

#### 3.2 Partnership Agreements
- **URL:** `common:coordination_partnerships`
- **Icon:** Amber file-contract (fas fa-file-contract)
- **Description:** Track MOAs, MOUs, and collaboration terms
- **Features:**
  - 9 partnership types
  - 12 status states (concept → active → completed)
  - Milestone tracking
  - Document version control

#### 3.3 Coordination Activities
- **URL:** `common:coordination_events`
- **Icon:** Lime calendar-check (fas fa-calendar-check)
- **Description:** Manage meetings, events, and follow-ups
- **Features:**
  - 10 engagement types (consultation, meeting, workshop, FGD, etc.)
  - Attendance tracking
  - Satisfaction ratings
  - Follow-up management

---

## 4. Recommendations Module

**Icon:** Gavel (fas fa-gavel)
**URL:** `common:recommendations_home`
**Visibility:** 🔒 Staff/Superuser/MOA Staff (`can_access_policies`)

### Sub-Navigation

#### 4.1 Policies
- **URL:** `common:recommendations_manage`
- **Icon:** Orange balance-scale (fas fa-balance-scale)
- **Description:** Monitor policy recommendations and status
- **Features:**
  - Evidence-based recommendations
  - A/B/C prioritization
  - Approval workflow (OOBC ED → OCM → Parliament)
  - Impact simulation (4 scenarios)

#### 4.2 Systematic Programs
- **URL:** `common:recommendations_programs`
- **Icon:** Indigo project-diagram (fas fa-project-diagram)
- **Description:** Review programmatic interventions and pipelines
- **Features:**
  - Multi-year program tracking
  - Thematic clustering
  - Budget allocation planning

#### 4.3 Services
- **URL:** `common:recommendations_services`
- **Icon:** Teal concierge-bell (fas fa-concierge-bell)
- **Description:** Track service delivery priorities and progress
- **Features:**
  - Service catalog
  - Application management
  - Request tracking

---

## 5. M&E Module (Monitoring & Evaluation)

**Icon:** Chart pie (fas fa-chart-pie)
**URL:** `monitoring:home`

### Sub-Navigation

#### 5.1 MOA PPAs
- **URL:** `monitoring:moa_ppas`
- **Icon:** Blue file-contract (fas fa-file-contract)
- **Description:** Monitor Ministries, Offices, and Agencies programs
- **Features:**
  - PPA (Programs, Projects, Activities) tracking
  - Budget monitoring
  - Timeline management
  - Beneficiary tracking

#### 5.2 OOBC Initiatives 🔒
- **URL:** `monitoring:oobc_initiatives`
- **Icon:** Emerald hand-holding-heart (fas fa-hand-holding-heart)
- **Description:** Office-led programs supporting OBC communities
- **Visibility:** Staff/Superuser only (`can_access_oobc_initiatives`)
- **Features:**
  - Internal project management
  - Budget utilization tracking
  - Impact measurement

#### 5.3 OBC Requests
- **URL:** `monitoring:obc_requests`
- **Icon:** Indigo file-signature (fas fa-file-signature)
- **Description:** Community proposals and assistance requests
- **Features:**
  - Request submission portal
  - Prioritization workflow
  - Response tracking
  - Fulfillment monitoring

#### 5.4 M&E Analytics 🔒
- **URL:** `project_central:me_analytics_dashboard`
- **Icon:** Emerald chart-bar (fas fa-chart-bar)
- **Description:** Performance metrics and impact analysis
- **Visibility:** Staff/Superuser only (`can_access_me_analytics`)
- **Features:**
  - Budget anomaly detection
  - Timeline delay prediction
  - Performance forecasting
  - Risk analysis dashboards

---

## 6. OOBC Management Module

**Icon:** Toolbox (fas fa-toolbox)
**URL:** `common:oobc_management_home`
**Visibility:** 🔒 Staff/Superuser only (`can_access_oobc_management`)

### Sub-Navigation

#### 6.1 Staff Management
- **URL:** `common:staff_management`
- **Icon:** Green user-cog (fas fa-user-cog)
- **Description:** Coordinate workloads, tasks, and staffing needs
- **Features:**
  - Staff profiles and job descriptions
  - Team assignments
  - Performance targets (KPIs)
  - Training and development tracking

#### 6.2 Work Items
- **URL:** `common:work_item_list`
- **Icon:** Emerald tasks (fas fa-tasks)
- **Description:** Unified task, activity, and project management system
- **Features:**
  - Kanban board view
  - Hierarchical task structure (MPTT)
  - Status workflow (pending → in_progress → completed)
  - Assignment and due dates

#### 6.3 Planning & Budgeting
- **URL:** `common:planning_budgeting`
- **Icon:** Blue file-signature (fas fa-file-signature)
- **Description:** Manage OOBC Office PPAs and OBC MOA PPAs
- **Features:**
  - Strategic planning
  - Operational work planning
  - Budget allocation
  - Scenario modeling

#### 6.4 Calendar Management
- **URL:** `common:oobc_calendar`
- **Icon:** Blue calendar-week (fas fa-calendar-week)
- **Description:** Organization-wide schedule for coordination, MANA, and staff actions
- **Features:**
  - RFC 5545-compliant recurrence patterns
  - Resource booking (vehicles, equipment, rooms, facilitators)
  - Multi-channel notifications (email, SMS, push, in-app)
  - External calendar sync (Google, Outlook, Apple)

#### 6.5 Project Management Portal
- **URL:** `project_central:portfolio_dashboard`
- **Icon:** Purple project-diagram (fas fa-project-diagram)
- **Description:** Project-activity-task integration dashboard and workflow management
- **Features:**
  - Portfolio-level view
  - Resource allocation
  - Timeline visualization
  - Collaboration tools

#### 6.6 User Approvals 🔒
- **URL:** `common:user_approvals`
- **Icon:** Amber user-check (fas fa-user-check)
- **Description:** Review and approve pending user account registrations
- **Visibility:** Executive roles only
- **Features:**
  - Two-tier approval for MOA/NGA/LGU staff
  - Account verification
  - Role assignment
  - Organization linkage

---

## Role-Based Navigation

### OOBC Staff & Superusers (Full Access)
**Navigation Menu:**
1. ✅ OBC Data (all sub-items)
2. ✅ MANA (all sub-items)
3. ✅ Coordination (all sub-items)
4. ✅ Recommendations (all sub-items)
5. ✅ M&E (all sub-items including analytics)
6. ✅ OOBC Management (all sub-items)

### MOA Focal Users (Simplified Menu)
**Navigation Menu:**
1. ✅ MOA Profile (direct link to their organization)
2. ✅ M&E (MOA PPAs - view-only for non-MOA PPAs)
3. ✅ Recommendations (read-only)

**No Access:**
- ❌ MANA Module
- ❌ Geographic Data
- ❌ OOBC Initiatives
- ❌ M&E Analytics
- ❌ OOBC Management

### MANA Participants/Facilitators
**Navigation Menu:**
1. ✅ Provincial OBC (read-only)
2. ✅ Regional MANA (overview only)
3. ✅ Facilitator Dashboard (if has `can_facilitate_workshop` permission)

**Separate Access:**
- Sequential Workshops (`/mana/workshops/assessments/{id}/participant/`)
- 5-workshop progression (gated access)

**No Access:**
- ❌ Desk Review
- ❌ Survey Module
- ❌ KII Module
- ❌ Coordination
- ❌ Recommendations
- ❌ M&E
- ❌ OOBC Management

### Community Leaders
**Navigation Menu:**
1. ✅ OBC Data (read-only for own community)
2. ✅ Dashboard (announcements, calendar events)

**No Access:**
- ❌ All other modules

---

## Breadcrumb Navigation

**Location:** Sticky below navbar (top-16 z-40)
**Pattern:** Dashboard > Section > Subsection > Current Page

### Examples:
```
Dashboard > OBC Data > Barangay OBC > Edit Barangay Profile
Dashboard > MANA > Regional Overview > Region IX
Dashboard > Coordination > Mapped Partners > Organization Details
Dashboard > M&E > MOA PPAs > Add PPA
Dashboard > OOBC Mgt > Staff Management > Staff Profile
```

**Implementation:** `{% block breadcrumb %}` in `base.html`

---

## User Menu & Profile

**Location:** Right side of navbar
**Trigger:** User avatar circle button

### User Information Display
- Full Name: `user.get_full_name|default:user.username`
- User Type: `user.get_user_type_display`
- Visibility: Hidden on mobile (md:flex)

### Dropdown Menu Items

1. **Profile** (`common:profile`)
   - Icon: User circle (fas fa-user-circle)
   - Edit personal information
   - Change password
   - Notification preferences

2. **Admin Panel** (`/admin/`) 🔒
   - Icon: Tools (fas fa-tools)
   - Visibility: Only if `user.is_staff`
   - Django admin interface

3. **Logout** (`common:logout`)
   - Icon: Sign-out (fas fa-sign-out-alt)
   - Color: Red text
   - Clear session and redirect

---

## Mobile Navigation

### Mobile Menu Toggle
- **Button:** Hamburger icon (fas fa-bars)
- **Visibility:** Screens < 1024px (lg:hidden)
- **Container:** Slides from right (80vw width)
- **Animation:** Smooth transition (duration-200)

### Mobile Menu Structure

**Accordion Sections:**
- Each main section has expandable toggle
- Chevron icon rotates 180° when expanded
- Only one section expanded at a time
- Sub-items indented (pl-9)

**Touch-Optimized:**
- Larger touch targets (min 48px)
- Clear visual feedback
- Auto-close on link click
- Auto-close on outside click
- Escape key closes menu

---

## Quick Action Sections

### Dashboard Quick Links
Each module home page features:
- **Return to Dashboard** button (top-left)
- **Quick stats cards** with action buttons
- **Recent activity** timelines

### Module-Specific Quick Actions

**OBC Data Home:**
- Add Barangay OBC
- Upload Community Data
- Generate Coverage Report

**MANA Home:**
- Create New Assessment
- View Pending Submissions
- Generate MANA Report

**Coordination Home:**
- Schedule Engagement
- Add Partner Organization
- View Calendar

**M&E Home:**
- Add MOA PPA
- View Analytics Dashboard
- Generate M&E Report

---

## URL Routing Structure

### Main URL Patterns

```python
# Dashboard
/dashboard/ → Main landing page

# OBC Data Module
/communities/ → Barangay OBCs
/communities/municipal/ → Municipal OBCs
/communities/provincial/ → Provincial OBCs
/communities/geographic-data/ → Geographic layers

# MANA Module
/mana/regional/ → Regional overview
/mana/provincial/ → Provincial overview
/mana/desk-review/ → Desk review
/mana/survey/ → Survey module
/mana/kii/ → Key Informant Interviews
/mana/workshops/ → Sequential workshops (participants)

# Coordination Module
/coordination/ → Coordination home
/coordination/organizations/ → Partner directory
/coordination/partnerships/ → Partnership agreements
/coordination/events/ → Coordination activities

# Recommendations Module
/policies/ → Policy recommendations
/policies/programs/ → Systematic programs
/policies/services/ → Service catalog

# M&E Module
/monitoring/ → M&E home
/monitoring/moa-ppas/ → MOA PPAs
/monitoring/oobc-initiatives/ → OOBC initiatives
/monitoring/obc-requests/ → Community requests
/project-management/analytics/ → M&E Analytics

# OOBC Management Module
/oobc-management/staff/ → Staff management
/oobc-management/work-items/ → Work items
/oobc-management/planning/ → Planning & budgeting
/oobc-management/calendar/ → Calendar management
/project-management/ → Project portal
/oobc-management/approvals/ → User approvals

# Admin
/admin/ → Django admin panel
```

### URL Naming Convention
- `app_name:view_name` (e.g., `common:dashboard`)
- Namespaced by app (common, monitoring, project_central)
- Consistent patterns across modules

---

## Accessibility Features

### ARIA Attributes
- `aria-label` on navigation sections
- `aria-haspopup="true"` on dropdown triggers
- `aria-expanded` on mobile accordion toggles
- `role="menu"` and `role="menuitem"` on dropdowns

### Keyboard Navigation
- Focus indicators on all interactive elements
- Escape key closes dropdowns and mobile menu
- Tab navigation through menu items
- Enter/Space activates buttons

### Visual Accessibility
- **High Contrast:** 4.5:1 minimum text contrast
- **Touch Targets:** Minimum 48px for mobile
- **Focus Indicators:** Clear blue outline on focus
- **Color Independence:** Icons and labels (not color alone)

---

## Visual Design & Branding

### Color Scheme
- **Primary Gradient:** Blue-to-Teal (`bg-bangsamoro`)
- **Navbar Background:** Blue-to-Teal with shadow
- **Text:** White on dark background
- **Hover:** Light green (`text-green-200`)

### Icon Color Coding (Sub-navigation)
- **Blue:** Primary/Infrastructure
- **Emerald/Green:** Success/OOBC initiatives
- **Amber/Orange:** Warnings/Approvals
- **Purple:** Advanced/Analytics
- **Indigo:** Programs/Systematic
- **Cyan:** User management
- **Rose/Red:** Critical actions

### Typography
- **Font:** System fonts (sans-serif)
- **Nav Items:** Medium weight (font-medium)
- **Sub-items:** Regular weight
- **Icons:** FontAwesome 5

---

## Best Practices for Users

### Navigation Tips
1. **Use Breadcrumbs:** Quickly navigate back to parent sections
2. **Bookmark Common Pages:** Direct URLs for frequent tasks
3. **Check User Type:** Verify your role in user menu
4. **Explore Dashboards:** Each module has a dedicated dashboard
5. **Use Search (Coming Soon):** Global search across modules

### Mobile Usage
1. **Rotate to Landscape:** Better table viewing
2. **Use Pull-to-Refresh:** Update data on mobile
3. **Enable Notifications:** Stay updated on approvals
4. **Offline Mode (Coming Soon):** Work without connection

### Efficiency Tips
1. **Keyboard Shortcuts:** Use Tab, Enter, Escape
2. **Quick Actions:** Use dashboard quick action cards
3. **Bulk Operations:** Select multiple items in tables
4. **Export Data:** Download reports as CSV/Excel
5. **Filters & Search:** Narrow down large datasets

---

## Related Documentation

- [Technical Organization](02-technical-organization.md) - Django app structure
- [Domain Architecture](03-domain-architecture.md) - Module relationships
- [Module Navigation Mapping](04-module-navigation-mapping.md) - Quick reference
- [UI Components & Standards](../../ui/OBCMS_UI_COMPONENTS_STANDARDS.md) - Design system

---

**Last Updated:** 2025-10-12
**Template Location:** `src/templates/common/navbar.html`
**Permission Filters:** `src/common/templatetags/moa_rbac.py`

# UAT Test Plan - BMMS Phase 7 Pilot Onboarding

**Document Version:** 1.0
**Last Updated:** 2025-10-14
**Status:** Ready for Execution
**Target Phase:** Phase 7 - Pilot MOA Onboarding

---

## Table of Contents

1. [Overview](#overview)
2. [Test Environment Setup](#test-environment-setup)
3. [Test Data Preparation](#test-data-preparation)
4. [Test Scenarios](#test-scenarios)
5. [Bug Reporting Process](#bug-reporting-process)
6. [UAT Schedule](#uat-schedule)
7. [Daily Check-in Procedures](#daily-check-in-procedures)
8. [Completion Tracking](#completion-tracking)
9. [Roles and Responsibilities](#roles-and-responsibilities)
10. [Success Criteria](#success-criteria)

---

## Overview

### Purpose
This User Acceptance Testing (UAT) plan validates that the Bangsamoro Ministerial Management System (BMMS) meets the operational needs of the three pilot Ministries, Offices, and Agencies (MOAs) before full rollout to all 44 MOAs.

### Scope
- **Planning Module**: Strategic plan creation and submission
- **Budgeting Module**: Budget proposal creation and submission (Parliament Bill No. 325)
- **Coordination Module**: Inter-MOA partnerships and calendar management
- **Performance Reporting**: Dashboard and export capabilities
- **OCM Oversight**: Aggregated viewing and reporting (OCM users only)

### Pilot MOAs
1. **Ministry of Basic, Higher, and Technical Education (MBHTE)**
2. **Ministry of Health (MOH)**
3. **Ministry of Social Services and Development (MSSD)**

### Testing Duration
**Total Duration:** 2 weeks (10 business days)
- **Week 1:** Core functionality testing (TS1-TS4)
- **Week 2:** Advanced features and integration testing (TS5-TS7)

### Testing Team
- **UAT Coordinator:** BMMS Implementation Team Lead
- **Pilot Users:** 3-5 users per pilot MOA (15 total users)
- **Technical Support:** Development team (on-call)
- **OCM Observer:** 1 OCM representative

---

## Test Environment Setup

### Environment Details
- **URL:** `https://staging.bmms.barmm.gov.ph`
- **Database:** Isolated staging database (no production data)
- **Backup Schedule:** Daily snapshots during UAT period
- **Access Hours:** Monday-Friday, 8:00 AM - 5:00 PM (Asia/Manila)

### Prerequisites for Testers

#### Hardware Requirements
- **Device:** Desktop, laptop, or tablet
- **Screen Resolution:** Minimum 1366x768 (responsive design tested)
- **Internet:** Stable connection (minimum 2 Mbps)
- **Browser:** Chrome 120+, Firefox 121+, Edge 120+, Safari 17+

#### User Account Setup
Each tester will receive:
1. **Organization Assignment:** One of three pilot MOAs
2. **User Credentials:** Username and temporary password
3. **Role Assignment:** Based on actual job function
   - Planning Officer
   - Budget Officer
   - Coordination Officer
   - Department Head
   - MOA Administrator
   - OCM Observer (for OCM testers only)

#### Initial Login Steps
1. Navigate to `https://staging.bmms.barmm.gov.ph`
2. Click "Login" button
3. Enter provided username and temporary password
4. Complete mandatory password change
5. Review welcome tutorial (5 minutes)
6. Verify organization name displayed correctly

### Test Environment Reset
- **Daily Reset:** 7:00 AM Asia/Manila (if needed)
- **On-Demand Reset:** Request via UAT coordinator
- **Data Preservation:** Marked test data retained for review

---

## Test Data Preparation

### Pre-Populated Data

#### Geographic Data
- All regions, provinces, municipalities, and barangays loaded
- Focus areas: Regions IX, X, XI, XII (Mindanao)

#### User Data
- 15 test users (5 per pilot MOA)
- 1 OCM observer account
- Role assignments match real-world structure

#### Organization Data
- Three pilot MOA profiles created
- Organizational hierarchies defined
- Budget allocations preset for FY 2026

### Test Data Templates

#### Strategic Plan Template
```
Plan Name: [MOA Name] Strategic Plan FY 2026
Planning Period: January 1, 2026 - December 31, 2026
Focus Areas:
  - Service delivery enhancement
  - Capacity building
  - Infrastructure development
Goals: 3-5 strategic goals
Objectives: 2-4 objectives per goal
Key Performance Indicators: 1-3 KPIs per objective
```

#### Budget Proposal Template (Bill No. 325)
```
Proposal Name: [MOA Name] FY 2026 Budget Proposal
Fiscal Year: 2026
Total Budget: PHP 50,000,000 - PHP 500,000,000
Categories:
  - Personnel Services (PS)
  - Maintenance and Other Operating Expenses (MOOE)
  - Capital Outlay (CO)
Programs: Aligned with strategic plan
Sub-programs: Program components
Activities: Budget line items
```

#### Inter-MOA Partnership Template
```
Partnership Name: [MOA A] - [MOA B] Collaboration
Partnership Type: Service Collaboration / Resource Sharing
Lead Organization: [MOA Name]
Partner Organizations: [Other MOA(s)]
Focus Area: Education / Health / Social Services
Duration: 6-12 months
Expected Outcomes: 3-5 measurable outcomes
```

### Sample Test Users

| Username | Organization | Role | Primary Scenarios |
|----------|--------------|------|-------------------|
| mbhte_planning01 | MBHTE | Planning Officer | TS1, TS4, TS6 |
| mbhte_budget01 | MBHTE | Budget Officer | TS2, TS4, TS7 |
| mbhte_coord01 | MBHTE | Coordination Officer | TS3, TS6 |
| moh_planning01 | MOH | Planning Officer | TS1, TS4, TS6 |
| moh_budget01 | MOH | Budget Officer | TS2, TS4, TS7 |
| moh_coord01 | MOH | Coordination Officer | TS3, TS6 |
| mssd_planning01 | MSSD | Planning Officer | TS1, TS4, TS6 |
| mssd_budget01 | MSSD | Budget Officer | TS2, TS4, TS7 |
| mssd_coord01 | MSSD | Coordination Officer | TS3, TS6 |
| ocm_observer01 | OCM | OCM Observer | TS5, TS7 |

---

## Test Scenarios

### TS1: Create and Submit Strategic Plan

**Test ID:** TS1
**Priority:** CRITICAL
**Module:** Planning
**Estimated Duration:** 30-45 minutes

#### Objective
Verify that planning officers can create, edit, save, and submit a comprehensive strategic plan aligned with their MOA's mandate.

#### Prerequisites
- User logged in with Planning Officer role
- Access to Planning module
- Understanding of strategic planning concepts

#### Test Data Requirements
- Organization: Assigned pilot MOA
- Planning period: FY 2026 (Jan 1 - Dec 31, 2026)
- 3 strategic goals minimum
- 2 objectives per goal minimum
- 1 KPI per objective minimum

#### Step-by-Step Instructions

**Step 1: Navigate to Planning Module**
1. Click "Planning" in main navigation menu
2. Verify Planning dashboard loads
3. Confirm "Create New Plan" button is visible

**Expected Result:**
- Planning dashboard displays existing plans (if any)
- "Create New Plan" button is enabled and clickable
- User sees statistics: Total Plans, Draft Plans, Submitted Plans, Approved Plans

**Step 2: Initiate New Strategic Plan**
1. Click "Create New Plan" button
2. Select plan type: "Strategic Plan"
3. Enter plan name: "[Your MOA] Strategic Plan FY 2026"
4. Set planning period: January 1, 2026 - December 31, 2026
5. Add brief description (50-200 words)
6. Click "Continue" button

**Expected Result:**
- Form validation passes
- System navigates to strategic plan builder interface
- Autosave indicator appears (saves every 30 seconds)
- Progress tracker shows "Step 1 of 5: Basic Information - Complete"

**Step 3: Define Strategic Goals**
1. Click "Add Strategic Goal" button
2. Enter goal title: "Enhance Service Delivery Quality"
3. Enter goal description (100-300 words)
4. Set goal priority: High / Medium / Low
5. Select focus area from dropdown (e.g., "Service Excellence")
6. Repeat for 2-3 additional goals
7. Click "Save Goals" button

**Expected Result:**
- Each goal displays with edit/delete options
- Goal counter updates: "3 of 3 goals defined"
- Progress tracker shows "Step 2 of 5: Strategic Goals - Complete"
- Success notification: "Goals saved successfully"

**Step 4: Define Objectives and KPIs**
1. Click "Add Objectives" under first goal
2. Enter objective title: "Improve response time to beneficiary requests"
3. Enter objective description (50-150 words)
4. Set target completion date: Q4 2026
5. Click "Add KPI" under objective
6. Enter KPI name: "Average response time (hours)"
7. Set baseline value: 48 hours
8. Set target value: 24 hours
9. Select measurement frequency: Monthly
10. Repeat for all objectives (2-4 per goal)
11. Click "Save Objectives & KPIs" button

**Expected Result:**
- Objectives nest visually under their parent goals
- KPIs display with baseline and target values
- System calculates total KPIs: "9 KPIs defined"
- Progress tracker shows "Step 3 of 5: Objectives & KPIs - Complete"

**Step 5: Assign Responsibilities**
1. For each objective, click "Assign Responsibility"
2. Select responsible unit/department from dropdown
3. Add responsible officer name (optional)
4. Set start date and end date for objective
5. Click "Save Assignments" button

**Expected Result:**
- Responsibility assignments display on each objective card
- Timeline visualization shows overlapping/sequential objectives
- Progress tracker shows "Step 4 of 5: Responsibilities - Complete"

**Step 6: Review and Submit**
1. Click "Review Plan" button
2. Review summary page showing all goals, objectives, KPIs
3. Verify all required fields are completed (system highlights missing items)
4. Click "Preview PDF" to see formatted plan
5. Click "Submit for Approval" button
6. Add submission notes (optional): "Initial strategic plan for FY 2026"
7. Confirm submission in dialog box

**Expected Result:**
- PDF preview generates successfully (opens in new tab)
- Plan formatting is professional and readable
- Submit button changes to "Plan Submitted" (disabled)
- Status badge changes from "Draft" to "Pending Approval"
- Notification email sent to approver (Department Head)
- Success message: "Strategic plan submitted successfully. Approval pending."
- User redirected to Planning dashboard

**Step 7: Verify Submission**
1. Return to Planning dashboard
2. Locate submitted plan in "Pending Approval" section
3. Click plan title to view read-only version
4. Verify all entered data is saved correctly

**Expected Result:**
- Plan appears in "Pending Approval" list
- Submission timestamp displayed
- Read-only view shows all goals, objectives, KPIs
- "Edit" button is disabled (plan locked for approval)
- Activity log shows submission record

#### Pass/Fail Criteria

**PASS Criteria:**
- All steps completed without errors
- Data saved correctly at each stage
- Autosave prevented data loss
- PDF preview generated successfully
- Submission workflow completed
- Status changed to "Pending Approval"
- Notification sent to approver

**FAIL Criteria:**
- Form validation errors prevent submission
- Data loss during autosave
- PDF preview fails to generate
- Submission does not change status
- Approval notification not sent
- User unable to view submitted plan

#### Roles to Test This Scenario
- Planning Officer (Primary)
- Department Head (Approval workflow)
- MOA Administrator (View all plans)

#### Notes for Testers
- Test autosave by refreshing page mid-creation
- Try submitting incomplete plan to verify validation
- Check mobile responsiveness on tablet/phone
- Verify accessibility: keyboard navigation, screen reader compatibility

---

### TS2: Create and Submit Budget Proposal

**Test ID:** TS2
**Priority:** CRITICAL
**Module:** Budgeting
**Estimated Duration:** 45-60 minutes

#### Objective
Verify that budget officers can create, structure, and submit a comprehensive budget proposal compliant with Parliament Bill No. 325 (Bangsamoro Budget Process).

#### Prerequisites
- User logged in with Budget Officer role
- Access to Budgeting module
- Strategic plan exists (TS1 completed or pre-populated)
- Understanding of Bill No. 325 budget categories

#### Test Data Requirements
- Organization: Assigned pilot MOA
- Fiscal year: FY 2026
- Total budget allocation: PHP 50,000,000 - PHP 500,000,000
- Budget categories: PS (Personnel Services), MOOE (Maintenance and Other Operating Expenses), CO (Capital Outlay)
- Programs: Aligned with strategic plan goals
- Sub-programs: Program components
- Activities: Line-item budget entries

#### Step-by-Step Instructions

**Step 1: Navigate to Budgeting Module**
1. Click "Budgeting" in main navigation menu
2. Verify Budgeting dashboard loads
3. Confirm "Create New Budget Proposal" button is visible
4. Review budget allocation summary for your MOA

**Expected Result:**
- Budgeting dashboard displays FY 2026 allocation
- "Create New Budget Proposal" button is enabled
- Dashboard shows: Total Allocation, Utilized Amount, Remaining Balance
- Historical budget data displayed (if available)

**Step 2: Initiate New Budget Proposal**
1. Click "Create New Budget Proposal" button
2. Enter proposal name: "[Your MOA] FY 2026 Budget Proposal"
3. Select fiscal year: 2026
4. Verify total allocation displayed: PHP [Amount]
5. Select linked strategic plan from dropdown
6. Add executive summary (200-500 words)
7. Click "Continue to Budget Structure" button

**Expected Result:**
- Form validation passes
- System displays total allocation correctly
- Strategic plan dropdown shows approved/submitted plans
- Executive summary accepts rich text formatting
- Progress indicator shows "Step 1 of 6: Proposal Information"

**Step 3: Define Program Structure**
1. Click "Add Program" button
2. Enter program name: "Education Quality Enhancement Program"
3. Link to strategic goal from dropdown (auto-populated from linked plan)
4. Select program category: Service Delivery / Support Services / Capital Investment
5. Set program duration: Full year / Quarterly
6. Add program description (100-300 words)
7. Click "Add Sub-Program" under program
8. Enter sub-program name: "Teacher Training Initiative"
9. Add sub-program description
10. Repeat to create 2-3 programs with 2-3 sub-programs each
11. Click "Save Program Structure" button

**Expected Result:**
- Programs display in hierarchical tree structure
- Visual indicator shows program linked to strategic goal
- Sub-programs nest under parent programs
- Program counter updates: "3 programs, 7 sub-programs"
- Progress indicator shows "Step 2 of 6: Program Structure - Complete"

**Step 4: Allocate Budget by Category**
1. Select first program from list
2. Click "Allocate Budget" button
3. Enter Personnel Services (PS) amount: PHP 20,000,000
4. Enter MOOE amount: PHP 15,000,000
5. Enter Capital Outlay (CO) amount: PHP 10,000,000
6. Verify total calculates automatically: PHP 45,000,000
7. Repeat for all programs
8. Review allocation summary showing all programs
9. Verify total does not exceed MOA allocation
10. Click "Save Budget Allocations" button

**Expected Result:**
- Budget calculator shows running total
- System warns if allocation exceeds limit (red warning banner)
- Percentage of total allocation displayed per program
- Chart visualizes PS/MOOE/CO distribution
- Progress indicator shows "Step 3 of 6: Budget Allocation - Complete"

**Step 5: Define Activities and Line Items**
1. Expand first sub-program
2. Click "Add Activity" button
3. Enter activity name: "Quarterly Teacher Workshop - Q1"
4. Select activity type: Training / Procurement / Construction / etc.
5. Enter activity description (50-150 words)
6. Set implementation schedule: Start date and end date
7. Click "Add Line Item" under activity
8. Enter line item details:
   - Item description: "Training materials and supplies"
   - Unit cost: PHP 500
   - Quantity: 100 teachers
   - Total: PHP 50,000 (auto-calculated)
   - Budget category: MOOE
9. Add 2-3 more line items for activity
10. Repeat for 5-7 activities per sub-program
11. Click "Save Activities" button

**Expected Result:**
- Activities nest under sub-programs in tree structure
- Line items display with unit cost calculations
- System validates line item totals match activity budget
- Activity timeline visualizes implementation schedule
- Warning appears if activity budget exceeds sub-program allocation
- Progress indicator shows "Step 4 of 6: Activities - Complete"

**Step 6: Align with Bill No. 325 Requirements**
1. Click "Bill No. 325 Compliance Check" button
2. Review compliance checklist:
   - Budget aligned with BARMM development priorities
   - Gender-responsive budgeting indicators included
   - Environmental sustainability considerations noted
   - Beneficiary impact assessment completed
3. For each item, click "Add Compliance Note" and enter justification
4. Upload supporting documents (optional):
   - Cost estimates
   - Procurement plans
   - Environmental impact assessments
5. Click "Save Compliance Data" button

**Expected Result:**
- Compliance checklist shows all items addressed
- Green checkmarks appear for completed items
- Supporting documents upload successfully (max 10MB per file)
- Compliance score calculated: "100% compliant"
- Progress indicator shows "Step 5 of 6: Compliance - Complete"

**Step 7: Review and Submit**
1. Click "Review Budget Proposal" button
2. Review summary page showing:
   - Program structure
   - Budget allocations by category (PS/MOOE/CO)
   - Activity timelines
   - Compliance status
3. Click "Generate Budget Report" to preview PDF
4. Verify report formatting follows Bill No. 325 template
5. Return to review page
6. Click "Submit Budget Proposal" button
7. Add submission notes: "FY 2026 initial budget proposal per Bill No. 325"
8. Confirm submission in dialog box

**Expected Result:**
- PDF report generates successfully (5-10 seconds)
- Report includes all budget tables, charts, and compliance notes
- Report is professionally formatted and print-ready
- Submit button changes to "Proposal Submitted" (disabled)
- Status changes from "Draft" to "Under Review"
- Notification sent to budget reviewer and Department Head
- Success message: "Budget proposal submitted for review"
- User redirected to Budgeting dashboard

**Step 8: Verify Submission**
1. Return to Budgeting dashboard
2. Locate submitted proposal in "Under Review" section
3. Click proposal title to view read-only version
4. Verify all budget data, programs, activities saved correctly
5. Check activity log for submission timestamp

**Expected Result:**
- Proposal appears in "Under Review" list with timestamp
- Read-only view displays complete budget structure
- "Edit" button is disabled (locked for review)
- Activity log shows submission and reviewer assignment
- Dashboard budget summary updates with proposed amounts

#### Pass/Fail Criteria

**PASS Criteria:**
- All steps completed without errors
- Budget calculations accurate (no rounding errors)
- Total allocation not exceeded
- Program structure aligns with strategic plan
- Bill No. 325 compliance requirements met
- PDF report generated successfully
- Submission workflow completed
- Status changed to "Under Review"
- Notifications sent to reviewers

**FAIL Criteria:**
- Budget calculations incorrect
- System allows over-allocation
- Program linkage to strategic plan fails
- Compliance checklist incomplete
- PDF report generation fails
- Submission does not change status
- Notifications not sent
- Data loss during save operations

#### Roles to Test This Scenario
- Budget Officer (Primary)
- Planning Officer (Verify strategic plan linkage)
- Department Head (Review workflow)
- OCM Budget Analyst (OCM aggregated view)

#### Notes for Testers
- Test budget calculator with large numbers (PHP 1,000,000,000+)
- Try allocating more than MOA total to verify validation
- Check rounding behavior for decimal amounts
- Verify currency formatting (PHP symbol, thousand separators)
- Test PDF generation with 20+ programs (stress test)
- Check mobile responsiveness for budget review

---

### TS3: Create Inter-MOA Partnership

**Test ID:** TS3
**Priority:** HIGH
**Module:** Coordination
**Estimated Duration:** 20-30 minutes

#### Objective
Verify that coordination officers can create, manage, and track inter-MOA partnerships for collaborative projects and resource sharing.

#### Prerequisites
- User logged in with Coordination Officer role
- Access to Coordination module
- Knowledge of other pilot MOAs and their mandates

#### Test Data Requirements
- Lead organization: User's assigned MOA
- Partner organizations: At least one other pilot MOA
- Partnership type: Service Collaboration / Resource Sharing / Joint Program
- Focus area: Education / Health / Social Services / Infrastructure
- Duration: 6-12 months
- Expected outcomes: 3-5 measurable results

#### Step-by-Step Instructions

**Step 1: Navigate to Coordination Module**
1. Click "Coordination" in main navigation menu
2. Verify Coordination dashboard loads
3. Confirm "Inter-MOA Partnerships" tab is visible
4. Click "Inter-MOA Partnerships" tab

**Expected Result:**
- Coordination dashboard displays with multiple tabs
- "Inter-MOA Partnerships" tab is active
- "Create New Partnership" button is visible and enabled
- Existing partnerships displayed (if any) with status badges

**Step 2: Initiate New Partnership**
1. Click "Create New Partnership" button
2. Enter partnership name: "MBHTE-MOH School Health Program"
3. Select partnership type: "Service Collaboration"
4. Select lead organization: [Your MOA]
5. Click "Add Partner Organization" button
6. Select partner from dropdown: [Other pilot MOA]
7. Add partnership description (200-400 words):
   - Purpose and objectives
   - Scope of collaboration
   - Resource commitments
8. Click "Continue" button

**Expected Result:**
- Form validation passes
- Lead organization pre-selected (user's MOA)
- Partner dropdown shows only other MOAs (not same organization)
- Character counter for description (400 max)
- Progress indicator shows "Step 1 of 4: Basic Information"

**Step 3: Define Focus Areas and Outcomes**
1. Select primary focus area: "Education"
2. Select secondary focus areas (optional): "Health", "Community Development"
3. Set partnership duration:
   - Start date: February 1, 2026
   - End date: January 31, 2027 (12 months)
4. Click "Add Expected Outcome" button
5. Enter outcome 1: "Train 500 teachers on health education integration"
6. Set outcome target date: June 30, 2026
7. Select outcome measurement: Quantitative (number of teachers trained)
8. Repeat for 3-5 total outcomes
9. Click "Save Focus Areas & Outcomes" button

**Expected Result:**
- Focus areas display as colored tags
- Duration calculates automatically: "12 months"
- Outcomes list with target dates and measurement types
- Timeline visualization shows outcome milestones
- Progress indicator shows "Step 2 of 4: Focus & Outcomes - Complete"

**Step 4: Assign Resources and Responsibilities**
1. Under "Lead Organization Resources", click "Add Resource Commitment"
2. Select resource type: "Personnel" / "Budget" / "Equipment" / "Facilities"
3. For Personnel: Enter "2 full-time coordinators"
4. Click "Add Budget Commitment"
5. Enter amount: PHP 5,000,000
6. Select budget source: "Program Budget" / "Special Allocation"
7. Under "Partner Organization Resources", click "Add Partner Commitment"
8. Enter partner resource: "Mobile health units (3 units)"
9. Click "Assign Coordination Roles"
10. Select lead coordinator from your MOA: [User or colleague]
11. Select partner coordinator: [Contact from partner MOA]
12. Add coordinator contact details (email, phone)
13. Click "Save Resources & Responsibilities" button

**Expected Result:**
- Resource commitments display in structured table
- Budget amounts formatted with PHP symbol and commas
- Resource types color-coded (Personnel: blue, Budget: green, Equipment: orange)
- Coordinator information saved with contact details
- Progress indicator shows "Step 3 of 4: Resources - Complete"

**Step 5: Set Coordination Schedule**
1. Click "Add Coordination Meeting" button
2. Select meeting frequency: "Monthly"
3. Set first meeting date: February 15, 2026
4. Select meeting type: "Virtual" / "In-Person" / "Hybrid"
5. Add meeting agenda template (optional):
   - Progress updates
   - Resource allocation
   - Issue resolution
6. Click "Add Reporting Milestone" button
7. Enter milestone: "Quarterly Progress Report"
8. Set milestone date: April 30, 2026
9. Repeat for additional milestones (quarterly)
10. Click "Save Schedule" button

**Expected Result:**
- Meeting schedule generates recurring events
- Calendar preview shows all meetings (color-coded)
- Milestones display on timeline with date markers
- System checks for date conflicts with existing events
- Progress indicator shows "Step 4 of 4: Schedule - Complete"

**Step 6: Review and Create Partnership**
1. Click "Review Partnership" button
2. Review summary page showing:
   - Partnership details
   - Partner organizations
   - Focus areas and outcomes
   - Resource commitments
   - Coordination schedule
3. Click "Preview Partnership Agreement" to see PDF
4. Return to review page
5. Click "Create Partnership" button
6. Confirm in dialog box: "Create and notify partner organization?"

**Expected Result:**
- Summary page displays all entered information
- PDF preview generates partnership agreement document
- Agreement includes all details in professional format
- Create button is enabled (green)
- Confirmation dialog appears

**Step 7: Verify Partnership Creation**
1. Confirm creation in dialog
2. Verify success message: "Partnership created successfully"
3. System redirects to partnership detail page
4. Verify status: "Pending Partner Confirmation"
5. Verify notification sent to partner organization coordinator
6. Click "Back to Partnerships" button
7. Locate new partnership in list with "Pending" status badge

**Expected Result:**
- Partnership created successfully
- Status is "Pending Partner Confirmation"
- Partnership appears in "My Partnerships" list
- Notification email sent to partner coordinator
- Activity log records creation event
- User can view partnership details (read-only until confirmed)

**Step 8: Simulate Partner Confirmation (Optional)**
1. Log out and log in as partner organization coordinator
2. Navigate to Coordination > Inter-MOA Partnerships
3. Locate partnership in "Pending Confirmation" section
4. Click partnership title to review
5. Click "Confirm Partnership" button
6. Add confirmation notes (optional)
7. Verify status changes to "Active"
8. Log back in as original user
9. Verify partnership now shows "Active" status

**Expected Result:**
- Partner coordinator receives notification
- Partnership details viewable by partner
- "Confirm" and "Decline" buttons visible
- Confirmation changes status to "Active"
- Both organizations can now access full partnership features
- Activity log records confirmation event

#### Pass/Fail Criteria

**PASS Criteria:**
- All steps completed without errors
- Partnership created with correct details
- Partner organization notified
- Status tracking works correctly
- PDF agreement generated successfully
- Coordination schedule created
- Resource commitments saved
- Confirmation workflow functional (if tested)

**FAIL Criteria:**
- Form validation errors prevent creation
- Partner notification not sent
- Status does not update correctly
- PDF agreement fails to generate
- Schedule conflicts not detected
- Resource data not saved
- Confirmation workflow fails

#### Roles to Test This Scenario
- Coordination Officer (Primary)
- Partner MOA Coordination Officer (Confirmation workflow)
- MOA Administrator (View all partnerships)
- OCM Observer (View aggregated partnerships)

#### Notes for Testers
- Test creating partnership with multiple partners (3+ MOAs)
- Try creating duplicate partnership to verify validation
- Check calendar integration for meeting schedule
- Verify mobile responsiveness for partnership details
- Test notification delivery and content
- Check accessibility: screen reader announces partnership status

---

### TS4: Generate Performance Report

**Test ID:** TS4
**Priority:** HIGH
**Module:** Performance Reporting
**Estimated Duration:** 20-30 minutes

#### Objective
Verify that users can generate comprehensive performance reports showing KPI progress, budget utilization, and program achievements.

#### Prerequisites
- User logged in with Planning Officer, Budget Officer, or MOA Administrator role
- Strategic plan exists with defined KPIs (TS1 completed)
- Budget proposal exists with activities (TS2 completed)
- Some performance data entered (KPI progress updates)

#### Test Data Requirements
- Reporting period: Q1 2026 (January-March) or custom date range
- KPIs with baseline and target values
- Budget utilization data (actual vs. planned)
- Activity completion status
- Program outputs and outcomes

#### Step-by-Step Instructions

**Step 1: Navigate to Reports Module**
1. Click "Reports" in main navigation menu
2. Verify Reports dashboard loads
3. Confirm "Generate New Report" button is visible
4. Review report templates available

**Expected Result:**
- Reports dashboard displays with report categories
- "Generate New Report" button is enabled
- Recent reports listed (if any) with download links
- Report templates shown: Performance, Budget, Strategic, Custom

**Step 2: Select Report Type and Parameters**
1. Click "Generate New Report" button
2. Select report type: "Performance Report"
3. Select reporting period:
   - Option A: "Quarterly" - Select Q1 2026
   - Option B: "Custom Date Range" - Enter Jan 1 - Mar 31, 2026
4. Select report scope: "All Programs" or specific program
5. Select data sources to include:
   - Strategic Plan KPIs (checked)
   - Budget Utilization (checked)
   - Activity Completion (checked)
   - Partnership Progress (checked)
6. Click "Configure Report" button

**Expected Result:**
- Report type selection displays available templates
- Date range picker validates dates (end date after start date)
- Program dropdown populated from user's MOA strategic plan
- Data source checkboxes allow multi-selection
- "Configure Report" button becomes active when required fields filled

**Step 3: Configure Report Sections**
1. Review default report structure:
   - Executive Summary
   - KPI Performance Dashboard
   - Budget Utilization Analysis
   - Program Progress
   - Challenges and Mitigation
   - Recommendations
2. Toggle sections on/off as needed (all on for full report)
3. For "KPI Performance Dashboard", select visualization type: "Charts and Tables"
4. For "Budget Utilization", select comparison: "Planned vs. Actual"
5. For "Program Progress", select detail level: "Detailed" (shows activities)
6. Click "Add Custom Section" (optional)
7. Enter section title: "Community Impact Highlights"
8. Add section content: Rich text editor with uploaded images
9. Click "Save Report Configuration" button

**Expected Result:**
- Report sections display in drag-and-drop interface
- Sections can be reordered by dragging
- Visualization options appear when section selected
- Custom sections allow rich text and media uploads
- Configuration saves automatically (autosave indicator)

**Step 4: Preview Report Data**
1. Click "Preview Report Data" button
2. Review KPI section showing:
   - KPI name
   - Baseline value
   - Target value
   - Current value (Q1 progress)
   - Progress percentage
   - Status indicator (On Track / At Risk / Behind)
3. Review Budget section showing:
   - Total allocated budget
   - Total utilized (Q1)
   - Utilization percentage
   - Category breakdown (PS/MOOE/CO)
4. Review Activity section showing:
   - Planned activities (Q1)
   - Completed activities
   - In-progress activities
   - Delayed activities
5. Click "Edit Data" if corrections needed (redirects to source module)
6. Verify data accuracy before proceeding

**Expected Result:**
- Preview displays actual data from system
- KPI progress calculated correctly (percentage)
- Budget utilization shows accurate amounts
- Activity status reflects current state
- Status indicators color-coded (Green: on track, Yellow: at risk, Red: behind)
- "Edit Data" links work correctly

**Step 5: Generate Report**
1. Return to report configuration page
2. Click "Generate Report" button
3. Select output format:
   - PDF (for printing/official reports)
   - Excel (for data analysis)
   - PowerPoint (for presentations)
4. Select report quality: Standard / High Quality (larger file size)
5. Add report metadata:
   - Report title: "Q1 2026 Performance Report - [MOA Name]"
   - Prepared by: [Your name]
   - Report date: April 15, 2026
6. Click "Generate" button
7. Wait for generation progress indicator (5-15 seconds)

**Expected Result:**
- Output format selection displays with format icons
- Quality options explain file size implications
- Metadata form validates required fields
- "Generate" button becomes "Generating..." with spinner
- Progress bar shows generation status: "Processing data... 50%"

**Step 6: Download and Review Report**
1. When generation completes, click "Download Report" button
2. Verify file downloads to browser's download folder
3. Open PDF report and verify:
   - Cover page with MOA logo and report title
   - Table of contents with page numbers
   - Executive summary (1 page)
   - KPI dashboard with charts and tables
   - Budget utilization charts (pie, bar, line)
   - Program progress section with activity list
   - Professional formatting and BMMS branding
4. Check report metadata: File properties show report date and author
5. Verify page numbering and footer with timestamp

**Expected Result:**
- Report downloads successfully (no errors)
- PDF file size: 2-5 MB (depends on charts and data)
- Report is professionally formatted
- All charts render correctly (no broken images)
- Tables are readable and properly formatted
- BMMS logo and branding appear on all pages
- Page numbers sequential and correct

**Step 7: Share and Archive Report**
1. Return to report generation page
2. Click "Share Report" button
3. Select sharing method: "Email" / "Generate Link"
4. For Email: Enter recipient email addresses (comma-separated)
5. Add email subject: "Q1 2026 Performance Report - [MOA Name]"
6. Add email message (optional)
7. Click "Send Report" button
8. Verify success message: "Report sent to 3 recipients"
9. Click "Archive Report" button to save in report library
10. Add archive tags: "Q1", "2026", "Performance"
11. Confirm archive action

**Expected Result:**
- Email sharing sends immediately
- Recipients receive email with report attached (or download link)
- Email subject and message appear correctly
- Success notification confirms delivery
- Archived report appears in "Report Library" with tags
- Report metadata saved: Generation date, creator, sharing history

**Step 8: Verify Report in Library**
1. Navigate to Reports > Report Library
2. Locate archived report using filters:
   - Report type: Performance
   - Date range: Q1 2026
   - Tags: Q1, 2026
3. Click report title to view details
4. Verify download link works
5. Check activity log for generation and sharing events

**Expected Result:**
- Report appears in library with correct metadata
- Filters work correctly to locate report
- Report details page shows all information
- Download link generates fresh report file
- Activity log records all actions (generation, sharing, archiving)

#### Pass/Fail Criteria

**PASS Criteria:**
- All steps completed without errors
- Report generated in selected format(s)
- Data accuracy verified (KPIs, budget, activities)
- Charts and visualizations render correctly
- Report formatting is professional
- Download and sharing work correctly
- Report archived successfully
- Activity log tracks all actions

**FAIL Criteria:**
- Report generation fails or times out
- Data inaccuracies in report
- Charts fail to render or are distorted
- Formatting issues (broken layout, missing pages)
- Download fails or file corrupted
- Email sharing does not send
- Archive operation fails

#### Roles to Test This Scenario
- Planning Officer (KPI reports)
- Budget Officer (Budget utilization reports)
- MOA Administrator (Comprehensive reports)
- Department Head (Executive summaries)
- OCM Observer (Aggregated MOA reports)

#### Notes for Testers
- Test report generation with large datasets (100+ KPIs)
- Try generating multiple formats simultaneously
- Check mobile view for report preview (not PDF download)
- Verify report templates meet Bill No. 325 reporting requirements
- Test sharing with invalid email addresses (validation)
- Check accessibility: PDF reports should be screen-reader compatible

---

### TS5: View OCM Dashboard (OCM Users Only)

**Test ID:** TS5
**Priority:** HIGH
**Module:** OCM Aggregation
**Estimated Duration:** 15-20 minutes

#### Objective
Verify that Office of the Chief Minister (OCM) observers can access aggregated, read-only views of all pilot MOA data for oversight and monitoring purposes.

#### Prerequisites
- User logged in with OCM Observer role
- Access to OCM Dashboard module
- Multiple pilot MOAs have submitted plans and budgets (TS1, TS2 completed)

#### Test Data Requirements
- At least 3 pilot MOAs with submitted strategic plans
- At least 3 pilot MOAs with submitted budget proposals
- Active inter-MOA partnerships (TS3 completed)
- Performance data from all pilot MOAs

#### Step-by-Step Instructions

**Step 1: Navigate to OCM Dashboard**
1. Click "OCM Dashboard" in main navigation menu
2. Verify OCM Dashboard loads (distinct from MOA dashboard)
3. Confirm "All MOAs" view is default
4. Review dashboard layout: Summary cards, charts, tables

**Expected Result:**
- OCM Dashboard displays with aggregated data
- Navigation menu shows OCM-specific options
- Dashboard title: "Office of the Chief Minister - BMMS Oversight"
- Summary cards show totals across all MOAs
- User role badge displays: "OCM Observer"

**Step 2: Review Aggregated Summary Statistics**
1. Locate summary stat cards at top of dashboard
2. Verify "Total MOAs" card shows: 3 pilot MOAs
3. Verify "Total Budget Allocation" shows sum of all MOA budgets
4. Verify "Active Strategic Plans" shows count of submitted plans
5. Verify "Active Partnerships" shows count of inter-MOA partnerships
6. Hover over each card to see tooltip with details
7. Click on "Total Budget Allocation" card to drill down

**Expected Result:**
- Stat cards display correct aggregated values
- Values formatted correctly (PHP currency, whole numbers)
- Cards use semantic colors (blue, green, yellow, orange)
- Hover tooltips provide additional context
- Clicking card navigates to detail view

**Step 3: Analyze MOA Comparison Charts**
1. Scroll to "MOA Budget Allocation Comparison" chart
2. Verify bar chart shows all 3 pilot MOAs side-by-side
3. Verify budget amounts accurate for each MOA
4. Hover over bars to see exact values
5. Scroll to "Strategic Plan Progress" chart
6. Verify chart shows KPI completion percentage per MOA
7. Scroll to "Budget Utilization by MOA" chart
8. Verify chart compares planned vs. actual spending
9. Click "Export Chart" button to download PNG image

**Expected Result:**
- Charts render correctly with all MOAs displayed
- Bar chart colors differentiate MOAs (MBHTE: blue, MOH: green, MSSD: orange)
- Hover tooltips show exact values and percentages
- Charts are responsive and readable on different screen sizes
- Export function downloads high-resolution chart image (PNG)

**Step 4: Review MOA Detail Table**
1. Scroll to "MOA Performance Summary" table
2. Verify table columns:
   - MOA Name
   - Total Budget
   - Budget Utilized (%)
   - Active Plans
   - Active Partnerships
   - Overall Performance (status indicator)
3. Verify all 3 pilot MOAs listed
4. Click on MOA name to drill down to MOA-specific dashboard
5. Verify MOA dashboard opens in read-only mode
6. Review MOA-specific data: plans, budgets, activities
7. Verify "Edit" buttons are hidden (read-only for OCM)
8. Click "Back to OCM Dashboard" button

**Expected Result:**
- Table displays all pilot MOAs with accurate data
- Columns sortable by clicking column header
- Status indicators color-coded (Green: on track, Yellow: needs attention, Red: critical)
- Drill-down navigation works correctly
- MOA dashboard displays in read-only mode
- No edit/delete actions available to OCM observer
- Back navigation returns to OCM Dashboard

**Step 5: Filter and Search MOA Data**
1. Locate "Filter MOAs" section above table
2. Select filter: "Budget Allocation" > "Greater than PHP 100,000,000"
3. Verify table updates to show only MOAs matching filter
4. Clear filter and select: "Performance Status" > "On Track"
5. Verify table updates again
6. Use search box: Enter "Ministry of Health"
7. Verify table shows only MOH row
8. Clear search and filters to show all MOAs

**Expected Result:**
- Filters apply immediately (no page reload)
- Table updates with smooth animation
- Filter tags display below filter section showing active filters
- Search highlights matching text in table
- "Clear All Filters" button appears when filters active
- Table returns to full view when filters cleared

**Step 6: Review Inter-MOA Partnership Network**
1. Click "Partnerships" tab in OCM Dashboard
2. Verify "Partnership Network" visualization loads
3. Review network graph showing MOA nodes and partnership connections
4. Click on MBHTE node to see partnerships involving MBHTE
5. Verify partnership details panel appears on right
6. Review partnership list table below network graph
7. Filter partnerships by status: "Active"
8. Verify table shows only active partnerships
9. Click on partnership name to view full partnership details

**Expected Result:**
- Network graph renders with MOA nodes and connecting lines
- Node size represents number of partnerships (larger = more partnerships)
- Connections color-coded by partnership type
- Interactive: clicking node highlights connections
- Partnership details panel shows relevant information
- Partnership table sortable and filterable
- Drill-down to partnership details works correctly

**Step 7: Generate Aggregated Reports**
1. Click "Generate OCM Report" button in dashboard header
2. Select report type: "MOA Performance Comparison"
3. Select date range: Q1 2026
4. Select MOAs to include: All pilot MOAs (default)
5. Select comparison metrics:
   - Budget utilization
   - KPI achievement
   - Partnership activity
6. Click "Generate Report" button
7. Wait for report generation (10-20 seconds)
8. Download generated report (PDF)
9. Open and review report content

**Expected Result:**
- Report configuration modal appears
- All pilot MOAs selected by default
- Metric checkboxes allow multi-selection
- Generate button active when required fields complete
- Progress indicator shows generation status
- Report downloads successfully
- Report contains comparative analysis of all MOAs
- Charts and tables show side-by-side MOA data

**Step 8: Verify Data Privacy and Access Control**
1. Navigate to MOA-specific detail page (e.g., MBHTE)
2. Attempt to access "Edit" function (should be hidden or disabled)
3. Attempt to access beneficiary-level data (should be restricted)
4. Verify only aggregated, anonymized data visible
5. Click "Activity Log" tab
6. Verify OCM access logged with timestamp and user

**Expected Result:**
- Edit buttons not visible or disabled for OCM observer
- Beneficiary personal data not accessible (Data Privacy Act 2012)
- Only program-level and statistical data visible
- Access attempts logged in activity log
- Activity log shows: "OCM Observer viewed MBHTE dashboard - [timestamp]"
- No ability to modify any MOA data

#### Pass/Fail Criteria

**PASS Criteria:**
- All steps completed without errors
- Aggregated data accurate across all MOAs
- Charts and visualizations render correctly
- Drill-down navigation works as expected
- Read-only access enforced correctly
- Filters and search function properly
- Reports generate successfully
- Data privacy controls respected
- Activity logging captures OCM access

**FAIL Criteria:**
- Aggregated data inaccuracies
- Charts fail to render or show incorrect data
- Edit functions accessible to OCM observer (security issue)
- Beneficiary data exposed to OCM (privacy violation)
- Filters do not work or cause errors
- Report generation fails
- Navigation errors between OCM and MOA dashboards

#### Roles to Test This Scenario
- OCM Observer (Primary)
- OCM Budget Analyst (Budget-focused oversight)
- Chief Minister's Office Staff (Executive summaries)

#### Notes for Testers
- This scenario is OCM-specific and cannot be tested by MOA users
- Verify data aggregation updates in near real-time (within 5 minutes)
- Test with different numbers of MOAs to verify scalability
- Check that OCM observer cannot access draft/unapproved data
- Verify audit trail captures all OCM viewing activities
- Test mobile responsiveness for OCM dashboard (tablet view)

---

### TS6: Use Calendar for Coordination

**Test ID:** TS6
**Priority:** MEDIUM
**Module:** Calendar & Scheduling
**Estimated Duration:** 15-25 minutes

#### Objective
Verify that users can effectively use the integrated calendar system for scheduling activities, meetings, and tracking milestones across programs and partnerships.

#### Prerequisites
- User logged in with any authenticated role
- Access to Calendar module
- Strategic plan with activities (TS1 completed)
- Budget proposal with implementation schedule (TS2 completed)
- Active partnerships with coordination meetings (TS3 completed)

#### Test Data Requirements
- At least 5 scheduled activities from programs
- At least 3 partnership coordination meetings
- Mix of event types: meetings, activities, milestones, deadlines

#### Step-by-Step Instructions

**Step 1: Navigate to Calendar Module**
1. Click "Calendar" in main navigation menu
2. Verify Calendar view loads (default: Month view)
3. Confirm current month displayed (April 2026)
4. Review calendar legend showing event types

**Expected Result:**
- Calendar loads within 2 seconds
- Current date highlighted (today's date)
- Month view displays full calendar grid
- Legend shows color codes:
  - Blue: Meetings
  - Green: Activities
  - Orange: Milestones
  - Red: Deadlines
  - Purple: Partnerships

**Step 2: Review Existing Events**
1. Locate events on calendar (colored dots on dates)
2. Click on event dot for April 15, 2026
3. Verify event details pop-up appears:
   - Event title
   - Event type
   - Time (start and end)
   - Location (physical/virtual)
   - Description
   - Participants/Assigned to
4. Click "View Full Details" link in pop-up
5. Verify event detail page opens
6. Return to calendar view

**Expected Result:**
- Events display as colored dots on appropriate dates
- Multiple events on same day show stacked dots
- Pop-up appears immediately on click
- Event details complete and accurate
- Detail page shows full event information with edit/delete buttons
- Back navigation returns to calendar

**Step 3: Change Calendar Views**
1. Click "Week" view button in calendar toolbar
2. Verify calendar switches to week view (April 14-20, 2026)
3. Review events displayed in time slots (8 AM - 6 PM)
4. Click "Day" view button
5. Verify calendar shows single day (today's date)
6. Click "Agenda" view button
7. Verify list view of upcoming events (next 30 days)
8. Return to "Month" view

**Expected Result:**
- View transitions are smooth (no page reload)
- Week view shows 7 days with hourly time slots
- Events display in correct time slots
- Day view shows detailed hourly schedule
- Agenda view lists events chronologically
- All views maintain consistent event data

**Step 4: Create New Calendar Event**
1. Click "Add Event" button in calendar toolbar
2. Select event type: "Meeting"
3. Enter event title: "Budget Review Meeting - Q1"
4. Select date: April 22, 2026
5. Set start time: 2:00 PM
6. Set end time: 3:30 PM (1.5 hours)
7. Select location type: "Virtual"
8. Enter virtual meeting link: "https://meet.bmms.gov.ph/budget-q1"
9. Add description: "Review Q1 budget utilization and adjust Q2 allocations"
10. Click "Add Participants" button
11. Select participants from user list (3-5 users)
12. Set reminder: "1 day before" and "1 hour before"
13. Click "Save Event" button

**Expected Result:**
- Event creation form validates all required fields
- Time picker allows 15-minute increments
- Duration calculates automatically (end - start)
- Virtual location shows meeting link field
- Participant selector shows users from same MOA
- Reminder options: 1 hour, 1 day, 1 week before
- Save button creates event and closes modal
- Success notification: "Event created successfully"

**Step 5: Verify Event Appears on Calendar**
1. Navigate to April 22, 2026 on calendar
2. Locate newly created event (blue dot for meeting)
3. Click event dot to verify details
4. Verify meeting appears in participant calendars (if accessible)
5. Check that reminder notification scheduled
6. Verify event appears in Agenda view

**Expected Result:**
- Event displays on correct date
- Event color matches type (blue for meeting)
- Event details match entered information
- Participants receive calendar invitation notification
- Reminder scheduled in system notifications
- Event listed in Agenda view under April 22

**Step 6: Edit Existing Event**
1. Click on event created in Step 4
2. Click "Edit Event" button in pop-up
3. Change end time: 3:30 PM → 4:00 PM
4. Add additional participant
5. Update description: Add "Bring Q1 expense reports"
6. Click "Save Changes" button
7. Verify update notification: "Event updated successfully"
8. Verify participants receive update notification

**Expected Result:**
- Edit form pre-populates with existing data
- Changes save correctly
- Duration recalculates (2:00 PM - 4:00 PM = 2 hours)
- Calendar updates immediately (no refresh needed)
- Updated event details display correctly
- Participants notified of changes via email/in-app notification

**Step 7: Filter Calendar Events**
1. Click "Filter" button in calendar toolbar
2. Select filter options:
   - Event type: "Meetings" only
   - Visibility: "My Events" (events user created or is participant)
3. Apply filters
4. Verify calendar shows only meetings involving user
5. Clear filters
6. Select filter: "Partnership Events" only
7. Verify calendar shows only partnership-related events
8. Clear all filters

**Expected Result:**
- Filter panel opens with checkboxes for event types
- Filters apply immediately (HTMX instant update)
- Active filters display as tags above calendar
- Filtered view shows only matching events
- Clear filters button removes all filters
- Calendar returns to full view

**Step 8: Integrate with Program Activities**
1. Navigate to Planning module
2. Open existing strategic plan
3. Locate activity with scheduled date
4. Click "View in Calendar" link on activity
5. Verify calendar opens with activity date selected
6. Verify activity displays as calendar event (green dot)
7. Click activity event to view details
8. Verify event links back to program activity detail

**Expected Result:**
- "View in Calendar" link navigates to Calendar module
- Calendar opens on activity date (auto-scroll to date)
- Activity displays as event with correct color (green)
- Event details include link to source activity
- Link back to Planning module works correctly
- Activity status synced with calendar event status

**Step 9: Export Calendar**
1. Click "Export" button in calendar toolbar
2. Select export format: "iCal (.ics)" for Outlook/Google Calendar integration
3. Select date range: "Next 30 days"
4. Select events to export: "All Events" or "Filtered Events"
5. Click "Download Calendar" button
6. Verify .ics file downloads
7. (Optional) Import .ics file into personal calendar app to verify compatibility

**Expected Result:**
- Export modal displays format options
- Date range selector allows custom ranges
- Export generates .ics file (standard calendar format)
- File downloads successfully (filename: "BMMS_Calendar_2026-04.ics")
- File imports correctly into Google Calendar/Outlook
- Event details preserved in export (title, time, location, description)

**Step 10: View Conflict Detection**
1. Click "Add Event" button
2. Enter event details:
   - Title: "Staff Training Session"
   - Date: April 22, 2026
   - Time: 2:30 PM - 4:30 PM
3. Add participant who already has meeting at 2:00 PM (from Step 4)
4. Verify conflict warning appears:
   - "Participant [Name] has existing event at this time"
   - Shows conflicting event details
5. Choose to "Create Anyway" or "Choose Different Time"
6. If choosing different time, adjust to 5:00 PM - 6:30 PM
7. Verify conflict warning disappears
8. Save event

**Expected Result:**
- Conflict detection runs automatically when time/participants entered
- Warning displays in orange banner above form
- Conflicting event details shown with time and title
- User can proceed despite conflict (warning only, not blocking)
- Adjusting time removes conflict warning
- Event saves successfully without conflicts

#### Pass/Fail Criteria

**PASS Criteria:**
- All steps completed without errors
- Calendar views render correctly (Month, Week, Day, Agenda)
- Events display on correct dates with accurate details
- Event creation and editing work properly
- Filters apply correctly and update instantly
- Export to .ics format successful
- Integration with Planning/Budgeting modules functional
- Conflict detection identifies scheduling conflicts
- Notifications sent for new/updated events

**FAIL Criteria:**
- Calendar views fail to render or display incorrect dates
- Events appear on wrong dates or times
- Event creation fails or data not saved
- Filters do not work or cause errors
- Export file corrupted or incompatible
- Module integration broken (links do not work)
- Conflict detection fails to identify conflicts
- Notifications not sent to participants

#### Roles to Test This Scenario
- Coordination Officer (Primary user)
- Planning Officer (Activity scheduling)
- Budget Officer (Budget cycle milestones)
- All authenticated users (personal calendar use)

#### Notes for Testers
- Test calendar with 50+ events to verify performance
- Try creating recurring events (daily, weekly, monthly)
- Check timezone handling (all times should be Asia/Manila)
- Verify mobile calendar view (touch gestures for navigation)
- Test calendar printing functionality
- Check accessibility: keyboard navigation for date picker
- Verify calendar syncs with activity deadlines from programs

---

### TS7: Export Data to Excel

**Test ID:** TS7
**Priority:** MEDIUM
**Module:** Data Export
**Estimated Duration:** 15-20 minutes

#### Objective
Verify that users can export various datasets to Excel format for offline analysis, reporting, and record-keeping.

#### Prerequisites
- User logged in with any authenticated role
- Access to modules with exportable data
- Sufficient data in system (plans, budgets, activities, partnerships)

#### Test Data Requirements
- At least 10 activities in strategic plan
- At least 20 budget line items
- At least 5 partnerships
- Performance data with KPIs (10+ KPIs)

#### Step-by-Step Instructions

**Step 1: Navigate to Planning Module**
1. Click "Planning" in main navigation menu
2. Open existing strategic plan
3. Navigate to "Activities" tab showing activity list
4. Locate "Export" button above activity table
5. Verify export options available

**Expected Result:**
- Planning module loads successfully
- Strategic plan detail page displays
- Activities displayed in table format
- "Export" button visible and enabled
- Dropdown shows export format options: Excel, CSV, PDF

**Step 2: Export Activity List to Excel**
1. Click "Export" button dropdown
2. Select "Export to Excel (.xlsx)"
3. Verify export configuration modal appears
4. Review export options:
   - Data range: "All Activities" or "Filtered Activities"
   - Columns to include: (checkboxes for all activity fields)
   - Include: KPIs, Assignments, Budget Allocations
5. Ensure all checkboxes selected (full export)
6. Click "Export" button in modal
7. Wait for file generation (2-5 seconds)
8. Verify file downloads automatically

**Expected Result:**
- Export modal opens immediately
- Configuration options display with defaults selected
- "Export" button active when options selected
- Progress indicator shows "Generating file..."
- File downloads to browser's download folder
- Filename format: "BMMS_Activities_[MOAName]_2026-04-14.xlsx"
- File size: 50-200 KB (depends on data volume)

**Step 3: Verify Excel File Structure**
1. Open downloaded Excel file in Microsoft Excel or LibreOffice Calc
2. Verify workbook structure:
   - Sheet 1: "Activities" - Main activity data
   - Sheet 2: "KPIs" - Related KPI data
   - Sheet 3: "Assignments" - Responsibility assignments
   - Sheet 4: "Budget" - Budget allocations per activity
3. Review "Activities" sheet columns:
   - Activity ID
   - Activity Name
   - Description
   - Status
   - Start Date
   - End Date
   - Responsible Unit
   - Budget Allocated
   - Program Name
   - Sub-Program Name
4. Verify data accuracy (compare with on-screen table)
5. Check formatting: Headers bold, data rows formatted correctly

**Expected Result:**
- Excel file opens without errors
- Multiple sheets organized logically
- "Activities" sheet contains all activity records
- Columns properly named and formatted
- Date fields in Excel date format (sortable)
- Currency fields formatted with PHP symbol
- Headers in bold with background color
- Data rows alternate white/light gray for readability

**Step 4: Test Data Filtering and Sorting in Excel**
1. In "Activities" sheet, enable Excel AutoFilter (Data > Filter)
2. Filter by "Status" column: Select "Completed"
3. Verify only completed activities display
4. Clear filter
5. Sort by "Start Date" (oldest to newest)
6. Verify activities sorted chronologically
7. Use Excel formulas to calculate:
   - Total activities: `=COUNTA(B:B)-1` (count rows minus header)
   - Total budget allocated: `=SUM(H:H)`
8. Verify calculations match dashboard statistics

**Expected Result:**
- AutoFilter applies successfully to all columns
- Filter dropdown shows unique values per column
- Filtering updates row count correctly
- Sorting maintains data integrity (rows stay intact)
- Excel formulas calculate correctly
- Calculated totals match BMMS dashboard values

**Step 5: Export Budget Data to Excel**
1. Navigate to Budgeting module
2. Open existing budget proposal
3. Navigate to "Budget Details" tab
4. Click "Export Budget" button
5. Select export scope:
   - Full Budget (all programs, sub-programs, activities)
   - Summary Only (program-level totals)
6. Select "Full Budget" option
7. Click "Export to Excel" button
8. Wait for file download
9. Open downloaded budget Excel file

**Expected Result:**
- Budget export button accessible
- Export scope options clearly labeled
- File generates and downloads successfully
- Filename: "BMMS_Budget_[MOAName]_FY2026_2026-04-14.xlsx"
- File size: 100-500 KB (larger due to detailed line items)

**Step 6: Verify Budget Excel File Structure**
1. Review workbook sheets:
   - Sheet 1: "Summary" - Program-level budget totals
   - Sheet 2: "PS" - Personnel Services detail
   - Sheet 3: "MOOE" - Maintenance and Other Operating Expenses detail
   - Sheet 4: "CO" - Capital Outlay detail
   - Sheet 5: "Timeline" - Activity implementation schedule
2. Review "Summary" sheet:
   - Program Name
   - Total Allocation
   - PS Amount
   - MOOE Amount
   - CO Amount
   - Utilization (if performance data available)
3. Verify totals calculated with formulas (SUM functions)
4. Check "PS" sheet for detailed line items with unit costs and quantities
5. Verify formulas: Total = Unit Cost × Quantity

**Expected Result:**
- Budget workbook contains 5 sheets
- "Summary" sheet shows program-level aggregation
- Category sheets (PS/MOOE/CO) show detailed line items
- "Timeline" sheet shows Gantt-style schedule
- Formulas calculate correctly (line item totals, category totals)
- Grand total matches budget proposal total
- Charts embedded in "Summary" sheet (pie chart of PS/MOOE/CO distribution)

**Step 7: Export Performance Dashboard Data**
1. Navigate to Reports module
2. Open performance dashboard for current quarter (Q1 2026)
3. Click "Export Dashboard Data" button
4. Select export components:
   - KPI Progress Table
   - Budget Utilization Table
   - Activity Completion Status
   - Partnership Progress
5. Select "Include Charts" checkbox (exports charts as images)
6. Click "Export to Excel" button
7. Download and open file

**Expected Result:**
- Export options allow selective data export
- "Include Charts" option available
- File downloads successfully
- Filename: "BMMS_Performance_Q1_2026_[MOAName]_2026-04-14.xlsx"
- Workbook contains sheets for each selected component

**Step 8: Verify Performance Data Excel File**
1. Review "KPI Progress" sheet:
   - KPI Name
   - Baseline Value
   - Target Value
   - Current Value (Q1)
   - Progress (%)
   - Status (On Track / At Risk / Behind)
2. Verify conditional formatting:
   - Progress ≥90%: Green
   - Progress 70-89%: Yellow
   - Progress <70%: Red
3. Review embedded chart images (if "Include Charts" selected)
4. Verify chart images clear and readable
5. Check "Budget Utilization" sheet calculations:
   - Utilization % = (Actual Spent / Allocated) × 100

**Expected Result:**
- KPI data complete and accurate
- Conditional formatting applied correctly (color-coded cells)
- Status indicators match dashboard
- Chart images embedded as high-resolution PNG
- Charts positioned above respective data tables
- Budget utilization calculations correct

**Step 9: Export Partnership List**
1. Navigate to Coordination > Inter-MOA Partnerships
2. Locate partnership list table
3. Apply filter: Status = "Active"
4. Click "Export" button above table
5. Select "Export Filtered Data" (only active partnerships)
6. Select format: "Excel"
7. Download and open file
8. Verify only active partnerships exported

**Expected Result:**
- Filter applies before export (only active partnerships)
- Export confirmation shows record count: "Exporting 5 active partnerships"
- File downloads: "BMMS_Partnerships_Active_2026-04-14.xlsx"
- Excel sheet contains filtered data only (5 partnerships)
- Columns: Partnership Name, Lead MOA, Partner MOAs, Status, Start Date, End Date, Focus Area

**Step 10: Test Export with Large Dataset**
1. Navigate to Planning module
2. Select "Export All Plans" option (multiple strategic plans)
3. Verify warning if export exceeds 10,000 rows:
   - "Large export detected. Generation may take 30-60 seconds."
4. Proceed with export
5. Monitor progress indicator during generation
6. Verify file downloads successfully (may take longer)
7. Open file and verify data integrity
8. Check file size (should be <5 MB for optimal Excel performance)

**Expected Result:**
- Warning appears for large exports (>10,000 rows)
- Progress indicator shows percentage: "Generating... 45%"
- File generates without errors (may take 30-60 seconds)
- Downloaded file opens successfully in Excel
- No data corruption or missing rows
- File size reasonable (<5 MB)
- If file size >5 MB, system suggests CSV format alternative

#### Pass/Fail Criteria

**PASS Criteria:**
- All steps completed without errors
- Excel files download successfully
- Workbook structure logical and organized
- Data accuracy verified (matches on-screen data)
- Formulas and calculations correct
- Formatting professional (headers, colors, borders)
- Charts embedded correctly (if applicable)
- Filtered exports contain only filtered data
- Large exports handle gracefully (warnings, progress indicators)

**FAIL Criteria:**
- Export fails or times out
- Excel files corrupted or cannot open
- Data inaccuracies or missing records
- Formulas broken or incorrect
- Formatting issues (unreadable, misaligned)
- Charts missing or fail to render
- Filtered exports include unfiltered data
- Large exports crash or fail

#### Roles to Test This Scenario
- Budget Officer (Budget exports)
- Planning Officer (Activity exports)
- Coordination Officer (Partnership exports)
- MOA Administrator (Comprehensive exports)
- OCM Observer (Aggregated MOA data exports)

#### Notes for Testers
- Test exports in both Microsoft Excel and LibreOffice Calc
- Verify Excel file compatibility (Excel 2016+ format)
- Check that exported data respects user permissions (organization-scoped)
- Test export performance with 1,000+ rows
- Verify CSV export option available for very large datasets
- Check mobile/tablet: Export button works but file opens on desktop
- Verify accessibility: Export button keyboard accessible

---

## Bug Reporting Process

### Bug Severity Levels

| Level | Description | Examples | Response Time |
|-------|-------------|----------|---------------|
| **CRITICAL** | System unusable, data loss risk, security breach | Login fails for all users, data deleted, unauthorized access | <1 hour |
| **HIGH** | Major feature broken, significant impact on workflow | Budget submission fails, report generation error, calculation errors | <4 hours |
| **MEDIUM** | Feature partially works, workaround available | Export to Excel fails but CSV works, minor display issues | <1 day |
| **LOW** | Cosmetic issue, minimal impact | Text alignment, color mismatch, tooltip typo | <3 days |

### Bug Report Template

When reporting a bug, use this template (available as form in staging environment):

```markdown
# Bug Report

**Bug ID:** [Auto-generated]
**Reported By:** [Your name and organization]
**Date/Time:** [Timestamp]
**Test Scenario:** [e.g., TS2: Create and Submit Budget Proposal]
**Step Number:** [e.g., Step 4]

## Bug Details

**Severity:** [CRITICAL / HIGH / MEDIUM / LOW]

**Summary:** [One-sentence description]

**Expected Behavior:**
[What should happen according to UAT test plan]

**Actual Behavior:**
[What actually happened]

**Steps to Reproduce:**
1. [First step]
2. [Second step]
3. [Continue...]

**Environment:**
- Browser: [Chrome 120 / Firefox 121 / etc.]
- Device: [Desktop / Laptop / Tablet]
- OS: [Windows 11 / macOS 14 / etc.]
- Screen Resolution: [1920x1080 / etc.]
- Date/Time of Issue: [Exact timestamp]

**Supporting Evidence:**
- Screenshot: [Attach screenshot showing issue]
- Error Message: [Copy exact error text]
- Browser Console Log: [Right-click > Inspect > Console tab]
- Network Log: [If API error, capture failed request]

**Impact:**
[Describe how this affects testing or user workflow]

**Workaround:**
[If temporary workaround exists, describe it]

**Additional Notes:**
[Any other relevant information]
```

### Bug Reporting Channels

**Primary Channel: BMMS UAT Bug Tracker**
- URL: `https://staging.bmms.barmm.gov.ph/uat/bugs`
- Access: All UAT testers have access
- Use built-in bug report form (auto-populates environment details)

**Secondary Channel: Email**
- For CRITICAL bugs only (if tracker unavailable)
- Email: `bmms-uat-support@barmm.gov.ph`
- Subject: `[CRITICAL BUG] Brief description`
- Include all template details in email body

**Emergency Contact: Development Team Lead**
- For system-wide outages or data loss incidents
- Contact via provided emergency contact number
- Available during testing hours: Mon-Fri, 8 AM - 5 PM

### Bug Triage Process

1. **Submission:** Tester submits bug via tracker or email
2. **Acknowledgment:** Auto-confirmation sent (within 5 minutes)
3. **Review:** Development team reviews bug (within response time SLA)
4. **Classification:** Bug severity confirmed or adjusted
5. **Assignment:** Bug assigned to developer
6. **Resolution:** Fix implemented and deployed to staging
7. **Verification:** Tester notified to re-test specific scenario
8. **Closure:** Tester confirms fix and closes bug

### Bug Status Workflow

```
NEW → CONFIRMED → IN PROGRESS → RESOLVED → VERIFIED → CLOSED
        ↓                            ↓
   NOT A BUG                    REOPENED (if issue persists)
```

### Best Practices for Bug Reporting

**DO:**
- Report bugs immediately when discovered
- Provide detailed steps to reproduce
- Attach screenshots and error messages
- Test in multiple browsers if possible
- Check if bug already reported (search tracker)
- Follow up on assigned bugs

**DON'T:**
- Delay reporting (memory fades)
- Report multiple bugs in one ticket (separate reports)
- Assume bug is "too minor" to report (report all issues)
- Edit test data after bug occurs (preserve state for investigation)
- Delete screenshots or error messages

---

## UAT Schedule

### Two-Week Testing Timeline

#### Week 1: Core Functionality Testing

**Monday, April 14, 2026**
- **9:00 AM:** UAT Kickoff Meeting (Virtual)
  - Introduction to BMMS and UAT objectives
  - Walkthrough of test environment
  - Distribution of test accounts and credentials
  - Q&A session
- **10:30 AM:** Environment Access Testing
  - All testers log in and complete initial setup
  - Password changes and profile setup
- **11:00 AM:** Begin TS1 (Create Strategic Plan)
  - Planning Officers focus on TS1
  - Support team available for questions
- **3:00 PM:** Daily Check-in Call
  - Progress updates
  - Issue resolution
  - Next day planning

**Tuesday, April 15, 2026**
- **9:00 AM:** Continue TS1 (Strategic Plan)
  - Complete plan creation and submission
  - Test approval workflow (Department Heads)
- **11:00 AM:** Begin TS2 (Create Budget Proposal)
  - Budget Officers focus on TS2
  - Verify strategic plan linkage
- **3:00 PM:** Daily Check-in Call

**Wednesday, April 16, 2026**
- **9:00 AM:** Continue TS2 (Budget Proposal)
  - Complete budget structure and allocation
  - Test Bill No. 325 compliance features
- **1:00 PM:** Begin TS3 (Inter-MOA Partnership)
  - Coordination Officers focus on TS3
  - Test partnership creation and confirmation workflow
- **3:00 PM:** Daily Check-in Call

**Thursday, April 17, 2026**
- **9:00 AM:** Continue TS3 (Partnerships)
  - Complete partnership setup
  - Test coordination schedules
- **11:00 AM:** Begin TS4 (Generate Performance Report)
  - All roles test reporting
  - Verify data accuracy in reports
- **3:00 PM:** Daily Check-in Call

**Friday, April 18, 2026**
- **9:00 AM:** Complete TS4 (Performance Reports)
  - Test multiple report formats (PDF, Excel, PowerPoint)
  - Verify report sharing and archiving
- **11:00 AM:** Week 1 Wrap-up Meeting (Virtual)
  - Review completed test scenarios (TS1-TS4)
  - Discuss bugs reported and resolution status
  - Preview Week 2 advanced scenarios
- **1:00 PM:** Buffer time for re-testing bug fixes
- **No 3:00 PM call (week-end wrap-up completed in morning)**

#### Week 2: Advanced Features and Integration Testing

**Monday, April 21, 2026**
- **9:00 AM:** Week 2 Kickoff Call
  - Review Week 1 outcomes
  - Introduce advanced scenarios
- **10:00 AM:** Begin TS5 (OCM Dashboard)
  - OCM Observer tests aggregated views
  - Verify read-only access controls
  - Test data privacy compliance
- **11:00 AM:** Begin TS6 (Calendar Coordination)
  - All roles test calendar features
  - Test event creation and conflict detection
- **3:00 PM:** Daily Check-in Call

**Tuesday, April 22, 2026**
- **9:00 AM:** Continue TS6 (Calendar)
  - Test calendar integration with programs
  - Verify export to .ics functionality
- **11:00 AM:** Begin TS7 (Export Data to Excel)
  - Test exports from multiple modules
  - Verify Excel file structure and accuracy
- **3:00 PM:** Daily Check-in Call

**Wednesday, April 23, 2026**
- **9:00 AM:** Complete TS7 (Excel Export)
  - Test large dataset exports
  - Verify filtered data exports
- **11:00 AM:** Integration Testing
  - Test cross-module workflows
  - Verify data consistency across modules
- **1:00 PM:** Performance Testing
  - Simulate multiple concurrent users
  - Test system responsiveness under load
- **3:00 PM:** Daily Check-in Call

**Thursday, April 24, 2026**
- **9:00 AM:** Exploratory Testing
  - Testers explore features beyond test scenarios
  - Test edge cases and unusual workflows
- **11:00 AM:** Accessibility Testing
  - Test keyboard navigation
  - Verify screen reader compatibility
  - Test mobile/tablet responsiveness
- **3:00 PM:** Daily Check-in Call

**Friday, April 25, 2026**
- **9:00 AM:** Re-testing and Verification
  - Re-test all resolved bugs
  - Verify all test scenarios pass
- **11:00 AM:** Final Bug Triage
  - Review remaining open bugs
  - Prioritize fixes for production deployment
- **1:00 PM:** UAT Final Review Meeting (Virtual)
  - Present testing summary and results
  - Review pass/fail status of all scenarios
  - Discuss go-live readiness
  - Collect tester feedback on BMMS usability
- **3:00 PM:** UAT Closeout and Documentation
  - Submit final completion tracking spreadsheet
  - Complete feedback forms
  - Celebrate successful UAT completion

### Testing Hours

- **Core Testing Hours:** Monday-Friday, 9:00 AM - 5:00 PM (Asia/Manila)
- **Support Availability:** Same as testing hours
- **Daily Check-in Calls:** 3:00 PM daily (30 minutes)
- **Environment Maintenance:** 7:00 AM - 8:00 AM daily (if needed)

### Holiday/Disruption Contingency

If testing is disrupted (e.g., power outage, system issue):
- **Minor disruption (<2 hours):** Extend testing day by disruption duration
- **Major disruption (>2 hours):** Add buffer day at end of Week 2
- **Critical system outage:** Pause UAT, reschedule affected scenarios

---

## Daily Check-in Procedures

### Purpose of Daily Check-ins

Daily check-in calls ensure:
- Progress tracking and accountability
- Rapid issue resolution
- Team coordination and morale
- Adjustments to testing plan as needed

### Daily Check-in Agenda (30 minutes)

**1. Roll Call (2 minutes)**
   - Attendance confirmation
   - Note any absences or new participants

**2. Progress Updates (10 minutes)**
   - Each pilot MOA representative reports:
     - Test scenarios completed today
     - Number of tests passed/failed
     - Percentage completion of daily goal
   - Quick wins and positive feedback

**3. Issue Discussion (10 minutes)**
   - Bugs reported since last check-in
   - Blockers preventing testing progress
   - Clarification questions on test scenarios
   - Support requests

**4. Resolution and Next Steps (5 minutes)**
   - Development team provides bug status updates
   - Assign action items for overnight resolution
   - Confirm tomorrow's testing focus
   - Adjust schedule if needed

**5. Q&A and Closing (3 minutes)**
   - Open floor for questions
   - Reminders and announcements
   - Encouragement and team building

### Check-in Meeting Details

- **Platform:** Microsoft Teams / Zoom (link provided at kickoff)
- **Time:** 3:00 PM daily (Asia/Manila)
- **Duration:** 30 minutes (strict timebox)
- **Recording:** All calls recorded for documentation
- **Attendance:** Mandatory for all UAT testers (unless pre-approved absence)

### Check-in Report Template

After each check-in, UAT Coordinator will distribute summary:

```markdown
# BMMS UAT Daily Check-in Summary
**Date:** [Date]
**Day:** [e.g., Monday, Week 1, Day 1]

## Attendance
- Present: [List of testers present]
- Absent: [List with reasons]

## Progress Summary
- **Test Scenarios Completed:** [e.g., TS1: 100%, TS2: 50%]
- **Tests Passed:** [Number]
- **Tests Failed:** [Number]
- **Overall Completion:** [Percentage of total UAT]

## Issues Reported
- **New Bugs:** [Count] - [Critical: X, High: Y, Medium: Z, Low: W]
- **Resolved Bugs:** [Count]
- **Blockers:** [List any blocking issues]

## Key Discussion Points
- [Summary of important discussions]
- [Decisions made]

## Action Items
| Action | Assigned To | Due Date |
|--------|-------------|----------|
| [Action item] | [Name/Team] | [Date/Time] |

## Tomorrow's Focus
- Test scenarios: [e.g., Complete TS2, Begin TS3]
- Special activities: [e.g., Bug re-testing]

## Notes
- [Any additional notes or reminders]
```

### Escalation During Check-ins

If CRITICAL issues arise during check-in:
1. **Immediate Response:** Development team commits to resolution ETA
2. **Workaround:** Temporary solution provided to unblock testing
3. **Follow-up:** Emergency call scheduled within 2 hours if needed
4. **Communication:** All testers notified via email of status updates

---

## Completion Tracking

### Completion Tracking Spreadsheet Template

All testers will receive access to a shared Google Sheet for real-time tracking. Template structure:

**Sheet 1: Test Scenario Progress**

| Test ID | Test Scenario | Tester Name | Organization | Status | Pass/Fail | Date Completed | Comments | Bug IDs |
|---------|---------------|-------------|--------------|--------|-----------|----------------|----------|---------|
| TS1 | Create Strategic Plan | John Doe | MBHTE | Completed | PASS | 2026-04-15 | All steps passed | - |
| TS1 | Create Strategic Plan | Jane Smith | MOH | Completed | PASS | 2026-04-15 | Minor UI issue noted | BUG-001 |
| TS1 | Create Strategic Plan | Ali Hassan | MSSD | In Progress | - | - | Starting Step 4 | - |
| TS2 | Create Budget Proposal | Maria Lopez | MBHTE | Not Started | - | - | - | - |

**Sheet 2: Bug Summary**

| Bug ID | Test Scenario | Severity | Description | Reporter | Date Reported | Status | Resolution Date |
|--------|---------------|----------|-------------|----------|---------------|--------|-----------------|
| BUG-001 | TS1 | LOW | Text alignment issue in activity form | Jane Smith | 2026-04-15 | RESOLVED | 2026-04-16 |
| BUG-002 | TS2 | HIGH | Budget calculation error when using decimals | John Doe | 2026-04-16 | IN PROGRESS | - |

**Sheet 3: Daily Summary**

| Date | Scenarios Tested | Tests Passed | Tests Failed | Bugs Reported | Bugs Resolved | Completion % |
|------|------------------|--------------|--------------|---------------|---------------|--------------|
| 2026-04-14 | TS1 | 2 | 0 | 0 | 0 | 14% |
| 2026-04-15 | TS1, TS2 | 5 | 1 | 2 | 0 | 28% |

**Sheet 4: Tester Participation**

| Tester Name | Organization | Role | Total Tests Assigned | Tests Completed | Participation % | Bugs Reported |
|-------------|--------------|------|----------------------|-----------------|-----------------|---------------|
| John Doe | MBHTE | Planning Officer | 7 | 3 | 43% | 2 |
| Jane Smith | MOH | Budget Officer | 7 | 3 | 43% | 1 |

**Sheet 5: Sign-off**

| Test Scenario | MBHTE Sign-off | MOH Sign-off | MSSD Sign-off | UAT Coordinator Approval | Final Status |
|---------------|----------------|--------------|---------------|--------------------------|--------------|
| TS1 | ✅ | ✅ | ✅ | ✅ | APPROVED |
| TS2 | ⏳ | ⏳ | ⏳ | ⏳ | PENDING |

**Legend:**
- ✅ Approved
- ⏳ Pending
- ❌ Rejected (requires re-test)

### How to Use Tracking Spreadsheet

**For Testers:**
1. **Update Status Daily:** Mark test scenarios as "Not Started", "In Progress", or "Completed"
2. **Record Pass/Fail:** After completing scenario, mark PASS or FAIL
3. **Add Comments:** Provide brief notes on issues encountered
4. **Link Bugs:** Reference bug IDs in "Bug IDs" column
5. **Sign-off:** Once all tests for scenario pass, add checkmark in sign-off sheet

**For UAT Coordinator:**
1. **Monitor Progress:** Review completion percentages daily
2. **Identify Blockers:** Flag testers who are stuck or behind schedule
3. **Validate Sign-offs:** Approve scenarios once all MOAs sign off
4. **Generate Reports:** Use data for daily summaries and final report

### Completion Criteria

**Individual Test Scenario Completion:**
- All steps executed without skipping
- Pass/Fail recorded with justification
- Bugs reported for any failures
- Comments added for any issues
- Tester signature (electronic) in tracking sheet

**Overall UAT Completion:**
- All 7 test scenarios completed by all pilot MOAs (21 test executions total)
- 95% pass rate required (maximum 1 failure per scenario across all MOAs)
- All CRITICAL and HIGH bugs resolved
- All pilot MOAs sign off on system readiness
- UAT final report submitted

### Final UAT Report Structure

At end of UAT, coordinator will compile final report:

```markdown
# BMMS Phase 7 UAT Final Report

## Executive Summary
- Testing period: April 14-25, 2026
- Participating MOAs: MBHTE, MOH, MSSD
- Total testers: 15
- Test scenarios executed: 21 (7 scenarios × 3 MOAs)
- Overall pass rate: [Percentage]

## Test Scenario Results
[Summary table of all scenarios with pass/fail/blockers]

## Bug Summary
- Total bugs reported: [Count]
- CRITICAL: [Count - all resolved]
- HIGH: [Count - resolution status]
- MEDIUM: [Count - resolution status]
- LOW: [Count - resolution status]

## Key Findings
### Strengths
- [Positive feedback and successful features]

### Areas for Improvement
- [Issues requiring attention before production]

## Recommendations
- [Go/No-Go recommendation for Phase 8 rollout]
- [Prerequisite actions before full rollout]

## Appendices
- Appendix A: Detailed test scenario results
- Appendix B: Complete bug list
- Appendix C: Tester feedback survey results
- Appendix D: Performance test results
```

---

## Roles and Responsibilities

### UAT Coordinator

**Primary Responsibility:** Overall UAT planning, execution, and reporting

**Key Tasks:**
- Schedule and facilitate all UAT meetings
- Distribute test accounts and materials
- Monitor testing progress via tracking spreadsheet
- Conduct daily check-in calls
- Triage and prioritize bugs with development team
- Resolve tester questions and blockers
- Compile daily summaries and final report
- Approve scenario sign-offs
- Make go/no-go recommendation for production rollout

**Contact:** [Name, Email, Phone]

### Development Team Lead

**Primary Responsibility:** Technical support and bug resolution

**Key Tasks:**
- Provide technical support during testing hours
- Review and prioritize reported bugs
- Assign bugs to developers
- Communicate bug resolution timelines
- Deploy fixes to staging environment
- Verify bug fixes before re-test
- Participate in daily check-ins
- Document technical issues and resolutions

**Contact:** [Name, Email, Phone]

### Pilot MOA Representatives (3 total, 1 per MOA)

**Primary Responsibility:** Coordinate testing activities within their MOA

**Key Tasks:**
- Recruit and onboard 5 testers from their MOA
- Distribute test accounts and training materials
- Coordinate tester schedules to ensure coverage
- Collect and consolidate feedback from MOA testers
- Represent MOA in daily check-in calls
- Escalate blockers to UAT coordinator
- Approve sign-off for test scenarios
- Provide feedback on BMMS usability for MOA context

**Contacts:**
- **MBHTE Representative:** [Name, Email, Phone]
- **MOH Representative:** [Name, Email, Phone]
- **MSSD Representative:** [Name, Email, Phone]

### Pilot MOA Testers (15 total, 5 per MOA)

**Primary Responsibility:** Execute test scenarios and report findings

**Key Tasks:**
- Attend UAT kickoff and training sessions
- Execute assigned test scenarios according to plan
- Record progress in tracking spreadsheet
- Report bugs using standardized template
- Participate in daily check-in calls (when available)
- Re-test resolved bugs
- Provide feedback on system usability
- Complete UAT feedback survey

**Role Distribution per MOA:**
- 1 Planning Officer (TS1, TS4, TS6)
- 1 Budget Officer (TS2, TS4, TS7)
- 1 Coordination Officer (TS3, TS6)
- 1 Department Head (Approval workflows, TS4)
- 1 MOA Administrator (Cross-functional testing, all scenarios)

### OCM Observer

**Primary Responsibility:** Test OCM-specific features and oversight capabilities

**Key Tasks:**
- Execute TS5 (OCM Dashboard)
- Verify aggregated data accuracy
- Test read-only access controls
- Validate data privacy compliance
- Provide feedback on OCM reporting needs
- Represent OCM perspective in UAT meetings

**Contact:** [Name, Email, Phone]

### Technical Support Team (On-call)

**Primary Responsibility:** Provide immediate technical assistance

**Key Tasks:**
- Respond to support requests within 30 minutes
- Troubleshoot login/access issues
- Resolve browser/device compatibility problems
- Assist with test data creation/reset
- Escalate system-level issues to development team

**Contact:** `bmms-uat-support@barmm.gov.ph` or [Support Phone]

---

## Success Criteria

### Quantitative Criteria

**Test Execution:**
- 100% of test scenarios executed by all pilot MOAs (21 total)
- 95% overall pass rate (maximum 1 failure per scenario)
- 100% of CRITICAL bugs resolved
- 90% of HIGH bugs resolved
- All test scenarios signed off by MOA representatives

**Bug Resolution:**
- CRITICAL bugs: <1 hour resolution time (average)
- HIGH bugs: <4 hours resolution time (average)
- MEDIUM bugs: <1 day resolution time (average)
- LOW bugs: <3 days resolution time (average)

**Participation:**
- 90% tester attendance at daily check-ins
- 100% completion of UAT feedback surveys
- All pilot MOAs provide written sign-off

**Performance:**
- Page load times <3 seconds (average)
- Report generation <15 seconds (average)
- System uptime >99% during UAT period

### Qualitative Criteria

**Usability:**
- Testers can complete test scenarios with minimal support
- Interface intuitive for non-technical users
- Navigation logical and consistent
- Error messages helpful and actionable

**Functionality:**
- All core workflows function as designed
- Data integrity maintained across modules
- Integration between modules seamless
- Reporting accurate and comprehensive

**Compliance:**
- Bill No. 325 budget requirements fully supported
- Data privacy controls respect Data Privacy Act 2012
- RBAC enforces organization-based data isolation
- Audit logging captures all sensitive operations

**Readiness:**
- Pilot MOAs confident in using system for real work
- No show-stopping issues identified
- OCM satisfied with oversight capabilities
- Testers recommend system for full rollout

### Go/No-Go Decision Criteria

**GO Decision (Proceed to Phase 8 Full Rollout):**
- All quantitative criteria met
- All qualitative criteria satisfactory
- All CRITICAL and HIGH bugs resolved
- All pilot MOAs provide written approval
- UAT coordinator recommends go-live
- Development team confirms production readiness

**NO-GO Decision (Delay rollout, address issues):**
- <90% overall pass rate
- CRITICAL or HIGH bugs unresolved
- Any pilot MOA withholds sign-off
- Performance issues identified (page load >5 seconds)
- Data integrity concerns raised
- Security vulnerabilities discovered

**Conditional GO (Proceed with limitations):**
- 90-94% pass rate (minor issues only)
- All HIGH bugs resolved, some MEDIUM bugs remain
- All pilot MOAs sign off with noted reservations
- Workarounds documented for known issues
- Plan to address remaining issues within 30 days post-rollout

---

## Post-UAT Activities

### After Successful UAT Completion

**Immediate (Within 1 week):**
1. **Final Bug Fixes:** Resolve any remaining MEDIUM/LOW bugs
2. **Production Deployment:** Deploy approved version to production environment
3. **Data Migration:** Migrate pilot MOA test data to production (if applicable)
4. **User Training:** Schedule training sessions for Phase 8 onboarding MOAs
5. **Documentation Updates:** Incorporate UAT feedback into user guides

**Short-term (Within 1 month):**
1. **Phase 8 Kickoff:** Begin onboarding remaining 41 MOAs
2. **Lessons Learned:** Conduct retrospective meeting with UAT team
3. **Process Improvements:** Update UAT process based on pilot learnings
4. **Expanded Monitoring:** Implement production monitoring and alerting
5. **Support Desk:** Establish ongoing support for all BMMS users

### Tester Recognition

**Acknowledgment:**
- Certificate of Participation for all UAT testers
- Recognition in BMMS release notes and documentation
- Thank-you letter from BMMS Implementation Team Lead
- Acknowledgment in OCM communications

**Continued Involvement:**
- Opportunity to serve as "BMMS Champions" in their MOAs
- Priority access to advanced training sessions
- Consultation on future BMMS enhancements
- Invitation to Phase 8 kickoff as guest speakers

---

## Appendices

### Appendix A: Glossary of Terms

- **BARMM:** Bangsamoro Autonomous Region in Muslim Mindanao
- **Bill No. 325:** Parliament Bill No. 325 - Bangsamoro Budget Process Law
- **BMMS:** Bangsamoro Ministerial Management System
- **CO:** Capital Outlay (budget category)
- **KPI:** Key Performance Indicator
- **MBHTE:** Ministry of Basic, Higher, and Technical Education
- **MOA:** Ministry, Office, or Agency
- **MOH:** Ministry of Health
- **MOOE:** Maintenance and Other Operating Expenses (budget category)
- **MSSD:** Ministry of Social Services and Development
- **OCM:** Office of the Chief Minister
- **OOBC:** Office for Other Bangsamoro Communities
- **PS:** Personnel Services (budget category)
- **RBAC:** Role-Based Access Control
- **UAT:** User Acceptance Testing

### Appendix B: Contact Information

**UAT Support Channels:**
- **Email:** bmms-uat-support@barmm.gov.ph
- **Bug Tracker:** https://staging.bmms.barmm.gov.ph/uat/bugs
- **Phone Support:** [Support phone number] (Mon-Fri, 8 AM - 5 PM)
- **Emergency Contact:** [Emergency contact for critical issues]

**Key Personnel:**
- **UAT Coordinator:** [Name, Email, Phone]
- **Development Team Lead:** [Name, Email, Phone]
- **BMMS Project Manager:** [Name, Email, Phone]
- **OCM Representative:** [Name, Email, Phone]

### Appendix C: Additional Resources

**Training Materials:**
- BMMS User Guide (PDF): [Link]
- Video Tutorials: [Link to video library]
- Quick Reference Cards: [Link to printable guides]

**Technical Documentation:**
- BMMS Architecture Overview: [Link]
- RBAC Role Definitions: [Link]
- Bill No. 325 Compliance Guide: [Link]

**System Information:**
- Staging Environment URL: https://staging.bmms.barmm.gov.ph
- Browser Requirements: Chrome 120+, Firefox 121+, Edge 120+, Safari 17+
- Recommended Screen Resolution: 1366x768 minimum

---

## Document Control

**Version History:**

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-04-14 | BMMS Implementation Team | Initial release for Phase 7 UAT |

**Approval:**

| Role | Name | Signature | Date |
|------|------|-----------|------|
| BMMS Project Manager | [Name] | _____________ | ______ |
| UAT Coordinator | [Name] | _____________ | ______ |
| Development Team Lead | [Name] | _____________ | ______ |

**Distribution:**

This document has been distributed to:
- All UAT testers (15 pilot MOA representatives)
- OCM Observer
- BMMS Implementation Team
- Development Team
- OOBC Management

---

**END OF UAT TEST PLAN**

For questions or clarifications, contact the UAT Coordinator at [Email/Phone].

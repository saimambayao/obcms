# User Guide: Integrated Project Management System

**Office for Other Bangsamoro Communities (OOBC)**
**Version:** 1.0
**Last Updated:** October 1, 2025

---

## Table of Contents

1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [Portfolio Dashboard](#portfolio-dashboard)
4. [Managing Workflows](#managing-workflows)
5. [Budget Approval Process](#budget-approval-process)
6. [Alert Management](#alert-management)
7. [Analytics and Reporting](#analytics-and-reporting)
8. [Common Tasks](#common-tasks)
9. [Troubleshooting](#troubleshooting)

---

## Introduction

The Integrated Project Management System connects the entire project lifecycle from need identification through implementation and monitoring. This system helps OOBC staff:

- Track projects from needs assessment to completion
- Manage budget approvals with automatic ceiling validation
- Monitor alerts for unfunded needs, overdue projects, and budget issues
- Generate comprehensive reports and analytics
- Coordinate with MAOs and stakeholders

### Key Features

✅ **9-Stage Workflow Management** - Track projects through need identification, validation, policy linkage, MAO coordination, budget planning, approval, implementation, monitoring, and completion

✅ **5-Stage Budget Approval** - Technical review → Budget review → Stakeholder consultation → Executive approval → Approved/Enacted

✅ **Automated Alerts** - Daily alerts for unfunded needs, overdue projects, budget ceilings, approval bottlenecks, and more

✅ **Comprehensive Analytics** - Budget allocation by sector/source/region, utilization rates, cost-effectiveness analysis

✅ **Multi-Format Reports** - Portfolio performance, budget utilization, workflow progress, cost-effectiveness (HTML/CSV)

---

## Getting Started

### Accessing the System

1. **Navigate to Portfolio Dashboard**
   - URL: `http://your-server/project-central/portfolio/`
   - Or click "Project Management Portal" in the main navigation menu

2. **Login Required**
   - All features require authentication
   - Use your OOBC staff credentials

### User Roles and Permissions

- **Project Leads** - Create and manage workflows, advance stages
- **Budget Officers** - Review and approve budgets, manage ceilings
- **Executives** - Final approval authority
- **Administrators** - Full system access via Django admin

---

## Portfolio Dashboard

The Portfolio Dashboard is your main entry point showing key metrics and recent activity.

### Key Metrics Displayed

1. **Total Budget (FY)** - Total budget allocation for current fiscal year
2. **Active Projects** - Number of ongoing projects
3. **Unfunded Needs** - High-priority needs without funding
4. **Total Beneficiaries** - Total OBC slots across all projects

### Project Pipeline

Visual representation of projects at each stage:
- **Needs Identified** - Needs from MANA assessments
- **Planning** - PPAs being developed
- **Ongoing** - Active implementation
- **Completed** - Finished projects

### Active Alerts Section

Shows top 5 unacknowledged alerts by severity:
- **Critical** - Immediate action required
- **High** - Urgent attention needed
- **Medium** - Should be addressed soon
- **Low** - For awareness

### Recent Workflows

Last 10 workflows with:
- Current stage
- Priority level
- On-track/blocked status
- Initiation date

### Quick Actions

Direct links to:
- Analytics Dashboard
- Budget Planning
- Budget Approvals
- Reports

---

## Managing Workflows

### Creating a New Workflow

1. **From Portfolio Dashboard**
   - Click "Project List" → "Create Workflow"

2. **Required Information**
   - **Primary Need** - Select from high-priority unfunded needs
   - **Project Lead** - Assign staff member
   - **Priority Level** - High/Medium/Low
   - **Estimated Budget** - Initial budget estimate
   - **Target Completion Date** - Expected completion

3. **Optional Information**
   - **Linked PPA** - If PPA already exists
   - **MAO Focal Person** - Coordinating MAO
   - **Notes** - Additional context

4. **Click "Create Workflow"**

### Viewing Workflow Details

1. **Access Workflow**
   - Click on workflow from list or dashboard
   - Shows complete workflow information and timeline

2. **Information Displayed**
   - **Overview** - Lead, MAO, dates, budget, linked PPA
   - **Stage Timeline** - Visual representation of 9 stages
   - **Stage History** - All stage transitions with notes
   - **Related Tasks** - Auto-generated and manual tasks
   - **Active Alerts** - Workflow-specific alerts
   - **Original Need** - Link back to MANA assessment

### Advancing Workflow Stages

1. **From Workflow Detail Page**
   - Click "Advance Stage" button

2. **Select Next Stage**
   - System shows only valid next stages
   - Cannot skip stages (sequential advancement)

3. **Add Notes**
   - Document reason for advancement
   - Required for approval stages

4. **Automated Actions**
   - System generates stage-specific tasks
   - Sends email notifications
   - Updates linked PPA status
   - May create alerts if issues detected

### Workflow Stages Explained

1. **Need Identification** (Starting stage)
   - Need identified from MANA assessment
   - Initial priority assessment

2. **Need Validation**
   - Verify need is legitimate and high-priority
   - Community validation
   - Technical feasibility check

3. **Policy Linkage**
   - Link need to relevant policy recommendations
   - Ensure alignment with BARMM mandates

4. **MAO Coordination**
   - Engage relevant MAO
   - Establish focal person
   - Plan coordination approach

5. **Budget Planning**
   - Develop budget estimate
   - Create or link to PPA
   - Identify funding sources

6. **Approval**
   - Initiate 5-stage budget approval
   - Technical, budget, stakeholder, executive reviews

7. **Implementation**
   - Execute approved project
   - Monitor progress
   - Update status regularly

8. **Monitoring**
   - Track outcomes
   - Beneficiary verification
   - Progress reporting

9. **Completion**
   - Final deliverables
   - Impact assessment
   - Lessons learned
   - Archive workflow

### Reporting Blockers

If a workflow is blocked:

1. **From Workflow Detail**
   - Click "Report Blocker"

2. **Describe Blocker**
   - Clear description of obstacle
   - Impact on timeline
   - Assistance needed

3. **System Actions**
   - Sets workflow to "Blocked" status
   - Creates high-severity alert
   - Notifies supervisors
   - Escalates if not resolved

---

## Budget Approval Process

### 5-Stage Approval Workflow

**Stage 1: Draft**
- PPA created but not yet submitted
- Project team refines details

**Stage 2: Technical Review**
- Technical merit assessment
- Alignment with OOBC objectives
- Required: Title, category, sector, lead organization

**Stage 3: Budget Review**
- Financial analysis
- Budget ceiling validation
- Cost-benefit assessment
- Required: Budget allocation, funding source, appropriation class

**Stage 4: Stakeholder Consultation**
- Community engagement
- MAO consultation
- Partnership verification

**Stage 5: Executive Approval**
- Chief Minister review
- Final authorization
- Budget enactment

**Final: Approved/Enacted**
- Budget officially allocated
- Implementation can proceed

### Budget Approval Dashboard

Access via: Portfolio Dashboard → "Budget Approvals"

**Pipeline View:**
- See PPAs at each approval stage
- Stage counts and pending approvals
- Click PPA to review details

**Actions Available:**
- **Review** - View PPA details and approval history
- **Approve** - Advance to next stage
- **Reject** - Return to draft with reason

### Reviewing a PPA for Approval

1. **Access Review Page**
   - From Budget Approval Dashboard
   - Click PPA title

2. **Information Shown**
   - Complete PPA details
   - Budget ceiling compliance status
   - Approval history
   - Related workflows
   - Current stage requirements

3. **Budget Ceiling Validation**
   - **Green checkmark** - Within all ceilings
   - **Red X** - Exceeds one or more ceilings
   - Details of ceiling breaches shown

4. **Approval Decision**
   - **Approve** - Advance to next stage with notes
   - **Reject** - Return to draft with reason

### Budget Ceiling Management

**Purpose:** Ensure budget allocations stay within approved limits

**Types of Ceilings:**
- **Total Budget** - Overall fiscal year limit
- **Sector Ceilings** - Limits per sector (education, health, etc.)
- **Funding Source Ceilings** - Limits per source (GAA, local funds)
- **Regional Ceilings** - Limits per region

**Enforcement Levels:**
- **Hard Limit** - Cannot exceed (approval blocked)
- **Soft Limit** - Warning shown but can proceed with justification
- **Warning Only** - Informational notice

**Monitoring:**
- Real-time utilization tracking
- Alerts at 90% threshold
- Monthly ceiling reports

---

## Alert Management

### Accessing Alerts

- **From Portfolio Dashboard** - Top 5 unacknowledged alerts
- **From Alert List** - All alerts with filters
- **URL:** `/project-central/alerts/`

### Alert Types (11 Types)

1. **Unfunded Needs** - High-priority needs without PPAs
2. **Overdue PPAs** - Projects past target completion date
3. **Budget Ceiling** - Ceilings approaching/exceeding limit
4. **Approval Bottleneck** - PPAs stuck in approval >30 days
5. **Disbursement Delay** - Low disbursement rates
6. **Underspending** - Budget not being utilized
7. **Overspending** - Budget overruns
8. **Workflow Blocked** - Workflows with blockers
9. **Deadline Approaching** - Deadlines within 7 days
10. **Policy Lagging** - Low policy implementation rates
11. **Pending Reports** - Quarterly reports overdue

### Alert Severity Levels

- **Critical** - Immediate action required (red)
- **High** - Urgent attention (orange)
- **Medium** - Address soon (yellow)
- **Low** - For awareness (blue)
- **Info** - Informational (gray)

### Filtering Alerts

**Available Filters:**
- **Alert Type** - Filter by specific alert type
- **Severity** - Filter by severity level
- **Status** - Active only or all alerts
- **Acknowledged** - Show only unacknowledged

### Acknowledging Alerts

1. **From Alert List**
   - Click "Acknowledge" button

2. **Add Notes** (Optional)
   - Document action taken
   - Resolution approach

3. **Submit**
   - Alert marked as acknowledged
   - Remains in system for reference

### Automated Alert Resolution

System automatically deactivates alerts when:
- Unfunded need gets linked to PPA
- Overdue PPA is completed
- Budget ceiling drops below threshold
- Approval bottleneck is cleared
- Workflow blocker is removed

---

## Analytics and Reporting

### M&E Analytics Dashboard

Access via: Portfolio Dashboard → "Analytics Dashboard"

**Key Metrics:**
- Total budget by fiscal year
- Disbursement rate
- Active workflows
- Cost per beneficiary

**Visualizations (Chart.js):**
1. **Budget by Sector** - Pie chart showing allocation
2. **Budget by Source** - Bar chart of funding sources
3. **Utilization Rate** - Doughnut gauge showing disbursement
4. **Workflow Performance** - Bar chart of on-track/blocked

**Data Tables:**
- Sector budget breakdown with utilization
- Budget ceiling utilization with color-coded alerts

**Fiscal Year Selector:**
- Dropdown to view different years
- Updates all charts and tables

### Sector Analytics

View detailed analytics for specific sectors:
- Access from main analytics dashboard
- Sector-specific budget allocation
- Cost-effectiveness for sector
- List of PPAs in sector

### Geographic Analytics

Budget distribution by region:
- Total budget per region
- Project count per region
- Average budget per region

### Policy Analytics

Track implementation of policy recommendations:
- Needs linked to policy
- Workflows advancing policy
- Budget allocated to policy
- Implementation progress

### Report Generation

#### Available Reports

1. **Portfolio Performance Report**
   - Budget allocation (sector/source/region)
   - Utilization rates
   - Cost-effectiveness
   - Workflow performance
   - Alert summary

2. **Budget Utilization Report**
   - PPA-level details
   - Obligation and disbursement rates
   - Ceiling utilization
   - Sector filtering available

3. **Workflow Progress Report**
   - Workflow status by stage
   - On-track/blocked/overdue
   - Project lead assignments
   - Estimated budgets

4. **Cost-Effectiveness Report**
   - Cost per beneficiary
   - Sector comparisons
   - Min/max/average analysis

#### Generating Reports

1. **Access Report List**
   - Portfolio Dashboard → "Reports"

2. **Select Report Type**
   - Choose from 4 report types

3. **Set Parameters**
   - Fiscal year
   - Sector (if applicable)
   - Output format (HTML or CSV)

4. **Generate**
   - **HTML** - View in browser
   - **CSV** - Download for Excel

#### Scheduled Reports

Automated reports sent via email:
- **Weekly Workflow Report** - Every Monday 9:00 AM
- **Monthly Budget Report** - 1st of month 10:00 AM

---

## Common Tasks

### Task: Fund a High-Priority Need

1. Check Alert List for "Unfunded Needs" alerts
2. Click alert to view need details
3. Click "Create Workflow" from need page
4. Fill in workflow details (lead, priority, budget)
5. Create workflow
6. Advance to "Budget Planning" stage
7. Create or link PPA
8. Initiate budget approval
9. Workflow automatically advances as budget is approved

### Task: Approve a Budget

1. Go to Budget Approval Dashboard
2. Identify PPA in your stage (Technical/Budget/Stakeholder/Executive)
3. Click "Review" to see details
4. Check ceiling compliance (green = good)
5. Review approval history
6. Click "Approve" and add notes
7. PPA advances to next stage

### Task: Address a Blocked Workflow

1. Check Alert List for "Workflow Blocked" alerts
2. Click alert to view workflow
3. Read blocker description
4. Take corrective action
5. Update workflow notes with resolution
6. Click "Clear Blocker"
7. System deactivates alert automatically

### Task: Export Budget Report

1. Go to Reports page
2. Select "Budget Utilization Report"
3. Choose fiscal year
4. Select sector (optional)
5. Choose "CSV" format
6. Click "Generate"
7. Download CSV file
8. Open in Excel for analysis

### Task: Monitor Budget Ceilings

1. Go to M&E Analytics Dashboard
2. Scroll to "Budget Ceiling Utilization" table
3. Check utilization percentages
   - Green badge = Good (<75%)
   - Yellow badge = Warning (75-90%)
   - Red badge = Critical (>90%)
4. Click ceiling name for details
5. Review PPAs contributing to utilization

---

## Troubleshooting

### Issue: Cannot Advance Workflow Stage

**Possible Causes:**
- Stage requirements not met
- Missing required fields (e.g., PPA for budget planning)
- Workflow is blocked

**Solution:**
1. Check error message shown
2. Complete required information
3. If blocked, resolve blocker first
4. Try advancing again

### Issue: Budget Approval Rejected

**Possible Causes:**
- Budget exceeds ceiling (hard limit)
- Missing required fields for stage
- Technical/financial issues identified

**Solution:**
1. Review rejection reason in approval history
2. Address identified issues
3. Update PPA details
4. Resubmit for approval

### Issue: Alerts Not Appearing

**Possible Causes:**
- Alerts already acknowledged
- Filter hiding alerts
- Daily generation not yet run

**Solution:**
1. Check filter settings (show all alerts)
2. Check acknowledgment status
3. Wait for 6:00 AM daily generation
4. Contact administrator if persists

### Issue: Chart Not Displaying

**Possible Causes:**
- No data for selected fiscal year
- JavaScript error
- Browser compatibility

**Solution:**
1. Select different fiscal year
2. Refresh page
3. Try different browser
4. Check browser console for errors

### Issue: CSV Export Empty

**Possible Causes:**
- No data matching filters
- Query timeout

**Solution:**
1. Broaden filter criteria
2. Select different fiscal year
3. Try smaller date range
4. Contact administrator for large exports

---

## Getting Help

### Documentation

- **User Guide** (this document)
- **Admin Guide** - `/docs/admin-guide/`
- **Developer Documentation** - `/docs/development/`

### Support

- **Email:** oobc-support@barmm.gov.ph
- **Help Desk:** Submit ticket via system
- **Training:** Monthly refresher sessions

### Training Resources

- **Video Tutorials** - Available in system
- **Quick Start Guide** - `/docs/quick-start/`
- **FAQs** - `/docs/faq/`

---

## Keyboard Shortcuts

- **Alt + D** - Go to Dashboard
- **Alt + W** - Workflow List
- **Alt + A** - Alert List
- **Alt + B** - Budget Approvals
- **Alt + R** - Reports

---

**Document Version:** 1.0
**Last Updated:** October 1, 2025
**For:** OOBC Staff
**System:** Integrated Project Management System

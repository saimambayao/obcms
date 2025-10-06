# MOA WorkItem Tracking User Guide

**Document Type**: User Guide
**Target Audience**: MOA Program/Project Managers and Staff
**System Module**: Monitoring & Evaluation (M&E)
**Last Updated**: October 6, 2025

---

## Table of Contents

1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [Enabling WorkItem Tracking](#enabling-workitem-tracking)
4. [Understanding Work Breakdown Structure](#understanding-work-breakdown-structure)
5. [Creating and Managing Work Items](#creating-and-managing-work-items)
6. [Tracking Progress](#tracking-progress)
7. [Budget Management](#budget-management)
8. [Viewing Reports](#viewing-reports)
9. [Troubleshooting](#troubleshooting)
10. [FAQ](#faq)

---

## Introduction

### What is WorkItem Tracking?

WorkItem tracking is a powerful project management feature that helps MOA staff break down Programs, Projects, and Activities (PPAs) into manageable tasks and track execution progress in detail.

**Key Benefits:**
- Break down large PPAs into actionable work items
- Track progress at multiple levels (project → activity → task)
- Monitor budget allocation and expenditure
- Auto-sync progress back to PPA dashboard
- Generate detailed execution reports for MFBM and BPDA

**When to Use WorkItem Tracking:**
- ✅ Complex PPAs with multiple phases or activities
- ✅ PPAs requiring detailed budget breakdown
- ✅ PPAs with multiple implementing teams
- ✅ PPAs needing granular progress monitoring
- ❌ Simple, single-activity PPAs (overhead not worth it)

---

## Getting Started

### Prerequisites

Before enabling WorkItem tracking, ensure:
1. Your PPA is fully created in the M&E system
2. PPA has a budget allocation set (required for budget distribution)
3. You have "Editor" or "Admin" role for the PPA
4. PPA status is "Planning" or "Ongoing" (cannot enable for completed PPAs)

### Access WorkItem Tracking

**Navigation Path:**
```
Dashboard → Monitoring & Evaluation → MOA PPAs → [Select Your PPA] → "Enable WorkItem Tracking" button
```

**Screenshot Placeholder:**
> *Image showing the MOA PPA detail page with "Enable WorkItem Tracking" button highlighted*

---

## Enabling WorkItem Tracking

### Step-by-Step Process

#### Step 1: Navigate to Your PPA

1. Log in to OBCMS
2. Click "Monitoring & Evaluation" in the main navigation
3. Select "MOA PPAs" from the dropdown
4. Find your PPA in the list (use search if needed)
5. Click the PPA title to open the detail page

**Screenshot Placeholder:**
> *Image showing MOA PPA list with search functionality*

#### Step 2: Enable WorkItem Tracking

On the PPA detail page, you'll see a button labeled **"Enable WorkItem Tracking"**.

1. Click the "Enable WorkItem Tracking" button
2. A modal dialog will appear with configuration options

**Screenshot Placeholder:**
> *Image showing the "Enable WorkItem Tracking" modal dialog*

#### Step 3: Choose Structure Template

The system offers three pre-built structure templates:

| Template | Best For | Structure |
|----------|----------|-----------|
| **Program Template** | Large multi-year programs | Program → Sub-Programs → Activities → Tasks |
| **Activity Template** | Standard projects | Project → Activities → Tasks |
| **Minimal Template** | Simple projects | Project → Tasks |

**Example: Activity Template Structure**
```
Livelihood Training Program (Project)
├── Activity 1: Needs Assessment Workshop
│   ├── Task: Prepare training materials
│   ├── Task: Send participant invitations
│   └── Task: Arrange venue and logistics
├── Activity 2: Skills Training Sessions
│   ├── Task: Conduct Module 1 training
│   ├── Task: Conduct Module 2 training
│   └── Task: Post-training evaluation
└── Activity 3: Follow-up and Monitoring
    ├── Task: 30-day follow-up survey
    └── Task: Final impact assessment
```

**Recommendation:** Use **Activity Template** for most PPAs unless you have specific needs.

#### Step 4: Configure Budget Distribution

Choose how budget should be distributed across work items:

| Policy | Description | When to Use |
|--------|-------------|-------------|
| **Equal Distribution** | Divides budget equally across activities | Activities have similar costs |
| **Weighted Distribution** | Distributes based on expected effort | Activities have varying complexity |
| **Manual Allocation** | You set budget for each work item | You know exact budget per activity |

**MFBM Compliance Note:**
Total work item budgets MUST equal the PPA budget allocation. The system will validate this automatically.

**Screenshot Placeholder:**
> *Image showing budget distribution policy options*

#### Step 5: Configure Auto-Sync

Enable automatic synchronization between work items and PPA dashboard:

- **Auto-sync Progress** ✅ (Recommended: ON)
  - Work item completion automatically updates PPA progress percentage
  - Keeps stakeholders informed without manual updates

- **Auto-sync Status** ✅ (Recommended: ON)
  - Work item status changes update PPA status (e.g., "At Risk" → PPA flagged)
  - Helps BPDA identify issues early

**Best Practice:** Keep both auto-sync options enabled unless you have specific workflow requirements.

#### Step 6: Create Execution Project

1. Review your selections
2. Click **"Create Execution Project"**
3. Wait for the system to generate the work breakdown structure (5-10 seconds)
4. You'll be redirected to the WorkItem management interface

**Screenshot Placeholder:**
> *Image showing successful execution project creation confirmation*

---

## Understanding Work Breakdown Structure

### Hierarchy Levels

The WorkItem system uses a hierarchical structure (tree):

```
Level 1: Project (Root)
    ├── Level 2: Sub-Project or Activity
    │       ├── Level 3: Sub-Activity or Task
    │       │       └── Level 4: Subtask
    │       └── Level 3: Task
    └── Level 2: Activity
            └── Level 3: Task
```

### Work Item Types

| Type | Description | Can Contain | Examples |
|------|-------------|-------------|----------|
| **Project** | Top-level execution plan | Sub-Projects, Activities, Tasks | "Livelihood Training Program" |
| **Sub-Project** | Major program component | Activities, Tasks | "Phase 1: Skills Development" |
| **Activity** | Specific event or milestone | Sub-Activities, Tasks | "Training Workshop Day 1" |
| **Sub-Activity** | Breakdown of activity | Tasks | "Morning Session: Introduction" |
| **Task** | Actionable work unit | Subtasks | "Prepare PowerPoint presentation" |
| **Subtask** | Smallest work unit | None | "Review slides for typos" |

### Visual Indicators

The system uses color coding and icons to help you quickly understand status:

**Status Colors:**
- 🔵 **Blue border**: In Progress
- 🟢 **Green border**: Completed
- 🟡 **Amber border**: At Risk
- 🔴 **Red border**: Blocked
- ⚪ **Gray border**: Not Started
- ⚫ **Dark Gray border**: Cancelled

**Priority Badges:**
- 🔴 **Critical**: Red badge
- 🟠 **Urgent**: Orange badge
- 🟡 **High**: Yellow badge
- 🔵 **Medium**: Blue badge (default)
- 🟢 **Low**: Green badge

**Screenshot Placeholder:**
> *Image showing work items with different status colors and priority badges*

---

## Creating and Managing Work Items

### Adding New Work Items

#### Method 1: Using the "Add Work Item" Button

1. Navigate to your execution project dashboard
2. Find the parent work item (e.g., an Activity)
3. Click the **"+ Add Child"** button
4. Fill in the work item form:
   - **Title** (required): Clear, actionable title
   - **Work Type** (required): Task, Subtask, Activity, etc.
   - **Description**: Detailed explanation of work
   - **Priority**: Low, Medium, High, Urgent, Critical
   - **Start Date**: When work begins
   - **Due Date**: Deadline
   - **Assignees**: Team members responsible
   - **Allocated Budget**: Budget for this work item (optional)

5. Click **"Create Work Item"**

**Screenshot Placeholder:**
> *Image showing the "Add Work Item" form with all fields labeled*

#### Method 2: Duplicate Existing Work Item

If you have similar tasks, you can duplicate:

1. Find the work item to duplicate
2. Click the **"⋮"** menu (three dots)
3. Select **"Duplicate"**
4. Edit the duplicated work item as needed
5. Save

**Screenshot Placeholder:**
> *Image showing the context menu with "Duplicate" option*

### Editing Work Items

1. Click the work item title or the **"Edit"** button
2. Update fields as needed
3. Click **"Save Changes"**

**Important:** Changes to dates or budget may affect parent work items if auto-calculation is enabled.

### Moving Work Items

You can reorganize the hierarchy by dragging and dropping:

1. Click and hold the work item card
2. Drag to the new parent
3. Release to drop

**Validation:** The system prevents invalid moves (e.g., you cannot put a Project inside a Task).

**Screenshot Placeholder:**
> *Animated GIF showing drag-and-drop work item reorganization*

### Deleting Work Items

⚠️ **Warning:** Deleting a parent work item will delete ALL child work items.

1. Click the work item's **"⋮"** menu
2. Select **"Delete"**
3. Confirm deletion in the modal dialog
4. Review the list of child items that will be deleted
5. Type "DELETE" to confirm (safety measure)
6. Click **"Confirm Deletion"**

**Screenshot Placeholder:**
> *Image showing the delete confirmation dialog with child items listed*

---

## Tracking Progress

### Progress Calculation Methods

The system supports two progress calculation modes:

#### Auto-Calculate Progress (Recommended)

**How it works:**
- Progress = (Completed Children / Total Children) × 100%
- Automatically updates when child work items are completed
- Propagates up the hierarchy (task → activity → project)

**Example:**
```
Activity: Training Workshop (Auto-calculated: 67%)
├── Task: Prepare materials ✅ (Completed)
├── Task: Send invitations ✅ (Completed)
└── Task: Arrange venue 🔵 (In Progress)

Progress = 2 completed / 3 total = 67%
```

**Best for:** Standard workflows where completion is binary (done or not done)

#### Manual Progress Entry

**How it works:**
- You set progress percentage manually (0-100%)
- Useful for tasks with gradual completion
- Does not auto-calculate from children

**Example:**
```
Task: Write training manual (Manual: 75%)
├── Subtask: Draft outline ✅ (100%)
├── Subtask: Write chapters 🔵 (50%)
└── Subtask: Review and edit ⚪ (0%)

Manual progress = 75% (your estimate, not calculated)
```

**Best for:** Tasks with measurable incremental progress (writing, development, etc.)

**Toggle Setting:**
- Edit work item → Check/Uncheck **"Auto-calculate progress from children"**

**Screenshot Placeholder:**
> *Image showing the auto-calculate progress toggle in edit form*

### Updating Work Item Status

Status updates trigger important workflows:

1. Click the work item
2. Select new status from dropdown:
   - **Not Started**: Work hasn't begun
   - **In Progress**: Actively working on it
   - **At Risk**: Behind schedule or facing issues
   - **Blocked**: Cannot proceed due to blocker
   - **Completed**: Work finished successfully
   - **Cancelled**: Work no longer needed

3. Add a status comment (required for "At Risk" and "Blocked")
4. Click **"Update Status"**

**Auto-Sync Behavior:**
- If PPA has auto-sync enabled, status changes propagate to PPA dashboard
- "At Risk" or "Blocked" status flags the PPA for stakeholder attention
- Completing all top-level activities marks PPA as "Completed"

**Screenshot Placeholder:**
> *Image showing status dropdown with comment field for "At Risk" status*

### Adding Progress Notes

Document progress with detailed notes:

1. Open work item detail page
2. Scroll to **"Progress Updates"** section
3. Click **"Add Update"**
4. Enter:
   - **Update Type**: Progress, Issue, Milestone, General
   - **Notes**: Detailed description
   - **Attachments**: Upload supporting files (optional)
   - **Next Steps**: What needs to happen next
5. Click **"Save Update"**

**Screenshot Placeholder:**
> *Image showing the progress update form with attachments*

---

## Budget Management

### Allocating Budget to Work Items

#### Initial Budget Setup

When you enable WorkItem tracking, you choose a budget distribution policy:

**Equal Distribution Example:**
```
PPA Budget: ₱1,000,000.00
3 Activities created

Each activity gets: ₱1,000,000 ÷ 3 = ₱333,333.33
```

**Weighted Distribution Example:**
```
PPA Budget: ₱1,000,000.00
Activity 1 (weight: 50%) = ₱500,000.00
Activity 2 (weight: 30%) = ₱300,000.00
Activity 3 (weight: 20%) = ₱200,000.00
```

#### Adjusting Budget Allocations

You can manually adjust budget allocations:

1. Edit the work item
2. Update **"Allocated Budget"** field
3. Click **"Save"**

**Validation:**
- System checks that total child budgets = parent budget
- Error message if budget rollup doesn't match
- Must fix budget distribution before saving

**Example Validation Error:**
```
❌ Budget rollup mismatch: Parent budget is ₱1,000,000.00,
   but children budgets sum to ₱1,050,000.00 (variance: ₱50,000.00)
```

**Screenshot Placeholder:**
> *Image showing budget validation error with corrective action*

### Recording Actual Expenditures

Track actual spending against allocated budget:

1. Open work item detail page
2. Scroll to **"Budget Tracking"** section
3. Click **"Record Expenditure"**
4. Enter:
   - **Amount**: Actual expenditure (₱)
   - **Date**: Transaction date
   - **Description**: What was purchased/paid for
   - **Receipt/Reference**: Upload receipt or enter reference number
5. Click **"Save Expenditure"**

**Budget Status Indicators:**
- 🟢 **Under Budget**: Actual < Allocated
- 🟡 **At Budget**: Actual = Allocated (90-100%)
- 🔴 **Over Budget**: Actual > Allocated

**Screenshot Placeholder:**
> *Image showing expenditure recording form with receipt upload*

### Viewing Budget Reports

Generate budget execution reports:

1. Navigate to execution project dashboard
2. Click **"Reports"** tab
3. Select **"Budget Execution Report"**
4. Choose reporting level:
   - **Project-level**: Overall budget status
   - **Activity-level**: Budget per activity
   - **Detailed**: All work items with budgets

5. Click **"Generate Report"**
6. Export as Excel or PDF

**Report Includes:**
- Budget allocation vs. actual expenditure
- Variance analysis (over/under budget)
- Budget utilization percentage
- Spending trends over time

**Screenshot Placeholder:**
> *Image showing sample budget execution report with variance analysis*

---

## Viewing Reports

### Available Report Types

The WorkItem tracking system generates several report types for different stakeholders:

#### 1. Progress Report (For MOA Management)

**Purpose**: Track overall execution progress and identify bottlenecks

**Contents:**
- Overall project completion percentage
- Progress by activity
- Tasks at risk or blocked
- Upcoming milestones
- Team performance metrics

**How to Generate:**
```
Execution Project → Reports → Progress Report → Generate
```

**Screenshot Placeholder:**
> *Image showing progress report with gantt chart and status breakdown*

#### 2. Budget Report (For MFBM)

**Purpose**: Monitor budget utilization and financial compliance

**Contents:**
- Budget allocation tree (hierarchical view)
- Actual expenditure by work item
- Variance analysis (budget vs. actual)
- Budget utilization rate
- Over/under budget items flagged

**How to Generate:**
```
Execution Project → Reports → Budget Report → Generate
```

**Export Formats:** Excel (recommended for MFBM), PDF

**Screenshot Placeholder:**
> *Image showing budget report with allocation tree and variance table*

#### 3. Development Outcome Report (For BPDA)

**Purpose**: Track alignment with Bangsamoro Development Plan (BDP)

**Contents:**
- BDP outcome indicators tracked
- Beneficiary reach (OBC-specific metrics)
- Geographic coverage analysis
- Development impact assessment
- Alignment score with BDP priorities

**How to Generate:**
```
Execution Project → Reports → Development Report → Generate
```

**Screenshot Placeholder:**
> *Image showing development report with BDP alignment metrics*

#### 4. Team Performance Report (For MOA HR)

**Purpose**: Evaluate team and individual performance

**Contents:**
- Tasks completed per team member
- On-time completion rate
- Average task duration
- Workload distribution
- Performance trends

**How to Generate:**
```
Execution Project → Reports → Team Performance → Generate
```

**Screenshot Placeholder:**
> *Image showing team performance dashboard with completion metrics*

### Scheduling Automated Reports

Set up recurring reports for stakeholders:

1. Navigate to **"Reports"** tab
2. Click **"Schedule Report"**
3. Configure:
   - **Report Type**: Choose from available reports
   - **Frequency**: Weekly, Monthly, Quarterly
   - **Recipients**: Email addresses (comma-separated)
   - **Format**: Excel or PDF
4. Click **"Save Schedule"**

**Example Configuration:**
```
Report: Budget Execution Report
Frequency: Monthly (1st of every month)
Recipients: mfbm-budget@barmm.gov.ph, moa-pmo@barmm.gov.ph
Format: Excel
```

**Screenshot Placeholder:**
> *Image showing automated report scheduling form*

---

## Troubleshooting

### Common Issues and Solutions

#### Issue 1: "Cannot Enable WorkItem Tracking" Error

**Symptoms:**
- Button is grayed out or shows error when clicked

**Possible Causes:**
- PPA status is "Completed" or "Cancelled"
- PPA has no budget allocation set
- User lacks "Editor" or "Admin" role

**Solution:**
1. Check PPA status (must be "Planning" or "Ongoing")
2. Verify budget allocation is set (M&E → Edit PPA → Budget section)
3. Contact system admin to verify your role permissions

---

#### Issue 2: "Budget Rollup Mismatch" Error

**Symptoms:**
- Cannot save work item changes
- Error message about budget variance

**Cause:**
- Child work item budgets don't sum to parent budget

**Solution:**
1. Calculate total child budgets manually
2. Adjust individual child budgets to match parent
3. Or adjust parent budget to match child sum
4. Ensure variance is less than ₱0.01 (rounding tolerance)

**Example Fix:**
```
Parent Activity Budget: ₱500,000.00
Child Task 1: ₱200,000.00
Child Task 2: ₱150,000.00
Child Task 3: ₱150,000.00
Total: ₱500,000.00 ✅ (matches parent)
```

---

#### Issue 3: Progress Not Syncing to PPA

**Symptoms:**
- Work items show progress, but PPA dashboard shows 0%

**Possible Causes:**
- Auto-sync progress is disabled
- Execution project is not linked to PPA
- Celery worker is not running (technical issue)

**Solution:**
1. Check auto-sync setting:
   ```
   PPA Detail → WorkItem Settings → Auto-sync Progress (should be ✅)
   ```
2. Verify execution project link:
   ```
   PPA Detail → Execution Project section (should show linked project)
   ```
3. If still not working, contact BICTO support (may be technical issue)

---

#### Issue 4: Cannot Delete Work Item

**Symptoms:**
- Delete button is grayed out
- Error message when attempting to delete

**Possible Causes:**
- Work item has child items
- Work item is linked to other system objects (assessments, policies)
- User lacks delete permissions

**Solution:**
1. First delete all child work items (bottom-up approach)
2. Or use **"Delete with Children"** option (⚠️ deletes entire subtree)
3. Check for linked objects and unlink them first
4. Contact admin to verify your delete permissions

---

#### Issue 5: Reports Show Incorrect Data

**Symptoms:**
- Budget totals don't match
- Progress percentages seem wrong
- Missing work items in report

**Possible Causes:**
- Report cache is outdated
- Filters are applied (hiding some data)
- Data sync issue

**Solution:**
1. Click **"Refresh Data"** button on report page
2. Clear all filters and regenerate report
3. Check report date range (may be excluding recent data)
4. Export raw data to Excel and verify calculations manually
5. If still incorrect, report as bug to BICTO

---

### Getting Help

**Support Channels:**

1. **In-App Help**: Click the **"?"** icon in top-right corner
2. **Email Support**: bicto-support@oobc.barmm.gov.ph
3. **Phone**: +63 (XX) XXXX-XXXX (Office hours: 8AM-5PM)
4. **Knowledge Base**: https://docs.obcms.oobc.barmm.gov.ph

**When Reporting Issues:**
- Include PPA title and ID
- Screenshot of error message
- Steps you took before the error
- Your role and email address

---

## FAQ

### General Questions

**Q1: Do I need to enable WorkItem tracking for every PPA?**

A: No. Only enable it for complex PPAs that need detailed breakdown and tracking. Simple, single-activity PPAs don't need this overhead.

---

**Q2: Can I disable WorkItem tracking after enabling it?**

A: Yes, but with caution. Disabling will NOT delete work items, but they will become inactive. Progress will stop syncing to PPA. Contact BICTO before disabling.

---

**Q3: Who can see the work items I create?**

A: Visibility depends on PPA permissions:
- **Public PPAs**: Anyone with OBCMS access can view (read-only)
- **Restricted PPAs**: Only team members with "Viewer" or higher role
- **Editing**: Only "Editor" or "Admin" role can modify work items

---

### Budget Questions

**Q4: What happens if I exceed the allocated budget?**

A: The system will flag it with a red warning, but won't block you. MFBM will receive a notification. You should:
1. Document the reason for overrun in budget notes
2. Request budget adjustment from MFBM
3. Update PPA budget allocation if approved

---

**Q5: Can I transfer budget between work items?**

A: Yes, but you must maintain the total:
1. Decrease budget from Work Item A
2. Increase budget for Work Item B by same amount
3. Save changes
4. System validates that total remains the same

---

**Q6: How do I handle budget for work items added later?**

A: Two approaches:
1. **Re-distribute**: Reduce other work items to free up budget
2. **Increase PPA budget**: Request budget increase from MFBM first, then allocate to new work item

---

### Progress Tracking Questions

**Q7: What's the difference between "Completed" and "Cancelled"?**

A:
- **Completed**: Work finished successfully → counts toward progress
- **Cancelled**: Work abandoned/no longer needed → doesn't count toward progress

Example: If you have 5 tasks, complete 3, and cancel 2:
- Progress = 3 completed / 3 remaining = 100% ✅
- Cancelled tasks are excluded from calculation

---

**Q8: Can I reopen a completed work item?**

A: Yes:
1. Open the completed work item
2. Change status back to "In Progress"
3. Progress percentage will automatically adjust
4. Add a note explaining why it was reopened

---

**Q9: How often does progress sync to the PPA dashboard?**

A: Real-time (within 5 seconds) if auto-sync is enabled. The system uses signals to propagate changes immediately.

---

### Team Collaboration Questions

**Q10: Can multiple people work on the same work item?**

A: Yes. You can assign multiple team members:
1. Edit work item
2. In **"Assignees"** field, select multiple users
3. Save
4. All assignees receive notifications for status changes

---

**Q11: How do I hand over a work item to another team member?**

A:
1. Edit work item
2. Remove yourself from **"Assignees"**
3. Add the new assignee
4. Add a comment explaining the handover
5. Save (new assignee receives notification)

---

**Q12: Can I see what my team members are working on?**

A: Yes, use the Team Dashboard:
```
Execution Project → Team View → Filter by Team Member
```

Shows all work items assigned to each team member with status and deadlines.

---

### Reporting Questions

**Q13: Can I customize reports?**

A: Limited customization available:
- Filter by date range, status, priority
- Choose which columns to include
- Export to Excel for further customization

For custom reports, contact BICTO with requirements.

---

**Q14: How long are reports stored?**

A: Generated reports are stored for 90 days. Download and save important reports locally.

---

**Q15: Can I share reports with external stakeholders?**

A: Yes:
1. Generate report
2. Export as PDF
3. Download and share via email

⚠️ **Security Note**: Ensure reports don't contain sensitive information before sharing externally.

---

## Appendix: Keyboard Shortcuts

Speed up your workflow with keyboard shortcuts:

| Shortcut | Action |
|----------|--------|
| `Ctrl + N` | Create new work item |
| `Ctrl + E` | Edit selected work item |
| `Ctrl + S` | Save work item |
| `Ctrl + D` | Duplicate work item |
| `Delete` | Delete selected work item |
| `Ctrl + F` | Search work items |
| `Ctrl + P` | Print/Export current view |
| `Esc` | Close modal dialog |
| `Arrow Keys` | Navigate work items |
| `Enter` | Open selected work item |

---

## Appendix: Status Change Workflows

Visual guide to status transitions:

```
Not Started → In Progress → Completed ✅

Not Started → Cancelled ❌

In Progress → At Risk → In Progress
              ↓
            Blocked → In Progress
              ↓
            Cancelled ❌

In Progress → Completed ✅
```

**Rules:**
- Cannot go from "Completed" to "Not Started" (must go through "In Progress")
- "Cancelled" is terminal (can only reopen by changing to "Not Started")
- "At Risk" and "Blocked" are temporary states (must resolve to "In Progress" or "Cancelled")

---

## Document Revision History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | 2025-10-06 | Initial user guide created | BICTO Documentation Team |

---

**For technical support or questions about this guide, contact:**
BICTO Support Team
Email: bicto-support@oobc.barmm.gov.ph
Phone: +63 (XX) XXXX-XXXX

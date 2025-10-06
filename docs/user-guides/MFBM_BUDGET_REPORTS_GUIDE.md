# MFBM Budget Reports User Guide

**Document Type**: User Guide
**Target Audience**: MFBM Budget Analysts and Finance Officers
**System Module**: Monitoring & Evaluation (M&E) - WorkItem Integration
**Last Updated**: October 6, 2025

---

## Table of Contents

1. [Introduction](#introduction)
2. [Accessing Budget Reports](#accessing-budget-reports)
3. [Budget Allocation Tree](#budget-allocation-tree)
4. [Budget Execution Report](#budget-execution-report)
5. [Variance Analysis](#variance-analysis)
6. [Budget Distribution Management](#budget-distribution-management)
7. [Excel Report Generation](#excel-report-generation)
8. [Troubleshooting](#troubleshooting)
9. [FAQ](#faq)

---

## Introduction

### Purpose of Budget Reports

The WorkItem Integration system provides comprehensive budget tracking and reporting capabilities specifically designed to meet MFBM (Ministry of Finance, Budget and Management) requirements for:

- **Budget Allocation Tracking**: Monitor how PPA budgets are distributed across work items
- **Expenditure Monitoring**: Track actual expenditures against allocations
- **Variance Analysis**: Identify over/under budget situations
- **Compliance Reporting**: Ensure budget distributions follow BARMM financial regulations
- **Transparency**: Provide clear audit trails for budget decisions

### Report Types

| Report Type | Purpose | Frequency | Format |
|-------------|---------|-----------|--------|
| **Budget Allocation Tree** | Visualize hierarchical budget distribution | On-demand | Web/Excel |
| **Budget Execution Report** | Track budget utilization and variance | Monthly | Excel/PDF |
| **Variance Analysis** | Identify budget overruns/underruns | Monthly | Excel |
| **Budget Summary Dashboard** | High-level budget overview | Real-time | Web |

---

## Accessing Budget Reports

### Navigation Path

**For Specific PPA:**
```
Dashboard → Monitoring & Evaluation → MOA PPAs → [Select PPA] → Reports Tab → Budget Reports
```

**For All PPAs (System-wide):**
```
Dashboard → Reports → Budget Reports → Filter by Date Range/MOA
```

### Required Permissions

To access budget reports, you must have:
- **MFBM Budget Analyst** role, OR
- **System Administrator** role, OR
- **PPA Editor** role (limited to own PPAs)

**Screenshot Placeholder:**
> *Image showing Reports tab navigation with Budget Reports section*

---

## Budget Allocation Tree

### What is the Budget Allocation Tree?

The Budget Allocation Tree is a hierarchical visualization showing how a PPA's total budget is distributed across all work items (projects, activities, tasks).

**Example Structure:**
```
Livelihood Training Program (₱5,000,000.00)
├── Activity 1: Needs Assessment (₱500,000.00)
│   ├── Task: Field surveys (₱300,000.00)
│   └── Task: Data analysis (₱200,000.00)
├── Activity 2: Skills Training (₱3,500,000.00)
│   ├── Task: Training materials (₱500,000.00)
│   ├── Task: Trainer fees (₱1,500,000.00)
│   └── Task: Venue and logistics (₱1,500,000.00)
└── Activity 3: Post-training Support (₱1,000,000.00)
    └── Task: Follow-up visits (₱1,000,000.00)
```

### Generating the Budget Allocation Tree

#### Step 1: Navigate to PPA

1. Go to **Monitoring & Evaluation → MOA PPAs**
2. Select the PPA you want to analyze
3. Click **Reports** tab
4. Select **Budget Allocation Tree**

**Screenshot Placeholder:**
> *Image showing Budget Reports section with "Budget Allocation Tree" option*

#### Step 2: View the Tree

The tree displays:
- **Work Item Title**: Name of each work item
- **Allocated Budget**: Budget assigned to this work item (₱)
- **Budget Percentage**: Percentage of total PPA budget
- **Status Indicator**: Visual flag for budget compliance
- **Expand/Collapse**: Click arrows to expand/collapse levels

**Budget Status Indicators:**
- 🟢 **Green**: Budget allocated correctly (sum of children = parent)
- 🟡 **Amber**: Budget partially allocated (children < parent)
- 🔴 **Red**: Budget overallocated (children > parent)
- ⚪ **Gray**: No budget allocated

**Screenshot Placeholder:**
> *Image showing interactive budget allocation tree with color-coded status indicators*

#### Step 3: Drill Down into Details

Click any work item in the tree to see:
- Full budget breakdown
- Child work items and their allocations
- Actual expenditure to date
- Budget variance (allocated vs. actual)
- Budget notes and justifications

**Screenshot Placeholder:**
> *Image showing detailed budget view for a selected work item*

### Understanding Budget Rollup

**Budget Rollup Rule:**
> Parent budget MUST equal the sum of all child budgets

**Example:**
```
✅ CORRECT:
Activity: Training (₱1,000,000.00)
├── Task A: ₱400,000.00
├── Task B: ₱350,000.00
└── Task C: ₱250,000.00
Total: ₱1,000,000.00 (matches parent)

❌ INCORRECT:
Activity: Training (₱1,000,000.00)
├── Task A: ₱400,000.00
├── Task B: ₱350,000.00
└── Task C: ₱400,000.00
Total: ₱1,150,000.00 (exceeds parent by ₱150,000)
```

**What to Do When Budget Doesn't Roll Up:**
1. Identify the variance in the Budget Allocation Tree (flagged in red)
2. Contact the MOA PPA manager to correct the allocation
3. Document the reason for the mismatch
4. Request reallocation or budget amendment if needed

---

## Budget Execution Report

### What is the Budget Execution Report?

The Budget Execution Report compares **allocated budgets** vs. **actual expenditures** across all work items, highlighting over/under budget situations.

### Generating the Report

#### Step 1: Configure Report Parameters

1. Navigate to **Reports → Budget Execution Report**
2. Set report parameters:
   - **PPA Selection**: Single PPA or multiple PPAs
   - **Date Range**: Start and end date for expenditure period
   - **Reporting Level**: Project-level, Activity-level, or Detailed
   - **Include Completed**: ✅ Include completed work items
   - **Currency**: PHP (default)

**Screenshot Placeholder:**
> *Image showing Budget Execution Report configuration form*

#### Step 2: Generate Report

1. Click **"Generate Report"**
2. Wait for processing (5-15 seconds for large PPAs)
3. Report displays on screen in table format

**Report Columns:**

| Column | Description |
|--------|-------------|
| **Work Item** | Title and type of work item |
| **Allocated Budget** | Budget assigned (₱) |
| **Actual Expenditure** | Total expenditure recorded (₱) |
| **Variance** | Difference (Actual - Allocated) |
| **Variance %** | Percentage over/under budget |
| **Utilization %** | (Actual / Allocated) × 100% |
| **Status** | Budget status indicator |

**Screenshot Placeholder:**
> *Image showing Budget Execution Report table with sample data*

#### Step 3: Interpret Results

**Budget Status Codes:**

| Status | Condition | Action Required |
|--------|-----------|-----------------|
| 🟢 **On Budget** | Variance ≤ 5% | No action (normal variance) |
| 🟡 **Under Budget** | Actual < Allocated by >10% | Review for underspending; reallocate if needed |
| 🔴 **Over Budget** | Actual > Allocated | **ALERT**: Requires immediate review and justification |
| ⚪ **No Expenditure** | Actual = ₱0.00 | Normal for not-yet-started work items |

**Example Interpretation:**
```
Work Item: "Training Workshop - Day 1"
Allocated: ₱500,000.00
Actual: ₱535,000.00
Variance: +₱35,000.00 (+7%)
Status: 🔴 Over Budget

Action: Contact MOA PPA manager to provide justification for overrun.
Possible reasons: Increased participant count, venue cost increase, etc.
```

---

## Variance Analysis

### What is Variance Analysis?

Variance Analysis identifies **budget deviations** and categorizes them by:
- **Magnitude**: Small (<5%), Moderate (5-15%), Large (>15%)
- **Direction**: Overrun (positive variance) or Underrun (negative variance)
- **Category**: Personnel, Training, Logistics, Materials, etc.

### Running Variance Analysis

#### Step 1: Access Variance Analysis Tool

1. Navigate to **Reports → Variance Analysis**
2. Select PPAs to analyze (can select multiple)
3. Set variance threshold (default: 5%)
4. Click **"Run Analysis"**

**Screenshot Placeholder:**
> *Image showing Variance Analysis configuration screen*

#### Step 2: Review Variance Summary

The summary dashboard shows:

**Overall Statistics:**
- Total PPAs analyzed
- Total budget allocated
- Total expenditure
- Overall variance (₱ and %)
- Number of work items over/under budget

**Variance Distribution Chart:**
- Pie chart showing variance by category
- Bar chart showing top 10 work items with largest variance

**Screenshot Placeholder:**
> *Image showing variance summary dashboard with charts*

#### Step 3: Drill Down into Individual Variances

Click any work item to see:

**Variance Details:**
- Allocated budget
- Actual expenditure
- Variance amount and percentage
- Expenditure timeline (spending trends)
- Budget notes from MOA staff
- Supporting documents (receipts, invoices)

**Variance Justification:**
- Reason for variance (required for >10% variance)
- Approval status (pending, approved, rejected)
- Approver name and date

**Screenshot Placeholder:**
> *Image showing detailed variance analysis for a single work item*

### Variance Categories

The system classifies variances into categories for analysis:

| Category | Examples | Typical Variances |
|----------|----------|-------------------|
| **Personnel** | Salaries, honoraria, benefits | ±5% (rigid contracts) |
| **Training** | Workshops, seminars, materials | ±10% (variable attendance) |
| **Logistics** | Transport, accommodation, meals | ±15% (price fluctuations) |
| **Materials** | Supplies, equipment, tools | ±10% (bulk discounts, inflation) |
| **Infrastructure** | Construction, repairs | ±20% (weather, material costs) |

**Using Category Analysis:**
1. Identify categories with consistent overruns
2. Recommend budget adjustments for future PPAs
3. Flag potential procurement issues
4. Improve budget estimation accuracy

---

## Budget Distribution Management

### What is Budget Distribution?

Budget Distribution is the process of allocating a PPA's total budget across work items using systematic methods.

### Distribution Methods

The system supports three distribution methods:

#### Method 1: Equal Distribution

**Use Case:** When all activities have similar scope and cost

**How it Works:**
```
PPA Budget: ₱1,200,000.00
Number of Activities: 4

Each activity gets: ₱1,200,000 ÷ 4 = ₱300,000.00
```

**Steps:**
1. Navigate to PPA → **Budget Management**
2. Click **"Distribute Budget"**
3. Select **"Equal Distribution"**
4. Click **"Apply Distribution"**
5. Review and confirm

**Screenshot Placeholder:**
> *Image showing Equal Distribution configuration*

#### Method 2: Weighted Distribution

**Use Case:** When activities have different complexity or resource requirements

**How it Works:**
```
PPA Budget: ₱1,200,000.00

Activity 1 (high complexity): Weight 0.50 → ₱600,000.00
Activity 2 (medium complexity): Weight 0.30 → ₱360,000.00
Activity 3 (low complexity): Weight 0.20 → ₱240,000.00

Total: ₱1,200,000.00
```

**Steps:**
1. Navigate to PPA → **Budget Management**
2. Click **"Distribute Budget"**
3. Select **"Weighted Distribution"**
4. For each activity, set weight percentage (must sum to 100%)
5. Click **"Calculate Distribution"**
6. Review allocations and confirm

**Weight Assignment Guidelines:**
- **High Complexity (40-60%)**: Multi-day training, construction, research
- **Medium Complexity (20-40%)**: Single-day workshops, surveys, events
- **Low Complexity (5-20%)**: Meetings, documentation, reporting

**Screenshot Placeholder:**
> *Image showing Weighted Distribution with weight sliders for each activity*

#### Method 3: Manual Allocation

**Use Case:** When you know exact budget for each work item (e.g., from proposals, quotations)

**How it Works:**
You manually enter the budget for each work item. The system validates that the total matches the PPA budget.

**Steps:**
1. Navigate to PPA → **Budget Management**
2. Click **"Distribute Budget"**
3. Select **"Manual Allocation"**
4. For each work item, enter allocated budget (₱)
5. System shows running total and remaining budget
6. Click **"Apply Allocation"** when total = PPA budget

**Validation:**
```
✅ VALID:
PPA Budget: ₱1,000,000.00
Work Item A: ₱400,000.00
Work Item B: ₱350,000.00
Work Item C: ₱250,000.00
Total: ₱1,000,000.00 (matches PPA budget)

❌ INVALID:
PPA Budget: ₱1,000,000.00
Total Allocated: ₱950,000.00
Error: "Allocation sum (₱950,000.00) does not match PPA budget (₱1,000,000.00)"
```

**Screenshot Placeholder:**
> *Image showing Manual Allocation form with running total indicator*

### Redistributing Budget

If budget needs to be redistributed (e.g., priorities changed):

1. Navigate to PPA → **Budget Management**
2. Click **"Redistribute Budget"**
3. System shows current allocation
4. Choose new distribution method
5. Apply new distribution
6. System creates audit log entry (tracks changes for transparency)

**⚠️ Warning:** Redistributing budget will overwrite existing allocations. Ensure this is intentional.

**Screenshot Placeholder:**
> *Image showing budget redistribution confirmation dialog*

---

## Excel Report Generation

### Exporting Budget Reports to Excel

All budget reports can be exported to Excel for further analysis, archiving, or presentation.

### Step-by-Step Export Process

#### Step 1: Generate Report

1. Navigate to desired report (Budget Allocation Tree, Budget Execution, etc.)
2. Configure report parameters
3. Click **"Generate Report"**
4. Review report on screen

#### Step 2: Export to Excel

1. Click **"Export to Excel"** button (top-right of report)
2. Choose export options:
   - **Include Charts**: ✅ Include visual charts
   - **Include Raw Data**: ✅ Include data tables
   - **Include Summary**: ✅ Include executive summary
   - **Format**: .xlsx (recommended) or .xls (legacy)

3. Click **"Download"**
4. Excel file downloads to your browser's download folder

**Screenshot Placeholder:**
> *Image showing Excel export options dialog*

### Excel Report Structure

The exported Excel file contains multiple worksheets:

| Worksheet | Contents |
|-----------|----------|
| **Summary** | Executive summary with key metrics and charts |
| **Budget Allocation** | Complete budget allocation tree (hierarchical) |
| **Expenditure Details** | Actual expenditures with dates and descriptions |
| **Variance Analysis** | Variance calculations and status flags |
| **Raw Data** | All data in tabular format for pivot tables |
| **Metadata** | Report parameters, generation date, user |

**Screenshot Placeholder:**
> *Image showing Excel workbook with multiple worksheets*

### Excel Report Features

The Excel reports include:
- **Conditional Formatting**: Color-coded cells (green = good, red = over budget)
- **Pivot Tables**: Pre-configured pivot tables for analysis
- **Charts**: Budget distribution pie charts, variance bar charts
- **Formulas**: Variance calculations, budget utilization percentages
- **Filters**: Auto-filters on all data tables
- **Print-Ready Formatting**: Optimized for A4 printing

**Using Excel Reports:**
1. **Analysis**: Use pivot tables to analyze spending patterns
2. **Presentation**: Copy charts to PowerPoint for stakeholder presentations
3. **Archiving**: Save as official budget report for BARMM records
4. **Auditing**: Provide to auditors as supporting documentation

---

## Troubleshooting

### Issue 1: "Budget Allocation Tree Not Available"

**Symptoms:**
- Error message when trying to access Budget Allocation Tree
- Message: "No budget allocation data available"

**Possible Causes:**
- PPA does not have WorkItem tracking enabled
- PPA has no budget allocation set
- Work items have not been assigned budgets

**Solution:**
1. Verify PPA has WorkItem tracking enabled:
   ```
   PPA Detail → Check if "Execution Project" section exists
   ```
2. Verify PPA budget allocation is set:
   ```
   PPA Detail → Budget Allocation field (must have value)
   ```
3. If both are set, contact MOA PPA manager to allocate budget to work items
4. If issue persists, contact BICTO support

---

### Issue 2: "Budget Rollup Mismatch" Error

**Symptoms:**
- Red flag on Budget Allocation Tree
- Error message: "Children budgets do not sum to parent budget"

**Cause:**
The sum of child work item budgets does not equal the parent work item budget.

**Solution:**
1. Identify the work item with mismatch (flagged in red)
2. Calculate expected child budget sum
3. Compare to parent budget
4. Adjust child budgets to match parent, OR
5. Adjust parent budget to match child sum
6. Document reason for adjustment in budget notes

**Example:**
```
Problem:
Activity: Training (Parent Budget: ₱1,000,000.00)
├── Task A: ₱400,000.00
├── Task B: ₱350,000.00
└── Task C: ₱300,000.00
Total: ₱1,050,000.00 ❌ (exceeds parent by ₱50,000.00)

Solution Option 1 (Adjust children):
Reduce Task C to ₱250,000.00
Total: ₱1,000,000.00 ✅

Solution Option 2 (Adjust parent):
Increase Activity budget to ₱1,050,000.00
(Requires MFBM budget amendment approval)
```

---

### Issue 3: "Expenditure Exceeds Allocation" Warning

**Symptoms:**
- Red flag in Budget Execution Report
- Work item showing over budget

**Cause:**
Actual expenditure recorded exceeds allocated budget for that work item.

**Action Required (MFBM):**
1. Review expenditure details and supporting documents
2. Verify expenditures are legitimate and properly documented
3. Request justification from MOA PPA manager
4. Assess if budget reallocation is needed
5. If justified, approve budget amendment
6. If not justified, flag for audit review

**Documentation Required:**
- Detailed expenditure breakdown
- Receipts and invoices
- Justification memo from MOA
- Approval from MFBM Director (for >10% overrun)

---

### Issue 4: "Cannot Export to Excel" Error

**Symptoms:**
- Export button does nothing
- Error message: "Export failed"

**Possible Causes:**
- Report too large (>10,000 rows)
- Browser blocking download
- Temporary server issue

**Solution:**
1. **For large reports**: Use filters to reduce data size, then export
2. **Browser blocking**: Check browser's download settings, allow downloads from OBCMS
3. **Server issue**: Wait 5 minutes and try again; if persists, contact BICTO

**Alternative:**
If Excel export fails, use **"Copy to Clipboard"** button, then paste into Excel manually.

---

### Issue 5: "Variance Analysis Shows Incorrect Data"

**Symptoms:**
- Variance percentages don't match manual calculations
- Missing expenditures in report

**Possible Causes:**
- Report cache is outdated
- Date range filter excludes some expenditures
- Expenditures not yet approved/posted

**Solution:**
1. Click **"Refresh Data"** button to clear cache
2. Check date range filter:
   ```
   Report Parameters → Date Range: [Start] to [End]
   Ensure range includes all expected expenditures
   ```
3. Verify expenditure approval status:
   ```
   Only "Approved" expenditures are included in reports
   Check if pending expenditures need approval
   ```
4. If still incorrect, export raw data and verify manually

---

## FAQ

### General Questions

**Q1: How often should I review budget reports?**

A: MFBM recommends:
- **Budget Execution Report**: Monthly (review by 5th of next month)
- **Variance Analysis**: Monthly (for active PPAs)
- **Budget Allocation Tree**: Quarterly (to verify distribution integrity)

---

**Q2: Can I customize budget reports?**

A: Limited customization available:
- Filter by date range, MOA, sector, status
- Choose reporting level (project, activity, detailed)
- Select columns to include/exclude

For custom reports beyond these options, submit a request to BICTO.

---

**Q3: Are budget reports auditable?**

A: Yes. All budget reports include:
- Generation timestamp
- User who generated the report
- Report parameters used
- Data snapshot (reflects data at time of generation)

Reports are stored for 90 days and can be retrieved for audit purposes.

---

### Budget Allocation Questions

**Q4: What is the tolerance for budget rollup mismatches?**

A: The system allows a variance of ±₱0.01 (one centavo) to account for rounding errors. Any variance greater than this is flagged as an error.

---

**Q5: Can I change budget distribution method after initial setup?**

A: Yes, you can redistribute budget at any time using Budget Management → Redistribute Budget. However:
- This overwrites existing allocations
- An audit log entry is created
- Expenditures already recorded are not affected
- Ensure team is notified of the change

---

**Q6: What happens if a work item is deleted after budget allocation?**

A: When a work item with budget is deleted:
1. System checks if it has child work items (cannot delete if children exist)
2. If deletion is allowed, budget is freed up
3. Parent work item's budget rollup validation may fail
4. You must reallocate the freed budget to other work items

---

### Variance Analysis Questions

**Q7: What is considered an acceptable variance?**

A: MFBM guidelines:
- **±0-5%**: Acceptable (normal operational variance)
- **±5-10%**: Requires notification and monitoring
- **±10-15%**: Requires justification memo
- **>±15%**: Requires formal budget amendment approval

These are guidelines; actual tolerance may vary by budget line item.

---

**Q8: How do I justify a budget overrun?**

A: To justify an overrun:
1. Open the work item in Budget Execution Report
2. Click **"Add Variance Justification"**
3. Provide:
   - Reason for overrun (detailed explanation)
   - Supporting documents (quotes, invoices showing price increase)
   - Proposed action (request budget amendment, reallocate, absorb in other items)
4. Submit for MFBM review
5. MFBM approves, rejects, or requests more information

---

**Q9: Can variance analysis predict future overruns?**

A: The system provides **trend indicators**:
- **Spending Rate**: If spending 50% of budget in first 25% of project, flag as "at risk"
- **Historical Comparison**: Compare to similar PPAs (if available)
- **Forecast**: Projects final expenditure based on current burn rate

These are warnings, not definitive predictions. Use them to trigger early interventions.

---

### Excel Export Questions

**Q10: Why is my Excel export missing data?**

A: Common reasons:
- **Filters applied**: Clear all filters before exporting to get complete data
- **Permissions**: You can only export data you have permission to view
- **Date range**: Expand date range to include all data
- **Export size limit**: Reports >50,000 rows are truncated; use filters to reduce size

---

**Q11: Can I automate Excel report generation?**

A: Yes, use **Scheduled Reports**:
```
Reports → Budget Execution → Schedule Report
Frequency: Monthly (1st of month)
Recipients: mfbm-budget@barmm.gov.ph
Format: Excel
```

Reports are automatically generated and emailed.

---

**Q12: How do I use Excel reports for BARMM quarterly reporting?**

A: The Excel export is designed for BARMM reporting:
1. Generate Budget Execution Report for the quarter
2. Export to Excel
3. Use the **"Summary"** worksheet for executive summary
4. Use **"Variance Analysis"** worksheet for detailed analysis
5. Customize formatting as needed for BARMM templates
6. Save as official quarterly budget report

---

## Appendix: Budget Report Column Definitions

### Budget Allocation Tree Columns

| Column | Definition | Calculation |
|--------|------------|-------------|
| **Work Item** | Title and type of work item | N/A (user input) |
| **Level** | Hierarchy level (1=top) | Auto-calculated by MPTT |
| **Allocated Budget** | Budget assigned to this work item | Manual or distributed |
| **Child Budget Sum** | Sum of all child work item budgets | Σ(child allocated budgets) |
| **Budget Variance** | Difference between allocated and child sum | Allocated - Child Sum |
| **Status** | Budget compliance status | Green/Amber/Red based on variance |

### Budget Execution Report Columns

| Column | Definition | Calculation |
|--------|------------|-------------|
| **Allocated Budget** | Budget assigned | From budget allocation |
| **Actual Expenditure** | Total expenditure recorded | Σ(approved expenditures) |
| **Variance (₱)** | Difference in pesos | Actual - Allocated |
| **Variance (%)** | Difference percentage | (Actual / Allocated - 1) × 100% |
| **Utilization (%)** | Budget used percentage | (Actual / Allocated) × 100% |
| **Remaining Budget** | Unspent budget | Allocated - Actual |

---

## Appendix: Budget Status Color Codes

### Budget Allocation Tree

- 🟢 **Green**: Budget rollup is correct (children sum = parent)
- 🟡 **Amber**: Budget partially allocated (children sum < parent by >5%)
- 🔴 **Red**: Budget overallocated (children sum > parent) or underallocated (variance >10%)
- ⚪ **Gray**: No budget allocated

### Budget Execution Report

- 🟢 **Green**: Variance ≤5% (on budget)
- 🟡 **Amber**: Variance 5-10% (monitor)
- 🔴 **Red**: Variance >10% (requires action)
- ⚫ **Black**: No expenditure recorded

---

## Document Revision History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | 2025-10-06 | Initial MFBM budget reports guide created | BICTO Documentation Team |

---

**For technical support or questions about this guide, contact:**
BICTO Support Team
Email: bicto-support@oobc.barmm.gov.ph
Phone: +63 (XX) XXXX-XXXX

**For budget policy questions, contact:**
MFBM Budget Division
Email: budget-division@mfbm.barmm.gov.ph

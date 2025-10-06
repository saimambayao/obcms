# WorkItem Training Presentation Outline

**Document Type**: Training Materials
**Target Audience**: All OBCMS Stakeholders (MOA, MFBM, BPDA, BICTO)
**Duration**: 2 hours
**Format**: Presentation + Live Demo + Hands-on Exercises
**Last Updated**: October 6, 2025

---

## Presentation Overview

### Learning Objectives

By the end of this training, participants will be able to:

1. **Understand** the purpose and benefits of WorkItem integration
2. **Enable** WorkItem tracking for a PPA
3. **Create and manage** work items (projects, activities, tasks)
4. **Track** progress and update status
5. **Manage** budget allocation and distribution
6. **Generate** reports for stakeholders (MFBM, BPDA)

### Training Agenda

| Time | Section | Duration | Format |
|------|---------|----------|--------|
| 0:00 - 0:15 | Introduction & Overview | 15 min | Presentation |
| 0:15 - 0:30 | System Demo | 15 min | Live Demo |
| 0:30 - 0:50 | Hands-On Exercise 1: Enable Tracking | 20 min | Exercise |
| 0:50 - 1:10 | Managing Work Items | 20 min | Demo + Exercise |
| 1:10 - 1:30 | Budget Management | 20 min | Demo + Exercise |
| 1:30 - 1:50 | Reporting & Analysis | 20 min | Demo |
| 1:50 - 2:00 | Q&A and Wrap-Up | 10 min | Discussion |

---

## Slide Deck Outline

### SECTION 1: Introduction & Overview (Slides 1-10)

#### Slide 1: Title Slide
- **Title**: WorkItem Integration System Training
- **Subtitle**: Project, Activity, and Task Management for MOA PPAs
- **OOBC Logo** + **Date**

#### Slide 2: Training Objectives
- **Title**: What You'll Learn Today
- **Content**:
  - How to enable WorkItem tracking for PPAs
  - Managing work breakdown structures
  - Budget allocation and tracking
  - Progress monitoring and reporting
  - Best practices for each stakeholder role

#### Slide 3: Why WorkItem Integration?
- **Title**: The Problem We're Solving
- **Content**:
  - **Before**: PPAs tracked as monolithic entries, no detailed breakdown
  - **Challenge**: Hard to monitor execution progress, budget utilization unclear
  - **Impact**: Delays in identifying issues, poor budget accountability
- **Visual**: Before/After comparison diagram

#### Slide 4: WorkItem Integration Benefits
- **Title**: Benefits for Each Stakeholder
- **Table**:

| Stakeholder | Benefits |
|-------------|----------|
| **MOA Staff** | Break down complex PPAs, track tasks, assign team members |
| **MFBM Analysts** | Monitor budget utilization, identify overruns early |
| **BPDA Planners** | Track development outcomes, measure BDP alignment |
| **BICTO** | Centralized project management, automated reporting |

#### Slide 5: System Architecture Overview
- **Title**: How WorkItem Integration Works
- **Diagram**: PPA → Execution Project → Activities → Tasks
- **Key Concept**: Hierarchical tree structure (MPTT)
- **Visual**: Tree diagram showing PPA breakdown

#### Slide 6: Core Concepts - Work Item Types
- **Title**: Understanding Work Item Types
- **Content**:
  - **Project**: Top-level execution plan
  - **Activity**: Major milestone or event
  - **Task**: Actionable work unit
  - **Subtask**: Smallest work unit
- **Visual**: Hierarchy diagram with icons

#### Slide 7: Core Concepts - Progress Tracking
- **Title**: How Progress is Calculated
- **Content**:
  - **Auto-Calculate**: Progress = (Completed Children / Total Children) × 100%
  - **Manual Entry**: You set progress percentage
  - **Propagation**: Child progress rolls up to parent
- **Visual**: Flowchart showing progress calculation

#### Slide 8: Core Concepts - Budget Management
- **Title**: Budget Allocation and Tracking
- **Content**:
  - **Allocation**: Budget assigned to work item
  - **Expenditure**: Actual spending recorded
  - **Variance**: Difference between allocation and expenditure
  - **Rollup Rule**: Child budgets must sum to parent budget
- **Visual**: Budget tree with color-coded status

#### Slide 9: User Roles and Permissions
- **Title**: Who Can Do What?
- **Table**:

| Role | Permissions |
|------|-------------|
| **MOA Staff** | Enable tracking, create work items, update progress |
| **MFBM Analyst** | View budget reports, approve budget distributions |
| **BPDA Planner** | View development reports, track outcomes |
| **System Admin** | All permissions, system configuration |

#### Slide 10: Training Roadmap
- **Title**: Today's Training Flow
- **Visual**: Journey map showing training sections
- **Note**: "Please ask questions anytime!"

---

### SECTION 2: System Demo (Slides 11-20)

#### Slide 11: Demo Overview
- **Title**: Live System Demonstration
- **Content**:
  - We'll demonstrate enabling WorkItem tracking for a sample PPA
  - You'll follow along in the next exercise
- **Note**: Projector should show live OBCMS system

#### Slide 12-20: Live Demo Script

**Demo Scenario**: "Livelihood Training Program for OBCs in SOCCSKSARGEN"

**Demo Steps**:
1. **Navigate to PPA** (Show M&E → MOA PPAs → Select PPA)
2. **Enable WorkItem Tracking** (Click button, show modal)
3. **Choose Template** (Select "Activity Template")
4. **Configure Budget Distribution** (Select "Equal Distribution")
5. **Create Execution Project** (Show generated work items)
6. **Add New Activity** (Demonstrate creating child work item)
7. **Update Progress** (Mark task as completed, show auto-sync)
8. **View Budget Tree** (Show hierarchical budget view)
9. **Generate Report** (Export budget execution report)

**Slides**: Screenshots of each step with annotations

---

### SECTION 3: Hands-On Exercise 1 (Slides 21-25)

#### Slide 21: Exercise 1 - Enable WorkItem Tracking
- **Title**: Your Turn: Enable WorkItem Tracking
- **Instructions**:
  1. Log in to OBCMS using your training account
  2. Navigate to Monitoring & Evaluation → MOA PPAs
  3. Select your assigned PPA (found in handout)
  4. Click "Enable WorkItem Tracking"
  5. Choose "Activity Template"
  6. Select "Equal Distribution"
  7. Create execution project
- **Time**: 20 minutes
- **Support**: Trainers will assist

#### Slide 22: Exercise 1 - Success Criteria
- **Title**: Did You Complete the Exercise?
- **Checklist**:
  - ✅ Execution project created
  - ✅ At least 3 activities generated
  - ✅ Budget distributed equally
  - ✅ Can view work item tree

#### Slide 23: Exercise 1 - Common Issues
- **Title**: Troubleshooting Tips
- **Content**:
  - **"Button grayed out"**: PPA must have budget allocation set
  - **"Permission denied"**: Contact trainer to verify role
  - **"No activities generated"**: Check template selection

#### Slide 24: Exercise 1 - Debrief
- **Title**: Let's Review Together
- **Questions**:
  - How many work items were created?
  - What budget was allocated to each activity?
  - Who can see the work items you created?

#### Slide 25: Break
- **Title**: 5-Minute Break
- **Content**: Stretch, grab coffee, we'll resume at [time]

---

### SECTION 4: Managing Work Items (Slides 26-35)

#### Slide 26: Creating Work Items
- **Title**: Adding Work Items to Your Project
- **Content**:
  - **Add Child**: Click "Add Child" on parent work item
  - **Form Fields**: Title, Type, Description, Dates, Assignees
  - **Budget**: Optional budget allocation
- **Visual**: Screenshot of "Add Work Item" form

#### Slide 27: Work Item Lifecycle
- **Title**: Work Item Status Flow
- **Diagram**: Status transition diagram
  ```
  Not Started → In Progress → Completed
                     ↓
                  At Risk
                     ↓
                  Blocked
  ```

#### Slide 28: Updating Progress
- **Title**: Tracking Progress
- **Content**:
  - **Auto-Calculate**: System calculates from child completion
  - **Manual**: You set percentage directly
  - **Best Practice**: Use auto-calculate for parent items

#### Slide 29: Assigning Team Members
- **Title**: Collaboration Features
- **Content**:
  - Assign multiple users to a work item
  - Assigned users receive notifications
  - Team dashboard shows all assignments

#### Slide 30: Demo - Managing Work Items
- **Live Demo**:
  1. Create new task under an activity
  2. Assign to team member
  3. Update status to "In Progress"
  4. Mark as completed
  5. Show progress rollup to parent

#### Slides 31-32: Hands-On Exercise 2
- **Title**: Exercise 2 - Manage Work Items
- **Instructions**:
  1. Add a new task to Activity 1
  2. Set due date to next Friday
  3. Assign to yourself
  4. Update status to "In Progress"
  5. Add progress note
- **Time**: 15 minutes

#### Slide 33-35: Exercise 2 Review
- Debrief and Q&A

---

### SECTION 5: Budget Management (Slides 36-45)

#### Slide 36: Budget Allocation Basics
- **Title**: Understanding Budget Allocation
- **Content**:
  - **Total PPA Budget**: ₱5,000,000
  - **Distribution Methods**: Equal, Weighted, Manual
  - **Validation**: Children must sum to parent

#### Slide 37: Budget Distribution Methods
- **Title**: Choosing the Right Method
- **Table**:

| Method | When to Use | Example |
|--------|-------------|---------|
| **Equal** | Similar-sized activities | 3 activities × ₱1.67M each |
| **Weighted** | Different complexity | High:50%, Med:30%, Low:20% |
| **Manual** | Known exact costs | Activity A: ₱2M, B: ₱1.5M, C: ₱1.5M |

#### Slide 38: Recording Expenditures
- **Title**: Tracking Actual Spending
- **Content**:
  - Record expenditure with date and description
  - Upload receipt (optional but recommended)
  - System calculates variance automatically

#### Slide 39: Budget Variance Analysis
- **Title**: Understanding Variance
- **Content**:
  - **Variance = Actual - Allocated**
  - **Positive Variance** (red): Over budget
  - **Negative Variance** (green): Under budget
  - **Tolerance**: ±5% acceptable

#### Slide 40: Demo - Budget Management
- **Live Demo**:
  1. View budget allocation tree
  2. Redistribute budget (weighted method)
  3. Record expenditure for a task
  4. Show variance calculation
  5. Generate budget execution report

#### Slides 41-43: Hands-On Exercise 3
- **Title**: Exercise 3 - Budget Management
- **Instructions**:
  1. View your PPA budget allocation tree
  2. Record an expenditure for Task 1 (₱50,000)
  3. Check variance status
  4. Generate budget execution report
- **Time**: 15 minutes

#### Slides 44-45: MFBM Reporting
- **Title**: Budget Reports for MFBM
- **Content**: Overview of budget reports for MFBM analysts
- **Screenshot**: Sample budget execution report

---

### SECTION 6: Reporting & Analysis (Slides 46-55)

#### Slide 46: Report Types Overview
- **Title**: Available Reports
- **List**:
  - Progress Report (for MOA management)
  - Budget Execution Report (for MFBM)
  - Development Outcome Report (for BPDA)
  - Team Performance Report (for HR)

#### Slide 47-48: MOA Progress Reports
- **Demo**: Generate progress report
- **Screenshot**: Sample report with charts

#### Slide 49-50: MFBM Budget Reports
- **Demo**: Generate budget execution report
- **Screenshot**: Variance analysis table

#### Slide 51-52: BPDA Development Reports
- **Demo**: Generate BDP alignment report
- **Screenshot**: Alignment scorecard

#### Slide 53: Exporting Reports
- **Title**: Sharing Reports
- **Content**:
  - Export to Excel, PDF, PowerPoint
  - Schedule automated reports
  - Email to stakeholders

#### Slide 54: Demo - Reporting
- **Live Demo**: Generate and export all report types

#### Slide 55: Reporting Best Practices
- **Title**: Tips for Effective Reporting
- **Content**:
  - Generate reports monthly (at minimum)
  - Review variance before submitting to MFBM
  - Use Excel for detailed analysis
  - Archive reports for audit trail

---

### SECTION 7: Q&A and Wrap-Up (Slides 56-60)

#### Slide 56: Key Takeaways
- **Title**: What We Learned Today
- **List**:
  - ✅ Enabled WorkItem tracking for PPAs
  - ✅ Created and managed work items
  - ✅ Allocated and tracked budget
  - ✅ Generated reports for stakeholders

#### Slide 57: Resources
- **Title**: Where to Get Help
- **Content**:
  - **User Guides**: docs/user-guides/
  - **API Documentation**: docs/api/
  - **Support Email**: bicto-support@oobc.barmm.gov.ph
  - **Knowledge Base**: https://docs.obcms.oobc.barmm.gov.ph

#### Slide 58: Next Steps
- **Title**: After This Training
- **Action Items**:
  - [ ] Enable WorkItem tracking for your real PPAs
  - [ ] Train your team members
  - [ ] Set up automated reports
  - [ ] Provide feedback to BICTO

#### Slide 59: Feedback Form
- **Title**: We Value Your Feedback
- **QR Code**: Link to feedback form
- **Request**: Please complete before leaving

#### Slide 60: Thank You!
- **Title**: Thank You for Attending
- **Contact**:
  - Training Team: bicto-training@oobc.barmm.gov.ph
  - Support: bicto-support@oobc.barmm.gov.ph
- **Final Message**: "Questions? Let's discuss!"

---

## Training Materials Checklist

### Pre-Training

- [ ] Presentation slides finalized (PowerPoint or Google Slides)
- [ ] Training accounts created for all participants
- [ ] Sample PPAs created for exercises
- [ ] Handouts printed (user guides, cheat sheets)
- [ ] Projector and screen tested
- [ ] Internet connection verified
- [ ] Backup demo video prepared (in case of technical issues)

### During Training

- [ ] Sign-in sheet for attendance
- [ ] Training evaluation forms
- [ ] Certificates of completion
- [ ] Business cards for trainers

### Post-Training

- [ ] Share presentation slides with participants
- [ ] Send follow-up email with resources
- [ ] Collect and analyze feedback
- [ ] Update training materials based on feedback

---

## Hands-On Exercise Details

### Exercise 1: Enable WorkItem Tracking

**Objective**: Enable WorkItem tracking for assigned PPA

**Provided Materials**:
- Login credentials
- Assigned PPA ID
- Step-by-step guide

**Success Criteria**:
- Execution project created
- At least 3 work items visible
- Budget distributed

**Time**: 20 minutes

---

### Exercise 2: Manage Work Items

**Objective**: Create and manage work items

**Tasks**:
1. Create new task
2. Assign to team member
3. Update status
4. Add progress note

**Success Criteria**:
- Task created and assigned
- Status updated successfully
- Progress note saved

**Time**: 15 minutes

---

### Exercise 3: Budget Management

**Objective**: Allocate budget and record expenditure

**Tasks**:
1. View budget tree
2. Record expenditure
3. Generate budget report

**Success Criteria**:
- Expenditure recorded
- Variance calculated
- Report generated

**Time**: 15 minutes

---

## Trainer Notes

### Preparation Tips

- Arrive 30 minutes early to set up
- Test all demos before training starts
- Have backup plan if system is down
- Prepare answers to common questions

### Common Questions & Answers

**Q: Can I delete a work item after creating it?**
A: Yes, but if it has children, you must delete children first or use "Delete with Children" option.

**Q: What happens if budget exceeds allocation?**
A: System flags it with red warning. MFBM will be notified. Requires justification.

**Q: Can I disable WorkItem tracking after enabling?**
A: Yes, but work items remain inactive. Progress stops syncing. Consult BICTO first.

**Q: How often should I update progress?**
A: At least weekly for active tasks. Update immediately when status changes.

---

## Document Revision History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | 2025-10-06 | Initial training presentation outline | BICTO Training Team |

---

**For training inquiries:**
- Email: bicto-training@oobc.barmm.gov.ph
- Phone: +63 (XX) XXXX-XXXX

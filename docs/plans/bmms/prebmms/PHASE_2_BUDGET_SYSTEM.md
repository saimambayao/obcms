# Phase 2: Budget System Implementation
## Comprehensive Execution Plan for Budget Preparation and Execution

**Document Version:** 1.0
**Date:** 2025-10-13
**Status:** ✅ Ready for Implementation
**Priority:** CRITICAL - Legal requirement (Parliament Bill No. 325)

---

## Executive Summary

### Purpose

Implement a comprehensive budget system for OOBC that ensures **full compliance with Parliament Bill No. 325** (Bangsamoro Budget System Act), establishing:

1. **Budget Preparation Module** - Annual budget planning aligned with strategic goals
2. **Budget Execution Module** - Real-time tracking of allotments, obligations, and disbursements
3. **Financial Accountability** - Transparent reporting and performance monitoring

### Value to OOBC

**Priority:** CRITICAL ⭐⭐⭐⭐⭐

**Immediate Benefits:**
- ✅ **Legal Compliance** - Parliament Bill No. 325 mandates budget system
- ✅ **Financial Accountability** - Transparent tracking of public funds
- ✅ **Strategic Alignment** - Budgets linked to strategic plans and M&E programs
- ✅ **Real-time Visibility** - Budget utilization tracking and variance analysis
- ✅ **Evidence-Based Decision Making** - Data-driven budget allocation

### BMMS Compatibility

**Score:** 90% - Highly Compatible ✅

**Migration Path:** Add `organization` field via single migration when transitioning to BMMS multi-tenant architecture. All models are designed organization-agnostic and will seamlessly scale to multi-MOA context.

### Complexity Assessment

**Overall Complexity:** Complex

**Rationale:**
- Financial system with strict constraints (no overspending)
- Complex workflows (draft → submitted → approved → enacted)
- Integration with Planning and M&E modules
- Real-time calculations and validation
- Audit trail requirements

### Implementation Approach

**Two Sub-Phases:**

1. **Phase 2A: Budget Preparation** (PRIORITY: HIGH)
   - Budget proposal creation and justification
   - Program-level allocation
   - Planning module integration
   - Submission workflow

2. **Phase 2B: Budget Execution** (PRIORITY: CRITICAL)
   - Allotment tracking (quarterly releases)
   - Obligation recording
   - Disbursement tracking
   - Financial reporting and dashboards

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Phase 2A: Budget Preparation](#phase-2a-budget-preparation)
3. [Phase 2B: Budget Execution](#phase-2b-budget-execution)
4. [Database Schema Design](#database-schema-design)
5. [Code Examples](#code-examples)
6. [UI/UX Specifications](#uiux-specifications)
7. [Financial Business Rules](#financial-business-rules)
8. [Integration Points](#integration-points)
9. [Testing Strategy](#testing-strategy)
10. [Success Criteria](#success-criteria)
11. [BMMS Migration Notes](#bmms-migration-notes)

---

## Prerequisites

### Required Completions

- [x] **Phase 0 Complete** - URL structure refactored (module-based routing)
- [x] **Phase 1 Complete** - Planning module operational (strategic plans, annual work plans)

### Technical Requirements

- Django 5.2+ with PostgreSQL support
- Python virtual environment active (`venv/`)
- All dependencies in `requirements/base.txt` installed
- Working directory: `src/`

### Module Dependencies

```python
# Budget system depends on:
- common            # User model, authentication
- planning          # Strategic plans, annual work plans
- monitoring        # Programs, activities for budget linking
```

---

## Phase 2A: Budget Preparation

**Duration:** Complexity: Complex
**Prerequisites:** Phase 1 complete (Planning module)
**Value to OOBC:** ⭐⭐⭐⭐ HIGH

### Detailed Task Breakdown

#### 2A.1 App Structure Setup

**Tasks:**

- [ ] **Create `budget_preparation` Django app**
  ```bash
  cd src
  python manage.py startapp budget_preparation
  ```

- [ ] **Configure app in settings**
  ```python
  # src/obc_management/settings/base.py
  INSTALLED_APPS = [
      # ... existing apps ...
      'budget_preparation',
  ]
  ```

- [ ] **Create directory structure**
  ```bash
  mkdir -p src/budget_preparation/{models,services,forms,views}
  touch src/budget_preparation/models/__init__.py
  touch src/budget_preparation/services/__init__.py
  touch src/budget_preparation/forms/__init__.py
  touch src/budget_preparation/views/__init__.py
  ```

- [ ] **Create URL configuration**
  ```bash
  touch src/budget_preparation/urls.py
  ```

- [ ] **Register URLs in main config**
  ```python
  # src/obc_management/urls.py
  urlpatterns = [
      # ... existing patterns ...
      path('budget/preparation/', include('budget_preparation.urls')),
  ]
  ```

**Deliverables:**
- Empty Django app structure
- App registered in settings
- URL routing configured

---

#### 2A.2 Database Models (Preparation)

**Tasks:**

- [ ] **Create `BudgetProposal` model**
  - Annual budget proposal for OOBC
  - Fiscal year, total amount, status
  - Justification documentation
  - Link to strategic plan

- [ ] **Create `ProgramBudget` model**
  - Budget allocation per program
  - Requested vs. approved amounts
  - Link to M&E programs
  - Link to annual work plan objectives

- [ ] **Create `BudgetJustification` model**
  - Narrative support for budget requests
  - Evidence-based justifications
  - Expected outcomes
  - Risk assessment

- [ ] **Create `BudgetLineItem` model**
  - Detailed budget line items
  - Object of expenditure codes
  - Cost estimates
  - Quantity and unit costs

- [ ] **Create migrations**
  ```bash
  python manage.py makemigrations budget_preparation
  python manage.py migrate
  ```

**Deliverables:**
- 4 core models defined
- Relationships established
- Database migrations applied

---

#### 2A.3 Admin Interface (Preparation)

**Tasks:**

- [ ] **Register models in admin**
  ```python
  # src/budget_preparation/admin.py
  from django.contrib import admin
  from .models import BudgetProposal, ProgramBudget, BudgetJustification, BudgetLineItem

  @admin.register(BudgetProposal)
  class BudgetProposalAdmin(admin.ModelAdmin):
      list_display = ('fiscal_year', 'proposed_amount', 'status', 'submission_date')
      list_filter = ('status', 'fiscal_year')
      search_fields = ('fiscal_year',)
  ```

- [ ] **Configure inline editing**
  - Program budgets inline in proposal
  - Line items inline in program budget
  - Justifications inline in program budget

- [ ] **Add calculated fields**
  - Total requested amount (sum of program budgets)
  - Budget variance (requested vs. approved)
  - Submission progress percentage

**Deliverables:**
- Admin interface functional
- Inline editing working
- Quick data entry capability

---

#### 2A.4 Views & Forms (Preparation)

**Tasks:**

- [ ] **Create budget proposal CRUD views**
  - `budget_proposal_list` - List all proposals
  - `budget_proposal_create` - Create new proposal
  - `budget_proposal_detail` - View proposal details
  - `budget_proposal_edit` - Edit draft proposal
  - `budget_proposal_delete` - Delete draft proposal

- [ ] **Implement submission workflow**
  - Draft → Submitted (validate completeness)
  - Submitted → Under Review (OOBC leadership review)
  - Under Review → Approved (approval decision)
  - Approved → Enacted (final budget law)

- [ ] **Create program allocation views**
  - Program budget allocation interface
  - Visual allocation chart (pie chart)
  - Budget ceiling validation

- [ ] **Build justification management**
  - Rich text editor for narratives
  - Evidence attachment upload
  - Outcome projection forms

- [ ] **Implement complex budget forms**
  - Dynamic formsets for program budgets
  - Real-time calculation of totals
  - Client-side validation
  - Server-side constraint checks

**Deliverables:**
- Full CRUD for budget proposals
- Workflow state machine
- Form validation and calculations

---

#### 2A.5 Planning Integration

**Tasks:**

- [ ] **Link budgets to strategic goals**
  ```python
  class ProgramBudget(models.Model):
      strategic_goal = models.ForeignKey(
          'planning.StrategicGoal',
          on_delete=models.SET_NULL,
          null=True,
          related_name='program_budgets'
      )
  ```

- [ ] **Link budgets to annual work plans**
  ```python
  class ProgramBudget(models.Model):
      annual_work_plan = models.ForeignKey(
          'planning.AnnualWorkPlan',
          on_delete=models.SET_NULL,
          null=True
      )
  ```

- [ ] **Implement alignment validation**
  - Check all programs have strategic goal alignment
  - Verify annual plan objectives funded
  - Calculate strategic goal funding percentages

- [ ] **Create budget-plan alignment dashboard**
  - Visual representation of budget-to-plan alignment
  - Unfunded objectives report
  - Strategic goal funding distribution

**Deliverables:**
- Budget-plan linkage established
- Alignment validation rules
- Alignment visualization dashboard

---

#### 2A.6 M&E Integration

**Tasks:**

- [ ] **Link program budgets to M&E programs**
  ```python
  class ProgramBudget(models.Model):
      program = models.ForeignKey(
          'monitoring.Program',
          on_delete=models.CASCADE,
          related_name='budgets'
      )
  ```

- [ ] **Pull budget requirements from projects**
  - Aggregate project cost estimates
  - Calculate program budget needs
  - Identify underfunded programs

- [ ] **Create budget requirements report**
  - Program-wise budget needs
  - Funding gap analysis
  - Priority program identification

**Deliverables:**
- M&E program budget integration
- Budget requirements calculation
- Funding gap reports

---

## Phase 2B: Budget Execution

**Duration:** Complexity: Complex
**Prerequisites:** Phase 2A complete
**Value to OOBC:** ⭐⭐⭐⭐⭐ CRITICAL (Financial accountability)

### Detailed Task Breakdown

#### 2B.1 App Structure Setup

**Tasks:**

- [ ] **Create `budget_execution` Django app**
  ```bash
  cd src
  python manage.py startapp budget_execution
  ```

- [ ] **Configure app in settings**
  ```python
  INSTALLED_APPS = [
      # ... existing apps ...
      'budget_preparation',  # From Phase 2A
      'budget_execution',    # NEW
  ]
  ```

- [ ] **Create directory structure**
  ```bash
  mkdir -p src/budget_execution/{models,services,forms,views}
  ```

- [ ] **Register URLs**
  ```python
  # src/obc_management/urls.py
  urlpatterns = [
      # ... existing patterns ...
      path('budget/execution/', include('budget_execution.urls')),
  ]
  ```

**Deliverables:**
- Budget execution app created
- URL routing configured

---

#### 2B.2 Database Models (Execution)

**Tasks:**

- [ ] **Create `Allotment` model**
  - Quarterly budget releases
  - Link to program budget (approved amounts)
  - Quarter (Q1, Q2, Q3, Q4)
  - Released amount
  - Status (pending, released, utilized)

- [ ] **Create `Obligation` model**
  - Commitments against allotments
  - Purchase orders, contracts
  - Obligated amount
  - Obligated date
  - Link to allotment (constraint: cannot exceed)
  - Link to M&E activity (for tracking)

- [ ] **Create `Disbursement` model**
  - Actual payments
  - Link to obligation
  - Disbursed amount
  - Disbursed date
  - Payee information
  - Check/voucher number

- [ ] **Create `WorkItem` model** (detailed spending)
  - Breakdown of spending by work item
  - Link to project/activity
  - Cost center codes
  - Actual costs incurred

- [ ] **Create migrations**
  ```bash
  python manage.py makemigrations budget_execution
  python manage.py migrate
  ```

**Deliverables:**
- 4 execution models defined
- Financial constraints in database
- Migrations applied

---

#### 2B.3 Admin Interface (Execution)

**Tasks:**

- [ ] **Register execution models**
  ```python
  @admin.register(Allotment)
  class AllotmentAdmin(admin.ModelAdmin):
      list_display = ('program_budget', 'quarter', 'amount', 'status')
      list_filter = ('quarter', 'status')
  ```

- [ ] **Configure tracking displays**
  - Obligation tracking inline in allotment
  - Disbursement tracking inline in obligation
  - Real-time balance calculations

- [ ] **Add financial constraint validation**
  - Prevent obligation beyond allotment
  - Prevent disbursement beyond obligation
  - Display remaining balances

**Deliverables:**
- Admin interface for execution tracking
- Real-time balance displays
- Constraint enforcement

---

#### 2B.4 Views & Forms (Execution)

**Tasks:**

- [ ] **Create allotment management dashboard**
  - Quarterly allotment release interface
  - Allotment utilization metrics
  - Unreleased balance tracking

- [ ] **Build obligation recording forms**
  - Purchase order entry
  - Contract recording
  - Obligation amount validation
  - Activity linkage

- [ ] **Implement disbursement tracking**
  - Payment recording forms
  - Check/voucher tracking
  - Payee management
  - Disbursement verification

- [ ] **Create budget utilization reports**
  - Budget vs. actual comparison
  - Variance analysis
  - Program-wise utilization
  - Quarterly spending trends

- [ ] **Build financial dashboards**
  - Executive budget dashboard (stat cards)
  - Budget execution chart (stacked bar: allotment, obligation, disbursement)
  - Program utilization comparison
  - Monthly spending trends

**Deliverables:**
- Full execution tracking system
- Financial reporting capability
- Interactive dashboards

---

#### 2B.5 Financial Reporting

**Tasks:**

- [ ] **Implement monthly financial statements**
  - Statement of allotment, obligation, disbursement
  - Fund balance report
  - Cash flow statement

- [ ] **Create budget vs. actual comparison**
  - Approved budget baseline
  - Actual spending to date
  - Variance (amount and percentage)
  - Trend analysis

- [ ] **Build variance analysis reports**
  - Favorable vs. unfavorable variances
  - Variance explanations (manual notes)
  - Remedial action tracking

- [ ] **Implement program-wise utilization**
  - Program utilization percentage
  - Under-spending identification
  - Over-committed programs alert

- [ ] **Create dashboard visualizations**
  - Budget execution gauge charts
  - Monthly spending line charts
  - Program comparison bar charts
  - Quarterly trend analysis

**Deliverables:**
- Comprehensive financial reports
- Variance analysis capability
- Visual analytics dashboards

---

#### 2B.6 M&E Activity Integration

**Tasks:**

- [ ] **Link spending to specific activities**
  ```python
  class Obligation(models.Model):
      activity = models.ForeignKey(
          'monitoring.Activity',
          on_delete=models.CASCADE,
          null=True,
          related_name='obligations'
      )
  ```

- [ ] **Implement financial performance tracking**
  - Activity-level spending summaries
  - Budget utilization per activity
  - Cost efficiency metrics

- [ ] **Create activity spending reports**
  - Activity budget vs. actual
  - Activity completion vs. spending
  - Under/over-budget activities

**Deliverables:**
- Activity-level financial tracking
- Performance-spending correlation
- Cost efficiency reports

---

#### 2B.7 Testing (Both 2A and 2B)

**Tasks:**

- [ ] **Write model tests**
  - Test financial calculations
  - Test budget constraints (no overspending)
  - Test workflow state transitions
  - Test model relationships

- [ ] **Create view tests**
  - Test CRUD operations
  - Test permission requirements
  - Test form submissions
  - Test error handling

- [ ] **Implement form validation tests**
  - Test required fields
  - Test numeric validations
  - Test date range validations
  - Test financial constraint checks

- [ ] **Write financial constraint tests**
  - Test obligation ≤ allotment
  - Test disbursement ≤ obligation
  - Test quarterly allotment ≤ annual budget
  - Test budget total = sum of programs

- [ ] **Create integration tests**
  - Test Planning → Budget flow
  - Test Budget → M&E tracking
  - Test multi-module workflows

**Deliverables:**
- 80%+ test coverage
- All financial constraints tested
- Integration workflows verified

---

#### 2B.8 Documentation

**Tasks:**

- [ ] **Write user guide**
  - Budget preparation guide
  - Budget execution guide
  - Parliament Bill No. 325 compliance checklist
  - Financial workflows documentation

- [ ] **Create financial workflow diagrams**
  - Budget cycle flowchart
  - Approval workflow diagram
  - Execution tracking process

- [ ] **Document API endpoints**
  - Budget API reference
  - Execution tracking API
  - Financial reports API

- [ ] **Write admin manual**
  - System configuration
  - User management
  - Fiscal year setup
  - Reporting schedule

**Deliverables:**
- Complete user documentation
- Workflow diagrams
- API documentation

---

## Database Schema Design

### Budget Preparation Schema

```python
# src/budget_preparation/models/budget_proposal.py

from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal


class BudgetProposal(models.Model):
    """
    Annual budget proposal for OOBC

    BMMS Note: Will add organization field for multi-MOA support
    """

    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('under_review', 'Under Review'),
        ('approved', 'Approved'),
        ('enacted', 'Enacted'),
        ('rejected', 'Rejected'),
    ]

    # Fiscal year (e.g., 2025 for FY2025)
    fiscal_year = models.IntegerField(
        validators=[MinValueValidator(2020)]
    )

    # Total proposed amount (sum of all program budgets)
    proposed_amount = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )

    # Approved amount (after review/negotiation)
    approved_amount = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0.01'))]
    )

    # Budget justification (narrative)
    justification = models.TextField()

    # Link to strategic plan
    strategic_plan = models.ForeignKey(
        'planning.StrategicPlan',
        on_delete=models.SET_NULL,
        null=True,
        related_name='budget_proposals'
    )

    # Workflow status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft'
    )

    # Important dates
    submission_date = models.DateField(null=True, blank=True)
    approval_date = models.DateField(null=True, blank=True)
    enacted_date = models.DateField(null=True, blank=True)

    # Audit trail
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        'common.User',
        on_delete=models.PROTECT,
        related_name='budget_proposals_created'
    )

    class Meta:
        db_table = 'budget_preparation_proposal'
        ordering = ['-fiscal_year']
        unique_together = [['fiscal_year']]  # One budget per fiscal year
        indexes = [
            models.Index(fields=['fiscal_year', 'status']),
        ]

    def __str__(self):
        return f"FY{self.fiscal_year} Budget Proposal"

    def get_total_requested(self):
        """Calculate total from program budgets"""
        return self.program_budgets.aggregate(
            total=models.Sum('requested_amount')
        )['total'] or Decimal('0.00')

    def get_budget_variance(self):
        """Calculate variance between proposed and approved"""
        if self.approved_amount:
            return self.approved_amount - self.proposed_amount
        return Decimal('0.00')

    def can_edit(self):
        """Check if proposal can be edited"""
        return self.status in ['draft', 'under_review']

    def can_submit(self):
        """Check if proposal is ready for submission"""
        # Must have at least one program budget
        if not self.program_budgets.exists():
            return False
        # Must have justification
        if not self.justification:
            return False
        # Status must be draft
        return self.status == 'draft'


class ProgramBudget(models.Model):
    """
    Budget allocation per program

    Links to M&E programs and planning objectives
    """

    # Parent budget proposal
    budget_proposal = models.ForeignKey(
        'BudgetProposal',
        on_delete=models.CASCADE,
        related_name='program_budgets'
    )

    # Link to M&E program
    program = models.ForeignKey(
        'monitoring.Program',
        on_delete=models.CASCADE,
        related_name='budgets'
    )

    # Requested amount
    requested_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )

    # Approved amount (may differ from requested)
    approved_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0.01'))]
    )

    # Link to strategic goal
    strategic_goal = models.ForeignKey(
        'planning.StrategicGoal',
        on_delete=models.SET_NULL,
        null=True,
        related_name='program_budgets'
    )

    # Link to annual work plan
    annual_work_plan = models.ForeignKey(
        'planning.AnnualWorkPlan',
        on_delete=models.SET_NULL,
        null=True,
        related_name='program_budgets'
    )

    # Work plan objectives (JSONField)
    work_plan_objectives = models.JSONField(default=list)

    # Justification for this program
    justification = models.TextField(blank=True)

    # Expected outcomes
    expected_outcomes = models.TextField(blank=True)

    # Priority rank (1 = highest)
    priority_rank = models.IntegerField(default=1)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'budget_preparation_program_budget'
        ordering = ['priority_rank', 'program__name']
        unique_together = [['budget_proposal', 'program']]

    def __str__(self):
        return f"{self.program.name} - FY{self.budget_proposal.fiscal_year}"

    def get_variance(self):
        """Calculate variance between requested and approved"""
        if self.approved_amount:
            return self.approved_amount - self.requested_amount
        return Decimal('0.00')

    def get_utilization_rate(self):
        """Calculate budget utilization from allotments"""
        total_allotted = self.allotments.aggregate(
            total=models.Sum('amount')
        )['total'] or Decimal('0.00')

        if self.approved_amount and self.approved_amount > 0:
            return (total_allotted / self.approved_amount) * 100
        return Decimal('0.00')


class BudgetJustification(models.Model):
    """
    Narrative support for budget requests

    Provides evidence-based justification for programs
    """

    program_budget = models.ForeignKey(
        'ProgramBudget',
        on_delete=models.CASCADE,
        related_name='justifications'
    )

    # Justification type
    JUSTIFICATION_TYPES = [
        ('needs', 'Community Needs'),
        ('outcomes', 'Expected Outcomes'),
        ('evidence', 'Evidence Base'),
        ('risks', 'Risk Assessment'),
        ('alternatives', 'Alternative Considered'),
    ]

    justification_type = models.CharField(
        max_length=20,
        choices=JUSTIFICATION_TYPES
    )

    # Narrative content
    content = models.TextField()

    # Supporting evidence (optional file attachment)
    evidence_document = models.FileField(
        upload_to='budget/justifications/%Y/',
        null=True,
        blank=True
    )

    # Order for display
    display_order = models.IntegerField(default=1)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        'common.User',
        on_delete=models.PROTECT
    )

    class Meta:
        db_table = 'budget_preparation_justification'
        ordering = ['display_order', 'created_at']

    def __str__(self):
        return f"{self.get_justification_type_display()} - {self.program_budget}"


class BudgetLineItem(models.Model):
    """
    Detailed budget line items

    Granular breakdown of program budgets
    """

    program_budget = models.ForeignKey(
        'ProgramBudget',
        on_delete=models.CASCADE,
        related_name='line_items'
    )

    # Object of expenditure code (e.g., 5-01-01-010 for salaries)
    object_code = models.CharField(max_length=20)

    # Description
    description = models.CharField(max_length=255)

    # Quantity and unit cost
    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )

    unit = models.CharField(max_length=50)  # e.g., "person", "unit", "month"

    unit_cost = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )

    # Total cost (quantity * unit_cost)
    total_cost = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )

    # Notes
    notes = models.TextField(blank=True)

    class Meta:
        db_table = 'budget_preparation_line_item'
        ordering = ['object_code']

    def __str__(self):
        return f"{self.object_code} - {self.description}"

    def save(self, *args, **kwargs):
        """Auto-calculate total cost"""
        self.total_cost = self.quantity * self.unit_cost
        super().save(*args, **kwargs)
```

### Budget Execution Schema

```python
# src/budget_execution/models/allotment.py

from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from decimal import Decimal


class Allotment(models.Model):
    """
    Quarterly budget allotments

    Releases from approved program budgets
    """

    QUARTER_CHOICES = [
        (1, 'Q1 (Jan-Mar)'),
        (2, 'Q2 (Apr-Jun)'),
        (3, 'Q3 (Jul-Sep)'),
        (4, 'Q4 (Oct-Dec)'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('released', 'Released'),
        ('partially_utilized', 'Partially Utilized'),
        ('fully_utilized', 'Fully Utilized'),
        ('cancelled', 'Cancelled'),
    ]

    # Link to approved program budget
    program_budget = models.ForeignKey(
        'budget_preparation.ProgramBudget',
        on_delete=models.CASCADE,
        related_name='allotments'
    )

    # Quarter
    quarter = models.IntegerField(choices=QUARTER_CHOICES)

    # Allotment amount
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )

    # Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    # Release details
    release_date = models.DateField(null=True, blank=True)
    allotment_order_number = models.CharField(max_length=50, blank=True)

    # Notes
    notes = models.TextField(blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        'common.User',
        on_delete=models.PROTECT
    )

    class Meta:
        db_table = 'budget_execution_allotment'
        ordering = ['program_budget', 'quarter']
        unique_together = [['program_budget', 'quarter']]
        indexes = [
            models.Index(fields=['program_budget', 'status']),
        ]

    def __str__(self):
        return f"{self.program_budget} - {self.get_quarter_display()}"

    def clean(self):
        """Validate allotment doesn't exceed approved budget"""
        if self.program_budget.approved_amount:
            # Get total allotments for this program
            total_allotted = self.program_budget.allotments.exclude(
                pk=self.pk
            ).aggregate(
                total=models.Sum('amount')
            )['total'] or Decimal('0.00')

            total_allotted += self.amount

            if total_allotted > self.program_budget.approved_amount:
                raise ValidationError(
                    f"Total allotments ({total_allotted}) exceed approved budget "
                    f"({self.program_budget.approved_amount})"
                )

    def get_obligated_amount(self):
        """Calculate total obligations against this allotment"""
        return self.obligations.aggregate(
            total=models.Sum('amount')
        )['total'] or Decimal('0.00')

    def get_remaining_balance(self):
        """Calculate remaining balance"""
        return self.amount - self.get_obligated_amount()

    def get_utilization_rate(self):
        """Calculate utilization percentage"""
        if self.amount > 0:
            return (self.get_obligated_amount() / self.amount) * 100
        return Decimal('0.00')


class Obligation(models.Model):
    """
    Obligations against allotments

    Purchase orders, contracts, commitments
    """

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('committed', 'Committed'),
        ('partially_disbursed', 'Partially Disbursed'),
        ('fully_disbursed', 'Fully Disbursed'),
        ('cancelled', 'Cancelled'),
    ]

    # Link to allotment
    allotment = models.ForeignKey(
        'Allotment',
        on_delete=models.CASCADE,
        related_name='obligations'
    )

    # Description
    description = models.CharField(max_length=255)

    # Obligation amount
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )

    # Obligation date
    obligated_date = models.DateField()

    # Document reference (PO number, contract number)
    document_reference = models.CharField(max_length=100, blank=True)

    # Link to M&E activity (for tracking)
    activity = models.ForeignKey(
        'monitoring.Activity',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='obligations'
    )

    # Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    # Notes
    notes = models.TextField(blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        'common.User',
        on_delete=models.PROTECT
    )

    class Meta:
        db_table = 'budget_execution_obligation'
        ordering = ['-obligated_date']
        indexes = [
            models.Index(fields=['allotment', 'status']),
            models.Index(fields=['obligated_date']),
        ]

    def __str__(self):
        return f"{self.description} - {self.amount}"

    def clean(self):
        """Validate obligation doesn't exceed allotment"""
        # Get total obligations for this allotment
        total_obligated = self.allotment.obligations.exclude(
            pk=self.pk
        ).aggregate(
            total=models.Sum('amount')
        )['total'] or Decimal('0.00')

        total_obligated += self.amount

        if total_obligated > self.allotment.amount:
            raise ValidationError(
                f"Total obligations ({total_obligated}) exceed allotment "
                f"({self.allotment.amount})"
            )

    def get_disbursed_amount(self):
        """Calculate total disbursements"""
        return self.disbursements.aggregate(
            total=models.Sum('amount')
        )['total'] or Decimal('0.00')

    def get_remaining_balance(self):
        """Calculate remaining obligation balance"""
        return self.amount - self.get_disbursed_amount()


class Disbursement(models.Model):
    """
    Actual disbursements/payments

    Tracks actual cash outflows
    """

    # Link to obligation
    obligation = models.ForeignKey(
        'Obligation',
        on_delete=models.CASCADE,
        related_name='disbursements'
    )

    # Disbursement amount
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )

    # Disbursement date
    disbursed_date = models.DateField()

    # Payee information
    payee = models.CharField(max_length=255)

    # Check/voucher number
    check_number = models.CharField(max_length=50, blank=True)
    voucher_number = models.CharField(max_length=50, blank=True)

    # Payment method
    PAYMENT_METHODS = [
        ('check', 'Check'),
        ('bank_transfer', 'Bank Transfer'),
        ('cash', 'Cash'),
        ('other', 'Other'),
    ]

    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHODS,
        default='check'
    )

    # Notes
    notes = models.TextField(blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        'common.User',
        on_delete=models.PROTECT
    )

    class Meta:
        db_table = 'budget_execution_disbursement'
        ordering = ['-disbursed_date']
        indexes = [
            models.Index(fields=['obligation']),
            models.Index(fields=['disbursed_date']),
        ]

    def __str__(self):
        return f"{self.payee} - {self.amount} ({self.disbursed_date})"

    def clean(self):
        """Validate disbursement doesn't exceed obligation"""
        # Get total disbursements for this obligation
        total_disbursed = self.obligation.disbursements.exclude(
            pk=self.pk
        ).aggregate(
            total=models.Sum('amount')
        )['total'] or Decimal('0.00')

        total_disbursed += self.amount

        if total_disbursed > self.obligation.amount:
            raise ValidationError(
                f"Total disbursements ({total_disbursed}) exceed obligation "
                f"({self.obligation.amount})"
            )


class WorkItem(models.Model):
    """
    Detailed spending breakdown by work item

    Links spending to specific projects/activities
    """

    # Link to disbursement
    disbursement = models.ForeignKey(
        'Disbursement',
        on_delete=models.CASCADE,
        related_name='work_items'
    )

    # Link to project/activity
    project = models.ForeignKey(
        'monitoring.Project',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    activity = models.ForeignKey(
        'monitoring.Activity',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    # Cost center code
    cost_center = models.CharField(max_length=50, blank=True)

    # Amount allocated to this work item
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )

    # Description
    description = models.CharField(max_length=255)

    # Notes
    notes = models.TextField(blank=True)

    class Meta:
        db_table = 'budget_execution_work_item'
        ordering = ['project', 'activity']

    def __str__(self):
        if self.activity:
            return f"{self.activity.title} - {self.amount}"
        elif self.project:
            return f"{self.project.title} - {self.amount}"
        return f"{self.description} - {self.amount}"
```

### Relationship Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     BUDGET PREPARATION                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────┐                                          │
│  │ BudgetProposal   │ (One per fiscal year)                    │
│  │ - fiscal_year    │                                          │
│  │ - proposed_amt   │                                          │
│  │ - approved_amt   │                                          │
│  │ - status         │                                          │
│  └────────┬─────────┘                                          │
│           │                                                     │
│           │ 1:N                                                │
│           ▼                                                     │
│  ┌──────────────────┐         ┌──────────────────┐            │
│  │ ProgramBudget    │ 1:N     │ BudgetLineItem   │            │
│  │ - program (FK)   ├────────>│ - object_code    │            │
│  │ - requested_amt  │         │ - quantity       │            │
│  │ - approved_amt   │         │ - unit_cost      │            │
│  │ - strategic_goal │         │ - total_cost     │            │
│  └────────┬─────────┘         └──────────────────┘            │
│           │                                                     │
│           │ 1:N                                                │
│           ▼                                                     │
│  ┌──────────────────┐                                          │
│  │ BudgetJustif.    │                                          │
│  │ - type           │                                          │
│  │ - content        │                                          │
│  │ - evidence_doc   │                                          │
│  └──────────────────┘                                          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                           │
                           │ Approved budget feeds into execution
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                     BUDGET EXECUTION                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────┐                                          │
│  │ Allotment        │ (Quarterly releases)                     │
│  │ - program_budget │ FK to ProgramBudget                      │
│  │ - quarter        │ Q1, Q2, Q3, Q4                          │
│  │ - amount         │ ≤ approved_amount                       │
│  │ - status         │                                          │
│  └────────┬─────────┘                                          │
│           │                                                     │
│           │ 1:N                                                │
│           ▼                                                     │
│  ┌──────────────────┐                                          │
│  │ Obligation       │ (Purchase orders, contracts)            │
│  │ - allotment (FK) │                                          │
│  │ - amount         │ ≤ allotment.amount                      │
│  │ - activity (FK)  │ Link to M&E                             │
│  │ - document_ref   │                                          │
│  └────────┬─────────┘                                          │
│           │                                                     │
│           │ 1:N                                                │
│           ▼                                                     │
│  ┌──────────────────┐                                          │
│  │ Disbursement     │ (Actual payments)                        │
│  │ - obligation (FK)│                                          │
│  │ - amount         │ ≤ obligation.amount                     │
│  │ - payee          │                                          │
│  │ - check_number   │                                          │
│  └────────┬─────────┘                                          │
│           │                                                     │
│           │ 1:N                                                │
│           ▼                                                     │
│  ┌──────────────────┐                                          │
│  │ WorkItem         │ (Spending breakdown)                     │
│  │ - disbursement   │                                          │
│  │ - project (FK)   │ Link to M&E                             │
│  │ - activity (FK)  │                                          │
│  │ - amount         │                                          │
│  └──────────────────┘                                          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

FINANCIAL CONSTRAINTS:
━━━━━━━━━━━━━━━━━━━━━━━━━
1. Sum(Allotment.amount) ≤ ProgramBudget.approved_amount
2. Sum(Obligation.amount per Allotment) ≤ Allotment.amount
3. Sum(Disbursement.amount per Obligation) ≤ Obligation.amount
4. BudgetProposal.proposed_amount = Sum(ProgramBudget.requested_amount)
```

---

## Code Examples

### Budget Proposal Service

```python
# src/budget_preparation/services/budget_builder.py

from decimal import Decimal
from django.db import transaction
from django.core.exceptions import ValidationError
from ..models import BudgetProposal, ProgramBudget


class BudgetBuilderService:
    """
    Service for building and managing budget proposals
    """

    @transaction.atomic
    def create_budget_proposal(
        self,
        fiscal_year: int,
        strategic_plan,
        created_by,
        program_allocations: list
    ):
        """
        Create a new budget proposal with program allocations

        Args:
            fiscal_year: Fiscal year (e.g., 2025)
            strategic_plan: StrategicPlan instance
            created_by: User instance
            program_allocations: List of dicts with program budget data

        Returns:
            BudgetProposal instance
        """

        # Validate fiscal year
        if BudgetProposal.objects.filter(fiscal_year=fiscal_year).exists():
            raise ValidationError(
                f"Budget proposal for FY{fiscal_year} already exists"
            )

        # Calculate total proposed amount
        total_proposed = sum(
            Decimal(str(alloc['requested_amount']))
            for alloc in program_allocations
        )

        # Create budget proposal
        proposal = BudgetProposal.objects.create(
            fiscal_year=fiscal_year,
            proposed_amount=total_proposed,
            strategic_plan=strategic_plan,
            justification="Initial budget proposal",  # Will be edited later
            created_by=created_by
        )

        # Create program budgets
        for alloc in program_allocations:
            ProgramBudget.objects.create(
                budget_proposal=proposal,
                program=alloc['program'],
                requested_amount=Decimal(str(alloc['requested_amount'])),
                strategic_goal=alloc.get('strategic_goal'),
                annual_work_plan=alloc.get('annual_work_plan'),
                justification=alloc.get('justification', ''),
                priority_rank=alloc.get('priority_rank', 1),
            )

        return proposal

    def validate_budget_completeness(self, proposal: BudgetProposal):
        """
        Validate budget proposal is complete and ready for submission

        Returns:
            Tuple (is_valid: bool, errors: list)
        """
        errors = []

        # Must have at least one program budget
        if not proposal.program_budgets.exists():
            errors.append("Budget must have at least one program allocation")

        # Must have justification
        if not proposal.justification:
            errors.append("Overall budget justification is required")

        # Each program must have justification
        for program_budget in proposal.program_budgets.all():
            if not program_budget.justification:
                errors.append(
                    f"Program '{program_budget.program.name}' requires justification"
                )

        # Proposed amount must match sum of programs
        calculated_total = proposal.get_total_requested()
        if calculated_total != proposal.proposed_amount:
            errors.append(
                f"Proposed amount ({proposal.proposed_amount}) does not match "
                f"sum of program budgets ({calculated_total})"
            )

        return len(errors) == 0, errors

    @transaction.atomic
    def submit_budget_proposal(self, proposal: BudgetProposal, submission_date):
        """
        Submit budget proposal for review

        Validates completeness and changes status
        """
        # Validate completeness
        is_valid, errors = self.validate_budget_completeness(proposal)
        if not is_valid:
            raise ValidationError(errors)

        # Check status
        if proposal.status != 'draft':
            raise ValidationError(
                f"Cannot submit proposal with status '{proposal.status}'"
            )

        # Update status
        proposal.status = 'submitted'
        proposal.submission_date = submission_date
        proposal.save()

        return proposal

    @transaction.atomic
    def approve_budget_proposal(
        self,
        proposal: BudgetProposal,
        approved_amount: Decimal,
        program_approvals: dict,
        approval_date
    ):
        """
        Approve budget proposal with final amounts

        Args:
            proposal: BudgetProposal instance
            approved_amount: Total approved amount
            program_approvals: Dict mapping program_id to approved_amount
            approval_date: Date of approval
        """
        # Update proposal
        proposal.approved_amount = approved_amount
        proposal.approval_date = approval_date
        proposal.status = 'approved'
        proposal.save()

        # Update program budgets
        for program_id, approved_amt in program_approvals.items():
            program_budget = proposal.program_budgets.get(program_id=program_id)
            program_budget.approved_amount = Decimal(str(approved_amt))
            program_budget.save()

        return proposal
```

### Budget Execution Service

```python
# src/budget_execution/services/allotment_release.py

from decimal import Decimal
from django.db import transaction
from django.core.exceptions import ValidationError
from ..models import Allotment, Obligation, Disbursement


class AllotmentReleaseService:
    """
    Service for managing allotment releases
    """

    @transaction.atomic
    def release_quarterly_allotment(
        self,
        program_budget,
        quarter: int,
        amount: Decimal,
        release_date,
        created_by
    ):
        """
        Release quarterly allotment

        Args:
            program_budget: ProgramBudget instance (must be approved)
            quarter: Quarter (1, 2, 3, 4)
            amount: Allotment amount
            release_date: Release date
            created_by: User instance

        Returns:
            Allotment instance
        """

        # Validate program budget is approved
        if not program_budget.approved_amount:
            raise ValidationError(
                "Cannot release allotment for unapproved program budget"
            )

        # Check if allotment already exists
        if Allotment.objects.filter(
            program_budget=program_budget,
            quarter=quarter
        ).exists():
            raise ValidationError(
                f"Allotment for Q{quarter} already exists"
            )

        # Validate total allotments don't exceed approved budget
        existing_allotments = Allotment.objects.filter(
            program_budget=program_budget
        ).aggregate(total=models.Sum('amount'))['total'] or Decimal('0.00')

        if existing_allotments + amount > program_budget.approved_amount:
            raise ValidationError(
                f"Total allotments ({existing_allotments + amount}) would exceed "
                f"approved budget ({program_budget.approved_amount})"
            )

        # Create allotment
        allotment = Allotment.objects.create(
            program_budget=program_budget,
            quarter=quarter,
            amount=amount,
            status='released',
            release_date=release_date,
            created_by=created_by
        )

        return allotment

    @transaction.atomic
    def record_obligation(
        self,
        allotment: Allotment,
        description: str,
        amount: Decimal,
        obligated_date,
        activity=None,
        document_reference='',
        created_by=None
    ):
        """
        Record obligation against allotment

        Args:
            allotment: Allotment instance
            description: Description of obligation
            amount: Obligation amount
            obligated_date: Date of obligation
            activity: Optional M&E Activity instance
            document_reference: PO number, contract number, etc.
            created_by: User instance

        Returns:
            Obligation instance
        """

        # Validate allotment is released
        if allotment.status not in ['released', 'partially_utilized']:
            raise ValidationError(
                f"Cannot obligate against allotment with status '{allotment.status}'"
            )

        # Validate doesn't exceed allotment
        existing_obligations = allotment.obligations.aggregate(
            total=models.Sum('amount')
        )['total'] or Decimal('0.00')

        if existing_obligations + amount > allotment.amount:
            raise ValidationError(
                f"Total obligations ({existing_obligations + amount}) would exceed "
                f"allotment ({allotment.amount})"
            )

        # Create obligation
        obligation = Obligation.objects.create(
            allotment=allotment,
            description=description,
            amount=amount,
            obligated_date=obligated_date,
            activity=activity,
            document_reference=document_reference,
            status='committed',
            created_by=created_by
        )

        # Update allotment status
        if existing_obligations + amount >= allotment.amount:
            allotment.status = 'fully_utilized'
        else:
            allotment.status = 'partially_utilized'
        allotment.save()

        return obligation

    @transaction.atomic
    def record_disbursement(
        self,
        obligation: Obligation,
        amount: Decimal,
        disbursed_date,
        payee: str,
        payment_method: str,
        check_number='',
        voucher_number='',
        created_by=None
    ):
        """
        Record disbursement against obligation

        Args:
            obligation: Obligation instance
            amount: Disbursement amount
            disbursed_date: Date of disbursement
            payee: Payee name
            payment_method: Payment method (check, bank_transfer, etc.)
            check_number: Check number (if applicable)
            voucher_number: Voucher number
            created_by: User instance

        Returns:
            Disbursement instance
        """

        # Validate doesn't exceed obligation
        existing_disbursements = obligation.disbursements.aggregate(
            total=models.Sum('amount')
        )['total'] or Decimal('0.00')

        if existing_disbursements + amount > obligation.amount:
            raise ValidationError(
                f"Total disbursements ({existing_disbursements + amount}) would exceed "
                f"obligation ({obligation.amount})"
            )

        # Create disbursement
        disbursement = Disbursement.objects.create(
            obligation=obligation,
            amount=amount,
            disbursed_date=disbursed_date,
            payee=payee,
            payment_method=payment_method,
            check_number=check_number,
            voucher_number=voucher_number,
            created_by=created_by
        )

        # Update obligation status
        if existing_disbursements + amount >= obligation.amount:
            obligation.status = 'fully_disbursed'
        else:
            obligation.status = 'partially_disbursed'
        obligation.save()

        return disbursement


class BudgetUtilizationService:
    """
    Service for budget utilization tracking and reporting
    """

    def get_program_utilization_summary(self, program_budget):
        """
        Get budget utilization summary for a program

        Returns:
            Dict with utilization metrics
        """
        approved = program_budget.approved_amount or Decimal('0.00')

        # Total allotments
        allotted = program_budget.allotments.aggregate(
            total=models.Sum('amount')
        )['total'] or Decimal('0.00')

        # Total obligations
        obligated = Obligation.objects.filter(
            allotment__program_budget=program_budget
        ).aggregate(
            total=models.Sum('amount')
        )['total'] or Decimal('0.00')

        # Total disbursements
        disbursed = Disbursement.objects.filter(
            obligation__allotment__program_budget=program_budget
        ).aggregate(
            total=models.Sum('amount')
        )['total'] or Decimal('0.00')

        return {
            'approved_amount': approved,
            'allotted_amount': allotted,
            'obligated_amount': obligated,
            'disbursed_amount': disbursed,
            'allotment_rate': (allotted / approved * 100) if approved else Decimal('0.00'),
            'obligation_rate': (obligated / approved * 100) if approved else Decimal('0.00'),
            'disbursement_rate': (disbursed / approved * 100) if approved else Decimal('0.00'),
            'remaining_balance': approved - disbursed,
        }

    def get_quarterly_spending_trend(self, budget_proposal):
        """
        Get quarterly spending trend for entire budget

        Returns:
            List of dicts with quarterly data
        """
        fiscal_year = budget_proposal.fiscal_year

        quarterly_data = []

        for quarter in [1, 2, 3, 4]:
            # Get allotments for this quarter
            allotments = Allotment.objects.filter(
                program_budget__budget_proposal=budget_proposal,
                quarter=quarter
            )

            allotted = allotments.aggregate(
                total=models.Sum('amount')
            )['total'] or Decimal('0.00')

            # Get obligations for this quarter
            obligated = Obligation.objects.filter(
                allotment__in=allotments
            ).aggregate(
                total=models.Sum('amount')
            )['total'] or Decimal('0.00')

            # Get disbursements for this quarter
            disbursed = Disbursement.objects.filter(
                obligation__allotment__in=allotments
            ).aggregate(
                total=models.Sum('amount')
            )['total'] or Decimal('0.00')

            quarterly_data.append({
                'quarter': quarter,
                'quarter_label': f'Q{quarter}',
                'allotted': allotted,
                'obligated': obligated,
                'disbursed': disbursed,
            })

        return quarterly_data
```

---

## UI/UX Specifications

### Budget Dashboard (Stat Cards)

Following **OBCMS UI Standards** (3D Milk White Stat Cards):

```html
<!-- Budget Executive Dashboard -->
<!-- src/templates/budget_execution/dashboard.html -->

{% extends "common/base_with_sidebar.html" %}

{% block content %}
<div class="container mx-auto px-4 py-8">

    <!-- Page Header -->
    <div class="mb-8">
        <h1 class="text-3xl font-bold text-gray-900 mb-2">
            <i class="fas fa-chart-line text-blue-600 mr-2"></i>
            Budget Execution Dashboard
        </h1>
        <p class="text-gray-600">FY{{ fiscal_year }} Budget Performance</p>
    </div>

    <!-- Stat Cards Grid (4 columns) -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">

        <!-- Total Budget (Approved) -->
        <div class="relative overflow-hidden bg-gradient-to-br from-[#FEFDFB] to-[#FBF9F5] rounded-2xl transform hover:-translate-y-2 transition-all duration-300"
             style="box-shadow: 0 8px 20px rgba(0,0,0,0.08), 0 2px 8px rgba(0,0,0,0.06), inset 0 -2px 4px rgba(0,0,0,0.02), inset 0 2px 4px rgba(255,255,255,0.9);">
            <div class="absolute inset-0 bg-gradient-to-br from-white/60 via-transparent to-gray-100/20"></div>
            <div class="relative p-6">
                <div class="flex items-center justify-between">
                    <div>
                        <p class="text-gray-600 text-sm font-semibold uppercase tracking-wide">Total Budget</p>
                        <p class="text-4xl font-extrabold text-gray-800 mt-1">₱{{ approved_amount|floatformat:0 }}</p>
                    </div>
                    <div class="w-16 h-16 rounded-2xl flex items-center justify-center"
                         style="background: linear-gradient(135deg, #FFFFFF 0%, #F5F3F0 100%); box-shadow: 0 4px 12px rgba(0,0,0,0.1), inset 0 -2px 4px rgba(0,0,0,0.05), inset 0 2px 4px rgba(255,255,255,0.8);">
                        <i class="fas fa-wallet text-2xl text-amber-600"></i>
                    </div>
                </div>
            </div>
        </div>

        <!-- Allotted -->
        <div class="relative overflow-hidden bg-gradient-to-br from-[#FEFDFB] to-[#FBF9F5] rounded-2xl transform hover:-translate-y-2 transition-all duration-300"
             style="box-shadow: 0 8px 20px rgba(0,0,0,0.08), 0 2px 8px rgba(0,0,0,0.06), inset 0 -2px 4px rgba(0,0,0,0.02), inset 0 2px 4px rgba(255,255,255,0.9);">
            <div class="absolute inset-0 bg-gradient-to-br from-white/60 via-transparent to-gray-100/20"></div>
            <div class="relative p-6">
                <div class="flex items-center justify-between">
                    <div>
                        <p class="text-gray-600 text-sm font-semibold uppercase tracking-wide">Allotted</p>
                        <p class="text-4xl font-extrabold text-gray-800 mt-1">₱{{ allotted_amount|floatformat:0 }}</p>
                        <p class="text-xs text-emerald-600 font-medium mt-1">{{ allotment_rate|floatformat:1 }}% of budget</p>
                    </div>
                    <div class="w-16 h-16 rounded-2xl flex items-center justify-center"
                         style="background: linear-gradient(135deg, #FFFFFF 0%, #F5F3F0 100%); box-shadow: 0 4px 12px rgba(0,0,0,0.1), inset 0 -2px 4px rgba(0,0,0,0.05), inset 0 2px 4px rgba(255,255,255,0.8);">
                        <i class="fas fa-hand-holding-usd text-2xl text-blue-600"></i>
                    </div>
                </div>
            </div>
        </div>

        <!-- Obligated -->
        <div class="relative overflow-hidden bg-gradient-to-br from-[#FEFDFB] to-[#FBF9F5] rounded-2xl transform hover:-translate-y-2 transition-all duration-300"
             style="box-shadow: 0 8px 20px rgba(0,0,0,0.08), 0 2px 8px rgba(0,0,0,0.06), inset 0 -2px 4px rgba(0,0,0,0.02), inset 0 2px 4px rgba(255,255,255,0.9);">
            <div class="absolute inset-0 bg-gradient-to-br from-white/60 via-transparent to-gray-100/20"></div>
            <div class="relative p-6">
                <div class="flex items-center justify-between">
                    <div>
                        <p class="text-gray-600 text-sm font-semibold uppercase tracking-wide">Obligated</p>
                        <p class="text-4xl font-extrabold text-gray-800 mt-1">₱{{ obligated_amount|floatformat:0 }}</p>
                        <p class="text-xs text-purple-600 font-medium mt-1">{{ obligation_rate|floatformat:1 }}% of budget</p>
                    </div>
                    <div class="w-16 h-16 rounded-2xl flex items-center justify-center"
                         style="background: linear-gradient(135deg, #FFFFFF 0%, #F5F3F0 100%); box-shadow: 0 4px 12px rgba(0,0,0,0.1), inset 0 -2px 4px rgba(0,0,0,0.05), inset 0 2px 4px rgba(255,255,255,0.8);">
                        <i class="fas fa-file-contract text-2xl text-purple-600"></i>
                    </div>
                </div>
            </div>
        </div>

        <!-- Disbursed -->
        <div class="relative overflow-hidden bg-gradient-to-br from-[#FEFDFB] to-[#FBF9F5] rounded-2xl transform hover:-translate-y-2 transition-all duration-300"
             style="box-shadow: 0 8px 20px rgba(0,0,0,0.08), 0 2px 8px rgba(0,0,0,0.06), inset 0 -2px 4px rgba(0,0,0,0.02), inset 0 2px 4px rgba(255,255,255,0.9);">
            <div class="absolute inset-0 bg-gradient-to-br from-white/60 via-transparent to-gray-100/20"></div>
            <div class="relative p-6">
                <div class="flex items-center justify-between">
                    <div>
                        <p class="text-gray-600 text-sm font-semibold uppercase tracking-wide">Disbursed</p>
                        <p class="text-4xl font-extrabold text-gray-800 mt-1">₱{{ disbursed_amount|floatformat:0 }}</p>
                        <p class="text-xs text-emerald-600 font-medium mt-1">{{ disbursement_rate|floatformat:1 }}% of budget</p>
                    </div>
                    <div class="w-16 h-16 rounded-2xl flex items-center justify-center"
                         style="background: linear-gradient(135deg, #FFFFFF 0%, #F5F3F0 100%); box-shadow: 0 4px 12px rgba(0,0,0,0.1), inset 0 -2px 4px rgba(0,0,0,0.05), inset 0 2px 4px rgba(255,255,255,0.8);">
                        <i class="fas fa-money-check-alt text-2xl text-emerald-600"></i>
                    </div>
                </div>
            </div>
        </div>

    </div>

    <!-- Budget Execution Chart -->
    <div class="bg-white rounded-xl shadow-md border border-gray-200 p-6 mb-8">
        <h2 class="text-xl font-semibold text-gray-900 mb-4">
            <i class="fas fa-chart-bar text-blue-600 mr-2"></i>
            Quarterly Budget Execution
        </h2>
        <canvas id="budgetExecutionChart" width="800" height="300"></canvas>
    </div>

    <!-- Program-wise Utilization Table -->
    <div class="bg-white shadow-md rounded-xl overflow-hidden border border-gray-200">
        <div class="bg-gradient-to-r from-blue-600 to-emerald-600 px-6 py-4">
            <h2 class="text-xl font-semibold text-white">
                <i class="fas fa-list-alt mr-2"></i>
                Program-wise Budget Utilization
            </h2>
        </div>
        <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
                <tr>
                    <th class="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Program</th>
                    <th class="px-6 py-3 text-right text-xs font-semibold text-gray-700 uppercase tracking-wider">Approved</th>
                    <th class="px-6 py-3 text-right text-xs font-semibold text-gray-700 uppercase tracking-wider">Allotted</th>
                    <th class="px-6 py-3 text-right text-xs font-semibold text-gray-700 uppercase tracking-wider">Obligated</th>
                    <th class="px-6 py-3 text-right text-xs font-semibold text-gray-700 uppercase tracking-wider">Disbursed</th>
                    <th class="px-6 py-3 text-right text-xs font-semibold text-gray-700 uppercase tracking-wider">Utilization</th>
                </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
                {% for program in programs %}
                <tr class="hover:bg-gray-50 transition-colors duration-200">
                    <td class="px-6 py-4 whitespace-nowrap">
                        <div class="text-sm font-medium text-gray-900">{{ program.name }}</div>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-right text-sm text-gray-900">
                        ₱{{ program.approved|floatformat:0 }}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-right text-sm text-gray-900">
                        ₱{{ program.allotted|floatformat:0 }}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-right text-sm text-gray-900">
                        ₱{{ program.obligated|floatformat:0 }}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-right text-sm text-gray-900">
                        ₱{{ program.disbursed|floatformat:0 }}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-right">
                        <div class="flex items-center justify-end">
                            <span class="text-sm font-semibold text-gray-900 mr-2">
                                {{ program.utilization_rate|floatformat:1 }}%
                            </span>
                            <div class="w-24 h-2 bg-gray-200 rounded-full">
                                <div class="h-2 bg-emerald-600 rounded-full"
                                     style="width: {{ program.utilization_rate }}%"></div>
                            </div>
                        </div>
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>

</div>

{% block extra_js %}
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.js"></script>
<script>
// Budget Execution Chart
const ctx = document.getElementById('budgetExecutionChart').getContext('2d');
const chart = new Chart(ctx, {
    type: 'bar',
    data: {
        labels: ['Q1', 'Q2', 'Q3', 'Q4'],
        datasets: [
            {
                label: 'Allotted',
                data: {{ quarterly_allotted|safe }},
                backgroundColor: 'rgba(37, 99, 235, 0.7)',  // Blue
                borderColor: 'rgba(37, 99, 235, 1)',
                borderWidth: 1
            },
            {
                label: 'Obligated',
                data: {{ quarterly_obligated|safe }},
                backgroundColor: 'rgba(124, 58, 237, 0.7)',  // Purple
                borderColor: 'rgba(124, 58, 237, 1)',
                borderWidth: 1
            },
            {
                label: 'Disbursed',
                data: {{ quarterly_disbursed|safe }},
                backgroundColor: 'rgba(5, 150, 105, 0.7)',  // Emerald
                borderColor: 'rgba(5, 150, 105, 1)',
                borderWidth: 1
            }
        ]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
            y: {
                beginAtZero: true,
                ticks: {
                    callback: function(value) {
                        return '₱' + value.toLocaleString();
                    }
                }
            }
        },
        plugins: {
            legend: {
                position: 'top',
            },
            tooltip: {
                callbacks: {
                    label: function(context) {
                        return context.dataset.label + ': ₱' +
                               context.parsed.y.toLocaleString();
                    }
                }
            }
        }
    }
});
</script>
{% endblock %}

{% endblock %}
```

### Budget Forms (Standard Dropdown Pattern)

```html
<!-- Budget Preparation Form -->
<!-- src/templates/budget_preparation/program_budget_form.html -->

<form method="post" action="{% url 'budget_preparation:program_budget_create' proposal.id %}">
    {% csrf_token %}

    <!-- Program Selection -->
    <div class="space-y-1 mb-4">
        <label for="program-select" class="block text-sm font-medium text-gray-700 mb-2">
            Program<span class="text-red-500">*</span>
        </label>
        <div class="relative">
            <select id="program-select"
                    name="program"
                    class="block w-full py-3 px-4 text-base rounded-xl border border-gray-200 shadow-sm focus:ring-emerald-500 focus:border-emerald-500 min-h-[48px] appearance-none pr-12 bg-white transition-all duration-200"
                    required>
                <option value="">Select program...</option>
                {% for program in programs %}
                <option value="{{ program.id }}">{{ program.name }}</option>
                {% endfor %}
            </select>
            <span class="pointer-events-none absolute inset-y-0 right-0 flex items-center pr-4">
                <i class="fas fa-chevron-down text-gray-400 text-sm"></i>
            </span>
        </div>
    </div>

    <!-- Requested Amount -->
    <div class="mb-4">
        <label for="requested-amount" class="block text-sm font-medium text-gray-700 mb-2">
            Requested Amount<span class="text-red-500">*</span>
        </label>
        <div class="relative">
            <span class="absolute left-4 top-1/2 -translate-y-1/2 text-gray-500">₱</span>
            <input type="number"
                   id="requested-amount"
                   name="requested_amount"
                   step="0.01"
                   min="0.01"
                   class="w-full pl-8 pr-4 py-3 text-base rounded-xl border border-gray-200 shadow-sm focus:ring-emerald-500 focus:border-emerald-500 min-h-[48px] transition-all duration-200"
                   placeholder="0.00"
                   required>
        </div>
        <p class="mt-1 text-sm text-gray-500">Enter amount in Philippine Pesos</p>
    </div>

    <!-- Strategic Goal (Optional) -->
    <div class="space-y-1 mb-4">
        <label for="strategic-goal-select" class="block text-sm font-medium text-gray-700 mb-2">
            Strategic Goal (Optional)
        </label>
        <div class="relative">
            <select id="strategic-goal-select"
                    name="strategic_goal"
                    class="block w-full py-3 px-4 text-base rounded-xl border border-gray-200 shadow-sm focus:ring-emerald-500 focus:border-emerald-500 min-h-[48px] appearance-none pr-12 bg-white transition-all duration-200">
                <option value="">No strategic goal linkage</option>
                {% for goal in strategic_goals %}
                <option value="{{ goal.id }}">{{ goal.title }}</option>
                {% endfor %}
            </select>
            <span class="pointer-events-none absolute inset-y-0 right-0 flex items-center pr-4">
                <i class="fas fa-chevron-down text-gray-400 text-sm"></i>
            </span>
        </div>
    </div>

    <!-- Justification -->
    <div class="mb-4">
        <label for="justification" class="block text-sm font-medium text-gray-700 mb-2">
            Justification<span class="text-red-500">*</span>
        </label>
        <textarea id="justification"
                  name="justification"
                  rows="4"
                  class="w-full px-4 py-3 text-base rounded-xl border border-gray-200 shadow-sm focus:ring-emerald-500 focus:border-emerald-500 transition-all duration-200 resize-vertical"
                  placeholder="Provide justification for this budget request..."
                  required></textarea>
        <p class="mt-1 text-sm text-gray-500">Explain why this program requires funding</p>
    </div>

    <!-- Submit Row -->
    <div class="flex flex-col sm:flex-row justify-end space-y-2 sm:space-y-0 sm:space-x-3 pt-6 border-t border-gray-200">
        <button type="button"
                onclick="window.history.back()"
                class="px-6 py-3 border-2 border-gray-300 text-gray-700 rounded-xl hover:bg-gray-50 transition-colors duration-200">
            <i class="fas fa-times mr-2"></i>
            Cancel
        </button>
        <button type="submit"
                class="bg-gradient-to-r from-blue-600 to-emerald-600 text-white px-6 py-3 rounded-xl font-semibold hover:shadow-lg hover:-translate-y-1 transition-all duration-300">
            <i class="fas fa-save mr-2"></i>
            Save Program Budget
        </button>
    </div>

</form>
```

---

## Financial Business Rules

### Budget Constraints

**CRITICAL:** These constraints MUST be enforced at database and application level.

```python
# Financial Constraint Rules

# 1. Budget Proposal Constraint
BudgetProposal.proposed_amount == Sum(ProgramBudget.requested_amount)
# Enforced: In model clean() and service layer

# 2. Allotment Constraint
Sum(Allotment.amount per ProgramBudget) <= ProgramBudget.approved_amount
# Enforced: In Allotment.clean() method

# 3. Obligation Constraint
Sum(Obligation.amount per Allotment) <= Allotment.amount
# Enforced: In Obligation.clean() method

# 4. Disbursement Constraint
Sum(Disbursement.amount per Obligation) <= Obligation.amount
# Enforced: In Disbursement.clean() method

# 5. Fiscal Year Uniqueness
Only ONE BudgetProposal per fiscal_year
# Enforced: unique_together constraint
```

### Allotment Validation Rules

```python
def validate_allotment_release(program_budget, quarter, amount):
    """
    Validation rules for allotment release

    Returns:
        Tuple (is_valid: bool, error_message: str)
    """

    # Rule 1: Program budget must be approved
    if not program_budget.approved_amount:
        return False, "Cannot release allotment for unapproved program budget"

    # Rule 2: Quarter must not already have allotment
    if Allotment.objects.filter(
        program_budget=program_budget,
        quarter=quarter
    ).exists():
        return False, f"Allotment for Q{quarter} already exists"

    # Rule 3: Total allotments cannot exceed approved budget
    existing_total = program_budget.allotments.aggregate(
        total=models.Sum('amount')
    )['total'] or Decimal('0.00')

    if existing_total + amount > program_budget.approved_amount:
        return False, (
            f"Total allotments ({existing_total + amount}) would exceed "
            f"approved budget ({program_budget.approved_amount})"
        )

    # Rule 4: Amount must be positive
    if amount <= 0:
        return False, "Allotment amount must be positive"

    return True, ""
```

### Obligation Rules

```python
def validate_obligation(allotment, amount):
    """
    Validation rules for obligation recording

    Returns:
        Tuple (is_valid: bool, error_message: str)
    """

    # Rule 1: Allotment must be released
    if allotment.status not in ['released', 'partially_utilized']:
        return False, f"Cannot obligate against allotment with status '{allotment.status}'"

    # Rule 2: Cannot exceed allotment
    existing_obligations = allotment.obligations.aggregate(
        total=models.Sum('amount')
    )['total'] or Decimal('0.00')

    if existing_obligations + amount > allotment.amount:
        return False, (
            f"Total obligations ({existing_obligations + amount}) would exceed "
            f"allotment ({allotment.amount})"
        )

    # Rule 3: Amount must be positive
    if amount <= 0:
        return False, "Obligation amount must be positive"

    return True, ""
```

### Disbursement Constraints

```python
def validate_disbursement(obligation, amount):
    """
    Validation rules for disbursement recording

    Returns:
        Tuple (is_valid: bool, error_message: str)
    """

    # Rule 1: Cannot exceed obligation
    existing_disbursements = obligation.disbursements.aggregate(
        total=models.Sum('amount')
    )['total'] or Decimal('0.00')

    if existing_disbursements + amount > obligation.amount:
        return False, (
            f"Total disbursements ({existing_disbursements + amount}) would exceed "
            f"obligation ({obligation.amount})"
        )

    # Rule 2: Amount must be positive
    if amount <= 0:
        return False, "Disbursement amount must be positive"

    return True, ""
```

### Variance Thresholds

```python
# Variance Alert Thresholds

VARIANCE_THRESHOLDS = {
    'budget_overrun_warning': 0.95,  # Warn at 95% budget utilization
    'budget_overrun_critical': 1.00,  # Critical at 100%
    'under_spending_warning': 0.50,   # Warn if only 50% spent by Q3
    'program_variance_threshold': 0.10,  # 10% variance between requested and approved
}

def check_budget_variance_alerts(program_budget):
    """
    Check for budget variance alerts

    Returns:
        List of alert dicts
    """
    alerts = []

    utilization_rate = program_budget.get_utilization_rate()

    # Check overrun
    if utilization_rate >= VARIANCE_THRESHOLDS['budget_overrun_critical']:
        alerts.append({
            'level': 'critical',
            'message': f"Budget fully utilized ({utilization_rate:.1f}%)"
        })
    elif utilization_rate >= VARIANCE_THRESHOLDS['budget_overrun_warning']:
        alerts.append({
            'level': 'warning',
            'message': f"Budget almost exhausted ({utilization_rate:.1f}%)"
        })

    # Check underspending (if Q3 or later)
    current_quarter = get_current_quarter()
    if current_quarter >= 3:
        if utilization_rate < VARIANCE_THRESHOLDS['under_spending_warning'] * 100:
            alerts.append({
                'level': 'info',
                'message': f"Low budget utilization ({utilization_rate:.1f}%)"
            })

    return alerts
```

---

## Integration Points

### Planning Module Integration

```python
# Link program budgets to strategic goals and annual plans

class ProgramBudget(models.Model):
    # ... other fields ...

    # Link to strategic goal
    strategic_goal = models.ForeignKey(
        'planning.StrategicGoal',
        on_delete=models.SET_NULL,
        null=True,
        related_name='program_budgets'
    )

    # Link to annual work plan
    annual_work_plan = models.ForeignKey(
        'planning.AnnualWorkPlan',
        on_delete=models.SET_NULL,
        null=True,
        related_name='program_budgets'
    )

    def check_strategic_alignment(self):
        """
        Check if budget aligns with strategic plan

        Returns:
            Bool indicating alignment
        """
        if not self.strategic_goal:
            return False

        # Check if strategic goal is active
        if not self.strategic_goal.strategic_plan.status == 'active':
            return False

        return True
```

### M&E Module Integration

```python
# Link obligations to activities for financial tracking

class Obligation(models.Model):
    # ... other fields ...

    # Link to M&E activity
    activity = models.ForeignKey(
        'monitoring.Activity',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='obligations'
    )

    def get_activity_spending_summary(self):
        """
        Get spending summary for linked activity

        Returns:
            Dict with spending metrics
        """
        if not self.activity:
            return None

        total_obligated = self.activity.obligations.aggregate(
            total=models.Sum('amount')
        )['total'] or Decimal('0.00')

        total_disbursed = Disbursement.objects.filter(
            obligation__activity=self.activity
        ).aggregate(
            total=models.Sum('amount')
        )['total'] or Decimal('0.00')

        return {
            'activity': self.activity,
            'total_obligated': total_obligated,
            'total_disbursed': total_disbursed,
            'completion_rate': self.activity.get_completion_percentage(),
            'spending_rate': (total_disbursed / total_obligated * 100) if total_obligated else Decimal('0.00'),
        }
```

### Activity Tracking Integration

```python
# Financial performance tracking per activity

def get_activity_financial_performance(activity):
    """
    Get financial performance metrics for an activity

    Returns:
        Dict with performance data
    """

    # Get budget allocation
    program = activity.parent_program
    program_budget = program.budgets.filter(
        budget_proposal__status='approved'
    ).order_by('-budget_proposal__fiscal_year').first()

    if not program_budget:
        return None

    # Get spending
    obligations = activity.obligations.all()
    total_obligated = obligations.aggregate(
        total=models.Sum('amount')
    )['total'] or Decimal('0.00')

    disbursements = Disbursement.objects.filter(
        obligation__in=obligations
    )
    total_disbursed = disbursements.aggregate(
        total=models.Sum('amount')
    )['total'] or Decimal('0.00')

    # Get completion
    completion_rate = activity.get_completion_percentage()

    # Calculate efficiency
    spending_rate = (total_disbursed / program_budget.approved_amount * 100) if program_budget.approved_amount else Decimal('0.00')

    return {
        'activity': activity,
        'program_budget': program_budget.approved_amount,
        'obligated': total_obligated,
        'disbursed': total_disbursed,
        'completion_rate': completion_rate,
        'spending_rate': spending_rate,
        'efficiency_ratio': (completion_rate / spending_rate) if spending_rate else Decimal('0.00'),
    }
```

---

## Testing Strategy

### Model Tests

```python
# tests/budget_preparation/test_models.py

from decimal import Decimal
from django.test import TestCase
from django.core.exceptions import ValidationError
from budget_preparation.models import BudgetProposal, ProgramBudget
from monitoring.models import Program


class BudgetProposalModelTest(TestCase):
    """Test budget proposal model"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.program = Program.objects.create(
            name='Education Support Program',
            description='Test program'
        )

    def test_create_budget_proposal(self):
        """Test creating budget proposal"""
        proposal = BudgetProposal.objects.create(
            fiscal_year=2025,
            proposed_amount=Decimal('50000000.00'),
            justification='FY2025 budget proposal',
            created_by=self.user
        )

        self.assertEqual(proposal.fiscal_year, 2025)
        self.assertEqual(proposal.proposed_amount, Decimal('50000000.00'))
        self.assertEqual(proposal.status, 'draft')

    def test_fiscal_year_uniqueness(self):
        """Test only one budget per fiscal year"""
        BudgetProposal.objects.create(
            fiscal_year=2025,
            proposed_amount=Decimal('50000000.00'),
            justification='FY2025 budget',
            created_by=self.user
        )

        # Try to create duplicate
        with self.assertRaises(Exception):
            BudgetProposal.objects.create(
                fiscal_year=2025,
                proposed_amount=Decimal('60000000.00'),
                justification='Duplicate',
                created_by=self.user
            )

    def test_get_total_requested(self):
        """Test calculating total from program budgets"""
        proposal = BudgetProposal.objects.create(
            fiscal_year=2025,
            proposed_amount=Decimal('50000000.00'),
            justification='Test',
            created_by=self.user
        )

        ProgramBudget.objects.create(
            budget_proposal=proposal,
            program=self.program,
            requested_amount=Decimal('30000000.00'),
            justification='Test'
        )

        total = proposal.get_total_requested()
        self.assertEqual(total, Decimal('30000000.00'))


class ProgramBudgetConstraintTest(TestCase):
    """Test financial constraints"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.program = Program.objects.create(
            name='Test Program',
            description='Test'
        )
        self.proposal = BudgetProposal.objects.create(
            fiscal_year=2025,
            proposed_amount=Decimal('100000000.00'),
            justification='Test',
            created_by=self.user
        )
        self.program_budget = ProgramBudget.objects.create(
            budget_proposal=self.proposal,
            program=self.program,
            requested_amount=Decimal('50000000.00'),
            approved_amount=Decimal('40000000.00'),
            justification='Test'
        )

    def test_allotment_cannot_exceed_approved(self):
        """Test allotment constraint"""
        from budget_execution.models import Allotment

        # Try to create allotment exceeding approved amount
        allotment = Allotment(
            program_budget=self.program_budget,
            quarter=1,
            amount=Decimal('50000000.00'),  # Exceeds approved
            created_by=self.user
        )

        with self.assertRaises(ValidationError):
            allotment.clean()
```

### View Tests

```python
# tests/budget_preparation/test_views.py

from django.test import TestCase, Client
from django.urls import reverse
from budget_preparation.models import BudgetProposal


class BudgetProposalViewTest(TestCase):
    """Test budget proposal views"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')

    def test_budget_proposal_list_view(self):
        """Test listing budget proposals"""
        url = reverse('budget_preparation:proposal_list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'budget_preparation/proposal_list.html')

    def test_create_budget_proposal(self):
        """Test creating budget proposal"""
        url = reverse('budget_preparation:proposal_create')
        data = {
            'fiscal_year': 2025,
            'proposed_amount': '50000000.00',
            'justification': 'Test budget proposal',
        }

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 302)  # Redirect on success
        self.assertTrue(BudgetProposal.objects.filter(fiscal_year=2025).exists())
```

### Integration Tests

```python
# tests/budget_execution/test_integration.py

from django.test import TestCase
from decimal import Decimal
from budget_preparation.models import BudgetProposal, ProgramBudget
from budget_execution.models import Allotment, Obligation, Disbursement
from budget_execution.services import AllotmentReleaseService


class BudgetExecutionIntegrationTest(TestCase):
    """Test full budget execution workflow"""

    def setUp(self):
        self.service = AllotmentReleaseService()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

        # Create approved budget
        self.proposal = BudgetProposal.objects.create(
            fiscal_year=2025,
            proposed_amount=Decimal('100000000.00'),
            approved_amount=Decimal('90000000.00'),
            status='approved',
            created_by=self.user
        )

        self.program = Program.objects.create(
            name='Test Program',
            description='Test'
        )

        self.program_budget = ProgramBudget.objects.create(
            budget_proposal=self.proposal,
            program=self.program,
            requested_amount=Decimal('50000000.00'),
            approved_amount=Decimal('40000000.00'),
            justification='Test'
        )

    def test_full_execution_cycle(self):
        """Test complete budget execution cycle"""

        # Step 1: Release allotment
        allotment = self.service.release_quarterly_allotment(
            program_budget=self.program_budget,
            quarter=1,
            amount=Decimal('10000000.00'),
            release_date='2025-01-15',
            created_by=self.user
        )

        self.assertEqual(allotment.amount, Decimal('10000000.00'))
        self.assertEqual(allotment.status, 'released')

        # Step 2: Record obligation
        obligation = self.service.record_obligation(
            allotment=allotment,
            description='Purchase of equipment',
            amount=Decimal('5000000.00'),
            obligated_date='2025-02-01',
            document_reference='PO-2025-001',
            created_by=self.user
        )

        self.assertEqual(obligation.amount, Decimal('5000000.00'))
        self.assertEqual(obligation.status, 'committed')

        # Step 3: Record disbursement
        disbursement = self.service.record_disbursement(
            obligation=obligation,
            amount=Decimal('5000000.00'),
            disbursed_date='2025-02-15',
            payee='XYZ Company',
            payment_method='check',
            check_number='CHK-001',
            created_by=self.user
        )

        self.assertEqual(disbursement.amount, Decimal('5000000.00'))

        # Verify balances
        self.assertEqual(
            allotment.get_remaining_balance(),
            Decimal('5000000.00')  # 10M - 5M
        )
        self.assertEqual(
            obligation.get_remaining_balance(),
            Decimal('0.00')  # Fully disbursed
        )
```

---

## Success Criteria

### Phase 2A: Budget Preparation ✅

**Completion Criteria:**

- [ ] All 4 models created and migrated
- [ ] Admin interface functional
- [ ] Budget proposal CRUD working
- [ ] Program budget allocation interface complete
- [ ] Submission workflow implemented (draft → submitted → approved)
- [ ] Planning integration complete (strategic goals, annual plans)
- [ ] M&E integration complete (program linkage)
- [ ] Justification management working
- [ ] Budget validation rules enforced
- [ ] 80%+ test coverage

**Acceptance Tests:**

1. **Create Budget Proposal**
   - User can create new budget proposal for fiscal year
   - System prevents duplicate fiscal years
   - Proposed amount calculated from program budgets

2. **Allocate Program Budgets**
   - User can add multiple program budgets
   - Each program linked to M&E program
   - Optional strategic goal linkage
   - Justifications required

3. **Submit for Approval**
   - User can submit complete budget proposal
   - System validates completeness
   - Status changes to "submitted"

4. **Approve Budget**
   - Approver can review and approve
   - Approved amounts can differ from requested
   - Status changes to "approved"

---

### Phase 2B: Budget Execution ✅

**Completion Criteria:**

- [ ] All 4 execution models created and migrated
- [ ] Allotment release system working
- [ ] Obligation recording functional
- [ ] Disbursement tracking complete
- [ ] Financial constraints enforced at all levels
- [ ] Budget utilization dashboard operational
- [ ] Financial reports generated
- [ ] Variance analysis working
- [ ] Activity-level spending tracked
- [ ] 80%+ test coverage

**Acceptance Tests:**

1. **Release Quarterly Allotment**
   - User can release quarterly allotments
   - System enforces: total allotments ≤ approved budget
   - Allotment order numbers tracked

2. **Record Obligation**
   - User can record obligations against allotments
   - System enforces: obligations ≤ allotment
   - Activity linkage optional

3. **Record Disbursement**
   - User can record disbursements
   - System enforces: disbursements ≤ obligation
   - Payee and check information captured

4. **Financial Dashboard**
   - Dashboard displays budget execution metrics
   - Stat cards show approved, allotted, obligated, disbursed
   - Quarterly trend chart displays correctly
   - Program-wise utilization table accurate

5. **Budget Utilization Reports**
   - Monthly financial statements generated
   - Budget vs. actual comparison accurate
   - Variance analysis identifies over/under spending
   - Program-wise reports available

---

## BMMS Migration Notes

### Organization Field Addition

**When transitioning to BMMS multi-tenant architecture:**

```python
# Migration: budget_preparation/000X_add_organization_field.py

class Migration(migrations.Migration):

    dependencies = [
        ('budget_preparation', '000X_previous_migration'),
        ('organizations', '0001_initial'),  # NEW organizations app
    ]

    operations = [
        # Step 1: Add nullable organization field
        migrations.AddField(
            model_name='budgetproposal',
            name='organization',
            field=models.ForeignKey(
                'organizations.Organization',
                on_delete=models.PROTECT,
                null=True,  # Temporarily nullable
                related_name='budget_proposals'
            ),
        ),

        # Step 2: Populate with OOBC organization
        migrations.RunPython(assign_to_oobc_organization),

        # Step 3: Make required
        migrations.AlterField(
            model_name='budgetproposal',
            name='organization',
            field=models.ForeignKey(
                'organizations.Organization',
                on_delete=models.PROTECT,
                null=False,  # Now required
                related_name='budget_proposals'
            ),
        ),
    ]


def assign_to_oobc_organization(apps, schema_editor):
    """Assign all existing budget proposals to OOBC"""
    BudgetProposal = apps.get_model('budget_preparation', 'BudgetProposal')
    Organization = apps.get_model('organizations', 'Organization')

    oobc = Organization.objects.get(code='OOBC')

    BudgetProposal.objects.update(organization=oobc)
```

### Multi-Organization Considerations

**BMMS Enhancements:**

1. **Budget Consolidation Dashboard (OCM)**
   - Aggregate budget data across all 44 MOAs
   - Parliament-wide spending analytics
   - Cross-MOA budget comparison

2. **Budget Call Distribution**
   - MFBM distributes budget call to all MOAs
   - Budget ceiling per MOA
   - Submission deadlines tracked

3. **GAAB Management**
   - General Appropriations Act consolidation
   - Per-MOA appropriations
   - Parliament approval workflow

4. **OCM Oversight Features**
   - Real-time budget execution monitoring across government
   - Consolidated financial reports
   - Fiscal policy compliance tracking

**Code Changes for BMMS:**

```python
# Minimal changes needed - just add organization scoping

class BudgetProposal(models.Model):
    # ... existing fields ...

    # NEW: Organization field (for BMMS)
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.PROTECT,
        related_name='budget_proposals'
    )

    class Meta:
        unique_together = [['organization', 'fiscal_year']]  # One per org per year
```

**Query Adjustments:**

```python
# BEFORE (OBCMS):
proposals = BudgetProposal.objects.filter(fiscal_year=2025)

# AFTER (BMMS):
proposals = BudgetProposal.objects.filter(
    organization=request.organization,  # Auto-filtered by middleware
    fiscal_year=2025
)
```

---

## Dependencies

### Phase Dependencies

```
Phase 0: URL Structure Refactoring (COMPLETE)
    ↓
Phase 1: Planning Module (COMPLETE)
    ↓  - Strategic plans created
    ↓  - Annual work plans operational
    ↓
Phase 2A: Budget Preparation (START HERE)
    ↓  - Budget proposals linked to plans
    ↓  - Program allocations defined
    ↓
Phase 2B: Budget Execution (AFTER 2A)
    ↓  - Allotment tracking
    ↓  - Obligation/disbursement recording
    ↓
Phase 3: Coordination Enhancements (FUTURE)
```

### Module Dependencies

```python
# Budget Preparation depends on:
- common.User           # User authentication
- planning.StrategicPlan    # Strategic goal linkage
- planning.StrategicGoal    # Goal-budget alignment
- planning.AnnualWorkPlan   # Annual plan linkage
- monitoring.Program        # Program-budget linkage

# Budget Execution depends on:
- budget_preparation.BudgetProposal   # Approved budgets
- budget_preparation.ProgramBudget    # Approved allocations
- monitoring.Activity                  # Activity-spending linkage
- monitoring.Project                   # Project-spending linkage
```

---

## Implementation Checklist

### Before Starting

- [ ] Review Parliament Bill No. 325 (Bangsamoro Budget System Act)
- [ ] Confirm Phase 0 complete (URL refactoring)
- [ ] Confirm Phase 1 complete (Planning module)
- [ ] Review OBCMS UI Standards Master Guide
- [ ] Set up development environment (Python venv, PostgreSQL)

### Phase 2A: Budget Preparation

- [ ] Create `budget_preparation` app structure
- [ ] Define all models (BudgetProposal, ProgramBudget, BudgetJustification, BudgetLineItem)
- [ ] Apply migrations
- [ ] Configure admin interface
- [ ] Create budget proposal CRUD views
- [ ] Implement submission workflow
- [ ] Build program allocation UI
- [ ] Create justification forms
- [ ] Implement planning integration
- [ ] Implement M&E integration
- [ ] Write model tests (80%+ coverage)
- [ ] Write view tests
- [ ] Write integration tests
- [ ] Document user workflows

### Phase 2B: Budget Execution

- [ ] Create `budget_execution` app structure
- [ ] Define execution models (Allotment, Obligation, Disbursement, WorkItem)
- [ ] Apply migrations
- [ ] Implement allotment release service
- [ ] Create obligation recording service
- [ ] Build disbursement tracking service
- [ ] Create budget execution dashboard
- [ ] Implement financial reporting
- [ ] Build variance analysis
- [ ] Create program utilization reports
- [ ] Implement quarterly trend analysis
- [ ] Write financial constraint tests
- [ ] Write execution workflow tests
- [ ] Write integration tests
- [ ] Document financial procedures

### Final Validation

- [ ] Run full test suite (pytest)
- [ ] Verify 80%+ test coverage
- [ ] Test all financial constraints
- [ ] Verify Parliament Bill No. 325 compliance
- [ ] Test Planning module integration
- [ ] Test M&E module integration
- [ ] Review UI/UX consistency
- [ ] Test responsive behavior (mobile, tablet, desktop)
- [ ] Verify accessibility (WCAG 2.1 AA)
- [ ] User acceptance testing with OOBC staff
- [ ] Documentation review
- [ ] Deploy to staging environment

---

## Conclusion

This comprehensive execution plan provides:

✅ **Clear Task Breakdown** - All tasks organized into logical sub-phases
✅ **Complete Database Schema** - Financial models with constraints
✅ **Working Code Examples** - Services, views, and templates
✅ **UI Specifications** - Following OBCMS standards
✅ **Business Rules** - Financial constraints and validation
✅ **Integration Strategy** - Planning and M&E module linkage
✅ **Testing Approach** - Comprehensive test coverage
✅ **Success Criteria** - Clear acceptance tests
✅ **BMMS Compatibility** - Seamless multi-tenant migration path

**Implementation Approach:** Sequential execution of Phase 2A followed by Phase 2B, with continuous testing and validation throughout.

**Expected Outcome:** OOBC operates with a professional, Parliament Bill No. 325-compliant budget system that provides transparent financial accountability and real-time budget execution tracking.

---

**Document Status:** ✅ Ready for Implementation
**Review Required:** Yes (OOBC Leadership, Finance Team)
**Approval Required:** Yes (OOBC Director)
**Estimated Implementation Duration:** Complexity: Complex (both phases)

**Next Steps:**
1. Review and approve this execution plan
2. Assign development resources
3. Begin Phase 2A implementation
4. Proceed to Phase 2B after 2A completion
5. User acceptance testing
6. Training and rollout

---

**Last Updated:** 2025-10-13
**Document Version:** 1.0
**Author:** OBCMS Development Team

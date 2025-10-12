# Phase 2: Budget System Implementation Guide
## Quick Start Guide for Parliament Bill No. 325 Compliance

**Document Version:** 1.0
**Date:** October 13, 2025
**Status:** ✅ Ready for Implementation
**Priority:** CRITICAL ⭐⭐⭐⭐⭐
**Companion Doc:** [PHASE_2_BUDGET_SYSTEM_ARCHITECTURE.md](./PHASE_2_BUDGET_SYSTEM_ARCHITECTURE.md)

---

## Quick Reference Card

### What You're Building

**Two Django Apps:**
1. **`budget_preparation`** - Budget planning, proposals, approval workflow
2. **`budget_execution`** - Allotments, obligations, disbursements, tracking

**8 Core Models:**
- BudgetProposal, ProgramBudget, BudgetJustification, BudgetLineItem
- Allotment, Obligation, Disbursement, WorkItem

**Critical Requirements:**
- ✅ DecimalField (NOT FloatField) for all currency
- ✅ Database-level constraints (CHECK, triggers)
- ✅ Audit logging (ALL CREATE/UPDATE/DELETE)
- ✅ Financial validation (Allotment ≤ Budget, etc.)
- ✅ Parliament Bill No. 325 compliance

---

## Prerequisites Checklist

**Before Starting Phase 2:**

- [ ] **Phase 0 Complete** - URL structure refactored
- [ ] **Phase 1 Complete** - Planning module operational
  - Strategic plans working
  - Annual work plans functional
- [ ] **PostgreSQL Installed** - Recommended for development testing
  ```bash
  brew install postgresql@17  # macOS
  brew services start postgresql@17
  ```
- [ ] **Environment Ready**
  ```bash
  cd src
  source ../venv/bin/activate
  python manage.py check  # Should pass
  ```
- [ ] **Review Documentation**
  - [x] Phase 2 Budget System document (3,170 lines)
  - [x] Architecture document (this file's companion)
  - [x] OBCMS UI Standards Master Guide

---

## Implementation Order

### Phase 2A: Budget Preparation (First)

**Duration:** Moderate Complexity
**Value:** ⭐⭐⭐⭐ HIGH

**Order of Implementation:**

1. **Create App Structure** (30 minutes)
   ```bash
   cd src
   python manage.py startapp budget_preparation
   mkdir -p budget_preparation/{models,services,forms,views}
   touch budget_preparation/models/__init__.py
   ```

2. **Define Models** (2-4 hours)
   - BudgetProposal (core)
   - ProgramBudget (links to M&E)
   - BudgetJustification (narratives)
   - BudgetLineItem (detailed breakdowns)

3. **Create Migrations** (15 minutes)
   ```bash
   python manage.py makemigrations budget_preparation
   python manage.py migrate
   ```

4. **Admin Interface** (1 hour)
   - Register models
   - Configure list displays
   - Add inline editing

5. **Service Layer** (2-3 hours)
   - BudgetBuilderService (create, validate)
   - Workflow transitions (draft → submitted → approved)
   - Financial constraint checks

6. **Views & Forms** (3-4 hours)
   - CRUD views for budget proposals
   - Program allocation forms
   - Justification management
   - Submission workflow

7. **Planning Integration** (1-2 hours)
   - Link to strategic goals
   - Link to annual work plans
   - Alignment validation

8. **Testing** (2-3 hours)
   - Model tests (constraints)
   - View tests (CRUD)
   - Integration tests

**Total Estimated Complexity:** Moderate

---

### Phase 2B: Budget Execution (Second)

**Duration:** Complex
**Value:** ⭐⭐⭐⭐⭐ CRITICAL

**Order of Implementation:**

1. **Create App Structure** (30 minutes)
   ```bash
   python manage.py startapp budget_execution
   mkdir -p budget_execution/{models,services,forms,views}
   ```

2. **Define Models** (3-4 hours)
   - Allotment (quarterly releases)
   - Obligation (commitments)
   - Disbursement (payments)
   - WorkItem (detailed tracking)

3. **Financial Triggers** (2-3 hours)
   - PostgreSQL triggers for SUM constraints
   - Migration with RunSQL
   - Test trigger enforcement

4. **Audit Logging** (2-3 hours)
   - AuditLog model
   - Django signals
   - Middleware for request user

5. **Service Layer** (3-4 hours)
   - AllotmentReleaseService
   - Obligation tracking
   - Disbursement recording
   - Balance calculations

6. **Views & Forms** (4-5 hours)
   - Allotment management
   - Obligation forms
   - Disbursement tracking
   - Financial dashboards

7. **Financial Reporting** (3-4 hours)
   - Budget execution dashboard
   - Variance analysis
   - Program utilization reports
   - Quarterly trend charts

8. **M&E Integration** (1-2 hours)
   - Link obligations to activities
   - Activity spending reports
   - Cost efficiency metrics

9. **Testing** (3-4 hours)
   - Model tests (all constraints)
   - View tests
   - Integration tests (full cycle)
   - Financial accuracy tests

**Total Estimated Complexity:** Complex

---

## Critical Implementation Notes

### 1. Use DecimalField (NOT FloatField)

**CRITICAL:** All currency amounts MUST use DecimalField.

```python
# ✅ CORRECT
amount = models.DecimalField(
    max_digits=14,
    decimal_places=2,
    validators=[MinValueValidator(Decimal('0.01'))]
)

# ❌ WRONG - DO NOT USE
amount = models.FloatField()  # NO! Floating point errors!
```

**Why DecimalField?**
- Exact precision (no rounding errors)
- Safe for financial calculations
- Legal requirement for government systems

---

### 2. Database Constraints Are Mandatory

**Three Layers of Validation:**

1. **Django Model Constraints** (CheckConstraint)
   ```python
   class Meta:
       constraints = [
           models.CheckConstraint(
               check=models.Q(amount__gte=Decimal('0.01')),
               name='positive_amount'
           ),
       ]
   ```

2. **Model clean() Method**
   ```python
   def clean(self):
       if self.proposed_amount != self.get_total_requested():
           raise ValidationError("Amount mismatch")
   ```

3. **PostgreSQL Triggers** (for SUM validation)
   ```sql
   CREATE TRIGGER allotment_sum_check...
   ```

**All three layers required for data integrity!**

---

### 3. Audit Logging Is Mandatory

**Every financial operation MUST be logged:**

```python
# Automatic via Django signals
@receiver(post_save, sender=Disbursement)
def log_disbursement_change(sender, instance, created, **kwargs):
    AuditLog.objects.create(
        content_type=ContentType.objects.get_for_model(Disbursement),
        object_id=instance.pk,
        action='create' if created else 'update',
        user=get_request_user(),
        changes={}
    )
```

**What to log:**
- CREATE: Who, when, initial values
- UPDATE: Who, when, old/new values
- DELETE: Who, when, what was deleted

---

### 4. Financial Constraint Validation

**The Cascading Chain:**

```
Budget Proposal (₱100M)
    ↓
Program Budget (₱40M approved) ← ≤ ₱100M
    ↓
Allotment Q1 (₱10M) ← SUM ≤ ₱40M
    ↓
Obligation (₱5M) ← SUM ≤ ₱10M
    ↓
Disbursement (₱5M) ← SUM ≤ ₱5M
```

**Every level enforced at:**
- Application level (clean() method)
- Database level (triggers)

---

### 5. UUID Primary Keys

**All financial models use UUID (not integer IDs):**

```python
id = models.UUIDField(
    primary_key=True,
    default=uuid.uuid4,
    editable=False
)
```

**Benefits:**
- Security (non-sequential, unpredictable)
- API stability (no ID guessing)
- Multi-tenant ready (no collision risk)

---

## Testing Strategy

### Financial Integrity Tests (CRITICAL)

**Test ALL financial constraints:**

```python
def test_allotment_cannot_exceed_approved(self):
    """Test allotment constraint"""
    # Create program budget with ₱40M approved
    program_budget = ProgramBudget.objects.create(
        budget_proposal=self.proposal,
        program=self.program,
        requested_amount=Decimal('50000000.00'),
        approved_amount=Decimal('40000000.00'),
    )

    # Try to create allotment exceeding approved amount
    allotment = Allotment(
        program_budget=program_budget,
        quarter=1,
        amount=Decimal('50000000.00'),  # ❌ Exceeds approved
        created_by=self.user
    )

    # Should raise ValidationError
    with self.assertRaises(ValidationError):
        allotment.clean()
```

**Required Test Coverage:**
- [ ] Budget proposal sum = program budgets sum
- [ ] Allotment sum ≤ approved budget
- [ ] Obligation sum ≤ allotment
- [ ] Disbursement sum ≤ obligation
- [ ] Unique constraints enforced
- [ ] Status transitions valid
- [ ] Audit logs created

**Target:** 80%+ test coverage

---

## UI/UX Requirements

### Follow OBCMS UI Standards

**PRIMARY REFERENCE:** [docs/ui/OBCMS_UI_STANDARDS_MASTER.md](../../../ui/OBCMS_UI_STANDARDS_MASTER.md)

**Critical UI Components:**

1. **Budget Dashboard Stat Cards**
   - 3D milk white design
   - Semantic colors (blue, emerald, purple)
   - Hover animations (float up)

2. **Forms**
   - Standard dropdown (min-h-[48px])
   - Touch-friendly (48px minimum)
   - Accessibility (WCAG 2.1 AA)

3. **Tables**
   - Blue-to-teal gradient headers
   - Hover effects (row highlight)
   - Responsive (mobile-first)

4. **Charts**
   - Chart.js for visualization
   - Quarterly execution (stacked bars)
   - Budget utilization (gauge charts)

**Design Tokens:**
```css
/* Stat Card Colors (Semantic) */
--approved-color: #2563EB;    /* Blue-600 */
--allotted-color: #7C3AED;    /* Purple-600 */
--obligated-color: #EA580C;   /* Orange-600 */
--disbursed-color: #059669;   /* Emerald-600 */
```

---

## API Endpoints

### Budget Preparation API

```python
# GET /api/budget/proposals/
# List all budget proposals

# POST /api/budget/proposals/
# Create new budget proposal

# GET /api/budget/proposals/{id}/
# Get budget proposal details

# PATCH /api/budget/proposals/{id}/
# Update budget proposal

# POST /api/budget/proposals/{id}/submit/
# Submit for approval

# POST /api/budget/proposals/{id}/approve/
# Approve budget proposal

# GET /api/budget/proposals/{id}/programs/
# List program budgets

# POST /api/budget/proposals/{id}/programs/
# Create program budget
```

### Budget Execution API

```python
# POST /api/budget/allotments/
# Release quarterly allotment

# POST /api/budget/obligations/
# Record obligation

# POST /api/budget/disbursements/
# Record disbursement

# GET /api/budget/execution/dashboard/
# Get execution dashboard data

# GET /api/budget/reports/utilization/
# Get budget utilization report

# GET /api/budget/reports/variance/
# Get variance analysis
```

---

## Integration Points

### 1. Planning Module Integration

**Budget → Strategic Plans:**
```python
budget_proposal.strategic_plan = strategic_plan
program_budget.strategic_goal = strategic_goal
program_budget.annual_work_plan = annual_work_plan
```

**Alignment Validation:**
- Check all programs have strategic goal
- Verify annual plan objectives funded
- Calculate strategic goal funding percentages

---

### 2. M&E Module Integration

**Budget → M&E Programs:**
```python
program_budget.program = monitoring_program
obligation.activity = monitoring_activity
```

**Financial Performance Tracking:**
- Activity-level spending summaries
- Budget utilization per activity
- Cost efficiency metrics

---

### 3. Audit Logging Integration

**All operations logged:**
```python
# Automatic via signals
AuditLog.objects.create(
    content_type=ContentType.objects.get_for_model(Disbursement),
    object_id=disbursement.pk,
    action='create',
    user=request.user,
    changes={}
)
```

---

## Performance Considerations

### Database Query Optimization

**Use select_related() and prefetch_related():**

```python
# ✅ OPTIMIZED
budget_proposals = BudgetProposal.objects.select_related(
    'strategic_plan',
    'created_by'
).prefetch_related(
    'program_budgets__program',
    'program_budgets__strategic_goal'
).filter(fiscal_year=2025)

# ❌ UNOPTIMIZED (N+1 queries)
budget_proposals = BudgetProposal.objects.filter(fiscal_year=2025)
for proposal in budget_proposals:
    print(proposal.strategic_plan.title)  # Each iteration: 1 query!
```

**Index All Foreign Keys:**
- budget_proposal_id (program budgets)
- program_budget_id (allotments)
- allotment_id (obligations)
- obligation_id (disbursements)

---

### Aggregation Performance

**Use aggregate() and annotate():**

```python
# ✅ EFFICIENT - Single query
from django.db.models import Sum, F

program_budgets = ProgramBudget.objects.filter(
    budget_proposal=proposal
).annotate(
    total_allotted=Sum('allotments__amount'),
    total_obligated=Sum('allotments__obligations__amount'),
    total_disbursed=Sum('allotments__obligations__disbursements__amount')
)

# ❌ INEFFICIENT - N queries
for program_budget in program_budgets:
    total_allotted = program_budget.allotments.aggregate(Sum('amount'))['amount__sum']
```

---

## Security Considerations

### 1. Authorization Checks

**Every financial operation requires permission:**

```python
@login_required
def create_disbursement(request):
    # Check permission
    if not request.user.has_perm('budget_execution.add_disbursement'):
        raise PermissionDenied("No permission to create disbursements")

    # Check organization (BMMS multi-tenant)
    if hasattr(request.user, 'organization'):
        if obligation.allotment.program_budget.budget_proposal.organization != request.user.organization:
            raise PermissionDenied("Cannot create disbursement for different organization")

    # Proceed with creation...
```

---

### 2. CSRF Protection

**All POST/PUT/PATCH/DELETE require CSRF token:**

```html
<form method="post" action="{% url 'budget_preparation:program_budget_create' %}">
    {% csrf_token %}
    <!-- form fields -->
</form>
```

---

### 3. SQL Injection Prevention

**ALWAYS use Django ORM (never raw SQL for user input):**

```python
# ✅ SAFE - Parameterized
budgets = ProgramBudget.objects.filter(
    budget_proposal__fiscal_year=user_input_year
)

# ❌ UNSAFE - SQL injection risk
budgets = ProgramBudget.objects.raw(
    f"SELECT * FROM program_budget WHERE fiscal_year={user_input_year}"
)
```

---

## BMMS Migration Strategy

### Adding Organization Field

**When transitioning to multi-tenant BMMS:**

```python
# Migration: budget_preparation/000X_add_organization_field.py

class Migration(migrations.Migration):

    dependencies = [
        ('budget_preparation', '000X_previous'),
        ('organizations', '0001_initial'),
    ]

    operations = [
        # Step 1: Add nullable field
        migrations.AddField(
            model_name='budgetproposal',
            name='organization',
            field=models.ForeignKey(
                'organizations.Organization',
                on_delete=models.PROTECT,
                null=True,
                related_name='budget_proposals'
            ),
        ),

        # Step 2: Populate with OOBC
        migrations.RunPython(assign_to_oobc),

        # Step 3: Make required
        migrations.AlterField(
            model_name='budgetproposal',
            name='organization',
            field=models.ForeignKey(
                'organizations.Organization',
                on_delete=models.PROTECT,
                null=False,
                related_name='budget_proposals'
            ),
        ),

        # Step 4: Update unique constraint
        migrations.AlterUniqueTogether(
            name='budgetproposal',
            unique_together={('organization', 'fiscal_year')},
        ),
    ]


def assign_to_oobc(apps, schema_editor):
    """Assign all existing budgets to OOBC organization"""
    BudgetProposal = apps.get_model('budget_preparation', 'BudgetProposal')
    Organization = apps.get_model('organizations', 'Organization')

    oobc = Organization.objects.get(code='OOBC')
    BudgetProposal.objects.update(organization=oobc)
```

**Query Updates:**

```python
# BEFORE (OBCMS):
proposals = BudgetProposal.objects.filter(fiscal_year=2025)

# AFTER (BMMS):
proposals = BudgetProposal.objects.filter(
    organization=request.organization,  # Auto-filtered by middleware
    fiscal_year=2025
)
```

**BMMS Compatibility Score:** 90% - Single field addition, minimal code changes

---

## Success Criteria

### Phase 2A Completion

- [ ] All 4 models created and migrated
- [ ] Admin interface functional
- [ ] Budget proposal CRUD working
- [ ] Program allocation interface complete
- [ ] Submission workflow (draft → submitted → approved) operational
- [ ] Planning integration complete
- [ ] M&E integration complete
- [ ] Justification management working
- [ ] Budget validation rules enforced
- [ ] 80%+ test coverage

---

### Phase 2B Completion

- [ ] All 4 execution models created
- [ ] PostgreSQL triggers implemented
- [ ] Audit logging operational (ALL operations tracked)
- [ ] Allotment release system working
- [ ] Obligation recording functional
- [ ] Disbursement tracking complete
- [ ] Financial constraints enforced (ALL levels)
- [ ] Budget execution dashboard operational
- [ ] Financial reports generated
- [ ] Variance analysis working
- [ ] Activity-level spending tracked
- [ ] 80%+ test coverage
- [ ] Parliament Bill No. 325 compliance verified

---

## Troubleshooting Guide

### Issue: Migrations Fail

**Symptom:** `django.db.utils.OperationalError`

**Solution:**
```bash
# 1. Check database connection
python manage.py dbshell

# 2. Check for conflicting migrations
python manage.py showmigrations budget_preparation
python manage.py showmigrations budget_execution

# 3. Reset if needed (DEVELOPMENT ONLY)
python manage.py migrate budget_preparation zero
python manage.py migrate budget_execution zero
rm src/budget_preparation/migrations/00*.py
rm src/budget_execution/migrations/00*.py
python manage.py makemigrations
python manage.py migrate
```

---

### Issue: Financial Constraint Violations

**Symptom:** ValidationError or database IntegrityError

**Debug Steps:**

```python
# 1. Check current totals
program_budget = ProgramBudget.objects.get(pk=budget_id)
print(f"Approved: {program_budget.approved_amount}")

total_allotted = program_budget.allotments.aggregate(
    Sum('amount')
)['amount__sum']
print(f"Total Allotted: {total_allotted}")

# 2. Identify problem allotments
for allotment in program_budget.allotments.all():
    print(f"Q{allotment.quarter}: {allotment.amount}")

# 3. Fix constraint violation
# Option A: Increase approved amount
program_budget.approved_amount = Decimal('50000000.00')
program_budget.save()

# Option B: Reduce allotment amounts
problem_allotment.amount = Decimal('8000000.00')
problem_allotment.save()
```

---

### Issue: Audit Logs Not Created

**Symptom:** No entries in AuditLog table

**Solution:**

```python
# 1. Verify signals registered
from budget_execution import signals  # Import triggers registration

# 2. Check middleware installed
# settings.py
MIDDLEWARE = [
    # ...
    'common.middleware.audit.AuditMiddleware',  # ← Must be present
]

# 3. Test signal manually
from django.contrib.contenttypes.models import ContentType
from common.models import AuditLog
from budget_execution.models import Disbursement

disbursement = Disbursement.objects.first()
AuditLog.objects.create(
    content_type=ContentType.objects.get_for_model(Disbursement),
    object_id=disbursement.pk,
    action='test',
    user=request.user,
    changes={}
)
```

---

## Next Steps

### After Phase 2 Complete

1. **Phase 3: Coordination Enhancements** (MEDIUM priority)
   - Enhanced stakeholder engagement
   - Partnership management
   - Event scheduling improvements

2. **Phase 4: Module Migration** (MEDIUM priority)
   - MANA module to BMMS structure
   - M&E module enhancements
   - Policy tracking improvements

3. **Phase 5: OCM Aggregation Dashboard** (HIGH priority)
   - Consolidated budget view across all MOAs
   - Parliament-wide financial analytics
   - GAAB management

---

## Reference Documentation

**Primary Documents:**
1. [PHASE_2_BUDGET_SYSTEM.md](./PHASE_2_BUDGET_SYSTEM.md) - Complete specification (3,170 lines)
2. [PHASE_2_BUDGET_SYSTEM_ARCHITECTURE.md](./PHASE_2_BUDGET_SYSTEM_ARCHITECTURE.md) - Detailed architecture
3. [OBCMS UI Standards Master](../../../ui/OBCMS_UI_STANDARDS_MASTER.md) - UI guidelines
4. [PostgreSQL Migration Summary](../../../deployment/POSTGRESQL_MIGRATION_SUMMARY.md) - Database setup

**Planning Documents:**
- [BMMS Transition Plan](../TRANSITION_PLAN.md) - Overall BMMS strategy
- [Phase 0: URL Refactoring](./PHASE_0_URL_REFACTOR.md) - Foundation
- [Phase 1: Planning Module](./PHASE_1_PLANNING_MODULE.md) - Prerequisites

**Development Guides:**
- [Development README](../../../development/README.md) - Setup instructions
- [Testing Strategy](../../../testing/) - Test procedures

---

## Support & Questions

**For implementation questions:**
1. Review [PHASE_2_BUDGET_SYSTEM.md](./PHASE_2_BUDGET_SYSTEM.md) (comprehensive guide)
2. Check [Architecture document](./PHASE_2_BUDGET_SYSTEM_ARCHITECTURE.md) (technical specs)
3. Refer to [CLAUDE.md](../../../../CLAUDE.md) (project guidelines)

**For architectural decisions:**
- All architecture follows Django best practices
- Financial systems require extra validation layers
- Security and audit logging are non-negotiable
- BMMS compatibility built in from day one

---

**Document Status:** ✅ COMPLETE
**Ready for Implementation:** YES
**Prerequisites:** Phase 0, Phase 1 complete
**Next Action:** Begin Phase 2A implementation

---

**Prepared By:** Claude Code (OBCMS System Architect)
**Date:** October 13, 2025
**Version:** 1.0

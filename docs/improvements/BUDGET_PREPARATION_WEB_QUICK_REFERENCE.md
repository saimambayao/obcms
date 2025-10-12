# Budget Preparation Web Interface - Quick Reference

## Access URLs

| Feature | URL | View Function |
|---------|-----|---------------|
| Dashboard | `/budget/preparation/` | `budget_dashboard` |
| List Proposals | `/budget/preparation/proposals/` | `proposal_list` |
| Create Proposal | `/budget/preparation/proposals/create/` | `proposal_create` |
| View Proposal | `/budget/preparation/proposals/<pk>/` | `proposal_detail` |
| Edit Proposal | `/budget/preparation/proposals/<pk>/edit/` | `proposal_edit` |
| Submit Proposal | `/budget/preparation/proposals/<pk>/submit/` | `proposal_submit` |
| Approve Proposal | `/budget/preparation/proposals/<pk>/approve/` | `proposal_approve` |
| Reject Proposal | `/budget/preparation/proposals/<pk>/reject/` | `proposal_reject` |

## User Workflows

### Create Budget Proposal
1. Navigate to `/budget/preparation/proposals/create/`
2. Fill in: Fiscal Year, Title, Description
3. Click "Save" → redirects to Edit page
4. Add Program Budgets (linked to Planning objectives)
5. Add Line Items to each program
6. Review totals
7. Submit for approval

### Review & Approve Proposal
1. Navigate to proposal detail page
2. Review program budgets and line items
3. Check category breakdown (PS/MOOE/CO)
4. Click "Approve" or "Reject"
5. Provide notes (required for rejection)

### Filter & Search
1. Go to Proposals List
2. Use filters: Status, Fiscal Year
3. Search by title/description
4. Sort by fiscal year (newest first)

## Status Flow

```
draft → submitted → under_review → approved
                                 ↘ rejected → draft (can be edited again)
```

**Editable Statuses**: draft, rejected
**Non-Editable**: submitted, under_review, approved

## Form Fields

### BudgetProposal
- **fiscal_year** (required): Current year or future
- **title** (required): Brief descriptive title
- **description** (optional): Overview of objectives

### ProgramBudget
- **program** (required): WorkPlanObjective from Planning module
- **allocated_amount** (required): Budget in PHP (₱)
- **priority_level** (required): high, medium, low
- **justification** (required): Rationale for allocation
- **expected_outputs** (required): Deliverables and outcomes

### BudgetLineItem
- **category** (required): personnel, operating, capital
- **description** (required): Item description
- **unit_cost** (required): Cost per unit
- **quantity** (required): Number of units
- **notes** (optional): Additional specifications

## Validation Rules

### Proposal Submission
- ✅ Must have at least 1 program budget
- ✅ Each program must have line items
- ✅ Line items total must match allocated amount (±₱0.01 tolerance)
- ✅ Proposal total must match sum of program budgets

### Fiscal Year
- ✅ Must be current year or future
- ✅ Only one proposal per organization per fiscal year

### Budget Amounts
- ✅ All amounts must be > 0
- ✅ Quantities must be >= 1

## Permissions

### Required Permissions
- **View**: Login required (all users)
- **Create/Edit**: Login required (all users)
- **Approve/Reject**: `budget_preparation.can_approve_proposals`

### Editing Restrictions
- Can only edit: draft or rejected proposals
- Cannot edit: submitted, under_review, or approved proposals

## API Endpoints (HTMX)

### Statistics
```
GET /budget/preparation/api/stats/
Returns: JSON with proposal counts by status
```

### Recent Proposals
```
GET /budget/preparation/api/recent-proposals/
Returns: HTML partial with recent 5 proposals
```

## Service Layer

All operations use `BudgetBuilderService`:

```python
from budget_preparation.services.budget_builder import BudgetBuilderService

service = BudgetBuilderService()

# Create proposal
proposal = service.create_proposal(
    organization=org,
    fiscal_year=2025,
    title="FY 2025 Budget",
    description="Annual budget proposal",
    user=request.user
)

# Add program budget
program_budget = service.add_program_budget(
    proposal=proposal,
    program=work_plan_objective,
    allocated_amount=1000000.00,
    priority='high',
    justification="Critical infrastructure",
    expected_outputs="10 new facilities"
)

# Add line item
line_item = service.add_line_item(
    program_budget=program_budget,
    category='capital',
    description='Building Construction',
    unit_cost=500000.00,
    quantity=2
)

# Submit proposal
service.submit_proposal(proposal, request.user)
```

## Template Location

```
src/templates/budget_preparation/
├── dashboard.html              # Main dashboard
├── proposal_list.html          # List view with filters
├── proposal_detail.html        # Detailed view
├── proposal_form.html          # Create/edit form
└── partials/                   # HTMX partials
    ├── program_budget_item.html
    ├── program_form.html
    └── recent_proposals.html
```

## Common Issues & Solutions

### "Cannot edit proposal"
**Problem**: Proposal status is not draft/rejected
**Solution**: Only draft or rejected proposals can be edited

### "Line items total doesn't match"
**Problem**: Sum of line items ≠ allocated amount
**Solution**: Adjust line items or allocated amount to match

### "Duplicate proposal"
**Problem**: Proposal already exists for this fiscal year
**Solution**: Edit existing proposal or choose different fiscal year

### "No programs available"
**Problem**: No WorkPlanObjectives for selected fiscal year
**Solution**: Create annual work plan in Planning module first

## Integration Points

### Planning Module
- Links to `planning.WorkPlanObjective`
- Filters by fiscal year
- Shows strategic goal alignment

### Coordination Module
- Uses `coordination.Organization` for multi-tenancy
- Currently filters for OOBC organization

### MANA Module (Future)
- BudgetJustification can reference Assessment
- Evidence-based budgeting support

## Development Commands

```bash
# Check system
python manage.py check

# Show URLs
python manage.py show_urls | grep budget

# Create migrations (if needed)
python manage.py makemigrations budget_preparation

# Apply migrations
python manage.py migrate budget_preparation

# Run tests
python manage.py test budget_preparation

# Create superuser (for approval permission)
python manage.py createsuperuser
```

## Admin Interface

Access: `/admin/budget_preparation/`

Available models:
- BudgetProposal
- ProgramBudget
- BudgetLineItem
- BudgetJustification

## Quick Test Data

```python
# In Django shell: python manage.py shell

from budget_preparation.services.budget_builder import BudgetBuilderService
from coordination.models import Organization
from planning.models import WorkPlanObjective
from django.contrib.auth import get_user_model

User = get_user_model()
service = BudgetBuilderService()

# Get/create organization
org = Organization.objects.filter(name__icontains='OOBC').first()

# Get user
user = User.objects.first()

# Create proposal
proposal = service.create_proposal(
    organization=org,
    fiscal_year=2025,
    title="Test Budget Proposal FY 2025",
    description="Sample proposal for testing",
    user=user
)

# Get a work plan objective
objective = WorkPlanObjective.objects.first()

# Add program budget
if objective:
    program = service.add_program_budget(
        proposal=proposal,
        program=objective,
        allocated_amount=1000000.00,
        priority='high',
        justification="Test program for system validation",
        expected_outputs="Testing outputs"
    )

    # Add line items
    service.add_line_item(
        program_budget=program,
        category='personnel',
        description='Staff salaries',
        unit_cost=50000.00,
        quantity=10
    )

    service.add_line_item(
        program_budget=program,
        category='operating',
        description='Office supplies',
        unit_cost=25000.00,
        quantity=20
    )

print(f"Created proposal: {proposal}")
print(f"Total budget: ₱{proposal.total_proposed_budget:,.2f}")
```

## Status

**Implementation**: COMPLETE
**Testing**: Manual testing required
**Documentation**: Complete
**Ready for**: User Acceptance Testing (UAT)

---

**Last Updated**: 2025-10-13

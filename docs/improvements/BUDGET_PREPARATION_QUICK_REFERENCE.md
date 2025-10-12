# Budget Preparation App - Quick Reference

**Status:** ✅ Backend Complete | ❌ Frontend Not Implemented
**Date:** October 13, 2025

---

## 30-Second Summary

The budget_preparation Django app has **COMPLETE database models, business logic, admin interface, and 2,000+ lines of tests**, but has **NO web views, URLs, or API endpoints**. You can manage budgets via `/admin/` but there's no user-facing interface.

---

## Implementation Status Matrix

| Layer | Status | Completeness | Access Method |
|-------|--------|--------------|---------------|
| **Database Models** | ✅ Complete | 100% | Via ORM/Admin |
| **Migrations** | ✅ Applied | 100% | Database tables exist |
| **Admin Interface** | ✅ Complete | 100% | `/admin/budget_preparation/` |
| **Business Logic** | ✅ Complete | 100% | BudgetBuilderService |
| **Unit Tests** | ✅ Complete | 100% | pytest suite |
| **URLs** | ❌ Empty | 0% | N/A |
| **Views** | ❌ Empty | 0% | N/A |
| **Forms** | ❌ None | 0% | N/A |
| **Serializers** | ❌ None | 0% | N/A |
| **Templates** | ⚠️ Partial | 15% | References only |
| **Static Assets** | ⚠️ Minimal | 10% | 2 files |

---

## What You CAN Do Right Now

### 1. Use Django Admin ✅

```
http://localhost:8000/admin/budget_preparation/
```

**Available Operations:**
- Create/edit budget proposals
- Add program budgets
- Add line items (auto-calculates totals)
- Add budget justifications
- Link to MANA assessments and M&E entries
- Submit/approve/reject workflows
- View all proposals, programs, line items

### 2. Use Django ORM ✅

```python
from budget_preparation.models import BudgetProposal, ProgramBudget
from coordination.models import Organization

# Create a proposal
org = Organization.objects.first()
proposal = BudgetProposal.objects.create(
    organization=org,
    fiscal_year=2025,
    title="FY 2025 Budget",
    total_proposed_budget=100000000
)

# Query proposals
proposals = BudgetProposal.objects.filter(status='draft')
```

### 3. Use Service Layer ✅

```python
from budget_preparation.services import BudgetBuilderService

service = BudgetBuilderService()

# Create proposal
proposal = service.create_proposal(
    organization=org,
    fiscal_year=2025,
    title="FY 2025 Budget",
    description="Annual budget",
    user=request.user
)

# Add program budget
program_budget = service.add_program_budget(
    proposal=proposal,
    program=work_plan_objective,
    allocated_amount=50000000,
    priority='high',
    justification="Critical program"
)

# Add line items
line_item = service.add_line_item(
    program_budget=program_budget,
    category='operating',
    description='Office supplies',
    unit_cost=1000,
    quantity=100
)

# Validate and submit
errors = service.validate_proposal(proposal)
if not errors:
    service.submit_proposal(proposal, request.user)
```

### 4. Run Tests ✅

```bash
cd src

# Run all tests
pytest budget_preparation/tests/ -v

# Run specific test file
pytest budget_preparation/tests/test_models.py -v

# Run with coverage
pytest budget_preparation/tests/ --cov=budget_preparation --cov-report=html

# View coverage report
open htmlcov/index.html
```

---

## What You CANNOT Do Yet

### 1. Access via Web Browser ❌

**URLs Don't Exist:**
- `/budget/proposals/` - Not configured
- `/budget/proposals/create/` - Not configured
- `/budget/proposals/123/` - Not configured

**Why:** `budget_preparation/urls.py` is empty and not included in main URLs.

### 2. Use REST API ❌

**API Endpoints Don't Exist:**
- `GET /api/budget/proposals/` - Not implemented
- `POST /api/budget/proposals/` - Not implemented
- `PATCH /api/budget/proposals/123/` - Not implemented

**Why:** No serializers, no ViewSets, no API URLs configured.

### 3. Use HTML Forms ❌

**Forms Don't Exist:**
- BudgetProposalForm - Not created
- ProgramBudgetForm - Not created
- BudgetLineItemForm - Not created

**Why:** `forms/` directory is empty.

### 4. Render Templates ❌

**Templates Exist But Non-Functional:**
- `budget_proposal_form.html` - References undefined URLs
- `partials/program_budget_item.html` - References undefined variables

**Why:** Templates exist as reference but have no view logic to render them.

---

## Database Schema Quick View

```
┌─────────────────────────────────────────────────┐
│           BudgetProposal                        │
├─────────────────────────────────────────────────┤
│ + organization (FK → Organization)              │
│ + fiscal_year (int, >= 2024)                    │
│ + title (str)                                   │
│ + total_proposed_budget (decimal)               │
│ + status (draft/submitted/under_review/...)     │
│ + submitted_by, reviewed_by (FK → User)         │
└─────────────────────────────────────────────────┘
                    │
                    │ 1:N (CASCADE)
                    ▼
┌─────────────────────────────────────────────────┐
│           ProgramBudget                         │
├─────────────────────────────────────────────────┤
│ + budget_proposal (FK → BudgetProposal)         │
│ + program (FK → WorkPlanObjective)              │
│ + allocated_amount (decimal)                    │
│ + priority_level (high/medium/low)              │
│ + justification (text)                          │
└─────────────────────────────────────────────────┘
        │                           │
        │ 1:N (CASCADE)             │ 1:N (CASCADE)
        ▼                           ▼
┌──────────────────────┐  ┌──────────────────────────┐
│  BudgetLineItem      │  │  BudgetJustification     │
├──────────────────────┤  ├──────────────────────────┤
│ + category (PS/      │  │ + needs_assessment (FK)  │
│   MOOE/CO)           │  │ + monitoring_entry (FK)  │
│ + unit_cost          │  │ + rationale              │
│ + quantity           │  │ + expected_impact        │
│ + total_cost (auto)  │  └──────────────────────────┘
└──────────────────────┘
```

---

## Model Highlights

### BudgetProposal
- **Unique:** One proposal per organization per fiscal year
- **Status Flow:** draft → submitted → under_review → approved/rejected
- **Methods:** `submit()`, `approve()`, `reject()`
- **Properties:** `is_editable`, `allocated_total`

### ProgramBudget
- **Links To:** Planning Module (WorkPlanObjective)
- **Unique:** One program per proposal
- **Properties:** `line_items_total`, `has_variance`

### BudgetLineItem
- **Categories:** Personnel (PS), Operating (MOOE), Capital (CO)
- **Auto-Calc:** `total_cost = unit_cost × quantity`
- **Property:** `category_display_short` (PS/MOOE/CO)

### BudgetJustification
- **Links To:** MANA (Assessment), M&E (MonitoringEntry)
- **Property:** `has_evidence` (checks MANA or M&E links)

---

## Service Layer Methods

### BudgetBuilderService

```python
service = BudgetBuilderService()

# Core Operations
service.create_proposal(org, fiscal_year, title, description, user)
service.add_program_budget(proposal, program, amount, priority, justification)
service.add_line_item(program_budget, category, description, unit_cost, quantity)
service.add_justification(program_budget, rationale, alignment, impact)

# Workflow Operations
service.submit_proposal(proposal, user)
service.validate_proposal(proposal)  # Returns dict of errors
```

**Validation Rules:**
- ✅ Proposal must have ≥1 program budget
- ✅ Each program must have ≥1 line item
- ✅ Line items total = allocated amount (±1¢)
- ✅ Proposal total = sum of programs (±1¢)

---

## Admin Interface Highlights

### Available at: `/admin/budget_preparation/`

**BudgetProposal Admin:**
- Colored status badges (draft=gray, approved=green, rejected=red)
- Inline program budget editing
- Search by title, organization, description
- Filter by status, fiscal year, organization

**ProgramBudget Admin:**
- Inline line item editing
- Inline justification editing
- Raw ID fields for performance
- Priority level filtering

**BudgetLineItem Admin:**
- Auto-calculates total_cost on save
- Category filtering (PS/MOOE/CO)
- Formatted currency display

**BudgetJustification Admin:**
- ✓/✗ indicators for MANA and M&E links
- Raw ID fields for assessment/monitoring references

---

## Test Suite Highlights

### Test Files (2,006 lines total)

| File | Focus | Key Tests |
|------|-------|-----------|
| `test_models.py` | Model CRUD | Creation, validation, constraints, calculations |
| `test_services.py` | Business logic | Service methods, validation, transactions |
| `test_security.py` | Multi-tenancy | Organization isolation, permissions |
| `test_accessibility.py` | WCAG 2.1 AA | Touch targets, contrast, keyboard nav |
| `test_e2e_budget_preparation.py` | Workflows | End-to-end proposal lifecycle |
| `locustfile.py` | Performance | Load testing, concurrent users |

### Run Tests

```bash
# All tests
pytest budget_preparation/tests/ -v

# Specific category
pytest budget_preparation/tests/test_security.py -v

# With coverage
pytest budget_preparation/tests/ --cov=budget_preparation --cov-report=html

# Performance (Locust)
locust -f budget_preparation/tests/locustfile.py
```

---

## Integration Status

### ✅ Working Integrations

| Integration | Model | Relationship | Status |
|------------|-------|--------------|--------|
| Organizations | coordination.Organization | FK in BudgetProposal | ✅ Working |
| Planning | planning.WorkPlanObjective | FK in ProgramBudget | ✅ Working |
| MANA | mana.Assessment | FK in BudgetJustification | ✅ Working |
| M&E | monitoring.MonitoringEntry | FK in BudgetJustification | ✅ Working |
| Auth | auth.User | FK in BudgetProposal | ✅ Working |

### ❌ Missing Integrations

| Integration | Missing Component | Impact |
|------------|-------------------|--------|
| URL Routing | `obc_management/urls.py` include | App not accessible via HTTP |
| API Layer | DRF serializers + ViewSets | No REST API endpoints |
| Frontend | Views + Templates + Forms | No user interface |

---

## Next Steps to Make It Work

### STEP 1: Add URL Routing (5 minutes)

**File:** `src/obc_management/urls.py`

```python
urlpatterns = [
    # ... existing patterns ...
    path("budget/preparation/", include("budget_preparation.urls")),
]
```

**File:** `src/budget_preparation/urls.py`

```python
from django.urls import path
from . import views

app_name = 'budget_preparation'

urlpatterns = [
    path('', views.ProposalListView.as_view(), name='proposal_list'),
    path('create/', views.ProposalCreateView.as_view(), name='proposal_create'),
    path('<int:pk>/', views.ProposalDetailView.as_view(), name='proposal_detail'),
    path('<int:pk>/edit/', views.ProposalUpdateView.as_view(), name='proposal_update'),
]
```

### STEP 2: Create Views (PRIORITY)

**File:** `src/budget_preparation/views.py`

```python
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from .models import BudgetProposal
from .forms import BudgetProposalForm

class ProposalListView(ListView):
    model = BudgetProposal
    template_name = 'budget_preparation/proposal_list.html'
    context_object_name = 'proposals'

class ProposalDetailView(DetailView):
    model = BudgetProposal
    template_name = 'budget_preparation/proposal_detail.html'

class ProposalCreateView(CreateView):
    model = BudgetProposal
    form_class = BudgetProposalForm
    template_name = 'budget_preparation/proposal_form.html'

class ProposalUpdateView(UpdateView):
    model = BudgetProposal
    form_class = BudgetProposalForm
    template_name = 'budget_preparation/proposal_form.html'
```

### STEP 3: Create Forms (HIGH)

**File:** `src/budget_preparation/forms.py`

```python
from django import forms
from .models import BudgetProposal, ProgramBudget, BudgetLineItem

class BudgetProposalForm(forms.ModelForm):
    class Meta:
        model = BudgetProposal
        fields = ['organization', 'fiscal_year', 'title', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

class ProgramBudgetForm(forms.ModelForm):
    class Meta:
        model = ProgramBudget
        fields = ['program', 'allocated_amount', 'priority_level',
                  'justification', 'expected_outputs']

class BudgetLineItemForm(forms.ModelForm):
    class Meta:
        model = BudgetLineItem
        fields = ['category', 'description', 'unit_cost', 'quantity', 'notes']
```

### STEP 4: Create Functional Templates (HIGH)

**File:** `src/templates/budget_preparation/proposal_list.html`
**File:** `src/templates/budget_preparation/proposal_detail.html`

(Use existing `budget_proposal_form.html` as reference, fix URL names)

### STEP 5: Create API Layer (MEDIUM)

**File:** `src/budget_preparation/serializers.py`

```python
from rest_framework import serializers
from .models import BudgetProposal, ProgramBudget, BudgetLineItem

class BudgetProposalSerializer(serializers.ModelSerializer):
    class Meta:
        model = BudgetProposal
        fields = '__all__'
        read_only_fields = ['total_proposed_budget', 'created_at', 'updated_at']
```

**File:** `src/budget_preparation/api_views.py`

```python
from rest_framework import viewsets
from .models import BudgetProposal
from .serializers import BudgetProposalSerializer

class BudgetProposalViewSet(viewsets.ModelViewSet):
    queryset = BudgetProposal.objects.all()
    serializer_class = BudgetProposalSerializer
```

---

## Common Tasks

### Check If App Is Registered

```bash
cd src
python manage.py showmigrations budget_preparation
```

**Expected Output:**
```
budget_preparation
 [X] 0001_initial
```

### Access Admin Interface

```
1. Start server: python manage.py runserver
2. Go to: http://localhost:8000/admin/
3. Login with superuser credentials
4. Navigate to: Budget Preparation section
```

### Query Budget Data

```python
from budget_preparation.models import BudgetProposal

# All proposals
BudgetProposal.objects.all()

# Draft proposals
BudgetProposal.objects.filter(status='draft')

# Proposals for specific year
BudgetProposal.objects.filter(fiscal_year=2025)

# With related data
proposal = BudgetProposal.objects.prefetch_related(
    'program_budgets__line_items',
    'program_budgets__justifications'
).first()
```

### Create Test Data

```python
from budget_preparation.tests.fixtures.budget_data import *

# Use pytest fixtures (requires pytest session)
# Or create manually:
from coordination.models import Organization
from budget_preparation.models import BudgetProposal

org = Organization.objects.first()
proposal = BudgetProposal.objects.create(
    organization=org,
    fiscal_year=2025,
    title="Test Proposal",
    total_proposed_budget=100000000
)
```

---

## File Locations Quick Reference

```
src/budget_preparation/
├── models/
│   ├── __init__.py              ✅ Complete
│   ├── budget_proposal.py       ✅ Complete (168 lines)
│   ├── program_budget.py        ✅ Complete (90 lines)
│   ├── budget_line_item.py      ✅ Complete (101 lines)
│   └── budget_justification.py  ✅ Complete (83 lines)
├── migrations/
│   ├── __init__.py              ✅ Applied
│   └── 0001_initial.py          ✅ Applied (415 lines)
├── services/
│   ├── __init__.py              ✅ Complete
│   └── budget_builder.py        ✅ Complete (229 lines)
├── tests/
│   ├── __init__.py              ✅ Complete
│   ├── conftest.py              ✅ Complete
│   ├── README.md                ✅ Complete
│   ├── fixtures/
│   │   └── budget_data.py       ✅ Complete (9,652 bytes)
│   ├── test_models.py           ✅ Complete (281 lines)
│   ├── test_services.py         ✅ Complete (151 lines)
│   ├── test_security.py         ✅ Complete (577 lines)
│   ├── test_accessibility.py    ✅ Complete (568 lines)
│   ├── test_e2e_budget_preparation.py ✅ Complete (429 lines)
│   └── locustfile.py            ✅ Complete (13,676 bytes)
├── admin.py                     ✅ Complete (325 lines)
├── apps.py                      ✅ Complete
├── urls.py                      ❌ EMPTY (stub only)
├── views.py                     ❌ EMPTY (stub only)
├── forms/                       ❌ EMPTY directory
└── serializers.py               ❌ DOES NOT EXIST

src/templates/budget_preparation/
├── budget_proposal_form.html    ⚠️ Reference only (237 lines)
└── partials/
    └── program_budget_item.html ⚠️ Reference only (91 lines)

src/static/budget/
├── css/
│   └── budget-mobile.css        ⚠️ Minimal
└── js/
    └── budget_charts.js         ⚠️ Minimal
```

---

## Key Contacts & Resources

**Documentation:**
- Full Inventory: `/docs/improvements/BUDGET_PREPARATION_APP_INVENTORY.md`
- Budget Plan: `/docs/plans/budget/BANGSAMORO_BUDGET_SYSTEM_COMPREHENSIVE_PLAN.md`
- Test Suite: `/src/budget_preparation/tests/README.md`

**Legal Reference:**
- Parliament Bill No. 325 (Bangsamoro Budget System Act)

**OBCMS Standards:**
- UI Standards: `/docs/ui/OBCMS_UI_STANDARDS_MASTER.md`

---

**Document Version:** 1.0
**Last Updated:** October 13, 2025
**Quick Reference:** For detailed information, see BUDGET_PREPARATION_APP_INVENTORY.md

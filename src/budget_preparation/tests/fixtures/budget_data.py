"""
Test fixtures for budget preparation module

Provides reusable test data for budget proposals, program budgets, and line items.
"""

import pytest
from decimal import Decimal
from django.contrib.auth import get_user_model
from budget_preparation.models import (
    BudgetProposal,
    ProgramBudget,
    BudgetJustification,
    BudgetLineItem
)
from monitoring.models import MonitoringEntry
from planning.models import StrategicPlan, StrategicGoal, AnnualWorkPlan
from coordination.models import Organization

User = get_user_model()


@pytest.fixture
def test_organization(db):
    """Create test organization for OOBC."""
    return Organization.objects.create(
        name="Office for Other Bangsamoro Communities",
        code="OOBC",
        description="Test organization for budget testing",
        is_active=True
    )


@pytest.fixture
def test_user(db):
    """Create test user for budget operations."""
    return User.objects.create_user(
        username="budgetuser",
        email="budget@oobc.gov.ph",
        password="testpass123",
        first_name="Budget",
        last_name="Officer"
    )


@pytest.fixture
def test_admin_user(db):
    """Create admin user for approval operations."""
    return User.objects.create_superuser(
        username="budgetadmin",
        email="admin@oobc.gov.ph",
        password="adminpass123",
        first_name="Budget",
        last_name="Director"
    )


@pytest.fixture
def strategic_plan(db, test_user):
    """Create test strategic plan."""
    return StrategicPlan.objects.create(
        title="OOBC Strategic Plan 2024-2028",
        start_year=2024,
        end_year=2028,
        vision="Empowered Bangsamoro communities",
        mission="Support OBC development",
        status='active',
        created_by=test_user
    )


@pytest.fixture
def strategic_goal(db, strategic_plan):
    """Create test strategic goal."""
    return StrategicGoal.objects.create(
        strategic_plan=strategic_plan,
        title="Improve education access",
        description="Build 50 schools in OBCs",
        target_metric="Number of schools",
        target_value=Decimal('50.00'),
        current_value=Decimal('10.00'),
        priority='high',
        status='in_progress'
    )


@pytest.fixture
def annual_work_plan(db, strategic_plan, test_user):
    """Create test annual work plan."""
    return AnnualWorkPlan.objects.create(
        strategic_plan=strategic_plan,
        title="OOBC Annual Work Plan 2025",
        year=2025,
        description="FY 2025 operational plan",
        status='active',
        created_by=test_user
    )


@pytest.fixture
def monitoring_entry(db, test_organization):
    """Create test monitoring entry (PPA)."""
    return MonitoringEntry.objects.create(
        title="Education Infrastructure Program",
        description="Build schools and learning centers",
        category='program',
        status='active',
        organization=test_organization
    )


@pytest.fixture
def budget_proposal(db, test_organization, test_user):
    """Create test budget proposal."""
    return BudgetProposal.objects.create(
        organization=test_organization,
        fiscal_year=2025,
        title="OOBC FY 2025 Budget Proposal",
        description="Annual budget for OOBC operations",
        total_requested_budget=Decimal('100000000.00'),  # 100M
        total_approved_budget=None,  # Not yet approved
        status='draft',
        submitted_by=test_user
    )


@pytest.fixture
def approved_budget_proposal(db, test_organization, test_user, test_admin_user):
    """Create approved budget proposal for execution testing."""
    proposal = BudgetProposal.objects.create(
        organization=test_organization,
        fiscal_year=2025,
        title="OOBC FY 2025 Budget (Approved)",
        description="Approved budget for execution",
        total_requested_budget=Decimal('100000000.00'),
        total_approved_budget=Decimal('95000000.00'),  # 95M approved
        status='approved',
        submitted_by=test_user,
        approved_by=test_admin_user
    )
    return proposal


@pytest.fixture
def program_budget(db, budget_proposal, monitoring_entry, strategic_goal, annual_work_plan):
    """Create test program budget."""
    return ProgramBudget.objects.create(
        budget_proposal=budget_proposal,
        monitoring_entry=monitoring_entry,
        requested_amount=Decimal('50000000.00'),  # 50M requested
        approved_amount=None,  # Not yet approved
        strategic_goal=strategic_goal,
        annual_work_plan=annual_work_plan,
        justification="Critical education infrastructure needs",
        expected_outcomes="50 schools built, 10,000 students served",
        priority_rank=1
    )


@pytest.fixture
def approved_program_budget(db, approved_budget_proposal, monitoring_entry):
    """Create approved program budget for allotment testing."""
    return ProgramBudget.objects.create(
        budget_proposal=approved_budget_proposal,
        monitoring_entry=monitoring_entry,
        requested_amount=Decimal('50000000.00'),
        approved_amount=Decimal('45000000.00'),  # 45M approved
        justification="Critical program",
        priority_rank=1
    )


@pytest.fixture
def budget_line_item(db, program_budget):
    """Create test budget line item."""
    return BudgetLineItem.objects.create(
        program_budget=program_budget,
        category='personnel',
        sub_category='salaries',
        description="Program Manager Salary",
        unit_cost=Decimal('80000.00'),  # 80k/month
        quantity=12,  # 12 months
        total_cost=Decimal('960000.00'),
        justification="Full-time program manager required"
    )


@pytest.fixture
def budget_justification(db, budget_proposal):
    """Create test budget justification."""
    return BudgetJustification.objects.create(
        budget_proposal=budget_proposal,
        section='executive_summary',
        content="This budget supports strategic goal achievement...",
        order=1
    )


@pytest.fixture
def multiple_line_items(db, program_budget):
    """Create multiple line items for testing aggregations."""
    items = []

    # Personnel costs
    items.append(BudgetLineItem.objects.create(
        program_budget=program_budget,
        category='personnel',
        sub_category='salaries',
        description="Project Staff Salaries",
        unit_cost=Decimal('50000.00'),
        quantity=24,  # 2 staff x 12 months
        total_cost=Decimal('1200000.00')
    ))

    # Operating expenses
    items.append(BudgetLineItem.objects.create(
        program_budget=program_budget,
        category='operating',
        sub_category='supplies',
        description="Office Supplies",
        unit_cost=Decimal('20000.00'),
        quantity=12,  # 12 months
        total_cost=Decimal('240000.00')
    ))

    # Capital outlays
    items.append(BudgetLineItem.objects.create(
        program_budget=program_budget,
        category='capital',
        sub_category='equipment',
        description="Computer Equipment",
        unit_cost=Decimal('50000.00'),
        quantity=5,  # 5 units
        total_cost=Decimal('250000.00')
    ))

    return items


@pytest.fixture
def complete_budget_structure(db, test_organization, test_user, monitoring_entry):
    """
    Create complete budget structure for integration testing.

    Returns:
        dict: Contains proposal, 3 program budgets, and line items
    """
    proposal = BudgetProposal.objects.create(
        organization=test_organization,
        fiscal_year=2025,
        title="Complete Budget Test",
        total_requested_budget=Decimal('150000000.00'),
        status='draft',
        submitted_by=test_user
    )

    program_budgets = []
    for i in range(1, 4):
        pb = ProgramBudget.objects.create(
            budget_proposal=proposal,
            monitoring_entry=monitoring_entry,
            requested_amount=Decimal(f'{50000000 * i}.00'),
            priority_rank=i
        )
        program_budgets.append(pb)

        # Add line items to each program
        for j in range(1, 6):
            BudgetLineItem.objects.create(
                program_budget=pb,
                category=['personnel', 'operating', 'capital'][j % 3],
                description=f"Line Item {j}",
                unit_cost=Decimal('10000.00'),
                quantity=j,
                total_cost=Decimal(f'{10000 * j}.00')
            )

    return {
        'proposal': proposal,
        'program_budgets': program_budgets,
        'total_programs': 3,
        'total_line_items': 15
    }


# Helper functions for test data creation

def create_budget_proposal(**kwargs):
    """Helper to create budget proposals with defaults."""
    defaults = {
        'fiscal_year': 2025,
        'title': 'Test Budget Proposal',
        'status': 'draft',
        'total_requested_budget': Decimal('10000000.00')
    }
    defaults.update(kwargs)
    return BudgetProposal.objects.create(**defaults)


def create_program_budget(**kwargs):
    """Helper to create program budgets with defaults."""
    defaults = {
        'requested_amount': Decimal('1000000.00'),
        'priority_rank': 1
    }
    defaults.update(kwargs)
    return ProgramBudget.objects.create(**defaults)


def create_line_item(**kwargs):
    """Helper to create line items with defaults."""
    defaults = {
        'category': 'personnel',
        'description': 'Test Line Item',
        'unit_cost': Decimal('1000.00'),
        'quantity': 1,
        'total_cost': Decimal('1000.00')
    }
    defaults.update(kwargs)
    return BudgetLineItem.objects.create(**defaults)

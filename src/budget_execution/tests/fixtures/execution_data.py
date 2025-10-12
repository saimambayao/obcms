"""
Test fixtures for budget execution module

Provides reusable test data for allotments, obligations, and disbursements.
"""

import pytest
from decimal import Decimal
from datetime import date, timedelta
from django.contrib.auth import get_user_model
from budget_execution.models import Allotment, Obligation, Disbursement, WorkItem
from budget_preparation.models import ProgramBudget

User = get_user_model()


@pytest.fixture
def execution_user(db):
    """Create user for budget execution operations."""
    return User.objects.create_user(
        username="executionuser",
        email="execution@oobc.gov.ph",
        password="testpass123",
        first_name="Execution",
        last_name="Officer"
    )


@pytest.fixture
def allotment_q1(db, approved_program_budget, execution_user):
    """Create Q1 allotment."""
    return Allotment.objects.create(
        program_budget=approved_program_budget,
        quarter='Q1',
        amount=Decimal('10000000.00'),  # 10M for Q1
        release_date=date(2025, 1, 15),
        released_by=execution_user,
        status='released',
        reference_number='ALL-2025-Q1-001'
    )


@pytest.fixture
def allotment_q2(db, approved_program_budget, execution_user):
    """Create Q2 allotment."""
    return Allotment.objects.create(
        program_budget=approved_program_budget,
        quarter='Q2',
        amount=Decimal('12000000.00'),  # 12M for Q2
        release_date=date(2025, 4, 15),
        released_by=execution_user,
        status='released',
        reference_number='ALL-2025-Q2-001'
    )


@pytest.fixture
def work_item(db, monitoring_entry):
    """Create test work item for obligations."""
    return WorkItem.objects.create(
        monitoring_entry=monitoring_entry,
        title="School Construction - Lanao del Sur",
        description="Build 2-classroom school building",
        estimated_cost=Decimal('5000000.00'),
        target_completion_date=date(2025, 6, 30),
        status='in_progress'
    )


@pytest.fixture
def work_item_2(db, monitoring_entry):
    """Create second work item."""
    return WorkItem.objects.create(
        monitoring_entry=monitoring_entry,
        title="Teacher Training Program",
        description="Train 50 teachers",
        estimated_cost=Decimal('500000.00'),
        target_completion_date=date(2025, 3, 31),
        status='not_started'
    )


@pytest.fixture
def obligation(db, allotment_q1, work_item, execution_user):
    """Create test obligation."""
    return Obligation.objects.create(
        allotment=allotment_q1,
        work_item=work_item,
        amount=Decimal('5000000.00'),  # 5M obligation
        payee="ABC Construction Corp.",
        payee_tin="123-456-789-000",
        purpose="School building construction contract",
        obligation_date=date(2025, 2, 1),
        obligated_by=execution_user,
        status='obligated',
        reference_number='OBL-2025-001'
    )


@pytest.fixture
def partial_obligation(db, allotment_q1, work_item_2, execution_user):
    """Create partially disbursed obligation."""
    return Obligation.objects.create(
        allotment=allotment_q1,
        work_item=work_item_2,
        amount=Decimal('500000.00'),
        payee="Training Services Inc.",
        purpose="Teacher training program",
        obligation_date=date(2025, 2, 15),
        obligated_by=execution_user,
        status='partially_disbursed',
        reference_number='OBL-2025-002'
    )


@pytest.fixture
def disbursement(db, obligation, execution_user):
    """Create test disbursement (partial)."""
    return Disbursement.objects.create(
        obligation=obligation,
        amount=Decimal('2500000.00'),  # 50% payment
        payment_date=date(2025, 3, 1),
        payment_method='check',
        check_number='CHK-2025-001',
        bank_name='Land Bank of the Philippines',
        disbursed_by=execution_user,
        status='paid',
        reference_number='DIS-2025-001'
    )


@pytest.fixture
def full_disbursement(db, partial_obligation, execution_user):
    """Create full disbursement."""
    return Disbursement.objects.create(
        obligation=partial_obligation,
        amount=Decimal('500000.00'),  # 100% payment
        payment_date=date(2025, 3, 15),
        payment_method='bank_transfer',
        bank_name='Development Bank of the Philippines',
        disbursed_by=execution_user,
        status='paid',
        reference_number='DIS-2025-002'
    )


@pytest.fixture
def multiple_disbursements(db, obligation, execution_user):
    """Create multiple disbursements for testing aggregations."""
    disbursements = []

    # First payment - 30%
    disbursements.append(Disbursement.objects.create(
        obligation=obligation,
        amount=Decimal('1500000.00'),
        payment_date=date(2025, 2, 15),
        payment_method='check',
        check_number='CHK-2025-100',
        disbursed_by=execution_user,
        status='paid'
    ))

    # Second payment - 30%
    disbursements.append(Disbursement.objects.create(
        obligation=obligation,
        amount=Decimal('1500000.00'),
        payment_date=date(2025, 3, 15),
        payment_method='check',
        check_number='CHK-2025-101',
        disbursed_by=execution_user,
        status='paid'
    ))

    # Final payment - 40%
    disbursements.append(Disbursement.objects.create(
        obligation=obligation,
        amount=Decimal('2000000.00'),
        payment_date=date(2025, 4, 15),
        payment_method='bank_transfer',
        disbursed_by=execution_user,
        status='paid'
    ))

    return disbursements


@pytest.fixture
def complete_execution_cycle(db, approved_program_budget, monitoring_entry, execution_user):
    """
    Create complete budget execution cycle for integration testing.

    Flow: Allotment → Multiple Obligations → Multiple Disbursements

    Returns:
        dict: Contains allotment, obligations, disbursements, and work items
    """
    # Create allotment
    allotment = Allotment.objects.create(
        program_budget=approved_program_budget,
        quarter='Q1',
        amount=Decimal('20000000.00'),
        release_date=date(2025, 1, 15),
        released_by=execution_user,
        status='released'
    )

    obligations = []
    disbursements = []

    # Create 3 work items with obligations and disbursements
    for i in range(1, 4):
        work_item = WorkItem.objects.create(
            monitoring_entry=monitoring_entry,
            title=f"Work Item {i}",
            estimated_cost=Decimal(f'{5000000 * i}.00'),
            status='in_progress'
        )

        obligation = Obligation.objects.create(
            allotment=allotment,
            work_item=work_item,
            amount=Decimal(f'{5000000 * i}.00'),
            payee=f"Contractor {i}",
            purpose=f"Contract {i}",
            obligated_by=execution_user,
            status='obligated'
        )
        obligations.append(obligation)

        # Create partial disbursement (50%)
        disbursement = Disbursement.objects.create(
            obligation=obligation,
            amount=Decimal(f'{2500000 * i}.00'),
            payment_date=date(2025, 2, i),
            payment_method='check',
            disbursed_by=execution_user,
            status='paid'
        )
        disbursements.append(disbursement)

    return {
        'allotment': allotment,
        'obligations': obligations,
        'disbursements': disbursements,
        'total_allotted': Decimal('20000000.00'),
        'total_obligated': Decimal('30000000.00'),  # Sum of obligations
        'total_disbursed': Decimal('15000000.00')   # Sum of disbursements
    }


@pytest.fixture
def multi_quarter_execution(db, approved_program_budget, monitoring_entry, execution_user):
    """
    Create multi-quarter execution scenario.

    Returns:
        dict: Q1-Q4 allotments with obligations and disbursements
    """
    quarters_data = {}

    for quarter_num, quarter_name in enumerate(['Q1', 'Q2', 'Q3', 'Q4'], 1):
        # Create allotment for quarter
        allotment = Allotment.objects.create(
            program_budget=approved_program_budget,
            quarter=quarter_name,
            amount=Decimal(f'{10000000 + quarter_num * 1000000}.00'),
            release_date=date(2025, quarter_num * 3 - 2, 15),
            released_by=execution_user,
            status='released'
        )

        # Create work item and obligation
        work_item = WorkItem.objects.create(
            monitoring_entry=monitoring_entry,
            title=f"{quarter_name} Work Package",
            estimated_cost=Decimal(f'{5000000 * quarter_num}.00')
        )

        obligation = Obligation.objects.create(
            allotment=allotment,
            work_item=work_item,
            amount=Decimal(f'{5000000 * quarter_num}.00'),
            payee=f"{quarter_name} Contractor",
            obligated_by=execution_user,
            status='obligated'
        )

        quarters_data[quarter_name] = {
            'allotment': allotment,
            'work_item': work_item,
            'obligation': obligation
        }

    return quarters_data


# Helper functions for test data creation

def create_allotment(**kwargs):
    """Helper to create allotments with defaults."""
    defaults = {
        'quarter': 'Q1',
        'amount': Decimal('1000000.00'),
        'release_date': date.today(),
        'status': 'released'
    }
    defaults.update(kwargs)
    return Allotment.objects.create(**defaults)


def create_obligation(**kwargs):
    """Helper to create obligations with defaults."""
    defaults = {
        'amount': Decimal('500000.00'),
        'payee': 'Test Contractor',
        'purpose': 'Test purpose',
        'obligation_date': date.today(),
        'status': 'obligated'
    }
    defaults.update(kwargs)
    return Obligation.objects.create(**defaults)


def create_disbursement(**kwargs):
    """Helper to create disbursements with defaults."""
    defaults = {
        'amount': Decimal('250000.00'),
        'payment_date': date.today(),
        'payment_method': 'check',
        'status': 'paid'
    }
    defaults.update(kwargs)
    return Disbursement.objects.create(**defaults)


def create_work_item(**kwargs):
    """Helper to create work items with defaults."""
    defaults = {
        'title': 'Test Work Item',
        'estimated_cost': Decimal('1000000.00'),
        'status': 'not_started'
    }
    defaults.update(kwargs)
    return WorkItem.objects.create(**defaults)

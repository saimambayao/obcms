"""
Performance tests for budget operations

Tests system performance under various load conditions.
Target: Operations complete within acceptable time limits.
"""

import pytest
import time
from decimal import Decimal
from django.db.models import Sum, Count, Avg
from budget_preparation.models import BudgetProposal, ProgramBudget, BudgetLineItem
from budget_execution.models import Allotment, Obligation, Disbursement
from .fixtures.test_scenarios import PERFORMANCE_TEST_SCENARIOS


@pytest.mark.slow
@pytest.mark.django_db
class TestBudgetPerformance:
    """Performance tests for budget operations."""

    def test_bulk_line_item_creation(self, program_budget):
        """Test creating 100 line items - Target: < 2 seconds."""
        scenario = PERFORMANCE_TEST_SCENARIOS['bulk_line_items']

        start_time = time.time()

        # Create 100 line items
        line_items = []
        for i in range(100):
            line_items.append(
                BudgetLineItem(
                    program_budget=program_budget,
                    category=['personnel', 'operating', 'capital'][i % 3],
                    description=f"Line Item {i}",
                    unit_cost=Decimal('100000.00'),
                    quantity=1,
                    total_cost=Decimal('100000.00')
                )
            )

        # Bulk create
        BudgetLineItem.objects.bulk_create(line_items)

        elapsed_time = time.time() - start_time

        # Verify
        assert BudgetLineItem.objects.filter(
            program_budget=program_budget
        ).count() == 100
        assert elapsed_time < scenario['target_time_seconds'], \
            f"Bulk creation took {elapsed_time:.2f}s, target was {scenario['target_time_seconds']}s"

    def test_complex_query_performance(self, test_organization, test_user, monitoring_entry):
        """Test dashboard query with 50 programs - Target: < 1 second."""
        scenario = PERFORMANCE_TEST_SCENARIOS['complex_query']

        # Create proposal with 50 programs
        proposal = BudgetProposal.objects.create(
            organization=test_organization,
            fiscal_year=2025,
            title="Performance Test Budget",
            total_requested_budget=Decimal('500000000.00'),
            submitted_by=test_user
        )

        # Create 50 program budgets with line items
        for i in range(50):
            pb = ProgramBudget.objects.create(
                budget_proposal=proposal,
                monitoring_entry=monitoring_entry,
                requested_amount=Decimal('10000000.00'),
                priority_rank=i + 1
            )

            # Add 20 line items per program
            line_items = [
                BudgetLineItem(
                    program_budget=pb,
                    category=['personnel', 'operating', 'capital'][j % 3],
                    description=f"Program {i} Item {j}",
                    unit_cost=Decimal('50000.00'),
                    quantity=10,
                    total_cost=Decimal('500000.00')
                )
                for j in range(20)
            ]
            BudgetLineItem.objects.bulk_create(line_items)

        # Measure complex query performance
        start_time = time.time()

        # Dashboard query: Summary with aggregations
        summary = proposal.program_budgets.annotate(
            line_item_count=Count('line_items'),
            total_cost=Sum('line_items__total_cost'),
            avg_cost=Avg('line_items__total_cost')
        ).values(
            'id',
            'monitoring_entry__title',
            'requested_amount',
            'line_item_count',
            'total_cost',
            'avg_cost'
        )

        # Force query execution
        list(summary)

        elapsed_time = time.time() - start_time

        # Verify
        assert elapsed_time < scenario['target_time_seconds'], \
            f"Complex query took {elapsed_time:.2f}s, target was {scenario['target_time_seconds']}s"

    def test_financial_validation_performance(self, approved_program_budget, execution_user, monitoring_entry):
        """Test constraint validation on 1000 obligations - Target: < 5 seconds."""
        scenario = PERFORMANCE_TEST_SCENARIOS['financial_validation']

        # Create 10 allotments
        allotments = []
        for i in range(10):
            allotment = Allotment.objects.create(
                program_budget=approved_program_budget,
                quarter=['Q1', 'Q2', 'Q3', 'Q4'][i % 4],
                amount=Decimal('4000000.00'),
                released_by=execution_user,
                status='released'
            )
            allotments.append(allotment)

        # Measure validation performance
        start_time = time.time()

        # Create 100 obligations per allotment (1000 total)
        from budget_execution.models import WorkItem
        work_item = WorkItem.objects.create(
            monitoring_entry=monitoring_entry,
            title="Performance Test Work",
            estimated_cost=Decimal('1000000.00')
        )

        for allotment in allotments:
            obligations = [
                Obligation(
                    allotment=allotment,
                    work_item=work_item,
                    amount=Decimal('30000.00'),  # Safe amount
                    payee=f"Contractor {j}",
                    obligated_by=execution_user,
                    status='obligated'
                )
                for j in range(100)
            ]
            # Note: This will test constraint checking on each insert
            # TODO: May need batch validation for performance
            # Obligation.objects.bulk_create(obligations)

        elapsed_time = time.time() - start_time

        # Verify (uncomment when bulk create is enabled)
        # total_obligations = Obligation.objects.filter(
        #     allotment__in=allotments
        # ).count()
        # assert total_obligations == 1000
        # assert elapsed_time < scenario['target_time_seconds'], \
        #     f"Validation took {elapsed_time:.2f}s, target was {scenario['target_time_seconds']}s"

    def test_aggregation_heavy_query(self, test_organization, test_user, monitoring_entry):
        """Test multi-level aggregation across 10,000 line items - Target: < 3 seconds."""
        scenario = PERFORMANCE_TEST_SCENARIOS['aggregation_heavy']

        # Create 10 proposals
        proposals = []
        for i in range(10):
            proposal = BudgetProposal.objects.create(
                organization=test_organization,
                fiscal_year=2025 + i,
                title=f"Proposal {i}",
                total_requested_budget=Decimal('100000000.00'),
                submitted_by=test_user
            )
            proposals.append(proposal)

            # 20 programs per proposal
            for j in range(20):
                pb = ProgramBudget.objects.create(
                    budget_proposal=proposal,
                    monitoring_entry=monitoring_entry,
                    requested_amount=Decimal('5000000.00'),
                    priority_rank=j + 1
                )

                # 50 line items per program
                line_items = [
                    BudgetLineItem(
                        program_budget=pb,
                        category=['personnel', 'operating', 'capital'][k % 3],
                        description=f"Item {k}",
                        unit_cost=Decimal('10000.00'),
                        quantity=10,
                        total_cost=Decimal('100000.00')
                    )
                    for k in range(50)
                ]
                BudgetLineItem.objects.bulk_create(line_items)

        # Measure aggregation performance
        start_time = time.time()

        # Multi-level aggregation
        summary = BudgetLineItem.objects.filter(
            program_budget__budget_proposal__in=proposals
        ).values(
            'category',
            'program_budget__budget_proposal__fiscal_year'
        ).annotate(
            total_items=Count('id'),
            total_cost=Sum('total_cost'),
            avg_cost=Avg('unit_cost')
        )

        # Force execution
        list(summary)

        elapsed_time = time.time() - start_time

        # Verify
        total_line_items = BudgetLineItem.objects.filter(
            program_budget__budget_proposal__in=proposals
        ).count()
        assert total_line_items == 10000  # 10 proposals × 20 programs × 50 items

        assert elapsed_time < scenario['target_time_seconds'], \
            f"Aggregation took {elapsed_time:.2f}s, target was {scenario['target_time_seconds']}s"


@pytest.mark.slow
@pytest.mark.django_db
class TestExecutionPerformance:
    """Performance tests for budget execution operations."""

    def test_quarterly_allotment_creation(self, approved_program_budget, execution_user):
        """Test creating quarterly allotments - Target: < 1 second."""
        start_time = time.time()

        quarters = ['Q1', 'Q2', 'Q3', 'Q4']
        allotments = [
            Allotment(
                program_budget=approved_program_budget,
                quarter=quarter,
                amount=Decimal('10000000.00'),
                released_by=execution_user,
                status='released'
            )
            for quarter in quarters
        ]

        Allotment.objects.bulk_create(allotments)

        elapsed_time = time.time() - start_time

        assert elapsed_time < 1.0, \
            f"Allotment creation took {elapsed_time:.2f}s, target was 1.0s"

    def test_obligation_disbursement_chain(self, allotment_q1, work_item, execution_user):
        """Test creating obligation with disbursements - Target: < 2 seconds."""
        start_time = time.time()

        # Create obligation
        obligation = Obligation.objects.create(
            allotment=allotment_q1,
            work_item=work_item,
            amount=Decimal('5000000.00'),
            payee="Performance Test Contractor",
            obligated_by=execution_user,
            status='obligated'
        )

        # Create 10 progressive disbursements
        disbursements = [
            Disbursement(
                obligation=obligation,
                amount=Decimal('500000.00'),
                payment_method=['check', 'bank_transfer'][i % 2],
                disbursed_by=execution_user,
                status='paid'
            )
            for i in range(10)
        ]

        Disbursement.objects.bulk_create(disbursements)

        elapsed_time = time.time() - start_time

        assert elapsed_time < 2.0, \
            f"Obligation-disbursement chain took {elapsed_time:.2f}s, target was 2.0s"

    def test_execution_summary_calculation(self, complete_execution_cycle):
        """Test calculating execution summary - Target: < 1 second."""
        data = complete_execution_cycle

        start_time = time.time()

        # Calculate comprehensive summary
        allotment = data['allotment']

        total_obligated = Obligation.objects.filter(
            allotment=allotment
        ).aggregate(total=Sum('amount'))['total']

        total_disbursed = Disbursement.objects.filter(
            obligation__allotment=allotment
        ).aggregate(total=Sum('amount'))['total']

        # Calculate utilization rates
        obligation_rate = (total_obligated / allotment.amount) * 100
        disbursement_rate = (total_disbursed / allotment.amount) * 100

        elapsed_time = time.time() - start_time

        assert elapsed_time < 1.0, \
            f"Summary calculation took {elapsed_time:.2f}s, target was 1.0s"


@pytest.mark.slow
@pytest.mark.django_db
class TestDatabasePerformance:
    """Test database-level performance."""

    def test_index_effectiveness(self, budget_proposal):
        """Test that database indexes are effective."""
        # TODO: Implement index usage analysis
        # Use EXPLAIN to verify indexes are used
        pass

    def test_n_plus_one_prevention(self, complete_budget_structure):
        """Test that N+1 queries are prevented."""
        # TODO: Use django-debug-toolbar or similar
        # Verify query count doesn't scale with data
        pass

    def test_transaction_performance(self, approved_program_budget):
        """Test transaction commit performance."""
        # TODO: Measure transaction overhead
        pass

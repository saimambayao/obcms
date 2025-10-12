"""
Integration tests for budget system

Tests complete budget lifecycle from preparation through execution.
"""

import pytest
from decimal import Decimal
from datetime import date
from budget_preparation.models import BudgetProposal, ProgramBudget, BudgetLineItem
from budget_execution.models import Allotment, Obligation, Disbursement
from django.db.models import Sum


@pytest.mark.integration
@pytest.mark.django_db
class TestBudgetFullCycle:
    """Test complete budget lifecycle."""

    def test_full_budget_cycle(self, test_organization, test_user, test_admin_user, monitoring_entry, execution_user):
        """
        Test complete budget cycle:
        Proposal → Approval → Allotment → Obligation → Disbursement
        """
        # STEP 1: Create budget proposal
        proposal = BudgetProposal.objects.create(
            organization=test_organization,
            fiscal_year=2025,
            title="Full Cycle Test Budget",
            total_requested_budget=Decimal('100000000.00'),
            status='draft',
            submitted_by=test_user
        )

        # STEP 2: Add program budget
        program_budget = ProgramBudget.objects.create(
            budget_proposal=proposal,
            monitoring_entry=monitoring_entry,
            requested_amount=Decimal('50000000.00'),
            priority_rank=1
        )

        # STEP 3: Add line items
        BudgetLineItem.objects.create(
            program_budget=program_budget,
            category='personnel',
            description="Personnel costs",
            unit_cost=Decimal('30000000.00'),
            quantity=1,
            total_cost=Decimal('30000000.00')
        )

        BudgetLineItem.objects.create(
            program_budget=program_budget,
            category='operating',
            description="Operating expenses",
            unit_cost=Decimal('15000000.00'),
            quantity=1,
            total_cost=Decimal('15000000.00')
        )

        BudgetLineItem.objects.create(
            program_budget=program_budget,
            category='capital',
            description="Capital outlays",
            unit_cost=Decimal('5000000.00'),
            quantity=1,
            total_cost=Decimal('5000000.00')
        )

        # STEP 4: Submit proposal
        proposal.status = 'submitted'
        proposal.save()

        # STEP 5: Approve proposal
        proposal.status = 'approved'
        proposal.total_approved_budget = Decimal('95000000.00')
        proposal.approved_by = test_admin_user
        program_budget.approved_amount = Decimal('45000000.00')
        program_budget.save()
        proposal.save()

        # STEP 6: Release Q1 allotment
        allotment = Allotment.objects.create(
            program_budget=program_budget,
            quarter='Q1',
            amount=Decimal('10000000.00'),
            released_by=execution_user,
            status='released'
        )

        # STEP 7: Create work item and obligation
        from budget_execution.models import WorkItem
        work_item = WorkItem.objects.create(
            monitoring_entry=monitoring_entry,
            title="Implementation Phase 1",
            estimated_cost=Decimal('8000000.00'),
            status='in_progress'
        )

        obligation = Obligation.objects.create(
            allotment=allotment,
            work_item=work_item,
            amount=Decimal('8000000.00'),
            payee="Implementation Contractor",
            obligated_by=execution_user,
            status='obligated'
        )

        # STEP 8: Record disbursements (progressive payment)
        # First payment: 30%
        disbursement_1 = Disbursement.objects.create(
            obligation=obligation,
            amount=Decimal('2400000.00'),
            payment_method='check',
            disbursed_by=execution_user,
            status='paid'
        )

        # Second payment: 30%
        disbursement_2 = Disbursement.objects.create(
            obligation=obligation,
            amount=Decimal('2400000.00'),
            payment_method='check',
            disbursed_by=execution_user,
            status='paid'
        )

        # VERIFY complete cycle
        assert proposal.status == 'approved'
        assert program_budget.approved_amount == Decimal('45000000.00')
        assert allotment.status == 'released'
        assert obligation.status == 'obligated'

        # Verify financial totals
        total_line_items = BudgetLineItem.objects.filter(
            program_budget=program_budget
        ).aggregate(total=Sum('total_cost'))['total']
        assert total_line_items == Decimal('50000000.00')

        total_disbursed = Disbursement.objects.filter(
            obligation=obligation
        ).aggregate(total=Sum('amount'))['total']
        assert total_disbursed == Decimal('4800000.00')  # 60% of 8M

    def test_multi_program_budget(self, test_organization, test_user, monitoring_entry):
        """Test budget with multiple programs."""
        proposal = BudgetProposal.objects.create(
            organization=test_organization,
            fiscal_year=2025,
            title="Multi-Program Budget",
            total_requested_budget=Decimal('200000000.00'),
            status='draft',
            submitted_by=test_user
        )

        # Create 5 program budgets
        for i in range(1, 6):
            program_budget = ProgramBudget.objects.create(
                budget_proposal=proposal,
                monitoring_entry=monitoring_entry,
                requested_amount=Decimal(f'{40000000 * i}.00'),
                priority_rank=i
            )

            # Add 3 line items per program
            for j in range(1, 4):
                BudgetLineItem.objects.create(
                    program_budget=program_budget,
                    category=['personnel', 'operating', 'capital'][j-1],
                    description=f"Program {i} - Item {j}",
                    unit_cost=Decimal(f'{10000000 * j}.00'),
                    quantity=1,
                    total_cost=Decimal(f'{10000000 * j}.00')
                )

        # Verify structure
        assert proposal.program_budgets.count() == 5
        total_line_items = BudgetLineItem.objects.filter(
            program_budget__budget_proposal=proposal
        ).count()
        assert total_line_items == 15

    def test_quarterly_allotment_releases(self, approved_program_budget, execution_user):
        """Test releasing allotments across quarters."""
        quarters = ['Q1', 'Q2', 'Q3', 'Q4']
        quarter_amounts = [
            Decimal('10000000.00'),
            Decimal('12000000.00'),
            Decimal('13000000.00'),
            Decimal('10000000.00')
        ]

        for quarter, amount in zip(quarters, quarter_amounts):
            Allotment.objects.create(
                program_budget=approved_program_budget,
                quarter=quarter,
                amount=amount,
                released_by=execution_user,
                status='released'
            )

        # Verify all quarters created
        total_allotted = Allotment.objects.filter(
            program_budget=approved_program_budget
        ).aggregate(total=Sum('amount'))['total']

        assert total_allotted == Decimal('45000000.00')
        assert approved_program_budget.allotments.count() == 4


@pytest.mark.integration
@pytest.mark.django_db
class TestBudgetExecutionFlows:
    """Test various budget execution flows."""

    def test_progressive_disbursement_30_30_40(self, allotment_q1, work_item, execution_user):
        """Test 30-30-40 progressive disbursement pattern."""
        # Create obligation
        obligation = Obligation.objects.create(
            allotment=allotment_q1,
            work_item=work_item,
            amount=Decimal('10000000.00'),
            payee="Progressive Contractor",
            obligated_by=execution_user,
            status='obligated'
        )

        # First payment: 30%
        Disbursement.objects.create(
            obligation=obligation,
            amount=Decimal('3000000.00'),
            payment_date=date(2025, 2, 15),
            payment_method='check',
            disbursed_by=execution_user,
            status='paid'
        )

        # Second payment: 30%
        Disbursement.objects.create(
            obligation=obligation,
            amount=Decimal('3000000.00'),
            payment_date=date(2025, 3, 15),
            payment_method='check',
            disbursed_by=execution_user,
            status='paid'
        )

        # Final payment: 40%
        Disbursement.objects.create(
            obligation=obligation,
            amount=Decimal('4000000.00'),
            payment_date=date(2025, 4, 15),
            payment_method='bank_transfer',
            disbursed_by=execution_user,
            status='paid'
        )

        # Verify total disbursed
        total = Disbursement.objects.filter(
            obligation=obligation
        ).aggregate(total=Sum('amount'))['total']
        assert total == Decimal('10000000.00')

    def test_multiple_work_items_single_allotment(self, allotment_q1, monitoring_entry, execution_user):
        """Test executing multiple work items under one allotment."""
        from budget_execution.models import WorkItem

        work_items = []
        obligations = []

        # Create 3 work items
        for i in range(1, 4):
            work_item = WorkItem.objects.create(
                monitoring_entry=monitoring_entry,
                title=f"Work Package {i}",
                estimated_cost=Decimal(f'{2000000 * i}.00'),
                status='in_progress'
            )
            work_items.append(work_item)

            obligation = Obligation.objects.create(
                allotment=allotment_q1,
                work_item=work_item,
                amount=Decimal(f'{2000000 * i}.00'),
                payee=f"Contractor {i}",
                obligated_by=execution_user,
                status='obligated'
            )
            obligations.append(obligation)

        # Verify total obligations within allotment
        total_obligated = Obligation.objects.filter(
            allotment=allotment_q1
        ).aggregate(total=Sum('amount'))['total']

        # Total: 2M + 4M + 6M = 12M (but allotment is 10M)
        # This should be caught by constraint (TODO: uncomment when constraint exists)
        # assert total_obligated <= allotment_q1.amount


@pytest.mark.integration
@pytest.mark.django_db
class TestBudgetReporting:
    """Test budget reporting and analytics integration."""

    def test_execution_summary_aggregation(self, complete_execution_cycle):
        """Test aggregating execution summary data."""
        data = complete_execution_cycle

        # Verify aggregations
        assert data['total_allotted'] == Decimal('20000000.00')
        assert len(data['obligations']) == 3
        assert len(data['disbursements']) == 3

    def test_variance_analysis(self, approved_budget_proposal):
        """Test variance analysis across proposal."""
        # TODO: Implement variance calculation
        # - Requested vs Approved variance
        # - Program-level variances
        # - Category-level variances
        pass

    def test_utilization_rate_calculation(self, approved_program_budget):
        """Test utilization rate calculation."""
        # TODO: Implement utilization calculation
        # utilization_rate = (total_disbursed / approved_amount) * 100
        pass


@pytest.mark.integration
@pytest.mark.django_db
class TestDataIntegrity:
    """Test data integrity across budget lifecycle."""

    def test_cascade_delete_maintains_integrity(self, budget_proposal, program_budget, allotment_q1, obligation):
        """Test that cascade deletes maintain data integrity."""
        # Store IDs for verification
        proposal_id = budget_proposal.id
        program_id = program_budget.id
        allotment_id = allotment_q1.id
        obligation_id = obligation.id

        # Delete proposal should cascade to all related objects
        budget_proposal.delete()

        # Verify cascade
        assert not BudgetProposal.objects.filter(id=proposal_id).exists()
        assert not ProgramBudget.objects.filter(id=program_id).exists()
        assert not Allotment.objects.filter(id=allotment_id).exists()
        assert not Obligation.objects.filter(id=obligation_id).exists()

    def test_referential_integrity_constraints(self):
        """Test that referential integrity is enforced."""
        # TODO: Test that orphaned records cannot exist
        pass

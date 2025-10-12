"""
Unit tests for Budget Preparation models

Tests model creation, validation, relationships, and business logic.
"""

import pytest
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from budget_preparation.models import (
    BudgetProposal,
    ProgramBudget,
    BudgetLineItem,
    BudgetJustification
)


@pytest.mark.django_db
class TestBudgetProposal:
    """Test BudgetProposal model."""

    def test_create_budget_proposal(self, test_organization, test_user):
        """Test creating a budget proposal."""
        proposal = BudgetProposal.objects.create(
            organization=test_organization,
            fiscal_year=2025,
            title="Test FY 2025 Budget",
            description="Test budget proposal",
            total_requested_budget=Decimal('100000000.00'),
            status='draft',
            submitted_by=test_user
        )

        assert proposal.id is not None
        assert proposal.fiscal_year == 2025
        assert proposal.status == 'draft'
        assert proposal.organization == test_organization
        assert proposal.total_requested_budget == Decimal('100000000.00')

    def test_budget_proposal_str(self, budget_proposal):
        """Test __str__ method."""
        expected = f"{budget_proposal.organization.code} - FY{budget_proposal.fiscal_year}"
        assert str(budget_proposal) == expected

    def test_unique_fiscal_year_per_organization(self, test_organization, test_user):
        """Test unique constraint on organization + fiscal_year."""
        # Create first proposal
        BudgetProposal.objects.create(
            organization=test_organization,
            fiscal_year=2025,
            title="First Proposal",
            total_requested_budget=Decimal('1000000.00'),
            submitted_by=test_user
        )

        # Attempt to create duplicate should fail
        with pytest.raises(IntegrityError):
            BudgetProposal.objects.create(
                organization=test_organization,
                fiscal_year=2025,
                title="Duplicate Proposal",
                total_requested_budget=Decimal('2000000.00'),
                submitted_by=test_user
            )

    def test_submit_proposal(self, budget_proposal):
        """Test submitting a proposal changes status."""
        # TODO: Implement when submit() method exists
        pass

    def test_approve_proposal(self, budget_proposal, test_admin_user):
        """Test approving a proposal."""
        # TODO: Implement when approve() method exists
        pass

    def test_calculate_total_requested(self, budget_proposal):
        """Test auto-calculation of total requested budget from programs."""
        # TODO: Implement when calculation logic exists
        pass

    def test_variance_calculation(self, approved_budget_proposal):
        """Test variance between requested and approved budgets."""
        # TODO: Implement when get_variance() method exists
        pass


@pytest.mark.django_db
class TestProgramBudget:
    """Test ProgramBudget model."""

    def test_create_program_budget(self, budget_proposal, monitoring_entry):
        """Test creating a program budget."""
        pb = ProgramBudget.objects.create(
            budget_proposal=budget_proposal,
            monitoring_entry=monitoring_entry,
            requested_amount=Decimal('50000000.00'),
            priority_rank=1
        )

        assert pb.id is not None
        assert pb.requested_amount == Decimal('50000000.00')
        assert pb.approved_amount is None
        assert pb.priority_rank == 1

    def test_unique_constraint(self, budget_proposal, monitoring_entry):
        """Test unique constraint on budget_proposal + monitoring_entry."""
        # Create first program budget
        ProgramBudget.objects.create(
            budget_proposal=budget_proposal,
            monitoring_entry=monitoring_entry,
            requested_amount=Decimal('10000000.00'),
            priority_rank=1
        )

        # Attempt to create duplicate should fail
        with pytest.raises(IntegrityError):
            ProgramBudget.objects.create(
                budget_proposal=budget_proposal,
                monitoring_entry=monitoring_entry,
                requested_amount=Decimal('20000000.00'),
                priority_rank=2
            )

    def test_variance_calculation(self, program_budget):
        """Test variance calculation methods."""
        program_budget.approved_amount = Decimal('45000000.00')
        program_budget.save()

        variance = program_budget.get_variance()
        assert variance == Decimal('-5000000.00')

        variance_pct = program_budget.get_variance_percentage()
        assert variance_pct == Decimal('-10.00')

    def test_utilization_rate(self, approved_program_budget):
        """Test budget utilization rate calculation."""
        # TODO: Implement when allotments are created
        pass

    def test_execution_summary(self, approved_program_budget):
        """Test execution summary generation."""
        # TODO: Implement with allotments, obligations, disbursements
        pass


@pytest.mark.django_db
class TestBudgetLineItem:
    """Test BudgetLineItem model."""

    def test_create_line_item(self, program_budget):
        """Test creating a budget line item."""
        line_item = BudgetLineItem.objects.create(
            program_budget=program_budget,
            category='personnel',
            sub_category='salaries',
            description="Test Line Item",
            unit_cost=Decimal('50000.00'),
            quantity=12,
            total_cost=Decimal('600000.00')
        )

        assert line_item.id is not None
        assert line_item.category == 'personnel'
        assert line_item.total_cost == Decimal('600000.00')

    def test_total_cost_calculation(self, program_budget):
        """Test automatic total_cost calculation on save."""
        line_item = BudgetLineItem.objects.create(
            program_budget=program_budget,
            category='operating',
            description="Auto-calculate test",
            unit_cost=Decimal('1000.00'),
            quantity=10,
            total_cost=Decimal('0.00')  # Should be overwritten
        )

        # Verify total_cost was calculated
        line_item.refresh_from_db()
        assert line_item.total_cost == Decimal('10000.00')

    def test_line_item_categories(self, program_budget):
        """Test all line item categories (personnel, operating, capital)."""
        categories = ['personnel', 'operating', 'capital']

        for category in categories:
            item = BudgetLineItem.objects.create(
                program_budget=program_budget,
                category=category,
                description=f"{category} test",
                unit_cost=Decimal('1000.00'),
                quantity=1,
                total_cost=Decimal('1000.00')
            )
            assert item.category == category

    def test_aggregation_by_category(self, multiple_line_items):
        """Test aggregating line items by category."""
        # TODO: Implement aggregation test
        pass


@pytest.mark.django_db
class TestBudgetJustification:
    """Test BudgetJustification model."""

    def test_create_justification(self, budget_proposal):
        """Test creating budget justification."""
        justification = BudgetJustification.objects.create(
            budget_proposal=budget_proposal,
            section='executive_summary',
            content="Test justification content",
            order=1
        )

        assert justification.id is not None
        assert justification.section == 'executive_summary'
        assert justification.order == 1

    def test_ordering(self, budget_proposal):
        """Test justifications are ordered correctly."""
        j1 = BudgetJustification.objects.create(
            budget_proposal=budget_proposal,
            section='section_1',
            content="First",
            order=3
        )
        j2 = BudgetJustification.objects.create(
            budget_proposal=budget_proposal,
            section='section_2',
            content="Second",
            order=1
        )
        j3 = BudgetJustification.objects.create(
            budget_proposal=budget_proposal,
            section='section_3',
            content="Third",
            order=2
        )

        justifications = list(budget_proposal.justifications.all())
        assert justifications[0] == j2  # order=1
        assert justifications[1] == j3  # order=2
        assert justifications[2] == j1  # order=3


@pytest.mark.django_db
class TestBudgetIntegration:
    """Integration tests for budget preparation models."""

    def test_complete_proposal_structure(self, complete_budget_structure):
        """Test complete budget proposal with programs and line items."""
        data = complete_budget_structure

        assert data['proposal'].program_budgets.count() == 3
        assert BudgetLineItem.objects.filter(
            program_budget__budget_proposal=data['proposal']
        ).count() == 15

    def test_cascade_delete(self, budget_proposal, program_budget, budget_line_item):
        """Test cascade deletion of related objects."""
        proposal_id = budget_proposal.id
        program_id = program_budget.id
        line_item_id = budget_line_item.id

        # Delete proposal should cascade
        budget_proposal.delete()

        assert not BudgetProposal.objects.filter(id=proposal_id).exists()
        assert not ProgramBudget.objects.filter(id=program_id).exists()
        assert not BudgetLineItem.objects.filter(id=line_item_id).exists()

    def test_soft_delete_with_strategic_plan(self, program_budget, strategic_goal):
        """Test SET_NULL behavior when strategic goal is deleted."""
        program_budget.strategic_goal = strategic_goal
        program_budget.save()

        strategic_goal.delete()
        program_budget.refresh_from_db()

        assert program_budget.strategic_goal is None

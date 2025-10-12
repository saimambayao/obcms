"""
Budget Builder Service

Service layer for building and validating budget proposals.
Implements transaction-wrapped operations for data integrity.
"""

from django.db import transaction
from django.core.exceptions import ValidationError
from decimal import Decimal
from ..models import BudgetProposal, ProgramBudget, BudgetLineItem, BudgetJustification


class BudgetBuilderService:
    """Service for building and validating budget proposals."""

    @transaction.atomic
    def create_proposal(self, organization, fiscal_year, title, description, user):
        """
        Create a new budget proposal.

        Args:
            organization: Organization (MOA) creating the proposal
            fiscal_year: Fiscal year (e.g., 2025)
            title: Proposal title
            description: Proposal description
            user: User creating the proposal

        Returns:
            BudgetProposal: Created proposal instance

        Raises:
            ValidationError: If proposal already exists for org/fiscal_year
        """
        # Check for existing proposal
        existing = BudgetProposal.objects.filter(
            organization=organization,
            fiscal_year=fiscal_year
        ).exists()

        if existing:
            raise ValidationError(
                f"Budget proposal already exists for {organization} FY {fiscal_year}"
            )

        proposal = BudgetProposal.objects.create(
            organization=organization,
            fiscal_year=fiscal_year,
            title=title,
            description=description,
            submitted_by=user,
            total_proposed_budget=Decimal('0.00')
        )

        return proposal

    @transaction.atomic
    def add_program_budget(self, proposal, program, allocated_amount, priority, justification, expected_outputs=''):
        """
        Add a program budget to a proposal.

        Args:
            proposal: BudgetProposal instance
            program: WorkPlanObjective instance
            allocated_amount: Budget amount (Decimal or float)
            priority: Priority level ('high', 'medium', 'low')
            justification: Justification text
            expected_outputs: Expected outputs text (optional)

        Returns:
            ProgramBudget: Created program budget instance

        Raises:
            ValidationError: If validation fails
        """
        if not proposal.is_editable:
            raise ValidationError("Cannot modify submitted/approved proposals")

        # Check for duplicate program
        if ProgramBudget.objects.filter(budget_proposal=proposal, program=program).exists():
            raise ValidationError(f"Program {program} already exists in this proposal")

        program_budget = ProgramBudget.objects.create(
            budget_proposal=proposal,
            program=program,
            allocated_amount=Decimal(str(allocated_amount)),
            priority_level=priority,
            justification=justification,
            expected_outputs=expected_outputs or f"Expected outputs for {program.title}"
        )

        # Update proposal total
        self._update_proposal_total(proposal)

        return program_budget

    @transaction.atomic
    def add_line_item(self, program_budget, category, description, unit_cost, quantity, notes=''):
        """
        Add a line item to a program budget.

        Args:
            program_budget: ProgramBudget instance
            category: 'personnel', 'operating', or 'capital'
            description: Item description
            unit_cost: Cost per unit (Decimal or float)
            quantity: Number of units (int)
            notes: Additional notes (optional)

        Returns:
            BudgetLineItem: Created line item instance
        """
        if not program_budget.budget_proposal.is_editable:
            raise ValidationError("Cannot modify submitted/approved proposals")

        line_item = BudgetLineItem.objects.create(
            program_budget=program_budget,
            category=category,
            description=description,
            unit_cost=Decimal(str(unit_cost)),
            quantity=quantity,
            notes=notes
        )
        # total_cost is auto-calculated in save() method

        return line_item

    @transaction.atomic
    def submit_proposal(self, proposal, user):
        """
        Submit proposal for review.

        Args:
            proposal: BudgetProposal instance
            user: User submitting the proposal

        Raises:
            ValidationError: If proposal validation fails
        """
        # Validate completeness
        validation_errors = self.validate_proposal(proposal)
        if validation_errors:
            raise ValidationError(validation_errors)

        # Submit
        proposal.submit(user)

        return proposal

    def validate_proposal(self, proposal):
        """
        Validate budget proposal completeness.

        Args:
            proposal: BudgetProposal instance

        Returns:
            dict: Dictionary of validation errors (empty if valid)
        """
        errors = {}

        # Check if proposal has program budgets
        program_budgets = proposal.program_budgets.all()
        if not program_budgets.exists():
            errors['program_budgets'] = "Proposal must have at least one program budget"

        # Check each program budget has line items
        for pb in program_budgets:
            if not pb.line_items.exists():
                errors[f'program_{pb.id}'] = f"Program '{pb.program.title}' must have budget line items"

            # Check line items total matches allocated amount
            line_items_total = pb.line_items_total
            allocated = pb.allocated_amount
            variance = abs(line_items_total - allocated)

            if variance > Decimal('0.01'):  # Allow 1 cent tolerance
                errors[f'program_{pb.id}_variance'] = (
                    f"Program '{pb.program.title}': Line items total (₱{line_items_total:,.2f}) "
                    f"does not match allocated amount (₱{allocated:,.2f})"
                )

        # Check proposal total matches sum of program budgets
        program_total = proposal.allocated_total
        proposal_total = proposal.total_proposed_budget
        variance = abs(program_total - proposal_total)

        if variance > Decimal('0.01'):
            errors['total_variance'] = (
                f"Proposal total (₱{proposal_total:,.2f}) does not match "
                f"sum of program budgets (₱{program_total:,.2f})"
            )

        return errors

    def _update_proposal_total(self, proposal):
        """Update proposal total from program budgets."""
        total = proposal.allocated_total
        proposal.total_proposed_budget = total
        proposal.save(update_fields=['total_proposed_budget', 'updated_at'])

    @transaction.atomic
    def add_justification(self, program_budget, rationale, alignment, expected_impact,
                         needs_assessment=None, monitoring_entry=None):
        """
        Add evidence-based justification to a program budget.

        Args:
            program_budget: ProgramBudget instance
            rationale: Rationale text
            alignment: Alignment with priorities text
            expected_impact: Expected impact text
            needs_assessment: Optional Assessment FK
            monitoring_entry: Optional MonitoringEntry FK

        Returns:
            BudgetJustification: Created justification instance
        """
        justification = BudgetJustification.objects.create(
            program_budget=program_budget,
            rationale=rationale,
            alignment_with_priorities=alignment,
            expected_impact=expected_impact,
            needs_assessment_reference=needs_assessment,
            monitoring_entry_reference=monitoring_entry
        )

        return justification

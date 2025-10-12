"""
Budget Execution Service Layer
Compliance: Parliament Bill No. 325 Section 78

All financial operations use @transaction.atomic for data integrity.
PostgreSQL triggers provide triple-layer validation:
1. Django model clean() validation
2. Database CHECK constraints
3. PostgreSQL triggers (real-time balance validation)
"""

from django.db import transaction
from django.core.exceptions import ValidationError
from decimal import Decimal
from datetime import date
from typing import Optional
import logging

from ..models import Allotment, Obligation, Disbursement, DisbursementLineItem
from budget_preparation.models import ProgramBudget
from monitoring.models import MonitoringEntry

logger = logging.getLogger(__name__)


class AllotmentReleaseService:
    """
    Service for managing budget execution lifecycle:
    - Allotment releases (quarterly)
    - Obligation creation (purchase orders, contracts)
    - Disbursement recording (actual payments)
    """

    # ========================================================================
    # ALLOTMENT MANAGEMENT
    # ========================================================================

    @transaction.atomic
    def release_allotment(
        self,
        program_budget: ProgramBudget,
        quarter: int,
        amount: Decimal,
        created_by,
        release_date: Optional[date] = None,
        allotment_order_number: str = "",
        notes: str = ""
    ) -> Allotment:
        """
        Release a quarterly allotment from an approved program budget.

        Args:
            program_budget: The approved program budget to release from
            quarter: Quarter number (1-4)
            amount: Allotment amount to release
            created_by: User releasing the allotment
            release_date: Official release date (defaults to today)
            allotment_order_number: Official document reference
            notes: Additional remarks

        Returns:
            Created Allotment instance

        Raises:
            ValidationError: If allotment exceeds approved budget or already exists for quarter
        """
        # Validate program budget is approved
        if not program_budget.approved_amount:
            raise ValidationError(
                f"Program budget {program_budget} has no approved amount. "
                "Cannot release allotment."
            )

        # Check if allotment already exists for this quarter
        existing = Allotment.objects.filter(
            program_budget=program_budget,
            quarter=quarter
        ).first()

        if existing:
            raise ValidationError(
                f"Allotment for {program_budget} Q{quarter} already exists. "
                f"Cannot create duplicate allotment."
            )

        # Create allotment (model validation will check total doesn't exceed approved)
        allotment = Allotment.objects.create(
            program_budget=program_budget,
            quarter=quarter,
            amount=amount,
            status='released',
            release_date=release_date or date.today(),
            allotment_order_number=allotment_order_number,
            notes=notes,
            created_by=created_by
        )

        logger.info(
            f"Allotment released: {allotment.id} | "
            f"Program: {program_budget} | Q{quarter} | "
            f"Amount: P{amount:,.2f}"
        )

        return allotment

    @transaction.atomic
    def update_allotment_status(self, allotment: Allotment, status: str) -> Allotment:
        """
        Update allotment status.

        Args:
            allotment: Allotment to update
            status: New status (pending, released, partially_utilized, fully_utilized, cancelled)

        Returns:
            Updated Allotment instance
        """
        old_status = allotment.status
        allotment.status = status
        allotment.save()

        logger.info(
            f"Allotment status updated: {allotment.id} | "
            f"{old_status} -> {status}"
        )

        return allotment

    # ========================================================================
    # OBLIGATION MANAGEMENT
    # ========================================================================

    @transaction.atomic
    def create_obligation(
        self,
        allotment: Allotment,
        description: str,
        amount: Decimal,
        obligated_date: date,
        created_by,
        document_ref: str = "",
        monitoring_entry: Optional[MonitoringEntry] = None,
        notes: str = ""
    ) -> Obligation:
        """
        Create an obligation against an allotment.

        Args:
            allotment: Allotment to obligate against
            description: Description of obligation (e.g., "Purchase Order #12345")
            amount: Obligation amount
            obligated_date: Date of obligation
            created_by: User creating the obligation
            document_ref: PO/Contract number
            monitoring_entry: Optional link to M&E entry
            notes: Additional remarks

        Returns:
            Created Obligation instance

        Raises:
            ValidationError: If obligation exceeds available allotment balance
        """
        # Create obligation (model validation + PostgreSQL trigger will validate)
        obligation = Obligation.objects.create(
            allotment=allotment,
            description=description,
            amount=amount,
            obligated_date=obligated_date,
            document_ref=document_ref,
            monitoring_entry=monitoring_entry,
            status='committed',
            notes=notes,
            created_by=created_by
        )

        logger.info(
            f"Obligation created: {obligation.id} | "
            f"Allotment: {allotment.id} | "
            f"Amount: P{amount:,.2f} | "
            f"Document: {document_ref}"
        )

        return obligation

    @transaction.atomic
    def update_obligation_status(self, obligation: Obligation, status: str) -> Obligation:
        """
        Update obligation status.

        Args:
            obligation: Obligation to update
            status: New status (pending, committed, partially_disbursed, fully_disbursed, cancelled)

        Returns:
            Updated Obligation instance
        """
        old_status = obligation.status
        obligation.status = status
        obligation.save()

        logger.info(
            f"Obligation status updated: {obligation.id} | "
            f"{old_status} -> {status}"
        )

        return obligation

    # ========================================================================
    # DISBURSEMENT MANAGEMENT
    # ========================================================================

    @transaction.atomic
    def record_disbursement(
        self,
        obligation: Obligation,
        amount: Decimal,
        disbursed_date: date,
        payee: str,
        payment_method: str,
        created_by,
        check_number: str = "",
        voucher_number: str = "",
        notes: str = ""
    ) -> Disbursement:
        """
        Record a disbursement for an obligation.

        Args:
            obligation: Obligation to disburse against
            amount: Disbursement amount
            disbursed_date: Date of payment
            payee: Name of payee
            payment_method: Payment method (check, bank_transfer, cash, other)
            created_by: User recording disbursement
            check_number: Check number if applicable
            voucher_number: Voucher number
            notes: Additional remarks

        Returns:
            Created Disbursement instance

        Raises:
            ValidationError: If disbursement exceeds available obligation balance
        """
        # Create disbursement (model validation + PostgreSQL trigger will validate)
        # PostgreSQL trigger will also auto-update obligation status
        disbursement = Disbursement.objects.create(
            obligation=obligation,
            amount=amount,
            disbursed_date=disbursed_date,
            payee=payee,
            check_number=check_number,
            voucher_number=voucher_number,
            payment_method=payment_method,
            notes=notes,
            created_by=created_by
        )

        logger.info(
            f"Disbursement recorded: {disbursement.id} | "
            f"Obligation: {obligation.id} | "
            f"Amount: P{amount:,.2f} | "
            f"Payee: {payee}"
        )

        return disbursement

    @transaction.atomic
    def add_line_item(
        self,
        disbursement: Disbursement,
        description: str,
        amount: Decimal,
        cost_center: str = "",
        monitoring_entry: Optional[MonitoringEntry] = None,
        notes: str = ""
    ) -> DisbursementLineItem:
        """
        Add a line item breakdown to a disbursement.

        Args:
            disbursement: Disbursement to add line item to
            description: Item description
            amount: Line item amount
            cost_center: Optional cost center code
            monitoring_entry: Optional link to M&E entry
            notes: Additional remarks

        Returns:
            Created DisbursementLineItem instance
        """
        line_item = DisbursementLineItem.objects.create(
            disbursement=disbursement,
            description=description,
            amount=amount,
            cost_center=cost_center,
            monitoring_entry=monitoring_entry,
            notes=notes
        )

        logger.info(
            f"Line item created: {line_item.id} | "
            f"Disbursement: {disbursement.id} | "
            f"Amount: P{amount:,.2f}"
        )

        return line_item

    # ========================================================================
    # QUERY METHODS
    # ========================================================================

    def get_available_balance(self, allotment: Allotment) -> Decimal:
        """
        Calculate available balance for an allotment.

        Args:
            allotment: Allotment to calculate balance for

        Returns:
            Available balance (allotment amount - total obligations)
        """
        return allotment.get_remaining_balance()

    def get_obligation_balance(self, obligation: Obligation) -> Decimal:
        """
        Calculate remaining balance for an obligation.

        Args:
            obligation: Obligation to calculate balance for

        Returns:
            Remaining balance (obligation amount - total disbursements)
        """
        return obligation.get_remaining_balance()

    def get_utilization_rate(self, allotment: Allotment) -> Decimal:
        """
        Calculate utilization percentage for an allotment.

        Args:
            allotment: Allotment to calculate utilization for

        Returns:
            Utilization rate as percentage (0-100)
        """
        return allotment.get_utilization_rate()

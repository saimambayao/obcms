"""
Budget Distribution Service for MOA PPAs and WorkItem Hierarchy

This service handles budget allocation distribution from MonitoringEntry (PPA) to
hierarchical WorkItem structures using precise Decimal calculations.

Features:
- Equal distribution across work items
- Weighted distribution based on custom weights
- Manual distribution with validation
- Budget rollup validation
- Decimal precision (avoiding float errors)

Usage:
    from monitoring.services.budget_distribution import BudgetDistributionService

    # Equal distribution
    distribution = BudgetDistributionService.distribute_equal(ppa, work_items)
    count = BudgetDistributionService.apply_distribution(ppa, distribution)

    # Weighted distribution
    weights = {work_item_1.id: 0.4, work_item_2.id: 0.6}
    distribution = BudgetDistributionService.distribute_weighted(ppa, work_items, weights)
    count = BudgetDistributionService.apply_distribution(ppa, distribution)

    # Manual distribution
    allocations = {work_item_1.id: Decimal('50000.00'), work_item_2.id: Decimal('30000.00')}
    distribution = BudgetDistributionService.distribute_manual(ppa, allocations)
    count = BudgetDistributionService.apply_distribution(ppa, distribution)

Author: OBCMS Development Team
Date: 2025-10-06
"""

from decimal import Decimal, ROUND_DOWN, ROUND_UP, InvalidOperation
from typing import Dict, List, Optional, Union
import uuid

from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Sum, Q

from monitoring.models import MonitoringEntry
from common.models import WorkItem


# Constants
ZERO_DECIMAL = Decimal("0.00")
TOLERANCE = Decimal("0.01")  # Allow 1 centavo tolerance for rounding


class BudgetDistributionService:
    """
    Service class for distributing PPA budgets across WorkItem hierarchy.

    This service ensures precise budget distribution using Decimal arithmetic
    and validates that distributed amounts match the PPA's budget_allocation.
    """

    @staticmethod
    def _validate_ppa(ppa: MonitoringEntry) -> Decimal:
        """
        Validate PPA has a budget allocation.

        Args:
            ppa: MonitoringEntry instance to validate

        Returns:
            Decimal: The validated budget allocation amount

        Raises:
            ValidationError: If PPA has no budget allocation or allocation is zero/negative
        """
        if not isinstance(ppa, MonitoringEntry):
            raise ValidationError("Invalid PPA: must be a MonitoringEntry instance")

        if ppa.budget_allocation is None:
            raise ValidationError(
                f"PPA '{ppa.title}' has no budget allocation set. "
                "Please set budget_allocation before distributing."
            )

        budget = Decimal(str(ppa.budget_allocation))

        if budget <= ZERO_DECIMAL:
            raise ValidationError(
                f"PPA '{ppa.title}' has invalid budget allocation: {budget}. "
                "Budget must be greater than zero."
            )

        return budget

    @staticmethod
    def _validate_work_items(work_items: List[WorkItem]) -> List[WorkItem]:
        """
        Validate work items list is not empty and all items are valid.

        Args:
            work_items: List of WorkItem instances

        Returns:
            List[WorkItem]: Validated work items list

        Raises:
            ValidationError: If work items list is empty or contains invalid items
        """
        if not work_items:
            raise ValidationError("Cannot distribute budget: no work items provided")

        if not isinstance(work_items, (list, tuple)):
            raise ValidationError("work_items must be a list or tuple")

        for item in work_items:
            if not isinstance(item, WorkItem):
                raise ValidationError(
                    f"Invalid work item: {item}. All items must be WorkItem instances."
                )

        return work_items

    @staticmethod
    def distribute_equal(
        ppa: MonitoringEntry, work_items: Union[List[WorkItem], None] = None
    ) -> Dict[uuid.UUID, Decimal]:
        """
        Distribute PPA budget equally across all work items.

        If the budget does not divide evenly, the remainder is assigned to the
        first work item to ensure the total matches exactly.

        Args:
            ppa: MonitoringEntry with budget_allocation set
            work_items: List of WorkItem instances to distribute budget across.
                       If None, fetches all related work items from ppa.

        Returns:
            Dict[uuid.UUID, Decimal]: Mapping of work_item.id to allocated amount

        Raises:
            ValidationError: If PPA has no budget, work_items is empty, or validation fails

        Example:
            >>> distribution = BudgetDistributionService.distribute_equal(ppa, [wi1, wi2, wi3])
            >>> # Budget: 100000.00, 3 items
            >>> # Result: {wi1.id: 33333.34, wi2.id: 33333.33, wi3.id: 33333.33}
        """
        budget = BudgetDistributionService._validate_ppa(ppa)

        # If work_items not provided, fetch from PPA
        if work_items is None:
            work_items = list(ppa.work_items.all())

        work_items = BudgetDistributionService._validate_work_items(work_items)

        item_count = len(work_items)

        # Calculate base amount per item (rounded down to 2 decimal places)
        base_amount = (budget / item_count).quantize(Decimal("0.01"), rounding=ROUND_DOWN)

        # Calculate remainder
        total_base = base_amount * item_count
        remainder = budget - total_base

        # Build distribution dictionary
        distribution = {}

        for i, work_item in enumerate(work_items):
            if i == 0:
                # First item gets base amount + remainder
                distribution[work_item.id] = base_amount + remainder
            else:
                distribution[work_item.id] = base_amount

        # Validate total matches budget
        total = sum(distribution.values())
        if abs(total - budget) > TOLERANCE:
            raise ValidationError(
                f"Distribution total ({total}) does not match budget ({budget}). "
                f"Difference: {abs(total - budget)}"
            )

        return distribution

    @staticmethod
    def distribute_weighted(
        ppa: MonitoringEntry,
        work_items: Union[List[WorkItem], None] = None,
        weights: Optional[Dict[uuid.UUID, float]] = None,
    ) -> Dict[uuid.UUID, Decimal]:
        """
        Distribute PPA budget based on provided weights.

        Weights should sum to 1.0 (100%). If they don't, a ValidationError is raised.

        Args:
            ppa: MonitoringEntry with budget_allocation set
            work_items: List of WorkItem instances to distribute budget across.
                       If None, fetches all related work items from ppa.
            weights: Dict mapping work_item.id to weight (0.0 to 1.0).
                    Weights must sum to 1.0.

        Returns:
            Dict[uuid.UUID, Decimal]: Mapping of work_item.id to allocated amount

        Raises:
            ValidationError: If weights don't sum to 1.0, missing work items, or validation fails

        Example:
            >>> weights = {wi1.id: 0.5, wi2.id: 0.3, wi3.id: 0.2}
            >>> distribution = BudgetDistributionService.distribute_weighted(ppa, [wi1, wi2, wi3], weights)
            >>> # Budget: 100000.00
            >>> # Result: {wi1.id: 50000.00, wi2.id: 30000.00, wi3.id: 20000.00}
        """
        budget = BudgetDistributionService._validate_ppa(ppa)

        # If work_items not provided, fetch from PPA
        if work_items is None:
            work_items = list(ppa.work_items.all())

        work_items = BudgetDistributionService._validate_work_items(work_items)

        if weights is None:
            raise ValidationError("Weights dictionary is required for weighted distribution")

        # Validate weights provided for all work items
        work_item_ids = {item.id for item in work_items}
        weight_ids = set(weights.keys())

        missing_weights = work_item_ids - weight_ids
        if missing_weights:
            raise ValidationError(
                f"Missing weights for work items: {missing_weights}. "
                "All work items must have weights assigned."
            )

        extra_weights = weight_ids - work_item_ids
        if extra_weights:
            raise ValidationError(
                f"Weights provided for non-existent work items: {extra_weights}"
            )

        # Validate weights are valid numbers and sum to 1.0
        try:
            weight_sum = Decimal("0")
            for work_item_id, weight in weights.items():
                weight_decimal = Decimal(str(weight))
                if weight_decimal < 0:
                    raise ValidationError(
                        f"Invalid weight for {work_item_id}: {weight}. "
                        "Weights must be non-negative."
                    )
                weight_sum += weight_decimal
        except (InvalidOperation, ValueError) as e:
            raise ValidationError(f"Invalid weight value: {e}")

        # Allow small tolerance for floating point precision
        if abs(weight_sum - Decimal("1.0")) > Decimal("0.0001"):
            raise ValidationError(
                f"Weights must sum to 1.0 (100%). Current sum: {weight_sum}"
            )

        # Calculate weighted distribution
        distribution = {}
        running_total = ZERO_DECIMAL

        # Sort work items for consistent processing
        sorted_items = sorted(work_items, key=lambda x: str(x.id))

        for i, work_item in enumerate(sorted_items):
            weight = Decimal(str(weights[work_item.id]))

            if i == len(sorted_items) - 1:
                # Last item gets remainder to ensure exact total
                distribution[work_item.id] = budget - running_total
            else:
                amount = (budget * weight).quantize(Decimal("0.01"), rounding=ROUND_DOWN)
                distribution[work_item.id] = amount
                running_total += amount

        # Validate total matches budget
        total = sum(distribution.values())
        if abs(total - budget) > TOLERANCE:
            raise ValidationError(
                f"Distribution total ({total}) does not match budget ({budget}). "
                f"Difference: {abs(total - budget)}"
            )

        return distribution

    @staticmethod
    def distribute_manual(
        ppa: MonitoringEntry, allocations: Dict[uuid.UUID, Union[Decimal, float, str]]
    ) -> Dict[uuid.UUID, Decimal]:
        """
        Validate and return manual budget allocations.

        Validates that:
        1. All allocations are valid Decimal amounts
        2. Sum of allocations equals PPA budget (within tolerance)
        3. All work items in allocations exist in the database

        Args:
            ppa: MonitoringEntry with budget_allocation set
            allocations: Dict mapping work_item.id to manually assigned amount

        Returns:
            Dict[uuid.UUID, Decimal]: Validated allocation dictionary (converted to Decimal)

        Raises:
            ValidationError: If allocations don't sum to budget or validation fails

        Example:
            >>> allocations = {wi1.id: Decimal('50000.00'), wi2.id: Decimal('50000.00')}
            >>> distribution = BudgetDistributionService.distribute_manual(ppa, allocations)
        """
        budget = BudgetDistributionService._validate_ppa(ppa)

        if not allocations:
            raise ValidationError("Manual allocations dictionary cannot be empty")

        # Convert all allocations to Decimal and validate
        validated_allocations = {}
        total = ZERO_DECIMAL

        try:
            for work_item_id, amount in allocations.items():
                # Ensure work_item_id is UUID
                if not isinstance(work_item_id, uuid.UUID):
                    try:
                        work_item_id = uuid.UUID(str(work_item_id))
                    except (ValueError, AttributeError):
                        raise ValidationError(
                            f"Invalid work item ID: {work_item_id}. Must be a valid UUID."
                        )

                # Convert amount to Decimal
                amount_decimal = Decimal(str(amount))

                if amount_decimal < ZERO_DECIMAL:
                    raise ValidationError(
                        f"Invalid allocation for {work_item_id}: {amount_decimal}. "
                        "Allocations must be non-negative."
                    )

                validated_allocations[work_item_id] = amount_decimal
                total += amount_decimal

        except (InvalidOperation, ValueError) as e:
            raise ValidationError(f"Invalid allocation amount: {e}")

        # Validate sum equals budget (within tolerance)
        difference = abs(total - budget)
        if difference > TOLERANCE:
            raise ValidationError(
                f"Manual allocations total ({total}) does not match PPA budget ({budget}). "
                f"Difference: {difference}. "
                f"Allocations must sum to exactly {budget} (tolerance: {TOLERANCE})."
            )

        # Validate all work items exist in database
        work_item_ids = list(validated_allocations.keys())
        existing_ids = set(
            WorkItem.objects.filter(id__in=work_item_ids).values_list("id", flat=True)
        )

        missing_ids = set(work_item_ids) - existing_ids
        if missing_ids:
            raise ValidationError(
                f"Work items not found: {missing_ids}. "
                "All work items must exist in the database."
            )

        return validated_allocations

    @staticmethod
    @transaction.atomic
    def apply_distribution(
        ppa: MonitoringEntry, distribution: Dict[uuid.UUID, Decimal]
    ) -> int:
        """
        Apply calculated budget distribution to work items.

        Updates the allocated_budget field for each work item in the distribution.
        Validates budget rollup after application.

        This operation is atomic - if any update fails, all changes are rolled back.

        Args:
            ppa: MonitoringEntry the budget is distributed from
            distribution: Dict mapping work_item.id to allocated amount
                         (output from distribute_* methods)

        Returns:
            int: Number of work items updated

        Raises:
            ValidationError: If validation fails or rollup doesn't match PPA budget

        Example:
            >>> distribution = BudgetDistributionService.distribute_equal(ppa, work_items)
            >>> count = BudgetDistributionService.apply_distribution(ppa, distribution)
            >>> print(f"Updated {count} work items")
        """
        budget = BudgetDistributionService._validate_ppa(ppa)

        if not distribution:
            raise ValidationError("Distribution dictionary cannot be empty")

        # Validate distribution total
        total = sum(distribution.values())
        if abs(total - budget) > TOLERANCE:
            raise ValidationError(
                f"Cannot apply distribution: total ({total}) does not match "
                f"PPA budget ({budget}). Difference: {abs(total - budget)}"
            )

        # Fetch all work items to update
        work_item_ids = list(distribution.keys())
        work_items = WorkItem.objects.filter(id__in=work_item_ids)

        if work_items.count() != len(work_item_ids):
            found_ids = set(work_items.values_list("id", flat=True))
            missing_ids = set(work_item_ids) - found_ids
            raise ValidationError(
                f"Cannot apply distribution: work items not found: {missing_ids}"
            )

        # Update each work item
        updated_count = 0
        for work_item in work_items:
            allocated_amount = distribution[work_item.id]
            work_item.allocated_budget = allocated_amount
            work_item.save(update_fields=["allocated_budget", "updated_at"])
            updated_count += 1

        # Validate rollup: sum of all related work items should equal PPA budget
        actual_total = (
            ppa.work_items.aggregate(total=Sum("allocated_budget"))["total"] or ZERO_DECIMAL
        )
        actual_total = Decimal(str(actual_total))

        if abs(actual_total - budget) > TOLERANCE:
            raise ValidationError(
                f"Budget rollup validation failed after distribution. "
                f"PPA budget: {budget}, WorkItem total: {actual_total}. "
                f"Difference: {abs(actual_total - budget)}"
            )

        return updated_count

    @staticmethod
    def get_current_distribution(ppa: MonitoringEntry) -> Dict[uuid.UUID, Decimal]:
        """
        Get current budget distribution for a PPA's work items.

        Args:
            ppa: MonitoringEntry instance

        Returns:
            Dict[uuid.UUID, Decimal]: Current allocation per work item

        Example:
            >>> current = BudgetDistributionService.get_current_distribution(ppa)
            >>> for work_item_id, amount in current.items():
            ...     print(f"{work_item_id}: {amount}")
        """
        work_items = ppa.work_items.all()

        distribution = {}
        for work_item in work_items:
            if work_item.allocated_budget:
                distribution[work_item.id] = Decimal(str(work_item.allocated_budget))
            else:
                distribution[work_item.id] = ZERO_DECIMAL

        return distribution

    @staticmethod
    def clear_distribution(ppa: MonitoringEntry) -> int:
        """
        Clear all budget allocations for a PPA's work items.

        Sets allocated_budget to None for all related work items.

        Args:
            ppa: MonitoringEntry instance

        Returns:
            int: Number of work items cleared

        Example:
            >>> count = BudgetDistributionService.clear_distribution(ppa)
            >>> print(f"Cleared {count} work items")
        """
        return ppa.work_items.update(allocated_budget=None)

    @staticmethod
    def validate_rollup(ppa: MonitoringEntry) -> Dict[str, Union[Decimal, bool, str]]:
        """
        Validate that work item budget allocations roll up correctly to PPA budget.

        Args:
            ppa: MonitoringEntry instance

        Returns:
            Dict with validation results:
                - ppa_budget: PPA budget_allocation
                - work_items_total: Sum of work item allocated_budget
                - difference: Absolute difference
                - is_valid: True if within tolerance
                - message: Validation message

        Example:
            >>> result = BudgetDistributionService.validate_rollup(ppa)
            >>> if not result['is_valid']:
            ...     print(result['message'])
        """
        budget = ppa.budget_allocation or ZERO_DECIMAL
        budget = Decimal(str(budget))

        work_items_total = (
            ppa.work_items.aggregate(total=Sum("allocated_budget"))["total"] or ZERO_DECIMAL
        )
        work_items_total = Decimal(str(work_items_total))

        difference = abs(work_items_total - budget)
        is_valid = difference <= TOLERANCE

        if is_valid:
            message = f"Budget rollup is valid (difference: {difference})"
        else:
            message = (
                f"Budget rollup validation failed. "
                f"PPA budget: {budget}, WorkItem total: {work_items_total}, "
                f"Difference: {difference} (tolerance: {TOLERANCE})"
            )

        return {
            "ppa_budget": budget,
            "work_items_total": work_items_total,
            "difference": difference,
            "is_valid": is_valid,
            "message": message,
        }

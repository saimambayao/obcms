from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from decimal import Decimal
import uuid


class BudgetLineItem(models.Model):
    """
    Detailed line items for program budgets

    Provides granular budget breakdown by object code
    """

    # Primary Key
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    # Parent program budget
    program_budget = models.ForeignKey(
        'ProgramBudget',
        on_delete=models.CASCADE,
        related_name='line_items',
        help_text="Program budget this line item belongs to"
    )

    # Object code (e.g., 5-01-01-010 for Personnel Services)
    object_code = models.CharField(
        max_length=50,
        help_text="Budget object code (e.g., 5-01-01-010)"
    )

    # Description
    description = models.CharField(
        max_length=255,
        help_text="Line item description"
    )

    # Quantity
    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Quantity of items"
    )

    # Unit
    unit = models.CharField(
        max_length=50,
        help_text="Unit of measurement (e.g., pieces, months, trips)"
    )

    # Unit cost
    unit_cost = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Cost per unit"
    )

    # Total cost (calculated: quantity * unit_cost)
    total_cost = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],

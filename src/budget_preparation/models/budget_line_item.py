"""
Budget Line Item Model

Detailed cost breakdown for program budgets.
Implements appropriation classes (PS/MOOE/CO) per BARMM budget standards.
"""

from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal


class BudgetLineItem(models.Model):
    """
    Individual line items representing detailed budget breakdown.

    Categories follow BARMM budget structure:
    - Personnel Services (PS): Salaries, wages, benefits
    - Maintenance & Other Operating Expenses (MOOE): Operations, supplies
    - Capital Outlay (CO): Equipment, infrastructure
    """

    CATEGORY_CHOICES = [
        ('personnel', 'Personnel Services (PS)'),
        ('operating', 'Maintenance & Other Operating Expenses (MOOE)'),
        ('capital', 'Capital Outlay (CO)'),
    ]

    program_budget = models.ForeignKey(
        'ProgramBudget',
        on_delete=models.CASCADE,
        related_name='line_items',
        help_text="Parent program budget"
    )

    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default='operating',  # MOOE is the most common category
        help_text="Appropriation category (PS/MOOE/CO)"
    )

    description = models.CharField(
        max_length=255,
        help_text="Item description (e.g., 'Office Supplies', 'Training Materials')"
    )

    unit_cost = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Cost per unit (₱)"
    )

    quantity = models.IntegerField(
        validators=[MinValueValidator(1)],
        help_text="Number of units"
    )

    total_cost = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text="Total cost (auto-calculated: unit_cost × quantity)"
    )

    notes = models.TextField(
        blank=True,
        help_text="Additional notes or specifications"
    )

    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['category', '-total_cost']
        verbose_name = "Budget Line Item"
        verbose_name_plural = "Budget Line Items"
        indexes = [
            models.Index(fields=['program_budget', 'category']),
        ]

    def __str__(self):
        return f"{self.description} - ₱{self.total_cost:,.2f}"

    def save(self, *args, **kwargs):
        """Auto-calculate total_cost before saving."""
        self.total_cost = Decimal(str(self.unit_cost)) * Decimal(str(self.quantity))
        super().save(*args, **kwargs)

    @property
    def category_display_short(self):
        """Return short category code (PS/MOOE/CO)."""
        category_map = {
            'personnel': 'PS',
            'operating': 'MOOE',
            'capital': 'CO',
        }
        return category_map.get(self.category, self.category.upper())

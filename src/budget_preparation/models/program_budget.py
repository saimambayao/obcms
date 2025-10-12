"""
Program Budget Model

Links budget proposals to planning module work plan objectives.
Implements programmatic budgeting philosophy per Bill No. 325.
"""

from django.db import models
from django.core.validators import MinValueValidator


class ProgramBudget(models.Model):
    """
    Budget allocation for a specific program/objective within a budget proposal.

    Integration Note: Uses WorkPlanObjective from planning module as "program".
    This ensures budget allocations are linked to strategic planning objectives.
    """

    PRIORITY_CHOICES = [
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low'),
    ]

    budget_proposal = models.ForeignKey(
        'BudgetProposal',
        on_delete=models.CASCADE,
        related_name='program_budgets',
        help_text="Parent budget proposal"
    )

    # Integration with Phase 1 Planning Module
    program = models.ForeignKey(
        'planning.WorkPlanObjective',
        on_delete=models.PROTECT,
        related_name='budget_allocations',
        help_text="Work plan objective this budget supports"
    )

    allocated_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Budget amount allocated to this program (₱)"
    )

    priority_level = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default='medium',
        help_text="Priority level for this program budget"
    )

    justification = models.TextField(
        help_text="Justification for budget allocation amount"
    )

    expected_outputs = models.TextField(
        help_text="Expected deliverables and outputs from this program"
    )

    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-priority_level', '-allocated_amount']
        verbose_name = "Program Budget"
        verbose_name_plural = "Program Budgets"
        unique_together = [['budget_proposal', 'program']]
        indexes = [
            models.Index(fields=['budget_proposal', 'priority_level']),
        ]

    def __str__(self):
        return f"{self.program.title} - ₱{self.allocated_amount:,.2f}"

    @property
    def line_items_total(self):
        """Calculate total from all budget line items."""
        return self.line_items.aggregate(
            total=models.Sum('total_cost')
        )['total'] or 0

    @property
    def has_variance(self):
        """Check if line items total differs from allocated amount."""
        return abs(self.line_items_total - self.allocated_amount) > 0.01

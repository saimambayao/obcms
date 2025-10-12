from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from decimal import Decimal
import uuid


class Allotment(models.Model):
    """
    Quarterly budget allotments (releases from approved program budgets)

    Financial Constraint: SUM(allotments per program) d ProgramBudget.approved_amount
    Legal Requirement: Parliament Bill No. 325 Section 45 - Allotment Release

    BMMS Ready: Inherits organization from parent ProgramBudget
    """

    QUARTER_CHOICES = [
        (1, 'Q1 (Jan-Mar)'),
        (2, 'Q2 (Apr-Jun)'),
        (3, 'Q3 (Jul-Sep)'),
        (4, 'Q4 (Oct-Dec)'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('released', 'Released'),
        ('partially_utilized', 'Partially Utilized'),
        ('fully_utilized', 'Fully Utilized'),
        ('cancelled', 'Cancelled'),
    ]

    # Primary Key
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    # Link to approved program budget
    program_budget = models.ForeignKey(
        'budget_preparation.ProgramBudget',
        on_delete=models.CASCADE,
        related_name='allotments',
        help_text="Program budget this allotment is released from"
    )

    # Quarter
    quarter = models.IntegerField(
        choices=QUARTER_CHOICES,
        help_text="Quarter (1-4)"
    )

    # Allotment amount
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Allotment amount released"
    )

    # Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        db_index=True,
        help_text="Allotment status"
    )

    # Release details
    release_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date allotment was released"
    )
    allotment_order_number = models.CharField(
        max_length=50,
        blank=True,
        help_text="Official allotment order number"
    )

    # Notes
    notes = models.TextField(
        blank=True,
        help_text="Additional notes or remarks"
    )

    # Audit trail
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        'common.User',
        on_delete=models.PROTECT,
        related_name='allotments_created'
    )

    class Meta:
        db_table = 'budget_execution_allotment'
        ordering = ['program_budget', 'quarter']
        unique_together = [['program_budget', 'quarter']]  # One allotment per quarter
        verbose_name = 'Allotment'
        verbose_name_plural = 'Allotments'
        indexes = [
            models.Index(fields=['program_budget', 'status']),
            models.Index(fields=['quarter']),
            models.Index(fields=['release_date']),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(amount__gte=Decimal('0.01')),
                name='allotment_positive_amount'
            ),
            models.CheckConstraint(
                check=models.Q(quarter__gte=1) & models.Q(quarter__lte=4),
                name='allotment_valid_quarter'
            ),
        ]

    def __str__(self):
        return f"{self.program_budget} - {self.get_quarter_display()} (₱{self.amount:,.2f})"

    def clean(self):
        """
        Validate allotment doesn't exceed approved budget

        Raises:
            ValidationError: If total allotments exceed approved budget
        """
        if not self.program_budget.approved_amount:
            raise ValidationError(
                "Cannot create allotment for program budget without approved amount"
            )

        # Calculate total allotments for this program
        from django.db.models import Sum
        total_allotted = self.program_budget.allotments.exclude(
            pk=self.pk
        ).aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0.00')

        total_allotted += self.amount

        # Check constraint
        if total_allotted > self.program_budget.approved_amount:
            raise ValidationError(
                f"Total allotments (₱{total_allotted:,.2f}) would exceed "
                f"approved budget (₱{self.program_budget.approved_amount:,.2f})"
            )

    def save(self, *args, **kwargs):
        """Override save to run validation"""
        self.full_clean()
        super().save(*args, **kwargs)

    def get_obligated_amount(self) -> Decimal:
        """Calculate total obligations against this allotment"""
        from django.db.models import Sum
        return self.obligations.aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0.00')

    def get_remaining_balance(self) -> Decimal:
        """Calculate remaining balance"""
        return self.amount - self.get_obligated_amount()

    def get_utilization_rate(self) -> Decimal:
        """Calculate utilization percentage"""
        if self.amount > 0:
            return (self.get_obligated_amount() / self.amount) * 100
        return Decimal('0.00')

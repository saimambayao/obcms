"""
Budget Proposal Model

Implements budget preparation for annual fiscal year planning.
Complies with Parliament Bill No. 325 (Bangsamoro Budget System Act).
"""

from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class BudgetProposal(models.Model):
    """
    Budget proposal submitted by an organization for a fiscal year.

    BMMS Note: Organization field provides multi-tenant data isolation.
    Each organization (MOA) can only see their own budget proposals.
    """

    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('under_review', 'Under Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    # BMMS Multi-tenancy: Organization-based isolation
    organization = models.ForeignKey(
        'coordination.Organization',
        on_delete=models.PROTECT,
        related_name='budget_proposals',
        help_text="MOA submitting this budget proposal"
    )

    fiscal_year = models.IntegerField(
        validators=[MinValueValidator(2024)],
        help_text="Fiscal year this budget is for (e.g., 2025)"
    )

    title = models.CharField(
        max_length=255,
        help_text="Budget proposal title"
    )

    description = models.TextField(
        blank=True,
        default='',
        help_text="Overview of budget proposal objectives and scope"
    )

    total_proposed_budget = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        help_text="Total budget amount proposed (₱)"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        help_text="Current status of budget proposal"
    )

    # Submission tracking
    submitted_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='submitted_budget_proposals',
        help_text="User who submitted this proposal"
    )

    submitted_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Date and time of submission"
    )

    # Review tracking
    reviewed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_budget_proposals',
        help_text="User who reviewed this proposal"
    )

    reviewed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Date and time of review"
    )

    approval_notes = models.TextField(
        blank=True,
        help_text="Reviewer notes and approval/rejection reasons"
    )

    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-fiscal_year', 'organization']
        verbose_name = "Budget Proposal"
        verbose_name_plural = "Budget Proposals"
        indexes = [
            models.Index(fields=['organization', 'fiscal_year']),
            models.Index(fields=['status']),
            models.Index(fields=['fiscal_year']),
        ]
        unique_together = [['organization', 'fiscal_year']]

    def __str__(self):
        return f"{self.organization} - FY {self.fiscal_year}"

    @property
    def is_editable(self):
        """Check if proposal can be edited (draft or rejected status)."""
        return self.status in ['draft', 'rejected']

    @property
    def allocated_total(self):
        """Calculate total allocated from all program budgets."""
        return self.program_budgets.aggregate(
            total=models.Sum('allocated_amount')
        )['total'] or 0

    def submit(self, user):
        """Submit proposal for review."""
        if self.status != 'draft':
            raise ValueError("Only draft proposals can be submitted")

        self.status = 'submitted'
        self.submitted_at = timezone.now()
        self.submitted_by = user
        self.save(update_fields=['status', 'submitted_at', 'submitted_by', 'updated_at'])

    def approve(self, user, notes=''):
        """Approve the budget proposal."""
        if self.status != 'under_review':
            raise ValueError("Only proposals under review can be approved")

        self.status = 'approved'
        self.reviewed_by = user
        self.reviewed_at = timezone.now()
        self.approval_notes = notes
        self.save(update_fields=['status', 'reviewed_by', 'reviewed_at', 'approval_notes', 'updated_at'])

    def reject(self, user, notes):
        """Reject the budget proposal."""
        if self.status != 'under_review':
            raise ValueError("Only proposals under review can be rejected")

        self.status = 'rejected'
        self.reviewed_by = user
        self.reviewed_at = timezone.now()
        self.approval_notes = notes
        self.save(update_fields=['status', 'reviewed_by', 'reviewed_at', 'approval_notes', 'updated_at'])

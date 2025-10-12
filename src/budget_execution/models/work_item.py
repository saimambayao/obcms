from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
import uuid


class DisbursementLineItem(models.Model):
    """
    Detailed breakdown of disbursement spending (formerly WorkItem)
    Renamed to avoid conflict with common.WorkItem
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    disbursement = models.ForeignKey('Disbursement', on_delete=models.CASCADE, related_name='line_items')
    monitoring_entry = models.ForeignKey('monitoring.MonitoringEntry', on_delete=models.SET_NULL, null=True, blank=True, related_name='disbursement_line_items')
    cost_center = models.CharField(max_length=100, blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    description = models.CharField(max_length=255)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'budget_execution_disbursement_line_item'
        ordering = ['-created_at']
        verbose_name = 'Disbursement Line Item'
        verbose_name_plural = 'Disbursement Line Items'
        indexes = [
            models.Index(fields=['disbursement']),
            models.Index(fields=['monitoring_entry']),
        ]
        constraints = [
            models.CheckConstraint(check=models.Q(amount__gte=Decimal('0.01')), name='disbursement_line_item_positive_amount'),
        ]

    def __str__(self):
        return f"{self.description} - ₱{self.amount:,.2f}"

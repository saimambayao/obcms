from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from decimal import Decimal
import uuid


class Obligation(models.Model):
    """
    Obligation records (purchase orders, contracts)
    
    Financial Constraint: SUM(obligations per allotment) ≤ Allotment.amount
    """
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('committed', 'Committed'),
        ('partially_disbursed', 'Partially Disbursed'),
        ('fully_disbursed', 'Fully Disbursed'),
        ('cancelled', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    allotment = models.ForeignKey('Allotment', on_delete=models.CASCADE, related_name='obligations')
    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    obligated_date = models.DateField()
    document_ref = models.CharField(max_length=100, blank=True, help_text="PO/Contract number")
    monitoring_entry = models.ForeignKey('monitoring.MonitoringEntry', on_delete=models.SET_NULL, null=True, blank=True, related_name='obligations')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', db_index=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey('common.User', on_delete=models.PROTECT, related_name='obligations_created')
    
    class Meta:
        db_table = 'budget_execution_obligation'
        ordering = ['-obligated_date']
        verbose_name = 'Obligation'
        verbose_name_plural = 'Obligations'
        indexes = [
            models.Index(fields=['allotment', 'status']),
            models.Index(fields=['-obligated_date']),
        ]
        constraints = [
            models.CheckConstraint(check=models.Q(amount__gte=Decimal('0.01')), name='obligation_positive_amount'),
        ]
    
    def __str__(self):
        return f"{self.description} - ₱{self.amount:,.2f}"
    
    def clean(self):
        from django.db.models import Sum
        total_obligated = self.allotment.obligations.exclude(pk=self.pk).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        total_obligated += self.amount
        if total_obligated > self.allotment.amount:
            raise ValidationError(f"Total obligations (₱{total_obligated:,.2f}) would exceed allotment (₱{self.allotment.amount:,.2f})")
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
    
    def get_disbursed_amount(self) -> Decimal:
        from django.db.models import Sum
        return self.disbursements.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    
    def get_remaining_balance(self) -> Decimal:
        return self.amount - self.get_disbursed_amount()

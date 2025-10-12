from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from decimal import Decimal
import uuid


class Disbursement(models.Model):
    """
    Actual payment disbursements
    
    Financial Constraint: SUM(disbursements per obligation) ≤ Obligation.amount
    """
    
    PAYMENT_METHOD_CHOICES = [
        ('check', 'Check'),
        ('bank_transfer', 'Bank Transfer'),
        ('cash', 'Cash'),
        ('other', 'Other'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    obligation = models.ForeignKey('Obligation', on_delete=models.CASCADE, related_name='disbursements')
    amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    disbursed_date = models.DateField()
    payee = models.CharField(max_length=255)
    check_number = models.CharField(max_length=50, blank=True)
    voucher_number = models.CharField(max_length=50, blank=True)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='check')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey('common.User', on_delete=models.PROTECT, related_name='disbursements_created')
    
    class Meta:
        db_table = 'budget_execution_disbursement'
        ordering = ['-disbursed_date']
        verbose_name = 'Disbursement'
        verbose_name_plural = 'Disbursements'
        indexes = [
            models.Index(fields=['obligation']),
            models.Index(fields=['-disbursed_date']),
        ]
        constraints = [
            models.CheckConstraint(check=models.Q(amount__gte=Decimal('0.01')), name='disbursement_positive_amount'),
        ]
    
    def __str__(self):
        return f"{self.payee} - ₱{self.amount:,.2f} ({self.disbursed_date})"
    
    def clean(self):
        from django.db.models import Sum
        total_disbursed = self.obligation.disbursements.exclude(pk=self.pk).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        total_disbursed += self.amount
        if total_disbursed > self.obligation.amount:
            raise ValidationError(f"Total disbursements (₱{total_disbursed:,.2f}) would exceed obligation (₱{self.obligation.amount:,.2f})")
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

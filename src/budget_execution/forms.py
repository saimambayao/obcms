"""
Budget Execution Forms
Phase 2B: Budget Execution (Parliament Bill No. 325 Section 78)

Django forms for allotment release, obligation creation, and disbursement recording.
"""

from django import forms
from django.core.exceptions import ValidationError
from django.db.models import Sum
from decimal import Decimal

from .models import Allotment, Obligation, Disbursement, DisbursementLineItem
from budget_preparation.models import ProgramBudget
from monitoring.models import MonitoringEntry


class AllotmentReleaseForm(forms.ModelForm):
    """
    Form for releasing quarterly budget allotments.

    Validates:
    - Amount does not exceed program budget balance
    - Quarter not already released for this program budget
    """

    class Meta:
        model = Allotment
        fields = [
            'program_budget',
            'quarter',
            'amount',
            'release_date',
            'status',
            'allotment_order_number',
            'notes'
        ]
        widgets = {
            'program_budget': forms.Select(attrs={
                'class': 'block w-full py-3 px-4 text-base rounded-xl border border-gray-200 shadow-sm focus:ring-emerald-500 focus:border-emerald-500 min-h-[48px]',
                'required': True,
            }),
            'quarter': forms.Select(attrs={
                'class': 'block w-full py-3 px-4 text-base rounded-xl border border-gray-200 shadow-sm focus:ring-emerald-500 focus:border-emerald-500 min-h-[48px]',
                'required': True,
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'w-full pl-8 pr-4 py-3 text-base rounded-xl border border-gray-200 shadow-sm focus:ring-emerald-500 focus:border-emerald-500 min-h-[48px]',
                'step': '0.01',
                'min': '0.01',
                'placeholder': '0.00',
                'required': True,
            }),
            'release_date': forms.DateInput(attrs={
                'class': 'w-full px-4 py-3 text-base rounded-xl border border-gray-200 shadow-sm focus:ring-emerald-500 focus:border-emerald-500 min-h-[48px]',
                'type': 'date',
                'required': True,
            }),
            'status': forms.Select(attrs={
                'class': 'block w-full py-3 px-4 text-base rounded-xl border border-gray-200 shadow-sm focus:ring-emerald-500 focus:border-emerald-500 min-h-[48px]',
            }),
            'allotment_order_number': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 text-base rounded-xl border border-gray-200 shadow-sm focus:ring-emerald-500 focus:border-emerald-500 min-h-[48px]',
                'placeholder': 'e.g., AO-2025-001',
            }),
            'notes': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 text-base rounded-xl border border-gray-200 shadow-sm focus:ring-emerald-500 focus:border-emerald-500 transition-all duration-200 resize-vertical',
                'rows': 3,
                'placeholder': 'Optional notes or special instructions...',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Filter program budgets to only show approved ones
        self.fields['program_budget'].queryset = ProgramBudget.objects.filter(
            approved_amount__isnull=False
        ).select_related('program', 'budget_proposal').order_by('-budget_proposal__fiscal_year')

        # Set default status to 'released'
        if not self.instance.pk:
            self.fields['status'].initial = 'released'

    def clean(self):
        """
        Validate allotment doesn't exceed available program budget balance.
        """
        cleaned_data = super().clean()
        program_budget = cleaned_data.get('program_budget')
        quarter = cleaned_data.get('quarter')
        amount = cleaned_data.get('amount')

        if not all([program_budget, quarter, amount]):
            return cleaned_data

        # Check if allotment already exists for this quarter
        existing = Allotment.objects.filter(
            program_budget=program_budget,
            quarter=quarter
        )

        # Exclude current instance if editing
        if self.instance.pk:
            existing = existing.exclude(pk=self.instance.pk)

        if existing.exists():
            raise ValidationError(
                f'Allotment for {program_budget.program.name} Q{quarter} already exists. '
                'Cannot create duplicate allotment.'
            )

        # Calculate total allotted
        total_allotted = Allotment.objects.filter(
            program_budget=program_budget
        ).exclude(
            pk=self.instance.pk if self.instance.pk else None
        ).aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0.00')

        total_allotted += amount

        # Check constraint
        if total_allotted > program_budget.approved_amount:
            remaining = program_budget.approved_amount - (total_allotted - amount)
            raise ValidationError(
                f'Total allotments (₱{total_allotted:,.2f}) would exceed '
                f'approved budget (₱{program_budget.approved_amount:,.2f}). '
                f'Remaining balance: ₱{remaining:,.2f}'
            )

        return cleaned_data


class ObligationForm(forms.ModelForm):
    """
    Form for creating budget obligations.

    Validates:
    - Amount does not exceed allotment available balance
    - Allotment is in released or partially utilized status
    """

    class Meta:
        model = Obligation
        fields = [
            'allotment',
            'description',
            'amount',
            'obligated_date',
            'document_ref',
            'monitoring_entry',
            'status',
            'notes'
        ]
        widgets = {
            'allotment': forms.Select(attrs={
                'class': 'block w-full py-3 px-4 text-base rounded-xl border border-gray-200 shadow-sm focus:ring-emerald-500 focus:border-emerald-500 min-h-[48px]',
                'required': True,
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 text-base rounded-xl border border-gray-200 shadow-sm focus:ring-emerald-500 focus:border-emerald-500 transition-all duration-200 resize-vertical',
                'rows': 3,
                'placeholder': 'Describe the goods, services, or work to be procured...',
                'required': True,
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'w-full pl-8 pr-4 py-3 text-base rounded-xl border border-gray-200 shadow-sm focus:ring-emerald-500 focus:border-emerald-500 min-h-[48px]',
                'step': '0.01',
                'min': '0.01',
                'placeholder': '0.00',
                'required': True,
            }),
            'obligated_date': forms.DateInput(attrs={
                'class': 'w-full px-4 py-3 text-base rounded-xl border border-gray-200 shadow-sm focus:ring-emerald-500 focus:border-emerald-500 min-h-[48px]',
                'type': 'date',
                'required': True,
            }),
            'document_ref': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 text-base rounded-xl border border-gray-200 shadow-sm focus:ring-emerald-500 focus:border-emerald-500 min-h-[48px]',
                'placeholder': 'e.g., PO-2025-001',
                'required': True,
            }),
            'monitoring_entry': forms.Select(attrs={
                'class': 'block w-full py-3 px-4 text-base rounded-xl border border-gray-200 shadow-sm focus:ring-emerald-500 focus:border-emerald-500 min-h-[48px]',
            }),
            'status': forms.Select(attrs={
                'class': 'block w-full py-3 px-4 text-base rounded-xl border border-gray-200 shadow-sm focus:ring-emerald-500 focus:border-emerald-500 min-h-[48px]',
            }),
            'notes': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 text-base rounded-xl border border-gray-200 shadow-sm focus:ring-emerald-500 focus:border-emerald-500 transition-all duration-200 resize-vertical',
                'rows': 3,
                'placeholder': 'Optional notes or remarks...',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Filter allotments to only show released/partially utilized ones
        self.fields['allotment'].queryset = Allotment.objects.filter(
            status__in=['released', 'partially_utilized']
        ).select_related(
            'program_budget__program',
            'program_budget__budget_proposal'
        ).order_by('-release_date')

        # Filter monitoring entries to only show active ones
        self.fields['monitoring_entry'].queryset = MonitoringEntry.objects.filter(
            status__in=['planned', 'in_progress']
        ).order_by('-created_at')
        self.fields['monitoring_entry'].required = False

        # Set default status to 'committed'
        if not self.instance.pk:
            self.fields['status'].initial = 'committed'

    def clean(self):
        """
        Validate obligation doesn't exceed available allotment balance.
        """
        cleaned_data = super().clean()
        allotment = cleaned_data.get('allotment')
        amount = cleaned_data.get('amount')

        if not all([allotment, amount]):
            return cleaned_data

        # Calculate total obligated
        total_obligated = Obligation.objects.filter(
            allotment=allotment
        ).exclude(
            pk=self.instance.pk if self.instance.pk else None
        ).aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0.00')

        total_obligated += amount

        # Check constraint
        if total_obligated > allotment.amount:
            remaining = allotment.amount - (total_obligated - amount)
            raise ValidationError(
                f'Total obligations (₱{total_obligated:,.2f}) would exceed '
                f'allotment (₱{allotment.amount:,.2f}). '
                f'Remaining balance: ₱{remaining:,.2f}'
            )

        return cleaned_data


class DisbursementForm(forms.ModelForm):
    """
    Form for recording budget disbursements.

    Validates:
    - Amount does not exceed obligation available balance
    - Obligation is in committed or partially disbursed status
    """

    PAYMENT_METHOD_CHOICES = [
        ('check', 'Check'),
        ('bank_transfer', 'Bank Transfer'),
        ('cash', 'Cash'),
        ('gcash', 'GCash'),
        ('other', 'Other'),
    ]

    class Meta:
        model = Disbursement
        fields = [
            'obligation',
            'amount',
            'disbursed_date',
            'payee',
            'payment_method',
            'check_number',
            'voucher_number',
            'notes'
        ]
        widgets = {
            'obligation': forms.Select(attrs={
                'class': 'block w-full py-3 px-4 text-base rounded-xl border border-gray-200 shadow-sm focus:ring-emerald-500 focus:border-emerald-500 min-h-[48px]',
                'required': True,
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'w-full pl-8 pr-4 py-3 text-base rounded-xl border border-gray-200 shadow-sm focus:ring-emerald-500 focus:border-emerald-500 min-h-[48px]',
                'step': '0.01',
                'min': '0.01',
                'placeholder': '0.00',
                'required': True,
            }),
            'disbursed_date': forms.DateInput(attrs={
                'class': 'w-full px-4 py-3 text-base rounded-xl border border-gray-200 shadow-sm focus:ring-emerald-500 focus:border-emerald-500 min-h-[48px]',
                'type': 'date',
                'required': True,
            }),
            'payee': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 text-base rounded-xl border border-gray-200 shadow-sm focus:ring-emerald-500 focus:border-emerald-500 min-h-[48px]',
                'placeholder': 'Name of payee or recipient',
                'required': True,
            }),
            'payment_method': forms.Select(attrs={
                'class': 'block w-full py-3 px-4 text-base rounded-xl border border-gray-200 shadow-sm focus:ring-emerald-500 focus:border-emerald-500 min-h-[48px]',
                'required': True,
            }),
            'check_number': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 text-base rounded-xl border border-gray-200 shadow-sm focus:ring-emerald-500 focus:border-emerald-500 min-h-[48px]',
                'placeholder': 'e.g., CHK-2025-001',
            }),
            'voucher_number': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 text-base rounded-xl border border-gray-200 shadow-sm focus:ring-emerald-500 focus:border-emerald-500 min-h-[48px]',
                'placeholder': 'e.g., DV-2025-001',
            }),
            'notes': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 text-base rounded-xl border border-gray-200 shadow-sm focus:ring-emerald-500 focus:border-emerald-500 transition-all duration-200 resize-vertical',
                'rows': 3,
                'placeholder': 'Optional notes or payment instructions...',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Filter obligations to only show committed/partially disbursed ones
        self.fields['obligation'].queryset = Obligation.objects.filter(
            status__in=['committed', 'partially_disbursed']
        ).select_related(
            'allotment__program_budget__program'
        ).order_by('-obligated_date')

        # Override payment_method choices
        self.fields['payment_method'].widget.choices = [
            ('', 'Select method...'),
        ] + list(self.PAYMENT_METHOD_CHOICES)

    def clean(self):
        """
        Validate disbursement doesn't exceed available obligation balance.
        """
        cleaned_data = super().clean()
        obligation = cleaned_data.get('obligation')
        amount = cleaned_data.get('amount')

        if not all([obligation, amount]):
            return cleaned_data

        # Calculate total disbursed
        total_disbursed = Disbursement.objects.filter(
            obligation=obligation
        ).exclude(
            pk=self.instance.pk if self.instance.pk else None
        ).aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0.00')

        total_disbursed += amount

        # Check constraint
        if total_disbursed > obligation.amount:
            remaining = obligation.amount - (total_disbursed - amount)
            raise ValidationError(
                f'Total disbursements (₱{total_disbursed:,.2f}) would exceed '
                f'obligation (₱{obligation.amount:,.2f}). '
                f'Remaining balance: ₱{remaining:,.2f}'
            )

        return cleaned_data


class DisbursementLineItemForm(forms.ModelForm):
    """
    Form for individual disbursement line items.
    """

    class Meta:
        model = DisbursementLineItem
        fields = [
            'description',
            'amount',
            'cost_center',
            'monitoring_entry',
            'notes'
        ]
        widgets = {
            'description': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 text-base rounded-xl border border-gray-200 shadow-sm focus:ring-emerald-500 focus:border-emerald-500 min-h-[48px]',
                'placeholder': 'Item description',
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'w-full pl-8 pr-4 py-3 text-base rounded-xl border border-gray-200 shadow-sm focus:ring-emerald-500 focus:border-emerald-500 min-h-[48px]',
                'step': '0.01',
                'min': '0.01',
                'placeholder': '0.00',
            }),
            'cost_center': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 text-base rounded-xl border border-gray-200 shadow-sm focus:ring-emerald-500 focus:border-emerald-500 min-h-[48px]',
                'placeholder': 'Optional cost center code',
            }),
            'monitoring_entry': forms.Select(attrs={
                'class': 'block w-full py-3 px-4 text-base rounded-xl border border-gray-200 shadow-sm focus:ring-emerald-500 focus:border-emerald-500 min-h-[48px]',
            }),
            'notes': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 text-base rounded-xl border border-gray-200 shadow-sm focus:ring-emerald-500 focus:border-emerald-500 transition-all duration-200 resize-vertical',
                'rows': 2,
            }),
        }


# Formset for disbursement line items
DisbursementLineItemFormSet = forms.inlineformset_factory(
    Disbursement,
    DisbursementLineItem,
    form=DisbursementLineItemForm,
    extra=3,
    can_delete=True,
    min_num=0,
    validate_min=False,
)

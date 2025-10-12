"""
Budget Execution Admin Interfaces
Compliance: Parliament Bill No. 325 Section 78

Admin interfaces for managing allotments, obligations, and disbursements.
All financial operations are audited via AuditMiddleware.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Sum
from decimal import Decimal

from .models import Allotment, Obligation, Disbursement, DisbursementLineItem


# ============================================================================
# INLINE ADMINS
# ============================================================================

class ObligationInline(admin.TabularInline):
    """Inline for managing obligations under an allotment."""
    model = Obligation
    extra = 0
    fields = ['description', 'amount', 'obligated_date', 'document_ref', 'status']
    readonly_fields = ['created_at', 'created_by']
    can_delete = False  # Prevent accidental deletion


class DisbursementInline(admin.TabularInline):
    """Inline for managing disbursements under an obligation."""
    model = Disbursement
    extra = 0
    fields = ['payee', 'amount', 'disbursed_date', 'payment_method', 'voucher_number']
    readonly_fields = ['created_at', 'created_by']
    can_delete = False


class LineItemInline(admin.TabularInline):
    """Inline for managing line items under a disbursement."""
    model = DisbursementLineItem
    extra = 0
    fields = ['description', 'amount', 'cost_center']
    can_delete = True


# ============================================================================
# MAIN ADMIN CLASSES
# ============================================================================

@admin.register(Allotment)
class AllotmentAdmin(admin.ModelAdmin):
    """Admin interface for Allotments."""

    list_display = [
        'program_budget',
        'quarter_display',
        'amount_display',
        'obligated_display',
        'balance_display',
        'utilization_display',
        'status_badge',
        'release_date',
        'created_by'
    ]
    list_filter = ['quarter', 'status', 'release_date', 'created_at']
    search_fields = [
        'program_budget__program__name',
        'allotment_order_number',
        'notes'
    ]
    readonly_fields = [
        'created_at',
        'updated_at',
        'created_by',
        'obligated_amount_display',
        'remaining_balance_display',
        'utilization_rate_display'
    ]
    fieldsets = (
        ('Allotment Information', {
            'fields': (
                'program_budget',
                'quarter',
                'amount',
                'status'
            )
        }),
        ('Release Details', {
            'fields': (
                'release_date',
                'allotment_order_number',
                'notes'
            )
        }),
        ('Financial Summary', {
            'fields': (
                'obligated_amount_display',
                'remaining_balance_display',
                'utilization_rate_display'
            ),
            'classes': ('collapse',)
        }),
        ('Audit Trail', {
            'fields': (
                'created_by',
                'created_at',
                'updated_at'
            ),
            'classes': ('collapse',)
        }),
    )
    inlines = [ObligationInline]

    def save_model(self, request, obj, form, change):
        """Auto-set created_by on new allotments."""
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    # Display methods
    def quarter_display(self, obj):
        return f"Q{obj.quarter}"
    quarter_display.short_description = "Quarter"

    def amount_display(self, obj):
        return f"P{obj.amount:,.2f}"
    amount_display.short_description = "Allotment Amount"

    def obligated_display(self, obj):
        obligated = obj.get_obligated_amount()
        return f"P{obligated:,.2f}"
    obligated_display.short_description = "Obligated"

    def balance_display(self, obj):
        balance = obj.get_remaining_balance()
        color = 'green' if balance > 0 else 'red'
        return format_html(
            '<span style="color: {};">P{:,.2f}</span>',
            color,
            balance
        )
    balance_display.short_description = "Balance"

    def utilization_display(self, obj):
        rate = obj.get_utilization_rate()
        color = 'green' if rate < 80 else 'orange' if rate < 100 else 'red'
        return format_html(
            '<span style="color: {};">{:.1f}%</span>',
            color,
            rate
        )
    utilization_display.short_description = "Utilization"

    def status_badge(self, obj):
        colors = {
            'pending': 'gray',
            'released': 'blue',
            'partially_utilized': 'orange',
            'fully_utilized': 'green',
            'cancelled': 'red'
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            colors.get(obj.status, 'gray'),
            obj.get_status_display()
        )
    status_badge.short_description = "Status"

    # Readonly display methods
    def obligated_amount_display(self, obj):
        return f"P{obj.get_obligated_amount():,.2f}"
    obligated_amount_display.short_description = "Total Obligated"

    def remaining_balance_display(self, obj):
        return f"P{obj.get_remaining_balance():,.2f}"
    remaining_balance_display.short_description = "Remaining Balance"

    def utilization_rate_display(self, obj):
        return f"{obj.get_utilization_rate():.2f}%"
    utilization_rate_display.short_description = "Utilization Rate"


@admin.register(Obligation)
class ObligationAdmin(admin.ModelAdmin):
    """Admin interface for Obligations."""

    list_display = [
        'description',
        'allotment_link',
        'amount_display',
        'disbursed_display',
        'balance_display',
        'status_badge',
        'obligated_date',
        'document_ref',
        'created_by'
    ]
    list_filter = ['status', 'obligated_date', 'created_at']
    search_fields = [
        'description',
        'document_ref',
        'allotment__program_budget__program__name',
        'notes'
    ]
    readonly_fields = [
        'created_at',
        'updated_at',
        'created_by',
        'disbursed_amount_display',
        'remaining_balance_display'
    ]
    fieldsets = (
        ('Obligation Information', {
            'fields': (
                'allotment',
                'description',
                'amount',
                'obligated_date',
                'document_ref',
                'status'
            )
        }),
        ('M&E Integration', {
            'fields': ('monitoring_entry',),
            'classes': ('collapse',)
        }),
        ('Financial Summary', {
            'fields': (
                'disbursed_amount_display',
                'remaining_balance_display'
            ),
            'classes': ('collapse',)
        }),
        ('Additional Details', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('Audit Trail', {
            'fields': (
                'created_by',
                'created_at',
                'updated_at'
            ),
            'classes': ('collapse',)
        }),
    )
    inlines = [DisbursementInline]

    def save_model(self, request, obj, form, change):
        """Auto-set created_by on new obligations."""
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    # Display methods
    def allotment_link(self, obj):
        url = reverse('admin:budget_execution_allotment_change', args=[obj.allotment.pk])
        return format_html('<a href="{}">{}</a>', url, obj.allotment)
    allotment_link.short_description = "Allotment"

    def amount_display(self, obj):
        return f"P{obj.amount:,.2f}"
    amount_display.short_description = "Obligation Amount"

    def disbursed_display(self, obj):
        disbursed = obj.get_disbursed_amount()
        return f"P{disbursed:,.2f}"
    disbursed_display.short_description = "Disbursed"

    def balance_display(self, obj):
        balance = obj.get_remaining_balance()
        color = 'green' if balance > 0 else 'red'
        return format_html(
            '<span style="color: {};">P{:,.2f}</span>',
            color,
            balance
        )
    balance_display.short_description = "Balance"

    def status_badge(self, obj):
        colors = {
            'pending': 'gray',
            'committed': 'blue',
            'partially_disbursed': 'orange',
            'fully_disbursed': 'green',
            'cancelled': 'red'
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            colors.get(obj.status, 'gray'),
            obj.get_status_display()
        )
    status_badge.short_description = "Status"

    def disbursed_amount_display(self, obj):
        return f"P{obj.get_disbursed_amount():,.2f}"
    disbursed_amount_display.short_description = "Total Disbursed"

    def remaining_balance_display(self, obj):
        return f"P{obj.get_remaining_balance():,.2f}"
    remaining_balance_display.short_description = "Remaining Balance"


@admin.register(Disbursement)
class DisbursementAdmin(admin.ModelAdmin):
    """Admin interface for Disbursements."""

    list_display = [
        'payee',
        'obligation_link',
        'amount_display',
        'disbursed_date',
        'payment_method',
        'voucher_number',
        'check_number',
        'created_by'
    ]
    list_filter = ['payment_method', 'disbursed_date', 'created_at']
    search_fields = [
        'payee',
        'voucher_number',
        'check_number',
        'obligation__description',
        'notes'
    ]
    readonly_fields = [
        'created_at',
        'updated_at',
        'created_by'
    ]
    fieldsets = (
        ('Disbursement Information', {
            'fields': (
                'obligation',
                'amount',
                'disbursed_date',
                'payee'
            )
        }),
        ('Payment Details', {
            'fields': (
                'payment_method',
                'voucher_number',
                'check_number'
            )
        }),
        ('Additional Details', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('Audit Trail', {
            'fields': (
                'created_by',
                'created_at',
                'updated_at'
            ),
            'classes': ('collapse',)
        }),
    )
    inlines = [LineItemInline]

    def save_model(self, request, obj, form, change):
        """Auto-set created_by on new disbursements."""
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    # Display methods
    def obligation_link(self, obj):
        url = reverse('admin:budget_execution_obligation_change', args=[obj.obligation.pk])
        return format_html('<a href="{}">{}</a>', url, obj.obligation)
    obligation_link.short_description = "Obligation"

    def amount_display(self, obj):
        return f"P{obj.amount:,.2f}"
    amount_display.short_description = "Disbursement Amount"


@admin.register(DisbursementLineItem)
class DisbursementLineItemAdmin(admin.ModelAdmin):
    """Admin interface for Disbursement Line Items."""

    list_display = [
        'description',
        'disbursement_link',
        'amount_display',
        'cost_center',
        'created_at'
    ]
    list_filter = ['cost_center', 'created_at']
    search_fields = [
        'description',
        'cost_center',
        'disbursement__payee',
        'notes'
    ]
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Line Item Information', {
            'fields': (
                'disbursement',
                'description',
                'amount',
                'cost_center'
            )
        }),
        ('M&E Integration', {
            'fields': ('monitoring_entry',),
            'classes': ('collapse',)
        }),
        ('Additional Details', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': (
                'created_at',
                'updated_at'
            ),
            'classes': ('collapse',)
        }),
    )

    # Display methods
    def disbursement_link(self, obj):
        url = reverse('admin:budget_execution_disbursement_change', args=[obj.disbursement.pk])
        return format_html('<a href="{}">{}</a>', url, obj.disbursement)
    disbursement_link.short_description = "Disbursement"

    def amount_display(self, obj):
        return f"P{obj.amount:,.2f}"
    amount_display.short_description = "Amount"

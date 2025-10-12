"""Budget Preparation Admin Interface"""

from django.contrib import admin
from django.utils.html import format_html
from .models import (
    BudgetProposal,
    ProgramBudget,
    BudgetJustification,
    BudgetLineItem
)


class BudgetLineItemInline(admin.TabularInline):
    """Inline editing for budget line items"""
    model = BudgetLineItem
    extra = 1
    fields = ['category', 'description', 'unit_cost', 'quantity', 'total_cost', 'notes']
    readonly_fields = ['total_cost']


class BudgetJustificationInline(admin.TabularInline):
    """Inline editing for budget justifications"""
    model = BudgetJustification
    extra = 0
    fields = [
        'needs_assessment_reference',
        'monitoring_entry_reference',
        'rationale',
        'alignment_with_priorities',
        'expected_impact'
    ]
    raw_id_fields = ['needs_assessment_reference', 'monitoring_entry_reference']


class ProgramBudgetInline(admin.TabularInline):
    """Inline editing for program budgets"""
    model = ProgramBudget
    extra = 1
    fields = ['program', 'allocated_amount', 'priority_level', 'justification']
    raw_id_fields = ['program']


@admin.register(BudgetProposal)
class BudgetProposalAdmin(admin.ModelAdmin):
    """Admin interface for Budget Proposals"""

    list_display = [
        'title',
        'organization',
        'fiscal_year',
        'formatted_total',
        'status_badge',
        'submitted_at',
    ]

    list_filter = [
        'status',
        'fiscal_year',
        'organization',
        'submitted_at',
    ]

    search_fields = [
        'title',
        'description',
        'organization__name',
    ]

    readonly_fields = [
        'total_proposed_budget',
        'submitted_at',
        'reviewed_at',
        'created_at',
        'updated_at',
    ]

    fieldsets = (
        ('Basic Information', {
            'fields': (
                'organization',
                'fiscal_year',
                'title',
                'description',
            )
        }),
        ('Budget Summary', {
            'fields': (
                'total_proposed_budget',
                'status',
            )
        }),
        ('Submission Details', {
            'fields': (
                'submitted_by',
                'submitted_at',
            )
        }),
        ('Review Details', {
            'fields': (
                'reviewed_by',
                'reviewed_at',
                'approval_notes',
            )
        }),
        ('Audit Information', {
            'fields': (
                'created_at',
                'updated_at',
            ),
            'classes': ('collapse',)
        }),
    )

    inlines = [ProgramBudgetInline]

    def formatted_total(self, obj):
        """Display formatted budget total."""
        return f"₱{obj.total_proposed_budget:,.2f}"
    formatted_total.short_description = "Total Budget"

    def status_badge(self, obj):
        """Display status as colored badge."""
        colors = {
            'draft': 'gray',
            'submitted': 'blue',
            'under_review': 'orange',
            'approved': 'green',
            'rejected': 'red',
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = "Status"


@admin.register(ProgramBudget)
class ProgramBudgetAdmin(admin.ModelAdmin):
    """Admin interface for Program Budgets"""

    list_display = [
        'program',
        'budget_proposal',
        'formatted_amount',
        'priority_level',
        'created_at',
    ]

    list_filter = [
        'priority_level',
        'budget_proposal__fiscal_year',
        'budget_proposal__organization',
    ]

    search_fields = [
        'program__title',
        'budget_proposal__title',
        'justification',
    ]

    raw_id_fields = ['budget_proposal', 'program']

    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Program Information', {
            'fields': (
                'budget_proposal',
                'program',
            )
        }),
        ('Budget Details', {
            'fields': (
                'allocated_amount',
                'priority_level',
                'justification',
                'expected_outputs',
            )
        }),
        ('Audit Information', {
            'fields': (
                'created_at',
                'updated_at',
            ),
            'classes': ('collapse',)
        }),
    )

    inlines = [BudgetLineItemInline, BudgetJustificationInline]

    def formatted_amount(self, obj):
        """Display formatted budget amount."""
        return f"₱{obj.allocated_amount:,.2f}"
    formatted_amount.short_description = "Allocated Budget"


@admin.register(BudgetJustification)
class BudgetJustificationAdmin(admin.ModelAdmin):
    """Admin interface for Budget Justifications"""

    list_display = [
        'program_budget',
        'has_needs_assessment',
        'has_monitoring_entry',
        'created_at',
    ]

    list_filter = [
        'program_budget__budget_proposal__fiscal_year',
        'created_at',
    ]

    search_fields = [
        'program_budget__program__title',
        'rationale',
        'alignment_with_priorities',
    ]

    raw_id_fields = [
        'program_budget',
        'needs_assessment_reference',
        'monitoring_entry_reference',
    ]

    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Program Reference', {
            'fields': ('program_budget',)
        }),
        ('Evidence References', {
            'fields': (
                'needs_assessment_reference',
                'monitoring_entry_reference',
            )
        }),
        ('Justification Details', {
            'fields': (
                'rationale',
                'alignment_with_priorities',
                'expected_impact',
            )
        }),
        ('Audit Information', {
            'fields': (
                'created_at',
                'updated_at',
            ),
            'classes': ('collapse',)
        }),
    )

    def has_needs_assessment(self, obj):
        """Check if linked to needs assessment."""
        return '✓' if obj.needs_assessment_reference else '✗'
    has_needs_assessment.short_description = "MANA Link"

    def has_monitoring_entry(self, obj):
        """Check if linked to M&E entry."""
        return '✓' if obj.monitoring_entry_reference else '✗'
    has_monitoring_entry.short_description = "M&E Link"


@admin.register(BudgetLineItem)
class BudgetLineItemAdmin(admin.ModelAdmin):
    """Admin interface for Budget Line Items"""

    list_display = [
        'description',
        'category',
        'program_budget',
        'unit_cost',
        'quantity',
        'formatted_total',
        'created_at',
    ]

    list_filter = [
        'category',
        'program_budget__budget_proposal__fiscal_year',
    ]

    search_fields = [
        'description',
        'program_budget__program__title',
        'notes',
    ]

    raw_id_fields = ['program_budget']

    readonly_fields = ['total_cost', 'created_at', 'updated_at']

    fieldsets = (
        ('Line Item Details', {
            'fields': (
                'program_budget',
                'category',
                'description',
            )
        }),
        ('Cost Breakdown', {
            'fields': (
                'unit_cost',
                'quantity',
                'total_cost',
                'notes',
            )
        }),
        ('Audit Information', {
            'fields': (
                'created_at',
                'updated_at',
            ),
            'classes': ('collapse',)
        }),
    )

    def formatted_total(self, obj):
        """Display formatted total cost."""
        return f"₱{obj.total_cost:,.2f}"
    formatted_total.short_description = "Total Cost"

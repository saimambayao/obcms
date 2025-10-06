"""Admin registrations for Monitoring & Evaluation models."""

from django.contrib import admin
from django.utils.html import format_html

from common.models import WorkItem

from .models import (
    MonitoringEntry,
    MonitoringEntryFunding,
    MonitoringEntryWorkflowStage,
    MonitoringEntryWorkflowDocument,
    MonitoringUpdate,
    StrategicGoal,
    AnnualPlanningCycle,
    BudgetScenario,
    ScenarioAllocation,
    OutcomeIndicator,
    CeilingManagement,
)


class MonitoringUpdateInline(admin.TabularInline):
    """Inline updates to provide quick history in the admin panel."""

    model = MonitoringUpdate
    extra = 0
    fields = (
        "created_at",
        "update_type",
        "status",
        "request_status",
        "progress",
        "follow_up_date",
        "created_by",
    )
    readonly_fields = ("created_at",)


class MonitoringEntryFundingInline(admin.TabularInline):
    """Inline funding flow management for quick adjustments."""

    model = MonitoringEntryFunding
    extra = 0
    fields = (
        "tranche_type",
        "amount",
        "funding_source",
        "funding_source_other",
        "scheduled_date",
        "remarks",
    )


class MonitoringEntryWorkflowStageInline(admin.TabularInline):
    """Inline workflow stage tracking for planning milestones."""

    model = MonitoringEntryWorkflowStage
    extra = 0
    fields = (
        "stage",
        "status",
        "owner_team",
        "owner_organization",
        "due_date",
        "completed_at",
        "notes",
    )


class MonitoringEntryWorkflowDocumentInline(admin.TabularInline):
    """Inline document uploads for workflow stages."""

    model = MonitoringEntryWorkflowDocument
    extra = 0
    fields = (
        "title",
        "document_type",
        "file",
        "description",
        "uploaded_by",
        "created_at",
    )
    readonly_fields = ("created_at", "uploaded_by")

    def save_model(self, request, obj, form, change):
        if not obj.uploaded_by:
            obj.uploaded_by = request.user
        super().save_model(request, obj, form, change)


# ============================================================================
# DEPRECATED: MonitoringEntryStaffTaskInline
# ============================================================================
# This inline has been removed as StaffTask has been replaced by WorkItem.
# Monitoring tasks are now managed through the WorkItem system.
# See: docs/refactor/WORKITEM_MIGRATION_COMPLETE.md
# ============================================================================

# class MonitoringEntryStaffTaskInline(admin.TabularInline):
#     """Inline view of monitoring staff tasks - DEPRECATED."""
#     model = WorkItem
#     # ... (removed for now, will be reimplemented for WorkItem)


@admin.register(MonitoringEntry)
class MonitoringEntryAdmin(admin.ModelAdmin):
    """Admin configuration for monitoring entries."""

    list_display = (
        "title",
        "category",
        "status",
        "request_status",
        "progress",
        "priority",
        "plan_year",
        "funding_source",
        "appropriation_class",
        "lead_organization",
        "submitted_by_community",
        "cost_per_beneficiary_display",
        "updated_at",
    )
    list_filter = (
        "category",
        "status",
        "request_status",
        "priority",
        "plan_year",
        "fiscal_year",
        "sector",
        "appropriation_class",
        "funding_source",
        "cost_effectiveness_rating",
        "compliance_gad",
        "compliance_ccet",
        "supports_peace_agenda",
        "lead_organization",
        "submitted_to_organization",
        "communities",
    )
    search_fields = (
        "title",
        "summary",
        "oobc_unit",
        "program_code",
        "plan_reference",
        "support_required",
    )
    autocomplete_fields = (
        "lead_organization",
        "supporting_organizations",
        "submitted_by_community",
        "communities",
        "submitted_to_organization",
        "related_assessment",
        # "related_event",  # REMOVED - use WorkItem instead
        "related_policy",
        "needs_addressed",
        "implementing_policies",
        "standard_outcome_indicators",
    )
    filter_horizontal = (
        "supporting_organizations",
        "communities",
        "needs_addressed",
        "implementing_policies",
        "standard_outcome_indicators",
    )
    inlines = [
        MonitoringEntryFundingInline,
        MonitoringEntryWorkflowStageInline,
        # MonitoringEntryStaffTaskInline,  # DEPRECATED: Replaced by WorkItem
        MonitoringUpdateInline,
    ]
    date_hierarchy = "created_at"

    fieldsets = (
        (
            "Basic Information",
            {
                "fields": (
                    "title",
                    "category",
                    "summary",
                    ("status", "request_status", "priority"),
                    "progress",
                )
            },
        ),
        (
            "Organizations & Communities",
            {
                "fields": (
                    "lead_organization",
                    "supporting_organizations",
                    "implementing_moa",
                    "oobc_unit",
                    "submitted_by_community",
                    "communities",
                    "submitted_to_organization",
                )
            },
        ),
        (
            "Evidence-Based Budgeting (Phase 1)",
            {
                "fields": (
                    "needs_addressed",
                    "implementing_policies",
                    "related_policy",
                ),
                "description": "Link this PPA to community needs and policy recommendations",
            },
        ),
        (
            "Planning & Budget",
            {
                "fields": (
                    ("plan_year", "fiscal_year"),
                    "sector",
                    ("appropriation_class", "funding_source"),
                    "funding_source_other",
                    "program_code",
                    "plan_reference",
                    "goal_alignment",
                    "moral_governance_pillar",
                )
            },
        ),
        (
            "Budget Details",
            {
                "fields": (
                    ("budget_ceiling", "budget_allocation", "budget_currency"),
                    "budget_obc_allocation",
                    ("total_slots", "obc_slots"),
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "Compliance Tags",
            {
                "fields": (
                    "compliance_gad",
                    "compliance_ccet",
                    "benefits_indigenous_peoples",
                    "supports_peace_agenda",
                    "supports_sdg",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "Timeline",
            {
                "fields": (
                    ("start_date", "target_end_date", "actual_end_date"),
                    "next_milestone_date",
                    "milestone_dates",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "Coverage",
            {
                "fields": (
                    "coverage_region",
                    "coverage_province",
                    "coverage_municipality",
                    "coverage_barangay",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "Related Activities",
            {
                "fields": (
                    "related_assessment",
                    "related_event",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "Progress & Follow-up",
            {
                "fields": (
                    "standard_outcome_indicators",
                    "outcome_framework",
                    "outcome_indicators",
                    "accomplishments",
                    "challenges",
                    "support_required",
                    "follow_up_actions",
                    "obcs_benefited",
                    "last_status_update",
                    ("cost_per_beneficiary", "cost_effectiveness_rating"),
                ),
                "classes": ("collapse",),
            },
        ),
    )

    def cost_per_beneficiary_display(self, obj):
        """Formatted cost per beneficiary for admin listing."""

        if obj.cost_per_beneficiary:
            return format_html(
                '<span class="text-gray-700">₱{:,.2f}</span>',
                obj.cost_per_beneficiary,
            )
        return "—"

    cost_per_beneficiary_display.short_description = "Cost/Person"


@admin.register(MonitoringUpdate)
class MonitoringUpdateAdmin(admin.ModelAdmin):
    """Admin configuration for monitoring updates."""

    list_display = (
        "entry",
        "update_type",
        "status",
        "request_status",
        "progress",
        "follow_up_date",
        "created_by",
        "created_at",
    )
    list_filter = (
        "update_type",
        "status",
        "request_status",
        "created_at",
    )
    search_fields = ("entry__title", "notes", "next_steps")
    autocomplete_fields = ("entry",)
    date_hierarchy = "created_at"


@admin.register(MonitoringEntryFunding)
class MonitoringEntryFundingAdmin(admin.ModelAdmin):
    """Admin configuration for detailed funding flows."""

    list_display = (
        "entry",
        "tranche_type",
        "amount",
        "funding_source",
        "scheduled_date",
        "updated_at",
    )
    list_filter = (
        "tranche_type",
        "funding_source",
        "scheduled_date",
    )
    search_fields = (
        "entry__title",
        "remarks",
    )
    autocomplete_fields = ("entry",)
    date_hierarchy = "scheduled_date"


@admin.register(MonitoringEntryWorkflowStage)
class MonitoringEntryWorkflowStageAdmin(admin.ModelAdmin):
    """Admin configuration for workflow stage tracking."""

    list_display = (
        "entry",
        "stage",
        "status",
        "owner_team",
        "owner_organization",
        "due_date",
        "completed_at",
        "updated_at",
    )
    list_filter = (
        "stage",
        "status",
        "owner_team",
        "owner_organization",
    )
    search_fields = (
        "entry__title",
        "notes",
    )
    autocomplete_fields = (
        "entry",
        "owner_team",
        "owner_organization",
    )
    inlines = [MonitoringEntryWorkflowDocumentInline]
    date_hierarchy = "due_date"


@admin.register(MonitoringEntryWorkflowDocument)
class MonitoringEntryWorkflowDocumentAdmin(admin.ModelAdmin):
    """Admin configuration for workflow documents."""

    list_display = (
        "title",
        "workflow_stage",
        "document_type",
        "file_size",
        "uploaded_by",
        "created_at",
    )
    list_filter = (
        "document_type",
        "created_at",
    )
    search_fields = (
        "title",
        "description",
        "workflow_stage__entry__title",
    )
    autocomplete_fields = ("workflow_stage",)
    readonly_fields = ("file_size", "uploaded_by", "created_at", "updated_at")
    date_hierarchy = "created_at"

    def save_model(self, request, obj, form, change):
        if not obj.uploaded_by:
            obj.uploaded_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(OutcomeIndicator)
class OutcomeIndicatorAdmin(admin.ModelAdmin):
    """Admin interface for reusable outcome indicators."""

    list_display = (
        "indicator_name",
        "category",
        "unit_of_measure",
        "frequency",
        "is_active",
        "updated_at",
    )
    list_filter = ("category", "is_active")
    search_fields = (
        "indicator_name",
        "definition",
        "data_source",
        "measurement_method",
    )
    ordering = ("category", "indicator_name")


# Phase 5: Strategic Planning Integration - Admin Interfaces


@admin.register(StrategicGoal)
class StrategicGoalAdmin(admin.ModelAdmin):
    """Admin interface for Strategic Goals."""

    list_display = [
        "title",
        "sector_badge",
        "priority_badge",
        "timeline_display",
        "progress_bar",
        "status_badge",
        "alignment_indicators",
        "linked_ppas_count",
    ]

    list_filter = [
        "status",
        "sector",
        "priority_level",
        "aligns_with_rdp",
        "aligns_with_national_framework",
        "start_year",
        "target_year",
    ]

    search_fields = [
        "title",
        "description",
        "goal_statement",
        "rdp_reference",
    ]

    autocomplete_fields = [
        "lead_agency",
        "created_by",
    ]

    filter_horizontal = [
        "supporting_agencies",
        "linked_ppas",
        "linked_policies",
    ]

    readonly_fields = [
        "created_at",
        "updated_at",
        "duration_years",
        "is_active",
        "achievement_rate",
    ]

    fieldsets = (
        (
            "Basic Information",
            {
                "fields": (
                    "title",
                    "description",
                    "goal_statement",
                    "sector",
                    "priority_level",
                )
            },
        ),
        ("Timeline", {"fields": ("start_year", "target_year", "duration_years")}),
        (
            "Alignment",
            {
                "fields": (
                    "aligns_with_rdp",
                    "rdp_reference",
                    "aligns_with_national_framework",
                )
            },
        ),
        (
            "Targets & Indicators",
            {
                "fields": (
                    "target_outcome",
                    "baseline_value",
                    "target_value",
                    "unit_of_measure",
                    "estimated_total_budget",
                )
            },
        ),
        ("Responsibility", {"fields": ("lead_agency", "supporting_agencies")}),
        (
            "Linkages",
            {"fields": ("linked_ppas", "linked_policies"), "classes": ("collapse",)},
        ),
        (
            "Progress & Status",
            {
                "fields": (
                    "status",
                    "progress_percentage",
                    "is_active",
                    "achievement_rate",
                )
            },
        ),
        (
            "Metadata",
            {
                "fields": ("created_by", "created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )

    def sector_badge(self, obj):
        colors = {
            "education": "#3b82f6",
            "health": "#ef4444",
            "livelihood": "#10b981",
            "infrastructure": "#f59e0b",
            "governance": "#8b5cf6",
            "social_protection": "#ec4899",
            "cultural": "#14b8a6",
            "peace": "#6366f1",
            "environment": "#22c55e",
        }
        color = colors.get(obj.sector, "#6b7280")
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 4px; font-size: 11px; font-weight: 600;">{}</span>',
            color,
            obj.get_sector_display(),
        )

    sector_badge.short_description = "Sector"

    def priority_badge(self, obj):
        colors = {
            "critical": "#dc2626",
            "high": "#ea580c",
            "medium": "#ca8a04",
            "low": "#65a30d",
        }
        color = colors.get(obj.priority_level, "#6b7280")
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 4px; font-size: 11px; font-weight: 600;">{}</span>',
            color,
            obj.get_priority_level_display(),
        )

    priority_badge.short_description = "Priority"

    def timeline_display(self, obj):
        return f"{obj.start_year}–{obj.target_year} ({obj.duration_years}y)"

    timeline_display.short_description = "Timeline"

    def progress_bar(self, obj):
        color = (
            "#10b981"
            if obj.progress_percentage >= 70
            else "#f59e0b" if obj.progress_percentage >= 40 else "#ef4444"
        )
        return format_html(
            '<div style="width: 100px; background: #e5e7eb; border-radius: 4px; height: 16px;">'
            '<div style="width: {}%; background: {}; border-radius: 4px; height: 16px; '
            'display: flex; align-items: center; justify-content: center; color: white; font-size: 10px; font-weight: 600;">'
            "{}%</div></div>",
            obj.progress_percentage,
            color,
            obj.progress_percentage,
        )

    progress_bar.short_description = "Progress"

    def status_badge(self, obj):
        colors = {
            "draft": "#6b7280",
            "approved": "#3b82f6",
            "active": "#10b981",
            "achieved": "#14b8a6",
            "revised": "#f59e0b",
            "discontinued": "#ef4444",
        }
        color = colors.get(obj.status, "#6b7280")
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 4px; font-size: 11px; font-weight: 600;">{}</span>',
            color,
            obj.get_status_display(),
        )

    status_badge.short_description = "Status"

    def alignment_indicators(self, obj):
        indicators = []
        if obj.aligns_with_rdp:
            indicators.append(
                '<span style="color: #10b981;" title="Aligns with RDP">✓ RDP</span>'
            )
        if obj.aligns_with_national_framework:
            indicators.append(
                '<span style="color: #3b82f6;" title="Aligns with National Framework">✓ National</span>'
            )
        return format_html(" ".join(indicators)) if indicators else "—"

    alignment_indicators.short_description = "Alignment"

    def linked_ppas_count(self, obj):
        count = obj.linked_ppas.count()
        if count > 0:
            return format_html(
                '<span style="color: #10b981; font-weight: 600;">{} PPAs</span>', count
            )
        return format_html('<span style="color: #9ca3af;">No PPAs</span>')

    linked_ppas_count.short_description = "Linked PPAs"


@admin.register(AnnualPlanningCycle)
class AnnualPlanningCycleAdmin(admin.ModelAdmin):
    """Admin interface for Annual Planning Cycles."""

    list_display = [
        "fiscal_year_display",
        "cycle_name",
        "status_badge",
        "budget_summary",
        "utilization_bar",
        "timeline_progress",
        "strategic_goals_count",
        "ppas_count",
    ]

    list_filter = [
        "status",
        "fiscal_year",
    ]

    search_fields = [
        "cycle_name",
        "notes",
    ]

    autocomplete_fields = [
        "created_by",
    ]

    filter_horizontal = [
        "strategic_goals",
        "monitoring_entries",
        "needs_addressed",
    ]

    readonly_fields = [
        "created_at",
        "updated_at",
        "budget_utilization_rate",
        "is_current_cycle",
        "days_until_budget_submission",
    ]

    fieldsets = (
        ("Planning Cycle", {"fields": ("fiscal_year", "cycle_name", "status")}),
        (
            "Timeline",
            {
                "fields": (
                    "planning_start_date",
                    "planning_end_date",
                    "budget_submission_date",
                    "budget_approval_date",
                    "execution_start_date",
                    "execution_end_date",
                    "days_until_budget_submission",
                )
            },
        ),
        (
            "Budget",
            {
                "fields": (
                    "total_budget_envelope",
                    "allocated_budget",
                    "budget_utilization_rate",
                )
            },
        ),
        ("Strategic Alignment", {"fields": ("strategic_goals",)}),
        (
            "Implementation",
            {
                "fields": ("monitoring_entries", "needs_addressed"),
                "classes": ("collapse",),
            },
        ),
        (
            "Documentation",
            {
                "fields": (
                    "plan_document_url",
                    "budget_document_url",
                    "notes",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "Metadata",
            {
                "fields": (
                    "created_by",
                    "created_at",
                    "updated_at",
                    "is_current_cycle",
                ),
                "classes": ("collapse",),
            },
        ),
    )

    def fiscal_year_display(self, obj):
        if obj.is_current_cycle:
            return format_html(
                '<strong style="color: #10b981;">FY {} <span style="background: #10b981; '
                'color: white; padding: 2px 6px; border-radius: 3px; font-size: 10px;">CURRENT</span></strong>',
                obj.fiscal_year,
            )
        return f"FY {obj.fiscal_year}"

    fiscal_year_display.short_description = "Fiscal Year"

    def status_badge(self, obj):
        colors = {
            "planning": "#6b7280",
            "budget_preparation": "#3b82f6",
            "budget_approval": "#f59e0b",
            "execution": "#10b981",
            "monitoring": "#8b5cf6",
            "completed": "#14b8a6",
            "archived": "#9ca3af",
        }
        color = colors.get(obj.status, "#6b7280")
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 4px; font-size: 11px; font-weight: 600;">{}</span>',
            color,
            obj.get_status_display(),
        )

    status_badge.short_description = "Status"

    def budget_summary(self, obj):
        if obj.total_budget_envelope:
            return format_html(
                '<div style="font-size: 11px;">'
                "<div>Envelope: <strong>₱{:,.2f}</strong></div>"
                "<div>Allocated: <strong>₱{:,.2f}</strong></div>"
                "</div>",
                obj.total_budget_envelope,
                obj.allocated_budget,
            )
        return "—"

    budget_summary.short_description = "Budget"

    def utilization_bar(self, obj):
        rate = obj.budget_utilization_rate
        color = "#10b981" if rate >= 70 else "#f59e0b" if rate >= 40 else "#ef4444"
        return format_html(
            '<div style="width: 100px; background: #e5e7eb; border-radius: 4px; height: 16px;">'
            '<div style="width: {}%; background: {}; border-radius: 4px; height: 16px; '
            'display: flex; align-items: center; justify-content: center; color: white; font-size: 10px; font-weight: 600;">'
            "{:.0f}%</div></div>",
            min(rate, 100),
            color,
            rate,
        )

    utilization_bar.short_description = "Utilization"

    def timeline_progress(self, obj):
        from django.utils import timezone

        today = timezone.now().date()

        if today < obj.planning_start_date:
            return format_html('<span style="color: #6b7280;">Not Started</span>')
        elif today <= obj.planning_end_date:
            return format_html('<span style="color: #3b82f6;">Planning</span>')
        elif today <= obj.budget_submission_date:
            days = obj.days_until_budget_submission
            return format_html(
                '<span style="color: #f59e0b;">Budget Due: {} days</span>', days
            )
        elif today <= obj.execution_end_date:
            return format_html('<span style="color: #10b981;">Executing</span>')
        else:
            return format_html('<span style="color: #9ca3af;">Ended</span>')

    timeline_progress.short_description = "Timeline"

    def strategic_goals_count(self, obj):
        count = obj.strategic_goals.count()
        return (
            format_html(
                '<span style="color: #3b82f6; font-weight: 600;">{}</span>', count
            )
            if count > 0
            else "—"
        )

    strategic_goals_count.short_description = "Strategic Goals"

    def ppas_count(self, obj):
        count = obj.monitoring_entries.count()
        return (
            format_html(
                '<span style="color: #10b981; font-weight: 600;">{}</span>', count
            )
            if count > 0
            else "—"
        )

    ppas_count.short_description = "PPAs"


# =============================================================================
# Phase 6: Scenario Planning & Budget Optimization Admin
# =============================================================================


class ScenarioAllocationInline(admin.TabularInline):
    """Inline allocations for scenario planning."""

    model = ScenarioAllocation
    extra = 0
    fields = (
        "ppa",
        "allocated_amount",
        "priority_rank",
        "status",
        "allocation_rationale",
        "overall_score",
    )
    readonly_fields = ("overall_score",)
    autocomplete_fields = ["ppa"]


@admin.register(BudgetScenario)
class BudgetScenarioAdmin(admin.ModelAdmin):
    """Admin interface for budget scenarios."""

    list_display = [
        "scenario_name_display",
        "scenario_type_badge",
        "budget_summary",
        "utilization_bar",
        "optimization_score_display",
        "beneficiaries_display",
        "status_badge",
        "created_at",
    ]

    list_filter = [
        "status",
        "scenario_type",
        "is_baseline",
        "planning_cycle",
        "created_at",
    ]

    search_fields = [
        "name",
        "description",
        "notes",
    ]

    readonly_fields = [
        "id",
        "allocated_budget",
        "optimization_score",
        "estimated_beneficiaries",
        "estimated_needs_addressed",
        "budget_utilization_rate",
        "unallocated_budget",
        "optimization_weights_sum",
        "created_at",
        "updated_at",
    ]

    fieldsets = [
        (
            "Basic Information",
            {
                "fields": (
                    "id",
                    "name",
                    "description",
                    "scenario_type",
                    "is_baseline",
                    "planning_cycle",
                    "status",
                )
            },
        ),
        (
            "Budget",
            {
                "fields": (
                    "total_budget",
                    "allocated_budget",
                    "budget_utilization_rate",
                    "unallocated_budget",
                )
            },
        ),
        (
            "Optimization Weights",
            {
                "fields": (
                    "weight_needs_coverage",
                    "weight_equity",
                    "weight_strategic_alignment",
                    "optimization_weights_sum",
                ),
                "description": "Adjust weights for multi-objective optimization (should sum to ~1.00)",
            },
        ),
        (
            "Results & Metrics",
            {
                "fields": (
                    "optimization_score",
                    "estimated_beneficiaries",
                    "estimated_needs_addressed",
                )
            },
        ),
        (
            "Metadata",
            {
                "fields": (
                    "notes",
                    "created_by",
                    "created_at",
                    "updated_at",
                ),
                "classes": ("collapse",),
            },
        ),
    ]

    inlines = [ScenarioAllocationInline]

    def scenario_name_display(self, obj):
        """Display scenario name with baseline badge."""
        if obj.is_baseline:
            return format_html(
                '<strong style="color: #10b981;">{}</strong> '
                '<span style="background: #10b981; color: white; padding: 2px 8px; '
                'border-radius: 12px; font-size: 10px; font-weight: 600;">BASELINE</span>',
                obj.name,
            )
        return format_html("<strong>{}</strong>", obj.name)

    scenario_name_display.short_description = "Scenario"

    def scenario_type_badge(self, obj):
        """Visual badge for scenario type."""
        colors = {
            "baseline": "#10b981",
            "optimistic": "#3b82f6",
            "conservative": "#f59e0b",
            "needs_based": "#8b5cf6",
            "equity_focused": "#ec4899",
            "custom": "#6b7280",
        }
        color = colors.get(obj.scenario_type, "#6b7280")

        return format_html(
            '<span style="background: {}; color: white; padding: 4px 12px; '
            'border-radius: 16px; font-size: 11px; font-weight: 600;">{}</span>',
            color,
            obj.get_scenario_type_display(),
        )

    scenario_type_badge.short_description = "Type"

    def budget_summary(self, obj):
        """Display budget allocation summary."""
        return format_html(
            '<div style="font-size: 12px;">'
            '<div style="color: #10b981; font-weight: 600;">₱{:,.0f}</div>'
            '<div style="color: #6b7280; font-size: 10px;">of ₱{:,.0f}</div>'
            "</div>",
            obj.allocated_budget,
            obj.total_budget,
        )

    budget_summary.short_description = "Allocation"

    def utilization_bar(self, obj):
        """Visual budget utilization bar."""
        rate = float(obj.budget_utilization_rate)
        color = "#10b981" if rate >= 80 else "#3b82f6" if rate >= 50 else "#f59e0b"

        return format_html(
            '<div style="width: 120px; background: #e5e7eb; border-radius: 8px; height: 20px; position: relative;">'
            '<div style="width: {}%; background: {}; border-radius: 8px; height: 20px; '
            "display: flex; align-items: center; justify-content: center; color: white; "
            'font-size: 11px; font-weight: 700; transition: width 0.3s;">{:.1f}%</div>'
            "</div>",
            min(rate, 100),
            color,
            rate,
        )

    utilization_bar.short_description = "Utilization"

    def optimization_score_display(self, obj):
        """Display optimization score with color coding."""
        if obj.optimization_score is None:
            return format_html('<span style="color: #9ca3af;">Not optimized</span>')

        score = float(obj.optimization_score)
        if score >= 80:
            color = "#10b981"
            icon = "✅"
        elif score >= 60:
            color = "#3b82f6"
            icon = "✓"
        elif score >= 40:
            color = "#f59e0b"
            icon = "⚠️"
        else:
            color = "#ef4444"
            icon = "⚠"

        return format_html(
            '<span style="color: {}; font-weight: 700; font-size: 13px;">{} {:.1f}</span>',
            color,
            icon,
            score,
        )

    optimization_score_display.short_description = "Opt. Score"

    def beneficiaries_display(self, obj):
        """Display estimated beneficiaries."""
        if obj.estimated_beneficiaries > 0:
            return format_html(
                '<div style="font-size: 12px;">'
                '<div style="color: #3b82f6; font-weight: 600;">{:,}</div>'
                '<div style="color: #6b7280; font-size: 10px;">{} needs</div>'
                "</div>",
                obj.estimated_beneficiaries,
                obj.estimated_needs_addressed,
            )
        return "—"

    beneficiaries_display.short_description = "Beneficiaries"

    def status_badge(self, obj):
        """Visual badge for scenario status."""
        colors = {
            "draft": "#6b7280",
            "under_review": "#3b82f6",
            "approved": "#10b981",
            "implemented": "#8b5cf6",
            "archived": "#9ca3af",
        }
        color = colors.get(obj.status, "#6b7280")

        return format_html(
            '<span style="background: {}; color: white; padding: 4px 12px; '
            'border-radius: 16px; font-size: 11px; font-weight: 600; text-transform: uppercase;">{}</span>',
            color,
            obj.get_status_display(),
        )

    status_badge.short_description = "Status"


@admin.register(CeilingManagement)
class CeilingManagementAdmin(admin.ModelAdmin):
    """Admin configuration for planning ceiling tracking."""

    list_display = (
        "fiscal_year",
        "funding_source",
        "sector",
        "ceiling_amount",
        "allocated_amount",
        "remaining_ceiling",
        "is_exceeded",
        "updated_at",
    )
    list_filter = ("fiscal_year", "funding_source", "sector", "is_exceeded")
    search_fields = ("funding_source", "sector", "notes")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-fiscal_year", "funding_source", "sector")


@admin.register(ScenarioAllocation)
class ScenarioAllocationAdmin(admin.ModelAdmin):
    """Admin interface for scenario allocations."""

    list_display = [
        "scenario_link",
        "ppa_link",
        "allocated_amount_display",
        "priority_rank",
        "scores_display",
        "cost_per_beneficiary_display",
        "status_badge",
    ]

    list_filter = [
        "status",
        "scenario__status",
        "scenario__scenario_type",
        "ppa__sector",
        "created_at",
    ]

    search_fields = [
        "scenario__name",
        "ppa__title",
        "allocation_rationale",
    ]

    readonly_fields = [
        "id",
        "cost_per_beneficiary",
        "needs_coverage_score",
        "equity_score",
        "strategic_alignment_score",
        "overall_score",
        "created_at",
        "updated_at",
    ]

    fieldsets = [
        (
            "Allocation Details",
            {
                "fields": (
                    "id",
                    "scenario",
                    "ppa",
                    "allocated_amount",
                    "priority_rank",
                    "status",
                )
            },
        ),
        ("Rationale", {"fields": ("allocation_rationale",)}),
        (
            "Impact Metrics (Auto-calculated)",
            {
                "fields": (
                    "cost_per_beneficiary",
                    "needs_coverage_score",
                    "equity_score",
                    "strategic_alignment_score",
                    "overall_score",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "Metadata",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                ),
                "classes": ("collapse",),
            },
        ),
    ]

    autocomplete_fields = ["scenario", "ppa"]

    def scenario_link(self, obj):
        """Link to scenario."""
        return format_html(
            '<a href="/admin/monitoring/budgetscenario/{}/change/">{}</a>',
            obj.scenario.id,
            obj.scenario.name,
        )

    scenario_link.short_description = "Scenario"

    def ppa_link(self, obj):
        """Link to PPA."""
        return format_html(
            '<a href="/admin/monitoring/monitoringentry/{}/change/">{}</a>',
            obj.ppa.id,
            obj.ppa.title[:50],
        )

    ppa_link.short_description = "PPA"

    def allocated_amount_display(self, obj):
        """Display allocated amount."""
        return format_html(
            '<span style="color: #10b981; font-weight: 700; font-size: 14px;">₱{:,.2f}</span>',
            obj.allocated_amount,
        )

    allocated_amount_display.short_description = "Allocation"

    def cost_per_beneficiary_display(self, obj):
        """Display cost per beneficiary."""
        if obj.cost_per_beneficiary:
            return format_html(
                '<span style="color: #6b7280; font-size: 12px;">₱{:,.2f}/person</span>',
                obj.cost_per_beneficiary,
            )
        return "—"

    cost_per_beneficiary_display.short_description = "Cost/Person"

    def scores_display(self, obj):
        """Display compact scores."""
        if obj.overall_score:
            return format_html(
                '<div style="font-size: 11px;">'
                '<div style="color: #10b981;">Overall: {:.1f}</div>'
                '<div style="color: #6b7280;">N:{:.0f} E:{:.0f} S:{:.0f}</div>'
                "</div>",
                obj.overall_score,
                obj.needs_coverage_score or 0,
                obj.equity_score or 0,
                obj.strategic_alignment_score or 0,
            )
        return "—"

    scores_display.short_description = "Scores"

    def status_badge(self, obj):
        """Visual badge for allocation status."""
        colors = {
            "proposed": "#3b82f6",
            "approved": "#10b981",
            "rejected": "#ef4444",
            "pending_review": "#f59e0b",
        }
        color = colors.get(obj.status, "#6b7280")

        return format_html(
            '<span style="background: {}; color: white; padding: 3px 10px; '
            'border-radius: 12px; font-size: 10px; font-weight: 600;">{}</span>',
            color,
            obj.get_status_display(),
        )

    status_badge.short_description = "Status"

"""
Django Admin Configuration for Planning Module

Provides comprehensive admin interface for strategic planning functionality.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from planning.models import (
    StrategicPlan,
    StrategicGoal,
    AnnualWorkPlan,
    WorkPlanObjective
)


# Inline Admin Classes
class StrategicGoalInline(admin.TabularInline):
    """Inline admin for Strategic Goals within Strategic Plan"""
    model = StrategicGoal
    extra = 1
    fields = (
        'title',
        'priority',
        'target_metric',
        'target_value',
        'current_value',
        'completion_percentage',
        'status'
    )
    show_change_link = True


class WorkPlanObjectiveInline(admin.TabularInline):
    """Inline admin for Work Plan Objectives within Annual Work Plan"""
    model = WorkPlanObjective
    extra = 1
    fields = (
        'title',
        'strategic_goal',
        'target_date',
        'indicator',
        'target_value',
        'current_value',
        'completion_percentage',
        'status'
    )
    show_change_link = True


# Main Admin Classes
@admin.register(StrategicPlan)
class StrategicPlanAdmin(admin.ModelAdmin):
    """Admin interface for Strategic Plans"""

    list_display = (
        'title',
        'year_range_display',
        'status_badge',
        'progress_bar',
        'goals_count',
        'created_at'
    )
    list_filter = ('status', 'start_year', 'end_year')
    search_fields = ('title', 'vision', 'mission')
    readonly_fields = ('created_at', 'updated_at', 'overall_progress')
    inlines = [StrategicGoalInline]

    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'start_year', 'end_year', 'status')
        }),
        ('Strategic Direction', {
            'fields': ('vision', 'mission'),
            'description': 'Define the long-term vision and mission'
        }),
        ('Progress Tracking', {
            'fields': ('overall_progress',),
            'classes': ('collapse',)
        }),
        ('Audit Information', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def year_range_display(self, obj):
        """Display formatted year range"""
        return f"{obj.start_year}-{obj.end_year}"
    year_range_display.short_description = 'Period'

    def status_badge(self, obj):
        """Display status as colored badge"""
        colors = {
            'draft': '#6c757d',
            'approved': '#0d6efd',
            'active': '#198754',
            'archived': '#6c757d',
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px; font-size: 11px;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'

    def progress_bar(self, obj):
        """Display progress as visual bar"""
        progress = obj.overall_progress
        color = '#198754' if progress >= 75 else '#ffc107' if progress >= 50 else '#dc3545'
        return format_html(
            '<div style="width:100px; background-color:#e9ecef; border-radius:3px;">'
            '<div style="width:{}%; background-color:{}; height:20px; border-radius:3px; '
            'text-align:center; color:white; font-size:11px; line-height:20px;">{:.1f}%</div>'
            '</div>',
            progress, color, progress
        )
    progress_bar.short_description = 'Progress'

    def goals_count(self, obj):
        """Display count of strategic goals"""
        count = obj.goals.count()
        return format_html(
            '<a href="{}?strategic_plan__id__exact={}">{} goals</a>',
            reverse('admin:planning_strategicgoal_changelist'),
            obj.id,
            count
        )
    goals_count.short_description = 'Goals'

    def save_model(self, request, obj, form, change):
        """Auto-populate created_by field on creation"""
        if not change:  # Only on creation
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(StrategicGoal)
class StrategicGoalAdmin(admin.ModelAdmin):
    """Admin interface for Strategic Goals"""

    list_display = (
        'title',
        'strategic_plan',
        'priority_badge',
        'progress_indicator',
        'status_badge',
        'on_track_indicator'
    )
    list_filter = ('priority', 'status', 'strategic_plan')
    search_fields = ('title', 'description', 'target_metric')
    readonly_fields = ('created_at', 'updated_at', 'is_on_track')

    fieldsets = (
        ('Basic Information', {
            'fields': ('strategic_plan', 'title', 'description', 'priority', 'status')
        }),
        ('Target Metrics', {
            'fields': (
                'target_metric',
                'target_value',
                'current_value',
                'completion_percentage'
            ),
            'description': 'Define measurable targets for this goal'
        }),
        ('Progress Analysis', {
            'fields': ('is_on_track',),
            'classes': ('collapse',)
        }),
        ('Audit Information', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def priority_badge(self, obj):
        """Display priority as colored badge"""
        colors = {
            'critical': '#dc3545',
            'high': '#fd7e14',
            'medium': '#ffc107',
            'low': '#6c757d',
        }
        color = colors.get(obj.priority, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px; font-size: 11px; font-weight: bold;">{}</span>',
            color,
            obj.get_priority_display().upper()
        )
    priority_badge.short_description = 'Priority'

    def progress_indicator(self, obj):
        """Display completion percentage with bar"""
        percentage = float(obj.completion_percentage)
        color = '#198754' if percentage >= 75 else '#ffc107' if percentage >= 50 else '#dc3545'
        return format_html(
            '<div style="width:120px; background-color:#e9ecef; border-radius:3px;">'
            '<div style="width:{}%; background-color:{}; height:20px; border-radius:3px; '
            'text-align:center; color:white; font-size:11px; line-height:20px;">{:.1f}%</div>'
            '</div>',
            percentage, color, percentage
        )
    progress_indicator.short_description = 'Completion'

    def status_badge(self, obj):
        """Display status as colored badge"""
        colors = {
            'not_started': '#6c757d',
            'in_progress': '#0d6efd',
            'completed': '#198754',
            'deferred': '#ffc107',
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px; font-size: 11px;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'

    def on_track_indicator(self, obj):
        """Display whether goal is on track"""
        is_on_track = obj.is_on_track
        icon = '✓' if is_on_track else '✗'
        color = '#198754' if is_on_track else '#dc3545'
        return format_html(
            '<span style="color: {}; font-weight: bold; font-size: 16px;">{}</span>',
            color,
            icon
        )
    on_track_indicator.short_description = 'On Track'


@admin.register(AnnualWorkPlan)
class AnnualWorkPlanAdmin(admin.ModelAdmin):
    """Admin interface for Annual Work Plans"""

    list_display = (
        'title',
        'year',
        'strategic_plan',
        'status_badge',
        'progress_bar',
        'objectives_summary',
        'created_at'
    )
    list_filter = ('year', 'status', 'strategic_plan')
    search_fields = ('title', 'description')
    readonly_fields = ('created_at', 'updated_at', 'overall_progress', 'total_objectives', 'completed_objectives')
    inlines = [WorkPlanObjectiveInline]

    fieldsets = (
        ('Basic Information', {
            'fields': ('strategic_plan', 'title', 'year', 'status')
        }),
        ('Plan Details', {
            'fields': ('description', 'budget_total')
        }),
        ('Progress Tracking', {
            'fields': ('overall_progress', 'total_objectives', 'completed_objectives'),
            'classes': ('collapse',)
        }),
        ('Audit Information', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def status_badge(self, obj):
        """Display status as colored badge"""
        colors = {
            'draft': '#6c757d',
            'approved': '#0d6efd',
            'active': '#198754',
            'completed': '#20c997',
            'archived': '#6c757d',
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px; font-size: 11px;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'

    def progress_bar(self, obj):
        """Display progress as visual bar"""
        progress = obj.overall_progress
        color = '#198754' if progress >= 75 else '#ffc107' if progress >= 50 else '#dc3545'
        return format_html(
            '<div style="width:100px; background-color:#e9ecef; border-radius:3px;">'
            '<div style="width:{}%; background-color:{}; height:20px; border-radius:3px; '
            'text-align:center; color:white; font-size:11px; line-height:20px;">{:.1f}%</div>'
            '</div>',
            progress, color, progress
        )
    progress_bar.short_description = 'Progress'

    def objectives_summary(self, obj):
        """Display objectives count with link"""
        total = obj.total_objectives
        completed = obj.completed_objectives
        return format_html(
            '<a href="{}?annual_work_plan__id__exact={}">{} / {} objectives</a>',
            reverse('admin:planning_workplanobjective_changelist'),
            obj.id,
            completed,
            total
        )
    objectives_summary.short_description = 'Objectives'

    def save_model(self, request, obj, form, change):
        """Auto-populate created_by field on creation"""
        if not change:  # Only on creation
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(WorkPlanObjective)
class WorkPlanObjectiveAdmin(admin.ModelAdmin):
    """Admin interface for Work Plan Objectives"""

    list_display = (
        'title',
        'annual_work_plan',
        'strategic_goal_link',
        'target_date',
        'progress_indicator',
        'status_badge',
        'overdue_indicator'
    )
    list_filter = ('status', 'annual_work_plan', 'target_date')
    search_fields = ('title', 'description', 'indicator')
    readonly_fields = ('created_at', 'updated_at', 'is_overdue', 'days_remaining')

    fieldsets = (
        ('Basic Information', {
            'fields': (
                'annual_work_plan',
                'strategic_goal',
                'title',
                'description',
                'target_date',
                'status'
            )
        }),
        ('Success Indicators', {
            'fields': (
                'indicator',
                'baseline_value',
                'target_value',
                'current_value',
                'completion_percentage'
            ),
            'description': 'Define how success will be measured'
        }),
        ('Deadline Analysis', {
            'fields': ('is_overdue', 'days_remaining'),
            'classes': ('collapse',)
        }),
        ('Audit Information', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    actions = ['update_progress_from_indicators']

    def strategic_goal_link(self, obj):
        """Display strategic goal with link"""
        if obj.strategic_goal:
            url = reverse('admin:planning_strategicgoal_change', args=[obj.strategic_goal.id])
            return format_html('<a href="{}">{}</a>', url, obj.strategic_goal.title)
        return '-'
    strategic_goal_link.short_description = 'Strategic Goal'

    def progress_indicator(self, obj):
        """Display completion percentage with bar"""
        percentage = float(obj.completion_percentage)
        color = '#198754' if percentage >= 75 else '#ffc107' if percentage >= 50 else '#dc3545'
        return format_html(
            '<div style="width:120px; background-color:#e9ecef; border-radius:3px;">'
            '<div style="width:{}%; background-color:{}; height:20px; border-radius:3px; '
            'text-align:center; color:white; font-size:11px; line-height:20px;">{:.1f}%</div>'
            '</div>',
            percentage, color, percentage
        )
    progress_indicator.short_description = 'Completion'

    def status_badge(self, obj):
        """Display status as colored badge"""
        colors = {
            'not_started': '#6c757d',
            'in_progress': '#0d6efd',
            'completed': '#198754',
            'deferred': '#ffc107',
            'cancelled': '#dc3545',
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px; font-size: 11px;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'

    def overdue_indicator(self, obj):
        """Display whether objective is overdue"""
        is_overdue = obj.is_overdue
        if is_overdue:
            days = abs(obj.days_remaining)
            return format_html(
                '<span style="color: #dc3545; font-weight: bold;">'
                '⚠ {} days overdue</span>',
                days
            )
        elif obj.status == 'completed':
            return format_html('<span style="color: #198754;">✓ Completed</span>')
        else:
            days = obj.days_remaining
            if days <= 7:
                color = '#dc3545'
            elif days <= 30:
                color = '#ffc107'
            else:
                color = '#198754'
            return format_html(
                '<span style="color: {};">{} days remaining</span>',
                color,
                days
            )
    overdue_indicator.short_description = 'Deadline Status'

    def update_progress_from_indicators(self, request, queryset):
        """Admin action to update progress from indicator values"""
        count = 0
        for objective in queryset:
            objective.update_progress_from_indicator()
            count += 1
        self.message_user(
            request,
            f'Successfully updated progress for {count} objective(s) based on indicator values.'
        )
    update_progress_from_indicators.short_description = 'Update progress from indicator values'


# Admin site customization
admin.site.site_header = "OBCMS Planning Administration"
admin.site.site_title = "OBCMS Planning Admin"
admin.site.index_title = "Strategic Planning Management"

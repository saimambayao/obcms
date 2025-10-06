"""
Admin interface for the unified WorkItem model.

Uses django-mptt's MPTTModelAdmin for hierarchical tree display.
See: docs/refactor/UNIFIED_WORK_HIERARCHY_EVALUATION.md
"""

from django.contrib import admin
from django.utils.html import format_html
from mptt.admin import MPTTModelAdmin, DraggableMPTTAdmin

from .work_item_model import WorkItem


@admin.register(WorkItem)
class WorkItemAdmin(DraggableMPTTAdmin):
    """
    Admin interface for WorkItem with hierarchical drag-and-drop tree interface.

    Features:
    - Drag-and-drop reorganization
    - Hierarchical indentation
    - Type-specific icons and colors
    - Progress bars
    - Status badges
    """

    # ========== LIST DISPLAY ==========
    list_display = (
        "tree_actions",
        "indented_title",
        "work_type_badge",
        "status_badge",
        "priority_badge",
        "progress_bar",
        "assigned_to",
        "date_range",
        "calendar_visibility",
    )

    list_display_links = ("indented_title",)

    # ========== FILTERS ==========
    list_filter = (
        "work_type",
        "status",
        "priority",
        "is_calendar_visible",
        "created_at",
        "start_date",
    )

    # ========== SEARCH ==========
    search_fields = ("title", "description", "assignees__username", "assignees__first_name", "assignees__last_name")

    # ========== FIELD ORDERING ==========
    fieldsets = (
        (
            "Basic Information",
            {
                "fields": (
                    "work_type",
                    "parent",
                    "title",
                    "description",
                )
            },
        ),
        (
            "Status & Progress",
            {
                "fields": (
                    "status",
                    "priority",
                    "progress",
                    "auto_calculate_progress",
                )
            },
        ),
        (
            "Scheduling",
            {
                "fields": (
                    "start_date",
                    "due_date",
                    "start_time",
                    "end_time",
                    "completed_at",
                )
            },
        ),
        (
            "Assignment",
            {
                "fields": (
                    "assignees",
                    "teams",
                    "created_by",
                )
            },
        ),
        (
            "Calendar Settings",
            {
                "fields": (
                    "is_calendar_visible",
                    "calendar_color",
                    "is_recurring",
                    "recurrence_pattern",
                )
            },
        ),
        (
            "Type-Specific Data",
            {
                "classes": ("collapse",),
                "fields": (
                    "project_data",
                    "activity_data",
                    "task_data",
                ),
            },
        ),
        (
            "Relationships",
            {
                "classes": ("collapse",),
                "fields": (
                    "related_items",
                    "content_type",
                    "object_id",
                ),
            },
        ),
    )

    # ========== DRAGGABLE MPTT SETTINGS ==========
    mptt_level_indent = 20
    expand_tree_by_default = False

    # ========== FILTERS & RELATED LOOKUPS ==========
    autocomplete_fields = ["assignees", "teams", "created_by", "recurrence_pattern"]
    filter_horizontal = ("related_items",)

    # ========== CUSTOM DISPLAY METHODS ==========

    def indented_title(self, instance):
        """Display title with hierarchical indentation."""
        return instance.title

    indented_title.short_description = "Title"

    def work_type_badge(self, instance):
        """Display work type with icon and color."""
        colors = {
            WorkItem.WORK_TYPE_PROJECT: "#3B82F6",  # Blue
            WorkItem.WORK_TYPE_SUB_PROJECT: "#60A5FA",  # Light Blue
            WorkItem.WORK_TYPE_ACTIVITY: "#10B981",  # Green
            WorkItem.WORK_TYPE_SUB_ACTIVITY: "#34D399",  # Light Green
            WorkItem.WORK_TYPE_TASK: "#F59E0B",  # Orange
            WorkItem.WORK_TYPE_SUBTASK: "#FBBF24",  # Light Orange
        }

        icons = {
            WorkItem.WORK_TYPE_PROJECT: "📁",
            WorkItem.WORK_TYPE_SUB_PROJECT: "📂",
            WorkItem.WORK_TYPE_ACTIVITY: "🎯",
            WorkItem.WORK_TYPE_SUB_ACTIVITY: "🎲",
            WorkItem.WORK_TYPE_TASK: "📋",
            WorkItem.WORK_TYPE_SUBTASK: "✓",
        }

        color = colors.get(instance.work_type, "#6B7280")
        icon = icons.get(instance.work_type, "•")

        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 12px; font-size: 11px; font-weight: bold;">'
            "{} {}</span>",
            color,
            icon,
            instance.get_work_type_display(),
        )

    work_type_badge.short_description = "Type"
    work_type_badge.admin_order_field = "work_type"

    def status_badge(self, instance):
        """Display status with color coding."""
        colors = {
            WorkItem.STATUS_NOT_STARTED: "#9CA3AF",  # Gray
            WorkItem.STATUS_IN_PROGRESS: "#3B82F6",  # Blue
            WorkItem.STATUS_AT_RISK: "#F59E0B",  # Orange
            WorkItem.STATUS_BLOCKED: "#EF4444",  # Red
            WorkItem.STATUS_COMPLETED: "#10B981",  # Green
            WorkItem.STATUS_CANCELLED: "#6B7280",  # Dark Gray
        }

        color = colors.get(instance.status, "#6B7280")

        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 12px; font-size: 11px; font-weight: bold;">{}</span>',
            color,
            instance.get_status_display(),
        )

    status_badge.short_description = "Status"
    status_badge.admin_order_field = "status"

    def priority_badge(self, instance):
        """Display priority with color coding."""
        colors = {
            WorkItem.PRIORITY_LOW: "#10B981",  # Green
            WorkItem.PRIORITY_MEDIUM: "#3B82F6",  # Blue
            WorkItem.PRIORITY_HIGH: "#F59E0B",  # Orange
            WorkItem.PRIORITY_URGENT: "#EF4444",  # Red
            WorkItem.PRIORITY_CRITICAL: "#DC2626",  # Dark Red
        }

        color = colors.get(instance.priority, "#6B7280")

        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 12px; font-size: 11px; font-weight: bold;">{}</span>',
            color,
            instance.get_priority_display(),
        )

    priority_badge.short_description = "Priority"
    priority_badge.admin_order_field = "priority"

    def progress_bar(self, instance):
        """Display progress as a visual progress bar."""
        progress = instance.progress
        color = "#10B981" if progress == 100 else "#3B82F6" if progress >= 50 else "#F59E0B"

        return format_html(
            '<div style="width: 100px; background-color: #E5E7EB; '
            'border-radius: 4px; overflow: hidden;">'
            '<div style="width: {}%; background-color: {}; height: 20px; '
            'text-align: center; line-height: 20px; color: white; '
            'font-size: 11px; font-weight: bold;">{}</div></div>',
            progress,
            color,
            f"{progress}%",
        )

    progress_bar.short_description = "Progress"
    progress_bar.admin_order_field = "progress"

    def assigned_to(self, instance):
        """Display assigned users."""
        assignees = instance.assignees.all()[:3]
        if not assignees:
            return format_html('<span style="color: #9CA3AF;">Unassigned</span>')

        names = [u.get_full_name() or u.username for u in assignees]
        more = instance.assignees.count() - 3

        text = ", ".join(names)
        if more > 0:
            text += f" +{more} more"

        return format_html('<span title="{}">{}</span>', text, text[:30] + "..." if len(text) > 30 else text)

    assigned_to.short_description = "Assigned To"

    def date_range(self, instance):
        """Display start and due dates."""
        if not instance.start_date and not instance.due_date:
            return format_html('<span style="color: #9CA3AF;">No dates</span>')

        start = instance.start_date.strftime("%b %d") if instance.start_date else "?"
        due = instance.due_date.strftime("%b %d") if instance.due_date else "?"

        return format_html("{} → {}", start, due)

    date_range.short_description = "Date Range"

    def calendar_visibility(self, instance):
        """Display calendar visibility status."""
        if instance.is_calendar_visible:
            return format_html(
                '<span style="color: #10B981; font-weight: bold;">✓ Visible</span>'
            )
        return format_html('<span style="color: #9CA3AF;">Hidden</span>')

    calendar_visibility.short_description = "Calendar"
    calendar_visibility.admin_order_field = "is_calendar_visible"

    # ========== ACTIONS ==========
    actions = [
        "mark_completed",
        "mark_in_progress",
        "show_in_calendar",
        "hide_from_calendar",
    ]

    def mark_completed(self, request, queryset):
        """Mark selected items as completed."""
        updated = queryset.update(status=WorkItem.STATUS_COMPLETED, progress=100)
        self.message_user(request, f"{updated} work items marked as completed.")

    mark_completed.short_description = "Mark as completed"

    def mark_in_progress(self, request, queryset):
        """Mark selected items as in progress."""
        updated = queryset.update(status=WorkItem.STATUS_IN_PROGRESS)
        self.message_user(request, f"{updated} work items marked as in progress.")

    mark_in_progress.short_description = "Mark as in progress"

    def show_in_calendar(self, request, queryset):
        """Show selected items in calendar."""
        updated = queryset.update(is_calendar_visible=True)
        self.message_user(request, f"{updated} work items now visible in calendar.")

    show_in_calendar.short_description = "Show in calendar"

    def hide_from_calendar(self, request, queryset):
        """Hide selected items from calendar."""
        updated = queryset.update(is_calendar_visible=False)
        self.message_user(request, f"{updated} work items hidden from calendar.")

    hide_from_calendar.short_description = "Hide from calendar"

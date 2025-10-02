from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils import timezone

from .models import (
    Barangay,
    CalendarNotification,
    CalendarResource,
    CalendarResourceBooking,
    ExternalCalendarSync,
    Municipality,
    Province,
    RecurringEventPattern,
    Region,
    SharedCalendarLink,
    StaffLeave,
    StaffTask,
    StaffTeam,
    StaffTeamMembership,
    TaskTemplate,
    TaskTemplateItem,
    User,
    UserCalendarPreferences,
)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin interface for the custom User model."""

    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "user_type",
        "organization",
        "is_approved",
        "is_active",
        "date_joined",
    )
    list_filter = (
        "user_type",
        "is_approved",
        "is_active",
        "is_staff",
        "is_superuser",
        "date_joined",
    )
    search_fields = ("username", "first_name", "last_name", "email", "organization")
    ordering = ("-date_joined",)

    fieldsets = BaseUserAdmin.fieldsets + (
        (
            "OBC Information",
            {"fields": ("user_type", "organization", "position", "contact_number")},
        ),
        ("Approval Status", {"fields": ("is_approved", "approved_by", "approved_at")}),
    )

    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        (
            "OBC Information",
            {"fields": ("user_type", "organization", "position", "contact_number")},
        ),
    )

    readonly_fields = ("approved_at",)

    def save_model(self, request, obj, form, change):
        """Override save to handle approval logic."""
        if change and "is_approved" in form.changed_data and obj.is_approved:
            if not obj.approved_by:
                obj.approved_by = request.user
            if not obj.approved_at:
                obj.approved_at = timezone.now()
        super().save_model(request, obj, form, change)

    actions = ["approve_users", "disapprove_users"]

    def approve_users(self, request, queryset):
        """Bulk approve selected users."""
        updated = queryset.filter(is_approved=False).update(
            is_approved=True, approved_by=request.user, approved_at=timezone.now()
        )
        self.message_user(request, f"{updated} users were approved.")

    approve_users.short_description = "Approve selected users"

    def disapprove_users(self, request, queryset):
        """Bulk disapprove selected users."""
        updated = queryset.filter(is_approved=True).update(
            is_approved=False, approved_by=None, approved_at=None
        )
        self.message_user(request, f"{updated} users were disapproved.")

    disapprove_users.short_description = "Disapprove selected users"


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    """Admin interface for Region model."""

    list_display = ("code", "name", "province_count", "is_active", "created_at")
    list_filter = ("is_active", "created_at")
    search_fields = ("code", "name", "description")
    ordering = ("code",)
    readonly_fields = ("created_at", "updated_at", "province_count")

    fieldsets = (
        (None, {"fields": ("code", "name", "description", "is_active")}),
        ("Statistics", {"fields": ("province_count",), "classes": ("collapse",)}),
        (
            "Timestamps",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )


@admin.register(Province)
class ProvinceAdmin(admin.ModelAdmin):
    """Admin interface for Province model."""

    list_display = (
        "name",
        "region",
        "capital",
        "municipality_count",
        "is_active",
        "created_at",
    )
    list_filter = ("region", "is_active", "created_at")
    search_fields = ("code", "name", "capital", "region__name")
    ordering = ("region__code", "name")
    readonly_fields = ("created_at", "updated_at", "municipality_count", "full_path")

    fieldsets = (
        (None, {"fields": ("region", "code", "name", "capital", "is_active")}),
        ("Administrative Path", {"fields": ("full_path",), "classes": ("collapse",)}),
        ("Statistics", {"fields": ("municipality_count",), "classes": ("collapse",)}),
        (
            "Timestamps",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )


@admin.register(Municipality)
class MunicipalityAdmin(admin.ModelAdmin):
    """Admin interface for Municipality model."""

    list_display = (
        "name",
        "municipality_type",
        "province",
        "barangay_count",
        "is_active",
        "created_at",
    )
    list_filter = (
        "municipality_type",
        "province__region",
        "province",
        "is_active",
        "created_at",
    )
    search_fields = ("code", "name", "province__name", "province__region__name")
    ordering = ("province__region__code", "province__name", "name")
    readonly_fields = ("created_at", "updated_at", "barangay_count", "full_path")

    fieldsets = (
        (
            None,
            {"fields": ("province", "code", "name", "municipality_type", "is_active")},
        ),
        ("Administrative Path", {"fields": ("full_path",), "classes": ("collapse",)}),
        ("Statistics", {"fields": ("barangay_count",), "classes": ("collapse",)}),
        (
            "Timestamps",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )


@admin.register(Barangay)
class BarangayAdmin(admin.ModelAdmin):
    """Admin interface for Barangay model."""

    list_display = (
        "name",
        "municipality",
        "province",
        "region",
        "is_urban",
        "is_active",
        "created_at",
    )
    list_filter = (
        "is_urban",
        "is_active",
        "municipality__province__region",
        "municipality__province",
        "municipality",
        "created_at",
    )
    search_fields = (
        "code",
        "name",
        "municipality__name",
        "municipality__province__name",
        "municipality__province__region__name",
    )
    ordering = (
        "municipality__province__region__code",
        "municipality__province__name",
        "municipality__name",
        "name",
    )
    readonly_fields = ("created_at", "updated_at", "full_path", "region", "province")


@admin.register(StaffTeam)
class StaffTeamAdmin(admin.ModelAdmin):
    """Admin configuration for staff teams."""

    list_display = ("name", "slug", "is_active", "created_at")
    list_filter = ("is_active", "created_at")
    search_fields = ("name", "description", "mission")
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ("created_at", "updated_at")


@admin.register(StaffTeamMembership)
class StaffTeamMembershipAdmin(admin.ModelAdmin):
    """Admin configuration for staff team memberships."""

    list_display = (
        "user",
        "team",
        "role",
        "is_active",
        "joined_at",
    )
    list_filter = ("role", "is_active", "team")
    search_fields = (
        "user__first_name",
        "user__last_name",
        "user__email",
        "team__name",
    )
    autocomplete_fields = ("team", "user", "assigned_by")
    readonly_fields = ("created_at", "updated_at")


@admin.register(StaffTask)
class StaffTaskAdmin(admin.ModelAdmin):
    """Admin configuration for staff tasks."""

    list_display = (
        "title",
        "domain_display_col",
        "teams_list",
        "assignee_list",
        "status",
        "priority",
        "due_date",
        "progress",
    )
    list_filter = (
        "status",
        "priority",
        "domain",
        "assessment_phase",
        "policy_phase",
        "service_phase",
        "task_role",
        "teams",
        "assignees",
    )
    search_fields = ("title", "description", "impact", "task_category")
    autocomplete_fields = (
        "teams",
        "assignees",
        "created_by",
        "linked_event",
        "created_from_template",
        "related_assessment",
        "related_policy",
        "related_ppa",
        "related_service",
        "related_community",
    )
    readonly_fields = (
        "created_at",
        "updated_at",
        "completed_at",
        "primary_domain_object",
        "domain_display",
    )
    fieldsets = (
        (
            "Basic Information",
            {
                "fields": (
                    "title",
                    "description",
                    "domain",
                    "task_category",
                    "impact",
                    "created_from_template",
                )
            },
        ),
        (
            "Assignment",
            {
                "fields": (
                    "teams",
                    "assignees",
                    "created_by",
                    "task_role",
                )
            },
        ),
        (
            "Schedule & Status",
            {
                "fields": (
                    "start_date",
                    "due_date",
                    "status",
                    "priority",
                    "progress",
                    "estimated_hours",
                    "actual_hours",
                )
            },
        ),
        (
            "Domain Relationships",
            {
                "fields": (
                    "linked_event",
                    "related_assessment",
                    "related_survey",
                    "related_workshop",
                    "related_baseline",
                    "related_need",
                    "related_mapping",
                    "related_policy",
                    "related_policy_milestone",
                    "related_policy_evidence",
                    "related_ppa",
                    "related_funding_flow",
                    "related_workflow_stage",
                    "related_outcome_indicator",
                    "related_strategic_goal",
                    "related_service",
                    "related_application",
                    "related_community",
                    "related_stakeholder",
                    "related_engagement",
                    "related_municipality_coverage",
                    "related_organization",
                    "related_partnership",
                    "related_partnership_milestone",
                    "related_communication",
                    "related_mao_focal_person",
                    "related_training",
                    "related_dev_plan",
                    "related_performance_target",
                    "related_municipal_profile",
                    "related_import",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "Workflow-Specific",
            {
                "fields": (
                    "assessment_phase",
                    "policy_phase",
                    "service_phase",
                    "deliverable_type",
                    "geographic_scope",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "Dependencies",
            {
                "fields": ("depends_on",),
                "classes": ("collapse",),
            },
        ),
        (
            "Timestamps",
            {
                "fields": ("created_at", "updated_at", "completed_at"),
                "classes": ("collapse",),
            },
        ),
    )

    @admin.display(description="Domain")
    def domain_display_col(self, obj):
        return obj.domain_display

    @admin.display(description="Assignees")
    def assignee_list(self, obj):
        return obj.assignee_display_name

    def teams_list(self, obj):
        """Display teams for the task."""
        teams = list(obj.teams.all())
        if not teams:
            return "No teams"
        return ", ".join(team.name for team in teams)

    teams_list.short_description = "Teams"


@admin.register(TaskTemplate)
class TaskTemplateAdmin(admin.ModelAdmin):
    """Admin configuration for task templates."""

    list_display = ("name", "domain", "is_active", "item_count", "created_at")
    list_filter = ("domain", "is_active", "created_at")
    search_fields = ("name", "description")
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        (
            None,
            {"fields": ("name", "domain", "description", "is_active")},
        ),
        (
            "Timestamps",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    @admin.display(description="Items")
    def item_count(self, obj):
        return obj.items.count()


class TaskTemplateItemInline(admin.TabularInline):
    """Inline for task template items."""

    model = TaskTemplateItem
    extra = 1
    fields = (
        "sequence",
        "title",
        "priority",
        "estimated_hours",
        "days_from_start",
        "assessment_phase",
        "policy_phase",
        "service_phase",
        "task_role",
    )


@admin.register(TaskTemplateItem)
class TaskTemplateItemAdmin(admin.ModelAdmin):
    """Admin configuration for task template items."""

    list_display = (
        "template",
        "sequence",
        "title",
        "priority",
        "estimated_hours",
        "days_from_start",
    )
    list_filter = (
        "template",
        "priority",
        "assessment_phase",
        "policy_phase",
        "service_phase",
        "task_role",
    )
    search_fields = ("title", "description")
    autocomplete_fields = ("template",)
    fieldsets = (
        (
            "Basic Information",
            {
                "fields": (
                    "template",
                    "sequence",
                    "title",
                    "description",
                    "task_category",
                )
            },
        ),
        (
            "Effort & Timing",
            {"fields": ("priority", "estimated_hours", "days_from_start")},
        ),
        (
            "Workflow Phases",
            {
                "fields": (
                    "assessment_phase",
                    "policy_phase",
                    "service_phase",
                    "task_role",
                ),
                "classes": ("collapse",),
            },
        ),
    )


# =============================================================================
# Calendar System Admin Registrations
# =============================================================================


@admin.register(RecurringEventPattern)
class RecurringEventPatternAdmin(admin.ModelAdmin):
    """Admin interface for Recurring Event Patterns."""

    list_display = (
        "id",
        "recurrence_type",
        "interval",
        "until_date",
        "count",
        "created_at",
    )
    list_filter = ("recurrence_type", "created_at")
    search_fields = ("recurrence_type",)
    readonly_fields = ("created_at", "modified_at")

    fieldsets = (
        ("Recurrence Type", {"fields": ("recurrence_type", "interval")}),
        ("Weekly Options", {"fields": ("by_weekday",), "classes": ("collapse",)}),
        (
            "Monthly Options",
            {"fields": ("by_monthday", "by_setpos"), "classes": ("collapse",)},
        ),
        ("End Conditions", {"fields": ("count", "until_date")}),
        ("Exceptions", {"fields": ("exception_dates",), "classes": ("collapse",)}),
        (
            "Timestamps",
            {"fields": ("created_at", "modified_at"), "classes": ("collapse",)},
        ),
    )


@admin.register(CalendarResource)
class CalendarResourceAdmin(admin.ModelAdmin):
    """Admin interface for Calendar Resources."""

    list_display = (
        "name",
        "resource_type",
        "is_available",
        "booking_requires_approval",
        "capacity",
        "created_at",
    )
    list_filter = ("resource_type", "is_available", "booking_requires_approval")
    search_fields = ("name", "description", "location")
    readonly_fields = ("created_at", "modified_at")

    fieldsets = (
        ("Basic Information", {"fields": ("resource_type", "name", "description")}),
        ("Capacity & Location", {"fields": ("capacity", "location")}),
        ("Availability", {"fields": ("is_available", "booking_requires_approval")}),
        ("Cost", {"fields": ("cost_per_use",)}),
        (
            "Timestamps",
            {"fields": ("created_at", "modified_at"), "classes": ("collapse",)},
        ),
    )


@admin.register(CalendarResourceBooking)
class CalendarResourceBookingAdmin(admin.ModelAdmin):
    """Admin interface for Calendar Resource Bookings."""

    list_display = (
        "resource",
        "start_datetime",
        "end_datetime",
        "status",
        "booked_by",
        "approved_by",
    )
    list_filter = ("status", "start_datetime", "resource__resource_type")
    search_fields = ("resource__name", "booked_by__username", "notes")
    readonly_fields = ("created_at",)
    date_hierarchy = "start_datetime"

    fieldsets = (
        ("Resource", {"fields": ("resource",)}),
        ("Event Link", {"fields": ("content_type", "object_id")}),
        ("Schedule", {"fields": ("start_datetime", "end_datetime")}),
        ("Status", {"fields": ("status", "booked_by", "approved_by")}),
        ("Notes", {"fields": ("notes",)}),
        ("Timestamps", {"fields": ("created_at",), "classes": ("collapse",)}),
    )


@admin.register(CalendarNotification)
class CalendarNotificationAdmin(admin.ModelAdmin):
    """Admin interface for Calendar Notifications."""

    list_display = (
        "recipient",
        "notification_type",
        "delivery_method",
        "scheduled_for",
        "status",
        "sent_at",
    )
    list_filter = ("notification_type", "delivery_method", "status", "scheduled_for")
    search_fields = ("recipient__username", "recipient__email", "error_message")
    readonly_fields = ("created_at", "sent_at")
    date_hierarchy = "scheduled_for"

    fieldsets = (
        ("Recipient", {"fields": ("recipient",)}),
        ("Event Link", {"fields": ("content_type", "object_id")}),
        ("Notification Details", {"fields": ("notification_type", "delivery_method")}),
        ("Schedule & Status", {"fields": ("scheduled_for", "sent_at", "status")}),
        ("Error Info", {"fields": ("error_message",), "classes": ("collapse",)}),
        ("Timestamps", {"fields": ("created_at",), "classes": ("collapse",)}),
    )


@admin.register(UserCalendarPreferences)
class UserCalendarPreferencesAdmin(admin.ModelAdmin):
    """Admin interface for User Calendar Preferences."""

    list_display = (
        "user",
        "email_enabled",
        "sms_enabled",
        "push_enabled",
        "daily_digest",
        "weekly_digest",
        "timezone",
    )
    list_filter = (
        "email_enabled",
        "sms_enabled",
        "push_enabled",
        "daily_digest",
        "weekly_digest",
    )
    search_fields = ("user__username", "user__email")
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        ("User", {"fields": ("user",)}),
        ("Default Reminders", {"fields": ("default_reminder_times",)}),
        (
            "Notification Channels",
            {"fields": ("email_enabled", "sms_enabled", "push_enabled")},
        ),
        ("Digest Emails", {"fields": ("daily_digest", "weekly_digest")}),
        ("Quiet Hours", {"fields": ("quiet_hours_start", "quiet_hours_end")}),
        ("Timezone", {"fields": ("timezone",)}),
        (
            "Timestamps",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )


@admin.register(ExternalCalendarSync)
class ExternalCalendarSyncAdmin(admin.ModelAdmin):
    """Admin interface for External Calendar Sync."""

    list_display = ("user", "provider", "sync_direction", "last_sync_at", "is_active")
    list_filter = ("provider", "sync_direction", "is_active")
    search_fields = ("user__username", "sync_status")
    readonly_fields = ("created_at", "last_sync_at")

    fieldsets = (
        ("User & Provider", {"fields": ("user", "provider")}),
        (
            "OAuth Tokens",
            {
                "fields": ("access_token", "refresh_token", "token_expires_at"),
                "classes": ("collapse",),
            },
        ),
        ("Sync Settings", {"fields": ("sync_direction", "sync_modules")}),
        ("Status", {"fields": ("last_sync_at", "sync_status", "is_active")}),
        ("Timestamps", {"fields": ("created_at",), "classes": ("collapse",)}),
    )


@admin.register(SharedCalendarLink)
class SharedCalendarLinkAdmin(admin.ModelAdmin):
    """Admin interface for Shared Calendar Links."""

    list_display = (
        "token",
        "created_by",
        "expires_at",
        "view_count",
        "max_views",
        "is_active",
    )
    list_filter = ("is_active", "expires_at")
    search_fields = ("token", "created_by__username")
    readonly_fields = ("token", "created_at", "view_count")
    date_hierarchy = "expires_at"

    fieldsets = (
        ("Link Details", {"fields": ("token", "created_by")}),
        (
            "Access Control",
            {"fields": ("expires_at", "max_views", "view_count", "is_active")},
        ),
        (
            "Filters",
            {"fields": ("filter_modules", "filter_date_from", "filter_date_to")},
        ),
        ("Timestamps", {"fields": ("created_at",), "classes": ("collapse",)}),
    )


@admin.register(StaffLeave)
class StaffLeaveAdmin(admin.ModelAdmin):
    """Admin interface for Staff Leave."""

    list_display = (
        "staff",
        "leave_type",
        "start_date",
        "end_date",
        "status",
        "approved_by",
    )
    list_filter = ("leave_type", "status", "start_date")
    search_fields = ("staff__username", "reason", "notes")
    readonly_fields = ("created_at", "updated_at")
    date_hierarchy = "start_date"

    fieldsets = (
        ("Staff", {"fields": ("staff",)}),
        ("Leave Details", {"fields": ("leave_type", "start_date", "end_date")}),
        ("Status", {"fields": ("status", "approved_by")}),
        ("Reason & Notes", {"fields": ("reason", "notes")}),
        (
            "Timestamps",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    actions = ["approve_leave", "reject_leave"]

    def approve_leave(self, request, queryset):
        """Bulk approve selected leave requests."""
        updated = queryset.filter(status="pending").update(
            status="approved", approved_by=request.user
        )
        self.message_user(request, f"{updated} leave requests were approved.")

    approve_leave.short_description = "Approve selected leave requests"

    def reject_leave(self, request, queryset):
        """Bulk reject selected leave requests."""
        updated = queryset.filter(status="pending").update(status="rejected")
        self.message_user(request, f"{updated} leave requests were rejected.")

    reject_leave.short_description = "Reject selected leave requests"

import json

from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from .models import (
    AIConversation,
    AIGeneratedDocument,
    AIInsight,
    AIOperation,
    AIUsageMetrics,
)


@admin.register(AIConversation)
class AIConversationAdmin(admin.ModelAdmin):
    """Admin interface for AI conversations."""

    list_display = [
        "title",
        "user",
        "conversation_type",
        "related_policy_link",
        "message_count",
        "model_used",
        "is_active",
        "created_at",
    ]
    list_filter = ["conversation_type", "model_used", "is_active", "created_at"]
    search_fields = ["title", "user__username", "user__email", "related_policy__title"]
    readonly_fields = ["message_count", "last_message_time", "messages_display"]
    date_hierarchy = "created_at"

    fieldsets = (
        (
            "Basic Information",
            {"fields": ("user", "conversation_type", "title", "related_policy")},
        ),
        (
            "Conversation Data",
            {
                "fields": (
                    "messages_display",
                    "context_data",
                    "message_count",
                    "last_message_time",
                ),
                "classes": ("collapse",),
            },
        ),
        ("Settings", {"fields": ("model_used", "is_active")}),
        (
            "Timestamps",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    def related_policy_link(self, obj):
        if obj.related_policy:
            url = reverse(
                "admin:policy_tracking_policyrecommendation_change",
                args=[obj.related_policy.pk],
            )
            return format_html(
                '<a href="{}">{}</a>', url, obj.related_policy.title[:50]
            )
        return "-"

    related_policy_link.short_description = "Related Policy"

    def messages_display(self, obj):
        if obj.messages:
            formatted_messages = []
            for msg in obj.messages[-5:]:  # Show last 5 messages
                role = msg.get("role", "unknown")
                content = (
                    msg.get("content", "")[:100] + "..."
                    if len(msg.get("content", "")) > 100
                    else msg.get("content", "")
                )
                timestamp = msg.get("timestamp", "No timestamp")
                formatted_messages.append(
                    f"<strong>{role.title()}:</strong> {content}<br><small>{timestamp}</small>"
                )
            return mark_safe("<br><br>".join(formatted_messages))
        return "No messages"

    messages_display.short_description = "Recent Messages"


@admin.register(AIInsight)
class AIInsightAdmin(admin.ModelAdmin):
    """Admin interface for AI insights."""

    list_display = [
        "title",
        "insight_type",
        "related_policy_link",
        "confidence_level",
        "is_validated",
        "view_count",
        "usefulness_score",
        "created_at",
    ]
    list_filter = [
        "insight_type",
        "confidence_level",
        "is_validated",
        "model_used",
        "created_at",
    ]
    search_fields = ["title", "content", "related_policy__title", "tags"]
    readonly_fields = ["view_count", "generated_by", "created_at", "updated_at"]
    date_hierarchy = "created_at"

    fieldsets = (
        (
            "Basic Information",
            {"fields": ("title", "insight_type", "related_policy", "conversation")},
        ),
        (
            "Content",
            {
                "fields": (
                    "summary",
                    "content",
                    "key_points",
                    "recommendations",
                    "cultural_considerations",
                )
            },
        ),
        (
            "Quality & Validation",
            {
                "fields": (
                    "confidence_level",
                    "model_used",
                    "is_validated",
                    "validated_by",
                    "validation_notes",
                    "usefulness_score",
                )
            },
        ),
        (
            "Usage & Metadata",
            {
                "fields": (
                    "view_count",
                    "tags",
                    "generated_by",
                    "created_at",
                    "updated_at",
                ),
                "classes": ("collapse",),
            },
        ),
    )

    actions = ["mark_as_validated", "mark_as_unvalidated"]

    def related_policy_link(self, obj):
        if obj.related_policy:
            url = reverse(
                "admin:policy_tracking_policyrecommendation_change",
                args=[obj.related_policy.pk],
            )
            return format_html(
                '<a href="{}">{}</a>', url, obj.related_policy.title[:50]
            )
        return "-"

    related_policy_link.short_description = "Related Policy"

    def mark_as_validated(self, request, queryset):
        queryset.update(is_validated=True, validated_by=request.user)
        self.message_user(request, f"{queryset.count()} insights marked as validated.")

    mark_as_validated.short_description = "Mark selected insights as validated"

    def mark_as_unvalidated(self, request, queryset):
        queryset.update(is_validated=False, validated_by=None, validation_notes="")
        self.message_user(
            request, f"{queryset.count()} insights marked as unvalidated."
        )

    mark_as_unvalidated.short_description = "Mark selected insights as unvalidated"


@admin.register(AIGeneratedDocument)
class AIGeneratedDocumentAdmin(admin.ModelAdmin):
    """Admin interface for AI generated documents."""

    list_display = [
        "title",
        "document_type",
        "related_policy_link",
        "status",
        "download_count",
        "generated_by",
        "created_at",
    ]
    list_filter = ["document_type", "status", "model_used", "created_at"]
    search_fields = ["title", "content", "related_policy__title"]
    readonly_fields = [
        "download_count",
        "generated_by",
        "created_at",
        "updated_at",
        "content_preview",
    ]
    date_hierarchy = "created_at"

    fieldsets = (
        (
            "Basic Information",
            {"fields": ("title", "document_type", "related_policy", "conversation")},
        ),
        (
            "Content",
            {"fields": ("content_preview", "content", "sections", "key_points")},
        ),
        (
            "Generation Details",
            {
                "fields": ("prompt_used", "model_used", "generation_parameters"),
                "classes": ("collapse",),
            },
        ),
        ("Review & Status", {"fields": ("status", "reviewed_by", "review_notes")}),
        (
            "Files & Downloads",
            {
                "fields": ("pdf_file", "word_file", "download_count"),
                "classes": ("collapse",),
            },
        ),
        (
            "Metadata",
            {
                "fields": ("generated_by", "created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )

    actions = ["approve_documents", "publish_documents", "archive_documents"]

    def related_policy_link(self, obj):
        if obj.related_policy:
            url = reverse(
                "admin:policy_tracking_policyrecommendation_change",
                args=[obj.related_policy.pk],
            )
            return format_html(
                '<a href="{}">{}</a>', url, obj.related_policy.title[:50]
            )
        return "-"

    related_policy_link.short_description = "Related Policy"

    def content_preview(self, obj):
        if obj.content:
            preview = (
                obj.content[:500] + "..." if len(obj.content) > 500 else obj.content
            )
            return format_html(
                '<div style="max-height: 200px; overflow-y: auto; white-space: pre-wrap;">{}</div>',
                preview,
            )
        return "No content"

    content_preview.short_description = "Content Preview"

    def approve_documents(self, request, queryset):
        queryset.update(status="approved", reviewed_by=request.user)
        self.message_user(request, f"{queryset.count()} documents approved.")

    approve_documents.short_description = "Approve selected documents"

    def publish_documents(self, request, queryset):
        queryset.update(status="published", reviewed_by=request.user)
        self.message_user(request, f"{queryset.count()} documents published.")

    publish_documents.short_description = "Publish selected documents"

    def archive_documents(self, request, queryset):
        queryset.update(status="archived")
        self.message_user(request, f"{queryset.count()} documents archived.")

    archive_documents.short_description = "Archive selected documents"


@admin.register(AIUsageMetrics)
class AIUsageMetricsAdmin(admin.ModelAdmin):
    """Admin interface for AI usage metrics."""

    list_display = [
        "user",
        "date",
        "conversations_started",
        "messages_sent",
        "insights_generated",
        "documents_created",
        "total_tokens_used",
    ]
    list_filter = ["date", "user"]
    search_fields = ["user__username", "user__email"]
    readonly_fields = ["created_at"]
    date_hierarchy = "date"

    fieldsets = (
        ("Basic Information", {"fields": ("user", "date")}),
        (
            "Usage Counts",
            {
                "fields": (
                    "conversations_started",
                    "messages_sent",
                    "insights_generated",
                    "documents_created",
                )
            },
        ),
        (
            "Feature Usage",
            {
                "fields": (
                    "policy_analysis_used",
                    "document_generation_used",
                    "cultural_guidance_used",
                    "evidence_review_used",
                )
            },
        ),
        (
            "Performance Metrics",
            {
                "fields": ("average_response_time", "total_tokens_used"),
                "classes": ("collapse",),
            },
        ),
        ("Metadata", {"fields": ("created_at",), "classes": ("collapse",)}),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("user")


@admin.register(AIOperation)
class AIOperationAdmin(admin.ModelAdmin):
    """Admin interface for AI operation logs."""

    list_display = [
        "created_at",
        "operation_type",
        "module",
        "user",
        "success_icon",
        "cached_icon",
        "tokens_used",
        "cost_display",
        "response_time_display",
        "model_used",
    ]
    list_filter = [
        "success",
        "cached",
        "operation_type",
        "module",
        "model_used",
        "created_at",
    ]
    search_fields = [
        "user__username",
        "user__email",
        "operation_type",
        "module",
        "error",
    ]
    readonly_fields = [
        "id",
        "created_at",
        "prompt_hash",
        "tokens_used",
        "cost",
        "response_time",
    ]
    date_hierarchy = "created_at"

    fieldsets = (
        (
            "Basic Information",
            {"fields": ("id", "operation_type", "module", "user", "created_at")},
        ),
        (
            "Technical Details",
            {
                "fields": ("model_used", "prompt_hash", "cached"),
            },
        ),
        (
            "Performance Metrics",
            {
                "fields": ("tokens_used", "cost", "response_time"),
            },
        ),
        (
            "Status",
            {
                "fields": ("success", "error", "error_category"),
            },
        ),
    )

    def success_icon(self, obj):
        if obj.success:
            return format_html(
                '<span style="color: green; font-size: 16px;">✓</span>'
            )
        return format_html('<span style="color: red; font-size: 16px;">✗</span>')

    success_icon.short_description = "Success"

    def cached_icon(self, obj):
        if obj.cached:
            return format_html(
                '<span style="color: blue;" title="Cached response">⚡</span>'
            )
        return "-"

    cached_icon.short_description = "Cache"

    def cost_display(self, obj):
        return f"${obj.cost:.4f}"

    cost_display.short_description = "Cost"
    cost_display.admin_order_field = "cost"

    def response_time_display(self, obj):
        return f"{obj.response_time:.2f}s"

    response_time_display.short_description = "Response Time"
    response_time_display.admin_order_field = "response_time"

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("user")

    # Add custom actions
    actions = ["export_to_csv"]

    def export_to_csv(self, request, queryset):
        import csv
        from django.http import HttpResponse

        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="ai_operations.csv"'

        writer = csv.writer(response)
        writer.writerow(
            [
                "Date",
                "Operation Type",
                "Module",
                "User",
                "Success",
                "Cached",
                "Tokens",
                "Cost",
                "Response Time",
                "Model",
            ]
        )

        for op in queryset:
            writer.writerow(
                [
                    op.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                    op.operation_type,
                    op.module,
                    op.user.username if op.user else "Anonymous",
                    "Yes" if op.success else "No",
                    "Yes" if op.cached else "No",
                    op.tokens_used,
                    f"${op.cost:.4f}",
                    f"{op.response_time:.2f}s",
                    op.model_used,
                ]
            )

        return response

    export_to_csv.short_description = "Export selected operations to CSV"

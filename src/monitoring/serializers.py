"""API serializers for Monitoring & Evaluation resources."""

from rest_framework import serializers

from common.models import WorkItem
from common.serializers import WorkItemSerializer

from .models import (
    MonitoringEntry,
    MonitoringEntryFunding,
    MonitoringEntryWorkflowStage,
    MonitoringEntryWorkflowDocument,
    MonitoringUpdate,
)


class MonitoringEntryFundingSerializer(serializers.ModelSerializer):
    """Serialize detailed funding flow entries."""

    tranche_type_display = serializers.CharField(
        source="get_tranche_type_display", read_only=True
    )
    funding_source_display = serializers.CharField(
        source="get_funding_source_display", read_only=True
    )

    class Meta:
        model = MonitoringEntryFunding
        fields = [
            "id",
            "tranche_type",
            "tranche_type_display",
            "amount",
            "funding_source",
            "funding_source_display",
            "funding_source_other",
            "scheduled_date",
            "remarks",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "created_at",
            "updated_at",
            "tranche_type_display",
            "funding_source_display",
        ]


class MonitoringEntryWorkflowDocumentSerializer(serializers.ModelSerializer):
    """Serialize workflow stage documents."""

    document_type_display = serializers.CharField(
        source="get_document_type_display", read_only=True
    )
    uploaded_by_name = serializers.CharField(
        source="uploaded_by.get_full_name", read_only=True
    )
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = MonitoringEntryWorkflowDocument
        fields = [
            "id",
            "title",
            "document_type",
            "document_type_display",
            "file",
            "file_url",
            "file_size",
            "description",
            "uploaded_by",
            "uploaded_by_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "document_type_display",
            "file_url",
            "file_size",
            "uploaded_by",
            "uploaded_by_name",
            "created_at",
            "updated_at",
        ]

    def get_file_url(self, obj):
        """Return full URL for file download."""
        if obj.file:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(obj.file.url)
            return obj.file.url
        return None


class MonitoringEntryWorkflowStageSerializer(serializers.ModelSerializer):
    """Serialize workflow stages and status updates."""

    stage_display = serializers.CharField(source="get_stage_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    owner_team_name = serializers.CharField(source="owner_team.name", read_only=True)
    owner_organization_name = serializers.CharField(
        source="owner_organization.name", read_only=True
    )
    documents = MonitoringEntryWorkflowDocumentSerializer(many=True, read_only=True)

    class Meta:
        model = MonitoringEntryWorkflowStage
        fields = [
            "id",
            "stage",
            "stage_display",
            "status",
            "status_display",
            "owner_team",
            "owner_team_name",
            "owner_organization",
            "owner_organization_name",
            "due_date",
            "completed_at",
            "notes",
            "documents",
            "updated_at",
        ]
        read_only_fields = [
            "stage_display",
            "status_display",
            "owner_team_name",
            "owner_organization_name",
            "documents",
            "updated_at",
        ]


class MonitoringEntryWorkItemSerializer(WorkItemSerializer):
    """Serialize WorkItem records linked to monitoring entries.

    This serializer extends WorkItemSerializer with monitoring-specific fields.
    It replaces the legacy MonitoringEntryStaffTaskSerializer.
    """

    # Add monitoring-specific fields from task_data JSON
    domain = serializers.SerializerMethodField()
    estimated_hours = serializers.SerializerMethodField()
    actual_hours = serializers.SerializerMethodField()

    class Meta(WorkItemSerializer.Meta):
        fields = WorkItemSerializer.Meta.fields + [
            "domain",
            "estimated_hours",
            "actual_hours",
        ]
        read_only_fields = WorkItemSerializer.Meta.read_only_fields + [
            "domain",
            "estimated_hours",
            "actual_hours",
        ]

    def get_domain(self, obj):
        """Extract domain from task_data JSON field."""
        return obj.task_data.get("domain", "general") if obj.task_data else "general"

    def get_estimated_hours(self, obj):
        """Extract estimated_hours from task_data JSON field."""
        return obj.task_data.get("estimated_hours") if obj.task_data else None

    def get_actual_hours(self, obj):
        """Extract actual_hours from task_data JSON field."""
        return obj.task_data.get("actual_hours") if obj.task_data else None


# Backward compatibility alias
MonitoringEntryStaffTaskSerializer = MonitoringEntryWorkItemSerializer


class MonitoringUpdateSerializer(serializers.ModelSerializer):
    """Serialize monitoring updates with author metadata."""

    created_by_name = serializers.CharField(
        source="created_by.get_full_name", read_only=True
    )
    update_type_display = serializers.CharField(
        source="get_update_type_display", read_only=True
    )
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    request_status_display = serializers.CharField(
        source="get_request_status_display", read_only=True
    )

    class Meta:
        model = MonitoringUpdate
        fields = [
            "id",
            "entry",
            "update_type",
            "update_type_display",
            "status",
            "status_display",
            "request_status",
            "request_status_display",
            "progress",
            "notes",
            "next_steps",
            "follow_up_date",
            "created_by",
            "created_by_name",
            "created_at",
        ]
        read_only_fields = [
            "created_by",
            "created_by_name",
            "created_at",
            "status_display",
            "request_status_display",
            "update_type_display",
        ]


class MonitoringEntrySerializer(serializers.ModelSerializer):
    """Serialize monitoring entries with related resource links."""

    category_display = serializers.CharField(
        source="get_category_display", read_only=True
    )
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    request_status_display = serializers.CharField(
        source="get_request_status_display", read_only=True
    )
    priority_display = serializers.CharField(
        source="get_priority_display", read_only=True
    )
    lead_organization_name = serializers.CharField(
        source="lead_organization.name", read_only=True
    )
    submitted_by_community_name = serializers.CharField(
        source="submitted_by_community.name", read_only=True
    )
    submitted_to_organization_name = serializers.CharField(
        source="submitted_to_organization.name", read_only=True
    )
    supporting_organizations = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field="name",
    )
    communities = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field="name",
    )
    updates = MonitoringUpdateSerializer(many=True, read_only=True)
    funding_flows = MonitoringEntryFundingSerializer(many=True, read_only=True)
    workflow_stages = MonitoringEntryWorkflowStageSerializer(many=True, read_only=True)
    task_assignments = serializers.SerializerMethodField()
    sector_display = serializers.CharField(source="get_sector_display", read_only=True)
    appropriation_class_display = serializers.CharField(
        source="get_appropriation_class_display",
        read_only=True,
    )
    funding_source_display = serializers.CharField(
        source="get_funding_source_display", read_only=True
    )

    class Meta:
        model = MonitoringEntry
        fields = [
            "id",
            "title",
            "category",
            "category_display",
            "summary",
            "plan_year",
            "fiscal_year",
            "sector",
            "sector_display",
            "appropriation_class",
            "appropriation_class_display",
            "funding_source",
            "funding_source_display",
            "funding_source_other",
            "program_code",
            "plan_reference",
            "goal_alignment",
            "moral_governance_pillar",
            "compliance_gad",
            "compliance_ccet",
            "benefits_indigenous_peoples",
            "supports_peace_agenda",
            "supports_sdg",
            "budget_ceiling",
            "status",
            "status_display",
            "request_status",
            "request_status_display",
            "priority",
            "priority_display",
            "progress",
            "lead_organization",
            "lead_organization_name",
            "supporting_organizations",
            "oobc_unit",
            "submitted_by_community",
            "submitted_by_community_name",
            "communities",
            "submitted_to_organization",
            "submitted_to_organization_name",
            "related_assessment",
            "related_policy",
            "start_date",
            "target_end_date",
            "actual_end_date",
            "next_milestone_date",
            "milestone_dates",
            "budget_allocation",
            "budget_currency",
            "budget_obc_allocation",
            "cost_per_beneficiary",
            "cost_effectiveness_rating",
            "outcome_framework",
            "outcome_indicators",
            "standard_outcome_indicators",
            "accomplishments",
            "challenges",
            "support_required",
            "follow_up_actions",
            "last_status_update",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
            "updates",
            "funding_flows",
            "workflow_stages",
            "task_assignments",
        ]
        read_only_fields = [
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
            "category_display",
            "status_display",
            "request_status_display",
            "priority_display",
            "lead_organization_name",
            "submitted_by_community_name",
            "submitted_to_organization_name",
            "sector_display",
            "appropriation_class_display",
            "funding_source_display",
        ]

    def get_task_assignments(self, obj):
        """Get WorkItem tasks linked to this monitoring entry.

        Links WorkItems to MonitoringEntry via GenericForeignKey (content_type + object_id).
        Filters to tasks with work_type='task' and domain='monitoring' in task_data.
        """
        from django.contrib.contenttypes.models import ContentType

        # Get ContentType for MonitoringEntry
        ct = ContentType.objects.get_for_model(MonitoringEntry)

        # Find WorkItems linked via GenericForeignKey
        tasks = WorkItem.objects.filter(
            content_type=ct,
            object_id=obj.id,
            work_type__in=[WorkItem.WORK_TYPE_TASK, WorkItem.WORK_TYPE_SUBTASK],
        ).order_by("due_date", "title")

        # Further filter to monitoring domain tasks
        # (domain is stored in task_data JSON field)
        monitoring_tasks = [
            task
            for task in tasks
            if task.task_data and task.task_data.get("domain") == "monitoring"
        ]

        serializer = MonitoringEntryWorkItemSerializer(
            monitoring_tasks, many=True, context=self.context
        )
        return serializer.data


# ==============================================================================
# Phase 3: PPA WorkItem Integration Serializers
# ==============================================================================


class WorkItemIntegrationSerializer(serializers.Serializer):
    """
    Serializer for WorkItem execution project creation and management.

    This serializer handles the creation of WorkItem hierarchies from PPA templates
    and provides data for tracking PPA execution progress.

    Used by: enable_workitem_tracking API endpoint
    """

    structure_template = serializers.ChoiceField(
        choices=["program", "activity", "milestone", "minimal"],
        default="activity",
        help_text="Template for WorkItem hierarchy structure",
    )

    # Read-only fields returned after creation
    execution_project_id = serializers.UUIDField(read_only=True)
    execution_project_title = serializers.CharField(read_only=True)
    work_items_created = serializers.IntegerField(read_only=True)
    structure_summary = serializers.DictField(read_only=True)


class BudgetAllocationNodeSerializer(serializers.Serializer):
    """
    Serializer for a single node in the budget allocation tree.

    Represents a WorkItem with its budget allocation and children nodes.
    Used recursively to build a nested tree structure.
    """

    id = serializers.UUIDField(help_text="WorkItem UUID")
    title = serializers.CharField(help_text="WorkItem title")
    work_type = serializers.CharField(help_text="WorkItem type (project/task/subtask)")
    allocated_budget = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        allow_null=True,
        help_text="Budget allocated to this WorkItem",
    )
    budget_currency = serializers.CharField(
        max_length=3, default="PHP", help_text="Currency code"
    )
    parent_id = serializers.UUIDField(
        allow_null=True, help_text="Parent WorkItem UUID (null for root)"
    )
    children = serializers.SerializerMethodField(
        help_text="Nested child WorkItems (recursive)"
    )

    def get_children(self, obj):
        """Recursively serialize child nodes."""
        children = obj.get("children", [])
        return BudgetAllocationNodeSerializer(children, many=True).data


class BudgetAllocationTreeSerializer(serializers.Serializer):
    """
    Serializer for the complete budget allocation tree.

    Returns a hierarchical structure showing how budget flows from PPA
    through the WorkItem hierarchy (Program → Activities → Tasks).

    Used by: budget_allocation_tree API endpoint
    """

    ppa_id = serializers.UUIDField(help_text="MonitoringEntry UUID")
    ppa_title = serializers.CharField(help_text="PPA title")
    total_budget = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        help_text="Total PPA budget allocation",
    )
    allocated_budget = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        help_text="Sum of allocated budget across all WorkItems",
    )
    unallocated_budget = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        help_text="Remaining unallocated budget",
    )
    budget_currency = serializers.CharField(
        max_length=3, default="PHP", help_text="Currency code"
    )
    tree = BudgetAllocationNodeSerializer(
        many=True, help_text="Root-level WorkItems with nested children"
    )


class BudgetDistributionRequestSerializer(serializers.Serializer):
    """
    Serializer for budget distribution requests.

    Validates and processes budget distribution across WorkItems using
    equal, weighted, or manual allocation methods.

    Used by: distribute_budget API endpoint
    """

    method = serializers.ChoiceField(
        choices=["equal", "weighted", "manual"],
        required=True,
        help_text="Distribution method: equal, weighted, or manual",
    )

    # For weighted distribution
    weights = serializers.DictField(
        child=serializers.FloatField(min_value=0.0, max_value=1.0),
        required=False,
        allow_null=True,
        help_text="Mapping of work_item_id (UUID) to weight (0.0-1.0). "
        "Required for 'weighted' method. Must sum to 1.0.",
    )

    # For manual distribution
    allocations = serializers.DictField(
        child=serializers.DecimalField(max_digits=15, decimal_places=2, min_value=0),
        required=False,
        allow_null=True,
        help_text="Mapping of work_item_id (UUID) to specific amount. "
        "Required for 'manual' method. Must sum to PPA budget.",
    )

    def validate(self, data):
        """Cross-field validation for distribution method and data."""
        method = data.get("method")

        if method == "weighted":
            if not data.get("weights"):
                raise serializers.ValidationError(
                    {"weights": "Weights are required for 'weighted' distribution method"}
                )

            # Validate weights sum to 1.0 (with tolerance)
            weight_sum = sum(data["weights"].values())
            if abs(weight_sum - 1.0) > 0.0001:
                raise serializers.ValidationError(
                    {"weights": f"Weights must sum to 1.0 (current sum: {weight_sum})"}
                )

        elif method == "manual":
            if not data.get("allocations"):
                raise serializers.ValidationError(
                    {
                        "allocations": "Allocations are required for 'manual' distribution method"
                    }
                )

        elif method == "equal":
            # No additional data required for equal distribution
            pass

        return data


class BudgetDistributionResponseSerializer(serializers.Serializer):
    """
    Serializer for budget distribution results.

    Returns summary of budget distribution operation including
    number of work items updated and distribution details.
    """

    success = serializers.BooleanField(default=True)
    message = serializers.CharField()
    work_items_updated = serializers.IntegerField(help_text="Number of WorkItems updated")
    distribution = serializers.DictField(
        child=serializers.DecimalField(max_digits=15, decimal_places=2),
        help_text="Mapping of work_item_id to allocated amount",
    )
    total_allocated = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        help_text="Total budget allocated across all WorkItems",
    )


class WorkItemSyncStatusSerializer(serializers.Serializer):
    """
    Serializer for WorkItem synchronization status.

    Returns status of progress and status sync between WorkItems and PPA.

    Used by: sync_from_workitem API endpoint
    """

    success = serializers.BooleanField(default=True)
    message = serializers.CharField()
    previous_progress = serializers.IntegerField(
        help_text="PPA progress before sync (0-100)"
    )
    updated_progress = serializers.IntegerField(
        help_text="PPA progress after sync (0-100)"
    )
    previous_status = serializers.CharField(help_text="PPA status before sync")
    updated_status = serializers.CharField(help_text="PPA status after sync")
    work_items_analyzed = serializers.IntegerField(
        help_text="Number of WorkItems analyzed for sync"
    )
    sync_timestamp = serializers.DateTimeField(help_text="Time of synchronization")

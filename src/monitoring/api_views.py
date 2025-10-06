"""REST API viewsets for Monitoring & Evaluation data."""

from decimal import Decimal
from django.db.models import Prefetch, Sum
from django.utils import timezone
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from .models import MonitoringEntry, MonitoringUpdate
from .serializers import (
    MonitoringEntrySerializer,
    MonitoringUpdateSerializer,
    WorkItemIntegrationSerializer,
    BudgetAllocationTreeSerializer,
    BudgetDistributionRequestSerializer,
    BudgetDistributionResponseSerializer,
    WorkItemSyncStatusSerializer,
)
from .services.budget_distribution import BudgetDistributionService


class MonitoringEntryViewSet(viewsets.ModelViewSet):
    """CRUD operations for monitoring entries."""

    serializer_class = MonitoringEntrySerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    queryset = MonitoringEntry.objects.all()
    filterset_fields = {
        "category": ["exact"],
        "status": ["exact"],
        "request_status": ["exact"],
        "priority": ["exact"],
        "lead_organization": ["exact"],
        "submitted_by_community": ["exact"],
        "submitted_to_organization": ["exact"],
    }
    search_fields = ["title", "summary", "oobc_unit", "support_required"]
    ordering_fields = [
        "created_at",
        "updated_at",
        "title",
        "priority",
        "progress",
        "target_end_date",
    ]
    ordering = ["-updated_at"]

    def get_queryset(self):
        return (
            MonitoringEntry.objects.all()
            .select_related(
                "lead_organization",
                "submitted_by_community",
                "submitted_to_organization",
                "related_assessment",
                "related_event",
                "related_policy",
                "created_by",
                "updated_by",
            )
            .prefetch_related(
                "supporting_organizations",
                "communities",
                Prefetch(
                    "updates",
                    queryset=MonitoringUpdate.objects.select_related("created_by"),
                ),
            )
        )

    def perform_create(self, serializer):
        serializer.save(
            created_by=self.request.user,
            updated_by=self.request.user,
        )

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    # ==============================================================================
    # Phase 3: PPA WorkItem Integration API Endpoints
    # ==============================================================================

    @action(
        detail=True,
        methods=["post"],
        url_path="enable-workitem-tracking",
        permission_classes=[permissions.IsAuthenticated],
    )
    def enable_workitem_tracking(self, request, pk=None):
        """
        Enable WorkItem tracking for a PPA by creating an execution project.

        POST /api/monitoring/entries/{id}/enable-workitem-tracking/

        Request Body:
            {
                "structure_template": "program" | "activity" | "milestone" | "minimal"
            }

        Response:
            {
                "structure_template": "activity",
                "execution_project_id": "uuid",
                "execution_project_title": "PPA Title - Execution",
                "work_items_created": 5,
                "structure_summary": {
                    "project": 1,
                    "tasks": 3,
                    "subtasks": 1
                }
            }

        Validations:
            - PPA must have approval_status >= 'technical_review'
            - PPA must not already have an execution project
            - structure_template must be valid choice
        """
        ppa = self.get_object()

        # Validate request data
        serializer = WorkItemIntegrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        structure_template = serializer.validated_data.get(
            "structure_template", "activity"
        )

        # Validate PPA approval status
        if ppa.approval_status not in [
            "technical_review",
            "budget_approved",
            "executive_approved",
        ]:
            return Response(
                {
                    "error": "PPA must be in technical review or approved status to enable WorkItem tracking",
                    "current_status": ppa.approval_status,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check if execution project already exists
        if hasattr(ppa, "execution_project") and ppa.execution_project:
            return Response(
                {
                    "error": "WorkItem tracking already enabled for this PPA",
                    "execution_project_id": str(ppa.execution_project.id),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Create execution project
        try:
            execution_project = ppa.create_execution_project(
                structure_template=structure_template, created_by=request.user
            )
        except Exception as e:
            return Response(
                {"error": f"Failed to create execution project: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # Count work items created
        work_items = execution_project.get_descendants(include_self=True)
        work_items_count = work_items.count()

        # Build structure summary
        structure_summary = {
            "project": work_items.filter(work_type="project").count(),
            "tasks": work_items.filter(work_type="task").count(),
            "subtasks": work_items.filter(work_type="subtask").count(),
        }

        response_data = {
            "structure_template": structure_template,
            "execution_project_id": str(execution_project.id),
            "execution_project_title": execution_project.title,
            "work_items_created": work_items_count,
            "structure_summary": structure_summary,
        }

        return Response(response_data, status=status.HTTP_201_CREATED)

    @action(
        detail=True,
        methods=["get"],
        url_path="budget-allocation-tree",
        permission_classes=[permissions.IsAuthenticated],
    )
    def budget_allocation_tree(self, request, pk=None):
        """
        Retrieve budget allocation tree for a PPA.

        GET /api/monitoring/entries/{id}/budget-allocation-tree/

        Response:
            {
                "ppa_id": "uuid",
                "ppa_title": "PPA Title",
                "total_budget": "100000.00",
                "allocated_budget": "85000.00",
                "unallocated_budget": "15000.00",
                "budget_currency": "PHP",
                "tree": [
                    {
                        "id": "uuid",
                        "title": "Program Phase 1",
                        "work_type": "project",
                        "allocated_budget": "85000.00",
                        "budget_currency": "PHP",
                        "parent_id": null,
                        "children": [...]
                    }
                ]
            }

        Validations:
            - PPA must have execution project enabled
            - PPA must have budget_allocation set
        """
        ppa = self.get_object()

        # Validate PPA has execution project
        if not hasattr(ppa, "execution_project") or not ppa.execution_project:
            return Response(
                {"error": "WorkItem tracking not enabled for this PPA"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validate PPA has budget
        if not ppa.budget_allocation:
            return Response(
                {"error": "PPA has no budget allocation set"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Get budget allocation tree
        try:
            tree_data = ppa.get_budget_allocation_tree()
        except Exception as e:
            return Response(
                {"error": f"Failed to retrieve budget tree: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # Calculate totals
        total_budget = Decimal(str(ppa.budget_allocation))
        allocated_budget = (
            ppa.work_items.aggregate(total=Sum("allocated_budget"))["total"]
            or Decimal("0.00")
        )
        unallocated_budget = total_budget - allocated_budget

        response_data = {
            "ppa_id": str(ppa.id),
            "ppa_title": ppa.title,
            "total_budget": str(total_budget),
            "allocated_budget": str(allocated_budget),
            "unallocated_budget": str(unallocated_budget),
            "budget_currency": ppa.budget_currency or "PHP",
            "tree": tree_data,
        }

        serializer = BudgetAllocationTreeSerializer(data=response_data)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.validated_data, status=status.HTTP_200_OK)

    @action(
        detail=True,
        methods=["post"],
        url_path="distribute-budget",
        permission_classes=[permissions.IsAuthenticated],
    )
    def distribute_budget(self, request, pk=None):
        """
        Distribute PPA budget across WorkItems.

        POST /api/monitoring/entries/{id}/distribute-budget/

        Request Body (Equal Distribution):
            {
                "method": "equal"
            }

        Request Body (Weighted Distribution):
            {
                "method": "weighted",
                "weights": {
                    "work_item_uuid_1": 0.5,
                    "work_item_uuid_2": 0.3,
                    "work_item_uuid_3": 0.2
                }
            }

        Request Body (Manual Distribution):
            {
                "method": "manual",
                "allocations": {
                    "work_item_uuid_1": "50000.00",
                    "work_item_uuid_2": "30000.00",
                    "work_item_uuid_3": "20000.00"
                }
            }

        Response:
            {
                "success": true,
                "message": "Budget distributed successfully using equal method",
                "work_items_updated": 3,
                "distribution": {
                    "work_item_uuid_1": "33333.34",
                    "work_item_uuid_2": "33333.33",
                    "work_item_uuid_3": "33333.33"
                },
                "total_allocated": "100000.00"
            }

        Validations:
            - PPA must have execution project enabled
            - PPA must have budget_allocation set
            - Method must be: equal, weighted, or manual
            - For weighted: weights must sum to 1.0
            - For manual: allocations must sum to PPA budget
        """
        ppa = self.get_object()

        # Validate request data
        serializer = BudgetDistributionRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        method = serializer.validated_data["method"]
        weights = serializer.validated_data.get("weights")
        allocations = serializer.validated_data.get("allocations")

        # Validate PPA has execution project
        if not hasattr(ppa, "execution_project") or not ppa.execution_project:
            return Response(
                {"error": "WorkItem tracking not enabled for this PPA"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validate PPA has budget
        if not ppa.budget_allocation:
            return Response(
                {"error": "PPA has no budget allocation set"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Get all work items for this PPA
        work_items = list(ppa.work_items.all())

        if not work_items:
            return Response(
                {"error": "No WorkItems found for this PPA"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Distribute budget based on method
        try:
            if method == "equal":
                distribution = BudgetDistributionService.distribute_equal(
                    ppa, work_items
                )
                message = "Budget distributed equally across all WorkItems"

            elif method == "weighted":
                # Convert string UUIDs to UUID objects
                from uuid import UUID

                weights_uuid = {UUID(k): v for k, v in weights.items()}
                distribution = BudgetDistributionService.distribute_weighted(
                    ppa, work_items, weights_uuid
                )
                message = "Budget distributed using weighted allocation"

            elif method == "manual":
                # Convert string UUIDs to UUID objects
                from uuid import UUID

                allocations_uuid = {
                    UUID(k): Decimal(str(v)) for k, v in allocations.items()
                }
                distribution = BudgetDistributionService.distribute_manual(
                    ppa, allocations_uuid
                )
                message = "Budget distributed using manual allocations"

            else:
                return Response(
                    {"error": f"Invalid distribution method: {method}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Apply distribution
            work_items_updated = BudgetDistributionService.apply_distribution(
                ppa, distribution
            )

        except Exception as e:
            return Response(
                {"error": f"Budget distribution failed: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Calculate total allocated
        total_allocated = sum(distribution.values())

        # Convert UUIDs to strings for JSON response
        distribution_str = {str(k): str(v) for k, v in distribution.items()}

        response_data = {
            "success": True,
            "message": message,
            "work_items_updated": work_items_updated,
            "distribution": distribution_str,
            "total_allocated": str(total_allocated),
        }

        response_serializer = BudgetDistributionResponseSerializer(data=response_data)
        response_serializer.is_valid(raise_exception=True)

        return Response(response_serializer.validated_data, status=status.HTTP_200_OK)

    @action(
        detail=True,
        methods=["post"],
        url_path="sync-from-workitem",
        permission_classes=[permissions.IsAuthenticated],
    )
    def sync_from_workitem(self, request, pk=None):
        """
        Synchronize PPA progress and status from WorkItem hierarchy.

        POST /api/monitoring/entries/{id}/sync-from-workitem/

        Response:
            {
                "success": true,
                "message": "Progress and status synchronized successfully",
                "previous_progress": 45,
                "updated_progress": 67,
                "previous_status": "ongoing",
                "updated_status": "ongoing",
                "work_items_analyzed": 12,
                "sync_timestamp": "2025-10-06T10:30:00Z"
            }

        Validations:
            - PPA must have execution project enabled
        """
        ppa = self.get_object()

        # Validate PPA has execution project
        if not hasattr(ppa, "execution_project") or not ppa.execution_project:
            return Response(
                {"error": "WorkItem tracking not enabled for this PPA"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Store previous values
        previous_progress = ppa.progress
        previous_status = ppa.status

        # Sync progress from WorkItems
        try:
            updated_progress = ppa.sync_progress_from_workitem()
            updated_status = ppa.sync_status_from_workitem()
        except Exception as e:
            return Response(
                {"error": f"Synchronization failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # Count work items analyzed
        work_items_count = ppa.work_items.count()

        response_data = {
            "success": True,
            "message": "Progress and status synchronized successfully",
            "previous_progress": previous_progress,
            "updated_progress": updated_progress,
            "previous_status": previous_status,
            "updated_status": updated_status,
            "work_items_analyzed": work_items_count,
            "sync_timestamp": timezone.now(),
        }

        serializer = WorkItemSyncStatusSerializer(data=response_data)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class MonitoringUpdateViewSet(viewsets.ModelViewSet):
    """CRUD operations for monitoring updates."""

    serializer_class = MonitoringUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    queryset = MonitoringUpdate.objects.all()
    filterset_fields = {
        "entry": ["exact"],
        "update_type": ["exact"],
        "status": ["exact"],
        "request_status": ["exact"],
    }
    search_fields = ["notes", "next_steps"]
    ordering_fields = ["created_at", "follow_up_date"]
    ordering = ["-created_at"]

    def get_queryset(self):
        return MonitoringUpdate.objects.select_related("entry", "created_by")

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(created_by=self.request.user)

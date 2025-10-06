from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import (
    # ActionItem,  # DEPRECATED - replaced by WorkItem
    Communication,
    CommunicationSchedule,
    CommunicationTemplate,
    ConsultationFeedback,
    EngagementFacilitator,
    EngagementTracking,
    # Event,  # DEPRECATED - replaced by WorkItem
    # EventDocument,  # DEPRECATED - related to Event
    # EventParticipant,  # DEPRECATED - related to Event
    Organization,
    OrganizationContact,
    Partnership,
    PartnershipDocument,
    PartnershipMilestone,
    PartnershipSignatory,
    StakeholderEngagement,
    StakeholderEngagementType,
)
from .serializers import (
    # ActionItemSerializer,  # DEPRECATED
    CommunicationScheduleSerializer,
    CommunicationSerializer,
    CommunicationTemplateSerializer,
    ConsultationFeedbackSerializer,
    EngagementFacilitatorSerializer,
    EngagementTrackingSerializer,
    # EventDocumentSerializer,  # DEPRECATED
    # EventListSerializer,  # DEPRECATED
    # EventParticipantSerializer,  # DEPRECATED
    # EventSerializer,  # DEPRECATED
    OrganizationContactSerializer,
    OrganizationSerializer,
    PartnershipDocumentSerializer,
    PartnershipListSerializer,
    PartnershipMilestoneSerializer,
    PartnershipSerializer,
    PartnershipSignatorySerializer,
    StakeholderEngagementSerializer,
    StakeholderEngagementTypeSerializer,
)


class StakeholderEngagementTypeViewSet(viewsets.ModelViewSet):
    """ViewSet for StakeholderEngagementType model."""

    queryset = StakeholderEngagementType.objects.all()
    serializer_class = StakeholderEngagementTypeSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["is_active"]
    search_fields = ["name", "description"]
    ordering = ["name"]


class StakeholderEngagementViewSet(viewsets.ModelViewSet):
    """ViewSet for StakeholderEngagement model."""

    queryset = StakeholderEngagement.objects.all().select_related(
        "engagement_type", "community", "lead_facilitator"
    )
    serializer_class = StakeholderEngagementSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["engagement_type", "community", "status", "outcome"]
    search_fields = ["title", "description", "community__name"]
    ordering_fields = ["title", "date", "created_at"]
    ordering = ["-date"]


class OrganizationViewSet(viewsets.ModelViewSet):
    """ViewSet for Organization model."""

    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["organization_type", "is_active"]
    search_fields = ["name", "acronym", "description"]
    ordering_fields = ["name", "created_at"]
    ordering = ["name"]

    @action(detail=True, methods=["get"])
    def contacts(self, request, pk=None):
        """Get contacts for this organization."""
        organization = self.get_object()
        contacts = organization.contacts.filter(is_active=True)
        serializer = OrganizationContactSerializer(contacts, many=True)
        return Response(serializer.data)


class CommunicationTemplateViewSet(viewsets.ModelViewSet):
    """ViewSet for CommunicationTemplate model."""

    queryset = CommunicationTemplate.objects.all()
    serializer_class = CommunicationTemplateSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["template_type", "is_active"]
    search_fields = ["name", "subject_template", "body_template"]
    ordering = ["name"]


class CommunicationViewSet(viewsets.ModelViewSet):
    """ViewSet for Communication model."""

    queryset = Communication.objects.all().select_related("template", "sender")
    serializer_class = CommunicationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["communication_type", "status", "sender", "template"]
    search_fields = ["subject", "message", "sender__username"]
    ordering_fields = ["subject", "sent_date", "created_at"]
    ordering = ["-sent_date"]


# ⚠️ DEPRECATED: Event-related ViewSets disabled - Event model is abstract
# Event, EventParticipant, and ActionItem models are deprecated and replaced by WorkItem
# Use: WorkItemViewSet from common.api for unified work item management
# See: docs/refactor/WORKITEM_MIGRATION_COMPLETE.md

# class EventViewSet(viewsets.ModelViewSet):
#     """ViewSet for Event model - DEPRECATED."""
#
#     queryset = Event.objects.all().select_related("community", "organizer")
#     permission_classes = [permissions.IsAuthenticated]
#     filter_backends = [
#         DjangoFilterBackend,
#         filters.SearchFilter,
#         filters.OrderingFilter,
#     ]
#     filterset_fields = ["event_type", "status", "community", "is_virtual"]
#     search_fields = ["title", "description", "community__name"]
#     ordering_fields = ["title", "planned_date", "created_at"]
#     ordering = ["-planned_date"]
#
#     def get_serializer_class(self):
#         if self.action == "list":
#             return EventListSerializer
#         return EventSerializer
#
#     @action(detail=True, methods=["get"])
#     def participants(self, request, pk=None):
#         """Get participants for this event."""
#         event = self.get_object()
#         participants = event.participants.all()
#         serializer = EventParticipantSerializer(participants, many=True)
#         return Response(serializer.data)
#
#     @action(detail=True, methods=["get"])
#     def action_items(self, request, pk=None):
#         """Get action items for this event."""
#         event = self.get_object()
#         action_items = event.action_items.all()
#         serializer = ActionItemSerializer(action_items, many=True)
#         return Response(serializer.data)


# class EventParticipantViewSet(viewsets.ModelViewSet):
#     """ViewSet for EventParticipant model - DEPRECATED."""
#
#     queryset = EventParticipant.objects.all().select_related("event", "participant")
#     serializer_class = EventParticipantSerializer
#     permission_classes = [permissions.IsAuthenticated]
#     filter_backends = [
#         DjangoFilterBackend,
#         filters.SearchFilter,
#         filters.OrderingFilter,
#     ]
#     filterset_fields = [
#         "event",
#         "response_status",
#         "attendance_status",
#         "participant_type",
#     ]
#     search_fields = ["participant__username", "event__title"]
#     ordering = ["event__planned_date", "participant__username"]


# class ActionItemViewSet(viewsets.ModelViewSet):
#     """ViewSet for ActionItem model - DEPRECATED."""
#
#     queryset = ActionItem.objects.all().select_related("event", "assigned_to")
#     serializer_class = ActionItemSerializer
#     permission_classes = [permissions.IsAuthenticated]
#     filter_backends = [
#         DjangoFilterBackend,
#         filters.SearchFilter,
#         filters.OrderingFilter,
#     ]
#     filterset_fields = ["event", "assigned_to", "status", "priority"]
#     search_fields = ["title", "description", "assigned_to__username"]
#     ordering_fields = ["title", "due_date", "priority", "created_at"]
#     ordering = ["due_date", "-priority"]


class PartnershipViewSet(viewsets.ModelViewSet):
    """ViewSet for Partnership model."""

    queryset = Partnership.objects.all().select_related("lead_organization")
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["partnership_type", "status", "lead_organization", "is_active"]
    search_fields = ["title", "description", "lead_organization__name"]
    ordering_fields = ["title", "start_date", "created_at"]
    ordering = ["-start_date"]

    def get_serializer_class(self):
        if self.action == "list":
            return PartnershipListSerializer
        return PartnershipSerializer

    @action(detail=True, methods=["get"])
    def signatories(self, request, pk=None):
        """Get signatories for this partnership."""
        partnership = self.get_object()
        signatories = partnership.signatories.all()
        serializer = PartnershipSignatorySerializer(signatories, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def milestones(self, request, pk=None):
        """Get milestones for this partnership."""
        partnership = self.get_object()
        milestones = partnership.milestones.all()
        serializer = PartnershipMilestoneSerializer(milestones, many=True)
        return Response(serializer.data)


class PartnershipSignatoryViewSet(viewsets.ModelViewSet):
    """ViewSet for PartnershipSignatory model."""

    queryset = PartnershipSignatory.objects.all().select_related(
        "partnership", "organization"
    )
    serializer_class = PartnershipSignatorySerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["partnership", "organization", "role", "is_active"]
    search_fields = ["organization__name", "signatory_name"]
    ordering = ["partnership__title", "organization__name"]


class PartnershipMilestoneViewSet(viewsets.ModelViewSet):
    """ViewSet for PartnershipMilestone model."""

    queryset = PartnershipMilestone.objects.all().select_related("partnership")
    serializer_class = PartnershipMilestoneSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["partnership", "status", "milestone_type"]
    search_fields = ["title", "description"]
    ordering_fields = ["title", "target_date", "created_at"]
    ordering = ["target_date"]


# Additional ViewSets for supporting models
class EngagementFacilitatorViewSet(viewsets.ModelViewSet):
    queryset = EngagementFacilitator.objects.all().select_related("engagement", "user")
    serializer_class = EngagementFacilitatorSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["engagement", "role"]


class ConsultationFeedbackViewSet(viewsets.ModelViewSet):
    queryset = ConsultationFeedback.objects.all().select_related("engagement")
    serializer_class = ConsultationFeedbackSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["engagement", "feedback_type", "satisfaction_level"]


class EngagementTrackingViewSet(viewsets.ModelViewSet):
    queryset = EngagementTracking.objects.all().select_related("engagement")
    serializer_class = EngagementTrackingSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["engagement", "tracking_type"]


class OrganizationContactViewSet(viewsets.ModelViewSet):
    queryset = OrganizationContact.objects.all().select_related("organization")
    serializer_class = OrganizationContactSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["organization", "contact_type", "is_primary"]


class CommunicationScheduleViewSet(viewsets.ModelViewSet):
    queryset = CommunicationSchedule.objects.all().select_related("communication")
    serializer_class = CommunicationScheduleSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["communication", "status"]


# class EventDocumentViewSet(viewsets.ModelViewSet):
#     """DEPRECATED - EventDocument model uses deprecated Event model."""
#     queryset = EventDocument.objects.all().select_related("event")
#     serializer_class = EventDocumentSerializer
#     permission_classes = [permissions.IsAuthenticated]
#     filterset_fields = ["event", "document_type"]


class PartnershipDocumentViewSet(viewsets.ModelViewSet):
    queryset = PartnershipDocument.objects.all().select_related("partnership")
    serializer_class = PartnershipDocumentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["partnership", "document_type"]

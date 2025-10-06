from rest_framework import serializers

from .models import (
    Communication,
    CommunicationSchedule,
    CommunicationTemplate,
    ConsultationFeedback,
    EngagementFacilitator,
    EngagementTracking,
    Organization,
    OrganizationContact,
    Partnership,
    PartnershipDocument,
    PartnershipMilestone,
    PartnershipSignatory,
    StakeholderEngagement,
    StakeholderEngagementType,
)

# Note: The following models have been removed/migrated:
# - ActionItem: Use WorkItem with work_type='task' instead
# - Event, EventDocument, EventParticipant: These coordination.Event models were removed
#   Events now use WorkItem with work_type='activity'
# See: docs/refactor/WORKITEM_MIGRATION_COMPLETE.md


class StakeholderEngagementTypeSerializer(serializers.ModelSerializer):
    """Serializer for StakeholderEngagementType model."""

    class Meta:
        model = StakeholderEngagementType
        fields = "__all__"


class EngagementFacilitatorSerializer(serializers.ModelSerializer):
    """Serializer for EngagementFacilitator model."""

    user_name = serializers.CharField(source="user.get_full_name", read_only=True)

    class Meta:
        model = EngagementFacilitator
        fields = "__all__"


class StakeholderEngagementSerializer(serializers.ModelSerializer):
    """Serializer for StakeholderEngagement model."""

    engagement_type_name = serializers.CharField(
        source="engagement_type.name", read_only=True
    )
    community_name = serializers.CharField(source="community.name", read_only=True)
    lead_facilitator_name = serializers.CharField(
        source="lead_facilitator.get_full_name", read_only=True
    )
    facilitators = EngagementFacilitatorSerializer(many=True, read_only=True)

    class Meta:
        model = StakeholderEngagement
        fields = "__all__"


class ConsultationFeedbackSerializer(serializers.ModelSerializer):
    """Serializer for ConsultationFeedback model."""

    engagement_title = serializers.CharField(source="engagement.title", read_only=True)

    class Meta:
        model = ConsultationFeedback
        fields = "__all__"


class EngagementTrackingSerializer(serializers.ModelSerializer):
    """Serializer for EngagementTracking model."""

    engagement_title = serializers.CharField(source="engagement.title", read_only=True)

    class Meta:
        model = EngagementTracking
        fields = "__all__"


class OrganizationContactSerializer(serializers.ModelSerializer):
    """Serializer for OrganizationContact model."""

    class Meta:
        model = OrganizationContact
        fields = "__all__"


class OrganizationSerializer(serializers.ModelSerializer):
    """Serializer for Organization model."""

    contacts = OrganizationContactSerializer(many=True, read_only=True)

    class Meta:
        model = Organization
        fields = "__all__"


class CommunicationTemplateSerializer(serializers.ModelSerializer):
    """Serializer for CommunicationTemplate model."""

    class Meta:
        model = CommunicationTemplate
        fields = "__all__"


class CommunicationSerializer(serializers.ModelSerializer):
    """Serializer for Communication model."""

    template_name = serializers.CharField(source="template.name", read_only=True)
    sender_name = serializers.CharField(source="sender.get_full_name", read_only=True)

    class Meta:
        model = Communication
        fields = "__all__"


class CommunicationScheduleSerializer(serializers.ModelSerializer):
    """Serializer for CommunicationSchedule model."""

    communication_subject = serializers.CharField(
        source="communication.subject", read_only=True
    )

    class Meta:
        model = CommunicationSchedule
        fields = "__all__"


# =============================================================================
# DEPRECATED SERIALIZERS - Models removed and replaced by WorkItem system
# These are commented out because the underlying models no longer exist
# See: docs/refactor/WORKITEM_MIGRATION_COMPLETE.md
# =============================================================================

# class EventDocumentSerializer(serializers.ModelSerializer):
#     """DEPRECATED: Serializer for EventDocument model."""
#     class Meta:
#         model = EventDocument
#         fields = "__all__"


# class ActionItemSerializer(serializers.ModelSerializer):
#     """DEPRECATED: Serializer for ActionItem model."""
#     event_title = serializers.CharField(source="event.title", read_only=True)
#     assigned_to_name = serializers.CharField(
#         source="assigned_to.get_full_name", read_only=True
#     )
#     dependency_titles = serializers.SerializerMethodField()
#     class Meta:
#         model = ActionItem
#         fields = "__all__"
#     def get_dependency_titles(self, obj):
#         return [dep.title for dep in obj.dependencies.all()]


# class EventParticipantSerializer(serializers.ModelSerializer):
#     """DEPRECATED: Serializer for EventParticipant model."""
#     event_title = serializers.CharField(source="event.title", read_only=True)
#     participant_name = serializers.CharField(
#         source="participant.get_full_name", read_only=True
#     )
#     class Meta:
#         model = EventParticipant
#         fields = "__all__"


# class EventSerializer(serializers.ModelSerializer):
#     """DEPRECATED: Serializer for Event model."""
#     community_name = serializers.CharField(source="community.name", read_only=True)
#     organizer_name = serializers.CharField(
#         source="organizer.get_full_name", read_only=True
#     )
#     participants = EventParticipantSerializer(many=True, read_only=True)
#     action_items = ActionItemSerializer(many=True, read_only=True)
#     documents = EventDocumentSerializer(many=True, read_only=True)
#     participant_count = serializers.SerializerMethodField()
#     class Meta:
#         model = Event
#         fields = "__all__"
#     def get_participant_count(self, obj):
#         return obj.participants.count()


# class EventListSerializer(serializers.ModelSerializer):
#     """DEPRECATED: Simplified serializer for Event list view."""
#     community_name = serializers.CharField(source="community.name", read_only=True)
#     organizer_name = serializers.CharField(
#         source="organizer.get_full_name", read_only=True
#     )
#     participant_count = serializers.SerializerMethodField()
#     action_item_count = serializers.SerializerMethodField()
#     class Meta:
#         model = Event
#         fields = [
#             "id",
#             "title",
#             "event_type",
#             "community_name",
#             "organizer_name",
#             "planned_date",
#             "actual_date",
#             "status",
#             "participant_count",
#             "action_item_count",
#             "is_virtual",
#             "virtual_platform",
#         ]
#     def get_participant_count(self, obj):
#         return obj.participants.count()
#     def get_action_item_count(self, obj):
#         return obj.action_items.count()

# End of deprecated Event serializers
# =============================================================================


class PartnershipDocumentSerializer(serializers.ModelSerializer):
    """Serializer for PartnershipDocument model."""

    class Meta:
        model = PartnershipDocument
        fields = "__all__"


class PartnershipMilestoneSerializer(serializers.ModelSerializer):
    """Serializer for PartnershipMilestone model."""

    partnership_title = serializers.CharField(
        source="partnership.title", read_only=True
    )

    class Meta:
        model = PartnershipMilestone
        fields = "__all__"


class PartnershipSignatorySerializer(serializers.ModelSerializer):
    """Serializer for PartnershipSignatory model."""

    organization_name = serializers.CharField(
        source="organization.name", read_only=True
    )

    class Meta:
        model = PartnershipSignatory
        fields = "__all__"


class PartnershipSerializer(serializers.ModelSerializer):
    """Serializer for Partnership model."""

    lead_organization_name = serializers.CharField(
        source="lead_organization.name", read_only=True
    )
    signatories = PartnershipSignatorySerializer(many=True, read_only=True)
    milestones = PartnershipMilestoneSerializer(many=True, read_only=True)
    documents = PartnershipDocumentSerializer(many=True, read_only=True)
    signatory_count = serializers.SerializerMethodField()

    class Meta:
        model = Partnership
        fields = "__all__"

    def get_signatory_count(self, obj):
        return obj.signatories.count()


class PartnershipListSerializer(serializers.ModelSerializer):
    """Simplified serializer for Partnership list view."""

    lead_organization_name = serializers.CharField(
        source="lead_organization.name", read_only=True
    )
    signatory_count = serializers.SerializerMethodField()
    milestone_count = serializers.SerializerMethodField()

    class Meta:
        model = Partnership
        fields = [
            "id",
            "title",
            "partnership_type",
            "lead_organization_name",
            "status",
            "start_date",
            "end_date",
            "signatory_count",
            "milestone_count",
            "is_active",
        ]

    def get_signatory_count(self, obj):
        return obj.signatories.count()

    def get_milestone_count(self, obj):
        return obj.milestones.count()

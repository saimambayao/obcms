from rest_framework import serializers
from .models import (
    OBCCommunity,
    CommunityLivelihood,
    CommunityInfrastructure,
    Stakeholder,
    StakeholderEngagement,
)


class CommunityLivelihoodSerializer(serializers.ModelSerializer):
    """Serializer for Community Livelihood model."""

    livelihood_type_display = serializers.CharField(
        source="get_livelihood_type_display", read_only=True
    )
    income_level_display = serializers.CharField(
        source="get_income_level_display", read_only=True
    )

    class Meta:
        model = CommunityLivelihood
        fields = [
            "id",
            "livelihood_type",
            "livelihood_type_display",
            "specific_activity",
            "description",
            "households_involved",
            "percentage_of_community",
            "is_primary_livelihood",
            "seasonal",
            "income_level",
            "income_level_display",
            "challenges",
            "opportunities",
        ]


class CommunityInfrastructureSerializer(serializers.ModelSerializer):
    """Serializer for Community Infrastructure model."""

    infrastructure_type_display = serializers.CharField(
        source="get_infrastructure_type_display", read_only=True
    )
    availability_status_display = serializers.CharField(
        source="get_availability_status_display", read_only=True
    )
    condition_display = serializers.CharField(
        source="get_condition_display", read_only=True
    )
    priority_display = serializers.CharField(
        source="get_priority_for_improvement_display", read_only=True
    )

    class Meta:
        model = CommunityInfrastructure
        fields = [
            "id",
            "infrastructure_type",
            "infrastructure_type_display",
            "availability_status",
            "availability_status_display",
            "description",
            "coverage_percentage",
            "condition",
            "condition_display",
            "priority_for_improvement",
            "priority_display",
            "notes",
            "last_assessed",
        ]


class OBCCommunitySerializer(serializers.ModelSerializer):
    """Full serializer for OBC Community model."""

    full_location = serializers.ReadOnlyField()
    total_age_demographics = serializers.ReadOnlyField()
    average_household_size = serializers.ReadOnlyField()
    unemployment_rate_display = serializers.CharField(
        source="get_unemployment_rate_display", read_only=True
    )
    settlement_type_display = serializers.CharField(
        source="get_settlement_type_display", read_only=True
    )

    # Administrative location details
    region = serializers.CharField(source="region.name", read_only=True)
    region_code = serializers.CharField(source="region.code", read_only=True)
    province = serializers.CharField(source="province.name", read_only=True)
    municipality = serializers.CharField(source="municipality.name", read_only=True)
    barangay_name = serializers.CharField(source="barangay.name", read_only=True)

    # Related data
    livelihoods = CommunityLivelihoodSerializer(many=True, read_only=True)
    infrastructure = CommunityInfrastructureSerializer(many=True, read_only=True)
    stakeholders = serializers.SerializerMethodField()

    class Meta:
        model = OBCCommunity
        fields = [
            "id",
            "full_location",
            "settlement_type",
            "settlement_type_display",
            "region",
            "region_code",
            "province",
            "municipality",
            "barangay_name",
            "specific_location",
            "population",
            "households",
            "families",
            "total_age_demographics",
            "average_household_size",
            "children_0_12",
            "youth_13_30",
            "adults_31_59",
            "seniors_60_plus",
            "primary_language",
            "other_languages",
            "cultural_background",
            "religious_practices",
            "mosques_count",
            "madrasah_count",
            "religious_leaders_count",
            "established_year",
            "origin_story",
            "migration_history",
            "unemployment_rate",
            "unemployment_rate_display",
            "needs_assessment_date",
            "priority_needs",
            "community_leader",
            "leader_contact",
            "is_active",
            "notes",
            "livelihoods",
            "infrastructure",
            "stakeholders",
            "created_at",
            "updated_at",
        ]

    def get_stakeholders(self, obj):
        """Return simplified stakeholder data for the community."""
        stakeholders = obj.stakeholders.filter(is_active=True).order_by(
            "stakeholder_type", "full_name"
        )
        return StakeholderListSerializer(stakeholders, many=True).data

    # History helpers -----------------------------------------------------
    def _get_history_user(self):
        request = self.context.get("request")
        user = getattr(request, "user", None)
        if user is not None and getattr(user, "is_authenticated", False):
            return user
        return None

    def create(self, validated_data):
        history_user = self._get_history_user()
        instance = OBCCommunity(**validated_data)
        if history_user:
            instance._history_user = history_user
        instance.save()
        return instance

    def update(self, instance, validated_data):
        history_user = self._get_history_user()
        if history_user:
            instance._history_user = history_user
        return super().update(instance, validated_data)


class OBCCommunityListSerializer(serializers.ModelSerializer):
    """Simplified serializer for OBC Community list view."""

    full_location = serializers.ReadOnlyField()
    unemployment_rate_display = serializers.CharField(
        source="get_unemployment_rate_display", read_only=True
    )
    settlement_type_display = serializers.CharField(
        source="get_settlement_type_display", read_only=True
    )

    # Administrative location details
    region = serializers.CharField(source="region.name", read_only=True)
    region_code = serializers.CharField(source="region.code", read_only=True)
    province = serializers.CharField(source="province.name", read_only=True)
    municipality = serializers.CharField(source="municipality.name", read_only=True)
    barangay_name = serializers.CharField(source="barangay.name", read_only=True)

    # Counts
    livelihood_count = serializers.SerializerMethodField()
    infrastructure_count = serializers.SerializerMethodField()

    class Meta:
        model = OBCCommunity
        fields = [
            "id",
            "full_location",
            "settlement_type",
            "settlement_type_display",
            "region",
            "region_code",
            "province",
            "municipality",
            "barangay_name",
            "population",
            "households",
            "unemployment_rate",
            "unemployment_rate_display",
            "primary_language",
            "mosques_count",
            "madrasah_count",
            "community_leader",
            "livelihood_count",
            "infrastructure_count",
            "is_active",
            "updated_at",
        ]

    def get_livelihood_count(self, obj):
        """Return the number of livelihoods for this community."""
        return obj.livelihoods.count()

    def get_infrastructure_count(self, obj):
        """Return the number of infrastructure items for this community."""
        return obj.infrastructure.count()


class CommunityStatsSerializer(serializers.Serializer):
    """Serializer for community statistics."""

    total_communities = serializers.IntegerField()
    total_population = serializers.IntegerField()
    total_households = serializers.IntegerField()
    by_region = serializers.DictField()
    by_unemployment_rate = serializers.DictField()
    by_settlement_type = serializers.DictField()
    religious_facilities = serializers.DictField()
    average_household_size = serializers.FloatField()
    language_distribution = serializers.DictField()


class StakeholderSerializer(serializers.ModelSerializer):
    """Serializer for Stakeholder model."""

    display_name = serializers.ReadOnlyField()
    years_of_service = serializers.ReadOnlyField()
    contact_info = serializers.ReadOnlyField()
    community_name = serializers.CharField(
        source="community.barangay.name", read_only=True
    )
    stakeholder_type_display = serializers.CharField(
        source="get_stakeholder_type_display", read_only=True
    )
    influence_level_display = serializers.CharField(
        source="get_influence_level_display", read_only=True
    )
    engagement_level_display = serializers.CharField(
        source="get_engagement_level_display", read_only=True
    )

    class Meta:
        model = Stakeholder
        fields = [
            "id",
            "full_name",
            "nickname",
            "display_name",
            "stakeholder_type",
            "stakeholder_type_display",
            "community",
            "community_name",
            "position",
            "organization",
            "responsibilities",
            "contact_number",
            "alternate_contact",
            "email",
            "address",
            "contact_info",
            "influence_level",
            "influence_level_display",
            "engagement_level",
            "engagement_level_display",
            "areas_of_influence",
            "age",
            "educational_background",
            "cultural_background",
            "languages_spoken",
            "since_year",
            "years_in_community",
            "years_of_service",
            "previous_roles",
            "special_skills",
            "networks",
            "achievements",
            "challenges_faced",
            "support_needed",
            "is_active",
            "is_verified",
            "verification_date",
            "notes",
            "created_at",
            "updated_at",
        ]


class StakeholderListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for Stakeholder listing."""

    display_name = serializers.ReadOnlyField()
    community_name = serializers.CharField(
        source="community.barangay.name", read_only=True
    )
    stakeholder_type_display = serializers.CharField(
        source="get_stakeholder_type_display", read_only=True
    )
    influence_level_display = serializers.CharField(
        source="get_influence_level_display", read_only=True
    )
    engagement_level_display = serializers.CharField(
        source="get_engagement_level_display", read_only=True
    )

    class Meta:
        model = Stakeholder
        fields = [
            "id",
            "display_name",
            "full_name",
            "nickname",
            "stakeholder_type",
            "stakeholder_type_display",
            "community_name",
            "position",
            "influence_level",
            "influence_level_display",
            "engagement_level",
            "engagement_level_display",
            "contact_number",
            "email",
            "is_active",
            "is_verified",
            "since_year",
        ]


class StakeholderEngagementSerializer(serializers.ModelSerializer):
    """Serializer for Stakeholder Engagement model."""

    stakeholder_name = serializers.CharField(
        source="stakeholder.display_name", read_only=True
    )
    community_name = serializers.CharField(
        source="stakeholder.community.barangay.name", read_only=True
    )
    engagement_type_display = serializers.CharField(
        source="get_engagement_type_display", read_only=True
    )
    outcome_display = serializers.CharField(
        source="get_outcome_display", read_only=True
    )

    class Meta:
        model = StakeholderEngagement
        fields = [
            "id",
            "stakeholder",
            "stakeholder_name",
            "community_name",
            "engagement_type",
            "engagement_type_display",
            "title",
            "description",
            "date",
            "duration_hours",
            "location",
            "participants_count",
            "outcome",
            "outcome_display",
            "key_points",
            "action_items",
            "challenges_encountered",
            "stakeholder_feedback",
            "follow_up_needed",
            "follow_up_date",
            "documented_by",
            "created_at",
            "updated_at",
        ]


class StakeholderStatsSerializer(serializers.Serializer):
    """Serializer for stakeholder statistics."""

    total_stakeholders = serializers.IntegerField()
    active_stakeholders = serializers.IntegerField()
    verified_stakeholders = serializers.IntegerField()
    by_type = serializers.DictField()
    by_influence_level = serializers.DictField()
    by_engagement_level = serializers.DictField()
    by_community = serializers.DictField()
    recent_engagements = serializers.IntegerField()

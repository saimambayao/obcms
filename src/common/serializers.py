from rest_framework import serializers

from .models import Barangay, Municipality, Province, Region, User
from .work_item_model import WorkItem


class BarangaySerializer(serializers.ModelSerializer):
    """Serializer for Barangay model."""

    full_path = serializers.ReadOnlyField()

    class Meta:
        model = Barangay
        fields = ["id", "code", "name", "is_urban", "is_active", "full_path"]


class MunicipalitySerializer(serializers.ModelSerializer):
    """Serializer for Municipality model."""

    full_path = serializers.ReadOnlyField()
    barangay_count = serializers.ReadOnlyField()
    barangays = BarangaySerializer(many=True, read_only=True)

    class Meta:
        model = Municipality
        fields = [
            "id",
            "code",
            "name",
            "municipality_type",
            "is_active",
            "full_path",
            "barangay_count",
            "barangays",
        ]


class ProvinceSerializer(serializers.ModelSerializer):
    """Serializer for Province model."""

    full_path = serializers.ReadOnlyField()
    municipality_count = serializers.ReadOnlyField()
    municipalities = MunicipalitySerializer(many=True, read_only=True)

    class Meta:
        model = Province
        fields = [
            "id",
            "code",
            "name",
            "capital",
            "is_active",
            "full_path",
            "municipality_count",
            "municipalities",
        ]


class RegionSerializer(serializers.ModelSerializer):
    """Serializer for Region model."""

    province_count = serializers.ReadOnlyField()
    provinces = ProvinceSerializer(many=True, read_only=True)

    class Meta:
        model = Region
        fields = [
            "id",
            "code",
            "name",
            "description",
            "is_active",
            "province_count",
            "provinces",
        ]


class RegionListSerializer(serializers.ModelSerializer):
    """Simplified serializer for Region list view."""

    province_count = serializers.ReadOnlyField()

    class Meta:
        model = Region
        fields = ["id", "code", "name", "description", "is_active", "province_count"]


class ProvinceListSerializer(serializers.ModelSerializer):
    """Simplified serializer for Province list view."""

    region_name = serializers.CharField(source="region.name", read_only=True)
    region_code = serializers.CharField(source="region.code", read_only=True)
    municipality_count = serializers.ReadOnlyField()
    full_path = serializers.ReadOnlyField()

    class Meta:
        model = Province
        fields = [
            "id",
            "code",
            "name",
            "capital",
            "is_active",
            "region_name",
            "region_code",
            "municipality_count",
            "full_path",
        ]


class MunicipalityListSerializer(serializers.ModelSerializer):
    """Simplified serializer for Municipality list view."""

    province_name = serializers.CharField(source="province.name", read_only=True)
    region_name = serializers.CharField(source="province.region.name", read_only=True)
    barangay_count = serializers.ReadOnlyField()
    full_path = serializers.ReadOnlyField()

    class Meta:
        model = Municipality
        fields = [
            "id",
            "code",
            "name",
            "municipality_type",
            "is_active",
            "province_name",
            "region_name",
            "barangay_count",
            "full_path",
        ]


class BarangayListSerializer(serializers.ModelSerializer):
    """Simplified serializer for Barangay list view."""

    municipality_name = serializers.CharField(
        source="municipality.name", read_only=True
    )
    province_name = serializers.CharField(
        source="municipality.province.name", read_only=True
    )
    region_name = serializers.CharField(
        source="municipality.province.region.name", read_only=True
    )
    full_path = serializers.ReadOnlyField()

    class Meta:
        model = Barangay
        fields = [
            "id",
            "code",
            "name",
            "is_urban",
            "is_active",
            "municipality_name",
            "province_name",
            "region_name",
            "full_path",
        ]


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model."""

    approved_by = serializers.StringRelatedField(read_only=True)
    full_name = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "user_type",
            "organization",
            "position",
            "contact_number",
            "is_active",
            "is_approved",
            "approved_by",
            "approved_at",
            "date_joined",
            "full_name",
        ]
        read_only_fields = ["id", "date_joined", "approved_by", "approved_at"]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        user = User(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user


class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new users."""

    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "password",
            "confirm_password",
            "first_name",
            "last_name",
            "user_type",
            "organization",
            "position",
            "contact_number",
        ]

    def validate(self, attrs):
        if attrs["password"] != attrs["confirm_password"]:
            raise serializers.ValidationError("Passwords don't match")
        attrs.pop("confirm_password")
        return attrs

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class WorkItemSerializer(serializers.ModelSerializer):
    """Serializer for WorkItem model (unified work hierarchy)."""

    work_type_display = serializers.CharField(
        source="get_work_type_display", read_only=True
    )
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    priority_display = serializers.CharField(
        source="get_priority_display", read_only=True
    )
    created_by_name = serializers.CharField(
        source="created_by.get_full_name", read_only=True
    )
    assignees_detail = serializers.SerializerMethodField()
    teams_detail = serializers.SerializerMethodField()
    is_overdue = serializers.SerializerMethodField()

    class Meta:
        model = WorkItem
        fields = [
            "id",
            "work_type",
            "work_type_display",
            "title",
            "description",
            "status",
            "status_display",
            "priority",
            "priority_display",
            "progress",
            "parent",
            "start_date",
            "due_date",
            "start_time",
            "end_time",
            "completed_at",
            "is_calendar_visible",
            "calendar_color",
            "auto_calculate_progress",
            "assignees_detail",
            "teams_detail",
            "created_by",
            "created_by_name",
            "is_recurring",
            "project_data",
            "activity_data",
            "task_data",
            "content_type",
            "object_id",
            "created_at",
            "updated_at",
            "is_overdue",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
            "work_type_display",
            "status_display",
            "priority_display",
            "created_by_name",
            "assignees_detail",
            "teams_detail",
            "is_overdue",
        ]

    def get_assignees_detail(self, obj):
        """Return detailed assignee information."""
        return [
            {
                "id": assignee.id,
                "name": assignee.get_full_name() or assignee.username,
                "email": assignee.email,
            }
            for assignee in obj.assignees.all()
        ]

    def get_teams_detail(self, obj):
        """Return detailed team information."""
        return [
            {
                "id": team.id,
                "name": team.name,
            }
            for team in obj.teams.all()
        ]

    def get_is_overdue(self, obj):
        """Check if the work item is overdue."""
        from django.utils import timezone

        if obj.due_date and obj.status not in [
            WorkItem.STATUS_COMPLETED,
            WorkItem.STATUS_CANCELLED,
        ]:
            return obj.due_date < timezone.now().date()
        return False

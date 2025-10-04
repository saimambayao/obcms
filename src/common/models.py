import uuid
from calendar import monthrange
from datetime import date, timedelta
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone
from django.utils.text import slugify


def _invalidate_calendar_cache() -> None:
    """Safely clear cached calendar artefacts without circular imports."""

    from common.services import calendar as calendar_service

    calendar_service.invalidate_calendar_cache()


class User(AbstractUser):
    """
    Custom User model for the OBC Management System.
    Extends Django's AbstractUser to include OBC-specific fields and roles.
    """

    USER_TYPES = (
        ("admin", "Administrator"),
        ("oobc_staff", "OOBC Staff"),
        ("cm_office", "Chief Minister Office"),
        ("bmoa", "BARMM Ministry/Agency/Office"),
        ("lgu", "Local Government Unit"),
        ("nga", "National Government Agency"),
        ("community_leader", "Community Leader"),
        ("researcher", "Assessment Coordinator/Researcher"),
    )

    user_type = models.CharField(
        max_length=20,
        choices=USER_TYPES,
        help_text="Type of user based on organization role",
    )
    organization = models.CharField(
        max_length=255, blank=True, help_text="Name of the organization or agency"
    )
    position = models.CharField(
        max_length=255,
        blank=True,
        help_text="Position or title within the organization",
    )
    contact_number = models.CharField(
        max_length=20, blank=True, help_text="Contact phone number"
    )
    is_approved = models.BooleanField(
        default=False, help_text="Whether the user account has been approved for access"
    )
    approved_by = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="approved_users",
        help_text="Admin user who approved this account",
    )
    approved_at = models.DateTimeField(
        null=True, blank=True, help_text="When the account was approved"
    )

    class Meta:
        db_table = "auth_user"
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return f"{self.get_full_name()} ({self.get_user_type_display()})"

    def get_full_name(self):
        """Return the full name of the user."""
        return super().get_full_name() or self.username

    @property
    def is_oobc_staff(self):
        """Check if user is OOBC staff."""
        return self.user_type == "oobc_staff"

    @property
    def is_community_leader(self):
        """Check if user is a community leader."""
        return self.user_type == "community_leader"

    @property
    def can_approve_users(self):
        """Check if user can approve other users."""
        return self.user_type in ["admin", "oobc_staff"] and self.is_superuser


class Region(models.Model):
    """
    Administrative region model representing Philippine regions.
    Focus on Regions IX (Zamboanga Peninsula), XII (SOCCSKSARGEN), and others.
    """

    code = models.CharField(
        max_length=10, unique=True, help_text="Official region code (e.g., IX, XII)"
    )
    name = models.CharField(max_length=255, help_text="Official region name")
    description = models.TextField(
        blank=True, help_text="Additional region description or notes"
    )
    is_active = models.BooleanField(
        default=True, help_text="Whether this region is active in the system"
    )

    # Geographic boundary information
    boundary_geojson = models.JSONField(
        null=True, blank=True, help_text="GeoJSON polygon defining the region boundary"
    )
    center_coordinates = models.JSONField(
        null=True, blank=True, help_text="Geographic center point [longitude, latitude]"
    )
    bounding_box = models.JSONField(
        null=True,
        blank=True,
        help_text="Bounding box [min_lng, min_lat, max_lng, max_lat]",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "common_region"
        ordering = ["code"]
        verbose_name = "Region"
        verbose_name_plural = "Regions"

    def __str__(self):
        return f"Region {self.code} - {self.name}"

    @property
    def province_count(self):
        """Return the number of provinces in this region."""
        return self.provinces.filter(is_active=True).count()

    @property
    def has_geographic_boundary(self):
        """Check if this region has geographic boundary data."""
        return bool(self.boundary_geojson)

    @property
    def geographic_layers_count(self):
        """Return the number of geographic layers associated with this region."""
        return self.geographic_layers.count()

    def get_contained_coordinates(self, coordinates):
        """Check if given coordinates [lng, lat] are within region boundary."""
        if not self.boundary_geojson:
            return False
        # Placeholder for actual geometric containment check
        # In production, this would use proper GIS libraries like Shapely
        return True

    def get_all_geographic_layers(self):
        """Get all geographic layers at this level and below."""
        from mana.models import GeographicDataLayer

        return GeographicDataLayer.objects.filter(
            models.Q(region=self)
            | models.Q(province__region=self)
            | models.Q(municipality__province__region=self)
            | models.Q(barangay__municipality__province__region=self)
            | models.Q(community__barangay__municipality__province__region=self)
        )


class Province(models.Model):
    """
    Administrative province model under regions.
    """

    region = models.ForeignKey(
        Region,
        on_delete=models.CASCADE,
        related_name="provinces",
        help_text="Parent region",
    )
    code = models.CharField(
        max_length=64, unique=True, help_text="Official province code"
    )
    name = models.CharField(max_length=255, help_text="Official province name")
    capital = models.CharField(
        max_length=255, blank=True, help_text="Provincial capital city"
    )
    is_active = models.BooleanField(
        default=True, help_text="Whether this province is active in the system"
    )
    population_total = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Total population based on latest PSA census",
    )

    # Geographic boundary information
    boundary_geojson = models.JSONField(
        null=True,
        blank=True,
        help_text="GeoJSON polygon defining the province boundary",
    )
    center_coordinates = models.JSONField(
        null=True, blank=True, help_text="Geographic center point [longitude, latitude]"
    )
    bounding_box = models.JSONField(
        null=True,
        blank=True,
        help_text="Bounding box [min_lng, min_lat, max_lng, max_lat]",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "common_province"
        ordering = ["region__code", "name"]
        verbose_name = "Province"
        verbose_name_plural = "Provinces"

    def __str__(self):
        return f"{self.name}, {self.region.name}"

    @property
    def municipality_count(self):
        """Return the number of municipalities in this province."""
        return self.municipalities.filter(is_active=True).count()

    @property
    def full_path(self):
        """Return the full administrative path."""
        return f"Region {self.region.code} > {self.name}"

    @property
    def has_geographic_boundary(self):
        """Check if this province has geographic boundary data."""
        return bool(self.boundary_geojson)

    @property
    def geographic_layers_count(self):
        """Return the number of geographic layers associated with this province."""
        return self.geographic_layers.count()

    def get_all_geographic_layers(self):
        """Get all geographic layers at this level and below."""
        from mana.models import GeographicDataLayer

        return GeographicDataLayer.objects.filter(
            models.Q(province=self)
            | models.Q(municipality__province=self)
            | models.Q(barangay__municipality__province=self)
            | models.Q(community__barangay__municipality__province=self)
        )


class Municipality(models.Model):
    """
    Administrative municipality/city model under provinces.
    """

    MUNICIPALITY_TYPES = (
        ("municipality", "Municipality"),
        ("city", "City"),
        ("component_city", "Component City"),
        ("independent_city", "Independent City"),
    )

    province = models.ForeignKey(
        Province,
        on_delete=models.CASCADE,
        related_name="municipalities",
        help_text="Parent province",
    )
    code = models.CharField(
        max_length=64, unique=True, help_text="Official municipality/city code"
    )
    name = models.CharField(max_length=255, help_text="Official municipality/city name")
    municipality_type = models.CharField(
        max_length=20,
        choices=MUNICIPALITY_TYPES,
        default="municipality",
        help_text="Type of local government unit",
    )
    is_active = models.BooleanField(
        default=True, help_text="Whether this municipality is active in the system"
    )
    population_total = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Total population based on latest PSA census",
    )

    # Geographic boundary information
    boundary_geojson = models.JSONField(
        null=True,
        blank=True,
        help_text="GeoJSON polygon defining the municipality boundary",
    )
    center_coordinates = models.JSONField(
        null=True, blank=True, help_text="Geographic center point [longitude, latitude]"
    )
    bounding_box = models.JSONField(
        null=True,
        blank=True,
        help_text="Bounding box [min_lng, min_lat, max_lng, max_lat]",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "common_municipality"
        ordering = ["province__name", "name"]
        verbose_name = "Municipality"
        verbose_name_plural = "Municipalities"

    def __str__(self):
        type_display = self.get_municipality_type_display()
        return f"{type_display} of {self.name}, {self.province.name}"

    @property
    def barangay_count(self):
        """Return the number of barangays in this municipality."""
        return self.barangays.filter(is_active=True).count()

    @property
    def full_path(self):
        """Return the full administrative path."""
        return (
            f"Region {self.province.region.code} > {self.province.name} > {self.name}"
        )

    @property
    def has_geographic_boundary(self):
        """Check if this municipality has geographic boundary data."""
        return bool(self.boundary_geojson)

    @property
    def geographic_layers_count(self):
        """Return the number of geographic layers associated with this municipality."""
        return self.geographic_layers.count()

    def get_all_geographic_layers(self):
        """Get all geographic layers at this level and below."""
        from mana.models import GeographicDataLayer

        return GeographicDataLayer.objects.filter(
            models.Q(municipality=self)
            | models.Q(barangay__municipality=self)
            | models.Q(community__barangay__municipality=self)
        )


class Barangay(models.Model):
    """
    Administrative barangay model under municipalities.
    Barangay is the smallest administrative unit in the Philippines.
    """

    municipality = models.ForeignKey(
        Municipality,
        on_delete=models.CASCADE,
        related_name="barangays",
        help_text="Parent municipality",
    )
    code = models.CharField(
        max_length=64, unique=True, help_text="Official barangay code"
    )
    name = models.CharField(max_length=255, help_text="Official barangay name")
    is_urban = models.BooleanField(
        default=False, help_text="Whether this barangay is classified as urban"
    )
    is_active = models.BooleanField(
        default=True, help_text="Whether this barangay is active in the system"
    )
    population_total = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Total population based on latest PSA census",
    )

    # Geographic boundary information
    boundary_geojson = models.JSONField(
        null=True,
        blank=True,
        help_text="GeoJSON polygon defining the barangay boundary",
    )
    center_coordinates = models.JSONField(
        null=True, blank=True, help_text="Geographic center point [longitude, latitude]"
    )
    bounding_box = models.JSONField(
        null=True,
        blank=True,
        help_text="Bounding box [min_lng, min_lat, max_lng, max_lat]",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "common_barangay"
        ordering = ["municipality__name", "name"]
        verbose_name = "Barangay"
        verbose_name_plural = "Barangays"

    def __str__(self):
        return f"Barangay {self.name}, {self.municipality.name}"

    @property
    def full_path(self):
        """Return the full administrative path."""
        return (
            f"Region {self.municipality.province.region.code} > "
            f"{self.municipality.province.name} > "
            f"{self.municipality.name} > "
            f"Barangay {self.name}"
        )

    @property
    def region(self):
        """Return the region this barangay belongs to."""
        return self.municipality.province.region

    @property
    def province(self):
        """Return the province this barangay belongs to."""
        return self.municipality.province

    @property
    def has_geographic_boundary(self):
        """Check if this barangay has geographic boundary data."""
        return bool(self.boundary_geojson)

    @property
    def geographic_layers_count(self):
        """Return the number of geographic layers associated with this barangay."""
        return self.geographic_layers.count()

    def get_all_geographic_layers(self):
        """Get all geographic layers at this level and below."""
        from mana.models import GeographicDataLayer

        return GeographicDataLayer.objects.filter(
            models.Q(barangay=self) | models.Q(community__barangay=self)
        )


class StaffProfile(models.Model):
    """Extended profile metadata for OOBC staff members."""

    STATUS_ACTIVE = "active"
    STATUS_INACTIVE = "inactive"
    STATUS_ON_LEAVE = "on_leave"
    EMPLOYMENT_STATUS_CHOICES = [
        (STATUS_ACTIVE, "Active"),
        (STATUS_ON_LEAVE, "On Leave"),
        (STATUS_INACTIVE, "Inactive"),
    ]

    TYPE_REGULAR = "regular"
    TYPE_CONTRACTUAL = "contractual"
    TYPE_CONSULTANT = "consultant"
    TYPE_VOLUNTEER = "volunteer"
    EMPLOYMENT_TYPE_CHOICES = [
        (TYPE_REGULAR, "Regular"),
        (TYPE_CONTRACTUAL, "Contractual"),
        (TYPE_CONSULTANT, "Consultant"),
        (TYPE_VOLUNTEER, "Volunteer"),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        related_name="staff_profile",
        on_delete=models.CASCADE,
    )
    employment_status = models.CharField(
        max_length=20,
        choices=EMPLOYMENT_STATUS_CHOICES,
        default=STATUS_ACTIVE,
    )
    employment_type = models.CharField(
        max_length=20,
        choices=EMPLOYMENT_TYPE_CHOICES,
        blank=True,
    )
    position_classification = models.CharField(max_length=150, blank=True)
    plantilla_item_number = models.CharField(max_length=100, blank=True)
    salary_grade = models.CharField(max_length=50, blank=True)
    salary_step = models.CharField(max_length=20, blank=True)
    reports_to = models.CharField(max_length=255, blank=True)
    date_joined_organization = models.DateField(null=True, blank=True)
    primary_location = models.CharField(max_length=255, blank=True)
    job_purpose = models.TextField(blank=True)
    key_result_areas = models.JSONField(default=list, blank=True)
    major_functions = models.JSONField(default=list, blank=True)
    deliverables = models.JSONField(default=list, blank=True)
    supervision_lines = models.JSONField(default=list, blank=True)
    cross_functional_partners = models.JSONField(default=list, blank=True)
    core_competencies = models.JSONField(default=list, blank=True)
    leadership_competencies = models.JSONField(default=list, blank=True)
    functional_competencies = models.JSONField(default=list, blank=True)
    qualification_education = models.CharField(max_length=255, blank=True)
    qualification_training = models.CharField(max_length=255, blank=True)
    qualification_experience = models.CharField(max_length=255, blank=True)
    qualification_eligibility = models.CharField(max_length=255, blank=True)
    qualification_competency = models.TextField(blank=True)
    job_documents_url = models.URLField(blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["user__last_name", "user__first_name"]

    def __str__(self):
        return f"Staff Profile: {self.user.get_full_name()}"

    def get_competencies(self, category: str) -> list[str]:
        """Return the stored competencies for a given category."""

        mapping = {
            "core": self.core_competencies,
            "leadership": self.leadership_competencies,
            "functional": self.functional_competencies,
        }
        return mapping.get(category, [])


class StaffTeam(models.Model):
    """Operational teams coordinating OOBC staff and task workflows."""

    ROLE_FOCUS_DEFAULT = [
        "strategy",
        "implementation",
        "monitoring",
        "coordination",
    ]

    name = models.CharField(max_length=150, unique=True)
    slug = models.SlugField(max_length=160, unique=True, blank=True)
    description = models.TextField(blank=True)
    mission = models.TextField(blank=True)
    focus_areas = models.JSONField(default=list, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name) or "team"
            slug = base_slug
            index = 1
            while StaffTeam.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{index}"
                index += 1
            self.slug = slug
        if not self.focus_areas:
            self.focus_areas = self.ROLE_FOCUS_DEFAULT
        super().save(*args, **kwargs)

    @property
    def active_memberships(self):
        """Return active memberships for this team."""
        return self.memberships.filter(is_active=True)


class StaffTeamMembership(models.Model):
    """Link OOBC staff to operational teams with roles."""

    ROLE_MEMBER = "member"
    ROLE_LEAD = "lead"
    ROLE_COORDINATOR = "coordinator"
    ROLE_CHOICES = [
        (ROLE_LEAD, "Team Lead"),
        (ROLE_COORDINATOR, "Coordinator"),
        (ROLE_MEMBER, "Member"),
    ]

    team = models.ForeignKey(
        StaffTeam, related_name="memberships", on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="team_memberships",
        on_delete=models.CASCADE,
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_MEMBER)
    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="assigned_team_memberships",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    joined_at = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("team", "user")
        ordering = ["team__name", "user__last_name", "user__first_name"]

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.team.name}"

    def deactivate(self, save=True):
        """Mark the membership as inactive."""
        self.is_active = False
        if save:
            self.save(update_fields=["is_active", "updated_at"])


class StaffTask(models.Model):
    """Task records connected to staff profiles, teams, and calendar events."""

    STATUS_NOT_STARTED = "not_started"
    STATUS_IN_PROGRESS = "in_progress"
    STATUS_AT_RISK = "at_risk"
    STATUS_COMPLETED = "completed"
    STATUS_CHOICES = [
        (STATUS_NOT_STARTED, "Not Started"),
        (STATUS_IN_PROGRESS, "In Progress"),
        (STATUS_AT_RISK, "At Risk"),
        (STATUS_COMPLETED, "Completed"),
    ]

    PRIORITY_LOW = "low"
    PRIORITY_MEDIUM = "medium"
    PRIORITY_HIGH = "high"
    PRIORITY_CRITICAL = "critical"
    PRIORITY_CHOICES = [
        (PRIORITY_LOW, "Low"),
        (PRIORITY_MEDIUM, "Medium"),
        (PRIORITY_HIGH, "High"),
        (PRIORITY_CRITICAL, "Critical"),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    impact = models.CharField(max_length=255, blank=True)
    teams = models.ManyToManyField(
        StaffTeam,
        related_name="tasks",
        blank=True,
    )
    assignees = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="assigned_staff_tasks",
        blank=True,
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="created_staff_tasks",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    linked_event = models.ForeignKey(
        "coordination.Event",
        related_name="staff_tasks",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default=STATUS_NOT_STARTED
    )
    priority = models.CharField(
        max_length=12, choices=PRIORITY_CHOICES, default=PRIORITY_MEDIUM
    )
    progress = models.PositiveSmallIntegerField(
        default=0, validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    board_position = models.PositiveIntegerField(
        default=0,
        help_text="Relative ordering for Kanban board presentation.",
    )
    start_date = models.DateField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Recurrence (Enhanced with RecurringEventPattern)
    is_recurring = models.BooleanField(
        default=False, help_text="Whether this is a recurring task"
    )

    recurrence_pattern = models.ForeignKey(
        "RecurringEventPattern",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="recurring_tasks",
        help_text="Recurrence pattern configuration (RFC 5545 compatible)",
    )

    recurrence_parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="recurrence_instances",
        help_text="Parent task if this is a recurrence instance",
    )

    is_recurrence_exception = models.BooleanField(
        default=False,
        help_text="True if this instance was edited separately from the recurrence pattern",
    )

    # ========== DOMAIN-SPECIFIC RELATIONSHIPS ==========

    # Common App (Staff Management)
    related_training = models.ForeignKey(
        "TrainingEnrollment",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="tasks",
        help_text="Related training enrollment",
    )
    related_dev_plan = models.ForeignKey(
        "StaffDevelopmentPlan",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="tasks",
        help_text="Related development plan",
    )
    related_performance_target = models.ForeignKey(
        "PerformanceTarget",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="tasks",
        help_text="Related performance target",
    )

    # Communities App
    related_community = models.ForeignKey(
        "communities.OBCCommunity",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="tasks",
        help_text="Related OBC community",
    )
    related_stakeholder = models.ForeignKey(
        "communities.Stakeholder",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="tasks",
        help_text="Related stakeholder",
    )
    related_engagement = models.ForeignKey(
        "communities.StakeholderEngagement",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="tasks",
        help_text="Related stakeholder engagement",
    )
    related_municipality_coverage = models.ForeignKey(
        "communities.MunicipalityCoverage",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="tasks",
        help_text="Related municipality coverage",
    )

    # MANA App
    related_assessment = models.ForeignKey(
        "mana.Assessment",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="tasks",
        help_text="Related MANA assessment",
    )
    related_survey = models.ForeignKey(
        "mana.Survey",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="tasks",
        help_text="Related survey",
    )
    related_workshop = models.ForeignKey(
        "mana.WorkshopActivity",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="tasks",
        help_text="Related workshop activity",
    )
    related_baseline = models.ForeignKey(
        "mana.BaselineStudy",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="tasks",
        help_text="Related baseline study",
    )
    related_need = models.ForeignKey(
        "mana.Need",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="tasks",
        help_text="Related identified need",
    )
    related_mapping = models.ForeignKey(
        "mana.MappingActivity",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="tasks",
        help_text="Related mapping activity",
    )

    # Coordination App
    # Note: linked_event already exists above
    related_organization = models.ForeignKey(
        "coordination.Organization",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="tasks",
        help_text="Related organization",
    )
    related_partnership = models.ForeignKey(
        "coordination.Partnership",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="tasks",
        help_text="Related partnership",
    )
    related_partnership_milestone = models.ForeignKey(
        "coordination.PartnershipMilestone",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="tasks",
        help_text="Related partnership milestone",
    )
    related_communication = models.ForeignKey(
        "coordination.Communication",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="tasks",
        help_text="Related communication",
    )
    related_mao_focal_person = models.ForeignKey(
        "coordination.MAOFocalPerson",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="tasks",
        help_text="Related MAO focal person",
    )

    # Monitoring App
    related_ppa = models.ForeignKey(
        "monitoring.MonitoringEntry",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="tasks",
        help_text="Related PPA/monitoring entry",
    )
    related_funding_flow = models.ForeignKey(
        "monitoring.MonitoringEntryFunding",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="tasks",
        help_text="Related funding flow",
    )
    related_workflow_stage = models.ForeignKey(
        "monitoring.MonitoringEntryWorkflowStage",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="tasks",
        help_text="Related workflow stage",
    )
    related_outcome_indicator = models.ForeignKey(
        "monitoring.OutcomeIndicator",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="tasks",
        help_text="Related outcome indicator",
    )
    related_strategic_goal = models.ForeignKey(
        "monitoring.StrategicGoal",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="tasks",
        help_text="Related strategic goal",
    )

    # Policy Tracking App
    related_policy = models.ForeignKey(
        "policy_tracking.PolicyRecommendation",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="tasks",
        help_text="Related policy recommendation",
    )
    related_policy_milestone = models.ForeignKey(
        "policy_tracking.PolicyImplementationMilestone",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="tasks",
        help_text="Related policy implementation milestone",
    )
    related_policy_evidence = models.ForeignKey(
        "policy_tracking.PolicyEvidence",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="tasks",
        help_text="Related policy evidence",
    )

    # Services App
    related_service = models.ForeignKey(
        "services.ServiceOffering",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="tasks",
        help_text="Related service offering",
    )
    related_application = models.ForeignKey(
        "services.ServiceApplication",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="tasks",
        help_text="Related service application",
    )

    # Municipal Profiles App
    related_municipal_profile = models.ForeignKey(
        "municipal_profiles.MunicipalOBCProfile",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="tasks",
        help_text="Related municipal profile",
    )

    # Data Imports App
    related_import = models.ForeignKey(
        "data_imports.DataImport",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="tasks",
        help_text="Related data import",
    )

    # Project Central App (Integrated Project Management)
    linked_workflow = models.ForeignKey(
        "project_central.ProjectWorkflow",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="tasks",
        help_text="Link task to project workflow",
    )

    linked_ppa = models.ForeignKey(
        "monitoring.MonitoringEntry",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="workflow_tasks",
        help_text="Link task to PPA (for workflow tasks)",
    )

    workflow_stage = models.CharField(
        max_length=30,
        blank=True,
        help_text="Workflow stage this task belongs to",
    )

    auto_generated = models.BooleanField(
        default=False,
        help_text="Whether this task was automatically generated by workflow automation",
    )

    # AI Assistant App (commented out - app not installed)
    # related_ai_conversation = models.ForeignKey(
    #     "ai_assistant.AIConversation",
    #     null=True,
    #     blank=True,
    #     on_delete=models.SET_NULL,
    #     related_name="tasks",
    #     help_text="Related AI conversation",
    # )
    # related_ai_document = models.ForeignKey(
    #     "ai_assistant.AIGeneratedDocument",
    #     null=True,
    #     blank=True,
    #     on_delete=models.SET_NULL,
    #     related_name="tasks",
    #     help_text="Related AI-generated document",
    # )

    # ========== DOMAIN-SPECIFIC CATEGORIZATION ==========

    DOMAIN_GENERAL = "general"
    DOMAIN_COMMUNITIES = "communities"
    DOMAIN_MANA = "mana"
    DOMAIN_COORDINATION = "coordination"
    DOMAIN_MONITORING = "monitoring"
    DOMAIN_POLICY = "policy"
    DOMAIN_SERVICES = "services"
    DOMAIN_MUNICIPAL = "municipal"
    DOMAIN_DATA = "data"
    DOMAIN_AI = "ai"
    DOMAIN_PROJECT_CENTRAL = "project_central"
    DOMAIN_CHOICES = [
        (DOMAIN_GENERAL, "General Staff Task"),
        (DOMAIN_COMMUNITIES, "Community Management"),
        (DOMAIN_MANA, "MANA Assessment"),
        (DOMAIN_COORDINATION, "Coordination & Partnerships"),
        (DOMAIN_MONITORING, "Monitoring & Evaluation"),
        (DOMAIN_POLICY, "Policy Development"),
        (DOMAIN_SERVICES, "Service Delivery"),
        (DOMAIN_MUNICIPAL, "Municipal Profiles"),
        (DOMAIN_DATA, "Data Management"),
        (DOMAIN_AI, "AI Operations"),
        (DOMAIN_PROJECT_CENTRAL, "Project Management"),
    ]

    domain = models.CharField(
        max_length=30,
        choices=DOMAIN_CHOICES,
        default=DOMAIN_GENERAL,
        blank=True,
        help_text="Domain/module this task belongs to",
    )

    task_category = models.CharField(
        max_length=50,
        blank=True,
        help_text="Specific task type within domain",
    )

    # ========== TASK CONTEXT (Phase 1 - Project-Activity Integration) ==========

    TASK_CONTEXT_STANDALONE = "standalone"
    TASK_CONTEXT_PROJECT = "project"
    TASK_CONTEXT_ACTIVITY = "activity"
    TASK_CONTEXT_PROJECT_ACTIVITY = "project_activity"
    TASK_CONTEXT_CHOICES = [
        (TASK_CONTEXT_STANDALONE, "Standalone Task"),
        (TASK_CONTEXT_PROJECT, "Project Task"),
        (TASK_CONTEXT_ACTIVITY, "Activity/Event Task"),
        (TASK_CONTEXT_PROJECT_ACTIVITY, "Project Activity Task"),
    ]

    task_context = models.CharField(
        max_length=20,
        choices=TASK_CONTEXT_CHOICES,
        default=TASK_CONTEXT_STANDALONE,
        blank=True,
        help_text="Context in which this task exists (standalone, project, activity, or both)",
    )

    # ========== WORKFLOW-SPECIFIC FIELDS ==========

    # MANA-specific
    ASSESSMENT_PHASE_PLANNING = "planning"
    ASSESSMENT_PHASE_DATA_COLLECTION = "data_collection"
    ASSESSMENT_PHASE_ANALYSIS = "analysis"
    ASSESSMENT_PHASE_REPORT_WRITING = "report_writing"
    ASSESSMENT_PHASE_REVIEW = "review"
    ASSESSMENT_PHASE_CHOICES = [
        (ASSESSMENT_PHASE_PLANNING, "Planning"),
        (ASSESSMENT_PHASE_DATA_COLLECTION, "Data Collection"),
        (ASSESSMENT_PHASE_ANALYSIS, "Analysis"),
        (ASSESSMENT_PHASE_REPORT_WRITING, "Report Writing"),
        (ASSESSMENT_PHASE_REVIEW, "Review"),
    ]

    assessment_phase = models.CharField(
        max_length=30,
        choices=ASSESSMENT_PHASE_CHOICES,
        blank=True,
        help_text="Which assessment phase this task supports",
    )

    deliverable_type = models.CharField(
        max_length=50,
        blank=True,
        help_text="Expected deliverable (survey_data, analysis_report, etc.)",
    )

    geographic_scope = models.JSONField(
        default=dict,
        blank=True,
        help_text="Geographic coverage: {region, province, municipality, barangay}",
    )

    # Policy-specific
    POLICY_PHASE_DRAFTING = "drafting"
    POLICY_PHASE_EVIDENCE = "evidence_collection"
    POLICY_PHASE_REVIEW = "review"
    POLICY_PHASE_CONSULTATION = "consultation"
    POLICY_PHASE_SUBMISSION = "submission"
    POLICY_PHASE_IMPLEMENTATION = "implementation"
    POLICY_PHASE_MONITORING = "monitoring"
    POLICY_PHASE_CHOICES = [
        (POLICY_PHASE_DRAFTING, "Drafting"),
        (POLICY_PHASE_EVIDENCE, "Evidence Collection"),
        (POLICY_PHASE_REVIEW, "Review & Revision"),
        (POLICY_PHASE_CONSULTATION, "Stakeholder Consultation"),
        (POLICY_PHASE_SUBMISSION, "Submission & Approval"),
        (POLICY_PHASE_IMPLEMENTATION, "Implementation"),
        (POLICY_PHASE_MONITORING, "Monitoring & Evaluation"),
    ]

    policy_phase = models.CharField(
        max_length=30,
        choices=POLICY_PHASE_CHOICES,
        blank=True,
        help_text="Which policy phase this task supports",
    )

    # Service-specific
    SERVICE_PHASE_SETUP = "setup"
    SERVICE_PHASE_REVIEW = "application_review"
    SERVICE_PHASE_DELIVERY = "delivery"
    SERVICE_PHASE_FOLLOWUP = "followup"
    SERVICE_PHASE_REPORTING = "reporting"
    SERVICE_PHASE_CHOICES = [
        (SERVICE_PHASE_SETUP, "Service Setup"),
        (SERVICE_PHASE_REVIEW, "Application Review"),
        (SERVICE_PHASE_DELIVERY, "Service Delivery"),
        (SERVICE_PHASE_FOLLOWUP, "Follow-up"),
        (SERVICE_PHASE_REPORTING, "Reporting"),
    ]

    service_phase = models.CharField(
        max_length=30,
        choices=SERVICE_PHASE_CHOICES,
        blank=True,
        help_text="Which service phase this task supports",
    )

    # Monitoring-specific (from MonitoringEntryTaskAssignment)
    TASK_ROLE_LEAD = "lead"
    TASK_ROLE_CONTRIBUTOR = "contributor"
    TASK_ROLE_REVIEWER = "reviewer"
    TASK_ROLE_APPROVER = "approver"
    TASK_ROLE_MONITOR = "monitor"
    TASK_ROLE_CHOICES = [
        (TASK_ROLE_LEAD, "Lead"),
        (TASK_ROLE_CONTRIBUTOR, "Contributor"),
        (TASK_ROLE_REVIEWER, "Reviewer"),
        (TASK_ROLE_APPROVER, "Approver"),
        (TASK_ROLE_MONITOR, "Monitor"),
    ]

    task_role = models.CharField(
        max_length=20,
        choices=TASK_ROLE_CHOICES,
        blank=True,
        help_text="Role of assignee in this task",
    )

    estimated_hours = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Estimated effort in hours",
    )

    actual_hours = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Actual effort spent in hours",
    )

    # ========== TASK DEPENDENCIES (OPTIONAL - MILESTONE 6) ==========
    depends_on = models.ManyToManyField(
        "self",
        symmetrical=False,
        related_name="dependent_tasks",
        blank=True,
        help_text="Tasks this task depends on",
    )

    # ========== TEMPLATE SUPPORT ==========
    created_from_template = models.ForeignKey(
        "TaskTemplate",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="created_tasks",
        help_text="Template this task was created from",
    )

    class Meta:
        ordering = ["board_position", "due_date", "-priority", "title"]
        indexes = [
            models.Index(fields=["domain", "status"]),
            models.Index(fields=["related_assessment", "assessment_phase"]),
            models.Index(fields=["related_ppa", "task_role"]),
            models.Index(fields=["related_policy", "policy_phase"]),
            models.Index(fields=["linked_event"]),
            models.Index(fields=["due_date", "status"]),
            models.Index(fields=["task_context", "status"]),
        ]

    def __init__(self, *args, **kwargs):
        self._pending_team_assignment = kwargs.pop("team", None)
        super().__init__(*args, **kwargs)

    def __str__(self):
        return self.title

    def clean(self):
        super().clean()

        domain_fks = [
            "related_training",
            "related_dev_plan",
            "related_performance_target",
            "linked_event",
            "related_community",
            "related_stakeholder",
            "related_engagement",
            "related_municipality_coverage",
            "related_assessment",
            "related_survey",
            "related_workshop",
            "related_baseline",
            "related_need",
            "related_mapping",
            "related_organization",
            "related_partnership",
            "related_partnership_milestone",
            "related_communication",
            "related_mao_focal_person",
            "related_ppa",
            "related_funding_flow",
            "related_workflow_stage",
            "related_outcome_indicator",
            "related_strategic_goal",
            "related_policy",
            "related_policy_milestone",
            "related_policy_evidence",
            "related_service",
            "related_application",
            "related_municipal_profile",
            "related_import",
            "linked_workflow",
            "linked_ppa",
        ]

        set_relations = [
            field_name for field_name in domain_fks if getattr(self, field_name)
        ]

        if len(set_relations) > 1:
            raise ValidationError(
                {
                    "__all__": "Task can only be linked to one primary domain object",
                }
            )

        if self.recurrence_pattern and not self.start_date:
            raise ValidationError(
                {
                    "start_date": "Recurring tasks must define a start date",
                }
            )

        # Validate task_context consistency (warnings only, not errors)
        import logging

        logger = logging.getLogger(__name__)

        if self.task_context == self.TASK_CONTEXT_PROJECT and not self.linked_workflow:
            logger.warning(
                f"Task {self.id or 'new'} has context 'project' but no linked_workflow"
            )

        if self.task_context == self.TASK_CONTEXT_ACTIVITY and not self.linked_event:
            logger.warning(
                f"Task {self.id or 'new'} has context 'activity' but no linked_event"
            )

        if self.task_context == self.TASK_CONTEXT_PROJECT_ACTIVITY:
            if not self.linked_workflow or not self.linked_event:
                logger.warning(
                    f"Task {self.id or 'new'} has context 'project_activity' but missing workflow or event"
                )

    def save(self, *args, **kwargs):
        pending_team = getattr(self, "_pending_team_assignment", None)
        super().save(*args, **kwargs)

        if pending_team is not None:
            resolved_teams = self._resolve_team_values(pending_team)
            if resolved_teams:
                self.teams.set(resolved_teams)
            else:
                self.teams.clear()
            self._pending_team_assignment = None

    def _resolve_team_values(self, value):
        """Normalize team inputs into iterable of StaffTeam instances."""

        if value is None:
            return []
        if isinstance(value, StaffTeam):
            return [value]
        if isinstance(value, (list, tuple, set)):
            resolved = []
            for item in value:
                resolved.extend(self._resolve_team_values(item))
            return resolved
        if isinstance(value, int):
            try:
                return [StaffTeam.objects.get(pk=value)]
            except StaffTeam.DoesNotExist:
                return []
        raise ValueError("Unsupported team assignment value.")

    @property
    def is_overdue(self):
        """Return True if the task is overdue."""
        if self.status == self.STATUS_COMPLETED or not self.due_date:
            return False
        return self.due_date < timezone.now().date()

    @property
    def assignee_display_name(self):
        """Return a human-friendly assignee label, handling missing data."""

        members = []
        if hasattr(self, "assignees"):
            try:
                members = list(self.assignees.all())
            except Exception:
                members = []
        if not members:
            return "Unassigned"

        def _display_name(user_obj):
            if not user_obj:
                return ""
            if hasattr(user_obj, "get_full_name"):
                full_name = (user_obj.get_full_name() or "").strip()
                if full_name:
                    return full_name
            username = getattr(user_obj, "username", "")
            return username

        labels = [
            label for label in (_display_name(member) for member in members) if label
        ]
        if not labels:
            return "Unassigned"
        return ", ".join(labels)

    @property
    def primary_domain_object(self):
        """Return the primary domain object this task is linked to."""
        for field_name in [
            "related_assessment",
            "related_survey",
            "related_workshop",
            "related_baseline",
            "related_need",
            "related_ppa",
            "related_policy",
            "linked_event",
            "related_service",
            "related_community",
            "related_organization",
            "related_partnership",
            "related_stakeholder",
            "related_application",
            "related_municipal_profile",
            "related_import",
            "related_training",
        ]:
            obj = getattr(self, field_name, None)
            if obj:
                return obj
        return None

    @property
    def domain_display(self):
        """Return human-friendly domain name."""
        return dict(self.DOMAIN_CHOICES).get(self.domain, "General")

    @property
    def team(self):
        """Return the first associated team for legacy access patterns."""

        if not hasattr(self, "teams"):
            return None
        try:
            return self.teams.all().first()
        except Exception:  # pragma: no cover - defensive fallback
            return None

    @team.setter
    def team(self, value):
        self._pending_team_assignment = value


class TaskTemplate(models.Model):
    """Reusable task templates for workflows."""

    name = models.CharField(max_length=255, unique=True)
    domain = models.CharField(
        max_length=30,
        choices=StaffTask.DOMAIN_CHOICES,
        help_text="Domain this template applies to",
    )
    description = models.TextField(blank=True)
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this template is available for use",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["domain", "name"]

    def __str__(self):
        return f"{self.get_domain_display()}: {self.name}"


class TaskTemplateItem(models.Model):
    """Individual task item within a template."""

    template = models.ForeignKey(
        TaskTemplate,
        on_delete=models.CASCADE,
        related_name="items",
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    task_category = models.CharField(max_length=50, blank=True)
    priority = models.CharField(
        max_length=12,
        choices=StaffTask.PRIORITY_CHOICES,
        default=StaffTask.PRIORITY_MEDIUM,
    )
    estimated_hours = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Estimated effort in hours",
    )
    sequence = models.PositiveIntegerField(
        default=0,
        help_text="Order of this task in the template",
    )
    days_from_start = models.PositiveIntegerField(
        default=0,
        help_text="Due date offset from parent entity start date",
    )

    # Phase-specific fields (populated based on template domain)
    assessment_phase = models.CharField(
        max_length=30,
        choices=StaffTask.ASSESSMENT_PHASE_CHOICES,
        blank=True,
    )
    policy_phase = models.CharField(
        max_length=30,
        choices=StaffTask.POLICY_PHASE_CHOICES,
        blank=True,
    )
    service_phase = models.CharField(
        max_length=30,
        choices=StaffTask.SERVICE_PHASE_CHOICES,
        blank=True,
    )
    task_role = models.CharField(
        max_length=20,
        choices=StaffTask.TASK_ROLE_CHOICES,
        blank=True,
    )

    class Meta:
        ordering = ["template", "sequence"]

    def __str__(self):
        return f"{self.template.name} - {self.sequence}: {self.title}"


class TrainingProgram(models.Model):
    """Catalogue of training opportunities for OOBC staff."""

    MODE_IN_PERSON = "in_person"
    MODE_VIRTUAL = "virtual"
    MODE_HYBRID = "hybrid"
    DELIVERY_MODE_CHOICES = [
        (MODE_IN_PERSON, "In Person"),
        (MODE_VIRTUAL, "Virtual"),
        (MODE_HYBRID, "Hybrid"),
    ]

    title = models.CharField(max_length=255)
    category = models.CharField(max_length=150, blank=True)
    description = models.TextField(blank=True)
    delivery_mode = models.CharField(
        max_length=20, choices=DELIVERY_MODE_CHOICES, default=MODE_IN_PERSON
    )
    competency_focus = models.JSONField(default=list, blank=True)
    duration_days = models.PositiveIntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return self.title


class TrainingEnrollment(models.Model):
    """Link staff to training programmes for development tracking."""

    STATUS_PLANNED = "planned"
    STATUS_ONGOING = "ongoing"
    STATUS_COMPLETED = "completed"
    STATUS_CANCELLED = "cancelled"
    STATUS_CHOICES = [
        (STATUS_PLANNED, "Planned"),
        (STATUS_ONGOING, "Ongoing"),
        (STATUS_COMPLETED, "Completed"),
        (STATUS_CANCELLED, "Cancelled"),
    ]

    staff_profile = models.ForeignKey(
        "StaffProfile",
        related_name="training_enrollments",
        on_delete=models.CASCADE,
    )
    program = models.ForeignKey(
        "TrainingProgram",
        related_name="enrollments",
        on_delete=models.CASCADE,
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default=STATUS_PLANNED
    )
    scheduled_date = models.DateField(null=True, blank=True)
    completion_date = models.DateField(null=True, blank=True)
    evidence_url = models.URLField(blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-scheduled_date", "program__title"]

    def __str__(self):
        return f"{self.staff_profile.user.get_full_name()} - {self.program.title}"


class StaffDevelopmentPlan(models.Model):
    """Individual development actions per staff member."""

    STATUS_PLANNED = "planned"
    STATUS_IN_PROGRESS = "in_progress"
    STATUS_COMPLETED = "completed"
    STATUS_CHOICES = [
        (STATUS_PLANNED, "Planned"),
        (STATUS_IN_PROGRESS, "In Progress"),
        (STATUS_COMPLETED, "Completed"),
    ]

    staff_profile = models.ForeignKey(
        "StaffProfile",
        related_name="development_plans",
        on_delete=models.CASCADE,
    )
    title = models.CharField(max_length=255)
    competency_focus = models.CharField(max_length=150, blank=True)
    target_date = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default=STATUS_PLANNED
    )
    support_needed = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["target_date", "title"]

    def __str__(self):
        return f"Development Plan: {self.title} ({self.staff_profile.user.get_full_name()})"


class PerformanceTarget(models.Model):
    """Targets and actuals for staff or team performance dashboards."""

    SCOPE_STAFF = "staff"
    SCOPE_TEAM = "team"
    SCOPE_CHOICES = [
        (SCOPE_STAFF, "Staff"),
        (SCOPE_TEAM, "Team"),
    ]

    STATUS_ON_TRACK = "on_track"
    STATUS_AT_RISK = "at_risk"
    STATUS_OFF_TRACK = "off_track"
    STATUS_CHOICES = [
        (STATUS_ON_TRACK, "On Track"),
        (STATUS_AT_RISK, "At Risk"),
        (STATUS_OFF_TRACK, "Off Track"),
    ]

    scope = models.CharField(max_length=10, choices=SCOPE_CHOICES)
    staff_profile = models.ForeignKey(
        "StaffProfile",
        related_name="performance_targets",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    team = models.ForeignKey(
        "StaffTeam",
        related_name="performance_targets",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    metric_name = models.CharField(max_length=150)
    performance_standard = models.CharField(max_length=255, blank=True)
    target_value = models.DecimalField(max_digits=10, decimal_places=2)
    actual_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    unit = models.CharField(max_length=50, blank=True)
    status = models.CharField(
        max_length=12, choices=STATUS_CHOICES, default=STATUS_ON_TRACK
    )
    period_start = models.DateField()
    period_end = models.DateField()
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-period_end", "metric_name"]

    def __str__(self):
        scope_label = dict(self.SCOPE_CHOICES).get(self.scope, self.scope)
        return f"{scope_label} Target: {self.metric_name}"

    def clean(self):
        """Ensure the appropriate relation is populated based on scope."""

        if self.scope == self.SCOPE_STAFF and not self.staff_profile:
            raise ValidationError("Staff targets require a staff profile.")
        if self.scope == self.SCOPE_TEAM and not self.team:
            raise ValidationError("Team targets require a team.")
        if self.scope == self.SCOPE_STAFF and self.team:
            raise ValidationError("Staff targets cannot be linked to a team.")
        if self.scope == self.SCOPE_TEAM and self.staff_profile:
            raise ValidationError("Team targets cannot be linked to a staff profile.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


# =====================================================================
# Calendar System Models
# =====================================================================


class RecurringEventPattern(models.Model):
    """
    Defines recurrence rules for events (RFC 5545 iCalendar compatible).
    Used to create repeating events like weekly meetings or monthly reviews.
    """

    RECURRENCE_DAILY = "daily"
    RECURRENCE_WEEKLY = "weekly"
    RECURRENCE_MONTHLY = "monthly"
    RECURRENCE_YEARLY = "yearly"
    RECURRENCE_TYPE_CHOICES = [
        (RECURRENCE_DAILY, "Daily"),
        (RECURRENCE_WEEKLY, "Weekly"),
        (RECURRENCE_MONTHLY, "Monthly"),
        (RECURRENCE_YEARLY, "Yearly"),
    ]

    recurrence_type = models.CharField(
        max_length=20,
        choices=RECURRENCE_TYPE_CHOICES,
        help_text="Type of recurrence pattern",
    )
    interval = models.PositiveIntegerField(
        default=1,
        help_text="Repeat every N days/weeks/months (e.g., 2 = every 2 weeks)",
    )

    # For weekly: days of week (Monday=1, Sunday=7)
    by_weekday = models.JSONField(
        default=list,
        blank=True,
        help_text="List of weekdays: [1,3,5] = Mon, Wed, Fri",
    )

    # For monthly: day of month or relative (first Monday, last Friday)
    by_monthday = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Day of month (1-31)",
    )
    by_setpos = models.JSONField(
        default=list,
        blank=True,
        help_text="Relative position: [1, 'monday'] = first Monday",
    )

    # End conditions
    count = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="End after N occurrences",
    )
    until_date = models.DateField(
        null=True,
        blank=True,
        help_text="End by this date",
    )

    # Exceptions (dates to skip)
    exception_dates = models.JSONField(
        default=list,
        blank=True,
        help_text="List of ISO dates to exclude from recurrence",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "common_recurring_event_pattern"
        verbose_name = "Recurring Event Pattern"
        verbose_name_plural = "Recurring Event Patterns"

    def __str__(self):
        return f"{self.get_recurrence_type_display()} (every {self.interval})"

    def get_occurrences(
        self, *, start_date: date, limit: int | None = None
    ) -> list[date]:
        """Generate recurrence dates honoring count, until, and exceptions."""

        if not isinstance(start_date, date):
            raise ValueError("start_date must be a datetime.date instance")

        if self.interval < 1:
            raise ValidationError("Interval must be at least 1")

        if self.until_date and start_date > self.until_date:
            return []

        max_occurrences = limit if limit is not None else self.count
        if max_occurrences is not None and max_occurrences <= 0:
            return []

        if max_occurrences is None and self.until_date is None:
            max_occurrences = 1000

        excluded = {value for value in (self.exception_dates or [])}
        occurrences: list[date] = []

        def include(candidate: date) -> bool:
            if self.until_date and candidate > self.until_date:
                return False
            if candidate.isoformat() in excluded:
                return False
            occurrences.append(candidate)
            return True

        if self.recurrence_type == self.RECURRENCE_DAILY:
            current = start_date
            while True:
                include(current)
                if max_occurrences is not None and len(occurrences) >= max_occurrences:
                    break
                current += timedelta(days=self.interval)
                if self.until_date and current > self.until_date:
                    break

        elif self.recurrence_type == self.RECURRENCE_WEEKLY:
            weekdays = sorted(
                {weekday for weekday in (self.by_weekday or []) if 1 <= weekday <= 7}
            )
            if not weekdays:
                weekdays = [start_date.isoweekday()]

            # Align to the beginning of the week containing the start date (Monday = 1)
            base_week_start = start_date - timedelta(days=start_date.isoweekday() - 1)
            week_index = 0

            while True:
                week_start = base_week_start + timedelta(
                    weeks=week_index * self.interval
                )
                for weekday in weekdays:
                    candidate = week_start + timedelta(days=weekday - 1)
                    if candidate < start_date:
                        continue
                    if self.until_date and candidate > self.until_date:
                        return occurrences
                    if candidate.isoformat() in excluded:
                        continue
                    occurrences.append(candidate)
                    if (
                        max_occurrences is not None
                        and len(occurrences) >= max_occurrences
                    ):
                        return occurrences
                week_index += 1

        elif self.recurrence_type == self.RECURRENCE_MONTHLY:
            monthday = self.by_monthday or start_date.day
            current = start_date
            increments = 0

            while True:
                year = current.year + (
                    (current.month - 1 + increments * self.interval) // 12
                )
                month = ((current.month - 1 + increments * self.interval) % 12) + 1
                day = min(monthday, monthrange(year, month)[1])
                candidate = date(year, month, day)
                if candidate < start_date:
                    increments += 1
                    continue
                if self.until_date and candidate > self.until_date:
                    break
                if candidate.isoformat() not in excluded:
                    occurrences.append(candidate)
                if max_occurrences is not None and len(occurrences) >= max_occurrences:
                    break
                increments += 1

        elif self.recurrence_type == self.RECURRENCE_YEARLY:
            current = start_date
            increments = 0

            while True:
                candidate = date(
                    current.year + increments * self.interval,
                    current.month,
                    current.day,
                )
                if candidate < start_date:
                    increments += 1
                    continue
                if self.until_date and candidate > self.until_date:
                    break
                if candidate.isoformat() not in excluded:
                    occurrences.append(candidate)
                if max_occurrences is not None and len(occurrences) >= max_occurrences:
                    break
                increments += 1

        else:
            raise ValidationError("Unsupported recurrence type")

        return occurrences


class CalendarResource(models.Model):
    """
    Bookable resources for events: vehicles, equipment, meeting rooms, facilitators.
    Enables resource scheduling and conflict prevention.
    """

    RESOURCE_VEHICLE = "vehicle"
    RESOURCE_EQUIPMENT = "equipment"
    RESOURCE_ROOM = "room"
    RESOURCE_FACILITATOR = "facilitator"
    RESOURCE_TYPE_CHOICES = [
        (RESOURCE_VEHICLE, "Vehicle"),
        (RESOURCE_EQUIPMENT, "Equipment"),
        (RESOURCE_ROOM, "Meeting Room"),
        (RESOURCE_FACILITATOR, "Facilitator/Trainer"),
    ]

    resource_type = models.CharField(
        max_length=20,
        choices=RESOURCE_TYPE_CHOICES,
        help_text="Type of resource",
    )
    name = models.CharField(max_length=255, help_text="Resource name")
    description = models.TextField(blank=True)
    capacity = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Max people (for rooms) or units available",
    )
    location = models.CharField(max_length=255, blank=True)

    # Availability
    is_available = models.BooleanField(
        default=True,
        help_text="Whether resource is currently available for booking",
    )
    booking_requires_approval = models.BooleanField(
        default=False,
        help_text="Whether bookings require approval",
    )

    # Cost
    cost_per_use = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Cost per use (optional)",
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "common_calendar_resource"
        ordering = ["resource_type", "name"]
        verbose_name = "Calendar Resource"
        verbose_name_plural = "Calendar Resources"

    def __str__(self):
        return f"{self.get_resource_type_display()}: {self.name}"

    @property
    def requires_approval(self) -> bool:
        """Compatibility alias for legacy booking approval flag."""

        return self.booking_requires_approval

    @property
    def status(self) -> str:
        """Return human-friendly availability status."""

        return "available" if self.is_available else "unavailable"

    @status.setter
    def status(self, value: str) -> None:
        """Allow legacy code to set status via string labels."""

        self.is_available = (value or "").lower() == "available"

    @property
    def allow_booking_advance_days(self) -> int:
        """Return allowed advance booking window; defaults to no limit."""

        return 0

    @property
    def max_booking_duration_hours(self) -> int:
        """Return maximum booking duration; defaults to unlimited."""

        return 0


class CalendarResourceBooking(models.Model):
    """
    Links events to resources for scheduling and conflict detection.
    Uses GenericForeignKey to support multiple event types.
    """

    STATUS_PENDING = "pending"
    STATUS_APPROVED = "approved"
    STATUS_REJECTED = "rejected"
    STATUS_CANCELLED = "cancelled"
    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending Approval"),
        (STATUS_APPROVED, "Approved"),
        (STATUS_REJECTED, "Rejected"),
        (STATUS_CANCELLED, "Cancelled"),
    ]

    resource = models.ForeignKey(
        CalendarResource,
        on_delete=models.CASCADE,
        related_name="bookings",
    )

    # Polymorphic: can link to Event, StakeholderEngagement, StaffTask, etc.
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    object_id = models.UUIDField(null=True, blank=True)
    event_instance = GenericForeignKey("content_type", "object_id")

    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
    )

    booked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="resource_bookings",
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        related_name="approved_resource_bookings",
        on_delete=models.SET_NULL,
    )

    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "common_calendar_resource_booking"
        indexes = [
            models.Index(fields=["start_datetime", "end_datetime"]),
            models.Index(fields=["resource", "status"]),
        ]
        verbose_name = "Calendar Resource Booking"
        verbose_name_plural = "Calendar Resource Bookings"

    def __str__(self):
        return f"{self.resource.name} - {self.start_datetime.date()}"

    def clean(self):
        """Check for overlapping bookings."""
        if not self.start_datetime or not self.end_datetime:
            return

        overlaps = CalendarResourceBooking.objects.filter(
            resource=self.resource,
            status__in=[self.STATUS_PENDING, self.STATUS_APPROVED],
            start_datetime__lt=self.end_datetime,
            end_datetime__gt=self.start_datetime,
        ).exclude(pk=self.pk)

        if overlaps.exists():
            raise ValidationError(
                f"Resource '{self.resource.name}' is already booked during this time."
            )

    def save(self, *args, **kwargs):
        result = super().save(*args, **kwargs)
        _invalidate_calendar_cache()
        return result

    def delete(self, *args, **kwargs):
        result = super().delete(*args, **kwargs)
        _invalidate_calendar_cache()
        return result


class CalendarNotification(models.Model):
    """
    Scheduled notifications for calendar events.
    Supports email, SMS, push, and in-app notifications.
    """

    NOTIFICATION_INVITATION = "invitation"
    NOTIFICATION_REMINDER = "reminder"
    NOTIFICATION_UPDATE = "update"
    NOTIFICATION_CANCELLATION = "cancellation"
    NOTIFICATION_RSVP_REQUEST = "rsvp_request"
    NOTIFICATION_TYPE_CHOICES = [
        (NOTIFICATION_INVITATION, "Event Invitation"),
        (NOTIFICATION_REMINDER, "Reminder"),
        (NOTIFICATION_UPDATE, "Event Updated"),
        (NOTIFICATION_CANCELLATION, "Event Cancelled"),
        (NOTIFICATION_RSVP_REQUEST, "RSVP Request"),
    ]

    DELIVERY_EMAIL = "email"
    DELIVERY_SMS = "sms"
    DELIVERY_PUSH = "push"
    DELIVERY_IN_APP = "in_app"
    DELIVERY_METHOD_CHOICES = [
        (DELIVERY_EMAIL, "Email"),
        (DELIVERY_SMS, "SMS"),
        (DELIVERY_PUSH, "Push Notification"),
        (DELIVERY_IN_APP, "In-App"),
    ]

    STATUS_PENDING = "pending"
    STATUS_SENT = "sent"
    STATUS_FAILED = "failed"
    STATUS_CANCELLED = "cancelled"
    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_SENT, "Sent"),
        (STATUS_FAILED, "Failed"),
        (STATUS_CANCELLED, "Cancelled"),
    ]

    # Polymorphic link to event
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    object_id = models.UUIDField(null=True, blank=True)
    event_instance = GenericForeignKey("content_type", "object_id")

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="calendar_notifications",
    )

    notification_type = models.CharField(
        max_length=20,
        choices=NOTIFICATION_TYPE_CHOICES,
    )

    delivery_method = models.CharField(
        max_length=20,
        choices=DELIVERY_METHOD_CHOICES,
    )

    scheduled_for = models.DateTimeField(help_text="When to send notification")
    sent_at = models.DateTimeField(null=True, blank=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
    )

    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "common_calendar_notification"
        indexes = [
            models.Index(fields=["scheduled_for", "status"]),
            models.Index(fields=["recipient", "scheduled_for"]),
        ]
        verbose_name = "Calendar Notification"
        verbose_name_plural = "Calendar Notifications"

    def __str__(self):
        return f"{self.get_notification_type_display()} to {self.recipient.get_full_name()}"


class UserCalendarPreferences(models.Model):
    """User preferences for calendar notifications and settings."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="calendar_preferences",
    )

    # Default reminder times (minutes before event)
    default_reminder_times = models.JSONField(
        default=list,
        blank=True,
        help_text="List of minutes: [1440, 60] = 1 day, 1 hour before",
    )

    # Notification channels
    email_enabled = models.BooleanField(default=True)
    sms_enabled = models.BooleanField(default=False)
    push_enabled = models.BooleanField(default=True)

    # Digest emails
    daily_digest = models.BooleanField(default=False)
    weekly_digest = models.BooleanField(default=True)

    # Quiet hours
    quiet_hours_start = models.TimeField(
        null=True,
        blank=True,
        help_text="Don't send notifications after this time",
    )
    quiet_hours_end = models.TimeField(
        null=True,
        blank=True,
        help_text="Resume notifications after this time",
    )

    # Timezone
    timezone = models.CharField(
        max_length=50,
        default="Asia/Manila",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "common_user_calendar_preferences"
        verbose_name = "User Calendar Preferences"
        verbose_name_plural = "User Calendar Preferences"

    def __str__(self):
        return f"Calendar Preferences: {self.user.get_full_name()}"


class ExternalCalendarSync(models.Model):
    """
    Sync configuration for external calendars (Google, Outlook, Apple).
    Enables two-way synchronization of events.
    """

    PROVIDER_GOOGLE = "google"
    PROVIDER_MICROSOFT = "microsoft"
    PROVIDER_APPLE = "apple"
    PROVIDER_CHOICES = [
        (PROVIDER_GOOGLE, "Google Calendar"),
        (PROVIDER_MICROSOFT, "Microsoft Outlook"),
        (PROVIDER_APPLE, "Apple iCloud"),
    ]

    SYNC_EXPORT_ONLY = "export_only"
    SYNC_IMPORT_ONLY = "import_only"
    SYNC_TWO_WAY = "two_way"
    SYNC_DIRECTION_CHOICES = [
        (SYNC_EXPORT_ONLY, "Export to external calendar only"),
        (SYNC_IMPORT_ONLY, "Import from external calendar only"),
        (SYNC_TWO_WAY, "Two-way sync"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="external_calendar_syncs",
    )
    provider = models.CharField(
        max_length=20,
        choices=PROVIDER_CHOICES,
    )

    # OAuth tokens (should be encrypted in production)
    access_token = models.TextField()
    refresh_token = models.TextField()
    token_expires_at = models.DateTimeField()

    # Settings
    sync_direction = models.CharField(
        max_length=20,
        choices=SYNC_DIRECTION_CHOICES,
        default=SYNC_EXPORT_ONLY,
    )

    # Which OOBC modules to sync
    sync_modules = models.JSONField(
        default=list,
        blank=True,
        help_text="List of module keys: ['coordination', 'staff', 'mana']",
    )

    last_sync_at = models.DateTimeField(null=True, blank=True)
    sync_status = models.CharField(max_length=50, blank=True)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "common_external_calendar_sync"
        verbose_name = "External Calendar Sync"
        verbose_name_plural = "External Calendar Syncs"

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.get_provider_display()}"


class SharedCalendarLink(models.Model):
    """
    Temporary view-only calendar access via shareable links.
    Enables calendar sharing without requiring authentication.
    """

    token = models.UUIDField(default=uuid.uuid4, unique=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="shared_calendar_links",
    )

    # Access control
    expires_at = models.DateTimeField()
    max_views = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Maximum number of views allowed (optional)",
    )
    view_count = models.PositiveIntegerField(default=0)

    # Filters
    filter_modules = models.JSONField(
        default=list,
        blank=True,
        help_text="Modules to include in shared view",
    )
    filter_date_from = models.DateField(null=True, blank=True)
    filter_date_to = models.DateField(null=True, blank=True)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "common_shared_calendar_link"
        verbose_name = "Shared Calendar Link"
        verbose_name_plural = "Shared Calendar Links"

    def __str__(self):
        return f"Shared Link by {self.created_by.get_full_name()}"


class StaffLeave(models.Model):
    """
    Staff leave/vacation tracking for calendar integration.
    Helps with resource planning and availability.
    """

    LEAVE_VACATION = "vacation"
    LEAVE_SICK = "sick"
    LEAVE_EMERGENCY = "emergency"
    LEAVE_OFFICIAL = "official"
    LEAVE_TYPE_CHOICES = [
        (LEAVE_VACATION, "Vacation Leave"),
        (LEAVE_SICK, "Sick Leave"),
        (LEAVE_EMERGENCY, "Emergency Leave"),
        (LEAVE_OFFICIAL, "Official Business"),
    ]

    STATUS_PENDING = "pending"
    STATUS_APPROVED = "approved"
    STATUS_REJECTED = "rejected"
    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending Approval"),
        (STATUS_APPROVED, "Approved"),
        (STATUS_REJECTED, "Rejected"),
    ]

    staff = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="leave_requests",
    )

    leave_type = models.CharField(
        max_length=20,
        choices=LEAVE_TYPE_CHOICES,
    )

    start_date = models.DateField()
    end_date = models.DateField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
    )

    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        related_name="approved_leaves",
        on_delete=models.SET_NULL,
    )

    reason = models.TextField(blank=True)
    notes = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        result = super().save(*args, **kwargs)
        _invalidate_calendar_cache()
        return result

    def delete(self, *args, **kwargs):
        result = super().delete(*args, **kwargs)
        _invalidate_calendar_cache()
        return result

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "common_staff_leave"
        ordering = ["-start_date"]
        verbose_name = "Staff Leave"
        verbose_name_plural = "Staff Leaves"

    def __str__(self):
        return f"{self.staff.get_full_name()} - {self.get_leave_type_display()} ({self.start_date})"

    def clean(self):
        """Validate date range."""
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise ValidationError("End date must be after start date.")

    def save(self, *args, **kwargs):
        result = super().save(*args, **kwargs)
        _invalidate_calendar_cache()
        return result

    def delete(self, *args, **kwargs):
        result = super().delete(*args, **kwargs)
        _invalidate_calendar_cache()
        return result

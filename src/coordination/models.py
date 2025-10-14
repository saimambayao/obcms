import uuid
from datetime import datetime, time

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone

from communities.models import OBCCommunity
from mana.models import Assessment
from common.models import Region, Province, Municipality, Barangay


def _invalidate_calendar_cache() -> None:
    from common.services import calendar as calendar_service

    calendar_service.invalidate_calendar_cache()


User = get_user_model()


class StakeholderEngagementType(models.Model):
    """Types of stakeholder engagement activities."""

    ENGAGEMENT_CATEGORIES = [
        ("consultation", "Public Consultation"),
        ("meeting", "Coordination Meeting"),
        ("workshop", "Workshop/Training"),
        ("focus_group", "Focus Group Discussion"),
        ("interview", "Key Informant Interview"),
        ("survey", "Survey/Questionnaire"),
        ("courtesy_call", "Courtesy Call"),
        ("field_visit", "Field Visit"),
        ("community_assembly", "Community Assembly"),
        ("validation", "Validation Session"),
    ]

    name = models.CharField(
        max_length=100, unique=True, help_text="Name of the engagement type"
    )

    category = models.CharField(
        max_length=25, choices=ENGAGEMENT_CATEGORIES, help_text="Category of engagement"
    )

    description = models.TextField(help_text="Description of this engagement type")

    icon = models.CharField(
        max_length=50, blank=True, help_text="CSS icon class for this engagement type"
    )

    color = models.CharField(
        max_length=7, default="#007bff", help_text="Color code for this engagement type"
    )

    is_active = models.BooleanField(
        default=True, help_text="Whether this engagement type is currently active"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["category", "name"]
        verbose_name_plural = "Stakeholder Engagement Types"

    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"


class StakeholderEngagement(models.Model):
    """Model for tracking stakeholder engagement and consultation activities."""

    STATUS_CHOICES = [
        ("planned", "Planned"),
        ("scheduled", "Scheduled"),
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
        ("postponed", "Postponed"),
        ("cancelled", "Cancelled"),
    ]

    PRIORITY_LEVELS = [
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
        ("critical", "Critical"),
    ]

    PARTICIPATION_LEVELS = [
        ("inform", "Inform"),
        ("consult", "Consult"),
        ("involve", "Involve"),
        ("collaborate", "Collaborate"),
        ("empower", "Empower"),
    ]

    # Basic Information
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    title = models.CharField(
        max_length=200, help_text="Title of the engagement activity"
    )

    engagement_type = models.ForeignKey(
        StakeholderEngagementType,
        on_delete=models.PROTECT,
        help_text="Type of engagement activity",
    )

    description = models.TextField(
        help_text="Detailed description of the engagement activity"
    )

    objectives = models.TextField(help_text="Objectives and expected outcomes")

    # Relationships
    community = models.ForeignKey(
        OBCCommunity,
        on_delete=models.CASCADE,
        related_name="stakeholder_engagements",
        help_text="Primary community involved",
    )

    related_assessment = models.ForeignKey(
        Assessment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="stakeholder_engagements",
        help_text="Related assessment (if applicable)",
    )

    # Engagement Details
    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default="planned",
        help_text="Current status of the engagement",
    )

    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_LEVELS,
        default="medium",
        help_text="Priority level of this engagement",
    )

    participation_level = models.CharField(
        max_length=12,
        choices=PARTICIPATION_LEVELS,
        default="consult",
        help_text="Level of participation (IAP2 framework)",
    )

    # Timeline
    planned_date = models.DateTimeField(
        help_text="Planned date and time for the engagement"
    )

    actual_start_datetime = models.DateTimeField(
        null=True, blank=True, help_text="Actual start date and time"
    )

    actual_end_datetime = models.DateTimeField(
        null=True, blank=True, help_text="Actual end date and time"
    )

    duration_minutes = models.IntegerField(
        null=True, blank=True, help_text="Planned duration in minutes"
    )

    # Location
    venue = models.CharField(
        max_length=200, help_text="Venue or location of the engagement"
    )

    address = models.TextField(help_text="Full address of the venue")

    coordinates = models.JSONField(
        null=True,
        blank=True,
        help_text="Geographic coordinates of the venue (GeoJSON format)",
    )

    # Participants
    facilitators = models.ManyToManyField(
        User,
        through="EngagementFacilitator",
        related_name="facilitated_engagements",
        help_text="Staff members facilitating the engagement",
    )

    target_participants = models.IntegerField(help_text="Target number of participants")

    actual_participants = models.IntegerField(
        default=0, help_text="Actual number of participants"
    )

    stakeholder_groups = models.TextField(
        help_text="Description of stakeholder groups involved"
    )

    # Methodology and Resources
    methodology = models.TextField(
        help_text="Methodology and approach for the engagement"
    )

    materials_needed = models.TextField(
        blank=True, help_text="Materials and resources needed"
    )

    budget_allocated = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Budget allocated for this engagement",
    )

    actual_cost = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Actual cost incurred",
    )

    # Participatory Budgeting Extension
    is_participatory_budgeting = models.BooleanField(
        default=False,
        help_text="Whether this engagement facilitates participatory budgeting",
    )

    budget_amount_to_allocate = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Total amount to be allocated during the participatory budgeting session",
    )

    voting_open_date = models.DateField(
        null=True,
        blank=True,
        help_text="When community voting opens for participatory budgeting",
    )

    voting_close_date = models.DateField(
        null=True,
        blank=True,
        help_text="When community voting closes for participatory budgeting",
    )

    # Results and Follow-up
    key_outcomes = models.TextField(blank=True, help_text="Key outcomes and results")

    feedback_summary = models.TextField(
        blank=True, help_text="Summary of feedback received"
    )

    action_items = models.TextField(
        blank=True, help_text="Action items and follow-up activities"
    )

    satisfaction_rating = models.IntegerField(
        choices=[(i, f"{i} stars") for i in range(1, 6)],
        null=True,
        blank=True,
        help_text="Overall satisfaction rating (1-5 stars)",
    )

    # Documentation
    meeting_minutes = models.TextField(
        blank=True, help_text="Meeting minutes or detailed notes"
    )

    attendance_list = models.JSONField(
        null=True, blank=True, help_text="List of attendees (JSON format)"
    )

    # Recurrence (Enhanced with RecurringEventPattern)
    is_recurring = models.BooleanField(
        default=False, help_text="Whether this is a recurring engagement"
    )

    recurrence_pattern = models.ForeignKey(
        "common.RecurringEventPattern",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="recurring_engagements",
        help_text="Recurrence pattern configuration (RFC 5545 compatible)",
    )

    recurrence_parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="recurrence_instances",
        help_text="Parent engagement if this is a recurrence instance",
    )

    is_recurrence_exception = models.BooleanField(
        default=False,
        help_text="True if this instance was edited separately from the recurrence pattern",
    )

    # Metadata
    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="created_engagements",
        help_text="User who created this engagement",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-planned_date"]
        indexes = [
            models.Index(fields=["community", "status"]),
            models.Index(fields=["engagement_type", "planned_date"]),
            models.Index(fields=["status", "priority"]),
            models.Index(fields=["is_participatory_budgeting", "planned_date"]),
        ]

    def __str__(self):
        return f"{self.title} - {self.community.name}"

    def clean(self):
        if self.actual_end_datetime and self.actual_start_datetime:
            if self.actual_end_datetime <= self.actual_start_datetime:
                raise ValidationError("End time must be after start time")

    @property
    def actual_duration_minutes(self):
        """Calculate actual duration in minutes."""
        if self.actual_start_datetime and self.actual_end_datetime:
            delta = self.actual_end_datetime - self.actual_start_datetime
            return int(delta.total_seconds() / 60)
        return None

    @property
    def is_overdue(self):
        """Check if engagement is overdue."""
        if self.status in ["planned", "scheduled"] and self.planned_date:
            return timezone.now() > self.planned_date
        return False

    @property
    def participation_rate(self):
        """Calculate participation rate as percentage."""
        if self.target_participants > 0:
            return (self.actual_participants / self.target_participants) * 100
        return 0


class EngagementFacilitator(models.Model):
    """Through model for engagement facilitators with roles."""

    FACILITATOR_ROLES = [
        ("lead_facilitator", "Lead Facilitator"),
        ("co_facilitator", "Co-Facilitator"),
        ("note_taker", "Note Taker"),
        ("logistics_coordinator", "Logistics Coordinator"),
        ("translator", "Translator/Interpreter"),
        ("technical_expert", "Technical Expert"),
        ("observer", "Observer"),
    ]

    engagement = models.ForeignKey(StakeholderEngagement, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.CharField(
        max_length=25,
        choices=FACILITATOR_ROLES,
        help_text="Role of the facilitator in this engagement",
    )

    is_primary = models.BooleanField(
        default=False, help_text="Whether this is the primary facilitator"
    )

    notes = models.TextField(
        blank=True, help_text="Additional notes about this facilitator's role"
    )

    class Meta:
        unique_together = ["engagement", "user", "role"]

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.get_role_display()}"


class ConsultationFeedback(models.Model):
    """Model for capturing feedback from stakeholder engagements."""

    FEEDBACK_TYPES = [
        ("verbal", "Verbal Feedback"),
        ("written", "Written Feedback"),
        ("survey", "Survey Response"),
        ("observation", "Observation Notes"),
        ("complaint", "Complaint/Concern"),
        ("suggestion", "Suggestion/Recommendation"),
    ]

    SENTIMENT_CHOICES = [
        ("positive", "Positive"),
        ("neutral", "Neutral"),
        ("negative", "Negative"),
        ("mixed", "Mixed"),
    ]

    engagement = models.ForeignKey(
        StakeholderEngagement,
        on_delete=models.CASCADE,
        related_name="feedback_items",
        help_text="Engagement this feedback relates to",
    )

    feedback_type = models.CharField(
        max_length=15, choices=FEEDBACK_TYPES, help_text="Type of feedback"
    )

    participant_name = models.CharField(
        max_length=100, blank=True, help_text="Name of the participant (optional)"
    )

    participant_organization = models.CharField(
        max_length=150, blank=True, help_text="Organization the participant represents"
    )

    feedback_content = models.TextField(help_text="Content of the feedback")

    topic_area = models.CharField(
        max_length=100, blank=True, help_text="Topic or subject area of the feedback"
    )

    sentiment = models.CharField(
        max_length=10,
        choices=SENTIMENT_CHOICES,
        null=True,
        blank=True,
        help_text="Overall sentiment of the feedback",
    )

    priority_level = models.CharField(
        max_length=10,
        choices=StakeholderEngagement.PRIORITY_LEVELS,
        default="medium",
        help_text="Priority level for addressing this feedback",
    )

    # Response and Follow-up
    response_provided = models.TextField(
        blank=True, help_text="Response provided to the feedback"
    )

    action_taken = models.TextField(
        blank=True, help_text="Action taken based on this feedback"
    )

    is_addressed = models.BooleanField(
        default=False, help_text="Whether this feedback has been addressed"
    )

    addressed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="addressed_feedback",
        help_text="User who addressed this feedback",
    )

    addressed_date = models.DateTimeField(
        null=True, blank=True, help_text="Date when feedback was addressed"
    )

    # Metadata
    recorded_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="recorded_feedback",
        help_text="User who recorded this feedback",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Feedback: {self.topic_area or 'General'} - {self.engagement.title}"


class CoordinationNote(models.Model):
    """Meeting minutes and notes linked to coordination activities (WorkItems)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    note_date = models.DateField(
        help_text="Date of the coordination activity or meeting."
    )
    note_time = models.TimeField(
        null=True,
        blank=True,
        help_text="Optional start time reference for the meeting.",
    )
    work_item = models.ForeignKey(
        "common.WorkItem",
        on_delete=models.CASCADE,
        related_name="coordination_notes",
        help_text="Linked coordination activity (WorkItem with work_type='activity').",
    )
    title = models.CharField(
        max_length=255,
        help_text="Subject or title for this coordination note entry.",
    )
    location_description = models.CharField(
        max_length=255,
        blank=True,
        help_text="Venue or location details, if different from the linked activity.",
    )

    meeting_overview = models.TextField(
        blank=True,
        help_text="Objectives or high-level context for the coordination activity.",
    )
    key_agenda = models.TextField(
        blank=True,
        help_text="Agenda items covered during the meeting.",
    )
    discussion_highlights = models.TextField(
        blank=True,
        help_text="Key discussion points and insights captured during the session.",
    )
    decisions = models.TextField(
        blank=True,
        help_text="Decisions or agreements reached.",
    )
    action_items = models.TextField(
        blank=True,
        help_text="Action items with responsible persons or teams.",
    )
    follow_up_items = models.TextField(
        blank=True,
        help_text="Follow-up requirements, deadlines, or support needed.",
    )
    partnership_details = models.TextField(
        blank=True,
        help_text="Specific partnership updates, commitments, or concerns.",
    )
    attachments_links = models.TextField(
        blank=True,
        help_text="Reference links, shared folders, or document notes.",
    )
    additional_notes = models.TextField(
        blank=True,
        help_text="Other remarks, observations, or reminders.",
    )

    staff_participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name="coordination_notes_participated",
        help_text="OOBC staff who were present or contributed.",
    )
    partner_organizations = models.ManyToManyField(
        "coordination.Organization",
        blank=True,
        related_name="coordination_notes",
        help_text="Partner organizations present in the activity.",
    )
    partnership_agreements = models.ManyToManyField(
        "coordination.Partnership",
        blank=True,
        related_name="coordination_notes",
        help_text="Related partnership agreements discussed.",
    )

    coverage_region = models.ForeignKey(
        Region,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="coordination_notes",
        help_text="Region covered by this coordination effort.",
    )
    coverage_province = models.ForeignKey(
        Province,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="coordination_notes",
        help_text="Province covered by this coordination effort.",
    )
    coverage_municipality = models.ForeignKey(
        Municipality,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="coordination_notes",
        help_text="Municipality or city covered.",
    )
    coverage_barangay = models.ForeignKey(
        Barangay,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="coordination_notes",
        help_text="Barangay covered, if applicable.",
    )
    coverage_map_data = models.JSONField(
        default=dict,
        blank=True,
        help_text="Serialized map metadata for geographic coverage (pins, bounds).",
    )

    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="coordination_notes_recorded",
        help_text="Staff member who recorded these notes.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-note_date", "-created_at"]
        verbose_name = "Coordination Note"
        verbose_name_plural = "Coordination Notes"
        indexes = [
            models.Index(fields=["note_date"]),
            models.Index(fields=["work_item"]),
        ]

    def __str__(self):
        return f"{self.title} ({self.note_date:%b %d, %Y})"


class EngagementTracking(models.Model):
    """Model for tracking engagement metrics and analytics."""

    TRACKING_PERIODS = [
        ("weekly", "Weekly"),
        ("monthly", "Monthly"),
        ("quarterly", "Quarterly"),
        ("yearly", "Yearly"),
    ]

    community = models.ForeignKey(
        OBCCommunity,
        on_delete=models.CASCADE,
        related_name="engagement_tracking",
        help_text="Community being tracked",
    )

    period_type = models.CharField(
        max_length=10, choices=TRACKING_PERIODS, help_text="Tracking period type"
    )

    period_start = models.DateField(help_text="Start date of the tracking period")

    period_end = models.DateField(help_text="End date of the tracking period")

    # Engagement Metrics
    total_engagements = models.IntegerField(
        default=0, help_text="Total number of engagements in the period"
    )

    completed_engagements = models.IntegerField(
        default=0, help_text="Number of completed engagements"
    )

    total_participants = models.IntegerField(
        default=0, help_text="Total number of participants across all engagements"
    )

    unique_participants = models.IntegerField(
        default=0, help_text="Number of unique participants"
    )

    average_satisfaction = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Average satisfaction rating",
    )

    # Feedback Metrics
    total_feedback_items = models.IntegerField(
        default=0, help_text="Total number of feedback items received"
    )

    positive_feedback_count = models.IntegerField(
        default=0, help_text="Number of positive feedback items"
    )

    negative_feedback_count = models.IntegerField(
        default=0, help_text="Number of negative feedback items"
    )

    feedback_response_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Percentage of feedback items that received responses",
    )

    # Engagement Quality Indicators
    engagement_reach = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Percentage of community reached through engagements",
    )

    repeat_participation_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Percentage of participants who attended multiple engagements",
    )

    diversity_index = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Diversity index of participants (0-1 scale)",
    )

    # Metadata
    calculated_by = models.ForeignKey(
        User, on_delete=models.PROTECT, help_text="User who calculated these metrics"
    )

    calculated_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-period_start"]
        unique_together = ["community", "period_type", "period_start"]

    def __str__(self):
        return f"{self.community.name} - {self.get_period_type_display()} ({self.period_start})"


class Organization(models.Model):
    """Model for managing stakeholder organizations (BMOAs, LGUs, NGAs, etc.)."""

    ORGANIZATION_TYPES = [
        ("bmoa", "BARMM Ministry/Agency/Office"),
        ("lgu", "Local Government Unit"),
        ("nga", "National Government Agency"),
        ("ingo", "International NGO"),
        ("ngo", "Non-Governmental Organization"),
        ("cso", "Civil Society Organization"),
        ("academic", "Academic Institution"),
        ("religious", "Religious Organization"),
        ("private", "Private Sector"),
        ("media", "Media Organization"),
        ("donor", "Donor Agency"),
        ("tribal", "Tribal/Indigenous Organization"),
        ("other", "Other"),
    ]

    PARTNERSHIP_LEVELS = [
        ("implementing", "Implementing Partner"),
        ("funding", "Funding Partner"),
        ("technical", "Technical Partner"),
        ("coordinating", "Coordinating Agency"),
        ("beneficiary", "Beneficiary Organization"),
        ("observer", "Observer"),
        ("other", "Other"),
    ]

    # Basic Information
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    name = models.CharField(max_length=255, help_text="Full name of the organization")

    acronym = models.CharField(
        max_length=20,
        blank=True,
        help_text="Organization acronym (e.g., MILF, ARMM, DOH)",
    )

    organization_type = models.CharField(
        max_length=15, choices=ORGANIZATION_TYPES, help_text="Type of organization"
    )

    description = models.TextField(
        blank=True, help_text="Description of the organization and its mandate"
    )

    # Mandate and Functions (particularly for government agencies)
    mandate = models.TextField(
        blank=True,
        help_text="Official mandate of the organization (particularly for government agencies)",
    )

    powers_and_functions = models.TextField(
        blank=True,
        help_text="Powers and functions of the organization (particularly for government agencies)",
    )

    # Contact Information
    address = models.TextField(
        blank=True, help_text="Physical address of the organization"
    )

    mailing_address = models.TextField(
        blank=True, help_text="Mailing address (if different from physical address)"
    )

    region = models.ForeignKey(
        Region,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="organizations",
        help_text="Region where the organization's primary office is located",
    )

    province = models.ForeignKey(
        Province,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="organizations",
        help_text="Province where the organization's primary office is located",
    )

    municipality = models.ForeignKey(
        Municipality,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="organizations",
        help_text="Municipality or city where the primary office is located",
    )

    barangay = models.ForeignKey(
        Barangay,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="organizations",
        help_text="Barangay where the primary office is located",
    )

    phone = models.CharField(
        max_length=50, blank=True, help_text="Primary phone number"
    )

    mobile = models.CharField(
        max_length=50, blank=True, help_text="Mobile phone number"
    )

    email = models.EmailField(blank=True, help_text="Primary email address")

    website = models.URLField(blank=True, help_text="Organization website")

    social_media = models.JSONField(
        null=True,
        blank=True,
        help_text="Social media accounts (Facebook, Twitter, etc.)",
    )

    # Key Personnel
    head_of_organization = models.CharField(
        max_length=255,
        blank=True,
        help_text="Name of the head of organization (e.g., Minister, Mayor, Director)",
    )

    head_position = models.CharField(
        max_length=100,
        blank=True,
        help_text="Position title of the head of organization",
    )

    focal_person = models.CharField(
        max_length=255,
        blank=True,
        help_text="Name of the designated focal person for OBC matters",
    )

    focal_person_position = models.CharField(
        max_length=100, blank=True, help_text="Position of the focal person"
    )

    focal_person_contact = models.CharField(
        max_length=100, blank=True, help_text="Contact information for the focal person"
    )

    focal_person_email = models.EmailField(
        blank=True, help_text="Email address of the focal person"
    )

    # Partnership Information
    partnership_level = models.CharField(
        max_length=15,
        choices=PARTNERSHIP_LEVELS,
        blank=True,
        help_text="Level of partnership with OOBC",
    )

    partnership_start_date = models.DateField(
        null=True, blank=True, help_text="Date when partnership was established"
    )

    partnership_status = models.CharField(
        max_length=20,
        choices=[
            ("active", "Active"),
            ("inactive", "Inactive"),
            ("suspended", "Suspended"),
            ("terminated", "Terminated"),
        ],
        default="active",
        help_text="Current partnership status",
    )

    # Operational Details
    areas_of_expertise = models.TextField(
        blank=True, help_text="Areas of expertise and services provided"
    )

    geographic_coverage = models.TextField(
        blank=True, help_text="Geographic areas of operation"
    )

    target_beneficiaries = models.TextField(
        blank=True, help_text="Target beneficiaries and communities served"
    )

    annual_budget = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Annual budget (in PHP)",
    )

    staff_count = models.PositiveIntegerField(
        null=True, blank=True, help_text="Number of staff members"
    )

    # Administrative Information
    registration_number = models.CharField(
        max_length=100,
        blank=True,
        help_text="Official registration number (SEC, DTI, etc.)",
    )

    tax_identification_number = models.CharField(
        max_length=50, blank=True, help_text="Tax Identification Number (TIN)"
    )

    accreditation_details = models.TextField(
        blank=True, help_text="Accreditation details and certifications"
    )

    # Engagement History
    last_engagement_date = models.DateField(
        null=True, blank=True, help_text="Date of last engagement or communication"
    )

    engagement_frequency = models.CharField(
        max_length=20,
        choices=[
            ("daily", "Daily"),
            ("weekly", "Weekly"),
            ("monthly", "Monthly"),
            ("quarterly", "Quarterly"),
            ("annually", "Annually"),
            ("as_needed", "As Needed"),
        ],
        default="as_needed",
        help_text="Frequency of engagement",
    )

    # Notes and Status
    notes = models.TextField(blank=True, help_text="Additional notes and observations")

    is_active = models.BooleanField(
        default=True, help_text="Whether this organization is currently active"
    )

    is_priority = models.BooleanField(
        default=False, help_text="Whether this is a priority partner organization"
    )

    # Metadata
    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="created_organizations",
        help_text="User who created this organization record",
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        indexes = [
            models.Index(fields=["organization_type", "partnership_status"]),
            models.Index(fields=["is_active", "is_priority"]),
            models.Index(fields=["partnership_level", "partnership_status"]),
            models.Index(fields=["region", "province", "municipality"]),
        ]

    def __str__(self):
        if self.acronym:
            return f"{self.name} ({self.acronym})"
        return self.name

    @property
    def display_name(self):
        """Return display name with acronym if available."""
        if self.acronym:
            return f"{self.acronym} - {self.name}"
        return self.name

    @property
    def location_display(self):
        """Return a formatted representation of the headquarters location."""
        location_parts = []
        if self.barangay:
            location_parts.append(self.barangay.name)
        if self.municipality:
            location_parts.append(self.municipality.name)
        if self.province:
            location_parts.append(self.province.name)
        if self.region:
            location_parts.append(self.region.name)
        if location_parts:
            return ", ".join(location_parts)
        return None

    def clean(self):
        """Ensure geographic hierarchy remains consistent."""
        super().clean()
        errors = {}

        if self.barangay:
            barangay_municipality = self.barangay.municipality
            if self.municipality and self.municipality != barangay_municipality:
                errors["barangay"] = (
                    "Selected barangay does not belong to the chosen municipality."
                )
            else:
                self.municipality = self.municipality or barangay_municipality

        if self.municipality:
            municipality_province = self.municipality.province
            if self.province and self.province != municipality_province:
                errors["municipality"] = (
                    "Selected municipality does not belong to the chosen province."
                )
            else:
                self.province = self.province or municipality_province

        if self.province:
            province_region = self.province.region
            if self.region and self.region != province_region:
                errors["province"] = (
                    "Selected province does not belong to the chosen region."
                )
            else:
                self.region = self.region or province_region

        if errors:
            raise ValidationError(errors)


class MAOFocalPerson(models.Model):
    """
    Model for tracking MAO (Ministry/Agency/Office) focal persons.

    Part of Phase 1 implementation for MAO coordination and quarterly
    meeting workflows. Replaces the simple text fields in Organization
    with a proper relational model supporting primary/alternate contacts.
    """

    ROLE_CHOICES = [
        ("primary", "Primary Focal Person"),
        ("alternate", "Alternate Focal Person"),
    ]

    # Basic Information
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    mao = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="focal_persons",
        limit_choices_to={"organization_type": "bmoa"},
        help_text="MAO that this focal person represents",
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="mao_focal_roles",
        help_text="User account for this focal person",
    )

    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default="primary",
        help_text="Role: primary or alternate focal person",
    )

    # Contact Information
    designation = models.CharField(
        max_length=255, help_text="Official title/position within the MAO"
    )

    contact_email = models.EmailField(help_text="Official email address")

    contact_phone = models.CharField(
        max_length=50, blank=True, help_text="Primary phone number"
    )

    contact_mobile = models.CharField(
        max_length=50, blank=True, help_text="Mobile phone number"
    )

    # Status
    is_active = models.BooleanField(
        default=True, help_text="Whether this focal person is currently active"
    )

    appointed_date = models.DateField(help_text="Date when appointed as focal person")

    end_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date when focal person role ended (if applicable)",
    )

    # Notes
    notes = models.TextField(
        blank=True, help_text="Additional notes about this focal person"
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["mao__name", "role", "-appointed_date"]
        verbose_name = "MAO Focal Person"
        verbose_name_plural = "MAO Focal Persons"
        unique_together = [["mao", "user", "role"]]
        indexes = [
            models.Index(fields=["mao", "is_active"]),
            models.Index(fields=["user", "is_active"]),
            models.Index(fields=["role", "is_active"]),
        ]

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} - {self.mao.name} ({self.get_role_display()})"


class OrganizationContact(models.Model):
    """Model for individual contacts within organizations."""

    CONTACT_TYPES = [
        ("primary", "Primary Contact"),
        ("secondary", "Secondary Contact"),
        ("technical", "Technical Contact"),
        ("administrative", "Administrative Contact"),
        ("executive", "Executive Contact"),
        ("field", "Field Contact"),
        ("emergency", "Emergency Contact"),
    ]

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="contacts",
        help_text="Organization this contact belongs to",
    )

    contact_type = models.CharField(
        max_length=15, choices=CONTACT_TYPES, help_text="Type of contact"
    )

    # Personal Information
    first_name = models.CharField(max_length=100, help_text="First name")

    last_name = models.CharField(max_length=100, help_text="Last name")

    middle_name = models.CharField(max_length=100, blank=True, help_text="Middle name")

    title = models.CharField(
        max_length=100,
        blank=True,
        help_text="Professional title (Mr., Ms., Dr., Eng., etc.)",
    )

    position = models.CharField(
        max_length=150, help_text="Position/designation in the organization"
    )

    department = models.CharField(
        max_length=150, blank=True, help_text="Department or unit"
    )

    # Contact Information
    email = models.EmailField(blank=True, help_text="Email address")

    phone = models.CharField(max_length=50, blank=True, help_text="Phone number")

    mobile = models.CharField(max_length=50, blank=True, help_text="Mobile number")

    alternative_email = models.EmailField(
        blank=True, help_text="Alternative email address"
    )

    # Professional Details
    areas_of_responsibility = models.TextField(
        blank=True, help_text="Areas of responsibility and expertise"
    )

    languages_spoken = models.CharField(
        max_length=200, blank=True, help_text="Languages spoken (comma-separated)"
    )

    # Preferences
    preferred_communication_method = models.CharField(
        max_length=20,
        choices=[
            ("email", "Email"),
            ("phone", "Phone"),
            ("mobile", "Mobile"),
            ("letter", "Official Letter"),
            ("meeting", "Face-to-face Meeting"),
        ],
        default="email",
        help_text="Preferred method of communication",
    )

    best_contact_time = models.CharField(
        max_length=100,
        blank=True,
        help_text="Best time to contact (e.g., 9AM-5PM weekdays)",
    )

    # Status
    is_active = models.BooleanField(
        default=True, help_text="Whether this contact is currently active"
    )

    is_primary = models.BooleanField(
        default=False,
        help_text="Whether this is the primary contact for the organization",
    )

    notes = models.TextField(
        blank=True, help_text="Additional notes about this contact"
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["last_name", "first_name"]
        indexes = [
            models.Index(fields=["organization", "contact_type"]),
            models.Index(fields=["is_active", "is_primary"]),
        ]

    def __str__(self):
        return f"{self.full_name} - {self.position} ({self.organization.name})"

    @property
    def full_name(self):
        """Return full name of the contact."""
        names = [self.first_name, self.middle_name, self.last_name]
        return " ".join([name for name in names if name])

    @property
    def display_name(self):
        """Return display name with title if available."""
        if self.title:
            return f"{self.title} {self.full_name}"
        return self.full_name


class Communication(models.Model):
    """Model for tracking communications with stakeholder organizations."""

    COMMUNICATION_TYPES = [
        ("email", "Email"),
        ("letter", "Official Letter"),
        ("meeting", "Meeting"),
        ("phone", "Phone Call"),
        ("video_call", "Video Conference"),
        ("site_visit", "Site Visit"),
        ("workshop", "Workshop/Training"),
        ("consultation", "Consultation"),
        ("memo", "Memorandum"),
        ("report", "Report Submission"),
        ("request", "Request/Application"),
        ("response", "Response/Reply"),
        ("announcement", "Announcement"),
        ("invitation", "Invitation"),
        ("other", "Other"),
    ]

    DIRECTION_CHOICES = [
        ("incoming", "Incoming"),
        ("outgoing", "Outgoing"),
        ("internal", "Internal"),
    ]

    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("sent", "Sent"),
        ("received", "Received"),
        ("acknowledged", "Acknowledged"),
        ("responded", "Responded"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]

    PRIORITY_LEVELS = [
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
        ("urgent", "Urgent"),
    ]

    # Basic Information
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="communications",
        help_text="Organization involved in this communication",
    )

    contact = models.ForeignKey(
        OrganizationContact,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="communications",
        help_text="Specific contact person (if applicable)",
    )

    related_engagement = models.ForeignKey(
        StakeholderEngagement,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="communications",
        help_text="Related stakeholder engagement (if applicable)",
    )

    # Communication Details
    communication_type = models.CharField(
        max_length=15, choices=COMMUNICATION_TYPES, help_text="Type of communication"
    )

    direction = models.CharField(
        max_length=10, choices=DIRECTION_CHOICES, help_text="Direction of communication"
    )

    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default="draft",
        help_text="Current status of the communication",
    )

    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_LEVELS,
        default="medium",
        help_text="Priority level of this communication",
    )

    # Content
    subject = models.CharField(
        max_length=255, help_text="Subject or title of the communication"
    )

    content = models.TextField(help_text="Content or description of the communication")

    reference_number = models.CharField(
        max_length=100,
        blank=True,
        help_text="Official reference number (for letters, memos, etc.)",
    )

    # Timeline
    communication_date = models.DateField(help_text="Date of the communication")

    communication_time = models.TimeField(
        null=True,
        blank=True,
        help_text="Time of the communication (for calls, meetings, etc.)",
    )

    due_date = models.DateField(
        null=True, blank=True, help_text="Due date for response or action"
    )

    # Participants
    sender = models.CharField(
        max_length=255, blank=True, help_text="Name of the sender"
    )

    sender_position = models.CharField(
        max_length=150, blank=True, help_text="Position of the sender"
    )

    recipient = models.CharField(
        max_length=255, blank=True, help_text="Name of the recipient"
    )

    recipient_position = models.CharField(
        max_length=150, blank=True, help_text="Position of the recipient"
    )

    cc_recipients = models.TextField(
        blank=True, help_text="CC recipients (one per line)"
    )

    # Follow-up
    requires_follow_up = models.BooleanField(
        default=False, help_text="Whether this communication requires follow-up"
    )

    follow_up_date = models.DateField(
        null=True, blank=True, help_text="Scheduled follow-up date"
    )

    follow_up_notes = models.TextField(
        blank=True, help_text="Follow-up notes and action items"
    )

    follow_up_completed = models.BooleanField(
        default=False, help_text="Whether follow-up has been completed"
    )

    # Response Details
    response_received = models.BooleanField(
        default=False, help_text="Whether a response has been received"
    )

    response_date = models.DateField(
        null=True, blank=True, help_text="Date response was received"
    )

    response_content = models.TextField(
        blank=True, help_text="Content of the response received"
    )

    # Documentation
    attachments = models.JSONField(
        null=True, blank=True, help_text="List of attached files (JSON format)"
    )

    meeting_minutes = models.TextField(
        blank=True, help_text="Meeting minutes (for meetings)"
    )

    outcomes = models.TextField(
        blank=True, help_text="Outcomes and decisions from the communication"
    )

    # Tags and Categories
    tags = models.CharField(
        max_length=500,
        blank=True,
        help_text="Tags for categorization (comma-separated)",
    )

    topic_areas = models.CharField(
        max_length=500, blank=True, help_text="Topic areas discussed (comma-separated)"
    )

    # Metadata
    recorded_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="recorded_communications",
        help_text="User who recorded this communication",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-communication_date", "-created_at"]
        indexes = [
            models.Index(fields=["organization", "communication_type"]),
            models.Index(fields=["direction", "status"]),
            models.Index(fields=["communication_date", "priority"]),
            models.Index(fields=["requires_follow_up", "follow_up_date"]),
        ]

    def __str__(self):
        return f"{self.subject} - {self.organization.name} ({self.communication_date})"

    @property
    def is_overdue(self):
        """Check if communication is overdue."""
        if self.due_date:
            return timezone.now().date() > self.due_date
        return False

    @property
    def follow_up_overdue(self):
        """Check if follow-up is overdue."""
        if (
            self.requires_follow_up
            and self.follow_up_date
            and not self.follow_up_completed
        ):
            return timezone.now().date() > self.follow_up_date
        return False


class CommunicationTemplate(models.Model):
    """Model for standardized communication templates."""

    TEMPLATE_TYPES = [
        ("email", "Email Template"),
        ("letter", "Letter Template"),
        ("memo", "Memorandum Template"),
        ("invitation", "Invitation Template"),
        ("announcement", "Announcement Template"),
        ("request", "Request Template"),
        ("response", "Response Template"),
        ("report", "Report Template"),
        ("other", "Other Template"),
    ]

    name = models.CharField(max_length=150, help_text="Name of the template")

    template_type = models.CharField(
        max_length=15, choices=TEMPLATE_TYPES, help_text="Type of template"
    )

    description = models.TextField(
        blank=True, help_text="Description of when to use this template"
    )

    subject_template = models.CharField(
        max_length=255,
        blank=True,
        help_text="Subject line template (with placeholders)",
    )

    content_template = models.TextField(
        help_text="Content template (with placeholders like {{organization_name}}, {{date}}, etc.)"
    )

    # Template Metadata
    language = models.CharField(
        max_length=15,
        default="en",
        choices=[
            ("en", "English"),
            ("fil", "Filipino"),
            ("ar", "Arabic"),
            ("maguindanaon", "Maguindanaon"),
            ("maranao", "Maranao"),
            ("tausug", "Tausug"),
        ],
        help_text="Language of the template",
    )

    formal_level = models.CharField(
        max_length=15,
        choices=[
            ("formal", "Formal"),
            ("semi_formal", "Semi-Formal"),
            ("informal", "Informal"),
        ],
        default="formal",
        help_text="Level of formality",
    )

    # Usage Instructions
    usage_instructions = models.TextField(
        blank=True, help_text="Instructions on how to use this template"
    )

    placeholders = models.JSONField(
        null=True,
        blank=True,
        help_text="List of available placeholders and their descriptions",
    )

    # Status
    is_active = models.BooleanField(
        default=True, help_text="Whether this template is currently active"
    )

    is_default = models.BooleanField(
        default=False, help_text="Whether this is the default template for this type"
    )

    # Approval Process
    requires_approval = models.BooleanField(
        default=False,
        help_text="Whether communications using this template require approval",
    )

    approver = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="template_approvals",
        help_text="User who can approve communications using this template",
    )

    # Metadata
    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="created_templates",
        help_text="User who created this template",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["template_type", "name"]
        unique_together = ["template_type", "is_default", "language"]

    def __str__(self):
        return f"{self.name} ({self.get_template_type_display()})"


class CommunicationSchedule(models.Model):
    """Model for scheduling and managing communication reminders."""

    SCHEDULE_TYPES = [
        ("one_time", "One-time"),
        ("recurring", "Recurring"),
        ("follow_up", "Follow-up Reminder"),
        ("deadline", "Deadline Reminder"),
    ]

    RECURRENCE_PATTERNS = [
        ("daily", "Daily"),
        ("weekly", "Weekly"),
        ("bi_weekly", "Bi-weekly"),
        ("monthly", "Monthly"),
        ("quarterly", "Quarterly"),
        ("semi_annual", "Semi-annual"),
        ("annual", "Annual"),
    ]

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="communication_schedules",
        help_text="Organization for this scheduled communication",
    )

    contact = models.ForeignKey(
        OrganizationContact,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="communication_schedules",
        help_text="Specific contact person (if applicable)",
    )

    template = models.ForeignKey(
        CommunicationTemplate,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Communication template to use",
    )

    # Scheduling Details
    schedule_type = models.CharField(
        max_length=15, choices=SCHEDULE_TYPES, help_text="Type of schedule"
    )

    title = models.CharField(
        max_length=200, help_text="Title or description of the scheduled communication"
    )

    scheduled_date = models.DateField(
        help_text="Date when communication should be sent/performed"
    )

    scheduled_time = models.TimeField(
        null=True,
        blank=True,
        help_text="Time when communication should be sent/performed",
    )

    # Recurrence Settings
    recurrence_pattern = models.CharField(
        max_length=15,
        choices=RECURRENCE_PATTERNS,
        blank=True,
        help_text="Recurrence pattern (for recurring schedules)",
    )

    recurrence_end_date = models.DateField(
        null=True, blank=True, help_text="End date for recurring schedule"
    )

    # Communication Content
    subject = models.CharField(
        max_length=255, help_text="Subject or title of the communication"
    )

    message_content = models.TextField(
        blank=True, help_text="Pre-written message content"
    )

    # Execution Status
    is_active = models.BooleanField(
        default=True, help_text="Whether this schedule is currently active"
    )

    last_executed = models.DateTimeField(
        null=True, blank=True, help_text="Date and time of last execution"
    )

    next_execution = models.DateTimeField(help_text="Date and time of next execution")

    execution_count = models.PositiveIntegerField(
        default=0, help_text="Number of times this schedule has been executed"
    )

    # Notification Settings
    send_reminder = models.BooleanField(
        default=True, help_text="Whether to send reminder notifications"
    )

    reminder_days_before = models.PositiveIntegerField(
        default=1, help_text="Days before scheduled date to send reminder"
    )

    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_communications",
        help_text="User assigned to handle this communication",
    )

    # Metadata
    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="created_schedules",
        help_text="User who created this schedule",
    )

    notes = models.TextField(blank=True, help_text="Additional notes and instructions")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["next_execution"]
        indexes = [
            models.Index(fields=["organization", "is_active"]),
            models.Index(fields=["next_execution", "is_active"]),
            models.Index(fields=["assigned_to", "is_active"]),
        ]

    def __str__(self):
        return f"{self.title} - {self.organization.name} ({self.scheduled_date})"

    def save(self, *args, **kwargs):
        if not self.next_execution:
            self.next_execution = timezone.make_aware(
                timezone.datetime.combine(
                    self.scheduled_date,
                    self.scheduled_time or timezone.datetime.min.time(),
                )
            )
        super().save(*args, **kwargs)


class Partnership(models.Model):
    """Model for managing MOAs, MOUs, and other formal partnerships."""

    PARTNERSHIP_TYPES = [
        ("moa", "Memorandum of Agreement"),
        ("mou", "Memorandum of Understanding"),
        ("contract", "Service Contract"),
        ("grant_agreement", "Grant Agreement"),
        ("cooperation_agreement", "Cooperation Agreement"),
        ("joint_venture", "Joint Venture"),
        ("consortium", "Consortium Agreement"),
        ("informal", "Informal Partnership"),
        ("other", "Other"),
    ]

    STATUS_CHOICES = [
        ("concept", "Concept/Planning"),
        ("draft", "Draft"),
        ("review", "Under Review"),
        ("negotiation", "Under Negotiation"),
        ("pending_approval", "Pending Approval"),
        ("pending_signature", "Pending Signature"),
        ("active", "Active"),
        ("completed", "Completed"),
        ("terminated", "Terminated"),
        ("expired", "Expired"),
        ("suspended", "Suspended"),
        ("cancelled", "Cancelled"),
    ]

    PRIORITY_LEVELS = [
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
        ("critical", "Critical"),
    ]

    # Basic Information
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    title = models.CharField(
        max_length=255, help_text="Title of the partnership/agreement"
    )

    partnership_type = models.CharField(
        max_length=25,
        choices=PARTNERSHIP_TYPES,
        help_text="Type of partnership or agreement",
    )

    description = models.TextField(help_text="Detailed description of the partnership")

    objectives = models.TextField(help_text="Objectives and goals of the partnership")

    scope = models.TextField(help_text="Scope of work and responsibilities")

    # Relationships
    organizations = models.ManyToManyField(
        Organization,
        related_name="partnerships",
        help_text="Organizations involved in this partnership",
    )

    communities = models.ManyToManyField(
        OBCCommunity,
        related_name="partnerships",
        blank=True,
        help_text="Communities involved or benefiting from this partnership",
    )

    lead_organization = models.ForeignKey(
        Organization,
        on_delete=models.PROTECT,
        related_name="led_partnerships",
        help_text="Lead organization for this partnership",
    )

    # Management
    focal_person = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="managed_partnerships",
        help_text="OOBC focal person managing this partnership",
    )

    backup_focal_person = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="backup_partnerships",
        help_text="Backup focal person",
    )

    # Timeline
    concept_date = models.DateField(
        null=True, blank=True, help_text="Date when partnership concept was developed"
    )

    negotiation_start_date = models.DateField(
        null=True, blank=True, help_text="Date when negotiations started"
    )

    signing_date = models.DateField(
        null=True, blank=True, help_text="Date when agreement was signed"
    )

    start_date = models.DateField(
        null=True, blank=True, help_text="Official start date of the partnership"
    )

    end_date = models.DateField(
        null=True, blank=True, help_text="End date of the partnership"
    )

    renewal_date = models.DateField(
        null=True, blank=True, help_text="Date for renewal consideration"
    )

    # Status and Progress
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="concept",
        help_text="Current status of the partnership",
    )

    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_LEVELS,
        default="medium",
        help_text="Priority level of this partnership",
    )

    progress_percentage = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Overall progress percentage (0-100)",
    )

    # Financial Information
    total_budget = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Total budget for the partnership (in PHP)",
    )

    oobc_contribution = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="OOBC financial contribution (in PHP)",
    )

    partner_contribution = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Partner financial contribution (in PHP)",
    )

    # Documentation
    document_number = models.CharField(
        max_length=100, blank=True, help_text="Official document/reference number"
    )

    legal_reference = models.CharField(
        max_length=200, blank=True, help_text="Legal or regulatory reference"
    )

    # Performance and Impact
    key_performance_indicators = models.TextField(
        blank=True, help_text="Key performance indicators and metrics"
    )

    expected_outcomes = models.TextField(
        blank=True, help_text="Expected outcomes and impact"
    )

    actual_outcomes = models.TextField(blank=True, help_text="Actual outcomes achieved")

    lessons_learned = models.TextField(
        blank=True, help_text="Lessons learned during implementation"
    )

    # Risk Management
    risks_identified = models.TextField(
        blank=True, help_text="Identified risks and challenges"
    )

    mitigation_strategies = models.TextField(
        blank=True, help_text="Risk mitigation strategies"
    )

    # Communication
    communication_plan = models.TextField(
        blank=True, help_text="Communication plan and protocols"
    )

    reporting_requirements = models.TextField(
        blank=True, help_text="Reporting requirements and schedule"
    )

    # Renewal and Termination
    is_renewable = models.BooleanField(
        default=False, help_text="Whether this partnership can be renewed"
    )

    renewal_criteria = models.TextField(blank=True, help_text="Criteria for renewal")

    termination_clause = models.TextField(
        blank=True, help_text="Termination conditions and procedures"
    )

    # Metadata
    notes = models.TextField(blank=True, help_text="Additional notes and observations")

    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="created_partnerships",
        help_text="User who created this partnership record",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["partnership_type", "status"]),
            models.Index(fields=["status", "priority"]),
            models.Index(fields=["focal_person", "status"]),
            models.Index(fields=["start_date", "end_date"]),
        ]

    def __str__(self):
        return f"{self.title} ({self.get_partnership_type_display()})"

    @property
    def is_active(self):
        """Check if partnership is currently active."""
        return self.status == "active"

    @property
    def is_expired(self):
        """Check if partnership has expired."""
        if self.end_date:
            return timezone.now().date() > self.end_date
        return False

    @property
    def days_until_expiry(self):
        """Calculate days until expiry."""
        if self.end_date:
            delta = self.end_date - timezone.now().date()
            return delta.days
        return None

    @property
    def duration_days(self):
        """Calculate total duration in days."""
        if self.start_date and self.end_date:
            return (self.end_date - self.start_date).days
        return None


class PartnershipSignatory(models.Model):
    """Model for tracking partnership signatories."""

    SIGNATORY_ROLES = [
        ("primary", "Primary Signatory"),
        ("witness", "Witness"),
        ("approver", "Approver"),
        ("notary", "Notary"),
        ("legal_counsel", "Legal Counsel"),
    ]

    partnership = models.ForeignKey(
        Partnership,
        on_delete=models.CASCADE,
        related_name="signatories",
        help_text="Partnership this signatory belongs to",
    )

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        help_text="Organization the signatory represents",
    )

    contact = models.ForeignKey(
        OrganizationContact,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Specific contact if available in system",
    )

    # Signatory Details
    name = models.CharField(max_length=255, help_text="Full name of the signatory")

    position = models.CharField(
        max_length=150, help_text="Position/title of the signatory"
    )

    role = models.CharField(
        max_length=15,
        choices=SIGNATORY_ROLES,
        default="primary",
        help_text="Role of this signatory",
    )

    # Contact Information
    email = models.EmailField(blank=True, help_text="Email address")

    phone = models.CharField(max_length=50, blank=True, help_text="Phone number")

    # Signing Details
    is_required = models.BooleanField(
        default=True, help_text="Whether this signatory's signature is required"
    )

    signed = models.BooleanField(
        default=False, help_text="Whether this signatory has signed"
    )

    signature_date = models.DateField(
        null=True, blank=True, help_text="Date when signature was provided"
    )

    signature_location = models.CharField(
        max_length=255, blank=True, help_text="Location where signature was provided"
    )

    # Authorization
    has_authority = models.BooleanField(
        default=True, help_text="Whether signatory has authority to sign"
    )

    authorization_document = models.CharField(
        max_length=255, blank=True, help_text="Reference to authorization document"
    )

    # Metadata
    notes = models.TextField(
        blank=True, help_text="Additional notes about this signatory"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["organization__name", "name"]
        unique_together = ["partnership", "organization", "name"]
        indexes = [
            models.Index(fields=["partnership", "signed"]),
            models.Index(fields=["organization", "signed"]),
        ]

    def __str__(self):
        return f"{self.name} - {self.organization.name}"


class PartnershipMilestone(models.Model):
    """Model for tracking partnership milestones and deliverables."""

    STATUS_CHOICES = [
        ("planned", "Planned"),
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
        ("delayed", "Delayed"),
        ("on_hold", "On Hold"),
        ("cancelled", "Cancelled"),
        ("overdue", "Overdue"),
    ]

    MILESTONE_TYPES = [
        ("deliverable", "Deliverable"),
        ("payment", "Payment"),
        ("review", "Review/Evaluation"),
        ("approval", "Approval"),
        ("event", "Event/Activity"),
        ("report", "Report Submission"),
        ("other", "Other"),
    ]

    partnership = models.ForeignKey(
        Partnership,
        on_delete=models.CASCADE,
        related_name="milestones",
        help_text="Partnership this milestone belongs to",
    )

    # Milestone Details
    title = models.CharField(max_length=255, help_text="Title of the milestone")

    description = models.TextField(help_text="Detailed description of the milestone")

    milestone_type = models.CharField(
        max_length=15,
        choices=MILESTONE_TYPES,
        default="deliverable",
        help_text="Type of milestone",
    )

    # Timeline
    planned_start_date = models.DateField(
        null=True, blank=True, help_text="Planned start date"
    )

    due_date = models.DateField(help_text="Due date for this milestone")

    actual_completion_date = models.DateField(
        null=True, blank=True, help_text="Actual completion date"
    )

    # Status and Progress
    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default="planned",
        help_text="Current status",
    )

    progress_percentage = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Progress percentage (0-100)",
    )

    # Responsibility
    responsible_organization = models.ForeignKey(
        Organization,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="responsible_milestones",
        help_text="Organization responsible for this milestone",
    )

    responsible_person = models.CharField(
        max_length=255, blank=True, help_text="Person responsible for this milestone"
    )

    oobc_focal_person = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="monitored_milestones",
        help_text="OOBC person monitoring this milestone",
    )

    # Dependencies
    depends_on = models.ManyToManyField(
        "self",
        symmetrical=False,
        blank=True,
        related_name="dependent_milestones",
        help_text="Milestones this depends on",
    )

    # Deliverables and Evidence
    deliverable_description = models.TextField(
        blank=True, help_text="Description of expected deliverable"
    )

    acceptance_criteria = models.TextField(
        blank=True, help_text="Criteria for accepting this milestone"
    )

    evidence_provided = models.TextField(
        blank=True, help_text="Evidence of completion provided"
    )

    verification_notes = models.TextField(
        blank=True, help_text="Notes from verification process"
    )

    verified_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="verified_milestones",
        help_text="User who verified completion",
    )

    verification_date = models.DateField(
        null=True, blank=True, help_text="Date of verification"
    )

    # Budget and Resources
    budget_allocated = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Budget allocated for this milestone",
    )

    actual_cost = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Actual cost incurred",
    )

    # Issues and Risks
    issues_encountered = models.TextField(
        blank=True, help_text="Issues encountered during implementation"
    )

    resolution_actions = models.TextField(
        blank=True, help_text="Actions taken to resolve issues"
    )

    # Metadata
    notes = models.TextField(blank=True, help_text="Additional notes")

    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="created_milestones",
        help_text="User who created this milestone",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["due_date", "created_at"]
        indexes = [
            models.Index(fields=["partnership", "status"]),
            models.Index(fields=["due_date", "status"]),
            models.Index(fields=["responsible_organization", "status"]),
        ]

    def __str__(self):
        return f"{self.title} - {self.partnership.title}"

    @property
    def is_overdue(self):
        """Check if milestone is overdue."""
        if self.status not in ["completed", "cancelled"]:
            return timezone.now().date() > self.due_date
        return False

    @property
    def days_until_due(self):
        """Calculate days until due date."""
        delta = self.due_date - timezone.now().date()
        return delta.days


class PartnershipDocument(models.Model):
    """Model for managing partnership-related documents."""

    DOCUMENT_TYPES = [
        ("agreement", "Main Agreement"),
        ("amendment", "Amendment"),
        ("appendix", "Appendix"),
        ("addendum", "Addendum"),
        ("proposal", "Proposal"),
        ("presentation", "Presentation"),
        ("report", "Report"),
        ("correspondence", "Correspondence"),
        ("legal_opinion", "Legal Opinion"),
        ("authorization", "Authorization"),
        ("certificate", "Certificate"),
        ("other", "Other"),
    ]

    partnership = models.ForeignKey(
        Partnership,
        on_delete=models.CASCADE,
        related_name="documents",
        help_text="Partnership this document belongs to",
    )

    document_type = models.CharField(
        max_length=15, choices=DOCUMENT_TYPES, help_text="Type of document"
    )

    title = models.CharField(max_length=255, help_text="Title of the document")

    description = models.TextField(blank=True, help_text="Description of the document")

    version = models.CharField(
        max_length=10, default="1.0", help_text="Document version"
    )

    file = models.FileField(upload_to="partnerships/%Y/%m/", help_text="Document file")

    file_size = models.PositiveIntegerField(
        null=True, blank=True, help_text="File size in bytes"
    )

    # Access Control
    is_confidential = models.BooleanField(
        default=False, help_text="Whether this document is confidential"
    )

    is_public = models.BooleanField(
        default=False, help_text="Whether this document can be shared publicly"
    )

    access_restrictions = models.TextField(
        blank=True, help_text="Access restrictions and guidelines"
    )

    # Document Metadata
    document_date = models.DateField(
        null=True, blank=True, help_text="Date of the document"
    )

    effective_date = models.DateField(
        null=True, blank=True, help_text="Date when document becomes effective"
    )

    expiry_date = models.DateField(
        null=True, blank=True, help_text="Date when document expires"
    )

    # Workflow
    requires_approval = models.BooleanField(
        default=False, help_text="Whether this document requires approval"
    )

    approved = models.BooleanField(
        default=False, help_text="Whether this document has been approved"
    )

    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_partnership_documents",
        help_text="User who approved this document",
    )

    approval_date = models.DateField(
        null=True, blank=True, help_text="Date of approval"
    )

    # Upload Details
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="uploaded_partnership_documents",
        help_text="User who uploaded this document",
    )

    upload_date = models.DateTimeField(auto_now_add=True)

    notes = models.TextField(
        blank=True, help_text="Additional notes about this document"
    )

    class Meta:
        ordering = ["-upload_date"]
        indexes = [
            models.Index(fields=["partnership", "document_type"]),
            models.Index(fields=["is_confidential", "is_public"]),
        ]

    def __str__(self):
        return f"{self.title} v{self.version} - {self.partnership.title}"

    def save(self, *args, **kwargs):
        if self.file:
            self.file_size = self.file.size
        super().save(*args, **kwargs)


class InterMOAPartnership(models.Model):
    """Inter-ministry partnership enabling collaboration between BARMM MOAs."""

    PARTNERSHIP_TYPES = [
        ("bilateral", "Bilateral Partnership (2 MOAs)"),
        ("multilateral", "Multilateral Partnership (3+ MOAs)"),
        ("joint_program", "Joint Program Implementation"),
        ("resource_sharing", "Resource Sharing Agreement"),
        ("capacity_building", "Capacity Building Initiative"),
        ("policy_coordination", "Policy Coordination"),
        ("service_delivery", "Joint Service Delivery"),
        ("other", "Other"),
    ]

    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("pending_approval", "Pending Approval"),
        ("active", "Active"),
        ("on_hold", "On Hold"),
        ("completed", "Completed"),
        ("terminated", "Terminated"),
    ]

    PRIORITY_LEVELS = [
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
        ("critical", "Critical"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    title = models.CharField(
        max_length=255,
        help_text="Title of the inter-MOA partnership",
    )

    partnership_type = models.CharField(
        max_length=30,
        choices=PARTNERSHIP_TYPES,
        help_text="Type of partnership between MOAs",
    )

    description = models.TextField(
        help_text="Detailed description of the partnership objectives and scope",
    )

    objectives = models.TextField(
        help_text="Specific objectives and goals of this partnership",
    )

    lead_moa_code = models.CharField(
        max_length=20,
        help_text="Code of the lead MOA (e.g., 'OOBC', 'MOH', 'MAFAR')",
    )

    participating_moa_codes = models.JSONField(
        default=list,
        help_text="List of participating MOA codes (e.g., ['MOH', 'MOLE'])",
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="draft",
        help_text="Current status of the partnership",
    )

    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_LEVELS,
        default="medium",
        help_text="Priority level of this partnership",
    )

    progress_percentage = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Overall progress (0-100%)",
    )

    start_date = models.DateField(
        null=True,
        blank=True,
        help_text="Partnership start date",
    )

    end_date = models.DateField(
        null=True,
        blank=True,
        help_text="Partnership end date (if applicable)",
    )

    focal_person_name = models.CharField(
        max_length=255,
        blank=True,
        help_text="Name of the focal person managing this partnership",
    )

    focal_person_email = models.EmailField(
        blank=True,
        help_text="Email of the focal person",
    )

    focal_person_phone = models.CharField(
        max_length=50,
        blank=True,
        help_text="Phone number of the focal person",
    )

    expected_outcomes = models.TextField(
        blank=True,
        help_text="Expected outcomes and impact of the partnership",
    )

    deliverables = models.TextField(
        blank=True,
        help_text="Key deliverables and milestones",
    )

    total_budget = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Total budget for the partnership (in PHP)",
    )

    resource_commitments = models.JSONField(
        default=dict,
        blank=True,
        help_text="Resource commitments by each MOA (JSON: {moa_code: resources})",
    )

    is_public = models.BooleanField(
        default=False,
        help_text="Whether this partnership is publicly visible (for OCM oversight)",
    )

    requires_ocm_approval = models.BooleanField(
        default=False,
        help_text="Whether this partnership requires OCM (Office of the Chief Minister) approval",
    )

    notes = models.TextField(
        blank=True,
        help_text="Additional notes and observations",
    )

    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="created_inter_moa_partnerships",
        help_text="User who created this partnership",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Inter-MOA Partnership"
        verbose_name_plural = "Inter-MOA Partnerships"
        indexes = [
            models.Index(fields=["lead_moa_code", "status"]),
            models.Index(fields=["status", "priority"]),
            models.Index(fields=["start_date", "end_date"]),
        ]

    def __str__(self):
        return f"{self.title} (Lead: {self.lead_moa_code})"

    @property
    def lead_organization(self):
        """Return the lead Organization object when available."""
        try:
            from organizations.models import Organization as MOAOrganization

            return MOAOrganization.objects.get(code=self.lead_moa_code)
        except Exception:
            return None

    @property
    def participating_organizations(self):
        """Return queryset of participating organizations."""
        try:
            from organizations.models import Organization as MOAOrganization
        except Exception:
            return []

        if not self.participating_moa_codes:
            return MOAOrganization.objects.none()

        return MOAOrganization.objects.filter(code__in=self.participating_moa_codes)

    @property
    def all_participating_moas(self):
        """Return unique list of participating MOA codes including the lead."""
        codes = [self.lead_moa_code]
        if self.participating_moa_codes:
            codes.extend(self.participating_moa_codes)
        return list({code for code in codes if code})

    @property
    def is_active(self):
        """Return True when partnership status is active."""
        return self.status == "active"

    @property
    def is_expired(self):
        """Return True if the partnership has passed its end date."""
        if self.end_date:
            return timezone.now().date() > self.end_date
        return False

    def can_view(self, user):
        """Determine if the given user can view this partnership."""
        if user.is_superuser:
            return True

        user_moa_codes = []
        if hasattr(user, "organization_memberships"):
            user_moa_codes = [
                membership.organization.code
                for membership in user.organization_memberships.all()
                if membership.organization
            ]

        if self.lead_moa_code in user_moa_codes:
            return True

        if self.participating_moa_codes:
            for code in self.participating_moa_codes:
                if code in user_moa_codes:
                    return True

        if self.is_public and getattr(user, "is_ocm_staff", False):
            return True

        return False

    def can_edit(self, user):
        """Determine if the given user can edit this partnership."""
        if user.is_superuser:
            return True

        if hasattr(user, "organization_memberships"):
            user_moa_codes = [
                membership.organization.code
                for membership in user.organization_memberships.all()
                if membership.organization
            ]
            if self.lead_moa_code in user_moa_codes:
                return True

        return False

    def clean(self):
        """Validate model fields before saving."""
        errors = {}

        if self.start_date and self.end_date and self.end_date <= self.start_date:
            errors["end_date"] = "End date must be after start date"

        if not 0 <= self.progress_percentage <= 100:
            errors["progress_percentage"] = "Progress must be between 0 and 100"

        if self.participating_moa_codes and self.lead_moa_code in self.participating_moa_codes:
            errors["participating_moa_codes"] = "Lead MOA cannot also be a participant MOA"

        if errors:
            raise ValidationError(errors)


# ========== BACKWARD COMPATIBILITY PROXIES ==========
# Import Event proxy to access legacy database table.
# See: docs/refactor/WORKITEM_MIGRATION_COMPLETE.md
from common.proxies import EventProxy as Event

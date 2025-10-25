import uuid

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone

from communities.models import OBCCommunity, ProvinceCoverage
from common.models import Barangay, Municipality, Province, Region

User = get_user_model()


class AssessmentCategory(models.Model):
    """Categories for different types of assessments."""

    CATEGORY_TYPES = [
        ("needs_assessment", "Needs Assessment"),
        ("baseline_study", "Baseline Study"),
        ("impact_assessment", "Impact Assessment"),
        ("situational_analysis", "Situational Analysis"),
        ("community_mapping", "Community Mapping"),
    ]

    name = models.CharField(
        max_length=100, unique=True, help_text="Name of the assessment category"
    )

    category_type = models.CharField(
        max_length=50, choices=CATEGORY_TYPES, help_text="Type of assessment category"
    )

    description = models.TextField(
        blank=True, help_text="Description of the assessment category"
    )

    icon = models.CharField(
        max_length=50, blank=True, help_text="CSS icon class for this category"
    )

    color = models.CharField(
        max_length=7,
        default="#007bff",
        help_text="Color code for this category (hex format)",
    )

    is_active = models.BooleanField(
        default=True, help_text="Whether this category is currently active"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Assessment Categories"

    def __str__(self):
        return self.name


class Assessment(models.Model):
    """Core model for managing mapping and needs assessments."""

    STATUS_CHOICES = [
        ("planning", "Planning"),
        ("preparation", "Preparation"),
        ("data_collection", "Data Collection"),
        ("analysis", "Analysis"),
        ("reporting", "Reporting"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]

    PRIORITY_CHOICES = [
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
        ("critical", "Critical"),
    ]

    ASSESSMENT_LEVELS = [
        ("regional", "Regional Level"),
        ("provincial", "Provincial Level"),
        ("city_municipal", "City/Municipal Level"),
        ("barangay", "Barangay Level"),
        ("community", "Community Level"),
    ]

    ASSESSMENT_METHODOLOGIES = [
        ("desk_review", "Desk Review/Research"),
        ("survey", "Survey"),
        ("kii", "Key Informant Interview (KII)"),
        ("workshop", "FGD/Workshops"),
        ("participatory", "Participatory Assessment"),
        ("observation", "Direct Observation"),
        ("mixed", "Mixed Methods"),
        ("other", "Other Methodologies"),
    ]

    # Basic Information
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    title = models.CharField(max_length=200, help_text="Title of the assessment")

    category = models.ForeignKey(
        AssessmentCategory, on_delete=models.PROTECT, help_text="Category of assessment"
    )

    description = models.TextField(help_text="Detailed description of the assessment")

    objectives = models.TextField(help_text="Objectives and goals of the assessment")

    # Assessment level and methodology
    assessment_level = models.CharField(
        max_length=20,
        choices=ASSESSMENT_LEVELS,
        default="community",
        help_text="Level at which the assessment is conducted",
    )

    primary_methodology = models.CharField(
        max_length=20,
        choices=ASSESSMENT_METHODOLOGIES,
        default="survey",
        help_text="Primary methodology used in the assessment",
    )

    secondary_methodologies = models.JSONField(
        null=True, blank=True, help_text="List of secondary methodologies used"
    )

    # Community and Location (flexible for different assessment levels)
    region = models.ForeignKey(
        Region,
        on_delete=models.SET_NULL,
        related_name="assessments",
        null=True,
        blank=True,
        help_text="Region covered by the assessment",
    )

    province = models.ForeignKey(
        Province,
        on_delete=models.SET_NULL,
        related_name="assessments",
        null=True,
        blank=True,
        help_text="Province being assessed (for regional/provincial assessments)",
    )

    municipality = models.ForeignKey(
        Municipality,
        on_delete=models.SET_NULL,
        related_name="assessments",
        null=True,
        blank=True,
        help_text="Municipality or city covered by the assessment",
    )

    barangay = models.ForeignKey(
        Barangay,
        on_delete=models.SET_NULL,
        related_name="assessments",
        null=True,
        blank=True,
        help_text="Barangay covered by the assessment",
    )

    community = models.ForeignKey(
        OBCCommunity,
        on_delete=models.CASCADE,
        related_name="assessments",
        null=True,
        blank=True,
        help_text="Community being assessed (for community-level assessments)",
    )

    location_details = models.TextField(
        blank=True, help_text="Additional location details and coverage area"
    )

    # Assessment Management
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="planning",
        help_text="Current status of the assessment",
    )

    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default="medium",
        help_text="Priority level of the assessment",
    )

    # Timeline
    planned_start_date = models.DateField(
        help_text="Planned start date for the assessment"
    )

    planned_end_date = models.DateField(
        help_text="Planned completion date for the assessment"
    )

    actual_start_date = models.DateField(
        null=True, blank=True, help_text="Actual start date of the assessment"
    )

    actual_end_date = models.DateField(
        null=True, blank=True, help_text="Actual completion date of the assessment"
    )

    # Team and Stakeholders
    lead_assessor = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="led_assessments",
        help_text="Lead person responsible for the assessment",
    )

    team_members = models.ManyToManyField(
        User,
        through="AssessmentTeamMember",
        related_name="assessment_teams",
        blank=True,
        help_text="Team members involved in the assessment",
    )

    # Budget and Resources
    estimated_budget = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Estimated budget for the assessment",
    )

    actual_budget = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Actual budget spent on the assessment",
    )

    # Results and Impact
    key_findings = models.TextField(
        blank=True, help_text="Key findings from the assessment"
    )

    recommendations = models.TextField(
        blank=True, help_text="Recommendations based on assessment results"
    )

    impact_level = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        null=True,
        blank=True,
        help_text="Level of impact identified",
    )

    # Metadata
    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="created_assessments",
        help_text="User who created this assessment",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Completion tracking
    progress_percentage = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Completion percentage (0-100)",
    )

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["community", "status"]),
            models.Index(fields=["province", "status"]),
            models.Index(fields=["municipality", "status"]),
            models.Index(fields=["barangay", "status"]),
            models.Index(fields=["region", "status"]),
            models.Index(fields=["category", "priority"]),
            models.Index(fields=["planned_start_date", "planned_end_date"]),
        ]

    def __str__(self):
        if self.community:
            display = self.community.display_name or self.community.barangay.name
            return f"{self.title} - {display}"
        if self.barangay:
            return f"{self.title} - {self.barangay.name}"
        if self.municipality:
            return f"{self.title} - {self.municipality.name}"
        if self.province:
            return f"{self.title} - {self.province.name}"
        if self.region:
            return f"{self.title} - {self.region.name}"
        return self.title

    @property
    def duration_days(self):
        """Calculate planned duration in days."""
        if self.planned_start_date and self.planned_end_date:
            return (self.planned_end_date - self.planned_start_date).days
        return None

    @property
    def is_overdue(self):
        """Check if assessment is overdue."""
        if self.status not in ["completed", "cancelled"] and self.planned_end_date:
            return timezone.now().date() > self.planned_end_date
        return False

    def clean(self):
        super().clean()

        errors = {}

        # Validate planned/actual timelines
        if self.planned_end_date and self.planned_start_date:
            if self.planned_end_date < self.planned_start_date:
                errors["planned_end_date"] = ValidationError(
                    "Planned end date cannot be earlier than start date."
                )
        if self.actual_end_date and self.actual_start_date:
            if self.actual_end_date < self.actual_start_date:
                errors["actual_end_date"] = ValidationError(
                    "Actual end date cannot be earlier than start date."
                )

        # Auto-align hierarchical relationships
        if self.community:
            community_barangay = self.community.barangay
            if community_barangay:
                self.barangay = community_barangay
                self.municipality = community_barangay.municipality
                if self.municipality:
                    self.province = self.municipality.province
                    if self.province:
                        self.region = self.province.region

        if self.barangay and not self.municipality:
            self.municipality = self.barangay.municipality
        if self.municipality and not self.province:
            self.province = self.municipality.province
        if self.province and not self.region:
            self.region = self.province.region

        # Validate hierarchical coherence when explicit selections are provided
        if (
            self.barangay
            and self.municipality
            and self.barangay.municipality_id != self.municipality_id
        ):
            errors["barangay"] = ValidationError(
                "Selected barangay must belong to the chosen municipality."
            )
        if (
            self.municipality
            and self.province
            and self.municipality.province_id != self.province_id
        ):
            errors["municipality"] = ValidationError(
                "Selected municipality must belong to the chosen province."
            )
        if self.province and self.region and self.province.region_id != self.region_id:
            errors["province"] = ValidationError(
                "Selected province must belong to the chosen region."
            )

        level = self.assessment_level or "community"

        if level == "regional":
            if not self.region:
                errors["region"] = ValidationError(
                    "Regional assessments must specify a region."
                )
            self.province = None
            self.municipality = None
            self.barangay = None
            self.community = None
        elif level == "provincial":
            if not self.region:
                errors["region"] = ValidationError(
                    "Provincial assessments must specify a region."
                )
            if not self.province:
                errors["province"] = ValidationError(
                    "Provincial assessments must specify a province."
                )
            self.municipality = None
            self.barangay = None
            self.community = None
        elif level == "city_municipal":
            if not self.region:
                errors["region"] = ValidationError(
                    "City/Municipal assessments must specify a region."
                )
            if not self.province:
                errors["province"] = ValidationError(
                    "City/Municipal assessments must specify a province."
                )
            if not self.municipality:
                errors["municipality"] = ValidationError(
                    "City/Municipal assessments must specify a municipality."
                )
            self.barangay = None
            self.community = None
        elif level == "barangay":
            if not self.region:
                errors["region"] = ValidationError(
                    "Barangay assessments must specify a region."
                )
            if not self.province:
                errors["province"] = ValidationError(
                    "Barangay assessments must specify a province."
                )
            if not self.municipality:
                errors["municipality"] = ValidationError(
                    "Barangay assessments must specify a municipality."
                )
            if not self.barangay:
                errors["barangay"] = ValidationError(
                    "Barangay assessments must specify a barangay."
                )
            self.community = None
        else:  # Community level and other granular configurations
            if not self.community:
                errors["community"] = ValidationError(
                    "Community assessments must be linked to a community."
                )
            # Hierarchy already enforced through auto-alignment above.

        if not self.region:
            errors.setdefault(
                "region",
                ValidationError(
                    "An assessment must be associated with at least one region."
                ),
            )

        if errors:
            raise ValidationError(errors)


class AssessmentTeamMember(models.Model):
    """Through model for assessment team members with roles."""

    ROLE_CHOICES = [
        ("team_leader", "Team Leader/Executive Director"),
        ("deputy_leader", "Deputy Team Leader/DMO IV"),
        ("facilitator", "Facilitator (DMO/CDO)"),
        ("documenter", "Documenter"),
        ("info_analyst", "Information System Analyst"),
        ("secretariat", "Secretariat/Admin Support"),
        ("data_collector", "Data Collector"),
        ("technical_expert", "Technical Expert"),
        ("observer", "Observer"),
    ]

    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        help_text="Role of the team member in this assessment",
    )

    assigned_date = models.DateField(
        default=timezone.now, help_text="Date when assigned to the assessment"
    )

    is_active = models.BooleanField(
        default=True, help_text="Whether this team member is currently active"
    )

    notes = models.TextField(
        blank=True, help_text="Additional notes about this team member's involvement"
    )

    class Meta:
        unique_together = ["assessment", "user", "role"]

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.get_role_display()} ({self.assessment.title})"


class Survey(models.Model):
    """Model for managing surveys within assessments."""

    SURVEY_TYPES = [
        ("household", "Household Survey"),
        ("community_leader", "Community Leader Interview"),
        ("focus_group", "Focus Group Discussion"),
        ("key_informant", "Key Informant Interview"),
        ("observation", "Direct Observation"),
        ("document_review", "Document Review"),
    ]

    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("active", "Active"),
        ("paused", "Paused"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]

    assessment = models.ForeignKey(
        Assessment,
        on_delete=models.CASCADE,
        related_name="surveys",
        help_text="Assessment this survey belongs to",
    )

    title = models.CharField(max_length=150, help_text="Title of the survey")

    survey_type = models.CharField(
        max_length=20, choices=SURVEY_TYPES, help_text="Type of survey"
    )

    description = models.TextField(help_text="Description of the survey")

    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default="draft",
        help_text="Current status of the survey",
    )

    target_respondents = models.IntegerField(help_text="Target number of respondents")

    actual_respondents = models.IntegerField(
        default=0, help_text="Actual number of respondents"
    )

    # Timeline
    start_date = models.DateField(help_text="Survey start date")

    end_date = models.DateField(help_text="Survey end date")

    # Survey Configuration
    questions_count = models.IntegerField(
        default=0, help_text="Number of questions in the survey"
    )

    estimated_duration_minutes = models.IntegerField(
        help_text="Estimated duration to complete survey (in minutes)"
    )

    # Metadata
    created_by = models.ForeignKey(
        User, on_delete=models.PROTECT, help_text="User who created this survey"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["assessment", "title"]

    def __str__(self):
        return f"{self.title} ({self.assessment.title})"

    @property
    def completion_rate(self):
        """Calculate completion rate as percentage."""
        if self.target_respondents > 0:
            return (self.actual_respondents / self.target_respondents) * 100
        return 0

    @property
    def is_complete(self):
        """Check if survey has reached target respondents."""
        return self.actual_respondents >= self.target_respondents


class SurveyQuestion(models.Model):
    """Model for survey questions."""

    QUESTION_TYPES = [
        ("text", "Text Response"),
        ("number", "Numeric Response"),
        ("single_choice", "Single Choice"),
        ("multiple_choice", "Multiple Choice"),
        ("scale", "Rating Scale"),
        ("yes_no", "Yes/No"),
        ("date", "Date"),
        ("location", "Geographic Location"),
    ]

    survey = models.ForeignKey(
        Survey,
        on_delete=models.CASCADE,
        related_name="questions",
        help_text="Survey this question belongs to",
    )

    question_text = models.TextField(help_text="The question text")

    question_type = models.CharField(
        max_length=20, choices=QUESTION_TYPES, help_text="Type of question"
    )

    order = models.IntegerField(help_text="Order of the question in the survey")

    is_required = models.BooleanField(
        default=False, help_text="Whether this question is required"
    )

    choices = models.JSONField(
        null=True,
        blank=True,
        help_text="Choices for single/multiple choice questions (JSON format)",
    )

    scale_min = models.IntegerField(
        null=True, blank=True, help_text="Minimum value for scale questions"
    )

    scale_max = models.IntegerField(
        null=True, blank=True, help_text="Maximum value for scale questions"
    )

    help_text = models.TextField(
        blank=True, help_text="Additional help text for respondents"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["survey", "order"]
        unique_together = ["survey", "order"]

    def __str__(self):
        return f"Q{self.order}: {self.question_text[:50]}..."


class SurveyResponse(models.Model):
    """Model for survey responses."""

    survey = models.ForeignKey(
        Survey,
        on_delete=models.CASCADE,
        related_name="responses",
        help_text="Survey this response belongs to",
    )

    respondent_name = models.CharField(
        max_length=100, blank=True, help_text="Name of the respondent (optional)"
    )

    respondent_contact = models.CharField(
        max_length=50,
        blank=True,
        help_text="Contact information of respondent (optional)",
    )

    demographic_info = models.JSONField(
        null=True, blank=True, help_text="Demographic information (JSON format)"
    )

    responses = models.JSONField(help_text="Survey responses (JSON format)")

    # Collection metadata
    collected_by = models.ForeignKey(
        User, on_delete=models.PROTECT, help_text="User who collected this response"
    )

    collection_date = models.DateTimeField(
        default=timezone.now, help_text="Date and time when response was collected"
    )

    collection_location = models.CharField(
        max_length=200, blank=True, help_text="Location where response was collected"
    )

    # Quality control
    is_validated = models.BooleanField(
        default=False, help_text="Whether this response has been validated"
    )

    validation_notes = models.TextField(
        blank=True, help_text="Notes from validation process"
    )

    validated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="validated_responses",
        help_text="User who validated this response",
    )

    validation_date = models.DateTimeField(
        null=True, blank=True, help_text="Date when response was validated"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-collection_date"]

    def __str__(self):
        return f"Response to {self.survey.title} - {self.collection_date.strftime('%Y-%m-%d')}"


class MappingActivity(models.Model):
    """Model for community mapping activities."""

    MAPPING_TYPES = [
        ("resource_mapping", "Resource Mapping"),
        ("infrastructure_mapping", "Infrastructure Mapping"),
        ("hazard_mapping", "Hazard and Risk Mapping"),
        ("social_mapping", "Social Mapping"),
        ("economic_mapping", "Economic Activity Mapping"),
        ("cultural_mapping", "Cultural Site Mapping"),
    ]

    STATUS_CHOICES = [
        ("planning", "Planning"),
        ("in_progress", "In Progress"),
        ("review", "Under Review"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]

    assessment = models.ForeignKey(
        Assessment,
        on_delete=models.CASCADE,
        related_name="mapping_activities",
        help_text="Assessment this mapping activity belongs to",
    )

    title = models.CharField(max_length=150, help_text="Title of the mapping activity")

    mapping_type = models.CharField(
        max_length=25, choices=MAPPING_TYPES, help_text="Type of mapping activity"
    )

    description = models.TextField(help_text="Description of the mapping activity")

    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default="planning",
        help_text="Current status of the mapping activity",
    )

    # Geographic coverage
    coverage_area = models.TextField(
        help_text="Description of the geographic area covered"
    )

    coordinates = models.JSONField(
        null=True, blank=True, help_text="Geographic coordinates (GeoJSON format)"
    )

    # Timeline
    start_date = models.DateField(help_text="Start date of mapping activity")

    end_date = models.DateField(help_text="End date of mapping activity")

    # Team and methodology
    mapping_team = models.ManyToManyField(
        User,
        related_name="mapping_activities",
        help_text="Team members involved in mapping",
    )

    methodology = models.TextField(help_text="Methodology used for mapping")

    tools_used = models.TextField(
        blank=True, help_text="Tools and equipment used for mapping"
    )

    # Results
    findings = models.TextField(
        blank=True, help_text="Key findings from the mapping activity"
    )

    map_outputs = models.JSONField(
        null=True, blank=True, help_text="References to map outputs and visualizations"
    )

    # Metadata
    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        help_text="User who created this mapping activity",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["assessment", "start_date"]
        verbose_name_plural = "Mapping Activities"

    def __str__(self):
        return f"{self.title} ({self.assessment.title})"


class NeedsCategory(models.Model):
    """Categories for different types of community needs."""

    SECTOR_TYPES = [
        ("education", "Education"),
        ("economic_development", "Economic Development"),
        ("social_development", "Social Development"),
        ("cultural_development", "Cultural Development"),
        ("infrastructure", "Infrastructure"),
        ("health", "Health"),
        ("governance", "Governance"),
        ("environment", "Environment"),
        ("security", "Peace and Security"),
    ]

    name = models.CharField(
        max_length=100, unique=True, help_text="Name of the needs category"
    )

    sector = models.CharField(
        max_length=25,
        choices=SECTOR_TYPES,
        help_text="Development sector this category belongs to",
    )

    description = models.TextField(help_text="Description of this needs category")

    icon = models.CharField(
        max_length=50, blank=True, help_text="CSS icon class for this category"
    )

    color = models.CharField(
        max_length=7,
        default="#007bff",
        help_text="Color code for this category (hex format)",
    )

    weight_factor = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=1.00,
        help_text="Weight factor for prioritization (0.1 to 2.0)",
    )

    is_active = models.BooleanField(
        default=True, help_text="Whether this category is currently active"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["sector", "name"]
        verbose_name_plural = "Needs Categories"

    def __str__(self):
        return f"{self.name} ({self.get_sector_display()})"


class Need(models.Model):
    """Individual community needs identified through assessments."""

    URGENCY_LEVELS = [
        ("immediate", "Immediate (Within 1 month)"),
        ("short_term", "Short-term (1-6 months)"),
        ("medium_term", "Medium-term (6-12 months)"),
        ("long_term", "Long-term (1+ years)"),
    ]

    FEASIBILITY_LEVELS = [
        ("very_low", "Very Low"),
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
        ("very_high", "Very High"),
    ]

    STATUS_CHOICES = [
        ("identified", "Identified"),
        ("validated", "Validated"),
        ("prioritized", "Prioritized"),
        ("planned", "Planned for Implementation"),
        ("in_progress", "Implementation in Progress"),
        ("completed", "Completed"),
        ("deferred", "Deferred"),
        ("rejected", "Rejected"),
    ]

    # Basic Information
    title = models.CharField(
        max_length=200, help_text="Title/name of the identified need"
    )

    description = models.TextField(help_text="Detailed description of the need")

    category = models.ForeignKey(
        NeedsCategory,
        on_delete=models.PROTECT,
        related_name="needs",
        help_text="Category this need belongs to",
    )

    assessment = models.ForeignKey(
        Assessment,
        on_delete=models.CASCADE,
        related_name="identified_needs",
        null=True,
        blank=True,
        help_text="Assessment that identified this need (optional for community-submitted needs)",
    )

    community = models.ForeignKey(
        OBCCommunity,
        on_delete=models.CASCADE,
        related_name="community_needs",
        help_text="Community that has this need",
    )

    # Impact and Scope
    affected_population = models.IntegerField(
        help_text="Number of people affected by this need"
    )

    affected_households = models.IntegerField(
        null=True, blank=True, help_text="Number of households affected"
    )

    geographic_scope = models.TextField(help_text="Geographic scope/area affected")

    # Prioritization Factors
    urgency_level = models.CharField(
        max_length=15, choices=URGENCY_LEVELS, help_text="How urgent is this need"
    )

    impact_severity = models.IntegerField(
        choices=[(i, str(i)) for i in range(1, 6)],
        help_text="Impact severity on community (1=Low, 5=High)",
    )

    feasibility = models.CharField(
        max_length=10,
        choices=FEASIBILITY_LEVELS,
        help_text="Feasibility of addressing this need",
    )

    estimated_cost = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Estimated cost to address this need",
    )

    # Status and Progress
    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default="identified",
        help_text="Current status of this need",
    )

    priority_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Calculated priority score",
    )

    priority_rank = models.IntegerField(
        null=True, blank=True, help_text="Priority ranking within community"
    )

    # Validation and Evidence
    evidence_sources = models.TextField(help_text="Sources of evidence for this need")

    validation_method = models.CharField(
        max_length=100, blank=True, help_text="Method used to validate this need"
    )

    is_validated = models.BooleanField(
        default=False, help_text="Whether this need has been validated"
    )

    validated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="validated_needs",
        help_text="User who validated this need",
    )

    validation_date = models.DateTimeField(
        null=True, blank=True, help_text="Date when need was validated"
    )

    # ==========================================
    # COMMUNITY PARTICIPATION & BUDGET LINKAGE
    # (Added as per Phase 1 implementation plan)
    # ==========================================

    # PATHWAY TRACKING
    SUBMISSION_TYPE_CHOICES = [
        ("assessment_driven", "Identified During Assessment"),
        ("community_submitted", "Community-Submitted"),
    ]

    submission_type = models.CharField(
        max_length=20,
        choices=SUBMISSION_TYPE_CHOICES,
        default="assessment_driven",
        help_text="How this need was identified",
    )

    # COMMUNITY SUBMISSION FIELDS
    submitted_by_user = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="community_submitted_needs",
        help_text="Community leader who submitted (if community-initiated)",
    )

    submission_date = models.DateField(
        null=True, blank=True, help_text="Date when community submitted this need"
    )

    # PARTICIPATORY BUDGETING
    community_votes = models.PositiveIntegerField(
        default=0,
        help_text="Votes received during participatory budgeting sessions",
    )

    # MAO COORDINATION WORKFLOW
    forwarded_to_mao = models.ForeignKey(
        "coordination.Organization",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="forwarded_needs",
        help_text="MAO that this need was forwarded to",
    )

    forwarded_date = models.DateField(
        null=True, blank=True, help_text="Date when forwarded to MAO"
    )

    forwarded_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="forwarded_needs",
        help_text="OOBC staff who forwarded this need",
    )

    # BUDGET LINKAGE (enables needs-to-budget integration)
    linked_ppa = models.ForeignKey(
        "monitoring.MonitoringEntry",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="addressing_needs",
        help_text="PPA (MonitoringEntry) that addresses this need",
    )

    budget_inclusion_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date when this need was included in budget/PPA",
    )

    # Metadata
    identified_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="identified_needs",
        help_text="User who identified this need",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-priority_score", "-impact_severity", "title"]
        indexes = [
            models.Index(fields=["community", "category"]),
            models.Index(fields=["status", "priority_score"]),
            models.Index(fields=["urgency_level", "impact_severity"]),
            # New indexes for Phase 1 integration (community participation & budget linkage)
            models.Index(fields=["submission_type", "status"]),
            models.Index(fields=["submitted_by_user", "status"]),
            models.Index(fields=["forwarded_to_mao", "status"]),
            models.Index(fields=["linked_ppa"]),  # For gap analysis queries
            models.Index(fields=["community_votes"]),  # For participatory budgeting
        ]

    def __str__(self):
        if self.community:
            return f"{self.title} - {self.community.barangay.name}"
        elif self.province:
            return f"{self.title} - {self.province.name}"
        return self.title

    def calculate_priority_score(self):
        """Calculate priority score based on various factors."""
        # Base score factors
        urgency_weights = {
            "immediate": 4.0,
            "short_term": 3.0,
            "medium_term": 2.0,
            "long_term": 1.0,
        }

        feasibility_weights = {
            "very_high": 2.0,
            "high": 1.5,
            "medium": 1.0,
            "low": 0.5,
            "very_low": 0.25,
        }

        # Calculate base score
        urgency_weight = urgency_weights.get(self.urgency_level, 1.0)
        impact_weight = self.impact_severity / 5.0 * 2.0  # Normalize to 0-2
        feasibility_weight = feasibility_weights.get(self.feasibility, 1.0)

        # Population impact factor
        population_factor = min(self.affected_population / 1000, 2.0)  # Cap at 2.0

        # Category weight factor
        category_weight = float(self.category.weight_factor) if self.category else 1.0

        # Calculate final score
        base_score = (
            urgency_weight + impact_weight + feasibility_weight + population_factor
        ) / 4
        final_score = base_score * category_weight

        return round(final_score, 2)

    @property
    def barangay(self):
        """Legacy accessor exposing the linked barangay."""

        if self.community_id and hasattr(self.community, "barangay"):
            return self.community.barangay
        return None

    @property
    def municipality(self):
        """Return municipality for compatibility with legacy templates."""

        barangay = self.barangay
        if barangay:
            return barangay.municipality
        return None

    @property
    def province(self):
        """Return province derived from the related barangay."""

        municipality = self.municipality
        if municipality:
            return municipality.province
        return None

    @property
    def region(self):
        """Return region derived from the related barangay."""

        province = self.province
        if province:
            return province.region
        return None


class NeedVote(models.Model):
    """
    Individual vote record for participatory budgeting.

    Tracks who voted for which need, when, and with what weight.
    Prevents double-voting and provides audit trail.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # What need was voted for
    need = models.ForeignKey(
        Need,
        on_delete=models.CASCADE,
        related_name="votes",
        help_text="The community need being voted for",
    )

    # Who voted
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="need_votes",
        help_text="The user who cast this vote",
    )

    # Vote details
    vote_weight = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Vote weight (1-5 stars). Default is 1 for simple upvote.",
    )

    comment = models.TextField(
        blank=True, help_text="Optional comment explaining why this need is important"
    )

    # Voter context (optional)
    voter_community = models.ForeignKey(
        "communities.OBCCommunity",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="community_votes",
        help_text="Community the voter belongs to (if applicable)",
    )

    # Metadata
    voted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    ip_address = models.GenericIPAddressField(
        null=True, blank=True, help_text="IP address for fraud detection"
    )

    class Meta:
        verbose_name = "Need Vote"
        verbose_name_plural = "Need Votes"
        unique_together = [["need", "user"]]  # One vote per user per need
        ordering = ["-voted_at"]
        indexes = [
            models.Index(fields=["need", "-voted_at"]),
            models.Index(fields=["user", "-voted_at"]),
            models.Index(fields=["-voted_at"]),
        ]

    def __str__(self):
        weight_stars = "⭐" * self.vote_weight
        return f"{self.user.username} → {self.need.title} ({weight_stars})"

    def save(self, *args, **kwargs):
        """Update need's community_votes counter on save."""
        is_new = self.pk is None
        old_weight = 0

        if not is_new:
            # Get old weight before update
            old_vote = NeedVote.objects.filter(pk=self.pk).first()
            if old_vote:
                old_weight = old_vote.vote_weight

        super().save(*args, **kwargs)

        # Update need's vote count
        if is_new:
            # New vote: add weight
            self.need.community_votes = models.F("community_votes") + self.vote_weight
            self.need.save(update_fields=["community_votes"])
        elif old_weight != self.vote_weight:
            # Vote weight changed: adjust difference
            weight_diff = self.vote_weight - old_weight
            self.need.community_votes = models.F("community_votes") + weight_diff
            self.need.save(update_fields=["community_votes"])

    def delete(self, *args, **kwargs):
        """Update need's community_votes counter on delete."""
        # Subtract vote weight from need
        self.need.community_votes = models.F("community_votes") - self.vote_weight
        self.need.save(update_fields=["community_votes"])
        super().delete(*args, **kwargs)


class NeedsPrioritization(models.Model):
    """Model for tracking needs prioritization exercises."""

    PRIORITIZATION_METHODS = [
        ("scoring_matrix", "Scoring Matrix"),
        ("pairwise_comparison", "Pairwise Comparison"),
        ("ranking", "Simple Ranking"),
        ("mca", "Multi-Criteria Analysis"),
        ("community_voting", "Community Voting"),
        ("expert_panel", "Expert Panel Review"),
    ]

    STATUS_CHOICES = [
        ("planning", "Planning"),
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]

    title = models.CharField(
        max_length=200, help_text="Title of the prioritization exercise"
    )

    description = models.TextField(
        help_text="Description of the prioritization exercise"
    )

    community = models.ForeignKey(
        OBCCommunity,
        on_delete=models.CASCADE,
        related_name="prioritization_exercises",
        help_text="Community for which needs are being prioritized",
    )

    assessment = models.ForeignKey(
        Assessment,
        on_delete=models.CASCADE,
        related_name="prioritization_exercises",
        help_text="Assessment this prioritization belongs to",
    )

    method = models.CharField(
        max_length=20,
        choices=PRIORITIZATION_METHODS,
        help_text="Method used for prioritization",
    )

    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default="planning",
        help_text="Status of the prioritization exercise",
    )

    # Participants
    facilitators = models.ManyToManyField(
        User,
        related_name="facilitated_prioritizations",
        help_text="Users who facilitated this prioritization",
    )

    participant_count = models.IntegerField(
        help_text="Number of community participants"
    )

    stakeholder_groups = models.TextField(
        help_text="Description of stakeholder groups involved"
    )

    # Timeline
    start_date = models.DateField(help_text="Start date of prioritization exercise")

    end_date = models.DateField(help_text="End date of prioritization exercise")

    # Criteria and Results
    prioritization_criteria = models.JSONField(
        help_text="Criteria used for prioritization (JSON format)"
    )

    results = models.JSONField(
        null=True, blank=True, help_text="Prioritization results (JSON format)"
    )

    top_priorities = models.TextField(
        blank=True, help_text="Summary of top priority needs identified"
    )

    recommendations = models.TextField(
        blank=True, help_text="Recommendations based on prioritization"
    )

    # Metadata
    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="created_prioritizations",
        help_text="User who created this prioritization",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-start_date"]

    def __str__(self):
        if self.community:
            return f"{self.title} - {self.community.barangay.name}"
        elif self.province:
            return f"{self.title} - {self.province.name}"
        return self.title


class NeedsPrioritizationItem(models.Model):
    """Individual items in a prioritization exercise."""

    prioritization = models.ForeignKey(
        NeedsPrioritization,
        on_delete=models.CASCADE,
        related_name="prioritization_items",
        help_text="Prioritization exercise this item belongs to",
    )

    need = models.ForeignKey(
        Need,
        on_delete=models.CASCADE,
        related_name="prioritization_items",
        help_text="Need being prioritized",
    )

    rank = models.IntegerField(help_text="Rank assigned in this prioritization")

    score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Score assigned in this prioritization",
    )

    criteria_scores = models.JSONField(
        null=True, blank=True, help_text="Scores for individual criteria (JSON format)"
    )

    justification = models.TextField(
        blank=True, help_text="Justification for the ranking/scoring"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["prioritization", "rank"]
        unique_together = ["prioritization", "need"]

    def __str__(self):
        return f"Rank {self.rank}: {self.need.title}"


class WorkshopActivity(models.Model):
    """Model for managing MANA workshop activities following OBC-MANA guidelines."""

    WORKSHOP_TYPES = [
        ("workshop_1", "Workshop 1: Understanding the Community Context"),
        ("workshop_2", "Workshop 2: Community Aspirations and Priorities"),
        ("workshop_3", "Workshop 3: Community Collaboration and Empowerment"),
        ("workshop_4", "Workshop 4: Community Feedback on Existing Initiatives"),
        ("workshop_5", "Workshop 5: OBCs Needs, Challenges, Factors, and Outcomes"),
        ("workshop_6", "Workshop 6: Ways Forward and Action Planning"),
    ]

    STATUS_CHOICES = [
        ("planned", "Planned"),
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]

    DAYS_MAPPING = [
        ("day_1", "Day 1: Arrival and Registration"),
        ("day_2", "Day 2: Opening and Understanding Community Context"),
        ("day_3", "Day 3: Aspirations, Priorities, Collaboration & Empowerment"),
        ("day_4", "Day 4: Feedback, Challenges, Ways Forward & Closing"),
        ("day_5", "Day 5: Departure"),
    ]

    # Basic Information
    assessment = models.ForeignKey(
        Assessment,
        on_delete=models.CASCADE,
        related_name="workshop_activities",
        help_text="Assessment this workshop belongs to",
    )

    workshop_type = models.CharField(
        max_length=15, choices=WORKSHOP_TYPES, help_text="Type of workshop activity"
    )

    title = models.CharField(max_length=250, help_text="Workshop title")

    description = models.TextField(
        help_text="Detailed description of workshop objectives"
    )

    workshop_day = models.CharField(
        max_length=10, choices=DAYS_MAPPING, help_text="Day of the 5-day MANA schedule"
    )

    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default="planned",
        help_text="Current status of the workshop",
    )

    # Timing
    scheduled_date = models.DateField(help_text="Scheduled date for the workshop")

    start_time = models.TimeField(help_text="Start time of the workshop")

    end_time = models.TimeField(help_text="End time of the workshop")

    duration_hours = models.FloatField(help_text="Duration in hours")

    # Participants and Facilitation
    target_participants = models.IntegerField(help_text="Target number of participants")

    actual_participants = models.IntegerField(
        default=0, help_text="Actual number of participants"
    )

    facilitators = models.ManyToManyField(
        User, related_name="facilitated_workshops", help_text="Workshop facilitators"
    )

    # Workshop Content and Methodology
    methodology = models.TextField(help_text="Workshop methodology and approach")

    materials_needed = models.TextField(
        blank=True, help_text="Materials and supplies needed"
    )

    # Expected Outputs
    expected_outputs = models.TextField(
        help_text="Expected workshop outputs and deliverables"
    )

    # Results
    key_findings = models.TextField(
        blank=True, help_text="Key findings from the workshop"
    )

    recommendations = models.TextField(
        blank=True, help_text="Recommendations emerging from workshop"
    )

    challenges_encountered = models.TextField(
        blank=True, help_text="Challenges encountered during workshop"
    )

    workshop_outputs = models.JSONField(
        null=True, blank=True, help_text="Detailed outputs from the workshop session"
    )

    # Metadata
    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="created_workshops",
        help_text="User who created this workshop",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["workshop_day", "start_time"]
        unique_together = ["assessment", "workshop_type"]

    def __str__(self):
        return f"{self.get_workshop_type_display()} - {self.assessment.title}"


class WorkshopQuestionDefinition(models.Model):
    """Canonical question definitions for Regional MANA workshops."""

    workshop_type = models.CharField(
        max_length=20,
        choices=WorkshopActivity.WORKSHOP_TYPES,
        help_text="Workshop this question belongs to",
    )

    question_id = models.CharField(
        max_length=50,
        help_text="Stable identifier matching schema JSON",
    )

    order = models.PositiveIntegerField(
        default=0,
        help_text="Display order within workshop",
    )

    version = models.CharField(
        max_length=20,
        default="v1",
        help_text="Schema version tag",
    )

    definition = models.JSONField(
        help_text="Full question payload including text, type, fields, and metadata",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["workshop_type", "order", "question_id"]
        unique_together = ["workshop_type", "question_id", "version"]
        verbose_name = "Workshop Question Definition"
        verbose_name_plural = "Workshop Question Definitions"

    def __str__(self):
        return f"{self.workshop_type} - {self.question_id} ({self.version})"


class WorkshopSession(models.Model):
    """Model for individual workshop sessions within a workshop activity."""

    SESSION_TYPES = [
        ("opening", "Opening Session"),
        ("presentation", "Presentation"),
        ("group_work", "Group Work"),
        ("plenary", "Plenary Discussion"),
        ("breakout", "Breakout Session"),
        ("synthesis", "Synthesis Session"),
        ("closing", "Closing Session"),
    ]

    workshop = models.ForeignKey(
        WorkshopActivity,
        on_delete=models.CASCADE,
        related_name="sessions",
        help_text="Workshop this session belongs to",
    )

    session_title = models.CharField(max_length=200, help_text="Title of the session")

    session_type = models.CharField(
        max_length=15, choices=SESSION_TYPES, help_text="Type of session"
    )

    session_order = models.IntegerField(help_text="Order of session within workshop")

    start_time = models.TimeField(help_text="Session start time")

    end_time = models.TimeField(help_text="Session end time")

    facilitator = models.ForeignKey(
        User, on_delete=models.PROTECT, help_text="Primary facilitator for this session"
    )

    objectives = models.TextField(help_text="Session objectives")

    methodology = models.TextField(help_text="Session methodology and activities")

    outputs = models.TextField(blank=True, help_text="Session outputs and results")

    notes = models.TextField(blank=True, help_text="Session notes and observations")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["workshop", "session_order"]
        unique_together = ["workshop", "session_order"]

    def __str__(self):
        return f"Session {self.session_order}: {self.session_title}"


class WorkshopParticipant(models.Model):
    """Model for tracking workshop participants."""

    PARTICIPANT_TYPES = [
        ("elder", "Community Elder"),
        ("women_leader", "Women Leader"),
        ("youth_leader", "Youth Leader"),
        ("farmer", "Farmer"),
        ("fisherfolk", "Fisherfolk"),
        ("religious_leader", "Religious Leader"),
        ("traditional_leader", "Traditional Leader"),
        ("milf_representative", "MILF Representative"),
        ("mnlf_representative", "MNLF Representative"),
        ("business_leader", "Business Leader"),
        ("teacher", "Teacher/Educator"),
        ("health_worker", "Health Worker"),
        ("other", "Other"),
    ]

    workshop = models.ForeignKey(
        WorkshopActivity,
        on_delete=models.CASCADE,
        related_name="participants",
        help_text="Workshop this participant attended",
    )

    name = models.CharField(max_length=100, help_text="Participant name")

    participant_type = models.CharField(
        max_length=20, choices=PARTICIPANT_TYPES, help_text="Type/role of participant"
    )

    gender = models.CharField(
        max_length=10,
        choices=[("male", "Male"), ("female", "Female")],
        help_text="Gender of participant",
    )

    age_group = models.CharField(
        max_length=15,
        choices=[
            ("18-30", "18-30 years"),
            ("31-45", "31-45 years"),
            ("46-60", "46-60 years"),
            ("60+", "60+ years"),
        ],
        help_text="Age group of participant",
    )

    contact_info = models.CharField(
        max_length=100, blank=True, help_text="Contact information"
    )

    organization = models.CharField(
        max_length=150, blank=True, help_text="Organization or group represented"
    )

    attendance_status = models.CharField(
        max_length=15,
        choices=[
            ("attended", "Attended"),
            ("partial", "Partial Attendance"),
            ("absent", "Absent"),
        ],
        default="attended",
        help_text="Attendance status",
    )

    participation_notes = models.TextField(
        blank=True, help_text="Notes on participant contributions"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["participant_type", "name"]
        unique_together = ["workshop", "name", "participant_type"]

    def __str__(self):
        return f"{self.name} ({self.get_participant_type_display()})"


class WorkshopOutput(models.Model):
    """Model for tracking workshop outputs and deliverables."""

    OUTPUT_TYPES = [
        ("community_map", "Community Map"),
        ("timeline", "Historical Timeline"),
        ("asset_inventory", "Asset Inventory"),
        ("stakeholder_map", "Stakeholder Map"),
        ("vision_statement", "Vision Statement"),
        ("needs_assessment", "Needs Assessment"),
        ("priority_list", "Priority List"),
        ("organization_map", "Organization Map"),
        ("collaboration_strategy", "Collaboration Strategy"),
        ("program_feedback", "Program Feedback"),
        ("problem_tree", "Problem Tree"),
        ("solution_inventory", "Solution Inventory"),
        ("action_plan", "Action Plan"),
        ("meta_cards", "Meta Cards"),
        ("flip_charts", "Flip Charts"),
        ("photos", "Photo Documentation"),
        ("audio_recording", "Audio Recording"),
        ("other", "Other Output"),
    ]

    workshop = models.ForeignKey(
        WorkshopActivity,
        on_delete=models.CASCADE,
        related_name="outputs",
        help_text="Workshop that produced this output",
    )

    output_type = models.CharField(
        max_length=30, choices=OUTPUT_TYPES, help_text="Type of workshop output"
    )

    title = models.CharField(max_length=200, help_text="Title or name of the output")

    description = models.TextField(help_text="Description of the output")

    content = models.TextField(help_text="Content or details of the output")

    file_path = models.CharField(
        max_length=500, blank=True, help_text="Path to associated file (if any)"
    )

    created_by_session = models.ForeignKey(
        WorkshopSession,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Session that created this output",
    )

    # Metadata
    created_by = models.ForeignKey(
        User, on_delete=models.PROTECT, help_text="User who documented this output"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["workshop", "output_type"]

    def __str__(self):
        return f"{self.title} ({self.get_output_type_display()})"


class MANAReport(models.Model):
    """Model for managing OBC-MANA reports following the prescribed format."""

    REPORT_STATUS = [
        ("draft", "Draft"),
        ("review", "Under Review"),
        ("validation", "Validation"),
        ("final", "Final Report"),
        ("submitted", "Submitted"),
    ]

    REPORT_SECTIONS = [
        ("executive_summary", "Executive Summary"),
        ("context_background", "Context and Background"),
        ("methodology", "Methodology"),
        ("findings_analysis", "Findings and Analysis"),
        ("priority_recommendations", "Priority Issues and Recommendations"),
        ("implementation_framework", "Implementation Framework"),
        ("annexes", "Annexes"),
    ]

    # Basic Information
    assessment = models.OneToOneField(
        Assessment,
        on_delete=models.CASCADE,
        related_name="mana_report",
        help_text="Assessment this report belongs to",
    )

    title = models.CharField(max_length=300, help_text="Report title")

    report_status = models.CharField(
        max_length=15,
        choices=REPORT_STATUS,
        default="draft",
        help_text="Current status of the report",
    )

    # Report Content
    executive_summary = models.TextField(
        blank=True,
        help_text="Executive summary including key findings and recommendations",
    )

    context_background = models.TextField(
        blank=True, help_text="Legal/policy frameworks and community profile"
    )

    methodology = models.TextField(
        blank=True, help_text="Data collection methods and analytical framework"
    )

    # Findings and Analysis sections
    social_development_findings = models.TextField(
        blank=True, help_text="Education, health, social protection findings"
    )

    economic_development_findings = models.TextField(
        blank=True,
        help_text="Livelihoods, infrastructure, financial inclusion findings",
    )

    cultural_development_findings = models.TextField(
        blank=True,
        help_text="Cultural practices, religious institutions, arts findings",
    )

    rights_protection_findings = models.TextField(
        blank=True, help_text="Governance, access to justice, land rights findings"
    )

    # Priority Issues and Recommendations
    priority_issues = models.TextField(
        blank=True, help_text="Prioritized needs and justification"
    )

    policy_recommendations = models.TextField(
        blank=True, help_text="Policy recommendations for each priority"
    )

    program_development_opportunities = models.TextField(
        blank=True, help_text="Program development opportunities"
    )

    # Implementation Framework
    strategic_approaches = models.TextField(
        blank=True, help_text="Strategic approaches and timeframes"
    )

    stakeholder_roles = models.TextField(
        blank=True, help_text="Stakeholder roles and responsibilities"
    )

    resource_requirements = models.TextField(
        blank=True, help_text="Resource requirements and sources"
    )

    monitoring_evaluation = models.TextField(
        blank=True, help_text="Monitoring and evaluation mechanisms"
    )

    # Validation and Review
    validation_date = models.DateField(
        null=True, blank=True, help_text="Date of validation workshop"
    )

    validation_participants = models.TextField(
        blank=True, help_text="Validation workshop participants"
    )

    validation_feedback = models.TextField(
        blank=True, help_text="Feedback from validation workshop"
    )

    # Submission
    submission_date = models.DateField(
        null=True, blank=True, help_text="Date submitted to Office of Chief Minister"
    )

    submitted_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="submitted_reports",
        help_text="User who submitted the report",
    )

    # Metadata
    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="created_reports",
        help_text="User who created this report",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "MANA Report"
        verbose_name_plural = "MANA Reports"

    def __str__(self):
        return f"{self.title} - {self.get_report_status_display()}"


class BaselineStudy(models.Model):
    """Model for managing socio-economic baseline studies for OBC communities."""

    STUDY_TYPES = [
        ("comprehensive", "Comprehensive Baseline"),
        ("socio_economic", "Socio-Economic Study"),
        ("demographic", "Demographic Study"),
        ("livelihood", "Livelihood Assessment"),
        ("infrastructure", "Infrastructure Assessment"),
        ("service_delivery", "Service Delivery Assessment"),
        ("governance", "Governance Assessment"),
        ("cultural", "Cultural Assessment"),
        ("environmental", "Environmental Assessment"),
    ]

    STATUS_CHOICES = [
        ("planning", "Planning"),
        ("design", "Study Design"),
        ("data_collection", "Data Collection"),
        ("analysis", "Data Analysis"),
        ("reporting", "Report Writing"),
        ("review", "Under Review"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]

    METHODOLOGIES = [
        ("quantitative", "Quantitative"),
        ("qualitative", "Qualitative"),
        ("mixed_methods", "Mixed Methods"),
        ("participatory", "Participatory Research"),
        ("rapid_assessment", "Rapid Assessment"),
    ]

    # Basic Information
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    title = models.CharField(max_length=250, help_text="Title of the baseline study")

    study_type = models.CharField(
        max_length=20, choices=STUDY_TYPES, help_text="Type of baseline study"
    )

    description = models.TextField(help_text="Detailed description of the study")

    objectives = models.TextField(help_text="Study objectives and research questions")

    # Relations
    community = models.ForeignKey(
        OBCCommunity,
        on_delete=models.CASCADE,
        related_name="baseline_studies",
        help_text="Community being studied",
    )

    assessment = models.ForeignKey(
        Assessment,
        on_delete=models.CASCADE,
        related_name="baseline_studies",
        help_text="Parent assessment this baseline study belongs to",
    )

    # Study Management
    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default="planning",
        help_text="Current status of the study",
    )

    methodology = models.CharField(
        max_length=20, choices=METHODOLOGIES, help_text="Research methodology used"
    )

    # Timeline
    planned_start_date = models.DateField(help_text="Planned start date for the study")

    planned_end_date = models.DateField(
        help_text="Planned completion date for the study"
    )

    actual_start_date = models.DateField(
        null=True, blank=True, help_text="Actual start date of the study"
    )

    actual_end_date = models.DateField(
        null=True, blank=True, help_text="Actual completion date of the study"
    )

    # Team and Participants
    principal_investigator = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="led_baseline_studies",
        help_text="Principal investigator for the study",
    )

    research_team = models.ManyToManyField(
        User,
        through="BaselineStudyTeamMember",
        related_name="baseline_study_teams",
        help_text="Research team members",
    )

    # Study Design
    sample_size_target = models.IntegerField(
        null=True, blank=True, help_text="Target sample size for the study"
    )

    sample_size_actual = models.IntegerField(
        default=0, help_text="Actual sample size achieved"
    )

    sampling_method = models.CharField(
        max_length=100, blank=True, help_text="Sampling method used"
    )

    data_collection_methods = models.TextField(
        help_text="Description of data collection methods"
    )

    # Study Areas and Indicators
    study_domains = models.JSONField(
        help_text="Study domains and indicators (JSON format)"
    )

    geographic_coverage = models.TextField(help_text="Geographic coverage of the study")

    target_population = models.TextField(help_text="Description of target population")

    # Budget and Resources
    estimated_budget = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Estimated budget for the study",
    )

    actual_budget = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Actual budget spent",
    )

    funding_source = models.CharField(
        max_length=150, blank=True, help_text="Funding source for the study"
    )

    # Results and Outputs
    key_findings = models.TextField(blank=True, help_text="Summary of key findings")

    baseline_indicators = models.JSONField(
        null=True, blank=True, help_text="Baseline indicator values (JSON format)"
    )

    recommendations = models.TextField(blank=True, help_text="Study recommendations")

    limitations = models.TextField(
        blank=True, help_text="Study limitations and constraints"
    )

    # Data Quality
    response_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Response rate percentage",
    )

    data_quality_score = models.IntegerField(
        choices=[(i, f"{i}/10") for i in range(1, 11)],
        null=True,
        blank=True,
        help_text="Data quality score (1-10)",
    )

    # Documentation
    study_protocol = models.TextField(
        blank=True, help_text="Study protocol and procedures"
    )

    data_analysis_plan = models.TextField(
        blank=True, help_text="Data analysis plan and methods"
    )

    # Ethical Considerations
    ethics_approval = models.BooleanField(
        default=False, help_text="Whether ethics approval was obtained"
    )

    ethics_approval_number = models.CharField(
        max_length=50, blank=True, help_text="Ethics approval reference number"
    )

    consent_procedures = models.TextField(
        blank=True, help_text="Informed consent procedures"
    )

    # Metadata
    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="created_baseline_studies",
        help_text="User who created this study",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["community", "study_type"]),
            models.Index(fields=["status", "planned_start_date"]),
            models.Index(fields=["assessment", "status"]),
        ]

    def __str__(self):
        if self.community:
            return f"{self.title} - {self.community.barangay.name}"
        elif self.province:
            return f"{self.title} - {self.province.name}"
        return self.title

    def clean(self):
        if self.planned_end_date and self.planned_start_date:
            if self.planned_end_date < self.planned_start_date:
                raise ValidationError(
                    "Planned end date cannot be earlier than start date"
                )

        if self.actual_end_date and self.actual_start_date:
            if self.actual_end_date < self.actual_start_date:
                raise ValidationError(
                    "Actual end date cannot be earlier than start date"
                )

    @property
    def duration_days(self):
        """Calculate planned duration in days."""
        if self.planned_start_date and self.planned_end_date:
            return (self.planned_end_date - self.planned_start_date).days
        return None

    @property
    def is_overdue(self):
        """Check if study is overdue."""
        if self.status not in ["completed", "cancelled"] and self.planned_end_date:
            return timezone.now().date() > self.planned_end_date
        return False

    def clean(self):
        # Validate that either community OR province is set, not both
        if not self.community and not self.province:
            raise ValidationError(
                "Either community or province must be specified for the assessment."
            )

        if self.community and self.province:
            raise ValidationError(
                "Assessment cannot be linked to both community and province. Choose one."
            )

        # Validate assessment level consistency
        if self.assessment_level in ["regional", "provincial"] and self.community:
            raise ValidationError(
                "Regional/Provincial assessments should be linked to a province, not a community."
            )

        if self.assessment_level in ["community", "barangay"] and self.province:
            raise ValidationError(
                "Community/Barangay assessments should be linked to a community, not a province."
            )

        # Existing date validations
        if self.planned_end_date and self.planned_start_date:
            if self.planned_end_date < self.planned_start_date:
                raise ValidationError(
                    "Planned end date cannot be earlier than start date"
                )

        if self.actual_end_date and self.actual_start_date:
            if self.actual_end_date < self.actual_start_date:
                raise ValidationError(
                    "Actual end date cannot be earlier than start date"
                )

    @property
    def completion_rate(self):
        """Calculate sample completion rate."""
        if self.sample_size_target and self.sample_size_target > 0:
            return (self.sample_size_actual / self.sample_size_target) * 100
        return 0


class BaselineStudyTeamMember(models.Model):
    """Through model for baseline study team members with roles."""

    TEAM_ROLES = [
        ("principal_investigator", "Principal Investigator"),
        ("co_investigator", "Co-Investigator"),
        ("field_coordinator", "Field Coordinator"),
        ("data_collector", "Data Collector"),
        ("data_analyst", "Data Analyst"),
        ("community_liaison", "Community Liaison"),
        ("translator", "Translator/Interpreter"),
        ("quality_assurance", "Quality Assurance"),
        ("supervisor", "Field Supervisor"),
    ]

    study = models.ForeignKey(BaselineStudy, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.CharField(
        max_length=25,
        choices=TEAM_ROLES,
        help_text="Role of the team member in this study",
    )

    assigned_date = models.DateField(
        default=timezone.now, help_text="Date when assigned to the study"
    )

    is_active = models.BooleanField(
        default=True, help_text="Whether this team member is currently active"
    )

    responsibilities = models.TextField(
        blank=True, help_text="Specific responsibilities and tasks"
    )

    class Meta:
        unique_together = ["study", "user", "role"]

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.get_role_display()}"


class BaselineDataCollection(models.Model):
    """Model for tracking baseline data collection activities."""

    COLLECTION_METHODS = [
        ("household_survey", "Household Survey"),
        ("key_informant_interview", "Key Informant Interview"),
        ("focus_group_discussion", "Focus Group Discussion"),
        ("community_meeting", "Community Meeting"),
        ("observation", "Direct Observation"),
        ("document_review", "Document Review"),
        ("secondary_data", "Secondary Data Collection"),
    ]

    STATUS_CHOICES = [
        ("planned", "Planned"),
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
        ("quality_check", "Quality Check"),
        ("validated", "Validated"),
        ("rejected", "Rejected"),
    ]

    study = models.ForeignKey(
        BaselineStudy,
        on_delete=models.CASCADE,
        related_name="data_collection_activities",
        help_text="Baseline study this data collection belongs to",
    )

    collection_method = models.CharField(
        max_length=25,
        choices=COLLECTION_METHODS,
        help_text="Data collection method used",
    )

    description = models.TextField(
        help_text="Description of the data collection activity"
    )

    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default="planned",
        help_text="Status of the data collection",
    )

    # Timeline
    planned_date = models.DateField(help_text="Planned date for data collection")

    actual_date = models.DateField(
        null=True, blank=True, help_text="Actual date of data collection"
    )

    duration_hours = models.FloatField(
        null=True, blank=True, help_text="Duration of data collection in hours"
    )

    # Location and Participants
    location = models.CharField(
        max_length=200, help_text="Location where data was collected"
    )

    coordinates = models.JSONField(
        null=True, blank=True, help_text="GPS coordinates of collection location"
    )

    target_participants = models.IntegerField(help_text="Target number of participants")

    actual_participants = models.IntegerField(
        default=0, help_text="Actual number of participants"
    )

    participant_demographics = models.JSONField(
        null=True, blank=True, help_text="Demographic breakdown of participants"
    )

    # Data Collection Team
    data_collectors = models.ManyToManyField(
        User,
        related_name="baseline_data_collections",
        help_text="Team members who collected the data",
    )

    supervisor = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="supervised_baseline_collections",
        help_text="Supervisor for this data collection",
    )

    # Data and Quality
    data_collected = models.JSONField(
        null=True, blank=True, help_text="Collected data (JSON format)"
    )

    data_quality_notes = models.TextField(
        blank=True, help_text="Notes on data quality and issues"
    )

    completion_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Completion rate percentage",
    )

    # Validation
    is_validated = models.BooleanField(
        default=False, help_text="Whether the data has been validated"
    )

    validated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="validated_baseline_data",
        help_text="User who validated the data",
    )

    validation_date = models.DateTimeField(
        null=True, blank=True, help_text="Date when data was validated"
    )

    validation_notes = models.TextField(
        blank=True, help_text="Validation notes and feedback"
    )

    # Metadata
    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="created_baseline_collections",
        help_text="User who created this data collection record",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-planned_date"]
        indexes = [
            models.Index(fields=["study", "collection_method"]),
            models.Index(fields=["status", "planned_date"]),
        ]

    def __str__(self):
        return f"{self.get_collection_method_display()} - {self.study.title}"

    @property
    def participation_rate(self):
        """Calculate participation rate."""
        if self.target_participants > 0:
            return (self.actual_participants / self.target_participants) * 100
        return 0


class BaselineIndicator(models.Model):
    """Model for baseline indicators and their values."""

    INDICATOR_TYPES = [
        ("demographic", "Demographic"),
        ("economic", "Economic"),
        ("social", "Social"),
        ("infrastructure", "Infrastructure"),
        ("health", "Health"),
        ("education", "Education"),
        ("governance", "Governance"),
        ("environment", "Environment"),
        ("cultural", "Cultural"),
    ]

    DATA_TYPES = [
        ("percentage", "Percentage"),
        ("count", "Count/Number"),
        ("currency", "Currency Value"),
        ("rate", "Rate"),
        ("index", "Index Score"),
        ("binary", "Yes/No"),
        ("categorical", "Categorical"),
        ("text", "Text/Qualitative"),
    ]

    study = models.ForeignKey(
        BaselineStudy,
        on_delete=models.CASCADE,
        related_name="indicators",
        help_text="Baseline study this indicator belongs to",
    )

    name = models.CharField(max_length=200, help_text="Name of the indicator")

    description = models.TextField(
        help_text="Description and definition of the indicator"
    )

    indicator_type = models.CharField(
        max_length=15, choices=INDICATOR_TYPES, help_text="Type/category of indicator"
    )

    data_type = models.CharField(
        max_length=15, choices=DATA_TYPES, help_text="Data type of the indicator value"
    )

    # Measurement
    unit_of_measurement = models.CharField(
        max_length=50,
        blank=True,
        help_text="Unit of measurement (e.g., %, PHP, persons)",
    )

    baseline_value = models.TextField(help_text="Baseline value of the indicator")

    target_value = models.TextField(
        blank=True, help_text="Target value for this indicator"
    )

    # Calculation and Data Source
    calculation_method = models.TextField(
        blank=True, help_text="How the indicator is calculated"
    )

    data_source = models.CharField(
        max_length=100, help_text="Source of data for this indicator"
    )

    collection_frequency = models.CharField(
        max_length=50,
        blank=True,
        help_text="How frequently this indicator should be collected",
    )

    # Quality and Reliability
    confidence_level = models.CharField(
        max_length=20, blank=True, help_text="Statistical confidence level"
    )

    margin_of_error = models.CharField(
        max_length=20, blank=True, help_text="Margin of error for the indicator"
    )

    data_quality_notes = models.TextField(
        blank=True, help_text="Notes on data quality and reliability"
    )

    # Disaggregation
    disaggregation_categories = models.JSONField(
        null=True, blank=True, help_text="Categories for disaggregating the indicator"
    )

    disaggregated_values = models.JSONField(
        null=True, blank=True, help_text="Disaggregated values (JSON format)"
    )

    # Metadata
    created_by = models.ForeignKey(
        User, on_delete=models.PROTECT, help_text="User who created this indicator"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["indicator_type", "name"]
        unique_together = ["study", "name"]

    def __str__(self):
        return f"{self.name} - {self.study.title}"


class CommunityProfile(models.Model):
    """Model for comprehensive community cultural and historical profile."""

    # Basic Information
    community = models.OneToOneField(
        OBCCommunity,
        on_delete=models.CASCADE,
        related_name="community_profile",
        help_text="OBC community this profile belongs to",
    )

    assessment = models.ForeignKey(
        Assessment,
        on_delete=models.CASCADE,
        related_name="community_profiles",
        help_text="Assessment that created/updated this profile",
    )

    # IV. CULTURAL AND HISTORICAL CONTEXT
    # Historical background
    brief_historical_background = models.TextField(
        blank=True, help_text="Key historical narratives of the community in the area"
    )

    established_year = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1800), MaxValueValidator(2030)],
        help_text="Year the community was established",
    )

    origin_story = models.TextField(
        blank=True, help_text="Story of how the community was established"
    )

    migration_history = models.TextField(
        blank=True, help_text="Migration history and patterns"
    )

    # Cultural practices and traditions
    cultural_practices_traditions = models.TextField(
        blank=True, help_text="Notable customs, traditions, festivals"
    )

    religious_affiliation = models.TextField(
        blank=True, help_text="Religious affiliation and specific practices"
    )

    traditional_leaders_role = models.TextField(
        blank=True, help_text="Role of traditional leaders (Imams, Elders, Chieftains)"
    )

    cultural_preservation_efforts = models.TextField(
        blank=True, help_text="Existing cultural preservation efforts"
    )

    # X. NEEDS ASSESSMENT DATA
    needs_assessment_date = models.DateField(
        null=True, blank=True, help_text="Date of last needs assessment"
    )

    key_findings_last_assessment = models.TextField(
        blank=True, help_text="Key findings from last needs assessment"
    )

    assessment_data_sources = models.TextField(
        blank=True,
        help_text="Data sources (community consultations, surveys, LGU data)",
    )

    identified_gaps = models.TextField(
        blank=True, help_text="Identified gaps based on assessments"
    )

    # Metadata
    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="created_community_profiles",
        help_text="User who created this profile",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["community__barangay__name"]
        verbose_name = "Community Cultural Profile"
        verbose_name_plural = "Community Cultural Profiles"

    def __str__(self):
        return f"Cultural Profile - {self.community.barangay.name}"


class CommunityGovernance(models.Model):
    """Model for community governance and leadership information."""

    RELATIONSHIP_LGU_CHOICES = [
        ("collaborative", "Collaborative"),
        ("strained", "Strained"),
        ("minimal", "Minimal"),
        ("good", "Good"),
        ("excellent", "Excellent"),
    ]

    # Basic Information
    community = models.OneToOneField(
        OBCCommunity,
        on_delete=models.CASCADE,
        related_name="governance_profile",
        help_text="OBC community this governance profile belongs to",
    )

    assessment = models.ForeignKey(
        Assessment,
        on_delete=models.CASCADE,
        related_name="governance_profiles",
        help_text="Assessment that created/updated this profile",
    )

    # V. GOVERNANCE AND COMMUNITY LEADERSHIP
    # Political representation and leadership
    formal_political_representation = models.TextField(
        blank=True, help_text="Presence in Barangay Council, LGU representation"
    )

    informal_leadership_structures = models.TextField(
        blank=True, help_text="Description of informal leadership structures"
    )

    community_organizations = models.TextField(
        blank=True,
        help_text="Community organizations/associations (name, focus, contact)",
    )

    relationship_with_lgu = models.CharField(
        max_length=20,
        choices=RELATIONSHIP_LGU_CHOICES,
        blank=True,
        help_text="Relationship with LGU",
    )

    participation_local_governance = models.TextField(
        blank=True, help_text="Participation in local governance and planning"
    )

    access_government_info = models.TextField(
        blank=True, help_text="Access to information on government programs"
    )

    # XI. CONTACT INFORMATION
    key_community_leaders = models.TextField(
        blank=True,
        help_text="Key community leader(s)/focal person(s) with contact details",
    )

    relevant_lgu_officials = models.TextField(
        blank=True, help_text="Relevant LGU official(s) and their contact information"
    )

    # Legacy fields for backward compatibility
    community_leader = models.CharField(
        max_length=255, blank=True, help_text="Name of the primary community leader"
    )

    leader_contact = models.CharField(
        max_length=100, blank=True, help_text="Contact information for community leader"
    )

    # Metadata
    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="created_governance_profiles",
        help_text="User who created this profile",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["community__barangay__name"]
        verbose_name = "Community Governance Profile"
        verbose_name_plural = "Community Governance Profiles"

    def __str__(self):
        return f"Governance Profile - {self.community.barangay.name}"


class CommunityChallenges(models.Model):
    """Model for tracking community challenges and barriers."""

    CHALLENGE_CATEGORIES = [
        ("governance_policy", "Governance and Policy"),
        ("public_services", "Access to Public Services"),
        ("land_ownership", "Land Ownership and Security"),
        ("economic", "Economic Disparities"),
        ("social_conflict", "Social Instability and Conflict"),
        ("cultural", "Cultural Miscommunication"),
        ("gender", "Gender Inequality"),
        ("substance_abuse", "Substance Abuse"),
        ("financial_fraud", "Investment Scams and Fraud"),
        ("environmental", "Environmental Degradation"),
        ("other", "Other Challenges"),
    ]

    # Basic Information
    community = models.ForeignKey(
        OBCCommunity,
        on_delete=models.CASCADE,
        related_name="challenges",
        help_text="OBC community facing this challenge",
    )

    assessment = models.ForeignKey(
        Assessment,
        on_delete=models.CASCADE,
        related_name="identified_challenges",
        help_text="Assessment that identified this challenge",
    )

    # Challenge Details
    category = models.CharField(
        max_length=20, choices=CHALLENGE_CATEGORIES, help_text="Category of challenge"
    )

    title = models.CharField(max_length=200, help_text="Brief title of the challenge")

    description = models.TextField(help_text="Detailed description of the challenge")

    impact_description = models.TextField(
        help_text="Impact of this challenge on the community"
    )

    affected_population = models.PositiveIntegerField(
        null=True, blank=True, help_text="Number of people affected by this challenge"
    )

    severity_level = models.IntegerField(
        choices=[(i, str(i)) for i in range(1, 6)],
        help_text="Severity level (1=Low, 5=Critical)",
    )

    # Specific challenge fields from original model
    # VI. CHALLENGES AND BARRIERS
    governance_policy_challenges = models.TextField(
        blank=True, help_text="Marginalization, lack of representation issues"
    )

    access_public_services_challenges = models.TextField(
        blank=True,
        help_text="Challenges in accessing education, health, infrastructure",
    )

    land_ownership_security_issues = models.TextField(
        blank=True, help_text="Land ownership and security challenges"
    )

    economic_disparities = models.TextField(
        blank=True, help_text="Poverty, limited employment, economic challenges"
    )

    social_instability_conflict = models.TextField(
        blank=True, help_text="Rido, security issues, social conflicts"
    )

    cultural_miscommunication = models.TextField(
        blank=True, help_text="Cultural miscommunication challenges"
    )

    gender_inequality_issues = models.TextField(
        blank=True, help_text="Gender inequality, early marriage issues"
    )

    substance_abuse_issues = models.TextField(
        blank=True, help_text="Drug use, substance abuse issues"
    )

    investment_scam_issues = models.TextField(
        blank=True, help_text="Investment scams and financial fraud issues"
    )

    environmental_degradation = models.TextField(
        blank=True, help_text="Mining, illegal fishing, environmental issues"
    )

    other_challenges = models.TextField(
        blank=True,
        help_text="Other specific challenges (ISAL education, Halal industry, etc.)",
    )

    challenges_impact = models.TextField(
        blank=True, help_text="Impact of these challenges on the community"
    )

    # Status and Resolution
    is_active = models.BooleanField(
        default=True, help_text="Whether this challenge is currently active"
    )

    resolution_efforts = models.TextField(
        blank=True, help_text="Efforts being made to address this challenge"
    )

    support_needed = models.TextField(
        blank=True, help_text="Support needed to address this challenge"
    )

    # Metadata
    identified_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="identified_challenges",
        help_text="User who identified this challenge",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-severity_level", "category", "title"]
        verbose_name = "Community Challenge"
        verbose_name_plural = "Community Challenges"

    def __str__(self):
        if self.community:
            return f"{self.title} - {self.community.barangay.name}"
        elif self.province:
            return f"{self.title} - {self.province.name}"
        return self.title


class CommunityAspirations(models.Model):
    """Model for tracking community aspirations and development priorities."""

    ASPIRATION_CATEGORIES = [
        ("poverty_eradication", "Poverty Eradication"),
        ("infrastructure", "Infrastructure Development"),
        ("livelihood", "Livelihood Programs"),
        ("education", "Education Enhancement"),
        ("healthcare", "Healthcare Access"),
        ("cultural_preservation", "Cultural Preservation"),
        ("peace_security", "Peace and Security"),
        ("governance", "Governance Improvement"),
        ("environment", "Environmental Protection"),
        ("other", "Other Aspirations"),
    ]

    PRIORITY_LEVELS = [
        ("critical", "Critical Priority"),
        ("high", "High Priority"),
        ("medium", "Medium Priority"),
        ("low", "Low Priority"),
    ]

    # Basic Information
    community = models.ForeignKey(
        OBCCommunity,
        on_delete=models.CASCADE,
        related_name="aspirations",
        help_text="OBC community with this aspiration",
    )

    assessment = models.ForeignKey(
        Assessment,
        on_delete=models.CASCADE,
        related_name="community_aspirations",
        help_text="Assessment that captured this aspiration",
    )

    # Aspiration Details
    category = models.CharField(
        max_length=25, choices=ASPIRATION_CATEGORIES, help_text="Category of aspiration"
    )

    title = models.CharField(max_length=200, help_text="Brief title of the aspiration")

    description = models.TextField(help_text="Detailed description of the aspiration")

    priority_level = models.CharField(
        max_length=10,
        choices=PRIORITY_LEVELS,
        default="medium",
        help_text="Priority level of this aspiration",
    )

    # Specific aspiration fields from original model
    # VII. COMMUNITY ASPIRATIONS AND DEVELOPMENT PRIORITIES
    key_aspirations = models.TextField(
        blank=True,
        help_text="Key community aspirations (poverty eradication, improved services, etc.)",
    )

    infrastructure_priorities = models.TextField(
        blank=True,
        help_text="Infrastructure development priorities (roads, water, health, schools)",
    )

    livelihood_program_priorities = models.TextField(
        blank=True,
        help_text="Livelihood program priorities (agriculture, fisheries, SMEs, Halal, ecotourism)",
    )

    education_priorities = models.TextField(
        blank=True,
        help_text="Education priorities (scholarships, skills training, Madrasah support)",
    )

    healthcare_priorities = models.TextField(
        blank=True, help_text="Healthcare access priorities"
    )

    cultural_preservation_priorities = models.TextField(
        blank=True, help_text="Cultural preservation initiative priorities"
    )

    peace_security_priorities = models.TextField(
        blank=True, help_text="Peace and order/conflict resolution priorities"
    )

    specific_project_proposals = models.TextField(
        blank=True, help_text="Specific project proposals/ideas from the community"
    )

    # Implementation Planning
    estimated_beneficiaries = models.PositiveIntegerField(
        null=True, blank=True, help_text="Estimated number of beneficiaries"
    )

    estimated_budget = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Estimated budget required",
    )

    proposed_timeline = models.CharField(
        max_length=100, blank=True, help_text="Proposed timeline for implementation"
    )

    potential_partners = models.TextField(
        blank=True, help_text="Potential partners for implementation"
    )

    # Status
    is_active = models.BooleanField(
        default=True, help_text="Whether this aspiration is still active/relevant"
    )

    implementation_status = models.CharField(
        max_length=20,
        choices=[
            ("identified", "Identified"),
            ("planning", "Under Planning"),
            ("funded", "Funded"),
            ("implementing", "Being Implemented"),
            ("completed", "Completed"),
            ("deferred", "Deferred"),
        ],
        default="identified",
        help_text="Implementation status",
    )

    # Metadata
    captured_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="captured_aspirations",
        help_text="User who captured this aspiration",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-priority_level", "category", "title"]
        verbose_name = "Community Aspiration"
        verbose_name_plural = "Community Aspirations"

    def __str__(self):
        if self.community:
            return f"{self.title} - {self.community.barangay.name}"
        elif self.province:
            return f"{self.title} - {self.province.name}"
        return self.title


class WorkshopParticipantAccount(models.Model):
    """Authenticated participant account for regional MANA workshops."""

    STAKEHOLDER_TYPES = [
        ("elder", "Community Elder"),
        ("women_leader", "Women Leader"),
        ("youth_leader", "Youth Leader"),
        ("farmer", "Farmer"),
        ("fisherfolk", "Fisherfolk"),
        ("religious_leader", "Religious Leader"),
        ("traditional_leader", "Traditional Leader"),
        ("milf_representative", "MILF Representative"),
        ("mnlf_representative", "MNLF Representative"),
        ("business_leader", "Business Leader"),
        ("teacher", "Teacher/Educator"),
        ("health_worker", "Health Worker"),
        ("lgu_official", "LGU Official"),
        ("ngo_representative", "NGO Representative"),
        ("other", "Other"),
    ]

    # Identity
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="workshop_participant_account",
        help_text="Django user account for authentication",
    )

    assessment = models.ForeignKey(
        Assessment,
        on_delete=models.CASCADE,
        related_name="participant_accounts",
        help_text="Assessment this participant is enrolled in",
    )

    # Demographics
    age = models.PositiveIntegerField(
        null=True, blank=True, help_text="Participant's age"
    )

    SEX_CHOICES = [
        ("male", "Male"),
        ("female", "Female"),
    ]

    sex = models.CharField(
        max_length=10, choices=SEX_CHOICES, blank=True, help_text="Participant's sex"
    )

    # Stakeholder Information
    stakeholder_type = models.CharField(
        max_length=20, choices=STAKEHOLDER_TYPES, help_text="Type of stakeholder"
    )

    # Education
    EDUCATIONAL_LEVELS = [
        ("graduate_degree", "Graduate Degree Holder"),
        ("bachelors_degree", "Bachelor's Degree Holder"),
        ("college_level", "College Level"),
        ("high_school_graduate", "High School Graduate"),
        ("high_school_level", "High School Level"),
        ("elementary_level", "Elementary Level"),
        ("no_formal_education", "No Formal Education"),
    ]

    educational_level = models.CharField(
        max_length=50,
        choices=EDUCATIONAL_LEVELS,
        blank=True,
        help_text="Educational attainment",
    )

    ARABIC_EDUCATION_LEVELS = [
        ("kulliyah_graduate", "Kulliyah Graduate"),
        ("thanawiyyah_level", "Thanawiyyah Level"),
        ("mutawassitah_level", "Mutawassitah Level"),
        ("ibtidaiyyah_level", "Ibtidaiyyah Level"),
        ("tahfidz_graduate", "Tahfidz Graduate/Level"),
        ("no_arabic_education", "No Arabic Education"),
    ]

    arabic_education_level = models.CharField(
        max_length=50,
        choices=ARABIC_EDUCATION_LEVELS,
        blank=True,
        help_text="Arabic/Islamic education level",
    )

    # Occupation
    OCCUPATION_CHOICES = [
        ("government_employee", "Government Employee"),
        ("business_owner", "Business Owner"),
        ("private_sector", "Private Sector Employee"),
        ("ngo_worker", "NGO Worker"),
        ("farmer", "Farmer"),
        ("fisherfolk", "Fisherfolk"),
        ("teacher", "Teacher/Educator"),
        ("health_worker", "Health Worker"),
        ("religious_worker", "Religious Worker/Imam"),
        ("traditional_leader", "Traditional/Community Leader"),
        ("student", "Student"),
        ("self_employed", "Self-Employed"),
        ("unemployed", "Unemployed"),
        ("retired", "Retired"),
        ("other", "Other"),
    ]

    occupation = models.CharField(
        max_length=50,
        choices=OCCUPATION_CHOICES,
        blank=True,
        help_text="Current occupation",
    )

    # Office/Business Information (Optional)
    office_business_name = models.CharField(
        max_length=200, blank=True, help_text="Name of office or business (optional)"
    )

    office_mandate = models.TextField(
        blank=True, help_text="Mandate of office (if government agency, optional)"
    )

    # Geography - Participant Address
    region = models.ForeignKey(
        Region,
        on_delete=models.CASCADE,
        related_name="workshop_participants_region",
        null=True,
        blank=True,
        help_text="Region of participant",
    )

    province = models.ForeignKey(
        Province,
        on_delete=models.CASCADE,
        related_name="workshop_participants",
        help_text="Province represented by this participant",
    )

    municipality = models.ForeignKey(
        Municipality,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="workshop_participants",
        help_text="Municipality (optional)",
    )

    barangay = models.ForeignKey(
        Barangay,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="workshop_participants",
        help_text="Barangay (optional)",
    )

    # Office/Business Address (Optional)
    office_region = models.ForeignKey(
        Region,
        on_delete=models.SET_NULL,
        related_name="office_participants",
        null=True,
        blank=True,
        help_text="Office region (optional)",
    )

    office_province = models.ForeignKey(
        Province,
        on_delete=models.SET_NULL,
        related_name="office_participants",
        null=True,
        blank=True,
        help_text="Office province (optional)",
    )

    office_municipality = models.ForeignKey(
        Municipality,
        on_delete=models.SET_NULL,
        related_name="office_participants",
        null=True,
        blank=True,
        help_text="Office municipality (optional)",
    )

    office_barangay = models.ForeignKey(
        Barangay,
        on_delete=models.SET_NULL,
        related_name="office_participants",
        null=True,
        blank=True,
        help_text="Office barangay (optional)",
    )

    # Mandate Awareness
    aware_of_mandate = models.BooleanField(
        default=False,
        help_text="Aware of the Mandate for Assistance to Other Bangsamoro Communities",
    )

    # Completion State
    completed_workshops = models.JSONField(
        default=list,
        help_text="List of completed workshop types (e.g., ['workshop_1', 'workshop_2'])",
    )

    current_workshop = models.CharField(
        max_length=15,
        blank=True,
        help_text="Currently accessible workshop type",
    )

    # Onboarding
    consent_given = models.BooleanField(
        default=False, help_text="Whether participant gave consent"
    )

    consent_date = models.DateTimeField(
        null=True, blank=True, help_text="Date consent was given"
    )

    profile_completed = models.BooleanField(
        default=False, help_text="Whether profile is complete"
    )

    # Metadata
    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="created_participant_accounts",
        help_text="Facilitator who created this account",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Facilitator-controlled advancement tracking
    facilitator_advanced_to = models.CharField(
        max_length=15,
        default="workshop_1",
        help_text="Maximum workshop unlocked by facilitator for this participant",
    )

    class Meta:
        ordering = ["province", "user__last_name"]
        unique_together = ["user", "assessment"]
        verbose_name = "Workshop Participant Account"
        verbose_name_plural = "Workshop Participant Accounts"
        permissions = [
            ("can_access_regional_mana", "Can access regional MANA workshops"),
            ("can_view_provincial_obc", "Can view provincial OBC data"),
            ("can_facilitate_workshop", "Can facilitate and manage MANA workshops"),
        ]

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.province.name}"


class FacilitatorAssessmentAssignment(models.Model):
    """Assignment of facilitators to specific MANA assessments."""

    facilitator = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="facilitator_assignments",
        help_text="Facilitator user assigned to this assessment",
    )

    assessment = models.ForeignKey(
        Assessment,
        on_delete=models.CASCADE,
        related_name="facilitator_assignments",
        help_text="Assessment the facilitator is assigned to",
    )

    assigned_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="facilitator_assignments_created",
        help_text="Staff/superuser who made this assignment",
    )

    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-assigned_at"]
        unique_together = ["facilitator", "assessment"]
        verbose_name = "Facilitator Assessment Assignment"
        verbose_name_plural = "Facilitator Assessment Assignments"

    def __str__(self):
        return f"{self.facilitator.get_full_name()} → {self.assessment.title}"


class WorkshopNotification(models.Model):
    """In-app notifications for workshop participants."""

    NOTIFICATION_TYPES = [
        ("workshop_advanced", "Workshop Advanced"),
        ("workshop_reminder", "Workshop Reminder"),
        ("assessment_complete", "Assessment Complete"),
    ]

    participant = models.ForeignKey(
        WorkshopParticipantAccount,
        on_delete=models.CASCADE,
        related_name="notifications",
        help_text="Participant receiving this notification",
    )

    notification_type = models.CharField(
        max_length=30,
        choices=NOTIFICATION_TYPES,
        help_text="Type of notification",
    )

    title = models.CharField(
        max_length=200,
        help_text="Notification title",
    )

    message = models.TextField(
        help_text="Notification message content",
    )

    workshop = models.ForeignKey(
        WorkshopActivity,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="notifications",
        help_text="Related workshop (if applicable)",
    )

    is_read = models.BooleanField(
        default=False,
        help_text="Whether participant has read this notification",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Workshop Notification"
        verbose_name_plural = "Workshop Notifications"
        indexes = [
            models.Index(fields=["participant", "-created_at"]),
            models.Index(fields=["participant", "is_read"]),
        ]

    def __str__(self):
        return f"{self.participant.user.get_full_name()} - {self.title}"

    def mark_as_read(self):
        """Mark notification as read."""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=["is_read", "read_at"])


class WorkshopResponse(models.Model):
    """Structured responses to workshop questions."""

    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("submitted", "Submitted"),
        ("validated", "Validated"),
    ]

    # Relations
    participant = models.ForeignKey(
        WorkshopParticipantAccount,
        on_delete=models.CASCADE,
        related_name="responses",
        help_text="Participant who submitted this response",
    )

    workshop = models.ForeignKey(
        WorkshopActivity,
        on_delete=models.CASCADE,
        related_name="structured_responses",
        help_text="Workshop this response belongs to",
    )

    question_id = models.CharField(
        max_length=50, help_text="Question identifier from schema"
    )

    # Response Data
    response_data = models.JSONField(
        help_text="Response content (structure depends on question type)"
    )

    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default="draft",
        help_text="Response status",
    )

    # Metadata
    submitted_at = models.DateTimeField(
        null=True, blank=True, help_text="When response was submitted"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["workshop", "participant", "question_id"]
        unique_together = ["participant", "workshop", "question_id"]
        indexes = [
            models.Index(fields=["workshop", "status"]),
            models.Index(fields=["participant", "workshop"]),
        ]

    def __str__(self):
        return f"{self.participant.user.get_full_name()} - {self.workshop.workshop_type} - Q{self.question_id}"


class WorkshopAccessLog(models.Model):
    """Audit log for workshop access and actions."""

    ACTION_TYPES = [
        ("view", "Viewed Workshop"),
        ("submit", "Submitted Response"),
        ("update", "Updated Response"),
        ("unlock", "Workshop Unlocked"),
        ("complete", "Workshop Completed"),
    ]

    # Relations
    participant = models.ForeignKey(
        WorkshopParticipantAccount,
        on_delete=models.CASCADE,
        related_name="access_logs",
        help_text="Participant who performed the action",
    )

    workshop = models.ForeignKey(
        WorkshopActivity,
        on_delete=models.CASCADE,
        related_name="access_logs",
        help_text="Workshop accessed",
    )

    # Action Details
    action_type = models.CharField(
        max_length=15, choices=ACTION_TYPES, help_text="Type of action"
    )

    metadata = models.JSONField(
        null=True,
        blank=True,
        help_text="Additional metadata (IP address, user agent, etc.)",
    )

    # Timestamp
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["participant", "workshop"]),
            models.Index(fields=["action_type", "created_at"]),
        ]

    def __str__(self):
        return f"{self.participant.user.get_full_name()} - {self.get_action_type_display()} - {self.created_at}"


class WorkshopSynthesis(models.Model):
    """AI-generated synthesis of workshop outputs."""

    STATUS_CHOICES = [
        ("queued", "Queued"),
        ("processing", "Processing"),
        ("completed", "Completed"),
        ("failed", "Failed"),
        ("reviewed", "Reviewed"),
        ("approved", "Approved"),
    ]

    # Relations
    assessment = models.ForeignKey(
        Assessment,
        on_delete=models.CASCADE,
        related_name="workshop_syntheses",
        help_text="Assessment this synthesis belongs to",
    )

    workshop = models.ForeignKey(
        WorkshopActivity,
        on_delete=models.CASCADE,
        related_name="syntheses",
        help_text="Workshop being synthesized",
    )

    # Synthesis Configuration
    prompt_template = models.TextField(help_text="Prompt template used for synthesis")

    filters = models.JSONField(
        null=True,
        blank=True,
        help_text="Filters applied (province, stakeholder type, etc.)",
    )

    # Results
    synthesis_text = models.TextField(
        blank=True, help_text="Generated synthesis content"
    )

    key_themes = models.JSONField(
        null=True, blank=True, help_text="Extracted key themes and patterns"
    )

    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default="queued",
        help_text="Synthesis status",
    )

    # AI Provider Metadata
    provider = models.CharField(
        max_length=50,
        blank=True,
        help_text="AI provider used (e.g., OpenAI, Anthropic)",
    )

    model = models.CharField(
        max_length=50, blank=True, help_text="Model used (e.g., gpt-4, claude-3)"
    )

    tokens_used = models.IntegerField(
        null=True, blank=True, help_text="Tokens consumed"
    )

    processing_time_seconds = models.FloatField(
        null=True, blank=True, help_text="Processing time in seconds"
    )

    error_message = models.TextField(blank=True, help_text="Error message if failed")

    # Review and Approval
    reviewed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_syntheses",
        help_text="User who reviewed this synthesis",
    )

    review_notes = models.TextField(
        blank=True, help_text="Review notes from facilitator"
    )

    approved_at = models.DateTimeField(
        null=True, blank=True, help_text="When synthesis was approved"
    )

    # Metadata
    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="created_syntheses",
        help_text="User who requested this synthesis",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["assessment", "status"]),
            models.Index(fields=["workshop", "status"]),
        ]
        verbose_name = "Workshop Synthesis"
        verbose_name_plural = "Workshop Syntheses"

    def __str__(self):
        return f"Synthesis - {self.workshop.get_workshop_type_display()} - {self.get_status_display()}"

import uuid

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone

from communities.models import OBCCommunity
from mana.models import Assessment, Need

User = get_user_model()


class PolicyRecommendation(models.Model):
    """Model for tracking policy recommendations from OBC needs assessments."""

    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("under_review", "Under Review"),
        ("needs_revision", "Needs Revision"),
        ("submitted", "Submitted to Chief Minister"),
        ("under_consideration", "Under Consideration"),
        ("approved", "Approved"),
        ("in_implementation", "In Implementation"),
        ("implemented", "Implemented"),
        ("rejected", "Rejected"),
        ("withdrawn", "Withdrawn"),
        ("on_hold", "On Hold"),
        ("expired", "Expired"),
    ]

    PRIORITY_LEVELS = [
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
        ("urgent", "Urgent"),
        ("critical", "Critical"),
    ]

    POLICY_CATEGORIES = [
        ("economic_development", "Economic Development"),
        ("social_development", "Social Development"),
        ("cultural_development", "Cultural Development"),
        ("rehabilitation_development", "Rehabilitation & Development"),
        ("protection_of_rights", "Protection of Rights"),
    ]

    SCOPE_LEVELS = [
        ("national", "National Level"),
        ("regional", "Regional Level (BARMM)"),
        ("provincial", "Provincial Level"),
        ("municipal", "Municipal/City Level"),
        ("barangay", "Barangay Level"),
        ("community", "Community Level"),
    ]

    # Basic Information
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    title = models.CharField(
        max_length=255, help_text="Title of the policy recommendation"
    )

    reference_number = models.CharField(
        max_length=50,
        unique=True,
        blank=True,
        help_text="Unique reference number for tracking",
    )

    category = models.CharField(
        max_length=30, choices=POLICY_CATEGORIES, help_text="Policy category"
    )

    description = models.TextField(
        help_text="Detailed description of the policy recommendation"
    )

    rationale = models.TextField(help_text="Rationale and justification for the policy")

    scope = models.CharField(
        max_length=15, choices=SCOPE_LEVELS, help_text="Scope and level of the policy"
    )

    # Relationships
    target_communities = models.ManyToManyField(
        OBCCommunity,
        related_name="policy_recommendations",
        blank=True,
        help_text="OBC communities that would be affected by this policy",
    )

    related_assessments = models.ManyToManyField(
        Assessment,
        related_name="policy_recommendations",
        blank=True,
        help_text="MANA assessments that support this recommendation",
    )

    related_needs = models.ManyToManyField(
        Need,
        related_name="policy_recommendations",
        blank=True,
        help_text="Specific assessed needs addressed by this policy",
    )

    # Management
    proposed_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="proposed_policies",
        help_text="User who proposed this policy",
    )

    lead_author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="authored_policies",
        help_text="Primary author/coordinator for this policy",
    )

    contributing_authors = models.ManyToManyField(
        User,
        related_name="co_authored_policies",
        blank=True,
        help_text="Additional authors and contributors",
    )

    assigned_reviewer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="policies_to_review",
        help_text="User assigned to review this policy",
    )

    # Status and Timeline
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="draft",
        help_text="Current status of the policy recommendation",
    )

    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_LEVELS,
        default="medium",
        help_text="Priority level",
    )

    submission_date = models.DateField(
        null=True, blank=True, help_text="Date submitted to higher authority"
    )

    review_deadline = models.DateField(
        null=True, blank=True, help_text="Deadline for review completion"
    )

    approval_date = models.DateField(
        null=True, blank=True, help_text="Date when policy was approved"
    )

    implementation_start_date = models.DateField(
        null=True, blank=True, help_text="Expected/actual implementation start date"
    )

    implementation_deadline = models.DateField(
        null=True, blank=True, help_text="Expected implementation completion date"
    )

    # Policy Content
    problem_statement = models.TextField(
        help_text="Clear statement of the problem being addressed"
    )

    policy_objectives = models.TextField(
        help_text="Specific objectives the policy aims to achieve"
    )

    proposed_solution = models.TextField(help_text="Detailed proposed solution")

    implementation_strategy = models.TextField(
        blank=True, help_text="Strategy for implementing the policy"
    )

    success_metrics = models.TextField(
        blank=True, help_text="Metrics for measuring policy success"
    )

    # Impact Assessment
    expected_outcomes = models.TextField(help_text="Expected outcomes and benefits")

    potential_risks = models.TextField(
        blank=True, help_text="Potential risks and challenges"
    )

    mitigation_strategies = models.TextField(
        blank=True, help_text="Strategies to mitigate identified risks"
    )

    stakeholder_impact = models.TextField(
        blank=True, help_text="Impact on various stakeholders"
    )

    # Resource Requirements
    budget_implications = models.TextField(
        blank=True, help_text="Budget requirements and financial implications"
    )

    estimated_cost = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Estimated implementation cost (in PHP)",
    )

    funding_source = models.CharField(
        max_length=255, blank=True, help_text="Proposed funding source(s)"
    )

    human_resources_required = models.TextField(
        blank=True, help_text="Human resources and staffing requirements"
    )

    technical_requirements = models.TextField(
        blank=True, help_text="Technical requirements and infrastructure needs"
    )

    # Legal and Regulatory
    legal_implications = models.TextField(
        blank=True, help_text="Legal implications and regulatory considerations"
    )

    regulatory_changes_needed = models.TextField(
        blank=True, help_text="Required regulatory or legal changes"
    )

    compliance_requirements = models.TextField(
        blank=True, help_text="Compliance requirements and standards"
    )

    # Implementation
    implementation_phases = models.TextField(
        blank=True, help_text="Implementation phases and timeline"
    )

    responsible_agencies = models.TextField(
        blank=True, help_text="Agencies responsible for implementation"
    )

    monitoring_framework = models.TextField(
        blank=True, help_text="Framework for monitoring implementation"
    )

    reporting_requirements = models.TextField(
        blank=True, help_text="Reporting requirements and schedule"
    )

    # Review and Feedback
    review_comments = models.TextField(blank=True, help_text="Comments from reviewers")

    revision_history = models.JSONField(
        null=True, blank=True, help_text="History of revisions and changes"
    )

    feedback_summary = models.TextField(
        blank=True, help_text="Summary of stakeholder feedback"
    )

    # Outcomes and Evaluation
    actual_outcomes = models.TextField(
        blank=True, help_text="Actual outcomes achieved (post-implementation)"
    )

    lessons_learned = models.TextField(
        blank=True, help_text="Lessons learned during implementation"
    )

    recommendations_for_improvement = models.TextField(
        blank=True, help_text="Recommendations for future improvements"
    )

    # Metadata
    notes = models.TextField(blank=True, help_text="Additional notes and observations")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status", "priority"]),
            models.Index(fields=["category", "status"]),
            models.Index(fields=["proposed_by", "status"]),
            models.Index(fields=["submission_date", "priority"]),
        ]

    def __str__(self):
        return (
            f"{self.reference_number}: {self.title}"
            if self.reference_number
            else self.title
        )

    def save(self, *args, **kwargs):
        if not self.reference_number:
            # Generate reference number
            year = timezone.now().year
            count = (
                PolicyRecommendation.objects.filter(created_at__year=year).count() + 1
            )
            self.reference_number = f"OOBC-PR-{year}-{count:04d}"
        super().save(*args, **kwargs)

    @property
    def is_overdue(self):
        """Check if policy review is overdue."""
        if self.review_deadline and self.status in ["under_review", "needs_revision"]:
            return timezone.now().date() > self.review_deadline
        return False

    @property
    def days_since_submission(self):
        """Calculate days since submission."""
        if self.submission_date:
            return (timezone.now().date() - self.submission_date).days
        return None


class PolicyEvidence(models.Model):
    """Model for documenting evidence supporting policy recommendations."""

    EVIDENCE_TYPES = [
        ("quantitative_data", "Quantitative Data"),
        ("qualitative_data", "Qualitative Data"),
        ("research_study", "Research Study"),
        ("needs_assessment", "Needs Assessment"),
        ("stakeholder_consultation", "Stakeholder Consultation"),
        ("case_study", "Case Study"),
        ("best_practice", "Best Practice"),
        ("legal_precedent", "Legal Precedent"),
        ("expert_opinion", "Expert Opinion"),
        ("field_observation", "Field Observation"),
        ("document_analysis", "Document Analysis"),
        ("comparative_analysis", "Comparative Analysis"),
        ("other", "Other"),
    ]

    RELIABILITY_LEVELS = [
        ("high", "High Reliability"),
        ("medium", "Medium Reliability"),
        ("low", "Low Reliability"),
        ("unverified", "Unverified"),
    ]

    policy = models.ForeignKey(
        PolicyRecommendation,
        on_delete=models.CASCADE,
        related_name="evidence",
        help_text="Policy recommendation this evidence supports",
    )

    title = models.CharField(max_length=255, help_text="Title of the evidence")

    evidence_type = models.CharField(
        max_length=25, choices=EVIDENCE_TYPES, help_text="Type of evidence"
    )

    description = models.TextField(help_text="Detailed description of the evidence")

    source = models.CharField(
        max_length=255, blank=True, help_text="Source of the evidence"
    )

    methodology = models.TextField(
        blank=True, help_text="Methodology used to collect this evidence"
    )

    # Reliability and Quality
    reliability_level = models.CharField(
        max_length=15,
        choices=RELIABILITY_LEVELS,
        default="medium",
        help_text="Assessed reliability of this evidence",
    )

    quality_notes = models.TextField(
        blank=True, help_text="Notes on evidence quality and limitations"
    )

    # Content
    key_findings = models.TextField(
        blank=True, help_text="Key findings from this evidence"
    )

    relevance_explanation = models.TextField(
        help_text="Explanation of how this evidence supports the policy"
    )

    statistical_data = models.JSONField(
        null=True, blank=True, help_text="Statistical data in JSON format"
    )

    # Documentation
    document = models.FileField(
        upload_to="policy_evidence/%Y/%m/",
        null=True,
        blank=True,
        help_text="Supporting document file",
    )

    url = models.URLField(blank=True, help_text="URL to online source")

    reference_citation = models.TextField(
        blank=True, help_text="Full citation for academic/formal references"
    )

    # Timeline
    date_collected = models.DateField(
        null=True, blank=True, help_text="Date when evidence was collected"
    )

    date_added = models.DateField(
        auto_now_add=True, help_text="Date when evidence was added to policy"
    )

    # Verification
    verified = models.BooleanField(
        default=False, help_text="Whether this evidence has been verified"
    )

    verified_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="verified_evidence",
        help_text="User who verified this evidence",
    )

    verification_date = models.DateField(
        null=True, blank=True, help_text="Date of verification"
    )

    verification_notes = models.TextField(
        blank=True, help_text="Verification notes and comments"
    )

    # Metadata
    added_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="added_evidence",
        help_text="User who added this evidence",
    )

    notes = models.TextField(blank=True, help_text="Additional notes")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-date_added"]
        indexes = [
            models.Index(fields=["policy", "evidence_type"]),
            models.Index(fields=["reliability_level", "verified"]),
        ]

    def __str__(self):
        return f"{self.title} - {self.policy.title}"


class PolicyImpact(models.Model):
    """Model for tracking expected and actual impacts of policy recommendations."""

    IMPACT_TYPES = [
        ("economic", "Economic Impact"),
        ("social", "Social Impact"),
        ("educational", "Educational Impact"),
        ("cultural", "Cultural Impact"),
        ("infrastructure", "Infrastructure Impact"),
        ("healthcare", "Healthcare Impact"),
        ("environmental", "Environmental Impact"),
        ("governance", "Governance Impact"),
        ("human_rights", "Human Rights Impact"),
        ("legal", "Legal Impact"),
        ("administrative", "Administrative Impact"),
        ("other", "Other Impact"),
    ]

    MEASUREMENT_TYPES = [
        ("quantitative", "Quantitative"),
        ("qualitative", "Qualitative"),
        ("mixed", "Mixed Methods"),
    ]

    policy = models.ForeignKey(
        PolicyRecommendation,
        on_delete=models.CASCADE,
        related_name="impacts",
        help_text="Policy this impact relates to",
    )

    impact_type = models.CharField(
        max_length=15, choices=IMPACT_TYPES, help_text="Type of impact"
    )

    title = models.CharField(max_length=255, help_text="Title of the impact indicator")

    description = models.TextField(help_text="Detailed description of the impact")

    # Measurement
    measurement_type = models.CharField(
        max_length=15,
        choices=MEASUREMENT_TYPES,
        default="quantitative",
        help_text="Type of measurement approach",
    )

    measurement_method = models.TextField(help_text="Method for measuring this impact")

    unit_of_measurement = models.CharField(
        max_length=100,
        blank=True,
        help_text="Unit of measurement (e.g., percentage, number, PHP)",
    )

    # Baseline and Targets
    baseline_value = models.CharField(
        max_length=200,
        blank=True,
        help_text="Baseline value before policy implementation",
    )

    baseline_date = models.DateField(
        null=True, blank=True, help_text="Date of baseline measurement"
    )

    target_value = models.CharField(
        max_length=200, blank=True, help_text="Target value to be achieved"
    )

    target_date = models.DateField(
        null=True, blank=True, help_text="Target date for achieving the value"
    )

    # Actual Results
    current_value = models.CharField(
        max_length=200, blank=True, help_text="Current measured value"
    )

    last_measurement_date = models.DateField(
        null=True, blank=True, help_text="Date of last measurement"
    )

    final_value = models.CharField(
        max_length=200,
        blank=True,
        help_text="Final achieved value (post-implementation)",
    )

    final_assessment_date = models.DateField(
        null=True, blank=True, help_text="Date of final impact assessment"
    )

    # Analysis
    analysis_notes = models.TextField(
        blank=True, help_text="Analysis of impact results"
    )

    variance_explanation = models.TextField(
        blank=True, help_text="Explanation for variance between target and actual"
    )

    contributing_factors = models.TextField(
        blank=True, help_text="Factors that contributed to the impact"
    )

    # Quality and Reliability
    data_quality = models.CharField(
        max_length=10,
        choices=[
            ("excellent", "Excellent"),
            ("good", "Good"),
            ("fair", "Fair"),
            ("poor", "Poor"),
        ],
        blank=True,
        help_text="Quality of impact data",
    )

    confidence_level = models.CharField(
        max_length=10,
        choices=[
            ("high", "High"),
            ("medium", "Medium"),
            ("low", "Low"),
        ],
        default="medium",
        help_text="Confidence level in the impact measurement",
    )

    # Metadata
    measured_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="measured_impacts",
        help_text="User who conducted the impact measurement",
    )

    notes = models.TextField(blank=True, help_text="Additional notes")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["impact_type", "title"]
        indexes = [
            models.Index(fields=["policy", "impact_type"]),
            models.Index(fields=["target_date", "policy"]),
        ]

    def __str__(self):
        return f"{self.title} - {self.policy.title}"

    @property
    def target_achievement_percentage(self):
        """Calculate percentage of target achieved (for numeric values only)."""
        try:
            if self.baseline_value and self.target_value and self.current_value:
                baseline = float(self.baseline_value)
                target = float(self.target_value)
                current = float(self.current_value)

                if target > baseline:
                    # Positive target (increase)
                    progress = (current - baseline) / (target - baseline) * 100
                else:
                    # Negative target (decrease)
                    progress = (baseline - current) / (baseline - target) * 100

                return round(progress, 2)
        except (ValueError, ZeroDivisionError):
            pass
        return None


class PolicyDocument(models.Model):
    """Model for managing documents related to policy recommendations."""

    DOCUMENT_TYPES = [
        ("policy_draft", "Policy Draft"),
        ("supporting_doc", "Supporting Document"),
        ("evidence", "Evidence Document"),
        ("consultation_report", "Consultation Report"),
        ("impact_assessment", "Impact Assessment"),
        ("implementation_plan", "Implementation Plan"),
        ("monitoring_report", "Monitoring Report"),
        ("evaluation_report", "Evaluation Report"),
        ("correspondence", "Correspondence"),
        ("presentation", "Presentation"),
        ("legal_opinion", "Legal Opinion"),
        ("other", "Other"),
    ]

    policy = models.ForeignKey(
        PolicyRecommendation,
        on_delete=models.CASCADE,
        related_name="documents",
        help_text="Policy this document belongs to",
    )

    document_type = models.CharField(
        max_length=20, choices=DOCUMENT_TYPES, help_text="Type of document"
    )

    title = models.CharField(max_length=255, help_text="Title of the document")

    description = models.TextField(blank=True, help_text="Description of the document")

    version = models.CharField(
        max_length=10, default="1.0", help_text="Document version"
    )

    file = models.FileField(
        upload_to="policy_documents/%Y/%m/", help_text="Document file"
    )

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

    # Document Metadata
    document_date = models.DateField(
        null=True, blank=True, help_text="Date of the document"
    )

    author = models.CharField(max_length=255, blank=True, help_text="Document author")

    # Upload Details
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="uploaded_policy_documents",
        help_text="User who uploaded this document",
    )

    upload_date = models.DateTimeField(auto_now_add=True)

    notes = models.TextField(blank=True, help_text="Additional notes")

    class Meta:
        ordering = ["-upload_date"]
        indexes = [
            models.Index(fields=["policy", "document_type"]),
            models.Index(fields=["is_confidential", "is_public"]),
        ]

    def __str__(self):
        return f"{self.title} v{self.version} - {self.policy.title}"

    def save(self, *args, **kwargs):
        if self.file:
            self.file_size = self.file.size
        super().save(*args, **kwargs)

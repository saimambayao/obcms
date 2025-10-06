"""Monitoring and Evaluation domain models."""

import uuid
from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import F, Q, Sum

ZERO_DECIMAL = Decimal("0.00")


class MonitoringEntryQuerySet(models.QuerySet):
    """Custom queryset for MonitoringEntry with common filters and optimizations."""

    def with_related(self):
        """Prefetch all common relationships for performance."""
        return self.select_related(
            "lead_organization",
            "implementing_moa",
            "submitted_by_community",
            "submitted_to_organization",
            "related_assessment",
            "related_policy",
            "coverage_region",
            "coverage_province",
            "coverage_municipality",
            "coverage_barangay",
            "created_by",
            "updated_by",
            "reviewed_by",
            "budget_approved_by",
            "executive_approved_by",
        ).prefetch_related(
            "communities",
            "supporting_organizations",
            "needs_addressed",
            "implementing_policies",
            "standard_outcome_indicators",
            "funding_flows",
            "workflow_stages",
            "updates",
        )

    def with_funding_totals(self):
        """Annotate with funding total calculations."""
        return self.annotate(
            total_allocations_sum=Sum(
                "funding_flows__amount",
                filter=Q(funding_flows__tranche_type="allocation"),
            ),
            total_obligations_sum=Sum(
                "funding_flows__amount",
                filter=Q(funding_flows__tranche_type="obligation"),
            ),
            total_disbursements_sum=Sum(
                "funding_flows__amount",
                filter=Q(funding_flows__tranche_type="disbursement"),
            ),
        )

    def active(self):
        """Filter to active entries (planning, ongoing)."""
        return self.filter(status__in=["planning", "ongoing"])

    def completed(self):
        """Filter to completed entries."""
        return self.filter(status="completed")

    def by_fiscal_year(self, year):
        """Filter by fiscal year."""
        return self.filter(fiscal_year=year)

    def by_plan_year(self, year):
        """Filter by planning year."""
        return self.filter(plan_year=year)

    def moa_ppas(self):
        """Filter to MOA PPAs."""
        return self.filter(category="moa_ppa")

    def oobc_ppas(self):
        """Filter to OOBC-led initiatives."""
        return self.filter(category="oobc_ppa")

    def obc_requests(self):
        """Filter to OBC community requests."""
        return self.filter(category="obc_request")

    def by_sector(self, sector):
        """Filter by sector."""
        return self.filter(sector=sector)

    def by_organization(self, org):
        """Filter by lead organization."""
        return self.filter(lead_organization=org)

    def high_priority(self):
        """Filter to high and urgent priority."""
        return self.filter(priority__in=["high", "urgent"])

    def over_budget(self):
        """Filter to entries with allocation variance."""
        return self.with_funding_totals().filter(
            total_allocations_sum__gt=F("budget_allocation")
        )

    def pending_approval(self):
        """Filter to entries pending approval."""
        return self.exclude(approval_status="approved")


class MonitoringEntryManager(models.Manager):
    """Custom manager for MonitoringEntry."""

    def get_queryset(self):
        return MonitoringEntryQuerySet(self.model, using=self._db)

    def with_related(self):
        return self.get_queryset().with_related()

    def with_funding_totals(self):
        return self.get_queryset().with_funding_totals()

    def active(self):
        return self.get_queryset().active()

    def completed(self):
        return self.get_queryset().completed()

    def by_fiscal_year(self, year):
        return self.get_queryset().by_fiscal_year(year)

    def by_plan_year(self, year):
        return self.get_queryset().by_plan_year(year)

    def moa_ppas(self):
        return self.get_queryset().moa_ppas()

    def oobc_ppas(self):
        return self.get_queryset().oobc_ppas()

    def obc_requests(self):
        return self.get_queryset().obc_requests()

    def by_sector(self, sector):
        return self.get_queryset().by_sector(sector)

    def by_organization(self, org):
        return self.get_queryset().by_organization(org)

    def high_priority(self):
        return self.get_queryset().high_priority()

    def over_budget(self):
        return self.get_queryset().over_budget()

    def pending_approval(self):
        return self.get_queryset().pending_approval()


class MonitoringEntry(models.Model):
    """Track M&E records covering PPAs and community requests."""

    CATEGORY_CHOICES = [
        ("moa_ppa", "MOA Project / Program / Activity"),
        ("oobc_ppa", "OOBC Project / Program / Activity"),
        ("obc_request", "OBC Request or Proposal"),
    ]

    APPROPRIATION_CLASS_PS = "ps"
    APPROPRIATION_CLASS_MOOE = "mooe"
    APPROPRIATION_CLASS_CO = "co"
    APPROPRIATION_CLASS_CHOICES = [
        (APPROPRIATION_CLASS_PS, "Personnel Services"),
        (APPROPRIATION_CLASS_MOOE, "Maintenance and Other Operating Expenses"),
        (APPROPRIATION_CLASS_CO, "Capital Outlay"),
    ]

    FUNDING_SOURCE_GAA = "gaa"
    FUNDING_SOURCE_BLOCK_GRANT = "block_grant"
    FUNDING_SOURCE_LGU = "lgu_counterpart"
    FUNDING_SOURCE_DONOR = "donor"
    FUNDING_SOURCE_INTERNAL = "internal"
    FUNDING_SOURCE_OTHERS = "others"
    FUNDING_SOURCE_CHOICES = [
        (FUNDING_SOURCE_GAA, "General Appropriations Act"),
        (FUNDING_SOURCE_BLOCK_GRANT, "BARMM Block Grant"),
        (FUNDING_SOURCE_LGU, "LGU Counterpart"),
        (FUNDING_SOURCE_DONOR, "Donor / Development Partner"),
        (FUNDING_SOURCE_INTERNAL, "OOBC / BARMM Internal"),
        (FUNDING_SOURCE_OTHERS, "Others"),
    ]

    SECTOR_ECONOMIC = "economic"
    SECTOR_SOCIAL = "social"
    SECTOR_INFRASTRUCTURE = "infrastructure"
    SECTOR_ENVIRONMENT = "environment"
    SECTOR_GOVERNANCE = "governance"
    SECTOR_PEACE = "peace_security"
    SECTOR_CHOICES = [
        (SECTOR_ECONOMIC, "Economic Development"),
        (SECTOR_SOCIAL, "Social Development"),
        (SECTOR_INFRASTRUCTURE, "Infrastructure"),
        (SECTOR_ENVIRONMENT, "Environment & DRRM"),
        (SECTOR_GOVERNANCE, "Governance & Institution Building"),
        (SECTOR_PEACE, "Peace, Security & Reconciliation"),
    ]

    COST_EFFECTIVENESS_CHOICES = [
        ("very_high", "Very High"),
        ("high", "High"),
        ("moderate", "Moderate"),
        ("low", "Low"),
    ]

    STATUS_CHOICES = [
        ("planning", "Planning"),
        ("ongoing", "Ongoing"),
        ("completed", "Completed"),
        ("on_hold", "On Hold"),
        ("cancelled", "Cancelled"),
    ]

    REQUEST_STATUS_CHOICES = [
        ("submitted", "Submitted"),
        ("under_review", "Under Review"),
        ("clarification", "For Clarification"),
        ("endorsed", "Endorsed"),
        ("approved", "Approved"),
        ("in_progress", "In Implementation"),
        ("completed", "Completed"),
        ("deferred", "Deferred"),
        ("declined", "Declined"),
    ]

    PRIORITY_CHOICES = [
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
        ("urgent", "Urgent"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(
        max_length=255, help_text="Name of the project, activity, or request"
    )
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    summary = models.TextField(
        blank=True, help_text="Overview of objectives, beneficiaries, and scope"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="planning",
        help_text="Implementation status for PPAs",
    )
    request_status = models.CharField(
        max_length=20,
        choices=REQUEST_STATUS_CHOICES,
        blank=True,
        help_text="Lifecycle state applicable to community requests",
    )
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default="medium",
        help_text="Priority level for follow-ups and support",
    )
    progress = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Overall completion percentage",
    )
    lead_organization = models.ForeignKey(
        "coordination.Organization",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="monitoring_entries",
        help_text="Primary implementing or receiving organization",
    )
    supporting_organizations = models.ManyToManyField(
        "coordination.Organization",
        blank=True,
        related_name="supporting_monitoring_entries",
        help_text="Supporting partner organizations",
    )
    implementing_moa = models.ForeignKey(
        "coordination.Organization",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="implemented_monitoring_entries",
        verbose_name="Implementing MOA",
        help_text="Primary MOA implementing the project",
    )
    oobc_unit = models.CharField(
        max_length=255,
        blank=True,
        help_text="OOBC unit or team responsible for follow-through",
    )
    submitted_by_community = models.ForeignKey(
        "communities.OBCCommunity",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="submitted_monitoring_entries",
        help_text="Origin OBC community for requests or proposals",
    )
    communities = models.ManyToManyField(
        "communities.OBCCommunity",
        blank=True,
        related_name="monitoring_entries",
        help_text="Targeted or benefiting OBC communities",
    )
    submitted_to_organization = models.ForeignKey(
        "coordination.Organization",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="received_monitoring_requests",
        help_text="Receiving MOA or office for requests",
    )
    related_assessment = models.ForeignKey(
        "mana.Assessment",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="monitoring_entries",
        help_text="Linked OBC-MANA assessment, if any",
    )
    # related_event removed - Event model deleted
    # Use WorkItem with work_type='activity' for coordination activities
    # See: docs/refactor/WORKITEM_MIGRATION_COMPLETE.md
    related_policy = models.ForeignKey(
        "policy_tracking.PolicyRecommendation",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="monitoring_entries",
        help_text="Policy recommendation informing this entry (DEPRECATED: use implementing_policies instead)",
    )

    # ==========================================
    # PHASE 1 INTEGRATION: NEEDS & POLICY LINKAGE
    # (Added for evidence-based budgeting)
    # ==========================================

    # MANY-TO-MANY: Multiple needs can be addressed by one PPA
    needs_addressed = models.ManyToManyField(
        "mana.Need",
        blank=True,
        related_name="implementing_ppas",
        help_text="Community needs this PPA addresses",
    )

    # MANY-TO-MANY: One PPA can implement multiple policies
    implementing_policies = models.ManyToManyField(
        "policy_tracking.PolicyRecommendation",
        blank=True,
        related_name="implementing_ppas",
        help_text="Policy recommendations this PPA implements",
    )

    plan_year = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(2000), MaxValueValidator(2100)],
        help_text="Planning reference year (e.g., AIP year)",
    )
    fiscal_year = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(2000), MaxValueValidator(2100)],
        help_text="Fiscal year the budget is intended for",
    )
    sector = models.CharField(
        max_length=32,
        choices=SECTOR_CHOICES,
        blank=True,
        help_text="Primary sector alignment for the PPA",
    )
    appropriation_class = models.CharField(
        max_length=8,
        choices=APPROPRIATION_CLASS_CHOICES,
        blank=True,
        help_text="Appropriation class (PS/MOOE/CO)",
    )
    funding_source = models.CharField(
        max_length=32,
        choices=FUNDING_SOURCE_CHOICES,
        blank=True,
        help_text="Primary funding source",
    )
    funding_source_other = models.CharField(
        max_length=255,
        blank=True,
        help_text="Specify funding source when tagged as Others",
    )
    program_code = models.CharField(
        max_length=100,
        blank=True,
        help_text="DBM/BARMM program or objective code",
    )
    plan_reference = models.CharField(
        max_length=255,
        blank=True,
        help_text="Reference to PDP/PIP/AIP or local investment plan",
    )
    goal_alignment = models.JSONField(
        default=list,
        blank=True,
        help_text="List of strategic alignment tags (e.g., PDP, SDG, Moral Governance)",
    )
    moral_governance_pillar = models.CharField(
        max_length=100,
        blank=True,
        help_text="Key Moral Governance pillar supported",
    )
    compliance_gad = models.BooleanField(
        default=False,
        help_text="Flag if expenditure is tagged under GAD",
    )
    compliance_ccet = models.BooleanField(
        default=False,
        help_text="Flag if expenditure is tagged under Climate Change Expenditure",
    )
    benefits_indigenous_peoples = models.BooleanField(
        default=False,
        help_text="Flag if initiative primarily benefits Indigenous Peoples communities",
    )
    supports_peace_agenda = models.BooleanField(
        default=False,
        help_text="Flag if initiative supports peacebuilding or security agenda",
    )
    supports_sdg = models.BooleanField(
        default=False,
        help_text="Flag if initiative contributes to SDG tracking",
    )
    budget_ceiling = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Ceiling allocated for budgeting scenarios",
    )
    start_date = models.DateField(null=True, blank=True)
    target_end_date = models.DateField(null=True, blank=True)
    actual_end_date = models.DateField(null=True, blank=True)
    next_milestone_date = models.DateField(null=True, blank=True)
    milestone_dates = models.JSONField(
        default=list,
        blank=True,
        help_text=(
            "Structured milestone entries: "
            "[{"
            "date"
            ": "
            "2025-10-15"
            ", "
            "title"
            ": "
            "Technical hearing"
            ", "
            "status"
            ": "
            "upcoming"
            "}]"
        ),
    )
    budget_allocation = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Budget allocation supporting the activity",
    )
    budget_currency = models.CharField(
        max_length=10,
        default="PHP",
        help_text="Currency of the recorded budget",
    )
    budget_obc_allocation = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Portion of the budget allocated specifically for OBCs",
    )
    total_slots = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Total number of beneficiary slots",
    )
    obc_slots = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Number of slots reserved for OBCs",
    )
    cost_per_beneficiary = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Computed or reported cost per beneficiary",
    )
    cost_effectiveness_rating = models.CharField(
        max_length=12,
        choices=COST_EFFECTIVENESS_CHOICES,
        blank=True,
        help_text="Qualitative cost-effectiveness rating",
    )
    coverage_region = models.ForeignKey(
        "common.Region",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="monitoring_entries",
        help_text="Region covered by the PPA",
    )
    coverage_province = models.ForeignKey(
        "common.Province",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="monitoring_entries",
        help_text="Province covered by the PPA",
    )
    coverage_municipality = models.ForeignKey(
        "common.Municipality",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="monitoring_entries",
        help_text="Municipality covered by the PPA",
    )
    coverage_barangay = models.ForeignKey(
        "common.Barangay",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="monitoring_entries",
        help_text="Barangay covered by the PPA",
    )
    outcome_framework = models.JSONField(
        default=dict,
        blank=True,
        help_text="Structured outcome framework including outputs, outcomes, and impacts",
    )
    outcome_indicators = models.TextField(
        blank=True,
        help_text="Legacy narrative field for outcome indicators (to be migrated to outcome framework)",
    )
    standard_outcome_indicators = models.ManyToManyField(
        "monitoring.OutcomeIndicator",
        blank=True,
        related_name="monitoring_entries",
        help_text="Standard outcome indicators referenced by this entry",
    )
    accomplishments = models.TextField(
        blank=True, help_text="Documented accomplishments and outputs"
    )
    challenges = models.TextField(
        blank=True, help_text="Challenges, risks, and mitigation notes"
    )
    support_required = models.TextField(
        blank=True, help_text="Support requested from OOBC or partners"
    )
    follow_up_actions = models.TextField(
        blank=True, help_text="Immediate next steps and focal assignments"
    )
    obcs_benefited = models.TextField(
        blank=True,
        help_text="Narrative describing OBC groups that have benefited",
    )
    last_status_update = models.DateField(
        null=True,
        blank=True,
        help_text="Date of the most recent status update",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="created_monitoring_entries",
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="updated_monitoring_entries",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # ========== BUDGET APPROVAL WORKFLOW (Project Management Portal Integration) ==========
    APPROVAL_STATUS_DRAFT = "draft"
    APPROVAL_STATUS_TECHNICAL_REVIEW = "technical_review"
    APPROVAL_STATUS_BUDGET_REVIEW = "budget_review"
    APPROVAL_STATUS_STAKEHOLDER_CONSULTATION = "stakeholder_consultation"
    APPROVAL_STATUS_EXECUTIVE_APPROVAL = "executive_approval"
    APPROVAL_STATUS_APPROVED = "approved"
    APPROVAL_STATUS_ENACTED = "enacted"
    APPROVAL_STATUS_REJECTED = "rejected"

    APPROVAL_STATUS_CHOICES = [
        (APPROVAL_STATUS_DRAFT, "Draft"),
        (APPROVAL_STATUS_TECHNICAL_REVIEW, "Technical Review"),
        (APPROVAL_STATUS_BUDGET_REVIEW, "Budget Review"),
        (APPROVAL_STATUS_STAKEHOLDER_CONSULTATION, "Stakeholder Consultation"),
        (APPROVAL_STATUS_EXECUTIVE_APPROVAL, "Executive Approval"),
        (APPROVAL_STATUS_APPROVED, "Approved"),
        (APPROVAL_STATUS_ENACTED, "Enacted"),
        (APPROVAL_STATUS_REJECTED, "Rejected"),
    ]

    approval_status = models.CharField(
        max_length=30,
        choices=APPROVAL_STATUS_CHOICES,
        default=APPROVAL_STATUS_DRAFT,
        help_text="Current status in the budget approval workflow",
        db_index=True,
    )

    approval_history = models.JSONField(
        default=list,
        blank=True,
        help_text="Complete history of approval stages with timestamps, reviewers, and comments",
    )

    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="technically_reviewed_ppas",
        help_text="User who completed technical review",
    )

    budget_approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="budget_approved_ppas",
        help_text="User who approved the budget allocation",
    )

    executive_approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="executive_approved_ppas",
        help_text="Executive who gave final approval",
    )

    approval_notes = models.TextField(
        blank=True,
        help_text="General notes about the approval process",
    )

    rejection_reason = models.TextField(
        blank=True,
        help_text="Reason for rejection (if approval_status is 'rejected')",
    )

    # ========== WORKITEM INTEGRATION FIELDS ==========
    execution_project = models.OneToOneField(
        'common.WorkItem',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='ppa_source',
        help_text="Root WorkItem project for execution tracking",
    )

    enable_workitem_tracking = models.BooleanField(
        default=False,
        help_text="Enable WorkItem-based execution tracking for this PPA",
    )

    budget_distribution_policy = models.CharField(
        max_length=20,
        choices=[
            ('equal', 'Equal'),
            ('weighted', 'Weighted'),
            ('manual', 'Manual')
        ],
        blank=True,
        help_text="Policy for distributing budget across child work items",
    )

    auto_sync_progress = models.BooleanField(
        default=True,
        help_text="Automatically sync progress from execution project",
    )

    auto_sync_status = models.BooleanField(
        default=True,
        help_text="Automatically sync status from execution project",
    )

    # Custom manager
    objects = MonitoringEntryManager()

    class Meta:
        ordering = ["-updated_at", "-created_at"]
        verbose_name = "Monitoring Entry"
        verbose_name_plural = "Monitoring Entries"
        constraints = [
            models.CheckConstraint(
                condition=Q(progress__gte=0) & Q(progress__lte=100),
                name='monitoring_entry_valid_progress'
            ),
            models.CheckConstraint(
                condition=Q(target_end_date__gte=F('start_date')) | Q(start_date__isnull=True) | Q(target_end_date__isnull=True),
                name='monitoring_entry_valid_date_range'
            ),
        ]

    def __str__(self):
        return self.title

    def clean(self):
        """Validate business rules at model level."""
        super().clean()
        errors = {}

        # Validate funding_source_other required when funding_source=others
        if self.funding_source == self.FUNDING_SOURCE_OTHERS and not self.funding_source_other:
            errors['funding_source_other'] = 'Please specify the funding source when selecting "Others".'

        # Validate date ranges
        if self.start_date and self.target_end_date:
            if self.target_end_date < self.start_date:
                errors['target_end_date'] = 'Target end date must be after start date.'

        if self.start_date and self.actual_end_date:
            if self.actual_end_date < self.start_date:
                errors['actual_end_date'] = 'Actual end date cannot be before start date.'

        # Validate budget allocation <= budget ceiling (if ceiling is set)
        if self.budget_ceiling and self.budget_allocation:
            if self.budget_allocation > self.budget_ceiling:
                errors['budget_allocation'] = (
                    f'Budget allocation (₱{self.budget_allocation:,.2f}) '
                    f'cannot exceed ceiling (₱{self.budget_ceiling:,.2f}).'
                )

        # Validate OBC-specific allocations
        if self.budget_obc_allocation and self.budget_allocation:
            if self.budget_obc_allocation > self.budget_allocation:
                errors['budget_obc_allocation'] = 'OBC allocation cannot exceed total budget allocation.'

        if self.obc_slots and self.total_slots:
            if self.obc_slots > self.total_slots:
                errors['obc_slots'] = 'OBC slots cannot exceed total slots.'

        # Validate category-specific required fields
        if self.category == 'moa_ppa' and not self.implementing_moa:
            errors['implementing_moa'] = 'Implementing MOA is required for MOA PPA entries.'

        if self.category == 'obc_request':
            if not self.submitted_by_community:
                errors['submitted_by_community'] = 'Submitting community is required for OBC requests.'
            if not self.submitted_to_organization:
                errors['submitted_to_organization'] = 'Recipient organization is required for OBC requests.'

        if errors:
            raise ValidationError(errors)

    def funding_total(self, tranche_type: str) -> float:
        """Return total amount recorded for a funding tranche type."""

        return (
            self.funding_flows.filter(tranche_type=tranche_type)
            .aggregate(total=models.Sum("amount"))
            .get("total")
            or 0
        )

    @property
    def is_request(self) -> bool:
        """Convenience flag identifying OBC requests."""

        return self.category == "obc_request"

    @property
    def total_allocations(self) -> Decimal:
        """Total allocation tranches recorded."""
        return Decimal(
            str(self.funding_total(MonitoringEntryFunding.TRANCHE_ALLOCATION))
        )

    @property
    def total_obligations(self) -> Decimal:
        """Total obligation tranches recorded."""
        return Decimal(
            str(self.funding_total(MonitoringEntryFunding.TRANCHE_OBLIGATION))
        )

    @property
    def total_disbursements(self) -> Decimal:
        """Total disbursement tranches recorded."""
        return Decimal(
            str(self.funding_total(MonitoringEntryFunding.TRANCHE_DISBURSEMENT))
        )

    @property
    def allocation_variance(self) -> Decimal:
        """Variance between budget allocation and recorded allocation tranches."""
        budget = self.budget_allocation or ZERO_DECIMAL
        actual = self.total_allocations
        return actual - budget

    @property
    def allocation_variance_pct(self) -> float:
        """Percentage variance for allocations."""
        budget = self.budget_allocation or ZERO_DECIMAL
        if budget == 0:
            return 0.0
        variance = self.allocation_variance
        return float((variance / budget) * 100)

    @property
    def obligation_rate(self) -> float:
        """Obligation rate as percentage of allocations."""
        allocations = self.total_allocations
        if allocations == 0:
            return 0.0
        obligations = self.total_obligations
        return float((obligations / allocations) * 100)

    @property
    def disbursement_rate(self) -> float:
        """Disbursement rate as percentage of obligations."""
        obligations = self.total_obligations
        if obligations == 0:
            return 0.0
        disbursements = self.total_disbursements
        return float((disbursements / obligations) * 100)

    @property
    def budget_utilization_rate(self) -> float:
        """Overall budget utilization (disbursements vs budget allocation)."""
        budget = self.budget_allocation or ZERO_DECIMAL
        if budget == 0:
            return 0.0
        disbursements = self.total_disbursements
        return float((disbursements / budget) * 100)

    @property
    def is_over_budget(self) -> bool:
        """Flag if allocations exceed budget."""
        return self.allocation_variance > 0

    @property
    def is_under_obligated(self) -> bool:
        """Flag if obligation rate is below 75%."""
        return self.obligation_rate < 75.0

    @property
    def work_items(self):
        """
        QuerySet of all WorkItems in the execution project hierarchy.

        Returns all descendants of the execution_project (including the project itself).
        Used by BudgetDistributionService to distribute budget across work items.

        Returns:
            QuerySet: WorkItem queryset containing all items in hierarchy

        Example:
            >>> ppa.work_items.all()  # All work items
            >>> ppa.work_items.filter(work_type='task')  # Just tasks
        """
        from common.work_item_model import WorkItem

        if not self.execution_project:
            # Return empty queryset if no execution project exists
            return WorkItem.objects.none()

        # Return all descendants including the root project
        return self.execution_project.get_descendants(include_self=True)

    # ========== WORKITEM INTEGRATION METHODS ==========

    def create_execution_project(self, structure_template='activity', created_by=None):
        """
        Create root WorkItem project for execution tracking.

        This method creates a hierarchical WorkItem structure for tracking PPA execution.
        It integrates with the WorkItemGenerationService (to be created in Phase 2) to
        generate a structured breakdown of activities/tasks.

        Args:
            structure_template (str): Template structure type. Options:
                - 'activity': Create activities for each outcome/output
                - 'milestone': Create tasks for each milestone
                - 'budget': Create structure based on budget categories
                Default: 'activity'
            created_by (User): User creating the execution project. Defaults to system user.

        Returns:
            WorkItem: The root project WorkItem instance

        Raises:
            ValidationError: If execution project already exists or PPA lacks required data

        Example:
            >>> entry = MonitoringEntry.objects.get(id='some-uuid')
            >>> project = entry.create_execution_project(
            ...     structure_template='activity',
            ...     created_by=request.user
            ... )
            >>> print(f"Created project: {project.title}")
            >>> print(f"Child activities: {project.get_children().count()}")
        """
        from django.contrib.auth import get_user_model
        from common.work_item_model import WorkItem
        from django.contrib.contenttypes.models import ContentType

        # Validation: Check if execution project already exists
        ct = ContentType.objects.get_for_model(self.__class__)
        existing_projects = WorkItem.objects.filter(
            content_type=ct,
            object_id=self.id,
            work_type=WorkItem.WORK_TYPE_PROJECT,
            parent__isnull=True
        )

        if existing_projects.exists():
            raise ValidationError(
                f"Execution project already exists for {self.title}. "
                "Delete the existing project before creating a new one."
            )

        # Validation: Ensure PPA has required data
        if not self.title:
            raise ValidationError("MonitoringEntry must have a title to create execution project.")

        # Get or create system user
        if created_by is None:
            User = get_user_model()
            system_user, _ = User.objects.get_or_create(
                username='system',
                defaults={
                    'first_name': 'System',
                    'last_name': 'User',
                    'is_active': False
                }
            )
            created_by = system_user

        # Create root project WorkItem
        project = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_PROJECT,
            title=f"{self.title} - Execution Plan",
            description=f"Execution tracking for {self.get_category_display()}: {self.title}",
            status=self._map_monitoring_status_to_workitem(),
            priority=self._map_monitoring_priority_to_workitem(),
            start_date=self.start_date,
            due_date=self.target_end_date,
            progress=self.progress,
            created_by=created_by,
            auto_calculate_progress=True,
            is_calendar_visible=True,
            related_ppa=self,
            allocated_budget=self.budget_allocation,
            actual_expenditure=Decimal('0.00'),
            project_data={
                'monitoring_entry_id': str(self.id),
                'structure_template': structure_template,
                'budget_allocation': str(self.budget_allocation) if self.budget_allocation else None,
                'fiscal_year': self.fiscal_year,
            }
        )

        # Link to MonitoringEntry via Generic Foreign Key
        project.content_type = ct
        project.object_id = self.id
        project.save()

        # Phase 2: Call WorkItemGenerationService to generate child structure
        # This will be implemented in Phase 2
        # from common.services.workitem_generation import WorkItemGenerationService
        # service = WorkItemGenerationService(project, self)
        # service.generate_structure(template=structure_template)

        return project

    def _map_monitoring_status_to_workitem(self):
        """Map MonitoringEntry status to WorkItem status."""
        from common.work_item_model import WorkItem

        status_mapping = {
            'planning': WorkItem.STATUS_NOT_STARTED,
            'ongoing': WorkItem.STATUS_IN_PROGRESS,
            'completed': WorkItem.STATUS_COMPLETED,
            'on_hold': WorkItem.STATUS_BLOCKED,
            'cancelled': WorkItem.STATUS_CANCELLED,
        }
        return status_mapping.get(self.status, WorkItem.STATUS_NOT_STARTED)

    def _map_monitoring_priority_to_workitem(self):
        """Map MonitoringEntry priority to WorkItem priority."""
        from common.work_item_model import WorkItem

        priority_mapping = {
            'low': WorkItem.PRIORITY_LOW,
            'medium': WorkItem.PRIORITY_MEDIUM,
            'high': WorkItem.PRIORITY_HIGH,
            'urgent': WorkItem.PRIORITY_URGENT,
        }
        return priority_mapping.get(self.priority, WorkItem.PRIORITY_MEDIUM)

    def sync_progress_from_workitem(self):
        """
        Calculate progress from execution_project descendants and update self.progress.

        This method syncs the MonitoringEntry progress with the completion status of
        its associated WorkItem execution project. Progress is calculated based on
        completed descendants (activities/tasks).

        Returns:
            int: Calculated progress percentage (0-100)

        Example:
            >>> entry = MonitoringEntry.objects.get(id='some-uuid')
            >>> calculated_progress = entry.sync_progress_from_workitem()
            >>> print(f"Progress updated: {calculated_progress}%")
            >>> entry.refresh_from_db()
            >>> assert entry.progress == calculated_progress
        """
        from common.work_item_model import WorkItem
        from django.contrib.contenttypes.models import ContentType

        # Find execution project
        try:
            ct = ContentType.objects.get_for_model(self.__class__)
            execution_project = WorkItem.objects.get(
                content_type=ct,
                object_id=self.id,
                work_type=WorkItem.WORK_TYPE_PROJECT,
                parent__isnull=True  # Root project only
            )
        except WorkItem.DoesNotExist:
            # No execution project exists, return current progress
            return self.progress
        except WorkItem.MultipleObjectsReturned:
            # Multiple projects found, use the latest
            ct = ContentType.objects.get_for_model(self.__class__)
            execution_project = WorkItem.objects.filter(
                content_type=ct,
                object_id=self.id,
                work_type=WorkItem.WORK_TYPE_PROJECT,
                parent__isnull=True
            ).latest('created_at')

        # Calculate progress from descendants
        descendants = execution_project.get_descendants()
        if not descendants.exists():
            # No children, use project's own progress
            calculated_progress = execution_project.progress
        else:
            # Calculate based on completed descendants
            total_descendants = descendants.count()
            completed_descendants = descendants.filter(
                status=WorkItem.STATUS_COMPLETED
            ).count()

            if total_descendants > 0:
                calculated_progress = int((completed_descendants / total_descendants) * 100)
            else:
                calculated_progress = 0

        # Update MonitoringEntry progress
        if self.progress != calculated_progress:
            self.progress = calculated_progress
            self.save(update_fields=['progress', 'updated_at'])

        return calculated_progress

    def sync_status_from_workitem(self):
        """
        Map WorkItem status to MonitoringEntry status and update self.status.

        This method syncs the MonitoringEntry status with the status of its
        associated WorkItem execution project.

        Returns:
            str: Updated status value

        Example:
            >>> entry = MonitoringEntry.objects.get(id='some-uuid')
            >>> updated_status = entry.sync_status_from_workitem()
            >>> print(f"Status updated: {updated_status}")
            >>> entry.refresh_from_db()
            >>> assert entry.status == updated_status
        """
        from common.work_item_model import WorkItem
        from django.contrib.contenttypes.models import ContentType

        # Find execution project
        try:
            ct = ContentType.objects.get_for_model(self.__class__)
            execution_project = WorkItem.objects.get(
                content_type=ct,
                object_id=self.id,
                work_type=WorkItem.WORK_TYPE_PROJECT,
                parent__isnull=True
            )
        except WorkItem.DoesNotExist:
            # No execution project exists, return current status
            return self.status
        except WorkItem.MultipleObjectsReturned:
            # Multiple projects found, use the latest
            ct = ContentType.objects.get_for_model(self.__class__)
            execution_project = WorkItem.objects.filter(
                content_type=ct,
                object_id=self.id,
                work_type=WorkItem.WORK_TYPE_PROJECT,
                parent__isnull=True
            ).latest('created_at')

        # Map WorkItem status to MonitoringEntry status
        workitem_status = execution_project.status
        status_mapping = {
            WorkItem.STATUS_NOT_STARTED: 'planning',
            WorkItem.STATUS_IN_PROGRESS: 'ongoing',
            WorkItem.STATUS_AT_RISK: 'ongoing',  # Keep as ongoing but flag risk
            WorkItem.STATUS_BLOCKED: 'on_hold',
            WorkItem.STATUS_COMPLETED: 'completed',
            WorkItem.STATUS_CANCELLED: 'cancelled',
        }

        mapped_status = status_mapping.get(workitem_status, self.status)

        # Update MonitoringEntry status
        if self.status != mapped_status:
            self.status = mapped_status
            self.save(update_fields=['status', 'updated_at'])

        return mapped_status

    def get_budget_allocation_tree(self):
        """
        Return hierarchical budget breakdown as dict.

        This method returns a nested dictionary representing the budget allocation
        across the WorkItem hierarchy, including allocated budgets and actual
        expenditures per work item with variance calculations.

        Returns:
            dict: Hierarchical budget breakdown with structure:
                {
                    'work_item_id': str,
                    'title': str,
                    'work_type': str,
                    'allocated_budget': Decimal,
                    'actual_expenditure': Decimal,
                    'variance': Decimal,
                    'variance_pct': float,
                    'children': [...]  # Recursive children
                }

        Example:
            >>> entry = MonitoringEntry.objects.get(id='some-uuid')
            >>> budget_tree = entry.get_budget_allocation_tree()
            >>> print(f"Root budget: ₱{budget_tree['allocated_budget']:,.2f}")
            >>> for child in budget_tree['children']:
            ...     print(f"  {child['title']}: ₱{child['allocated_budget']:,.2f}")
        """
        from common.work_item_model import WorkItem
        from django.contrib.contenttypes.models import ContentType

        # Find execution project
        try:
            ct = ContentType.objects.get_for_model(self.__class__)
            execution_project = WorkItem.objects.get(
                content_type=ct,
                object_id=self.id,
                work_type=WorkItem.WORK_TYPE_PROJECT,
                parent__isnull=True
            )
        except WorkItem.DoesNotExist:
            # No execution project exists, return basic structure
            return {
                'work_item_id': None,
                'title': self.title,
                'work_type': 'monitoring_entry',
                'allocated_budget': self.budget_allocation or Decimal('0.00'),
                'actual_expenditure': self.total_disbursements,
                'variance': (self.total_disbursements - (self.budget_allocation or Decimal('0.00'))),
                'variance_pct': self._calculate_variance_pct(
                    self.budget_allocation or Decimal('0.00'),
                    self.total_disbursements
                ),
                'children': []
            }
        except WorkItem.MultipleObjectsReturned:
            ct = ContentType.objects.get_for_model(self.__class__)
            execution_project = WorkItem.objects.filter(
                content_type=ct,
                object_id=self.id,
                work_type=WorkItem.WORK_TYPE_PROJECT,
                parent__isnull=True
            ).latest('created_at')

        # Build hierarchical tree recursively
        def build_tree(work_item):
            """Recursively build budget tree for a work item."""
            allocated = work_item.allocated_budget or Decimal('0.00')
            actual = work_item.actual_expenditure or Decimal('0.00')
            variance = actual - allocated
            variance_pct = self._calculate_variance_pct(allocated, actual)

            node = {
                'work_item_id': str(work_item.id),
                'title': work_item.title,
                'work_type': work_item.work_type,
                'work_type_display': work_item.get_work_type_display(),
                'allocated_budget': allocated,
                'actual_expenditure': actual,
                'variance': variance,
                'variance_pct': variance_pct,
                'status': work_item.status,
                'progress': work_item.progress,
                'children': []
            }

            # Recursively add children
            children = work_item.get_children()
            for child in children:
                node['children'].append(build_tree(child))

            return node

        return build_tree(execution_project)

    def _calculate_variance_pct(self, allocated, actual):
        """Calculate variance percentage."""
        if allocated == 0:
            return 0.0
        variance = actual - allocated
        return float((variance / allocated) * 100)

    def validate_budget_distribution(self):
        """
        Validate sum of child budgets equals PPA budget.

        This method ensures budget consistency across the WorkItem hierarchy by
        validating that the sum of allocated budgets in child work items matches
        the MonitoringEntry's budget_allocation.

        Returns:
            bool: True if budget distribution is valid

        Raises:
            ValidationError: If sum of child budgets doesn't match PPA budget

        Example:
            >>> entry = MonitoringEntry.objects.get(id='some-uuid')
            >>> try:
            ...     entry.validate_budget_distribution()
            ...     print("Budget distribution is valid")
            ... except ValidationError as e:
            ...     print(f"Validation failed: {e.message}")
        """
        from common.work_item_model import WorkItem
        from django.contrib.contenttypes.models import ContentType

        # Find execution project
        try:
            ct = ContentType.objects.get_for_model(self.__class__)
            execution_project = WorkItem.objects.get(
                content_type=ct,
                object_id=self.id,
                work_type=WorkItem.WORK_TYPE_PROJECT,
                parent__isnull=True
            )
        except WorkItem.DoesNotExist:
            # No execution project exists, validation passes
            return True
        except WorkItem.MultipleObjectsReturned:
            ct = ContentType.objects.get_for_model(self.__class__)
            execution_project = WorkItem.objects.filter(
                content_type=ct,
                object_id=self.id,
                work_type=WorkItem.WORK_TYPE_PROJECT,
                parent__isnull=True
            ).latest('created_at')

        # Get PPA budget allocation
        ppa_budget = self.budget_allocation or Decimal('0.00')

        # Calculate sum of child budgets (immediate children only)
        children = execution_project.get_children()
        if not children.exists():
            # No children, validation passes
            return True

        # Sum allocated budgets from children
        child_budget_sum = Decimal('0.00')
        for child in children:
            allocated = child.allocated_budget or Decimal('0.00')
            child_budget_sum += allocated

        # Tolerance for decimal comparison (0.01 = 1 cent)
        tolerance = Decimal('0.01')
        difference = abs(ppa_budget - child_budget_sum)

        if difference > tolerance:
            raise ValidationError(
                f"Budget distribution mismatch: PPA budget is ₱{ppa_budget:,.2f}, "
                f"but sum of child budgets is ₱{child_budget_sum:,.2f}. "
                f"Difference: ₱{difference:,.2f}. "
                f"Please adjust child budget allocations to match the total PPA budget."
            )

        return True


class OutcomeIndicator(models.Model):
    """Catalogue of standard outcome indicators for PPAs."""

    CATEGORY_CHOICES = [
        ("education", "Education"),
        ("health", "Health"),
        ("livelihood", "Livelihood"),
        ("governance", "Governance"),
        ("infrastructure", "Infrastructure"),
        ("social_protection", "Social Protection"),
        ("environment", "Environment"),
        ("peace_security", "Peace & Security"),
        ("other", "Other"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category = models.CharField(
        max_length=64,
        choices=CATEGORY_CHOICES,
        help_text="Domain classification for the indicator",
    )
    indicator_name = models.CharField(
        max_length=255,
        help_text="Name of the indicator",
    )
    definition = models.TextField(
        help_text="How the indicator is defined and interpreted",
    )
    measurement_method = models.TextField(
        blank=True,
        help_text="Methodology for measuring the indicator",
    )
    data_source = models.CharField(
        max_length=255,
        blank=True,
        help_text="Primary data source (e.g., survey, administrative records)",
    )
    frequency = models.CharField(
        max_length=100,
        blank=True,
        help_text="Collection frequency (e.g., quarterly, annual)",
    )
    unit_of_measure = models.CharField(
        max_length=50,
        blank=True,
        help_text="Unit of measure (e.g., percent, households)",
    )
    related_sdg = models.CharField(
        max_length=50,
        blank=True,
        help_text="Optional SDG reference",
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether the indicator is available for selection",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["category", "indicator_name"]
        indexes = [
            models.Index(fields=["category", "is_active"]),
            models.Index(fields=["indicator_name"]),
        ]

    def __str__(self):
        return f"{self.indicator_name}"


class MonitoringEntryFunding(models.Model):
    """Track detailed allocations, obligations, and disbursements per entry."""

    TRANCHE_ALLOCATION = "allocation"
    TRANCHE_OBLIGATION = "obligation"
    TRANCHE_DISBURSEMENT = "disbursement"
    TRANCHE_ADJUSTMENT = "adjustment"
    TRANCHE_CHOICES = [
        (TRANCHE_ALLOCATION, "Allocation"),
        (TRANCHE_OBLIGATION, "Obligation"),
        (TRANCHE_DISBURSEMENT, "Disbursement"),
        (TRANCHE_ADJUSTMENT, "Adjustment"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    entry = models.ForeignKey(
        MonitoringEntry,
        related_name="funding_flows",
        on_delete=models.CASCADE,
    )
    tranche_type = models.CharField(max_length=20, choices=TRANCHE_CHOICES)
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    funding_source = models.CharField(
        max_length=32,
        choices=MonitoringEntry.FUNDING_SOURCE_CHOICES,
        blank=True,
        help_text="Override funding source for this tranche",
    )
    funding_source_other = models.CharField(
        max_length=255,
        blank=True,
        help_text="Specify the funding source when using Others",
    )
    scheduled_date = models.DateField(
        null=True,
        blank=True,
        help_text="When the tranche is scheduled or recorded",
    )
    remarks = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="created_funding_flows",
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="updated_funding_flows",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-scheduled_date", "-created_at"]
        verbose_name = "Funding Flow"
        verbose_name_plural = "Funding Flows"

    def __str__(self):
        return f"{self.get_tranche_type_display()} - {self.amount}"


class MonitoringEntryWorkflowStage(models.Model):
    """Represent budget workflow milestones per monitoring entry."""

    STAGE_BUDGET_CALL = "budget_call"
    STAGE_FORMULATION = "formulation"
    STAGE_TECHNICAL = "technical_hearing"
    STAGE_LEGISLATION = "legislation"
    STAGE_EXECUTION = "execution"
    STAGE_ACCOUNTABILITY = "accountability"
    STAGE_CHOICES = [
        (STAGE_BUDGET_CALL, "Budget Call"),
        (STAGE_FORMULATION, "Formulation"),
        (STAGE_TECHNICAL, "Technical Budget Hearing"),
        (STAGE_LEGISLATION, "Budget Legislation"),
        (STAGE_EXECUTION, "Program Execution"),
        (STAGE_ACCOUNTABILITY, "Accountability"),
    ]

    STATUS_NOT_STARTED = "not_started"
    STATUS_IN_PROGRESS = "in_progress"
    STATUS_COMPLETED = "completed"
    STATUS_BLOCKED = "blocked"
    STATUS_CHOICES = [
        (STATUS_NOT_STARTED, "Not Started"),
        (STATUS_IN_PROGRESS, "In Progress"),
        (STATUS_COMPLETED, "Completed"),
        (STATUS_BLOCKED, "Blocked"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    entry = models.ForeignKey(
        MonitoringEntry,
        related_name="workflow_stages",
        on_delete=models.CASCADE,
    )
    stage = models.CharField(max_length=40, choices=STAGE_CHOICES)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_NOT_STARTED,
    )
    owner_team = models.ForeignKey(
        "common.StaffTeam",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="budget_workflow_stages",
    )
    owner_organization = models.ForeignKey(
        "coordination.Organization",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="budget_workflow_stages",
    )
    due_date = models.DateField(null=True, blank=True)
    completed_at = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    last_updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="updated_budget_workflow_stages",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("entry", "stage")
        ordering = ["entry", "stage"]
        verbose_name = "Budget Workflow Stage"
        verbose_name_plural = "Budget Workflow Stages"

    def __str__(self):
        return f"{self.entry.title} - {self.get_stage_display()}"


class MonitoringUpdate(models.Model):
    """Log granular progress updates for a monitoring entry."""

    UPDATE_TYPES = [
        ("status", "Status Update"),
        ("progress", "Progress Update"),
        ("milestone", "Milestone"),
        ("communication", "Communication"),
        ("note", "General Note"),
    ]

    entry = models.ForeignKey(
        MonitoringEntry,
        on_delete=models.CASCADE,
        related_name="updates",
        help_text="Parent monitoring entry",
    )
    update_type = models.CharField(max_length=20, choices=UPDATE_TYPES, default="note")
    status = models.CharField(
        max_length=20,
        choices=MonitoringEntry.STATUS_CHOICES,
        blank=True,
        help_text="Updated PPA implementation status",
    )
    request_status = models.CharField(
        max_length=20,
        choices=MonitoringEntry.REQUEST_STATUS_CHOICES,
        blank=True,
        help_text="Updated request lifecycle state",
    )
    progress = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="New completion percentage",
    )
    notes = models.TextField(help_text="Narrative update or decisions recorded")
    next_steps = models.TextField(
        blank=True,
        help_text="Follow-up actions to undertake after this update",
    )
    follow_up_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date for the next follow-up or coordination",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="monitoring_updates",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Monitoring Update"
        verbose_name_plural = "Monitoring Updates"

    def __str__(self):
        return f"Update for {self.entry.title} ({self.get_update_type_display()})"


class MonitoringEntryWorkflowDocument(models.Model):
    """Store documents and attachments for budget workflow stages."""

    DOCUMENT_TYPE_BUDGET_CALL = "budget_call"
    DOCUMENT_TYPE_SUBMISSION = "submission"
    DOCUMENT_TYPE_HEARING_NOTES = "hearing_notes"
    DOCUMENT_TYPE_APPROVAL = "approval"
    DOCUMENT_TYPE_AIP_FORM = "aip_form"
    DOCUMENT_TYPE_SUPPORTING = "supporting"
    DOCUMENT_TYPE_OTHER = "other"
    DOCUMENT_TYPE_CHOICES = [
        (DOCUMENT_TYPE_BUDGET_CALL, "Budget Call Memorandum"),
        (DOCUMENT_TYPE_SUBMISSION, "Submission Form"),
        (DOCUMENT_TYPE_HEARING_NOTES, "Technical Hearing Notes"),
        (DOCUMENT_TYPE_APPROVAL, "Approval Letter"),
        (DOCUMENT_TYPE_AIP_FORM, "AIP Form / Template"),
        (DOCUMENT_TYPE_SUPPORTING, "Supporting Document"),
        (DOCUMENT_TYPE_OTHER, "Other"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workflow_stage = models.ForeignKey(
        MonitoringEntryWorkflowStage,
        related_name="documents",
        on_delete=models.CASCADE,
        help_text="Parent workflow stage",
    )
    title = models.CharField(
        max_length=255,
        help_text="Document title or description",
    )
    document_type = models.CharField(
        max_length=32,
        choices=DOCUMENT_TYPE_CHOICES,
        default=DOCUMENT_TYPE_SUPPORTING,
        help_text="Type of document for categorization",
    )
    file = models.FileField(
        upload_to="monitoring/workflow_documents/%Y/%m/",
        help_text="Upload document file (PDF, Word, Excel, etc.)",
    )
    file_size = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="File size in bytes (auto-populated)",
    )
    description = models.TextField(
        blank=True,
        help_text="Additional notes or context for this document",
    )
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="uploaded_workflow_documents",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Workflow Document"
        verbose_name_plural = "Workflow Documents"

    def __str__(self):
        return f"{self.title} ({self.get_document_type_display()})"

    def save(self, *args, **kwargs):
        """Auto-populate file size before saving."""
        if self.file and hasattr(self.file, "size"):
            self.file_size = self.file.size
        super().save(*args, **kwargs)


# Import strategic planning models
from .strategic_models import StrategicGoal, AnnualPlanningCycle

# Import scenario planning models
from .scenario_models import BudgetScenario, ScenarioAllocation, CeilingManagement

# NOTE: MonitoringEntry is registered with auditlog in common/auditlog_config.py
# This provides centralized audit trail configuration for compliance tracking

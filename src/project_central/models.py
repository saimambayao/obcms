"""
Project Management Portal Models

Core models for the integrated project management system.
"""

import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from django.urls import reverse

User = get_user_model()


class BudgetApprovalStage(models.Model):
    """
    Tracks budget approval workflow for PPAs through multiple approval stages.

    Each PPA must go through several approval stages before budget is enacted.
    This model tracks the status of each stage and captures approval history.
    """

    STAGE_CHOICES = [
        ("draft", "Draft"),
        ("technical_review", "Technical Review"),
        ("budget_review", "Budget Review"),
        ("executive_approval", "Executive Approval"),
        ("enacted", "Enacted"),
    ]

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
        ("returned", "Returned for Revision"),
    ]

    # Identifiers
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Related PPA
    ppa = models.ForeignKey(
        "monitoring.MonitoringEntry",
        on_delete=models.CASCADE,
        related_name="approval_stages",
        help_text="PPA being approved",
    )

    # Stage and Status
    stage = models.CharField(
        max_length=30, choices=STAGE_CHOICES, help_text="Approval stage"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
        help_text="Current status of this approval stage",
    )

    # Approval Details
    approver = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="budget_approvals",
        help_text="User who approved/rejected this stage",
    )

    approved_at = models.DateTimeField(
        null=True, blank=True, help_text="When this stage was approved/rejected"
    )

    comments = models.TextField(blank=True, help_text="Reviewer comments and feedback")

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Budget Approval Stage"
        verbose_name_plural = "Budget Approval Stages"
        ordering = ["created_at"]
        unique_together = [["ppa", "stage"]]
        indexes = [
            models.Index(fields=["ppa", "stage"]),
            models.Index(fields=["status", "stage"]),
            models.Index(fields=["approver", "approved_at"]),
        ]

    def __str__(self):
        return f"{self.ppa.title} - {self.get_stage_display()} ({self.get_status_display()})"

    def approve(self, user, comments=""):
        """Mark this stage as approved."""
        self.status = "approved"
        self.approver = user
        self.approved_at = timezone.now()
        if comments:
            self.comments = comments
        self.save()

    def reject(self, user, comments):
        """Mark this stage as rejected."""
        self.status = "rejected"
        self.approver = user
        self.approved_at = timezone.now()
        self.comments = comments
        self.save()

    def return_for_revision(self, user, comments):
        """Return this stage for revision."""
        self.status = "returned"
        self.approver = user
        self.approved_at = timezone.now()
        self.comments = comments
        self.save()


class BudgetCeiling(models.Model):
    """
    Tracks budget ceilings by sector, funding source, and fiscal year.

    Budget ceilings enforce spending limits to ensure fiscal discipline
    and prevent over-allocation of resources.
    """

    SECTOR_CHOICES = [
        ("economic", "Economic Development"),
        ("social", "Social Development"),
        ("infrastructure", "Infrastructure"),
        ("education", "Education"),
        ("health", "Health"),
        ("environment", "Environment & Natural Resources"),
        ("governance", "Governance & Institutions"),
        ("peace", "Peace & Security"),
        ("cultural", "Cultural Development"),
    ]

    FUNDING_SOURCE_CHOICES = [
        ("gaa", "General Appropriations Act (GAA)"),
        ("block_grant", "Block Grant"),
        ("lgu", "Local Government Unit"),
        ("donor", "Donor Funding"),
        ("internal", "Internal Revenue"),
        ("others", "Others"),
    ]

    # Identifiers
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(
        max_length=200, help_text="Descriptive name for this budget ceiling"
    )

    # Scope
    fiscal_year = models.IntegerField(help_text="Fiscal year this ceiling applies to")

    sector = models.CharField(
        max_length=20,
        choices=SECTOR_CHOICES,
        null=True,
        blank=True,
        help_text="Sector this ceiling applies to (null = all sectors)",
    )

    funding_source = models.CharField(
        max_length=20,
        choices=FUNDING_SOURCE_CHOICES,
        null=True,
        blank=True,
        help_text="Funding source this ceiling applies to (null = all sources)",
    )

    # Budget Ceiling
    ceiling_amount = models.DecimalField(
        max_digits=12, decimal_places=2, help_text="Maximum budget allocation allowed"
    )

    allocated_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text="Total amount currently allocated (auto-calculated)",
    )

    # Status
    is_active = models.BooleanField(
        default=True, help_text="Whether this ceiling is currently enforced"
    )

    enforcement_level = models.CharField(
        max_length=10,
        choices=[
            ("soft", "Soft Limit (Warning)"),
            ("hard", "Hard Limit (Rejection)"),
        ],
        default="hard",
        help_text="Whether to warn or reject allocations exceeding ceiling",
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_budget_ceilings",
    )

    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = "Budget Ceiling"
        verbose_name_plural = "Budget Ceilings"
        ordering = ["-fiscal_year", "sector", "funding_source"]
        unique_together = [["fiscal_year", "sector", "funding_source"]]
        indexes = [
            models.Index(fields=["fiscal_year", "is_active"]),
            models.Index(fields=["sector", "fiscal_year"]),
            models.Index(fields=["funding_source", "fiscal_year"]),
        ]

    def __str__(self):
        parts = [f"FY {self.fiscal_year}"]
        if self.sector:
            parts.append(self.get_sector_display())
        if self.funding_source:
            parts.append(self.get_funding_source_display())
        parts.append(f"₱{self.ceiling_amount:,.2f}")
        return " - ".join(parts)

    def get_utilization_percentage(self):
        """Calculate percentage of ceiling currently allocated."""
        if self.ceiling_amount == 0:
            return 0
        return (self.allocated_amount / self.ceiling_amount) * 100

    def get_remaining_amount(self):
        """Calculate remaining budget available under this ceiling."""
        return max(0, self.ceiling_amount - self.allocated_amount)

    def is_near_limit(self, threshold=90):
        """Check if allocation is near the ceiling (default: 90%)."""
        return self.get_utilization_percentage() >= threshold

    def is_exceeded(self):
        """Check if allocation has exceeded the ceiling."""
        return self.allocated_amount > self.ceiling_amount

    def can_allocate(self, amount):
        """
        Check if a given amount can be allocated under this ceiling.

        Returns:
            tuple: (bool, str) - (can_allocate, reason_if_cannot)
        """
        if not self.is_active:
            return True, "Ceiling is not active"

        if self.allocated_amount + amount <= self.ceiling_amount:
            return True, ""

        if self.enforcement_level == "soft":
            return (
                True,
                f"Warning: Allocation would exceed ceiling by ₱{(self.allocated_amount + amount - self.ceiling_amount):,.2f}",
            )

        return (
            False,
            f"Cannot allocate ₱{amount:,.2f}. Would exceed ceiling by ₱{(self.allocated_amount + amount - self.ceiling_amount):,.2f}",
        )

    def update_allocated_amount(self):
        """Recalculate allocated amount from all relevant PPAs."""
        from monitoring.models import MonitoringEntry

        # Build filter conditions
        filters = {"fiscal_year": self.fiscal_year}

        if self.sector:
            filters["sector"] = self.sector

        if self.funding_source:
            filters["funding_source"] = self.funding_source

        # Calculate total allocation
        total = (
            MonitoringEntry.objects.filter(**filters).aggregate(
                total=models.Sum("budget_allocation")
            )["total"]
            or 0
        )

        self.allocated_amount = total
        self.save(update_fields=["allocated_amount", "updated_at"])

        return self.allocated_amount


class BudgetScenario(models.Model):
    """
    Budget scenario planning model for exploring different allocation strategies.

    Enables "what-if" analysis by creating alternative budget allocation scenarios
    that can be compared before finalizing the annual budget.
    """

    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("under_review", "Under Review"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
        ("archived", "Archived"),
    ]

    # Identifiers
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(
        max_length=200, help_text="Descriptive name for this scenario"
    )

    description = models.TextField(
        help_text="Detailed description of scenario assumptions and goals"
    )

    # Scope
    fiscal_year = models.IntegerField(help_text="Fiscal year this scenario applies to")

    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")

    is_baseline = models.BooleanField(
        default=False,
        help_text="Whether this is the baseline scenario (reality/status quo)",
    )

    # Budget Envelope
    total_budget_envelope = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Total budget available in this scenario",
    )

    # Scenario Data (stored as JSON for flexibility)
    allocation_by_sector = models.JSONField(
        default=dict, help_text="Budget allocation breakdown by sector"
    )

    allocation_by_source = models.JSONField(
        default=dict, help_text="Budget allocation breakdown by funding source"
    )

    allocation_by_region = models.JSONField(
        default=dict, help_text="Budget allocation breakdown by region"
    )

    key_assumptions = models.JSONField(
        default=list, help_text="List of key assumptions underlying this scenario"
    )

    expected_outcomes = models.JSONField(
        default=list, help_text="Expected outcomes if this scenario is implemented"
    )

    # Analysis
    strengths = models.TextField(blank=True, help_text="Strengths of this scenario")
    weaknesses = models.TextField(blank=True, help_text="Weaknesses of this scenario")
    opportunities = models.TextField(
        blank=True, help_text="Opportunities this scenario enables"
    )
    threats = models.TextField(blank=True, help_text="Threats/risks in this scenario")

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_project_scenarios",
    )

    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_scenarios",
    )

    approved_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Budget Scenario"
        verbose_name_plural = "Budget Scenarios"
        ordering = ["-fiscal_year", "-created_at"]
        indexes = [
            models.Index(fields=["fiscal_year", "status"]),
            models.Index(fields=["is_baseline", "fiscal_year"]),
        ]

    def __str__(self):
        return f"{self.name} (FY {self.fiscal_year}) - {self.get_status_display()}"

    def get_total_allocated(self):
        """Calculate total amount allocated across all sectors."""
        return sum(self.allocation_by_sector.values())

    def get_allocation_percentage_by_sector(self):
        """Get allocation percentages by sector."""
        total = self.get_total_allocated()
        if total == 0:
            return {}

        return {
            sector: (amount / total) * 100
            for sector, amount in self.allocation_by_sector.items()
        }

    def compare_to_baseline(self):
        """
        Compare this scenario to the baseline scenario.

        Returns:
            dict: Comparison metrics showing differences from baseline
        """
        try:
            baseline = BudgetScenario.objects.get(
                fiscal_year=self.fiscal_year, is_baseline=True
            )
        except BudgetScenario.DoesNotExist:
            return {"error": "No baseline scenario found for this fiscal year"}

        if baseline.id == self.id:
            return {"is_baseline": True}

        # Calculate differences
        comparison = {
            "total_budget_diff": self.total_budget_envelope
            - baseline.total_budget_envelope,
            "total_budget_diff_pct": (
                (
                    (self.total_budget_envelope - baseline.total_budget_envelope)
                    / baseline.total_budget_envelope
                    * 100
                )
                if baseline.total_budget_envelope > 0
                else 0
            ),
            "sector_differences": {},
        }

        # Compare sector allocations
        all_sectors = set(
            list(self.allocation_by_sector.keys())
            + list(baseline.allocation_by_sector.keys())
        )
        for sector in all_sectors:
            this_amount = self.allocation_by_sector.get(sector, 0)
            baseline_amount = baseline.allocation_by_sector.get(sector, 0)
            diff = this_amount - baseline_amount
            diff_pct = (
                (diff / baseline_amount * 100)
                if baseline_amount > 0
                else (100 if this_amount > 0 else 0)
            )

            comparison["sector_differences"][sector] = {
                "amount_diff": diff,
                "percent_diff": diff_pct,
                "this_scenario": this_amount,
                "baseline": baseline_amount,
            }

        return comparison


class Alert(models.Model):
    """
    System-generated alerts for project management and budget monitoring.

    Alerts are automatically generated daily via Celery tasks and notify users
    of important events, issues, or required actions.
    """

    ALERT_TYPES = [
        ("unfunded_needs", "Unfunded High-Priority Needs"),
        ("overdue_ppa", "Overdue PPA"),
        ("pending_mao_report", "Pending MAO Quarterly Report"),
        ("budget_ceiling", "Budget Ceiling Alert"),
        ("policy_lagging", "Policy Implementation Lagging"),
        ("approval_bottleneck", "Budget Approval Bottleneck"),
        ("disbursement_delay", "Disbursement Delay"),
        ("underspending", "Underspending Alert"),
        ("overspending", "Overspending Warning"),
        ("workflow_blocked", "Workflow Blocked"),
        ("milestone_missed", "Milestone Missed"),
    ]

    SEVERITY_LEVELS = [
        ("info", "Information"),
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
        ("critical", "Critical"),
    ]

    # Identifiers
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    alert_type = models.CharField(
        max_length=30,
        choices=ALERT_TYPES,
        help_text="Type of alert",
        db_index=True,
    )

    severity = models.CharField(
        max_length=10,
        choices=SEVERITY_LEVELS,
        default="medium",
        help_text="Severity level of this alert",
        db_index=True,
    )

    # Content
    title = models.CharField(
        max_length=200, help_text="Short title describing the alert"
    )

    description = models.TextField(
        help_text="Detailed description of the alert and recommended actions"
    )

    # Related Objects (nullable to support different alert types)
    # NOTE: ProjectWorkflow is now a proxy to WorkItem
    # See: common.proxies.ProjectWorkflowProxy
    related_workflow = models.ForeignKey(
        "common.WorkItem",  # Changed from "ProjectWorkflow" to use WorkItem directly
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="project_alerts",  # Changed from "alerts" to avoid conflicts
        help_text="Related project workflow (if applicable)",
    )

    related_ppa = models.ForeignKey(
        "monitoring.MonitoringEntry",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="alerts",
        help_text="Related PPA (if applicable)",
    )

    related_need = models.ForeignKey(
        "mana.Need",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="alerts",
        help_text="Related need (if applicable)",
    )

    related_policy = models.ForeignKey(
        "policy_tracking.PolicyRecommendation",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="alerts",
        help_text="Related policy (if applicable)",
    )

    related_mao = models.ForeignKey(
        "coordination.Organization",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="alerts",
        help_text="Related MAO (if applicable)",
    )

    # Additional Data
    alert_data = models.JSONField(
        default=dict, help_text="Additional structured data related to this alert"
    )

    # Action URL
    action_url = models.CharField(
        max_length=500,
        blank=True,
        help_text="URL to navigate to for addressing this alert",
    )

    # Status
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this alert is still active/relevant",
        db_index=True,
    )

    is_acknowledged = models.BooleanField(
        default=False, help_text="Whether this alert has been acknowledged by a user"
    )

    acknowledged_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="acknowledged_alerts",
        help_text="User who acknowledged this alert",
    )

    acknowledged_at = models.DateTimeField(
        null=True, blank=True, help_text="When this alert was acknowledged"
    )

    resolution_notes = models.TextField(
        blank=True, help_text="Notes on how this alert was resolved"
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(
        null=True, blank=True, help_text="When this alert should expire (optional)"
    )

    class Meta:
        verbose_name = "Alert"
        verbose_name_plural = "Alerts"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["alert_type", "is_active"]),
            models.Index(fields=["severity", "is_active", "-created_at"]),
            models.Index(fields=["is_active", "is_acknowledged"]),
        ]

    def __str__(self):
        return f"{self.get_alert_type_display()} - {self.title}"

    def acknowledge(self, user, notes=""):
        """Mark this alert as acknowledged."""
        self.is_acknowledged = True
        self.acknowledged_by = user
        self.acknowledged_at = timezone.now()
        if notes:
            self.resolution_notes = notes
        self.save()

    def deactivate(self, reason=""):
        """Deactivate this alert (mark as no longer relevant)."""
        self.is_active = False
        if reason:
            if self.resolution_notes:
                self.resolution_notes += f"\n\nDeactivated: {reason}"
            else:
                self.resolution_notes = f"Deactivated: {reason}"
        self.save()

    def is_expired(self):
        """Check if this alert has expired."""
        if not self.expires_at:
            return False
        return timezone.now() > self.expires_at

    def get_age_in_days(self):
        """Get age of alert in days."""
        return (timezone.now() - self.created_at).days

    @classmethod
    def create_alert(cls, alert_type, severity, title, description, **kwargs):
        """
        Convenience method to create an alert with additional related objects.

        Args:
            alert_type: Type of alert (from ALERT_TYPES)
            severity: Severity level (from SEVERITY_LEVELS)
            title: Alert title
            description: Alert description
            **kwargs: Additional fields (related_workflow, related_ppa, etc.)

        Returns:
            Alert: Created alert instance
        """
        return cls.objects.create(
            alert_type=alert_type,
            severity=severity,
            title=title,
            description=description,
            **kwargs,
        )

    @classmethod
    def get_active_alerts_by_type(cls, alert_type):
        """Get all active alerts of a specific type."""
        return cls.objects.filter(alert_type=alert_type, is_active=True).select_related(
            "related_workflow",
            "related_ppa",
            "related_need",
            "related_policy",
            "related_mao",
            "acknowledged_by",
        )

    @classmethod
    def get_unacknowledged_count_by_severity(cls):
        """Get count of unacknowledged alerts grouped by severity."""
        return (
            cls.objects.filter(is_active=True, is_acknowledged=False)
            .values("severity")
            .annotate(count=models.Count("id"))
            .order_by("severity")
        )

    @classmethod
    def cleanup_expired_alerts(cls):
        """Deactivate all expired alerts."""
        expired_alerts = cls.objects.filter(
            is_active=True, expires_at__lt=timezone.now()
        )

        count = expired_alerts.count()
        expired_alerts.update(is_active=False, updated_at=timezone.now())

        return count


# ========== BACKWARD COMPATIBILITY PROXY ==========
# Import ProjectWorkflow proxy to access legacy database table.
# See: docs/refactor/WORKITEM_MIGRATION_COMPLETE.md
from common.proxies import ProjectWorkflowProxy as ProjectWorkflow

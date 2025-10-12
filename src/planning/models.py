"""
Planning Module Models

This module implements strategic planning functionality for OOBC.
Supports 3-5 year strategic plans, annual work plans, and goal tracking.

BMMS Note: Organization-agnostic design. Organization field will be added
in BMMS migration for multi-tenant support.
"""

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.utils import timezone
import datetime

User = get_user_model()


class StrategicPlan(models.Model):
    """
    3-5 year strategic plan for OOBC

    BMMS Note: Will add organization field in multi-tenant migration
    Migration will be: organization = models.ForeignKey('organizations.Organization', on_delete=models.PROTECT)
    """

    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('approved', 'Approved'),
        ('active', 'Active'),
        ('archived', 'Archived'),
    ]

    title = models.CharField(
        max_length=255,
        help_text="Strategic plan title (e.g., 'OOBC Strategic Plan 2024-2028')"
    )
    start_year = models.IntegerField(
        validators=[MinValueValidator(2020)],
        help_text="Starting year of strategic plan"
    )
    end_year = models.IntegerField(
        validators=[MinValueValidator(2020)],
        help_text="Ending year of strategic plan"
    )
    vision = models.TextField(
        help_text="Long-term vision statement"
    )
    mission = models.TextField(
        help_text="Mission statement describing purpose and approach"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        help_text="Current status of strategic plan"
    )

    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='strategic_plans_created'
    )

    class Meta:
        ordering = ['-start_year']
        verbose_name = "Strategic Plan"
        verbose_name_plural = "Strategic Plans"
        indexes = [
            models.Index(fields=['start_year', 'end_year']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.title} ({self.start_year}-{self.end_year})"

    def clean(self):
        """Validate year range"""
        if self.end_year and self.start_year:
            if self.end_year <= self.start_year:
                raise ValidationError("End year must be after start year")

            if self.end_year - self.start_year > 10:
                raise ValidationError("Strategic plans should not exceed 10 years")

    @property
    def year_range(self):
        """Return formatted year range"""
        return f"{self.start_year}-{self.end_year}"

    @property
    def duration_years(self):
        """Return plan duration in years"""
        return self.end_year - self.start_year + 1

    @property
    def is_active(self):
        """Check if plan is currently active"""
        return self.status == 'active'

    @property
    def overall_progress(self):
        """Calculate overall progress from goals"""
        goals = self.goals.all()
        if not goals.exists():
            return 0

        total_progress = sum(goal.completion_percentage for goal in goals)
        return round(total_progress / goals.count(), 2)


class StrategicGoal(models.Model):
    """
    Strategic goals within a strategic plan

    Each goal represents a major objective to be achieved over the strategic plan period.
    """

    PRIORITY_CHOICES = [
        ('critical', 'Critical'),
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low'),
    ]

    STATUS_CHOICES = [
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('deferred', 'Deferred'),
    ]

    strategic_plan = models.ForeignKey(
        StrategicPlan,
        on_delete=models.CASCADE,
        related_name='goals'
    )
    title = models.CharField(
        max_length=255,
        help_text="Goal title (e.g., 'Improve education access in OBCs')"
    )
    description = models.TextField(
        help_text="Detailed description of the strategic goal"
    )
    target_metric = models.CharField(
        max_length=255,
        help_text="Metric used to measure goal achievement (e.g., 'Number of schools built')"
    )
    target_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Target value for the metric"
    )
    current_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Current value of the metric"
    )
    completion_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Percentage completion (0-100)"
    )
    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default='medium'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='not_started'
    )

    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['priority', '-created_at']
        verbose_name = "Strategic Goal"
        verbose_name_plural = "Strategic Goals"

    def __str__(self):
        return f"{self.title} ({self.completion_percentage}%)"

    @property
    def is_on_track(self):
        """Determine if goal is on track based on progress and time elapsed"""
        plan = self.strategic_plan
        current_year = timezone.now().year

        if current_year < plan.start_year:
            return True  # Plan hasn't started yet

        if current_year > plan.end_year:
            return self.status == 'completed'  # Plan ended

        # Calculate expected progress
        years_elapsed = current_year - plan.start_year + 1
        total_years = plan.duration_years
        expected_progress = (years_elapsed / total_years) * 100

        # Goal is on track if actual progress >= 80% of expected progress
        return float(self.completion_percentage) >= (expected_progress * 0.8)


class AnnualWorkPlan(models.Model):
    """
    Annual operational work plan

    Translates strategic plan goals into yearly actionable objectives.
    """

    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('approved', 'Approved'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('archived', 'Archived'),
    ]

    strategic_plan = models.ForeignKey(
        StrategicPlan,
        on_delete=models.CASCADE,
        related_name='annual_plans'
    )
    title = models.CharField(
        max_length=255,
        help_text="Annual plan title (e.g., 'OOBC Annual Work Plan 2025')"
    )
    year = models.IntegerField(
        validators=[MinValueValidator(2020)],
        help_text="Fiscal year for this work plan"
    )
    description = models.TextField(
        blank=True,
        help_text="Overview of annual priorities and approach"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft'
    )

    # Budget field for future integration
    budget_total = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Total budget allocation for this annual plan"
    )

    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='annual_plans_created'
    )

    class Meta:
        ordering = ['-year']
        verbose_name = "Annual Work Plan"
        verbose_name_plural = "Annual Work Plans"
        unique_together = [['strategic_plan', 'year']]
        indexes = [
            models.Index(fields=['year']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.title} ({self.year})"

    def clean(self):
        """Validate year is within strategic plan range"""
        if self.year and self.strategic_plan_id:
            if self.year < self.strategic_plan.start_year or self.year > self.strategic_plan.end_year:
                raise ValidationError(
                    f"Annual plan year must be within strategic plan range "
                    f"({self.strategic_plan.start_year}-{self.strategic_plan.end_year})"
                )

    @property
    def overall_progress(self):
        """Calculate overall progress from objectives"""
        objectives = self.objectives.all()
        if not objectives.exists():
            return 0

        total_progress = sum(float(obj.completion_percentage) for obj in objectives)
        return round(total_progress / objectives.count(), 2)

    @property
    def total_objectives(self):
        """Return total number of objectives"""
        return self.objectives.count()

    @property
    def completed_objectives(self):
        """Return number of completed objectives"""
        return self.objectives.filter(status='completed').count()


class WorkPlanObjective(models.Model):
    """
    Specific objectives within an annual work plan

    Measurable, time-bound objectives that contribute to strategic goals.
    """

    STATUS_CHOICES = [
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('deferred', 'Deferred'),
        ('cancelled', 'Cancelled'),
    ]

    annual_work_plan = models.ForeignKey(
        AnnualWorkPlan,
        on_delete=models.CASCADE,
        related_name='objectives'
    )
    strategic_goal = models.ForeignKey(
        StrategicGoal,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='work_plan_objectives',
        help_text="Strategic goal this objective contributes to"
    )
    title = models.CharField(
        max_length=255,
        help_text="Objective title (e.g., 'Build 5 new classrooms in Lanao del Sur OBCs')"
    )
    description = models.TextField(
        help_text="Detailed description of the objective"
    )
    target_date = models.DateField(
        help_text="Target completion date"
    )
    completion_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )

    # Measurable indicator
    indicator = models.CharField(
        max_length=255,
        help_text="How to measure success (e.g., 'Number of classrooms constructed')"
    )
    baseline_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Starting value of indicator"
    )
    target_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Target value of indicator"
    )
    current_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Current value of indicator"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='not_started'
    )

    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['target_date', '-created_at']
        verbose_name = "Work Plan Objective"
        verbose_name_plural = "Work Plan Objectives"

    def __str__(self):
        return f"{self.title} ({self.completion_percentage}%)"

    @property
    def is_overdue(self):
        """Check if objective is past target date and not completed"""
        return (
            self.target_date < timezone.now().date() and
            self.status != 'completed'
        )

    @property
    def days_remaining(self):
        """Calculate days until target date"""
        delta = self.target_date - timezone.now().date()
        return delta.days

    def update_progress_from_indicator(self):
        """Calculate completion percentage from indicator values"""
        if self.target_value == self.baseline_value:
            return 0

        progress = ((float(self.current_value) - float(self.baseline_value)) /
                   (float(self.target_value) - float(self.baseline_value))) * 100

        self.completion_percentage = max(0, min(100, progress))
        self.save(update_fields=['completion_percentage'])

"""
Organization model for BMMS multi-tenancy.

This module defines the Organization model representing BARMM Ministries, Offices,
and Agencies (MOAs) and the OrganizationMembership model for user-organization relationships.
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

from common.models import Region, Municipality

User = get_user_model()


class Organization(models.Model):
    """
    BARMM Ministry, Office, or Agency (MOA).

    Represents one of the 44 BARMM government organizations that will use BMMS.
    Each organization has isolated data and configurable module access.
    """

    ORG_TYPE_CHOICES = [
        ('ministry', _('Ministry')),
        ('office', _('Office')),
        ('agency', _('Agency')),
        ('special', _('Special Body')),
        ('commission', _('Commission')),
    ]

    # Identification
    code = models.CharField(
        max_length=20,
        unique=True,
        db_index=True,
        help_text=_('Unique organization code (e.g., OOBC, MOH, MOLE)')
    )
    name = models.CharField(
        max_length=200,
        help_text=_('Full organization name')
    )
    acronym = models.CharField(
        max_length=20,
        blank=True,
        help_text=_('Alternative acronym (if different from code)')
    )
    org_type = models.CharField(
        max_length=20,
        choices=ORG_TYPE_CHOICES,
        help_text=_('Type of organization')
    )

    # Mandate and Functions
    mandate = models.TextField(
        blank=True,
        help_text=_('Legal mandate and responsibilities')
    )
    powers = models.JSONField(
        default=list,
        blank=True,
        help_text=_('List of powers and functions')
    )

    # Module Activation Flags
    enable_mana = models.BooleanField(
        default=True,
        help_text=_('Enable MANA (Needs Assessment) module')
    )
    enable_planning = models.BooleanField(
        default=True,
        help_text=_('Enable Planning module')
    )
    enable_budgeting = models.BooleanField(
        default=True,
        help_text=_('Enable Budgeting module (Parliament Bill No. 325)')
    )
    enable_me = models.BooleanField(
        default=True,
        verbose_name=_('Enable M&E'),
        help_text=_('Enable Monitoring & Evaluation module')
    )
    enable_coordination = models.BooleanField(
        default=True,
        help_text=_('Enable Coordination module')
    )
    enable_policies = models.BooleanField(
        default=True,
        help_text=_('Enable Policies/Recommendations module')
    )

    # Geographic Coverage
    primary_region = models.ForeignKey(
        Region,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='primary_organizations',
        help_text=_('Primary region of operations')
    )
    service_areas = models.ManyToManyField(
        Municipality,
        blank=True,
        related_name='served_by_organizations',
        help_text=_('Municipalities served by this organization')
    )

    # Leadership and Contact
    head_official = models.CharField(
        max_length=200,
        blank=True,
        help_text=_('Name of head official (Minister, Director, etc.)')
    )
    head_title = models.CharField(
        max_length=100,
        blank=True,
        help_text=_('Title of head official')
    )
    primary_focal_person = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='primary_focal_organizations',
        help_text=_('Primary focal person for this organization')
    )

    # Contact Information
    email = models.EmailField(
        blank=True,
        help_text=_('Primary email address')
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        help_text=_('Primary phone number')
    )
    website = models.URLField(
        blank=True,
        help_text=_('Official website URL')
    )
    address = models.TextField(
        blank=True,
        help_text=_('Physical address')
    )

    # Status Flags
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        help_text=_('Whether this organization is currently active in BMMS')
    )
    is_pilot = models.BooleanField(
        default=False,
        db_index=True,
        help_text=_('Whether this is a pilot MOA (MOH, MOLE, MAFAR)')
    )

    # Onboarding Tracking
    onboarding_date = models.DateField(
        null=True,
        blank=True,
        help_text=_('Date when organization was onboarded to BMMS')
    )
    go_live_date = models.DateField(
        null=True,
        blank=True,
        help_text=_('Date when organization went live in BMMS')
    )

    # Audit Fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = _('Organization')
        verbose_name_plural = _('Organizations')
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['org_type', 'is_active']),
            models.Index(fields=['is_pilot']),
        ]

    def __str__(self):
        return f"{self.code} - {self.name}"

    def clean(self):
        """Validate organization data."""
        super().clean()
        if self.code:
            self.code = self.code.upper()

    @property
    def enabled_modules(self):
        """Return list of enabled module names."""
        modules = []
        if self.enable_mana:
            modules.append('MANA')
        if self.enable_planning:
            modules.append('Planning')
        if self.enable_budgeting:
            modules.append('Budgeting')
        if self.enable_me:
            modules.append('M&E')
        if self.enable_coordination:
            modules.append('Coordination')
        if self.enable_policies:
            modules.append('Policies')
        return modules


class OrganizationMembership(models.Model):
    """
    User membership in an organization.

    Links users to organizations with roles and permissions.
    Users can belong to multiple organizations (e.g., OCM staff, inter-agency coordination).
    """

    ROLE_CHOICES = [
        ('admin', _('Administrator')),
        ('manager', _('Manager')),
        ('staff', _('Staff')),
        ('viewer', _('Viewer')),
    ]

    # Relationships
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='organization_memberships',
        help_text=_('User account')
    )
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='memberships',
        help_text=_('Organization')
    )

    # Role and Status
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='staff',
        help_text=_('Role in the organization')
    )
    is_primary = models.BooleanField(
        default=False,
        db_index=True,
        help_text=_('Whether this is the user\'s primary organization')
    )
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        help_text=_('Whether this membership is currently active')
    )

    # Position Information
    position = models.CharField(
        max_length=200,
        blank=True,
        help_text=_('Job title or position within the organization')
    )
    department = models.CharField(
        max_length=200,
        blank=True,
        help_text=_('Department or unit within the organization')
    )

    # Permissions
    can_manage_users = models.BooleanField(
        default=False,
        help_text=_('Can add/remove users and manage memberships')
    )
    can_approve_plans = models.BooleanField(
        default=False,
        help_text=_('Can approve strategic plans and work plans')
    )
    can_approve_budgets = models.BooleanField(
        default=False,
        help_text=_('Can approve budget proposals')
    )
    can_view_reports = models.BooleanField(
        default=True,
        help_text=_('Can view reports and analytics')
    )

    # Audit Fields
    joined_date = models.DateField(
        auto_now_add=True,
        help_text=_('Date when user joined this organization')
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [['user', 'organization']]
        ordering = ['-is_primary', 'user__username']
        verbose_name = _('Organization Membership')
        verbose_name_plural = _('Organization Memberships')
        indexes = [
            models.Index(fields=['user', 'is_primary']),
            models.Index(fields=['organization', 'role']),
            models.Index(fields=['user', 'organization']),
        ]

    def __str__(self):
        primary = " (Primary)" if self.is_primary else ""
        return f"{self.user.username} @ {self.organization.code} - {self.get_role_display()}{primary}"

    def clean(self):
        """Validate membership data."""
        super().clean()

        # Ensure only one primary organization per user
        if self.is_primary:
            existing_primary = OrganizationMembership.objects.filter(
                user=self.user,
                is_primary=True
            ).exclude(pk=self.pk)

            if existing_primary.exists():
                raise ValidationError({
                    'is_primary': _('User already has a primary organization. '
                                  'Please unset the existing primary first.')
                })

    def save(self, *args, **kwargs):
        """Override save to enforce validation."""
        self.full_clean()
        super().save(*args, **kwargs)

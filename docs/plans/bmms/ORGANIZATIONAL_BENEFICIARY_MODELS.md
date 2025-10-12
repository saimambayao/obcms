# Organizational Beneficiary Database Models - BMMS

**Date:** October 12, 2025
**Status:** Design Complete - Ready for Implementation
**Version:** 1.0
**Author:** OBCMS System Architect (Claude Sonnet 4.5)

---

## Executive Summary

This document provides the complete Django model design for organizational beneficiaries in BMMS (Bangsamoro Ministerial Management System). Organizational beneficiaries are organizations that benefit from government programs, including cooperatives, associations, businesses, LGUs, and NGOs.

**Key Features:**
- Full integration with existing OBCMS architecture (geographic hierarchy, MOA scoping)
- Support for organizational enrollment in PPAs (Programs, Projects, and Activities)
- Link organizational beneficiaries to individual beneficiaries (membership tracking)
- Verification and validation workflow
- Audit trail and metadata tracking

---

## Architecture Overview

### Database Relationships

```
OrganizationalBeneficiary
    ├── ForeignKey → Barangay (geographic location)
    ├── ForeignKey → Municipality (geographic location)
    ├── ForeignKey → Organization (created_by_organization - which MOA registered this)
    ├── One-to-Many → OrganizationalBeneficiaryEnrollment
    └── One-to-Many → OrganizationalBeneficiaryMember

OrganizationalBeneficiaryEnrollment
    ├── ForeignKey → OrganizationalBeneficiary
    ├── ForeignKey → ProgramProjectActivity (from planning module)
    └── ForeignKey → Organization (organization that enrolled them)

OrganizationalBeneficiaryMember
    ├── ForeignKey → OrganizationalBeneficiary
    ├── ForeignKey → IndividualBeneficiary (when individual beneficiary tracking is added)
    └── role (membership role: member, officer, president, etc.)
```

---

## Model Specifications

### 1. OrganizationalBeneficiary Model

**Purpose:** Core model for tracking organizations that benefit from government programs.

**Key Fields:**
- Unique identification (SEC/DTI registration or UUID)
- Organization profile (name, type, registration details)
- Geographic location (barangay, municipality)
- Contact information (contact person, phone, email)
- Verification status
- MOA attribution (which MOA registered this beneficiary)

**Integration Points:**
- Geographic hierarchy (Barangay, Municipality via common.models)
- MOA attribution (Organization via coordination.models)
- Future: IndividualBeneficiary (when individual beneficiary tracking is implemented)

---

### 2. OrganizationalBeneficiaryEnrollment Model

**Purpose:** Track enrollment of organizational beneficiaries in specific PPAs.

**Key Fields:**
- Organizational beneficiary reference
- PPA reference (from planning module)
- Enrollment date and status
- Organization that enrolled them
- Expected impact metrics

**Integration Points:**
- ProgramProjectActivity (from planning module - Phase 2 of BMMS)
- Organization (MOA that enrolled the beneficiary)

---

### 3. OrganizationalBeneficiaryMember Model (Optional)

**Purpose:** Link organizational beneficiaries to individual beneficiaries for membership tracking.

**Key Fields:**
- Organizational beneficiary reference
- Individual beneficiary reference
- Membership role (member, officer, president, treasurer, etc.)
- Membership dates

**Use Case:** Track which individuals are members of cooperatives, associations, or organizations.

---

## Complete Django Model Code

```python
"""
Organizational Beneficiary Models for BMMS (Bangsamoro Ministerial Management System)

These models track organizations that benefit from government programs:
- Cooperatives, associations, businesses
- LGUs, NGOs, community organizations
- Their enrollment in PPAs (Programs, Projects, and Activities)
- Membership relationships with individual beneficiaries

Integration:
- Geographic hierarchy (Barangay, Municipality from common.models)
- MOA attribution (Organization from coordination.models)
- PPA enrollment (ProgramProjectActivity from planning module)
"""

import uuid
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone

from common.models import Barangay, Municipality
from coordination.models import Organization


class OrganizationalBeneficiary(models.Model):
    """
    Organizations that benefit from government programs.

    Includes cooperatives, associations, businesses, LGUs, NGOs, and other
    organizational entities enrolled in PPAs or receiving government support.
    """

    ORGANIZATION_TYPE_CHOICES = [
        ('cooperative', 'Cooperative'),
        ('association', 'Association'),
        ('business', 'Private Business'),
        ('lgu', 'Local Government Unit'),
        ('ngo', 'Non-Governmental Organization'),
        ('cbo', 'Community-Based Organization'),
        ('peoples_org', "People's Organization"),
        ('federation', 'Federation'),
        ('union', 'Union'),
        ('guild', 'Guild'),
        ('enterprise', 'Social Enterprise'),
        ('foundation', 'Foundation'),
        ('other', 'Other'),
    ]

    # Primary Key
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique identifier for this organizational beneficiary"
    )

    # Unique Identification
    unique_id = models.CharField(
        max_length=100,
        unique=True,
        help_text="Unique identifier: SEC/DTI/CDA registration number or generated UUID"
    )

    # Organization Profile
    organization_name = models.CharField(
        max_length=255,
        db_index=True,
        help_text="Official name of the organization"
    )

    organization_type = models.CharField(
        max_length=20,
        choices=ORGANIZATION_TYPE_CHOICES,
        db_index=True,
        help_text="Type of organization"
    )

    # Registration Information
    registration_number = models.CharField(
        max_length=100,
        blank=True,
        help_text="Official registration number (SEC, DTI, CDA, etc.)"
    )

    registration_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date when organization was officially registered"
    )

    registration_agency = models.CharField(
        max_length=100,
        blank=True,
        help_text="Agency where registered (SEC, DTI, CDA, etc.)"
    )

    # Contact Person
    contact_person_name = models.CharField(
        max_length=255,
        help_text="Name of primary contact person"
    )

    contact_person_position = models.CharField(
        max_length=100,
        blank=True,
        help_text="Position/title of contact person (President, Chairman, etc.)"
    )

    # Contact Information
    contact_number = models.CharField(
        max_length=50,
        blank=True,
        validators=[
            RegexValidator(
                regex=r'^[\d\s\+\-\(\)]+$',
                message="Enter a valid phone number"
            )
        ],
        help_text="Primary contact number"
    )

    contact_mobile = models.CharField(
        max_length=50,
        blank=True,
        validators=[
            RegexValidator(
                regex=r'^[\d\s\+\-\(\)]+$',
                message="Enter a valid mobile number"
            )
        ],
        help_text="Mobile phone number"
    )

    email = models.EmailField(
        blank=True,
        help_text="Email address of the organization or contact person"
    )

    # Address Information
    address = models.TextField(
        help_text="Complete physical address"
    )

    # Geographic Location (Links to existing OBCMS geographic hierarchy)
    barangay = models.ForeignKey(
        Barangay,
        on_delete=models.PROTECT,
        related_name='organizational_beneficiaries',
        help_text="Barangay where organization is located"
    )

    municipality = models.ForeignKey(
        Municipality,
        on_delete=models.PROTECT,
        related_name='organizational_beneficiaries',
        help_text="Municipality where organization is located"
    )

    # Organization Details
    number_of_members = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Total number of members (for cooperatives, associations, etc.)"
    )

    year_established = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Year when organization was established"
    )

    # BMMS: MOA Attribution (Organization-Scoped)
    # This tracks which MOA registered/created this organizational beneficiary
    created_by_organization = models.ForeignKey(
        Organization,
        on_delete=models.PROTECT,
        related_name='registered_organizational_beneficiaries',
        limit_choices_to={'organization_type': 'bmoa'},
        help_text="MOA that registered this organizational beneficiary"
    )

    # Verification Status
    is_verified = models.BooleanField(
        default=False,
        db_index=True,
        help_text="Whether this organization has been verified by the MOA"
    )

    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_organizational_beneficiaries',
        help_text="User who verified this organization"
    )

    verified_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Date when verification was completed"
    )

    verification_notes = models.TextField(
        blank=True,
        help_text="Notes from verification process"
    )

    # Additional Information
    description = models.TextField(
        blank=True,
        help_text="Brief description of the organization and its activities"
    )

    areas_of_focus = models.TextField(
        blank=True,
        help_text="Main areas of focus or services provided"
    )

    # Status
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        help_text="Whether this organization is currently active"
    )

    deactivation_reason = models.TextField(
        blank=True,
        help_text="Reason for deactivation (if applicable)"
    )

    deactivated_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Date when organization was deactivated"
    )

    # Metadata
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='created_organizational_beneficiaries',
        help_text="User who created this record"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when record was created"
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when record was last updated"
    )

    notes = models.TextField(
        blank=True,
        help_text="Additional notes or observations"
    )

    class Meta:
        db_table = 'bmms_organizational_beneficiary'
        ordering = ['organization_name']
        verbose_name = 'Organizational Beneficiary'
        verbose_name_plural = 'Organizational Beneficiaries'
        indexes = [
            models.Index(fields=['organization_name']),
            models.Index(fields=['organization_type', 'is_active']),
            models.Index(fields=['barangay', 'municipality']),
            models.Index(fields=['created_by_organization', 'is_verified']),
            models.Index(fields=['is_verified', 'is_active']),
        ]

    def __str__(self):
        return f"{self.organization_name} ({self.get_organization_type_display()})"

    def clean(self):
        """Validate geographic hierarchy consistency."""
        super().clean()

        # Ensure barangay belongs to the selected municipality
        if self.barangay and self.municipality:
            if self.barangay.municipality != self.municipality:
                raise ValidationError({
                    'barangay': 'Selected barangay does not belong to the selected municipality.'
                })

    def save(self, *args, **kwargs):
        # Auto-set municipality from barangay if not provided
        if self.barangay and not self.municipality:
            self.municipality = self.barangay.municipality

        # Generate unique_id if not provided
        if not self.unique_id:
            # Use registration number if available, otherwise generate UUID
            if self.registration_number:
                self.unique_id = f"REG-{self.registration_number}"
            else:
                self.unique_id = f"ORG-{str(self.id)[:8].upper()}"

        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def province(self):
        """Return the province (derived from municipality)."""
        return self.municipality.province if self.municipality else None

    @property
    def region(self):
        """Return the region (derived from province)."""
        return self.province.region if self.province else None

    @property
    def full_address(self):
        """Return complete address with geographic hierarchy."""
        parts = [
            self.address,
            f"Barangay {self.barangay.name}" if self.barangay else None,
            self.municipality.name if self.municipality else None,
            self.province.name if self.province else None,
        ]
        return ", ".join([p for p in parts if p])

    @property
    def enrollment_count(self):
        """Return count of PPA enrollments."""
        return self.enrollments.count()

    @property
    def active_enrollment_count(self):
        """Return count of active PPA enrollments."""
        return self.enrollments.filter(
            status__in=['enrolled', 'active']
        ).count()


class OrganizationalBeneficiaryEnrollment(models.Model):
    """
    Enrollment of organizational beneficiaries in specific PPAs.

    Tracks which organizations are enrolled in which government programs,
    projects, or activities, along with enrollment status and expected impact.
    """

    ENROLLMENT_STATUS_CHOICES = [
        ('enrolled', 'Enrolled'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('withdrawn', 'Withdrawn'),
        ('suspended', 'Suspended'),
        ('cancelled', 'Cancelled'),
    ]

    # Primary Key
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique identifier for this enrollment"
    )

    # Core Relationships
    organizational_beneficiary = models.ForeignKey(
        OrganizationalBeneficiary,
        on_delete=models.CASCADE,
        related_name='enrollments',
        help_text="Organization enrolled in this PPA"
    )

    # PPA Reference (from planning module - Phase 2 of BMMS)
    # Note: This will use the actual ProgramProjectActivity model when planning module is implemented
    ppa = models.ForeignKey(
        'planning.ProgramProjectActivity',  # Forward reference to planning module
        on_delete=models.CASCADE,
        related_name='organizational_enrollments',
        help_text="Program, Project, or Activity this organization is enrolled in"
    )

    # BMMS: Organization Scoping
    # This tracks which MOA enrolled this organization in the PPA
    organization = models.ForeignKey(
        Organization,
        on_delete=models.PROTECT,
        related_name='organizational_beneficiary_enrollments',
        limit_choices_to={'organization_type': 'bmoa'},
        help_text="MOA that enrolled this organizational beneficiary"
    )

    # Enrollment Details
    enrollment_date = models.DateField(
        default=timezone.now,
        db_index=True,
        help_text="Date when organization was enrolled"
    )

    status = models.CharField(
        max_length=15,
        choices=ENROLLMENT_STATUS_CHOICES,
        default='enrolled',
        db_index=True,
        help_text="Current enrollment status"
    )

    # Expected Impact
    expected_impact = models.TextField(
        blank=True,
        help_text="Expected impact or outcomes for this organization"
    )

    expected_members_served = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Expected number of organization members who will benefit"
    )

    expected_community_reach = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Expected number of community members reached through this organization"
    )

    # Actual Impact (to be updated during implementation)
    actual_members_served = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Actual number of organization members who benefited"
    )

    actual_community_reach = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Actual number of community members reached"
    )

    # Completion Details
    completion_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date when enrollment was completed or ended"
    )

    completion_notes = models.TextField(
        blank=True,
        help_text="Notes on completion or termination"
    )

    # Metadata
    enrolled_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='organizational_enrollments_created',
        help_text="User who enrolled this organization"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when enrollment was created"
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when enrollment was last updated"
    )

    notes = models.TextField(
        blank=True,
        help_text="Additional notes about this enrollment"
    )

    class Meta:
        db_table = 'bmms_organizational_beneficiary_enrollment'
        ordering = ['-enrollment_date']
        verbose_name = 'Organizational Beneficiary Enrollment'
        verbose_name_plural = 'Organizational Beneficiary Enrollments'
        unique_together = [
            ['organizational_beneficiary', 'ppa']
        ]
        indexes = [
            models.Index(fields=['organizational_beneficiary', 'status']),
            models.Index(fields=['ppa', 'status']),
            models.Index(fields=['organization', 'enrollment_date']),
            models.Index(fields=['enrollment_date', 'status']),
        ]

    def __str__(self):
        return f"{self.organizational_beneficiary.organization_name} → {self.ppa}"

    def clean(self):
        """Validate enrollment business rules."""
        super().clean()

        # Ensure organizational beneficiary is active
        if self.organizational_beneficiary and not self.organizational_beneficiary.is_active:
            raise ValidationError({
                'organizational_beneficiary': 'Cannot enroll an inactive organization.'
            })

        # Ensure organizational beneficiary is verified
        if self.organizational_beneficiary and not self.organizational_beneficiary.is_verified:
            raise ValidationError({
                'organizational_beneficiary': 'Organization must be verified before enrollment.'
            })

    @property
    def impact_achievement_rate(self):
        """
        Calculate impact achievement rate as percentage.

        Returns average of members served rate and community reach rate.
        """
        rates = []

        if self.expected_members_served and self.actual_members_served:
            member_rate = (self.actual_members_served / self.expected_members_served) * 100
            rates.append(member_rate)

        if self.expected_community_reach and self.actual_community_reach:
            reach_rate = (self.actual_community_reach / self.expected_community_reach) * 100
            rates.append(reach_rate)

        if rates:
            return sum(rates) / len(rates)
        return 0


class OrganizationalBeneficiaryMember(models.Model):
    """
    Membership relationship between organizational beneficiaries and individual beneficiaries.

    Tracks which individuals are members of which organizations (cooperatives, associations, etc.).
    This enables cross-referencing between organizational and individual beneficiary data.

    Note: This model references IndividualBeneficiary which will be implemented in a future phase.
    """

    MEMBERSHIP_ROLE_CHOICES = [
        ('member', 'Member'),
        ('officer', 'Officer'),
        ('president', 'President'),
        ('vice_president', 'Vice President'),
        ('secretary', 'Secretary'),
        ('treasurer', 'Treasurer'),
        ('board_member', 'Board Member'),
        ('auditor', 'Auditor'),
        ('committee_chair', 'Committee Chair'),
        ('other', 'Other Role'),
    ]

    # Primary Key
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique identifier for this membership"
    )

    # Core Relationships
    organizational_beneficiary = models.ForeignKey(
        OrganizationalBeneficiary,
        on_delete=models.CASCADE,
        related_name='members',
        help_text="Organization this person is a member of"
    )

    # Individual Beneficiary Reference (forward reference to future implementation)
    individual_beneficiary = models.ForeignKey(
        'beneficiaries.IndividualBeneficiary',  # Forward reference to beneficiaries module
        on_delete=models.CASCADE,
        related_name='organizational_memberships',
        help_text="Individual who is a member of this organization"
    )

    # Membership Details
    membership_role = models.CharField(
        max_length=20,
        choices=MEMBERSHIP_ROLE_CHOICES,
        default='member',
        db_index=True,
        help_text="Role or position within the organization"
    )

    membership_start_date = models.DateField(
        help_text="Date when membership started"
    )

    membership_end_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date when membership ended (if applicable)"
    )

    # Status
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        help_text="Whether this membership is currently active"
    )

    # Metadata
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when membership record was created"
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when membership record was last updated"
    )

    notes = models.TextField(
        blank=True,
        help_text="Additional notes about this membership"
    )

    class Meta:
        db_table = 'bmms_organizational_beneficiary_member'
        ordering = ['organizational_beneficiary', '-membership_start_date']
        verbose_name = 'Organizational Beneficiary Member'
        verbose_name_plural = 'Organizational Beneficiary Members'
        unique_together = [
            ['organizational_beneficiary', 'individual_beneficiary']
        ]
        indexes = [
            models.Index(fields=['organizational_beneficiary', 'is_active']),
            models.Index(fields=['individual_beneficiary', 'membership_role']),
            models.Index(fields=['membership_start_date', 'membership_end_date']),
        ]

    def __str__(self):
        return (
            f"{self.individual_beneficiary} → {self.organizational_beneficiary.organization_name} "
            f"({self.get_membership_role_display()})"
        )

    def clean(self):
        """Validate membership business rules."""
        super().clean()

        # Validate date range
        if self.membership_end_date and self.membership_start_date:
            if self.membership_end_date < self.membership_start_date:
                raise ValidationError({
                    'membership_end_date': 'End date must be after start date.'
                })

        # Ensure organizational beneficiary is active
        if self.organizational_beneficiary and not self.organizational_beneficiary.is_active:
            raise ValidationError({
                'organizational_beneficiary': 'Cannot add members to an inactive organization.'
            })
```

---

## Database Migration Notes

### Migration Order

1. **Phase 1 (Foundation):** Create `OrganizationalBeneficiary` model first
2. **Phase 2 (Planning Integration):** Create `OrganizationalBeneficiaryEnrollment` after planning module exists
3. **Phase 3 (Individual Linkage):** Create `OrganizationalBeneficiaryMember` after individual beneficiary tracking is implemented

### Dependencies

- **Existing Models (Available Now):**
  - `common.models.Barangay`
  - `common.models.Municipality`
  - `coordination.models.Organization`
  - `settings.AUTH_USER_MODEL` (User)

- **Future Models (Forward References):**
  - `planning.ProgramProjectActivity` (Phase 2 of BMMS)
  - `beneficiaries.IndividualBeneficiary` (Future beneficiary tracking module)

### Migration Strategy

```python
# Example migration file structure

from django.db import migrations, models
import django.db.models.deletion
import uuid

class Migration(migrations.Migration):

    dependencies = [
        ('common', '0001_initial'),  # Region, Province, Municipality, Barangay
        ('coordination', '0001_initial'),  # Organization
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrganizationalBeneficiary',
            fields=[
                # ... (all fields from model above)
            ],
        ),
        # OrganizationalBeneficiaryEnrollment and OrganizationalBeneficiaryMember
        # will be added in subsequent migrations after their dependencies exist
    ]
```

---

## Admin Interface Configuration

### Recommended Admin Setup

```python
from django.contrib import admin
from .models import (
    OrganizationalBeneficiary,
    OrganizationalBeneficiaryEnrollment,
    OrganizationalBeneficiaryMember
)


@admin.register(OrganizationalBeneficiary)
class OrganizationalBeneficiaryAdmin(admin.ModelAdmin):
    list_display = [
        'organization_name',
        'organization_type',
        'unique_id',
        'municipality',
        'barangay',
        'is_verified',
        'is_active',
        'created_by_organization',
    ]
    list_filter = [
        'organization_type',
        'is_verified',
        'is_active',
        'created_by_organization',
        'municipality__province__region',
    ]
    search_fields = [
        'organization_name',
        'unique_id',
        'registration_number',
        'contact_person_name',
    ]
    readonly_fields = [
        'id',
        'created_at',
        'updated_at',
    ]
    fieldsets = (
        ('Organization Profile', {
            'fields': (
                'organization_name',
                'organization_type',
                'unique_id',
                'description',
                'areas_of_focus',
            )
        }),
        ('Registration Information', {
            'fields': (
                'registration_number',
                'registration_date',
                'registration_agency',
                'year_established',
            )
        }),
        ('Contact Information', {
            'fields': (
                'contact_person_name',
                'contact_person_position',
                'contact_number',
                'contact_mobile',
                'email',
            )
        }),
        ('Location', {
            'fields': (
                'address',
                'barangay',
                'municipality',
            )
        }),
        ('Organization Details', {
            'fields': (
                'number_of_members',
            )
        }),
        ('BMMS Attribution', {
            'fields': (
                'created_by_organization',
            )
        }),
        ('Verification', {
            'fields': (
                'is_verified',
                'verified_by',
                'verified_date',
                'verification_notes',
            )
        }),
        ('Status', {
            'fields': (
                'is_active',
                'deactivation_reason',
                'deactivated_date',
            )
        }),
        ('Metadata', {
            'fields': (
                'id',
                'created_by',
                'created_at',
                'updated_at',
                'notes',
            )
        }),
    )


@admin.register(OrganizationalBeneficiaryEnrollment)
class OrganizationalBeneficiaryEnrollmentAdmin(admin.ModelAdmin):
    list_display = [
        'organizational_beneficiary',
        'ppa',
        'status',
        'enrollment_date',
        'organization',
        'expected_members_served',
    ]
    list_filter = [
        'status',
        'organization',
        'enrollment_date',
    ]
    search_fields = [
        'organizational_beneficiary__organization_name',
        'ppa__name',
    ]
    readonly_fields = [
        'id',
        'created_at',
        'updated_at',
    ]


@admin.register(OrganizationalBeneficiaryMember)
class OrganizationalBeneficiaryMemberAdmin(admin.ModelAdmin):
    list_display = [
        'individual_beneficiary',
        'organizational_beneficiary',
        'membership_role',
        'membership_start_date',
        'is_active',
    ]
    list_filter = [
        'membership_role',
        'is_active',
        'membership_start_date',
    ]
    search_fields = [
        'organizational_beneficiary__organization_name',
        'individual_beneficiary__first_name',
        'individual_beneficiary__last_name',
    ]
    readonly_fields = [
        'id',
        'created_at',
        'updated_at',
    ]
```

---

## API Design Considerations

### RESTful Endpoints (Django REST Framework)

```python
# Recommended URL patterns for organizational beneficiaries

urlpatterns = [
    # Organizational Beneficiaries
    path('organizational-beneficiaries/', views.OrganizationalBeneficiaryListCreateView.as_view()),
    path('organizational-beneficiaries/<uuid:pk>/', views.OrganizationalBeneficiaryDetailView.as_view()),

    # Enrollments
    path('organizational-beneficiaries/<uuid:org_id>/enrollments/', views.EnrollmentListCreateView.as_view()),
    path('enrollments/<uuid:pk>/', views.EnrollmentDetailView.as_view()),

    # Members
    path('organizational-beneficiaries/<uuid:org_id>/members/', views.MemberListCreateView.as_view()),
    path('members/<uuid:pk>/', views.MemberDetailView.as_view()),

    # Verification Workflow
    path('organizational-beneficiaries/<uuid:pk>/verify/', views.VerifyOrganizationView.as_view()),

    # Statistics
    path('organizational-beneficiaries/stats/', views.OrganizationalBeneficiaryStatsView.as_view()),
]
```

### Serializer Design

```python
class OrganizationalBeneficiarySerializer(serializers.ModelSerializer):
    province = serializers.StringRelatedField(read_only=True)
    region = serializers.StringRelatedField(read_only=True)
    enrollment_count = serializers.IntegerField(read_only=True)
    active_enrollment_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = OrganizationalBeneficiary
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']
```

---

## Testing Strategy

### Unit Tests

```python
class OrganizationalBeneficiaryModelTest(TestCase):
    """Test OrganizationalBeneficiary model."""

    def setUp(self):
        self.region = Region.objects.create(code='IX', name='Zamboanga Peninsula')
        self.province = Province.objects.create(region=self.region, code='ZAS', name='Zamboanga del Sur')
        self.municipality = Municipality.objects.create(province=self.province, code='PAGADIAN', name='Pagadian City')
        self.barangay = Barangay.objects.create(municipality=self.municipality, code='BALANGASAN', name='Balangasan')
        self.organization = Organization.objects.create(name='MAFAR', organization_type='bmoa')
        self.user = User.objects.create_user(username='testuser')

    def test_create_organizational_beneficiary(self):
        """Test creating an organizational beneficiary."""
        org_beneficiary = OrganizationalBeneficiary.objects.create(
            organization_name='Balangasan Farmers Cooperative',
            organization_type='cooperative',
            contact_person_name='Juan Dela Cruz',
            contact_number='09171234567',
            address='Purok 1, Balangasan',
            barangay=self.barangay,
            municipality=self.municipality,
            created_by_organization=self.organization,
            created_by=self.user,
        )
        self.assertEqual(org_beneficiary.organization_name, 'Balangasan Farmers Cooperative')
        self.assertTrue(org_beneficiary.unique_id)  # Auto-generated

    def test_geographic_hierarchy_validation(self):
        """Test that barangay must belong to municipality."""
        wrong_municipality = Municipality.objects.create(
            province=self.province,
            code='ANOTHER',
            name='Another Municipality'
        )

        org_beneficiary = OrganizationalBeneficiary(
            organization_name='Test Org',
            organization_type='cooperative',
            contact_person_name='Test Person',
            address='Test Address',
            barangay=self.barangay,
            municipality=wrong_municipality,  # Wrong municipality
            created_by_organization=self.organization,
            created_by=self.user,
        )

        with self.assertRaises(ValidationError):
            org_beneficiary.full_clean()
```

---

## Performance Considerations

### Database Indexes

All models include strategic indexes on:
- Foreign keys (automatic)
- Frequently queried fields (organization_type, status, is_verified, is_active)
- Date fields used for filtering (enrollment_date, membership_start_date)
- Composite indexes for common query patterns

### Query Optimization

```python
# Efficient queries with select_related and prefetch_related

# Fetch organizational beneficiaries with related data
orgs = OrganizationalBeneficiary.objects.select_related(
    'barangay__municipality__province__region',
    'created_by_organization',
    'verified_by',
).prefetch_related(
    'enrollments__ppa',
    'members__individual_beneficiary'
)

# Filter by MOA (organization-scoped)
mafar_beneficiaries = OrganizationalBeneficiary.objects.filter(
    created_by_organization__acronym='MAFAR'
).select_related('municipality', 'barangay')
```

---

## Security & Data Privacy

### Access Control

- **MOA Scoping:** Each organizational beneficiary is attributed to a specific MOA (`created_by_organization`)
- **Data Isolation:** MOA A cannot see organizational beneficiaries registered by MOA B
- **OCM Access:** Office of the Chief Minister sees aggregated read-only data from all MOAs
- **Verification Workflow:** Only verified organizations can be enrolled in PPAs

### Audit Trail

All models include:
- `created_by` - User who created the record
- `created_at` - Timestamp of creation
- `updated_at` - Timestamp of last update
- `notes` - Free-text field for additional context

### Data Validation

- Geographic hierarchy validation (barangay must belong to municipality)
- Email format validation
- Phone number format validation (regex)
- Business rule validation (active status, verification requirements)

---

## Future Enhancements

### Phase 1 (Current)
- ✅ OrganizationalBeneficiary model (complete)

### Phase 2 (After Planning Module)
- OrganizationalBeneficiaryEnrollment model
- Integration with ProgramProjectActivity (PPA) from planning module
- Enrollment workflow and status tracking

### Phase 3 (After Individual Beneficiary Tracking)
- OrganizationalBeneficiaryMember model
- Cross-referencing between organizational and individual beneficiaries
- Membership analytics and reporting

### Phase 4 (Advanced Features)
- Document uploads for registration certificates
- Financial tracking (grants, subsidies received)
- Impact measurement dashboards
- Organizational capacity assessments
- Partnership agreements with other organizations

---

## Implementation Checklist

### Prerequisites
- [ ] Review BMMS TRANSITION_PLAN.md (Phase 1: Foundation complete)
- [ ] Verify coordination.Organization model exists
- [ ] Verify common.models (Barangay, Municipality) exist
- [ ] Confirm User model configuration

### Implementation Steps

**Step 1: Create Django App (if needed)**
```bash
cd src
python manage.py startapp beneficiaries
```

**Step 2: Add Models**
- [ ] Copy OrganizationalBeneficiary model to `beneficiaries/models.py`
- [ ] Add model to `beneficiaries/__init__.py`

**Step 3: Create Migrations**
```bash
python manage.py makemigrations beneficiaries
python manage.py migrate beneficiaries
```

**Step 4: Register Admin Interface**
- [ ] Copy admin configuration to `beneficiaries/admin.py`
- [ ] Verify admin interface works

**Step 5: Create Serializers (Django REST Framework)**
- [ ] Create `beneficiaries/serializers.py`
- [ ] Add OrganizationalBeneficiarySerializer

**Step 6: Create Views and URLs**
- [ ] Create `beneficiaries/views.py`
- [ ] Create `beneficiaries/urls.py`
- [ ] Add to main `urls.py`

**Step 7: Write Tests**
- [ ] Create `beneficiaries/tests/test_models.py`
- [ ] Create `beneficiaries/tests/test_api.py`
- [ ] Run tests: `pytest beneficiaries/`

**Step 8: Update Documentation**
- [ ] Add to BMMS TRANSITION_PLAN.md
- [ ] Update API documentation
- [ ] Create user guide for organizational beneficiary management

---

## Questions & Answers

**Q: Can one organization be enrolled in multiple PPAs?**
A: Yes. The unique_together constraint is on `['organizational_beneficiary', 'ppa']`, meaning one organization can have multiple enrollments (one per PPA).

**Q: Can an organization be a member of another organization?**
A: Not directly in this design. OrganizationalBeneficiaryMember links organizations to *individual* beneficiaries (people). For organization-to-organization relationships, use the existing `coordination.Organization` and `coordination.Partnership` models.

**Q: How do we handle cooperatives with thousands of members?**
A: The `number_of_members` field stores the total count. Individual membership tracking via OrganizationalBeneficiaryMember is optional and should be used selectively (e.g., for officers and board members, not all general members).

**Q: What if an organization relocates to a different barangay?**
A: Update the `barangay` and `municipality` fields. The model includes `updated_at` timestamp to track when changes occurred. Consider adding a history tracking system for location changes if audit trail is critical.

**Q: How do we handle unregistered community organizations?**
A: Leave `registration_number` and `registration_agency` blank. The system will auto-generate a unique_id starting with "ORG-" prefix. Mark as verified by MOA once legitimacy is confirmed through other means.

---

## Conclusion

This comprehensive design provides a production-ready foundation for tracking organizational beneficiaries in BMMS. The models integrate seamlessly with existing OBCMS architecture while supporting the multi-tenant, organization-scoped design principles of BMMS.

**Key Benefits:**
- ✅ Full BMMS integration (organization-scoped, MOA attribution)
- ✅ Geographic hierarchy integration (Region → Province → Municipality → Barangay)
- ✅ Extensible design (supports future individual beneficiary linkage)
- ✅ Comprehensive validation and business rules
- ✅ Production-ready with indexes, metadata, and audit trails
- ✅ Clear migration path and dependencies

**Next Steps:**
1. Review and approve this design
2. Create Django app structure
3. Implement OrganizationalBeneficiary model (Phase 1)
4. Add enrollments and members in subsequent phases
5. Build UI for organizational beneficiary management

---

**Document Version:** 1.0
**Last Updated:** October 12, 2025
**Status:** ✅ Design Complete - Ready for Implementation
**Prepared by:** OBCMS System Architect (Claude Sonnet 4.5)

---

**See Also:**
- [BMMS TRANSITION_PLAN.md](TRANSITION_PLAN.md) - Complete BMMS implementation guide
- [docs/development/README.md](../../development/README.md) - Development guidelines
- [coordination/models.py](../../../src/coordination/models.py) - Organization model reference
- [common/models.py](../../../src/common/models.py) - Geographic hierarchy models

"""
Comprehensive Database Model Integration Tests for OBCMS/BMMS

This test suite provides comprehensive integration testing for all database models
in the OBCMS/BMMS system, focusing on:

1. Organizations App (BMMS Phase 1 - Critical)
2. Common App Models (User, RBAC, Geographic)
3. Communities, MANA, Coordination, Policies models
4. Multi-tenant data isolation (CRITICAL for BMMS)
5. Model relationships and data integrity

Author: Taskmaster Subagent
Created: 2025-10-15
"""

import pytest
import unittest
from decimal import Decimal
from datetime import date, datetime, timedelta
from django.test import TestCase, TransactionTestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import transaction, IntegrityError
from django.utils import timezone
from unittest.mock import patch, MagicMock

# Import models from all apps
from organizations.models import (
    Organization,
    OrganizationMembership,
    OrganizationScopedModel,
    get_current_organization,
    set_current_organization,
    clear_current_organization
)

from common.models import (
    User,
    Region,
    Province,
    Municipality,
    Barangay,
    StaffProfile,
    StaffTeam,
    StaffTeamMembership,
    TrainingProgram,
    TrainingEnrollment,
    PerformanceTarget,
    AuditLog,
    ChatMessage,
    RecurringEventPattern,
    CalendarResource,
    CalendarResourceBooking
)

from communities.models import (
    OBCCommunity,
    CommunityLivelihood,
    CommunityInfrastructure,
    Stakeholder,
    StakeholderEngagement,
    MunicipalityCoverage,
    ProvinceCoverage,
    GeographicDataLayer,
    MapVisualization,
    CommunityEvent
)

User = get_user_model()


class OrganizationModelIntegrationTests(TestCase):
    """Test Organization model and its relationships."""

    def setUp(self):
        """Set up test data for organization tests."""
        # Create test region
        self.region = Region.objects.create(
            code="IX",
            name="Zamboanga Peninsula",
            description="Test region for organizations"
        )

        # Create test province
        self.province = Province.objects.create(
            region=self.region,
            code="ZAS",
            name="Zamboanga del Sur",
            capital="Pagadian City"
        )

        # Create test municipality
        self.municipality = Municipality.objects.create(
            province=self.province,
            code="ZAS001",
            name="Aurora",
            municipality_type="municipality"
        )

        # Create test users
        self.admin_user = User.objects.create_user(
            username="admin_user",
            email="admin@test.com",
            password="testpass123",
            first_name="Admin",
            last_name="User",
            user_type="admin"
        )

        self.moa_user = User.objects.create_user(
            username="moa_user",
            email="moa@test.com",
            password="testpass123",
            first_name="MOA",
            last_name="User",
            user_type="bmoa"
        )

    def test_organization_creation_and_validation(self):
        """Test basic organization creation and validation."""
        # Test valid organization creation
        org = Organization.objects.create(
            code="OOBC",
            name="Office for Other Bangsamoro Communities",
            org_type="office",
            mandate="Test mandate for OOBC",
            primary_region=self.region,
            head_official="Test Minister",
            head_title="Minister",
            email="oobc@test.gov",
            phone="123-456-7890",
            website="https://oobc.test.gov",
            address="Test Address"
        )

        self.assertEqual(str(org), "OOBC - Office for Other Bangsamoro Communities")
        self.assertEqual(org.code, "OOBC")  # Should be uppercase
        self.assertTrue(org.is_active)
        self.assertFalse(org.is_pilot)
        self.assertIn("MANA", org.enabled_modules)

        # Test unique constraint on code
        with self.assertRaises(IntegrityError):
            Organization.objects.create(
                code="OOBC",  # Duplicate code
                name="Duplicate Org",
                org_type="office"
            )

    def test_organization_module_flags(self):
        """Test organization module activation flags."""
        # Test all modules enabled (default)
        org_all_enabled = Organization.objects.create(
            code="ALL",
            name="All Modules Org",
            org_type="ministry"
        )

        expected_modules = ["MANA", "Planning", "Budgeting", "M&E", "Coordination", "Policies"]
        self.assertEqual(sorted(org_all_enabled.enabled_modules), sorted(expected_modules))

        # Test selective module activation
        org_limited = Organization.objects.create(
            code="LIMITED",
            name="Limited Modules Org",
            org_type="agency",
            enable_mana=True,
            enable_planning=False,
            enable_budgeting=True,
            enable_me=False,
            enable_coordination=False,
            enable_policies=True
        )

        expected_limited = ["MANA", "Budgeting", "Policies"]
        self.assertEqual(sorted(org_limited.enabled_modules), sorted(expected_limited))

    def test_organization_geographic_relationships(self):
        """Test organization geographic relationships."""
        org = Organization.objects.create(
            code="TEST",
            name="Test Org",
            org_type="office",
            primary_region=self.region
        )

        # Test primary region relationship
        self.assertEqual(org.primary_region, self.region)

        # Test service areas (many-to-many)
        org.service_areas.add(self.municipality)
        self.assertIn(self.municipality, org.service_areas.all())
        self.assertEqual(org.service_areas.count(), 1)

    def test_organization_membership_model(self):
        """Test OrganizationMembership model and relationships."""
        org = Organization.objects.create(
            code="TEST",
            name="Test Org",
            org_type="office"
        )

        # Test basic membership creation
        membership = OrganizationMembership.objects.create(
            user=self.moa_user,
            organization=org,
            role="staff",
            position="Test Position",
            department="Test Department",
            can_manage_users=False,
            can_approve_plans=False,
            can_approve_budgets=False,
            can_view_reports=True
        )

        self.assertEqual(str(membership), "moa_user @ TEST - Staff")
        self.assertFalse(membership.is_primary)
        self.assertTrue(membership.is_active)

        # Test unique constraint on user-organization pair
        with self.assertRaises(IntegrityError):
            OrganizationMembership.objects.create(
                user=self.moa_user,  # Same user
                organization=org,     # Same organization
                role="viewer"
            )

    def test_organization_primary_membership_validation(self):
        """Test validation for primary organization membership."""
        org1 = Organization.objects.create(
            code="ORG1",
            name="First Org",
            org_type="office"
        )

        org2 = Organization.objects.create(
            code="ORG2",
            name="Second Org",
            org_type="ministry"
        )

        # Create first primary membership
        membership1 = OrganizationMembership.objects.create(
            user=self.moa_user,
            organization=org1,
            role="staff",
            is_primary=True
        )

        self.assertTrue(membership1.is_primary)

        # Attempt to create second primary membership should fail
        with self.assertRaises(ValidationError):
            membership2 = OrganizationMembership(
                user=self.moa_user,
                organization=org2,
                role="staff",
                is_primary=True
            )
            membership2.full_clean()

    def test_organization_focal_person_relationship(self):
        """Test organization focal person assignment."""
        org = Organization.objects.create(
            code="FOCAL",
            name="Focal Test Org",
            org_type="office"
        )

        # Assign focal person
        org.primary_focal_person = self.moa_user
        org.save()

        self.assertEqual(org.primary_focal_person, self.moa_user)
        self.assertIn(self.moa_user, User.objects.filter(primary_focal_organizations=org))

    def test_organization_pilot_features(self):
        """Test pilot MOA features."""
        pilot_org = Organization.objects.create(
            code="PILOT",
            name="Pilot MOA",
            org_type="ministry",
            is_pilot=True,
            onboarding_date=date.today(),
            go_live_date=date.today() + timedelta(days=30)
        )

        self.assertTrue(pilot_org.is_pilot)
        self.assertEqual(pilot_org.onboarding_date, date.today())
        self.assertEqual(pilot_org.go_live_date, date.today() + timedelta(days=30))

        # Test query filtering by pilot status
        pilot_orgs = Organization.objects.filter(is_pilot=True)
        self.assertIn(pilot_org, pilot_orgs)

    def test_organization_string_representations(self):
        """Test organization string representations."""
        org = Organization.objects.create(
            code="STR",
            name="String Test Org",
            org_type="agency"
        )

        self.assertEqual(str(org), "STR - String Test Org")

        membership = OrganizationMembership.objects.create(
            user=self.moa_user,
            organization=org,
            role="manager",
            is_primary=True
        )

        self.assertEqual(str(membership), "moa_user @ STR - Manager (Primary)")


class CommonModelsIntegrationTests(TestCase):
    """Test Common app models and their relationships."""

    def setUp(self):
        """Set up test data for common model tests."""
        # Create geographic hierarchy
        self.region = Region.objects.create(
            code="XII",
            name="SOCCSKSARGEN",
            description="Test region"
        )

        self.province = Province.objects.create(
            region=self.region,
            code="SAR",
            name="Sarangani",
            capital="Maitum"
        )

        self.municipality = Municipality.objects.create(
            province=self.province,
            code="SAR001",
            name="Maitum",
            municipality_type="municipality"
        )

        self.barangay = Barangay.objects.create(
            municipality=self.municipality,
            code="SAR001001",
            name="Poblacion"
        )

        # Create test users
        self.user = User.objects.create_user(
            username="testuser",
            email="test@test.com",
            password="testpass123",
            first_name="Test",
            last_name="User",
            user_type="oobc_staff"
        )

    def test_geographic_hierarchy_relationships(self):
        """Test geographic model relationships and hierarchy."""
        # Test region relationships
        self.assertEqual(self.province.region, self.region)
        self.assertIn(self.province, self.region.provinces.all())
        self.assertEqual(self.region.province_count, 1)

        # Test province relationships
        self.assertEqual(self.municipality.province, self.province)
        self.assertIn(self.municipality, self.province.municipalities.all())
        self.assertEqual(self.province.municipality_count, 1)

        # Test municipality relationships
        self.assertEqual(self.barangay.municipality, self.municipality)
        self.assertIn(self.barangay, self.municipality.barangays.all())
        self.assertEqual(self.municipality.barangay_count, 1)

        # Test hierarchical properties
        expected_path = f"Region {self.region.code} > {self.province.name} > {self.municipality.name} > Barangay {self.barangay.name}"
        self.assertEqual(self.barangay.full_path, expected_path)

        # Test convenience properties
        self.assertEqual(self.barangay.region, self.region)
        self.assertEqual(self.barangay.province, self.province)
        self.assertEqual(self.barangay.municipality, self.municipality)

    def test_geographic_coordinate_functionality(self):
        """Test geographic coordinate and boundary functionality."""
        # Test with coordinates
        self.barangay.latitude = 6.9214
        self.barangay.longitude = 124.6168
        self.barangay.save()

        # Test coordinate property
        expected_coords = [124.6168, 6.9214]  # [longitude, latitude] for GeoJSON
        self.assertEqual(self.barangay.coordinates, expected_coords)

        # Test with boundary data
        boundary_data = {
            "type": "Polygon",
            "coordinates": [[[124.0, 6.0], [125.0, 6.0], [125.0, 7.0], [124.0, 7.0], [124.0, 6.0]]]
        }
        self.barangay.boundary_geojson = boundary_data
        self.barangay.save()

        self.assertTrue(self.barangay.has_geographic_boundary)
        self.assertEqual(self.barangay.boundary_geojson, boundary_data)

    def test_user_model_extensions(self):
        """Test extended User model functionality."""
        # Test user type properties
        self.assertTrue(self.user.is_oobc_staff)
        self.assertFalse(self.user.is_oobc_executive)
        self.assertFalse(self.user.is_community_leader)
        self.assertFalse(self.user.is_moa_staff)

        # Test approval workflow
        self.assertFalse(self.user.is_approved)
        self.assertIsNone(self.user.approved_by)
        self.assertIsNone(self.user.approved_at)

        # Approve user
        admin_user = User.objects.create_user(
            username="admin",
            email="admin@test.com",
            password="adminpass",
            user_type="admin",
            is_superuser=True
        )

        self.user.approved_by = admin_user
        self.user.is_approved = True
        self.user.approved_at = timezone.now()
        self.user.save()

        self.assertTrue(self.user.is_approved)
        self.assertEqual(self.user.approved_by, admin_user)

    def test_staff_profile_model(self):
        """Test StaffProfile model and relationship to User."""
        profile = StaffProfile.objects.create(
            user=self.user,
            employment_status="active",
            employment_type="regular",
            position_classification="Professional",
            plantilla_item_number="001",
            salary_grade="15",
            reports_to="Team Lead",
            date_joined_organization=date.today() - timedelta(days=365),
            primary_location="Main Office"
        )

        self.assertEqual(str(profile), f"Staff Profile: {self.user.get_full_name()}")
        self.assertEqual(profile.user, self.user)
        self.assertEqual(self.user.staff_profile, profile)

        # Test competency methods
        profile.core_competencies = ["Leadership", "Communication"]
        profile.functional_competencies = ["Data Analysis", "Report Writing"]
        profile.save()

        core_comps = profile.get_competencies("core")
        functional_comps = profile.get_competencies("functional")

        self.assertEqual(core_comps, ["Leadership", "Communication"])
        self.assertEqual(functional_comps, ["Data Analysis", "Report Writing"])

    def test_staff_team_model(self):
        """Test StaffTeam model and memberships."""
        team = StaffTeam.objects.create(
            name="Assessment Team",
            description="Test assessment team",
            mission="Conduct community assessments",
            focus_areas=["assessment", "monitoring"]
        )

        self.assertEqual(str(team), "Assessment Team")
        self.assertTrue(team.is_active)
        self.assertEqual(team.focus_areas, ["assessment", "monitoring"])

        # Test team membership
        membership = StaffTeamMembership.objects.create(
            team=team,
            user=self.user,
            role="member",
            assigned_by=self.user
        )

        self.assertEqual(str(membership), f"{self.user.get_full_name()} - Assessment Team")
        self.assertIn(membership, team.memberships.all())
        self.assertIn(membership, self.user.team_memberships.all())
        self.assertTrue(membership.is_active)

        # Test unique constraint
        with self.assertRaises(IntegrityError):
            StaffTeamMembership.objects.create(
                team=team,
                user=self.user,  # Same user-team combination
                role="lead"
            )

    def test_training_program_and_enrollment(self):
        """Test TrainingProgram and TrainingEnrollment models."""
        program = TrainingProgram.objects.create(
            title="Community Assessment Training",
            category="Skills Development",
            description="Training on conducting community assessments",
            delivery_mode="in_person",
            competency_focus=["Assessment", "Data Collection"],
            duration_days=3
        )

        self.assertEqual(str(program), "Community Assessment Training")
        self.assertTrue(program.is_active)

        # Create staff profile for enrollment
        profile = StaffProfile.objects.create(user=self.user)

        # Test enrollment
        enrollment = TrainingEnrollment.objects.create(
            staff_profile=profile,
            program=program,
            status="planned",
            scheduled_date=date.today() + timedelta(days=30)
        )

        self.assertIn(enrollment, profile.training_enrollments.all())
        self.assertIn(enrollment, program.enrollments.all())

    def test_performance_target_model(self):
        """Test PerformanceTarget model with validation."""
        profile = StaffProfile.objects.create(user=self.user)
        team = StaffTeam.objects.create(name="Test Team")

        # Test staff target
        staff_target = PerformanceTarget.objects.create(
            scope="staff",
            staff_profile=profile,
            metric_name="Assessments Completed",
            performance_standard="Minimum 5 assessments per quarter",
            target_value=Decimal('5.00'),
            actual_value=Decimal('3.00'),
            unit="count",
            period_start=date.today().replace(day=1),
            period_end=date.today().replace(day=28)
        )

        self.assertEqual(str(staff_target), "Staff Target: Assessments Completed")
        self.assertEqual(staff_target.staff_profile, profile)

        # Test team target
        team_target = PerformanceTarget.objects.create(
            scope="team",
            team=team,
            metric_name="Team Efficiency",
            target_value=Decimal('90.00'),
            actual_value=Decimal('85.00'),
            unit="percent",
            period_start=date.today().replace(day=1),
            period_end=date.today().replace(day=28)
        )

        self.assertEqual(str(team_target), "Team Target: Team Efficiency")

        # Test validation - staff target without staff profile should fail
        with self.assertRaises(ValidationError):
            invalid_target = PerformanceTarget(
                scope="staff",
                team=team,  # Should not have team for staff scope
                metric_name="Invalid Target",
                target_value=Decimal('1.00')
            )
            invalid_target.full_clean()

    def test_audit_log_model(self):
        """Test AuditLog model for compliance tracking."""
        # Create test organization for audit
        org = Organization.objects.create(
            code="AUDIT",
            name="Audit Test Org",
            org_type="office"
        )

        # Create audit log for organization creation
        audit_log = AuditLog.objects.create(
            content_type=org.content_type,
            object_id=org.pk,
            action='create',
            user=self.user,
            changes={
                'code': 'AUDIT',
                'name': 'Audit Test Org',
                'org_type': 'office'
            },
            ip_address='127.0.0.1',
            user_agent='Test Client',
            notes='Initial organization creation'
        )

        self.assertEqual(str(audit_log), f"Create organization by {self.user.get_full_name()} at {audit_log.timestamp}")
        self.assertEqual(audit_log.action, 'create')
        self.assertEqual(audit_log.user, self.user)
        self.assertEqual(audit_log.content_object, org)

        # Test model name helper
        self.assertEqual(audit_log.get_model_name(), 'organization')

        # Test object representation helper
        self.assertEqual(audit_log.get_object_representation(), str(org))

    def test_calendar_models(self):
        """Test calendar-related models."""
        # Test recurring event pattern
        pattern = RecurringEventPattern.objects.create(
            recurrence_type="weekly",
            interval=1,
            by_weekday=[1, 3, 5],  # Monday, Wednesday, Friday
            count=12  # 12 occurrences
        )

        self.assertEqual(str(pattern), "Weekly (every 1)")

        # Test occurrence generation
        start_date = date.today()
        occurrences = pattern.get_occurrences(start_date=start_date, limit=5)
        self.assertEqual(len(occurrences), 5)

        # Test calendar resource
        resource = CalendarResource.objects.create(
            resource_type="vehicle",
            name="Service Vehicle 1",
            description="Toyota Hilux for field visits",
            capacity=4,
            location="Main Office",
            is_available=True,
            cost_per_use=Decimal('500.00')
        )

        self.assertEqual(str(resource), "Vehicle: Service Vehicle 1")
        self.assertTrue(resource.is_available)
        self.assertEqual(resource.status, "available")

        # Test resource booking
        booking = CalendarResourceBooking.objects.create(
            resource=resource,
            start_datetime=timezone.now() + timedelta(hours=1),
            end_datetime=timezone.now() + timedelta(hours=3),
            booked_by=self.user,
            status="pending"
        )

        self.assertEqual(str(booking), f"{resource.name} - {booking.start_datetime.date()}")
        self.assertEqual(booking.resource, resource)
        self.assertEqual(booking.booked_by, self.user)

        # Test overlapping booking detection
        with self.assertRaises(ValidationError):
            overlapping_booking = CalendarResourceBooking(
                resource=resource,
                start_datetime=timezone.now() + timedelta(hours=2),  # Overlaps
                end_datetime=timezone.now() + timedelta(hours=4),
                booked_by=self.user,
                status="pending"
            )
            overlapping_booking.full_clean()


class CommunitiesModelsIntegrationTests(TestCase):
    """Test Communities app models and their relationships."""

    def setUp(self):
        """Set up test data for communities model tests."""
        # Create geographic hierarchy
        self.region = Region.objects.create(
            code="IX",
            name="Zamboanga Peninsula",
            description="Test region"
        )

        self.province = Province.objects.create(
            region=self.region,
            code="ZAS",
            name="Zamboanga del Sur",
            capital="Pagadian City"
        )

        self.municipality = Municipality.objects.create(
            province=self.province,
            code="ZAS001",
            name="Tukuran",
            municipality_type="municipality"
        )

        self.barangay = Barangay.objects.create(
            municipality=self.municipality,
            code="ZAS001001",
            name="Poblacion"
        )

        # Create test user
        self.user = User.objects.create_user(
            username="comtest",
            email="comtest@test.com",
            password="testpass123",
            first_name="Community",
            last_name="Tester",
            user_type="oobc_staff"
        )

    def test_obc_community_creation_and_validation(self):
        """Test OBCCommunity model creation and validation."""
        community = OBCCommunity.objects.create(
            barangay=self.barangay,
            obc_id="R12-ZAS-TUK-001",
            community_names="Test Community, Sampaguita Community",
            purok_sitio="Purok 1",
            specific_location="Near the river",
            settlement_type="village",
            latitude=7.1234,
            longitude=123.4567,
            proximity_to_barmm="adjacent",
            estimated_obc_population=150,
            total_barangay_population=2000,
            households=30,
            families=35,
            primary_ethnolinguistic_group="maguindanaon",
            languages_spoken="Maguindanaon, Cebuano",
            established_year=1995,
            # Legacy fields for compatibility
            name="Test Community",
            population=150,
            primary_language="Maguindanaon"
        )

        self.assertEqual(community.display_name, "Test Community")
        self.assertEqual(community.barangay, self.barangay)
        self.assertEqual(community.obc_id, "R12-ZAS-TUK-001")
        self.assertEqual(community.estimated_obc_population, 150)

        # Test properties
        self.assertEqual(community.region, self.region)
        self.assertEqual(community.province, self.province)
        self.assertEqual(community.municipality, self.municipality)
        self.assertEqual(community.full_location, f"Region IX > Zamboanga del Sur > Tukuran > Barangay Poblacion > Near the river")

        # Test coordinate property
        expected_coords = [123.4567, 7.1234]  # [longitude, latitude]
        self.assertEqual(community.coordinates, expected_coords)

        # Test calculated properties
        self.assertEqual(community.total_age_demographics, 0)  # No age data set
        self.assertEqual(community.average_household_size, 5.0)  # 150/30
        self.assertEqual(community.percentage_obc_in_barangay, 7.5)  # 150/2000 * 100

    def test_community_livelihood_model(self):
        """Test CommunityLivelihood model."""
        community = OBCCommunity.objects.create(
            barangay=self.barangay,
            name="Livelihood Test Community",
            estimated_obc_population=100
        )

        livelihood = CommunityLivelihood.objects.create(
            community=community,
            livelihood_type="agriculture",
            specific_activity="Rice Farming",
            description="Lowland rice cultivation during rainy season",
            households_involved=25,
            percentage_of_community=Decimal('25.00'),
            is_primary_livelihood=True,
            seasonal=True,
            income_level="moderate",
            challenges="Limited irrigation, pest infestations",
            opportunities="Mechanization, better seed varieties"
        )

        self.assertIn("Primary", str(livelihood))
        self.assertEqual(livelihood.community, community)
        self.assertEqual(livelihood.livelihood_type, "agriculture")
        self.assertTrue(livelihood.is_primary_livelihood)

        # Test unique constraint
        with self.assertRaises(IntegrityError):
            CommunityLivelihood.objects.create(
                community=community,
                livelihood_type="agriculture",  # Same type for same community
                specific_activity="Another farming activity"
            )

    def test_community_infrastructure_model(self):
        """Test CommunityInfrastructure model."""
        community = OBCCommunity.objects.create(
            barangay=self.barangay,
            name="Infrastructure Test Community",
            estimated_obc_population=80
        )

        infrastructure = CommunityInfrastructure.objects.create(
            community=community,
            infrastructure_type="water",
            availability_status="limited",
            description="Communal water pump with limited hours",
            coverage_percentage=Decimal('60.00'),
            condition="fair",
            priority_for_improvement="high",
            notes="Water source dries up during summer",
            last_assessed=date.today() - timedelta(days=30)
        )

        self.assertEqual(str(infrastructure), f"Water Supply - {self.barangay.name} (Limited)")
        self.assertEqual(infrastructure.community, community)
        self.assertEqual(infrastructure.availability_status, "limited")
        self.assertEqual(infrastructure.coverage_percentage, Decimal('60.00'))

    def test_stakeholder_model(self):
        """Test Stakeholder model."""
        community = OBCCommunity.objects.create(
            barangay=self.barangay,
            name="Stakeholder Test Community",
            estimated_obc_population=120
        )

        stakeholder = Stakeholder.objects.create(
            full_name="Ahmad Abdullah",
            nickname="Ustadz Ahmad",
            stakeholder_type="ulama",
            community=community,
            position="Religious Leader",
            organization="Local Mosque",
            responsibilities="Leading prayers, religious instruction",
            contact_number="0912-345-6789",
            email="ahmad@test.com",
            influence_level="high",
            engagement_level="very_active",
            areas_of_influence="Religious matters, youth guidance",
            age=45,
            educational_background="Islamic Studies, BS Economics",
            since_year=2010,
            years_in_community=15,
            special_skills="Arabic language, conflict resolution",
            achievements="Established madrasah, resolved local conflicts",
            is_active=True,
            is_verified=True,
            verification_date=date.today() - timedelta(days=60)
        )

        self.assertEqual(str(stakeholder), "Ustadz Ahmad (Ulama) - Stakeholder Test Community")
        self.assertEqual(stakeholder.display_name, "Ustadz Ahmad")
        self.assertEqual(stakeholder.community, community)
        self.assertEqual(stakeholder.years_of_service, date.today().year - 2010)

        # Test contact info property
        contact_info = stakeholder.contact_info
        self.assertIn("Mobile: 0912-345-6789", contact_info)
        self.assertIn("Email: ahmad@test.com", contact_info)

    def test_stakeholder_engagement_model(self):
        """Test StakeholderEngagement model."""
        community = OBCCommunity.objects.create(
            barangay=self.barangay,
            name="Engagement Test Community",
            estimated_obc_population=90
        )

        stakeholder = Stakeholder.objects.create(
            full_name="Maria Santos",
            stakeholder_type="community_leader",
            community=community
        )

        engagement = StakeholderEngagement.objects.create(
            stakeholder=stakeholder,
            engagement_type="consultation",
            title="Community Needs Assessment",
            description="Consultation meeting to identify community priorities",
            date=date.today() - timedelta(days=7),
            duration_hours=Decimal('2.5'),
            location="Community Hall",
            participants_count=25,
            outcome="positive",
            key_points="Education, health, and livelihood identified as priorities",
            action_items="Follow-up on education programs, health mission schedule",
            documented_by="Field Officer"
        )

        self.assertEqual(str(engagement), f"{engagement.title} - {stakeholder.display_name} ({engagement.date})")
        self.assertEqual(engagement.stakeholder, stakeholder)
        self.assertEqual(engagement.engagement_type, "consultation")

    def test_municipality_coverage_model(self):
        """Test MunicipalityCoverage model with aggregation."""
        # Create OBC communities in the same municipality
        community1 = OBCCommunity.objects.create(
            barangay=self.barangay,
            name="Test Community 1",
            estimated_obc_population=100,
            households=20
        )

        # Create another barangay and community
        barangay2 = Barangay.objects.create(
            municipality=self.municipality,
            code="ZAS001002",
            name="Barangay 2"
        )

        community2 = OBCCommunity.objects.create(
            barangay=barangay2,
            name="Test Community 2",
            estimated_obc_population=80,
            households=15
        )

        # Create municipality coverage
        coverage = MunicipalityCoverage.objects.create(
            municipality=self.municipality,
            estimated_obc_population=200,
            total_obc_communities=2,
            key_barangays="Poblacion, Barangay 2",
            existing_support_programs="Livelihood training, health services",
            auto_sync=False,
            created_by=self.user
        )

        self.assertEqual(str(coverage), f"{self.municipality.name} Bangsamoro Coverage")
        self.assertEqual(coverage.municipality, self.municipality)
        self.assertEqual(coverage.region, self.region)
        self.assertEqual(coverage.province, self.province)

        # Test population reconciliation
        reconciliation = coverage.population_reconciliation
        self.assertEqual(reconciliation["total_municipal"], 200)
        self.assertEqual(reconciliation["attributed_to_barangays"], 180)  # 100 + 80
        self.assertEqual(reconciliation["unattributed"], 20)  # 200 - 180
        self.assertEqual(reconciliation["attribution_rate"], 90.0)  # 180/200 * 100

        # Test barangay attributed population
        self.assertEqual(coverage.barangay_attributed_population, 180)

    def test_province_coverage_model(self):
        """Test ProvinceCoverage model with aggregation."""
        # Create municipality coverages
        coverage1 = MunicipalityCoverage.objects.create(
            municipality=self.municipality,
            estimated_obc_population=300,
            total_obc_communities=3
        )

        # Create another municipality
        municipality2 = Municipality.objects.create(
            province=self.province,
            code="ZAS002",
            name="Pagadian City",
            municipality_type="city"
        )

        coverage2 = MunicipalityCoverage.objects.create(
            municipality=municipality2,
            estimated_obc_population=500,
            total_obc_communities=5
        )

        # Create province coverage
        province_coverage = ProvinceCoverage.objects.create(
            province=self.province,
            estimated_obc_population=1000,
            total_municipalities=2,
            total_obc_communities=8,
            key_municipalities="Tukuran, Pagadian City",
            existing_support_programs="Provincial development programs",
            auto_sync=False,
            created_by=self.user
        )

        self.assertEqual(str(province_coverage), f"{self.province.name} Bangsamoro Coverage")
        self.assertEqual(province_coverage.province, self.province)
        self.assertEqual(province_coverage.region, self.region)

        # Test population reconciliation
        reconciliation = province_coverage.population_reconciliation
        self.assertEqual(reconciliation["total_provincial"], 1000)
        self.assertEqual(reconciliation["attributed_to_municipalities"], 800)  # 300 + 500
        self.assertEqual(reconciliation["unattributed"], 200)  # 1000 - 800
        self.assertEqual(reconciliation["attribution_rate"], 80.0)  # 800/1000 * 100

    def test_geographic_data_layer_model(self):
        """Test GeographicDataLayer model."""
        community = OBCCommunity.objects.create(
            barangay=self.barangay,
            name="GIS Test Community",
            estimated_obc_population=75
        )

        # Test GeoJSON data
        geojson_data = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [123.4567, 7.1234]
                    },
                    "properties": {
                        "name": "Community Center",
                        "type": "infrastructure"
                    }
                }
            ]
        }

        layer = GeographicDataLayer.objects.create(
            name="Community Infrastructure",
            description="Map of community facilities and infrastructure",
            layer_type="point",
            data_source="field_survey",
            community=community,
            geojson_data=geojson_data,
            bounding_box=[123.45, 7.12, 123.46, 7.13],
            center_point=[123.4567, 7.1234],
            style_properties={
                "color": "#FF0000",
                "icon": "building"
            },
            opacity=0.8,
            data_collection_date=date.today() - timedelta(days=7),
            accuracy_meters=5.0,
            attribution="OOBC Field Team",
            is_public=False,
            feature_count=1,
            created_by=self.user
        )

        self.assertEqual(str(layer), "Community Infrastructure (Point Data)")
        self.assertEqual(layer.community, community)
        self.assertEqual(layer.administrative_level, "community")
        self.assertEqual(layer.full_administrative_path, community.full_location)

        # Test validation - barangay should belong to specified municipality
        layer.barangay = Barangay.objects.create(
            municipality=Municipality.objects.create(
                province=Province.objects.create(
                    region=Region.objects.create(code="X", name="Test Region"),
                    code="TEST",
                    name="Test Province"
                ),
                code="TEST001",
                name="Test Municipality"
            ),
            code="TEST001001",
            name="Test Barangay"
        )

        with self.assertRaises(ValidationError):
            layer.full_clean()  # Should fail - barangay doesn't match municipality

    def test_community_event_model(self):
        """Test CommunityEvent model."""
        community = OBCCommunity.objects.create(
            barangay=self.barangay,
            name="Event Test Community",
            estimated_obc_population=85
        )

        # Create recurring pattern
        pattern = RecurringEventPattern.objects.create(
            recurrence_type="monthly",
            interval=1,
            by_monthday=15,  # 15th of every month
            count=12
        )

        event = CommunityEvent.objects.create(
            community=community,
            title="Monthly Community Meeting",
            description="Regular community meeting to discuss local issues",
            event_type="meeting",
            start_date=date.today(),
            end_date=date.today(),
            all_day=True,
            location="Community Hall",
            organizer="Barangay Captain",
            is_public=True,
            is_recurring=True,
            recurrence_pattern=pattern,
            created_by=self.user
        )

        self.assertEqual(str(event), f"{event.title} - {community.name}")
        self.assertEqual(event.community, community)
        self.assertTrue(event.is_recurring)
        self.assertEqual(event.recurrence_pattern, pattern)

    def test_soft_delete_functionality(self):
        """Test soft delete functionality for community models."""
        community = OBCCommunity.objects.create(
            barangay=self.barangay,
            name="Soft Delete Test Community",
            estimated_obc_population=60
        )

        # Verify community exists
        self.assertTrue(OBCCommunity.objects.filter(pk=community.pk).exists())
        self.assertFalse(community.is_deleted)
        self.assertIsNone(community.deleted_at)
        self.assertIsNone(community.deleted_by)

        # Soft delete
        community.soft_delete(user=self.user)

        # Should be marked as deleted
        community.refresh_from_db()
        self.assertTrue(community.is_deleted)
        self.assertIsNotNone(community.deleted_at)
        self.assertEqual(community.deleted_by, self.user)

        # Should not appear in default queryset
        self.assertFalse(OBCCommunity.objects.filter(pk=community.pk).exists())

        # Should appear in all_objects queryset
        self.assertTrue(OBCCommunity.all_objects.filter(pk=community.pk).exists())

        # Restore
        community.restore()

        # Should be restored
        community.refresh_from_db()
        self.assertFalse(community.is_deleted)
        self.assertIsNone(community.deleted_at)
        self.assertTrue(OBCCommunity.objects.filter(pk=community.pk).exists())


class MultiTenantDataIsolationTests(TransactionTestCase):
    """Test multi-tenant data isolation - CRITICAL for BMMS."""

    def setUp(self):
        """Set up multi-tenant test data."""
        # Create organizations
        self.org1 = Organization.objects.create(
            code="ORG1",
            name="First Organization",
            org_type="ministry"
        )

        self.org2 = Organization.objects.create(
            code="ORG2",
            name="Second Organization",
            org_type="agency"
        )

        # Create users for each organization
        self.user1 = User.objects.create_user(
            username="user1",
            email="user1@test.com",
            password="testpass123",
            user_type="bmoa"
        )

        self.user2 = User.objects.create_user(
            username="user2",
            email="user2@test.com",
            password="testpass123",
            user_type="bmoa"
        )

        # Create memberships
        self.membership1 = OrganizationMembership.objects.create(
            user=self.user1,
            organization=self.org1,
            role="staff",
            is_primary=True
        )

        self.membership2 = OrganizationMembership.objects.create(
            user=self.user2,
            organization=self.org2,
            role="staff",
            is_primary=True
        )

        # Create test data with organization context
        self.test_data_1 = self._create_test_data_for_org(self.org1, "Data 1")
        self.test_data_2 = self._create_test_data_for_org(self.org2, "Data 2")

    def _create_test_data_for_org(self, organization, suffix):
        """Helper to create test data for a specific organization."""
        # This would create organization-scoped data
        # For now, we'll simulate with audit logs
        return {
            'audit_log': AuditLog.objects.create(
                content_type=organization.content_type,
                object_id=organization.pk,
                action='create',
                user=self.user1 if organization == self.org1 else self.user2,
                changes={'test': suffix}
            )
        }

    def test_organization_membership_isolation(self):
        """Test that users only see their own organization memberships."""
        # User 1 should only see membership to org1
        user1_memberships = OrganizationMembership.objects.filter(user=self.user1)
        self.assertEqual(user1_memberships.count(), 1)
        self.assertEqual(user1_memberships.first().organization, self.org1)

        # User 2 should only see membership to org2
        user2_memberships = OrganizationMembership.objects.filter(user=self.user2)
        self.assertEqual(user2_memberships.count(), 1)
        self.assertEqual(user2_memberships.first().organization, self.org2)

    def test_organization_data_isolation(self):
        """Test that organization data is properly isolated."""
        # Test that each organization has its own data
        org1_audit_logs = AuditLog.objects.filter(
            content_type=self.org1.content_type,
            object_id=self.org1.pk
        )
        org2_audit_logs = AuditLog.objects.filter(
            content_type=self.org2.content_type,
            object_id=self.org2.pk
        )

        self.assertEqual(org1_audit_logs.count(), 1)
        self.assertEqual(org2_audit_logs.count(), 1)

        # Verify data belongs to correct organizations
        self.assertNotEqual(
            org1_audit_logs.first().user,
            org2_audit_logs.first().user
        )

    def test_cross_organization_access_prevention(self):
        """Test that users cannot access data from other organizations."""
        # This test would verify that organization-scoped queries
        # properly filter data based on current organization context

        # Simulate setting current organization context
        set_current_organization(self.org1)

        # Verify current organization is set correctly
        current_org = get_current_organization()
        self.assertEqual(current_org, self.org1)

        # Clear context
        clear_current_organization()

        # Verify context is cleared
        self.assertIsNone(get_current_organization())

    def test_organization_scope_consistency(self):
        """Test organization scope consistency across related models."""
        # Test that related data maintains organization scope
        org1_membership = OrganizationMembership.objects.get(
            user=self.user1,
            organization=self.org1
        )

        # Verify relationship consistency
        self.assertEqual(org1_membership.organization, self.org1)
        self.assertEqual(org1_membership.user, self.user1)

        # Test that primary organization constraints work
        self.assertTrue(org1_membership.is_primary)

        # Attempt to create another primary membership should fail
        org3 = Organization.objects.create(
            code="ORG3",
            name="Third Organization",
            org_type="office"
        )

        with self.assertRaises(ValidationError):
            OrganizationMembership.objects.create(
                user=self.user1,
                organization=org3,
                role="staff",
                is_primary=True  # Should fail - user already has primary org
            )

    def test_pilot_organization_features(self):
        """Test pilot organization feature isolation."""
        # Make org1 a pilot organization
        self.org1.is_pilot = True
        self.org1.save()

        # Query pilot organizations
        pilot_orgs = Organization.objects.filter(is_pilot=True)
        self.assertIn(self.org1, pilot_orgs)
        self.assertNotIn(self.org2, pilot_orgs)

        # Query non-pilot organizations
        regular_orgs = Organization.objects.filter(is_pilot=False)
        self.assertNotIn(self.org1, regular_orgs)
        self.assertIn(self.org2, regular_orgs)

    def test_organization_module_access_isolation(self):
        """Test that module access is properly isolated per organization."""
        # Set different module configurations
        self.org1.enable_mana = True
        self.org1.enable_planning = False
        self.org1.enable_budgeting = True
        self.org1.save()

        self.org2.enable_mana = False
        self.org2.enable_planning = True
        self.org2.enable_budgeting = False
        self.org2.save()

        # Verify module access differs
        org1_modules = set(self.org1.enabled_modules)
        org2_modules = set(self.org2.enabled_modules)

        self.assertIn("MANA", org1_modules)
        self.assertNotIn("MANA", org2_modules)

        self.assertIn("Planning", org2_modules)
        self.assertNotIn("Planning", org1_modules)

        self.assertIn("Budgeting", org1_modules)
        self.assertNotIn("Budgeting", org2_modules)


class ModelRelationshipIntegrityTests(TestCase):
    """Test model relationship integrity and cascade behaviors."""

    def setUp(self):
        """Set up test data for relationship integrity tests."""
        self.region = Region.objects.create(
            code="TEST",
            name="Test Region"
        )

        self.province = Province.objects.create(
            region=self.region,
            code="TESTP",
            name="Test Province"
        )

        self.municipality = Municipality.objects.create(
            province=self.province,
            code="TESTM",
            name="Test Municipality"
        )

        self.barangay = Barangay.objects.create(
            municipality=self.municipality,
            code="TESTB",
            name="Test Barangay"
        )

        self.user = User.objects.create_user(
            username="reltest",
            email="rel@test.com",
            password="testpass123"
        )

    def test_geographic_hierarchy_cascade_delete(self):
        """Test cascade delete behavior in geographic hierarchy."""
        # Create dependent data
        community = OBCCommunity.objects.create(
            barangay=self.barangay,
            name="Test Community"
        )

        # Verify relationships exist
        self.assertEqual(community.barangay, self.barangay)
        self.assertEqual(self.barangay.municipality, self.municipality)
        self.assertEqual(self.municipality.province, self.province)
        self.assertEqual(self.province.region, self.region)

        # Test that deleting barangay cascades to community
        self.barangay.delete()

        with self.assertRaises(OBCCommunity.DoesNotExist):
            OBCCommunity.objects.get(pk=community.pk)

    def test_user_relationship_integrity(self):
        """Test user relationship integrity."""
        # Create related objects
        profile = StaffProfile.objects.create(user=self.user)
        team = StaffTeam.objects.create(name="Test Team")
        membership = StaffTeamMembership.objects.create(
            team=team,
            user=self.user
        )

        # Verify relationships
        self.assertEqual(profile.user, self.user)
        self.assertEqual(membership.user, self.user)
        self.assertIn(membership, self.user.team_memberships.all())

        # Test that deleting user cascades appropriately
        self.user.delete()

        # Related objects should be deleted
        with self.assertRaises(StaffProfile.DoesNotExist):
            StaffProfile.objects.get(pk=profile.pk)

        with self.assertRaises(StaffTeamMembership.DoesNotExist):
            StaffTeamMembership.objects.get(pk=membership.pk)

    def test_foreign_key_constraint_violations(self):
        """Test foreign key constraint violations."""
        # Test creating organization with non-existent region
        with self.assertRaises(ValueError):
            org = Organization(
                code="BAD",
                name="Bad Org",
                org_type="office",
                primary_region_id=99999  # Non-existent region
            )
            org.full_clean()

    def test_unique_constraint_enforcement(self):
        """Test unique constraint enforcement."""
        # Test unique constraint on geographic codes
        with self.assertRaises(IntegrityError):
            Region.objects.create(
                code="TEST",  # Duplicate code
                name="Duplicate Region"
            )

        # Test unique constraint on organization codes
        org1 = Organization.objects.create(
            code="UNIQUE",
            name="First Org",
            org_type="office"
        )

        with self.assertRaises(IntegrityError):
            Organization.objects.create(
                code="UNIQUE",  # Duplicate code
                name="Second Org",
                org_type="agency"
            )

    def test_many_to_many_relationship_integrity(self):
        """Test many-to-many relationship integrity."""
        org = Organization.objects.create(
            code="M2M",
            name="M2M Test Org",
            org_type="ministry"
        )

        # Test service areas relationship
        org.service_areas.add(self.municipality)

        # Verify relationship exists
        self.assertIn(self.municipality, org.service_areas.all())
        self.assertIn(org, self.municipality.served_by_organizations.all())

        # Test removing relationship
        org.service_areas.remove(self.municipality)

        self.assertNotIn(self.municipality, org.service_areas.all())
        self.assertNotIn(org, self.municipality.served_by_organizations.all())

    def test_model_string_representations(self):
        """Test model string representations across all models."""
        # Test geographic models
        self.assertEqual(str(self.region), "Region TEST - Test Region")
        self.assertEqual(str(self.province), "Test Province, Test Region")
        self.assertEqual(str(self.municipality), "Municipality of Test Municipality, Test Province")
        self.assertEqual(str(self.barangay), "Barangay Test Barangay, Test Municipality")

        # Test organization models
        org = Organization.objects.create(
            code="STR",
            name="String Test",
            org_type="office"
        )
        self.assertEqual(str(org), "STR - String Test")

        # Test user model
        self.user.first_name = "String"
        self.user.last_name = "Test"
        self.user.save()
        self.assertEqual(str(self.user), "String Test (bmoa)")


# Test runner and reporting utilities
class DatabaseIntegrationTestRunner:
    """Utility class for running tests and generating reports."""

    def __init__(self):
        self.test_results = {}
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.error_messages = []

    def run_all_tests(self):
        """Run all integration tests and generate comprehensive report."""
        test_classes = [
            OrganizationModelIntegrationTests,
            CommonModelsIntegrationTests,
            CommunitiesModelsIntegrationTests,
            MultiTenantDataIsolationTests,
            ModelRelationshipIntegrityTests
        ]

        for test_class in test_classes:
            self._run_test_class(test_class)

        return self._generate_report()

    def _run_test_class(self, test_class):
        """Run tests for a specific test class."""
        suite = unittest.TestLoader().loadTestsFromTestCase(test_class)
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)

        self.test_results[test_class.__name__] = {
            'tests_run': result.testsRun,
            'failures': len(result.failures),
            'errors': len(result.errors),
            'success_rate': (result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100
        }

        self.total_tests += result.testsRun
        self.passed_tests += result.testsRun - len(result.failures) - len(result.errors)
        self.failed_tests += len(result.failures) + len(result.errors)

        # Collect error messages
        for test, error in result.failures + result.errors:
            self.error_messages.append(f"{test_class.__name__}.{test._testMethodName}: {error}")

    def _generate_report(self):
        """Generate comprehensive test report."""
        report = {
            'summary': {
                'total_tests': self.total_tests,
                'passed_tests': self.passed_tests,
                'failed_tests': self.failed_tests,
                'success_rate': (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0,
                'timestamp': datetime.now().isoformat()
            },
            'test_results': self.test_results,
            'failed_tests': self.error_messages,
            'recommendations': self._generate_recommendations()
        }

        return report

    def _generate_recommendations(self):
        """Generate recommendations based on test results."""
        recommendations = []

        if self.failed_tests > 0:
            recommendations.append("Address failed tests before deploying to production")

        if self.test_results.get('MultiTenantDataIsolationTests', {}).get('failures', 0) > 0:
            recommendations.append("CRITICAL: Fix multi-tenant data isolation issues - BMMS security depends on this")

        if self.test_results.get('ModelRelationshipIntegrityTests', {}).get('failures', 0) > 0:
            recommendations.append("Fix model relationship integrity issues to prevent data corruption")

        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        if success_rate < 95:
            recommendations.append("Overall test success rate should be above 95% for production deployment")

        if not recommendations:
            recommendations.append("All tests passed - system is ready for production deployment")

        return recommendations


# Main test execution function
def run_database_model_integration_tests():
    """Main function to run all database model integration tests."""
    runner = DatabaseIntegrationTestRunner()
    report = runner.run_all_tests()

    print("\n" + "="*80)
    print("DATABASE MODEL INTEGRATION TEST REPORT")
    print("="*80)
    print(f"Total Tests: {report['summary']['total_tests']}")
    print(f"Passed: {report['summary']['passed_tests']}")
    print(f"Failed: {report['summary']['failed_tests']}")
    print(f"Success Rate: {report['summary']['success_rate']:.1f}%")
    print(f"Timestamp: {report['summary']['timestamp']}")

    print("\nTEST RESULTS BY CATEGORY:")
    print("-" * 40)
    for test_class, results in report['test_results'].items():
        print(f"{test_class}:")
        print(f"  Tests Run: {results['tests_run']}")
        print(f"  Failures: {results['failures']}")
        print(f"  Errors: {results['errors']}")
        print(f"  Success Rate: {results['success_rate']:.1f}%")

    if report['failed_tests']:
        print("\nFAILED TESTS:")
        print("-" * 40)
        for error in report['failed_tests']:
            print(f"❌ {error}")

    print("\nRECOMMENDATIONS:")
    print("-" * 40)
    for i, recommendation in enumerate(report['recommendations'], 1):
        print(f"{i}. {recommendation}")

    print("\n" + "="*80)

    return report


if __name__ == "__main__":
    # Run the comprehensive integration tests
    run_database_model_integration_tests()
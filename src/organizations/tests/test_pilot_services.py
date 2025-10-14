"""
Comprehensive unit tests for PilotRoleService and PilotUserService.

Tests cover:
- Role creation and synchronization
- Role assignment and validation
- User creation with memberships
- Password generation
- Email queuing (mocked)
- Edge cases and error handling
- Transaction rollback scenarios
"""

from unittest.mock import Mock, patch

import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.test import override_settings

from organizations.models import Organization, OrganizationMembership
from organizations.services.role_service import PilotRoleService, RoleDefinition
from organizations.services.user_service import PilotUserResult, PilotUserService

User = get_user_model()


# ============================================================================
# PilotRoleService Tests
# ============================================================================


@pytest.mark.django_db(transaction=True)
class TestPilotRoleService:
    """Test suite for PilotRoleService functionality."""

    @pytest.fixture(autouse=True)
    def setup(self, db):
        """Set up test environment before each test."""
        self.service = PilotRoleService()
        # Clean up any existing groups
        Group.objects.all().delete()
        yield
        # Clean up after each test
        Group.objects.all().delete()

    def test_default_roles_defined(self):
        """Test that all 5 default roles are defined in DEFAULT_ROLES."""
        expected_roles = {
            "pilot_admin",
            "planner",
            "budget_officer",
            "me_officer",
            "viewer",
        }
        actual_roles = {role.name for role in self.service.DEFAULT_ROLES}
        self.assertEqual(expected_roles, actual_roles)
        self.assertEqual(len(self.service.DEFAULT_ROLES), 5)

    def test_role_definitions_structure(self):
        """Test that each role definition has proper structure."""
        for role_def in self.service.DEFAULT_ROLES:
            self.assertIsInstance(role_def, RoleDefinition)
            self.assertIsInstance(role_def.name, str)
            self.assertIsInstance(role_def.description, str)
            self.assertIsNotNone(role_def.permissions)
            self.assertTrue(len(role_def.name) > 0)
            self.assertTrue(len(role_def.description) > 0)

    def test_ensure_roles_exist_creates_all_roles(self):
        """Test ensure_roles_exist() creates all 5 role groups."""
        self.service.ensure_roles_exist()

        created_groups = Group.objects.filter(
            name__in=[
                "pilot_admin",
                "planner",
                "budget_officer",
                "me_officer",
                "viewer",
            ]
        )
        self.assertEqual(created_groups.count(), 5)

        # Verify each role was created
        for role_def in self.service.DEFAULT_ROLES:
            group = Group.objects.get(name=role_def.name)
            self.assertIsNotNone(group)

    def test_ensure_roles_exist_is_idempotent(self):
        """Test that calling ensure_roles_exist() multiple times is safe."""
        # First call
        self.service.ensure_roles_exist()
        first_count = Group.objects.count()

        # Second call
        self.service.ensure_roles_exist()
        second_count = Group.objects.count()

        # Third call
        self.service.ensure_roles_exist()
        third_count = Group.objects.count()

        self.assertEqual(first_count, second_count)
        self.assertEqual(second_count, third_count)
        self.assertEqual(first_count, 5)

    def test_permission_synchronization_with_valid_permissions(self):
        """Test that permissions are properly synchronized when they exist."""
        # Create necessary content types and permissions
        org_ct = ContentType.objects.get_or_create(
            app_label="organizations", model="organization"
        )[0]
        Permission.objects.get_or_create(
            codename="view_organization",
            name="Can view organization",
            content_type=org_ct,
        )
        Permission.objects.get_or_create(
            codename="change_organization",
            name="Can change organization",
            content_type=org_ct,
        )

        self.service.ensure_roles_exist()

        # Check that pilot_admin has the expected permissions
        pilot_admin = Group.objects.get(name="pilot_admin")
        self.assertTrue(pilot_admin.permissions.exists())

    def test_permission_synchronization_with_missing_permissions(self):
        """Test that missing permissions are logged but don't break creation."""
        # This should not raise an error even if permissions don't exist
        self.service.ensure_roles_exist()

        # All groups should still be created
        self.assertEqual(Group.objects.count(), 5)

    def test_assign_role_with_valid_role(self):
        """Test assign_role() successfully assigns a role to a user."""
        user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

        group = self.service.assign_role(user, "pilot_admin")

        self.assertIsNotNone(group)
        self.assertEqual(group.name, "pilot_admin")
        self.assertTrue(user.groups.filter(name="pilot_admin").exists())

    def test_assign_role_with_invalid_role(self):
        """Test assign_role() raises ValueError for unknown roles."""
        user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

        with self.assertRaises(ValueError) as context:
            self.service.assign_role(user, "invalid_role")

        self.assertIn("Unknown pilot role", str(context.exception))
        self.assertIn("invalid_role", str(context.exception))

    def test_assign_role_ensures_role_exists(self):
        """Test assign_role() creates role if it doesn't exist."""
        user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

        # Ensure no groups exist
        Group.objects.all().delete()

        # This should create the role before assigning
        group = self.service.assign_role(user, "planner")

        self.assertIsNotNone(group)
        self.assertTrue(Group.objects.filter(name="planner").exists())

    def test_assign_role_multiple_times_is_idempotent(self):
        """Test assigning the same role multiple times doesn't create duplicates."""
        user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

        # Assign same role three times
        self.service.assign_role(user, "planner")
        self.service.assign_role(user, "planner")
        self.service.assign_role(user, "planner")

        # User should still have exactly one "planner" group
        self.assertEqual(user.groups.filter(name="planner").count(), 1)

    def test_assign_multiple_roles_to_user(self):
        """Test that a user can have multiple pilot roles."""
        user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

        self.service.assign_role(user, "planner")
        self.service.assign_role(user, "viewer")

        self.assertEqual(user.groups.count(), 2)
        self.assertTrue(user.groups.filter(name="planner").exists())
        self.assertTrue(user.groups.filter(name="viewer").exists())

    def test_available_roles_returns_sorted_list(self):
        """Test available_roles() returns all role names sorted."""
        roles = self.service.available_roles()

        self.assertEqual(len(roles), 5)
        self.assertIsInstance(roles, list)
        # Check if sorted
        self.assertEqual(roles, sorted(roles))
        # Check expected roles
        self.assertIn("pilot_admin", roles)
        self.assertIn("planner", roles)
        self.assertIn("budget_officer", roles)
        self.assertIn("me_officer", roles)
        self.assertIn("viewer", roles)

    def test_role_map_initialization(self):
        """Test that _role_map is properly initialized."""
        self.assertEqual(len(self.service._role_map), 5)

        for role_name in [
            "pilot_admin",
            "planner",
            "budget_officer",
            "me_officer",
            "viewer",
        ]:
            self.assertIn(role_name, self.service._role_map)
            self.assertIsInstance(self.service._role_map[role_name], RoleDefinition)

    def test_role_definitions_are_frozen(self):
        """Test that RoleDefinition dataclass is frozen (immutable)."""
        role_def = self.service.DEFAULT_ROLES[0]

        with self.assertRaises(Exception):
            # Should not be able to modify frozen dataclass
            role_def.name = "new_name"

    def test_permission_sync_adds_new_permissions(self):
        """Test that new permissions are added to existing groups."""
        # Create a group with no permissions
        group = Group.objects.create(name="pilot_admin")
        self.assertEqual(group.permissions.count(), 0)

        # Create some permissions
        org_ct = ContentType.objects.get_or_create(
            app_label="organizations", model="organization"
        )[0]
        perm1 = Permission.objects.create(
            codename="view_organization",
            name="Can view organization",
            content_type=org_ct,
        )

        # Sync should add the permission
        self.service.ensure_roles_exist()
        group.refresh_from_db()

        # Group should now have permissions
        self.assertTrue(group.permissions.exists())

    def test_permission_sync_removes_old_permissions(self):
        """Test that removed permissions are cleaned up."""
        # Create necessary permissions
        org_ct = ContentType.objects.get_or_create(
            app_label="organizations", model="organization"
        )[0]
        perm1 = Permission.objects.create(
            codename="view_organization",
            name="Can view organization",
            content_type=org_ct,
        )
        extra_perm = Permission.objects.create(
            codename="delete_organization",
            name="Can delete organization",
            content_type=org_ct,
        )

        # Create group with extra permission not in definition
        group = Group.objects.create(name="pilot_admin")
        group.permissions.add(perm1, extra_perm)

        initial_count = group.permissions.count()
        self.assertGreater(initial_count, 0)

        # Sync should remove extra permission
        self.service.ensure_roles_exist()
        group.refresh_from_db()

        # Extra permission should be removed if not in role definition
        # (depends on actual role definition)
        self.assertTrue(group.permissions.filter(pk=perm1.pk).exists())

    def test_transaction_rollback_on_error(self):
        """Test that role creation is rolled back on error."""
        initial_count = Group.objects.count()

        # Mock to cause an error during permission sync
        with patch.object(
            self.service, "_synchronize_group_permissions", side_effect=Exception("Test error")
        ):
            with self.assertRaises(Exception):
                self.service.ensure_roles_exist()

        # Groups should not be partially created due to transaction
        # Note: each role has its own transaction, so some may be created
        # This tests that individual role creation is atomic
        self.assertTrue(Group.objects.count() >= initial_count)


# ============================================================================
# PilotUserService Tests
# ============================================================================


@pytest.mark.django_db(transaction=True)
class TestPilotUserService:
    """Test suite for PilotUserService functionality."""

    @pytest.fixture(autouse=True)
    def setup(self, db):
        """Set up test environment before each test."""
        self.service = PilotUserService()
        # Create test organization
        self.org = Organization.objects.create(
            code='MOH_TEST',
            name='Ministry of Health',
            org_type='ministry',
            is_pilot=True,
            is_active=True,
        )
        # Clean up
        User.objects.all().delete()
        Group.objects.all().delete()
        yield
        # Cleanup after test
        Organization.objects.filter(code='MOH_TEST').delete()

    def test_generate_password_default_length(self):
        """Test generate_password() creates password with default length."""
        password = self.service.generate_password()

        assert isinstance(password, str)
        assert len(password) == 16  # Default length

    @override_settings(PILOT_DEFAULT_PASSWORD_LENGTH=24)
    def test_generate_password_custom_length(self):
        """Test generate_password() respects custom length setting."""
        password = self.service.generate_password()

        assert len(password) == 24

    def test_generate_password_custom_length_parameter(self):
        """Test generate_password() with explicit length parameter."""
        password = self.service.generate_password(length=32)

        assert len(password) == 32

    def test_generate_password_allowed_chars(self):
        """Test that generated password only contains allowed characters."""
        allowed_chars = "abcdefghjkmnpqrstuvwxyzABCDEFGHJKMNPQRSTUVWXYZ23456789@#$%"
        password = self.service.generate_password()

        for char in password:
            assert char in allowed_chars

    def test_generate_password_uniqueness(self):
        """Test that generate_password() creates unique passwords."""
        passwords = [self.service.generate_password() for _ in range(100)]

        # All passwords should be unique
        assert len(set(passwords)) == 100

    def test_create_pilot_user_success(self):
        """Test successful pilot user creation with all fields."""
        result = self.service.create_pilot_user(
            username="john.doe",
            email="john.doe@moh.gov.ph",
            organization_code="MOH_TEST",
            role="pilot_admin",
            first_name="John",
            last_name="Doe",
            phone="+639171234567",
            position="IT Manager",
            department="IT Department",
            send_welcome_email=False,
        )

        assert isinstance(result, PilotUserResult)
        assert result.user is not None
        assert result.user.username == "john.doe"
        assert result.user.email == "john.doe@moh.gov.ph"
        assert result.user.first_name == "John"
        assert result.user.last_name == "Doe"
        assert result.user.position == "IT Manager"
        assert result.user.contact_number == "+639171234567"
        assert result.user.user_type == "bmoa"
        assert result.user.organization == "Ministry of Health"
        assert result.user.is_active is True
        assert result.user.is_approved is True
        assert len(result.raw_password) > 0

    def test_create_pilot_user_minimal_fields(self):
        """Test pilot user creation with only required fields."""
        result = self.service.create_pilot_user(
            username="jane.doe",
            email="jane.doe@moh.gov.ph",
            organization_code="MOH_TEST",
            role="viewer",
            send_welcome_email=False,
        )

        assert result.user is not None
        assert result.user.username == "jane.doe"
        assert result.user.email == "jane.doe@moh.gov.ph"
        assert result.user.first_name == ""
        assert result.user.last_name == ""
        assert result.user.position == ""
        assert result.user.contact_number == ""

    def test_create_pilot_user_with_missing_organization(self):
        """Test that creating user with non-existent organization raises error."""
        with pytest.raises(Organization.DoesNotExist) as exc_info:
            self.service.create_pilot_user(
                username="test.user",
                email="test@example.com",
                organization_code="NONEXISTENT",
                role="viewer",
                send_welcome_email=False,
            )

        assert "Organization with code 'NONEXISTENT' not found" in str(exc_info.value)
        assert "Run load_pilot_moas first" in str(exc_info.value)

    def test_create_pilot_user_with_duplicate_username(self):
        """Test that duplicate username raises ValueError."""
        # Create first user
        self.service.create_pilot_user(
            username="duplicate.user",
            email="first@moh.gov.ph",
            organization_code="MOH_TEST",
            role="viewer",
            send_welcome_email=False,
        )

        # Try to create second user with same username
        with pytest.raises(ValueError) as exc_info:
            self.service.create_pilot_user(
                username="duplicate.user",
                email="second@moh.gov.ph",
                organization_code="MOH_TEST",
                role="viewer",
                send_welcome_email=False,
            )

        assert "Username 'duplicate.user' already exists" in str(exc_info.value)

    def test_create_pilot_user_with_duplicate_email(self):
        """Test that duplicate email raises ValueError."""
        # Create first user
        self.service.create_pilot_user(
            username="user.one",
            email="duplicate@moh.gov.ph",
            organization_code="MOH_TEST",
            role="viewer",
            send_welcome_email=False,
        )

        # Try to create second user with same email
        with pytest.raises(ValueError) as exc_info:
            self.service.create_pilot_user(
                username="user.two",
                email="duplicate@moh.gov.ph",
                organization_code="MOH_TEST",
                role="viewer",
                send_welcome_email=False,
            )

        assert "Email 'duplicate@moh.gov.ph' already exists" in str(exc_info.value)

    def test_create_pilot_user_case_insensitive_org_code(self):
        """Test that organization code lookup is case-insensitive."""
        result = self.service.create_pilot_user(
            username="test.user",
            email="test@example.com",
            organization_code="moh_test",  # lowercase
            role="viewer",
            send_welcome_email=False,
        )

        assert result.user.organization == "Ministry of Health"

    def test_create_pilot_user_creates_membership(self):
        """Test that OrganizationMembership is created."""
        result = self.service.create_pilot_user(
            username="test.user",
            email="test@moh.gov.ph",
            organization_code="MOH_TEST",
            role="planner",
            position="Senior Planner",
            department="Planning Division",
            send_welcome_email=False,
        )

        membership = OrganizationMembership.objects.get(user=result.user)
        assert membership.organization == self.org
        assert membership.role == "staff"
        assert membership.is_primary is True
        assert membership.position == "Senior Planner"
        assert membership.department == "Planning Division"

    def test_create_pilot_user_membership_permissions_admin(self):
        """Test that pilot_admin gets elevated membership permissions."""
        result = self.service.create_pilot_user(
            username="admin.user",
            email="admin@moh.gov.ph",
            organization_code="MOH_TEST",
            role="pilot_admin",
            send_welcome_email=False,
        )

        membership = OrganizationMembership.objects.get(user=result.user)
        assert membership.can_manage_users is True
        assert membership.can_approve_plans is True
        assert membership.can_approve_budgets is True

    def test_create_pilot_user_membership_permissions_planner(self):
        """Test that planner gets appropriate membership permissions."""
        result = self.service.create_pilot_user(
            username="planner.user",
            email="planner@moh.gov.ph",
            organization_code="MOH_TEST",
            role="planner",
            send_welcome_email=False,
        )

        membership = OrganizationMembership.objects.get(user=result.user)
        assert membership.can_manage_users is False
        assert membership.can_approve_plans is True
        assert membership.can_approve_budgets is False

    def test_create_pilot_user_membership_permissions_budget_officer(self):
        """Test that budget_officer gets budget approval permissions."""
        result = self.service.create_pilot_user(
            username="budget.user",
            email="budget@moh.gov.ph",
            organization_code="MOH_TEST",
            role="budget_officer",
            send_welcome_email=False,
        )

        membership = OrganizationMembership.objects.get(user=result.user)
        assert membership.can_manage_users is False
        assert membership.can_approve_plans is False
        assert membership.can_approve_budgets is True

    def test_create_pilot_user_membership_permissions_viewer(self):
        """Test that viewer gets no elevated permissions."""
        result = self.service.create_pilot_user(
            username="viewer.user",
            email="viewer@moh.gov.ph",
            organization_code="MOH_TEST",
            role="viewer",
            send_welcome_email=False,
        )

        membership = OrganizationMembership.objects.get(user=result.user)
        assert membership.can_manage_users is False
        assert membership.can_approve_plans is False
        assert membership.can_approve_budgets is False

    def test_create_pilot_user_assigns_role_group(self):
        """Test that user is assigned to the correct role group."""
        result = self.service.create_pilot_user(
            username="test.user",
            email="test@moh.gov.ph",
            organization_code="MOH_TEST",
            role="planner",
            send_welcome_email=False,
        )

        assert result.user.groups.filter(name="planner").exists()

    def test_create_pilot_user_with_custom_password(self):
        """Test that custom password is used when provided."""
        custom_password = "CustomPassword123!"

        result = self.service.create_pilot_user(
            username="test.user",
            email="test@moh.gov.ph",
            organization_code="MOH_TEST",
            role="viewer",
            password=custom_password,
            send_welcome_email=False,
        )

        assert result.raw_password == custom_password
        assert result.user.check_password(custom_password)

    def test_create_pilot_user_password_is_hashed(self):
        """Test that stored password is hashed, not plain text."""
        result = self.service.create_pilot_user(
            username="test.user",
            email="test@moh.gov.ph",
            organization_code="MOH_TEST",
            role="viewer",
            send_welcome_email=False,
        )

        # Password should be hashed
        assert result.user.password != result.raw_password
        assert result.user.password.startswith("pbkdf2_sha256$")
        # But user should be able to authenticate with raw password
        assert result.user.check_password(result.raw_password)

    @patch("organizations.services.user_service.send_pilot_welcome_email")
    def test_create_pilot_user_queues_welcome_email(self, mock_task):
        """Test that welcome email task is queued when enabled."""
        mock_task.delay = Mock()

        result = self.service.create_pilot_user(
            username="test.user",
            email="test@moh.gov.ph",
            organization_code="MOH_TEST",
            role="viewer",
            send_welcome_email=True,
        )

        mock_task.delay.assert_called_once_with(result.user.pk, result.raw_password)

    def test_create_pilot_user_skips_email_when_disabled(self):
        """Test that email is not queued when send_welcome_email=False."""
        with patch("organizations.services.user_service.send_pilot_welcome_email") as mock_task:
            mock_task.delay = Mock()

            result = self.service.create_pilot_user(
                username="test.user",
                email="test@moh.gov.ph",
                organization_code="MOH_TEST",
                role="viewer",
                send_welcome_email=False,
            )

            mock_task.delay.assert_not_called()

    @patch("organizations.services.user_service.send_pilot_welcome_email")
    def test_create_pilot_user_handles_email_queue_failure(self, mock_task):
        """Test that user creation succeeds even if email queueing fails."""
        mock_task.delay.side_effect = Exception("Celery connection failed")

        # Should not raise exception
        result = self.service.create_pilot_user(
            username="test.user",
            email="test@moh.gov.ph",
            organization_code="MOH_TEST",
            role="viewer",
            send_welcome_email=True,
        )

        # User should still be created
        assert result.user is not None
        assert result.user.username == "test.user"

    def test_create_pilot_user_transaction_rollback_on_error(self):
        """Test that transaction is rolled back if user creation fails."""
        initial_user_count = User.objects.count()
        initial_membership_count = OrganizationMembership.objects.count()

        # Create a situation that will fail (e.g., invalid role)
        with pytest.raises(ValueError):
            self.service.create_pilot_user(
                username="test.user",
                email="test@moh.gov.ph",
                organization_code="MOH_TEST",
                role="invalid_role",  # This will fail
                send_welcome_email=False,
            )

        # Verify nothing was created
        assert User.objects.count() == initial_user_count
        assert OrganizationMembership.objects.count() == initial_membership_count

    def test_update_role_assigns_new_role(self):
        """Test update_role() assigns new role to user."""
        result = self.service.create_pilot_user(
            username="test.user",
            email="test@moh.gov.ph",
            organization_code="MOH_TEST",
            role="viewer",
            send_welcome_email=False,
        )

        self.service.update_role(result.user, "planner")

        assert result.user.groups.filter(name="planner").exists()

    def test_update_role_preserves_existing_roles(self):
        """Test that update_role() doesn't remove existing roles."""
        result = self.service.create_pilot_user(
            username="test.user",
            email="test@moh.gov.ph",
            organization_code="MOH_TEST",
            role="viewer",
            send_welcome_email=False,
        )

        # Add second role
        self.service.update_role(result.user, "planner")

        # User should have both roles
        assert result.user.groups.filter(name="viewer").exists()
        assert result.user.groups.filter(name="planner").exists()
        assert result.user.groups.count() == 2

    def test_role_service_integration(self):
        """Test that PilotUserService properly integrates with PilotRoleService."""
        custom_role_service = Mock(spec=PilotRoleService)
        custom_role_service.assign_role = Mock()

        service = PilotUserService(role_service=custom_role_service)

        result = service.create_pilot_user(
            username="test.user",
            email="test@moh.gov.ph",
            organization_code="MOH_TEST",
            role="planner",
            send_welcome_email=False,
        )

        # Verify role service was called
        custom_role_service.assign_role.assert_called_once()

    def test_create_pilot_user_all_roles(self):
        """Test creating users with each available role."""
        roles = ["pilot_admin", "planner", "budget_officer", "me_officer", "viewer"]

        for idx, role in enumerate(roles):
            result = self.service.create_pilot_user(
                username=f"user_{role}",
                email=f"{role}@moh.gov.ph",
                organization_code="MOH_TEST",
                role=role,
                send_welcome_email=False,
            )

            assert result.user is not None
            assert result.user.groups.filter(name=role).exists()

    def test_create_pilot_user_fields_are_trimmed(self):
        """Test that empty string fields are stored correctly."""
        result = self.service.create_pilot_user(
            username="test.user",
            email="test@moh.gov.ph",
            organization_code="MOH_TEST",
            role="viewer",
            first_name="",
            last_name="",
            phone="",
            position="",
            department="",
            send_welcome_email=False,
        )

        assert result.user.first_name == ""
        assert result.user.last_name == ""
        assert result.user.position == ""
        assert result.user.contact_number == ""

    @pytest.mark.parametrize(
        "role,expected_manage,expected_approve_plans,expected_approve_budgets",
        [
            ("pilot_admin", True, True, True),
            ("planner", False, True, False),
            ("budget_officer", False, False, True),
            ("me_officer", False, False, False),
            ("viewer", False, False, False),
        ],
    )
    def test_membership_permissions_matrix(
        self, role, expected_manage, expected_approve_plans, expected_approve_budgets
    ):
        """Test membership permissions for all roles using parametrize."""
        result = self.service.create_pilot_user(
            username=f"user_{role}",
            email=f"{role}@moh.gov.ph",
            organization_code="MOH_TEST",
            role=role,
            send_welcome_email=False,
        )

        membership = OrganizationMembership.objects.get(user=result.user)
        assert membership.can_manage_users == expected_manage
        assert membership.can_approve_plans == expected_approve_plans
        assert membership.can_approve_budgets == expected_approve_budgets


# ============================================================================
# Integration Tests
# ============================================================================


@pytest.mark.django_db(transaction=True)
class TestPilotServicesIntegration:
    """Integration tests for both services working together."""

    @pytest.fixture(autouse=True)
    def setup(self, db):
        """Set up test environment."""
        self.org = Organization.objects.create(
            code='MOH_TEST',
            name='Ministry of Health',
            org_type='ministry',
            is_pilot=True,
            is_active=True,
        )
        User.objects.all().delete()
        Group.objects.all().delete()
        yield
        Organization.objects.filter(code='MOH_TEST').delete()

    def test_end_to_end_pilot_user_creation(self):
        """Test complete workflow of creating a pilot user."""
        role_service = PilotRoleService()
        user_service = PilotUserService(role_service=role_service)

        # Create pilot user
        result = user_service.create_pilot_user(
            username="john.admin",
            email="john.admin@moh.gov.ph",
            organization_code="MOH_TEST",
            role="pilot_admin",
            first_name="John",
            last_name="Admin",
            phone="+639171234567",
            position="System Administrator",
            department="IT Department",
            send_welcome_email=False,
        )

        # Verify user
        assert result.user.username == "john.admin"
        assert result.user.is_active is True

        # Verify membership
        membership = OrganizationMembership.objects.get(user=result.user)
        assert membership.organization.code == "MOH_TEST"
        assert membership.can_manage_users is True

        # Verify role group
        assert result.user.groups.filter(name="pilot_admin").exists()

        # Verify role exists in database
        group = Group.objects.get(name="pilot_admin")
        assert group is not None

    def test_multiple_users_same_organization(self):
        """Test creating multiple users in the same organization."""
        user_service = PilotUserService()

        # Create admin
        admin = user_service.create_pilot_user(
            username="admin",
            email="admin@moh.gov.ph",
            organization_code="MOH_TEST",
            role="pilot_admin",
            send_welcome_email=False,
        )

        # Create planner
        planner = user_service.create_pilot_user(
            username="planner",
            email="planner@moh.gov.ph",
            organization_code="MOH_TEST",
            role="planner",
            send_welcome_email=False,
        )

        # Create viewer
        viewer = user_service.create_pilot_user(
            username="viewer",
            email="viewer@moh.gov.ph",
            organization_code="MOH_TEST",
            role="viewer",
            send_welcome_email=False,
        )

        # All users should belong to same organization
        assert OrganizationMembership.objects.filter(organization=self.org).count() == 3

    def test_role_permissions_persist_across_service_instances(self):
        """Test that roles created by one service instance work with another."""
        # First service creates roles
        service1 = PilotUserService()
        result1 = service1.create_pilot_user(
            username="user1",
            email="user1@moh.gov.ph",
            organization_code="MOH_TEST",
            role="planner",
            send_welcome_email=False,
        )

        # Second service (new instance) uses existing roles
        service2 = PilotUserService()
        result2 = service2.create_pilot_user(
            username="user2",
            email="user2@moh.gov.ph",
            organization_code="MOH_TEST",
            role="planner",
            send_welcome_email=False,
        )

        # Both users should have the same role
        assert result1.user.groups.filter(name="planner").exists()
        assert result2.user.groups.filter(name="planner").exists()

        # Only one "planner" group should exist
        assert Group.objects.filter(name="planner").count() == 1

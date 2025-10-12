"""
RBAC (Role-Based Access Control) Models for OBCMS/BMMS

This module provides comprehensive RBAC infrastructure for multi-tenant
access control across the Bangsamoro Ministerial Management System (BMMS).

Architecture:
- Feature-based permissions (navbar menu items, modules, actions)
- Role-based assignment (Admin, Manager, Staff, Viewer)
- Organization-scoped isolation (MOA A cannot access MOA B data)
- OCM read-only aggregation (Office of Chief Minister oversight)

Database Design:
- UUID primary keys for security
- Organization FK for multi-tenancy
- Efficient indexing for permission checks
- Caching support for performance

References:
- NAVBAR_RBAC_ANALYSIS.md - Menu structure and requirements
- DJANGO_PERMISSIONS_RBAC_BEST_PRACTICES.md - Implementation patterns
- BMMS Transition Plan - Multi-tenant specifications
"""

import uuid
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class Feature(models.Model):
    """
    Represents a feature/resource in the system that can be permission-controlled.

    Features include:
    - Navbar menu items (Dashboard, OBC Data, MANA, Coordination, etc.)
    - Module access (Planning, Budget, M&E, etc.)
    - Specific actions (Create PPA, Approve Budget, Export Data, etc.)

    Examples:
    - feature_key='communities.barangay_obc', name='Barangay OBC Management'
    - feature_key='mana.regional_overview', name='Regional MANA Dashboard'
    - feature_key='oobc_management.user_approvals', name='User Approvals'
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    # Feature identification
    feature_key = models.CharField(
        max_length=100,
        unique=True,
        db_index=True,
        help_text="Unique identifier (e.g., 'communities.barangay_obc')"
    )

    name = models.CharField(
        max_length=255,
        help_text="Human-readable feature name"
    )

    description = models.TextField(
        blank=True,
        help_text="Description of what this feature does"
    )

    # Categorization
    module = models.CharField(
        max_length=50,
        db_index=True,
        help_text="Module this feature belongs to (e.g., 'communities', 'mana', 'coordination')"
    )

    category = models.CharField(
        max_length=50,
        blank=True,
        help_text="Feature category for grouping (e.g., 'navigation', 'data_management', 'reporting')"
    )

    # Parent-child hierarchy (for nested menus)
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='children',
        help_text="Parent feature for hierarchical organization"
    )

    # Status
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        help_text="Whether this feature is currently active"
    )

    # Organization-specific feature toggle
    organization = models.ForeignKey(
        'coordination.Organization',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='custom_features',
        help_text="Organization this feature is scoped to (null = global feature)"
    )

    # Metadata
    icon = models.CharField(
        max_length=50,
        blank=True,
        help_text="Icon class for UI display (e.g., 'fa-users')"
    )

    url_pattern = models.CharField(
        max_length=255,
        blank=True,
        help_text="URL pattern for this feature (e.g., '/communities/barangay/')"
    )

    sort_order = models.IntegerField(
        default=0,
        help_text="Display order within parent/module"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'rbac_feature'
        verbose_name = 'Feature'
        verbose_name_plural = 'Features'
        ordering = ['module', 'sort_order', 'name']
        indexes = [
            models.Index(fields=['module', 'is_active']),
            models.Index(fields=['parent', 'sort_order']),
            models.Index(fields=['organization', 'is_active']),
        ]

    def __str__(self):
        return f"{self.name} ({self.feature_key})"

    @property
    def full_key(self):
        """Return hierarchical feature key."""
        if self.parent:
            return f"{self.parent.full_key}.{self.feature_key}"
        return self.feature_key

    def clean(self):
        """Validate feature configuration."""
        # Prevent circular parent relationships
        if self.parent == self:
            raise ValidationError("A feature cannot be its own parent.")

        # Check for circular reference in parent chain
        parent = self.parent
        while parent:
            if parent == self:
                raise ValidationError("Circular parent relationship detected.")
            parent = parent.parent


class Permission(models.Model):
    """
    Represents a specific permission/action that can be granted.

    Permissions are granular actions like:
    - 'view' - Can view the feature/resource
    - 'create' - Can create new items
    - 'edit' - Can update existing items
    - 'delete' - Can delete items
    - 'approve' - Can approve submissions
    - 'export' - Can export data

    Permissions are scoped to Features for flexibility.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    # Permission identification
    codename = models.CharField(
        max_length=100,
        db_index=True,
        help_text="Permission identifier (e.g., 'view', 'create', 'approve')"
    )

    name = models.CharField(
        max_length=255,
        help_text="Human-readable permission name"
    )

    description = models.TextField(
        blank=True,
        help_text="Description of what this permission allows"
    )

    # Linked to feature
    feature = models.ForeignKey(
        Feature,
        on_delete=models.CASCADE,
        related_name='permissions',
        help_text="Feature this permission applies to"
    )

    # Permission type
    PERMISSION_TYPES = [
        ('view', 'View/Read'),
        ('create', 'Create/Add'),
        ('edit', 'Edit/Update'),
        ('delete', 'Delete/Remove'),
        ('approve', 'Approve/Authorize'),
        ('export', 'Export Data'),
        ('custom', 'Custom Action'),
    ]

    permission_type = models.CharField(
        max_length=20,
        choices=PERMISSION_TYPES,
        default='view',
        db_index=True,
        help_text="Type of permission"
    )

    # Status
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        help_text="Whether this permission is currently active"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'rbac_permission'
        verbose_name = 'Permission'
        verbose_name_plural = 'Permissions'
        ordering = ['feature', 'permission_type', 'codename']
        unique_together = [('feature', 'codename')]
        indexes = [
            models.Index(fields=['feature', 'permission_type', 'is_active']),
            models.Index(fields=['codename', 'is_active']),
        ]

    def __str__(self):
        return f"{self.feature.name} - {self.name}"

    @property
    def full_permission_key(self):
        """Return fully qualified permission key."""
        return f"{self.feature.feature_key}.{self.codename}"


class Role(models.Model):
    """
    Represents a user role with bundled permissions.

    Standard Roles (BMMS):
    - OOBC Admin - Full system access
    - OOBC Manager - Management-level access
    - OOBC Staff - Standard staff access
    - OOBC Viewer - Read-only access
    - MOA Admin - Ministry/Agency admin
    - MOA Manager - Ministry/Agency manager
    - MOA Staff - Ministry/Agency staff
    - MOA Viewer - Ministry/Agency viewer
    - OCM Analyst - Office of Chief Minister (read-only aggregated)

    Roles can be organization-scoped for multi-tenancy.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    # Role identification
    name = models.CharField(
        max_length=100,
        help_text="Role name (e.g., 'OOBC Admin', 'MOA Manager')"
    )

    slug = models.SlugField(
        max_length=100,
        db_index=True,
        help_text="URL-friendly role identifier"
    )

    description = models.TextField(
        blank=True,
        help_text="Description of role responsibilities"
    )

    # Role scope
    ROLE_SCOPES = [
        ('system', 'System-wide'),
        ('organization', 'Organization-specific'),
        ('module', 'Module-specific'),
    ]

    scope = models.CharField(
        max_length=20,
        choices=ROLE_SCOPES,
        default='organization',
        db_index=True,
        help_text="Scope of this role"
    )

    # Organization scoping (for multi-tenancy)
    organization = models.ForeignKey(
        'coordination.Organization',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='roles',
        help_text="Organization this role belongs to (null = global role)"
    )

    # Hierarchical roles (for inheritance)
    parent_role = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='child_roles',
        help_text="Parent role for permission inheritance"
    )

    # Role level (for hierarchy)
    ROLE_LEVELS = [
        (1, 'Viewer'),
        (2, 'Staff'),
        (3, 'Manager'),
        (4, 'Admin'),
        (5, 'Super Admin'),
    ]

    level = models.IntegerField(
        choices=ROLE_LEVELS,
        default=2,
        db_index=True,
        help_text="Role hierarchy level"
    )

    # Status
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        help_text="Whether this role is currently active"
    )

    is_system_role = models.BooleanField(
        default=False,
        help_text="Whether this is a system-defined role (cannot be deleted)"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='created_roles',
        help_text="User who created this role"
    )

    class Meta:
        db_table = 'rbac_role'
        verbose_name = 'Role'
        verbose_name_plural = 'Roles'
        ordering = ['-level', 'name']
        unique_together = [('slug', 'organization')]
        indexes = [
            models.Index(fields=['scope', 'is_active']),
            models.Index(fields=['organization', 'is_active']),
            models.Index(fields=['level', 'is_active']),
        ]

    def __str__(self):
        if self.organization:
            return f"{self.name} ({self.organization.name})"
        return f"{self.name} (Global)"

    def get_all_permissions(self):
        """Get all permissions including inherited from parent roles."""
        permissions = set(self.role_permissions.filter(is_active=True).values_list('permission_id', flat=True))

        # Add parent permissions
        if self.parent_role:
            parent_perms = self.parent_role.get_all_permissions()
            permissions.update(parent_perms)

        return permissions

    def clean(self):
        """Validate role configuration."""
        # Prevent circular parent relationships
        if self.parent_role == self:
            raise ValidationError("A role cannot be its own parent.")

        # System roles cannot be organization-scoped
        if self.is_system_role and self.organization:
            raise ValidationError("System roles cannot be organization-specific.")


class RolePermission(models.Model):
    """
    Links roles to permissions (many-to-many with metadata).

    This through model enables:
    - Permission grants/denials per role
    - Conditional permissions
    - Permission expiration
    - Audit trail
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        related_name='role_permissions',
        help_text="Role being granted permission"
    )

    permission = models.ForeignKey(
        Permission,
        on_delete=models.CASCADE,
        related_name='role_assignments',
        help_text="Permission being granted"
    )

    # Permission modifiers
    is_granted = models.BooleanField(
        default=True,
        help_text="True = grant permission, False = explicitly deny"
    )

    # Conditions (JSON for flexibility)
    conditions = models.JSONField(
        default=dict,
        blank=True,
        help_text="Conditions for permission (e.g., {'own_data_only': true})"
    )

    # Status
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        help_text="Whether this permission assignment is active"
    )

    # Expiration (optional)
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When this permission assignment expires"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    granted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='granted_role_permissions',
        help_text="User who granted this permission"
    )

    class Meta:
        db_table = 'rbac_role_permission'
        verbose_name = 'Role Permission'
        verbose_name_plural = 'Role Permissions'
        ordering = ['role', 'permission']
        unique_together = [('role', 'permission')]
        indexes = [
            models.Index(fields=['role', 'is_active']),
            models.Index(fields=['permission', 'is_active']),
            models.Index(fields=['expires_at']),
        ]

    def __str__(self):
        action = "granted" if self.is_granted else "denied"
        return f"{self.role.name} - {self.permission.name} ({action})"

    @property
    def is_expired(self):
        """Check if permission has expired."""
        if not self.expires_at:
            return False
        return timezone.now() > self.expires_at

    def clean(self):
        """Validate permission assignment."""
        # Check expiration
        if self.expires_at and self.expires_at <= timezone.now():
            raise ValidationError("Expiration date must be in the future.")


class UserRole(models.Model):
    """
    Assigns roles to users (many-to-many with metadata).

    Enables:
    - Multiple roles per user
    - Organization-scoped role assignments
    - Role assignment audit trail
    - Temporary role grants
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='user_roles',
        help_text="User being assigned role"
    )

    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        related_name='user_assignments',
        help_text="Role being assigned"
    )

    # Organization context (for multi-tenant roles)
    organization = models.ForeignKey(
        'coordination.Organization',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='user_role_assignments',
        help_text="Organization context for this role assignment"
    )

    # Status
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        help_text="Whether this role assignment is active"
    )

    # Expiration (optional)
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When this role assignment expires"
    )

    # Timestamps
    assigned_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='assigned_user_roles',
        help_text="User who assigned this role"
    )

    class Meta:
        db_table = 'rbac_user_role'
        verbose_name = 'User Role'
        verbose_name_plural = 'User Roles'
        ordering = ['user', 'role']
        unique_together = [('user', 'role', 'organization')]
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['role', 'is_active']),
            models.Index(fields=['organization', 'is_active']),
            models.Index(fields=['expires_at']),
        ]

    def __str__(self):
        if self.organization:
            return f"{self.user.get_full_name()} - {self.role.name} ({self.organization.name})"
        return f"{self.user.get_full_name()} - {self.role.name}"

    @property
    def is_expired(self):
        """Check if role assignment has expired."""
        if not self.expires_at:
            return False
        return timezone.now() > self.expires_at

    def clean(self):
        """Validate role assignment."""
        # Organization-scoped roles must have organization context
        if self.role.scope == 'organization' and not self.organization:
            raise ValidationError(
                f"Role '{self.role.name}' requires an organization context."
            )

        # Global roles cannot have organization context
        if self.role.scope == 'system' and self.organization:
            raise ValidationError(
                f"System role '{self.role.name}' cannot be assigned to a specific organization."
            )

        # Check expiration
        if self.expires_at and self.expires_at <= timezone.now():
            raise ValidationError("Expiration date must be in the future.")


class UserPermission(models.Model):
    """
    Direct permission assignments to users (bypassing roles).

    Use cases:
    - One-off permission grants
    - Temporary elevated access
    - Override role permissions
    - Emergency access

    Note: Direct permissions override role permissions.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='direct_permissions',
        help_text="User being granted permission"
    )

    permission = models.ForeignKey(
        Permission,
        on_delete=models.CASCADE,
        related_name='direct_user_assignments',
        help_text="Permission being granted"
    )

    # Permission modifiers
    is_granted = models.BooleanField(
        default=True,
        help_text="True = grant permission, False = explicitly deny (overrides role)"
    )

    # Organization context
    organization = models.ForeignKey(
        'coordination.Organization',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='user_permission_assignments',
        help_text="Organization context for this permission"
    )

    # Conditions (JSON for flexibility)
    conditions = models.JSONField(
        default=dict,
        blank=True,
        help_text="Conditions for permission (e.g., {'own_data_only': true})"
    )

    # Status
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        help_text="Whether this permission assignment is active"
    )

    # Expiration (optional)
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When this permission expires"
    )

    # Reason (for audit)
    reason = models.TextField(
        blank=True,
        help_text="Reason for granting this permission"
    )

    # Timestamps
    assigned_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    granted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='granted_user_permissions',
        help_text="User who granted this permission"
    )

    class Meta:
        db_table = 'rbac_user_permission'
        verbose_name = 'User Permission'
        verbose_name_plural = 'User Permissions'
        ordering = ['user', 'permission']
        unique_together = [('user', 'permission', 'organization')]
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['permission', 'is_active']),
            models.Index(fields=['organization', 'is_active']),
            models.Index(fields=['expires_at']),
        ]

    def __str__(self):
        action = "granted" if self.is_granted else "denied"
        if self.organization:
            return f"{self.user.get_full_name()} - {self.permission.name} ({action}) [{self.organization.name}]"
        return f"{self.user.get_full_name()} - {self.permission.name} ({action})"

    @property
    def is_expired(self):
        """Check if permission has expired."""
        if not self.expires_at:
            return False
        return timezone.now() > self.expires_at

    def clean(self):
        """Validate permission assignment."""
        # Check expiration
        if self.expires_at and self.expires_at <= timezone.now():
            raise ValidationError("Expiration date must be in the future.")

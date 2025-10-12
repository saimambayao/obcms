"""
Django Admin interface for RBAC (Role-Based Access Control) models.

Provides comprehensive management interface for:
- Features (system capabilities and menu items)
- Permissions (granular access controls)
- Roles (bundled permission sets)
- Role Permissions (role-to-permission assignments)
- User Roles (user-to-role assignments)
- User Permissions (direct user permission grants)

Features:
- Inline editing for role permissions
- Custom list displays with counts and links
- Autocomplete fields for better UX
- Admin actions for bulk operations
- Protection for system roles
- Auto-population of created_by/assigned_by fields
- Comprehensive filtering and search
"""

from django.contrib import admin
from django.db.models import Count, Q
from django.urls import reverse
from django.utils.html import format_html
from django.utils import timezone
from django.core.exceptions import ValidationError

from common.rbac_models import (
    Feature,
    Permission,
    Role,
    RolePermission,
    UserRole,
    UserPermission,
)


# ============================================================================
# INLINE ADMINS
# ============================================================================

class RolePermissionInline(admin.TabularInline):
    """Inline admin for role permissions."""

    model = RolePermission
    extra = 1
    autocomplete_fields = ['permission']
    fields = [
        'permission',
        'is_granted',
        'conditions',
        'is_active',
        'expires_at',
    ]
    readonly_fields = []

    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        qs = super().get_queryset(request)
        return qs.select_related('permission', 'permission__feature')


# ============================================================================
# FEATURE ADMIN
# ============================================================================

@admin.register(Feature)
class FeatureAdmin(admin.ModelAdmin):
    """Admin interface for Features."""

    list_display = [
        'name',
        'feature_key',
        'category',
        'module',
        'parent_link',
        'sort_order',
        'is_active',
        'sub_feature_count',
    ]

    list_filter = [
        'category',
        'module',
        'is_active',
        'parent',
        ('organization', admin.RelatedOnlyFieldListFilter),
    ]

    search_fields = [
        'name',
        'feature_key',
        'description',
        'module',
        'category',
    ]

    autocomplete_fields = ['parent', 'organization']

    readonly_fields = ['id', 'created_at', 'updated_at', 'full_key']

    fieldsets = (
        ('Basic Information', {
            'fields': (
                'id',
                'feature_key',
                'name',
                'description',
            )
        }),
        ('Categorization', {
            'fields': (
                'module',
                'category',
            )
        }),
        ('Hierarchy', {
            'fields': (
                'parent',
                'full_key',
            )
        }),
        ('UI Configuration', {
            'fields': (
                'icon',
                'url_pattern',
                'sort_order',
            )
        }),
        ('Organization Scope', {
            'fields': (
                'organization',
            ),
            'classes': ('collapse',),
        }),
        ('Status', {
            'fields': (
                'is_active',
            )
        }),
        ('Timestamps', {
            'fields': (
                'created_at',
                'updated_at',
            ),
            'classes': ('collapse',),
        }),
    )

    ordering = ['module', 'sort_order', 'name']

    def parent_link(self, obj):
        """Display parent feature as link."""
        if obj.parent:
            url = reverse('admin:common_feature_change', args=[obj.parent.pk])
            return format_html('<a href="{}">{}</a>', url, obj.parent.name)
        return '-'
    parent_link.short_description = 'Parent Feature'

    def sub_feature_count(self, obj):
        """Count and link to sub-features."""
        count = obj.children.count()
        if count > 0:
            url = reverse('admin:common_feature_changelist')
            return format_html(
                '<a href="{}?parent__id__exact={}">{} sub-features</a>',
                url, obj.pk, count
            )
        return '0'
    sub_feature_count.short_description = 'Sub-Features'

    def get_queryset(self, request):
        """Optimize queryset."""
        qs = super().get_queryset(request)
        return qs.select_related('parent', 'organization').annotate(
            children_count=Count('children')
        )


# ============================================================================
# PERMISSION ADMIN
# ============================================================================

@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    """Admin interface for Permissions."""

    list_display = [
        'full_code',
        'name',
        'feature_link',
        'permission_type',
        'is_active',
        'role_count',
    ]

    list_filter = [
        'permission_type',
        'is_active',
        ('feature__category', admin.RelatedOnlyFieldListFilter),
        ('feature__module', admin.RelatedOnlyFieldListFilter),
    ]

    search_fields = [
        'name',
        'codename',
        'description',
        'feature__name',
        'feature__feature_key',
    ]

    autocomplete_fields = ['feature']

    readonly_fields = ['id', 'created_at', 'updated_at', 'full_permission_key']

    fieldsets = (
        ('Basic Information', {
            'fields': (
                'id',
                'codename',
                'name',
                'description',
                'full_permission_key',
            )
        }),
        ('Feature Association', {
            'fields': (
                'feature',
            )
        }),
        ('Permission Type', {
            'fields': (
                'permission_type',
            )
        }),
        ('Status', {
            'fields': (
                'is_active',
            )
        }),
        ('Timestamps', {
            'fields': (
                'created_at',
                'updated_at',
            ),
            'classes': ('collapse',),
        }),
    )

    ordering = ['feature__module', 'feature__feature_key', 'permission_type', 'codename']

    def full_code(self, obj):
        """Display full permission code."""
        return obj.full_permission_key
    full_code.short_description = 'Full Code'
    full_code.admin_order_field = 'feature__feature_key'

    def feature_link(self, obj):
        """Display feature as link."""
        url = reverse('admin:common_feature_change', args=[obj.feature.pk])
        return format_html('<a href="{}">{}</a>', url, obj.feature.name)
    feature_link.short_description = 'Feature'
    feature_link.admin_order_field = 'feature__name'

    def role_count(self, obj):
        """Count roles using this permission."""
        count = obj.role_assignments.filter(is_active=True).count()
        if count > 0:
            url = reverse('admin:common_rolepermission_changelist')
            return format_html(
                '<a href="{}?permission__id__exact={}">{} roles</a>',
                url, obj.pk, count
            )
        return '0'
    role_count.short_description = 'Roles'

    def get_queryset(self, request):
        """Optimize queryset."""
        qs = super().get_queryset(request)
        return qs.select_related('feature').annotate(
            active_role_count=Count('role_assignments', filter=Q(role_assignments__is_active=True))
        )


# ============================================================================
# ROLE ADMIN
# ============================================================================

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    """Admin interface for Roles."""

    list_display = [
        'name',
        'slug',
        'scope',
        'level_display',
        'organization_link',
        'is_active',
        'is_system_role',
        'user_count',
        'permission_count',
    ]

    list_filter = [
        'scope',
        'level',
        'is_active',
        'is_system_role',
        ('organization', admin.RelatedOnlyFieldListFilter),
    ]

    search_fields = [
        'name',
        'slug',
        'description',
    ]

    autocomplete_fields = ['organization', 'parent_role']
    raw_id_fields = ['created_by']  # User model - use raw_id for admin ordering

    readonly_fields = ['id', 'created_at', 'updated_at']

    inlines = [RolePermissionInline]

    fieldsets = (
        ('Basic Information', {
            'fields': (
                'id',
                'name',
                'slug',
                'description',
            )
        }),
        ('Scope & Hierarchy', {
            'fields': (
                'scope',
                'level',
                'parent_role',
                'organization',
            )
        }),
        ('Status', {
            'fields': (
                'is_active',
                'is_system_role',
            )
        }),
        ('Metadata', {
            'fields': (
                'created_by',
                'created_at',
                'updated_at',
            ),
            'classes': ('collapse',),
        }),
    )

    ordering = ['-level', 'name']

    def level_display(self, obj):
        """Display role level with label."""
        return obj.get_level_display()
    level_display.short_description = 'Level'
    level_display.admin_order_field = 'level'

    def organization_link(self, obj):
        """Display organization as link."""
        if obj.organization:
            url = reverse('admin:coordination_organization_change', args=[obj.organization.pk])
            return format_html('<a href="{}">{}</a>', url, obj.organization.name)
        return 'Global'
    organization_link.short_description = 'Organization'
    organization_link.admin_order_field = 'organization__name'

    def user_count(self, obj):
        """Count users with this role."""
        count = obj.user_assignments.filter(is_active=True).count()
        if count > 0:
            url = reverse('admin:common_userrole_changelist')
            return format_html(
                '<a href="{}?role__id__exact={}">{} users</a>',
                url, obj.pk, count
            )
        return '0'
    user_count.short_description = 'Users'

    def permission_count(self, obj):
        """Count permissions in this role."""
        count = obj.role_permissions.filter(is_active=True).count()
        if count > 0:
            url = reverse('admin:common_rolepermission_changelist')
            return format_html(
                '<a href="{}?role__id__exact={}">{} permissions</a>',
                url, obj.pk, count
            )
        return '0'
    permission_count.short_description = 'Permissions'

    def get_queryset(self, request):
        """Optimize queryset."""
        qs = super().get_queryset(request)
        return qs.select_related('organization', 'parent_role', 'created_by').annotate(
            active_user_count=Count('user_assignments', filter=Q(user_assignments__is_active=True)),
            active_perm_count=Count('role_permissions', filter=Q(role_permissions__is_active=True))
        )

    def save_model(self, request, obj, form, change):
        """Auto-set created_by on creation."""
        if not change and not obj.created_by:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    def delete_model(self, request, obj):
        """Protect system roles from deletion."""
        if obj.is_system_role:
            raise ValidationError(
                f"Cannot delete system role '{obj.name}'. System roles are protected."
            )
        super().delete_model(request, obj)

    def delete_queryset(self, request, queryset):
        """Protect system roles from bulk deletion."""
        system_roles = queryset.filter(is_system_role=True)
        if system_roles.exists():
            raise ValidationError(
                f"Cannot delete {system_roles.count()} system roles. System roles are protected."
            )
        queryset.delete()

    actions = ['deactivate_roles']

    def deactivate_roles(self, request, queryset):
        """Bulk deactivate selected roles."""
        updated = queryset.filter(is_active=True, is_system_role=False).update(is_active=False)
        self.message_user(request, f"{updated} roles were deactivated (system roles excluded).")
    deactivate_roles.short_description = "Deactivate selected roles"


# ============================================================================
# ROLE PERMISSION ADMIN
# ============================================================================

@admin.register(RolePermission)
class RolePermissionAdmin(admin.ModelAdmin):
    """Admin interface for Role Permissions."""

    list_display = [
        'role_link',
        'permission_link',
        'is_granted',
        'is_active',
        'expires_at',
        'granted_by_link',
    ]

    list_filter = [
        'is_granted',
        'is_active',
        ('role', admin.RelatedOnlyFieldListFilter),
        ('permission__feature', admin.RelatedOnlyFieldListFilter),
        'expires_at',
    ]

    search_fields = [
        'role__name',
        'permission__name',
        'permission__codename',
    ]

    autocomplete_fields = ['role', 'permission']
    raw_id_fields = ['granted_by']  # User model - use raw_id for admin ordering

    readonly_fields = ['id', 'created_at', 'updated_at', 'is_expired']

    fieldsets = (
        ('Assignment', {
            'fields': (
                'id',
                'role',
                'permission',
                'is_granted',
            )
        }),
        ('Conditions', {
            'fields': (
                'conditions',
            ),
            'classes': ('collapse',),
        }),
        ('Validity Period', {
            'fields': (
                'expires_at',
                'is_expired',
            )
        }),
        ('Status', {
            'fields': (
                'is_active',
            )
        }),
        ('Metadata', {
            'fields': (
                'granted_by',
                'created_at',
                'updated_at',
            ),
            'classes': ('collapse',),
        }),
    )

    ordering = ['role', 'permission']

    def role_link(self, obj):
        """Display role as link."""
        url = reverse('admin:common_role_change', args=[obj.role.pk])
        return format_html('<a href="{}">{}</a>', url, obj.role.name)
    role_link.short_description = 'Role'
    role_link.admin_order_field = 'role__name'

    def permission_link(self, obj):
        """Display permission as link."""
        url = reverse('admin:common_permission_change', args=[obj.permission.pk])
        return format_html('<a href="{}">{}</a>', url, obj.permission.name)
    permission_link.short_description = 'Permission'
    permission_link.admin_order_field = 'permission__name'

    def granted_by_link(self, obj):
        """Display granted_by user as link."""
        if obj.granted_by:
            url = reverse('admin:common_user_change', args=[obj.granted_by.pk])
            return format_html('<a href="{}">{}</a>', url, obj.granted_by.get_full_name())
        return '-'
    granted_by_link.short_description = 'Granted By'
    granted_by_link.admin_order_field = 'granted_by__last_name'

    def get_queryset(self, request):
        """Optimize queryset."""
        qs = super().get_queryset(request)
        return qs.select_related('role', 'permission', 'permission__feature', 'granted_by')


# ============================================================================
# USER ROLE ADMIN
# ============================================================================

@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    """Admin interface for User Roles."""

    list_display = [
        'user_link',
        'role_link',
        'organization_link',
        'is_active',
        'assigned_at',
        'expires_at',
        'assigned_by_link',
    ]

    list_filter = [
        'is_active',
        ('role', admin.RelatedOnlyFieldListFilter),
        ('organization', admin.RelatedOnlyFieldListFilter),
        'assigned_at',
        'expires_at',
    ]

    search_fields = [
        'user__username',
        'user__first_name',
        'user__last_name',
        'user__email',
        'role__name',
    ]

    autocomplete_fields = ['role', 'organization']
    raw_id_fields = ['user', 'assigned_by']  # User model - use raw_id for admin ordering

    readonly_fields = ['id', 'assigned_at', 'updated_at', 'is_expired']

    fieldsets = (
        ('Assignment', {
            'fields': (
                'id',
                'user',
                'role',
                'organization',
            )
        }),
        ('Validity Period', {
            'fields': (
                'expires_at',
                'is_expired',
            )
        }),
        ('Status', {
            'fields': (
                'is_active',
            )
        }),
        ('Metadata', {
            'fields': (
                'assigned_by',
                'assigned_at',
                'updated_at',
            ),
            'classes': ('collapse',),
        }),
    )

    ordering = ['user__last_name', 'user__first_name', 'role']

    def user_link(self, obj):
        """Display user as link."""
        url = reverse('admin:common_user_change', args=[obj.user.pk])
        return format_html('<a href="{}">{}</a>', url, obj.user.get_full_name())
    user_link.short_description = 'User'
    user_link.admin_order_field = 'user__last_name'

    def role_link(self, obj):
        """Display role as link."""
        url = reverse('admin:common_role_change', args=[obj.role.pk])
        return format_html('<a href="{}">{}</a>', url, obj.role.name)
    role_link.short_description = 'Role'
    role_link.admin_order_field = 'role__name'

    def organization_link(self, obj):
        """Display organization as link."""
        if obj.organization:
            url = reverse('admin:coordination_organization_change', args=[obj.organization.pk])
            return format_html('<a href="{}">{}</a>', url, obj.organization.name)
        return '-'
    organization_link.short_description = 'Organization'
    organization_link.admin_order_field = 'organization__name'

    def assigned_by_link(self, obj):
        """Display assigned_by user as link."""
        if obj.assigned_by:
            url = reverse('admin:common_user_change', args=[obj.assigned_by.pk])
            return format_html('<a href="{}">{}</a>', url, obj.assigned_by.get_full_name())
        return '-'
    assigned_by_link.short_description = 'Assigned By'
    assigned_by_link.admin_order_field = 'assigned_by__last_name'

    def get_queryset(self, request):
        """Optimize queryset."""
        qs = super().get_queryset(request)
        return qs.select_related('user', 'role', 'organization', 'assigned_by')

    def save_model(self, request, obj, form, change):
        """Auto-set assigned_by on creation and validate."""
        if not change and not obj.assigned_by:
            obj.assigned_by = request.user

        # Validate before saving
        obj.full_clean()
        super().save_model(request, obj, form, change)

    actions = ['assign_role_to_users']

    def assign_role_to_users(self, request, queryset):
        """
        Bulk assign role - Note: This action just activates existing assignments.
        To assign new roles, use the Add User Role button.
        """
        updated = queryset.filter(is_active=False).update(is_active=True)
        self.message_user(request, f"{updated} user role assignments were activated.")
    assign_role_to_users.short_description = "Activate selected user role assignments"


# ============================================================================
# USER PERMISSION ADMIN
# ============================================================================

@admin.register(UserPermission)
class UserPermissionAdmin(admin.ModelAdmin):
    """Admin interface for User Permissions."""

    list_display = [
        'user_link',
        'permission_link',
        'is_granted',
        'organization_link',
        'is_active',
        'expires_at',
        'granted_by_link',
    ]

    list_filter = [
        'is_granted',
        'is_active',
        ('permission__feature', admin.RelatedOnlyFieldListFilter),
        ('organization', admin.RelatedOnlyFieldListFilter),
        'assigned_at',
        'expires_at',
    ]

    search_fields = [
        'user__username',
        'user__first_name',
        'user__last_name',
        'user__email',
        'permission__name',
        'permission__codename',
        'reason',
    ]

    autocomplete_fields = ['permission', 'organization']
    raw_id_fields = ['user', 'granted_by']  # User model - use raw_id for admin ordering

    readonly_fields = ['id', 'assigned_at', 'updated_at', 'is_expired']

    fieldsets = (
        ('Assignment', {
            'fields': (
                'id',
                'user',
                'permission',
                'organization',
                'is_granted',
            )
        }),
        ('Conditions', {
            'fields': (
                'conditions',
            ),
            'classes': ('collapse',),
        }),
        ('Validity Period', {
            'fields': (
                'expires_at',
                'is_expired',
            )
        }),
        ('Reason & Audit', {
            'fields': (
                'reason',
            ),
            'description': 'Please provide a reason for granting this permission.'
        }),
        ('Status', {
            'fields': (
                'is_active',
            )
        }),
        ('Metadata', {
            'fields': (
                'granted_by',
                'assigned_at',
                'updated_at',
            ),
            'classes': ('collapse',),
        }),
    )

    ordering = ['user__last_name', 'user__first_name', 'permission']

    def user_link(self, obj):
        """Display user as link."""
        url = reverse('admin:common_user_change', args=[obj.user.pk])
        return format_html('<a href="{}">{}</a>', url, obj.user.get_full_name())
    user_link.short_description = 'User'
    user_link.admin_order_field = 'user__last_name'

    def permission_link(self, obj):
        """Display permission as link."""
        url = reverse('admin:common_permission_change', args=[obj.permission.pk])
        return format_html('<a href="{}">{}</a>', url, obj.permission.name)
    permission_link.short_description = 'Permission'
    permission_link.admin_order_field = 'permission__name'

    def organization_link(self, obj):
        """Display organization as link."""
        if obj.organization:
            url = reverse('admin:coordination_organization_change', args=[obj.organization.pk])
            return format_html('<a href="{}">{}</a>', url, obj.organization.name)
        return 'Global'
    organization_link.short_description = 'Organization'
    organization_link.admin_order_field = 'organization__name'

    def granted_by_link(self, obj):
        """Display granted_by user as link."""
        if obj.granted_by:
            url = reverse('admin:common_user_change', args=[obj.granted_by.pk])
            return format_html('<a href="{}">{}</a>', url, obj.granted_by.get_full_name())
        return '-'
    granted_by_link.short_description = 'Granted By'
    granted_by_link.admin_order_field = 'granted_by__last_name'

    def get_queryset(self, request):
        """Optimize queryset."""
        qs = super().get_queryset(request)
        return qs.select_related('user', 'permission', 'permission__feature', 'organization', 'granted_by')

    def save_model(self, request, obj, form, change):
        """Auto-set granted_by on creation and validate."""
        if not change and not obj.granted_by:
            obj.granted_by = request.user

        # Validate before saving
        obj.full_clean()
        super().save_model(request, obj, form, change)

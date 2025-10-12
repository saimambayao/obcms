"""
Django admin configuration for Organizations app.

Provides comprehensive admin interface for managing:
- Organizations (44 BARMM MOAs)
- Organization Memberships (user-organization relationships)

Admin Features:
- Organization inline memberships
- Module activation toggles
- Pilot MOA filtering
- User role management
- Comprehensive search and filtering
"""

from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from organizations.models import Organization, OrganizationMembership


class OrganizationMembershipInline(admin.TabularInline):
    """
    Inline admin for managing organization memberships.

    Shows user memberships directly on organization admin page.
    """
    model = OrganizationMembership
    extra = 0
    fields = [
        'user',
        'role',
        'position',
        'is_primary',
        'is_active',
        'can_manage_users',
        'can_approve_plans',
        'can_approve_budgets',
    ]
    readonly_fields = ['joined_date']
    autocomplete_fields = ['user']


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    """
    Admin interface for Organization model.

    Features:
    - Comprehensive filtering by type, status, pilot flag
    - Search by code, name, acronym
    - Module activation in dedicated fieldset
    - Inline membership management
    - Geographic coverage management
    """

    list_display = [
        'code',
        'name',
        'org_type',
        'is_active',
        'is_pilot',
        'member_count_display',
        'enabled_modules_display',
    ]

    list_filter = [
        'org_type',
        'is_active',
        'is_pilot',
        'enable_mana',
        'enable_planning',
        'enable_budgeting',
        'enable_me',
        'enable_coordination',
        'enable_policies',
        'created_at',
    ]

    search_fields = [
        'code',
        'name',
        'acronym',
        'head_official',
        'email',
    ]

    ordering = ['name']

    autocomplete_fields = ['primary_focal_person', 'primary_region']
    filter_horizontal = ['service_areas']

    readonly_fields = [
        'created_at',
        'updated_at',
        'member_count',
        'admin_count',
    ]

    fieldsets = [
        (_('Identification'), {
            'fields': [
                'code',
                'name',
                'acronym',
                'org_type',
            ]
        }),
        (_('Mandate & Functions'), {
            'fields': [
                'mandate',
                'powers',
            ],
            'classes': ['collapse'],
        }),
        (_('Module Activation'), {
            'description': _('Enable or disable specific BMMS modules for this organization'),
            'fields': [
                'enable_mana',
                'enable_planning',
                'enable_budgeting',
                'enable_me',
                'enable_coordination',
                'enable_policies',
            ],
        }),
        (_('Geographic Coverage'), {
            'fields': [
                'primary_region',
                'service_areas',
            ],
            'classes': ['collapse'],
        }),
        (_('Leadership'), {
            'fields': [
                'head_official',
                'head_title',
                'primary_focal_person',
            ],
        }),
        (_('Contact Information'), {
            'fields': [
                'email',
                'phone',
                'website',
                'address',
            ],
            'classes': ['collapse'],
        }),
        (_('Status & Onboarding'), {
            'fields': [
                'is_active',
                'is_pilot',
                'onboarding_date',
                'go_live_date',
            ],
        }),
        (_('Statistics'), {
            'fields': [
                'member_count',
                'admin_count',
                'created_at',
                'updated_at',
            ],
            'classes': ['collapse'],
        }),
    ]

    inlines = [OrganizationMembershipInline]

    def member_count_display(self, obj):
        """Display member count with color coding."""
        count = obj.member_count
        if count == 0:
            return format_html('<span style="color: red;">0 members</span>')
        elif count < 5:
            return format_html('<span style="color: orange;">{} members</span>', count)
        else:
            return format_html('<span style="color: green;">{} members</span>', count)

    member_count_display.short_description = _('Members')

    def enabled_modules_display(self, obj):
        """Display enabled modules as badges."""
        modules = obj.enabled_modules
        if not modules:
            return format_html('<span style="color: gray;">None</span>')

        badges = []
        module_colors = {
            'MANA': '#3b82f6',  # blue
            'Planning': '#10b981',  # green
            'Budgeting': '#f59e0b',  # amber
            'M&E': '#8b5cf6',  # purple
            'Coordination': '#06b6d4',  # cyan
            'Policies': '#ec4899',  # pink
        }

        for module in modules:
            color = module_colors.get(module, '#6b7280')
            badges.append(
                f'<span style="background-color: {color}; color: white; '
                f'padding: 2px 8px; border-radius: 4px; margin-right: 4px; '
                f'font-size: 11px;">{module}</span>'
            )

        return format_html(''.join(badges))

    enabled_modules_display.short_description = _('Enabled Modules')

    def save_model(self, request, obj, form, change):
        """Override save to log admin actions."""
        if not change:
            # New organization
            obj.save()
        else:
            # Existing organization
            obj.save()

        super().save_model(request, obj, form, change)


@admin.register(OrganizationMembership)
class OrganizationMembershipAdmin(admin.ModelAdmin):
    """
    Admin interface for OrganizationMembership model.

    Features:
    - Filter by organization, role, status
    - Search by user details
    - Inline permission management
    - Primary organization highlighting
    """

    list_display = [
        'user_display',
        'organization',
        'role',
        'is_primary_display',
        'is_active',
        'permissions_display',
        'joined_date',
    ]

    list_filter = [
        'organization',
        'role',
        'is_primary',
        'is_active',
        'can_manage_users',
        'can_approve_plans',
        'can_approve_budgets',
        'joined_date',
    ]

    search_fields = [
        'user__username',
        'user__email',
        'user__first_name',
        'user__last_name',
        'organization__code',
        'organization__name',
        'position',
        'department',
    ]

    ordering = ['organization', 'user__username']

    autocomplete_fields = ['user', 'organization']

    readonly_fields = ['joined_date', 'created_at', 'updated_at']

    fieldsets = [
        (_('Relationship'), {
            'fields': [
                'user',
                'organization',
            ]
        }),
        (_('Role & Position'), {
            'fields': [
                'role',
                'position',
                'department',
                'is_primary',
                'is_active',
            ]
        }),
        (_('Permissions'), {
            'description': _('Specific permissions for this user in this organization'),
            'fields': [
                'can_manage_users',
                'can_approve_plans',
                'can_approve_budgets',
                'can_view_reports',
            ]
        }),
        (_('Audit Information'), {
            'fields': [
                'joined_date',
                'created_at',
                'updated_at',
            ],
            'classes': ['collapse'],
        }),
    ]

    def user_display(self, obj):
        """Display user full name or username."""
        user_name = obj.user.get_full_name() or obj.user.username
        return format_html('<strong>{}</strong>', user_name)

    user_display.short_description = _('User')

    def is_primary_display(self, obj):
        """Display primary status with icon."""
        if obj.is_primary:
            return format_html(
                '<span style="color: #10b981;" title="Primary Organization">★</span>'
            )
        return ''

    is_primary_display.short_description = _('Primary')

    def permissions_display(self, obj):
        """Display permissions as badges."""
        permissions = []

        if obj.can_manage_users:
            permissions.append('Users')
        if obj.can_approve_plans:
            permissions.append('Plans')
        if obj.can_approve_budgets:
            permissions.append('Budgets')

        if not permissions:
            return format_html('<span style="color: gray;">View Only</span>')

        return format_html(
            '<span style="color: #10b981;">{}</span>',
            ', '.join(permissions)
        )

    permissions_display.short_description = _('Permissions')


# ========== ADMIN ACTIONS ==========


@admin.action(description=_('Activate selected organizations'))
def activate_organizations(modeladmin, request, queryset):
    """Admin action to activate multiple organizations."""
    queryset.update(is_active=True)


@admin.action(description=_('Deactivate selected organizations'))
def deactivate_organizations(modeladmin, request, queryset):
    """Admin action to deactivate multiple organizations."""
    queryset.update(is_active=False)


@admin.action(description=_('Mark as pilot organizations'))
def mark_as_pilot(modeladmin, request, queryset):
    """Admin action to mark organizations as pilot."""
    queryset.update(is_pilot=True)


# Register actions
OrganizationAdmin.actions = [
    activate_organizations,
    deactivate_organizations,
    mark_as_pilot,
]

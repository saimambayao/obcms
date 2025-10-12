"""
Common app admin interface.

This module consolidates all admin registrations for the common app.
Django admin autodiscovery uses this __init__.py since the admin/ directory exists.
"""

# Import all admin classes from the models admin file
from .models_admin import (
    UserAdmin,
    RegionAdmin,
    ProvinceAdmin,
    MunicipalityAdmin,
    BarangayAdmin,
    StaffTeamAdmin,
    StaffTeamMembershipAdmin,
    RecurringEventPatternAdmin,
    CalendarResourceAdmin,
    CalendarResourceBookingAdmin,
    CalendarNotificationAdmin,
    UserCalendarPreferencesAdmin,
    ExternalCalendarSyncAdmin,
    SharedCalendarLinkAdmin,
    StaffLeaveAdmin,
    WorkItemAdmin,
)

# Import all RBAC admin classes
from .rbac_admin import (
    FeatureAdmin,
    PermissionAdmin,
    RoleAdmin,
    RolePermissionAdmin,
    UserRoleAdmin,
    UserPermissionAdmin,
)

__all__ = [
    # User and geographic models
    'UserAdmin',
    'RegionAdmin',
    'ProvinceAdmin',
    'MunicipalityAdmin',
    'BarangayAdmin',
    # Staff and teams
    'StaffTeamAdmin',
    'StaffTeamMembershipAdmin',
    # Calendar system
    'RecurringEventPatternAdmin',
    'CalendarResourceAdmin',
    'CalendarResourceBookingAdmin',
    'CalendarNotificationAdmin',
    'UserCalendarPreferencesAdmin',
    'ExternalCalendarSyncAdmin',
    'SharedCalendarLinkAdmin',
    'StaffLeaveAdmin',
    # Work items
    'WorkItemAdmin',
    # RBAC
    'FeatureAdmin',
    'PermissionAdmin',
    'RoleAdmin',
    'RolePermissionAdmin',
    'UserRoleAdmin',
    'UserPermissionAdmin',
]

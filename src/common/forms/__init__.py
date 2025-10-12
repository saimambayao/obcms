"""Public form interfaces for the common app."""

from .auth import CustomLoginForm, UserProfileForm, UserRegistrationForm, MOARegistrationForm
from .calendar import (
    CalendarResourceBookingForm,
    CalendarResourceForm,
    StaffLeaveForm,
    # UserCalendarPreferencesForm,  # TODO: Model not yet implemented
)
from .community import (
    COMMUNITY_PROFILE_FIELDS,
    COMMUNITY_PROFILE_LABELS,
    COMMUNITY_PROFILE_WIDGETS,
    MunicipalityCoverageForm,
    ProvinceCoverageForm,
    OBCCommunityForm,
)
from .needs import CommunityNeedSubmissionForm
from .province import ProvinceForm
from .rbac_forms import (
    UserRoleAssignmentForm,
    UserPermissionForm,
    BulkRoleAssignmentForm,
    FeatureToggleForm,
    RolePermissionAssignmentForm,
)
from .staff import (
    PerformanceTargetForm,
    StaffDevelopmentPlanForm,
    StaffProfileForm,
    StaffTaskForm,  # DEPRECATED: Stub only - raises error on instantiation
    StaffTeamForm,
    StaffTeamMembershipForm,
    TrainingEnrollmentForm,
    TrainingProgramForm,
)

__all__ = [
    "CustomLoginForm",
    "UserProfileForm",
    "UserRegistrationForm",
    "MOARegistrationForm",
    "CalendarResourceForm",
    "CalendarResourceBookingForm",
    "StaffLeaveForm",
    # "UserCalendarPreferencesForm",  # TODO: Model not yet implemented
    "COMMUNITY_PROFILE_FIELDS",
    "COMMUNITY_PROFILE_LABELS",
    "COMMUNITY_PROFILE_WIDGETS",
    "MunicipalityCoverageForm",
    "ProvinceCoverageForm",
    "OBCCommunityForm",
    "CommunityNeedSubmissionForm",
    "ProvinceForm",
    "UserRoleAssignmentForm",
    "UserPermissionForm",
    "BulkRoleAssignmentForm",
    "FeatureToggleForm",
    "RolePermissionAssignmentForm",
    "StaffProfileForm",
    "StaffTeamForm",
    "StaffTeamMembershipForm",
    "StaffTaskForm",  # DEPRECATED: Stub only - raises error on instantiation
    "PerformanceTargetForm",
    "TrainingProgramForm",
    "TrainingEnrollmentForm",
    "StaffDevelopmentPlanForm",
]

"""
RBAC Management Forms

Forms for role-based access control management integrated with User Approvals.

Features:
- User role assignment with organization context
- Direct permission grants/denials
- Bulk role assignments
- Feature toggles
- Validation for BMMS multi-tenancy

See:
- src/common/rbac_models.py - RBAC models
- src/common/views/rbac_management.py - RBAC views
"""

from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone

from common.models import User
from common.rbac_models import (
    Feature,
    Permission,
    Role,
    UserRole,
    UserPermission,
)


class UserRoleAssignmentForm(forms.Form):
    """
    Form for assigning a role to a user with organization context.

    Fields:
    - role: Role to assign
    - organization: Organization context (optional for system roles)
    - expires_at: Optional expiration date
    """

    role = forms.ModelChoiceField(
        queryset=Role.objects.filter(is_active=True),
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'data-role-scope': 'true',
        }),
        help_text="Select role to assign"
    )

    organization = forms.ModelChoiceField(
        queryset=None,  # Set in __init__ based on user permissions
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select',
        }),
        help_text="Organization context (required for organization-scoped roles)"
    )

    expires_at = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(attrs={
            'type': 'datetime-local',
            'class': 'form-input',
        }),
        help_text="Optional expiration date for temporary access"
    )

    def __init__(self, *args, **kwargs):
        # Extract request user for organization filtering
        self.request_user = kwargs.pop('request_user', None)
        super().__init__(*args, **kwargs)

        # Set organization queryset based on user access
        if self.request_user:
            from coordination.models import Organization
            from common.services.rbac_service import RBACService

            # Get organizations the user can manage
            accessible_orgs = RBACService.get_organizations_with_access(self.request_user)
            self.fields['organization'].queryset = Organization.objects.filter(
                id__in=[org.id for org in accessible_orgs]
            ).order_by('name')
        else:
            from coordination.models import Organization
            self.fields['organization'].queryset = Organization.objects.filter(
                organization_type='bmoa',
                is_active=True
            ).order_by('name')

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get('role')
        organization = cleaned_data.get('organization')
        expires_at = cleaned_data.get('expires_at')

        # Validate organization requirement for organization-scoped roles
        if role and role.scope == 'organization' and not organization:
            raise ValidationError({
                'organization': f"Role '{role.name}' requires an organization context."
            })

        # System roles cannot have organization context
        if role and role.scope == 'system' and organization:
            raise ValidationError({
                'organization': f"System role '{role.name}' cannot be assigned to a specific organization."
            })

        # Validate expiration date
        if expires_at and expires_at <= timezone.now():
            raise ValidationError({
                'expires_at': "Expiration date must be in the future."
            })

        return cleaned_data


class UserPermissionForm(forms.Form):
    """
    Form for granting/denying direct permissions to users.

    Fields:
    - permission: Permission to grant/deny
    - is_granted: Grant (True) or deny (False)
    - organization: Organization context (optional)
    - expires_at: Optional expiration
    - reason: Justification for permission change
    """

    permission = forms.ModelChoiceField(
        queryset=Permission.objects.filter(is_active=True).select_related('feature'),
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-select',
        }),
        help_text="Select permission to grant/deny"
    )

    is_granted = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-checkbox',
        }),
        help_text="Check to grant permission, uncheck to explicitly deny"
    )

    organization = forms.ModelChoiceField(
        queryset=None,  # Set in __init__
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select',
        }),
        help_text="Organization context (optional)"
    )

    expires_at = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(attrs={
            'type': 'datetime-local',
            'class': 'form-input',
        }),
        help_text="Optional expiration for temporary access"
    )

    reason = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-textarea',
            'rows': 3,
            'placeholder': 'Reason for permission change...'
        }),
        help_text="Justification for this permission change (recommended)"
    )

    def __init__(self, *args, **kwargs):
        self.request_user = kwargs.pop('request_user', None)
        super().__init__(*args, **kwargs)

        # Set organization queryset
        if self.request_user:
            from coordination.models import Organization
            from common.services.rbac_service import RBACService

            accessible_orgs = RBACService.get_organizations_with_access(self.request_user)
            self.fields['organization'].queryset = Organization.objects.filter(
                id__in=[org.id for org in accessible_orgs]
            ).order_by('name')
        else:
            from coordination.models import Organization
            self.fields['organization'].queryset = Organization.objects.filter(
                organization_type='bmoa',
                is_active=True
            ).order_by('name')

    def clean(self):
        cleaned_data = super().clean()
        expires_at = cleaned_data.get('expires_at')

        # Validate expiration date
        if expires_at and expires_at <= timezone.now():
            raise ValidationError({
                'expires_at': "Expiration date must be in the future."
            })

        return cleaned_data


class BulkRoleAssignmentForm(forms.Form):
    """
    Form for assigning a role to multiple users at once.

    Fields:
    - users: Multiple users to assign role to
    - role: Role to assign
    - organization: Organization context (optional)
    - expires_at: Optional expiration
    """

    users = forms.ModelMultipleChoiceField(
        queryset=User.objects.filter(is_active=True),
        required=True,
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'form-checkbox-group',
        }),
        help_text="Select users to assign role to"
    )

    role = forms.ModelChoiceField(
        queryset=Role.objects.filter(is_active=True),
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-select',
        }),
        help_text="Role to assign to selected users"
    )

    organization = forms.ModelChoiceField(
        queryset=None,  # Set in __init__
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select',
        }),
        help_text="Organization context (required for organization-scoped roles)"
    )

    expires_at = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(attrs={
            'type': 'datetime-local',
            'class': 'form-input',
        }),
        help_text="Optional expiration for temporary access"
    )

    def __init__(self, *args, **kwargs):
        self.request_user = kwargs.pop('request_user', None)
        super().__init__(*args, **kwargs)

        # Set organization queryset
        if self.request_user:
            from coordination.models import Organization
            from common.services.rbac_service import RBACService

            accessible_orgs = RBACService.get_organizations_with_access(self.request_user)
            self.fields['organization'].queryset = Organization.objects.filter(
                id__in=[org.id for org in accessible_orgs]
            ).order_by('name')
        else:
            from coordination.models import Organization
            self.fields['organization'].queryset = Organization.objects.filter(
                organization_type='bmoa',
                is_active=True
            ).order_by('name')

        # Filter users based on request user's access
        if self.request_user:
            from common.services.rbac_service import RBACService

            # Superusers and OOBC staff can assign to any user
            if not (self.request_user.is_superuser or self.request_user.is_oobc_staff):
                # MOA staff can only assign within their organization
                if self.request_user.is_moa_staff and self.request_user.moa_organization:
                    self.fields['users'].queryset = User.objects.filter(
                        is_active=True,
                        moa_organization=self.request_user.moa_organization
                    )

    def clean(self):
        cleaned_data = super().clean()
        users = cleaned_data.get('users')
        role = cleaned_data.get('role')
        organization = cleaned_data.get('organization')
        expires_at = cleaned_data.get('expires_at')

        # Validate users selection
        if not users or users.count() == 0:
            raise ValidationError({
                'users': "At least one user must be selected."
            })

        # Validate organization requirement
        if role and role.scope == 'organization' and not organization:
            raise ValidationError({
                'organization': f"Role '{role.name}' requires an organization context."
            })

        # System roles cannot have organization context
        if role and role.scope == 'system' and organization:
            raise ValidationError({
                'organization': f"System role '{role.name}' cannot be assigned to a specific organization."
            })

        # Validate expiration date
        if expires_at and expires_at <= timezone.now():
            raise ValidationError({
                'expires_at': "Expiration date must be in the future."
            })

        return cleaned_data


class FeatureToggleForm(forms.Form):
    """
    Form for enabling/disabling features for users.

    Creates direct permission grants/denials for feature access.

    Fields:
    - is_granted: Enable (True) or disable (False) feature
    - organization: Organization context (optional)
    - expires_at: Optional expiration
    - reason: Justification for change
    """

    is_granted = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-checkbox toggle-switch',
        }),
        help_text="Enable or disable feature access"
    )

    organization = forms.ModelChoiceField(
        queryset=None,  # Set in __init__
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select',
        }),
        help_text="Organization context (optional)"
    )

    expires_at = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(attrs={
            'type': 'datetime-local',
            'class': 'form-input',
        }),
        help_text="Optional expiration for temporary access"
    )

    reason = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-textarea',
            'rows': 2,
            'placeholder': 'Reason for feature toggle...'
        }),
        help_text="Justification for this change (recommended)"
    )

    def __init__(self, *args, **kwargs):
        self.request_user = kwargs.pop('request_user', None)
        self.feature = kwargs.pop('feature', None)
        super().__init__(*args, **kwargs)

        # Set organization queryset
        if self.request_user:
            from coordination.models import Organization
            from common.services.rbac_service import RBACService

            accessible_orgs = RBACService.get_organizations_with_access(self.request_user)
            self.fields['organization'].queryset = Organization.objects.filter(
                id__in=[org.id for org in accessible_orgs]
            ).order_by('name')
        else:
            from coordination.models import Organization
            self.fields['organization'].queryset = Organization.objects.filter(
                organization_type='bmoa',
                is_active=True
            ).order_by('name')

        # If feature is organization-specific, make organization required
        if self.feature and self.feature.organization:
            self.fields['organization'].required = True
            self.fields['organization'].initial = self.feature.organization

    def clean(self):
        cleaned_data = super().clean()
        expires_at = cleaned_data.get('expires_at')
        organization = cleaned_data.get('organization')

        # Validate expiration date
        if expires_at and expires_at <= timezone.now():
            raise ValidationError({
                'expires_at': "Expiration date must be in the future."
            })

        # Validate organization requirement for organization-specific features
        if self.feature and self.feature.organization and not organization:
            raise ValidationError({
                'organization': f"Feature '{self.feature.name}' requires organization context."
            })

        return cleaned_data


class RolePermissionAssignmentForm(forms.Form):
    """
    Form for assigning permissions to roles.

    Used for role configuration and permission bundling.

    Fields:
    - permissions: Multiple permissions to assign
    - is_granted: Grant or deny permissions
    - expires_at: Optional expiration
    """

    permissions = forms.ModelMultipleChoiceField(
        queryset=Permission.objects.filter(is_active=True).select_related('feature'),
        required=True,
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'form-checkbox-group',
        }),
        help_text="Select permissions to assign to this role"
    )

    is_granted = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-checkbox',
        }),
        help_text="Grant or deny these permissions"
    )

    expires_at = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(attrs={
            'type': 'datetime-local',
            'class': 'form-input',
        }),
        help_text="Optional expiration for temporary permissions"
    )

    def clean(self):
        cleaned_data = super().clean()
        permissions = cleaned_data.get('permissions')
        expires_at = cleaned_data.get('expires_at')

        # Validate permissions selection
        if not permissions or permissions.count() == 0:
            raise ValidationError({
                'permissions': "At least one permission must be selected."
            })

        # Validate expiration date
        if expires_at and expires_at <= timezone.now():
            raise ValidationError({
                'expires_at': "Expiration date must be in the future."
            })

        return cleaned_data

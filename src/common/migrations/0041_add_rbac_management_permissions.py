# Generated manually to add RBAC management permissions

from django.db import migrations


def create_rbac_management_permissions(apps, schema_editor):
    """
    Create permissions for RBAC management interface.

    These permissions control access to the user approvals RBAC tab
    and RBAC management operations.
    """
    Feature = apps.get_model('common', 'Feature')
    Permission = apps.get_model('common', 'Permission')
    Role = apps.get_model('common', 'Role')
    RolePermission = apps.get_model('common', 'RolePermission')

    # Create RBAC Management feature
    rbac_management_feature, created = Feature.objects.get_or_create(
        feature_key='rbac_management',
        defaults={
            'name': 'RBAC Management',
            'description': 'Manage user roles, permissions, and access control',
            'module': 'oobc_management',
            'category': 'administration',
            'is_active': True,
            'sort_order': 100,
        }
    )

    if not created:
        print(f"Feature 'rbac_management' already exists")

    # Create permissions for RBAC management
    permissions_data = [
        {
            'codename': 'oobc_management.manage_user_permissions',
            'name': 'Manage User Permissions',
            'description': 'View and manage user permissions and roles',
            'permission_type': 'manage',
        },
        {
            'codename': 'oobc_management.assign_user_roles',
            'name': 'Assign User Roles',
            'description': 'Assign and remove roles from users',
            'permission_type': 'edit',
        },
        {
            'codename': 'oobc_management.manage_feature_access',
            'name': 'Manage Feature Access',
            'description': 'Enable or disable feature access for users',
            'permission_type': 'manage',
        },
        {
            'codename': 'oobc_management.view_rbac_config',
            'name': 'View RBAC Configuration',
            'description': 'View roles, features, and permission configuration',
            'permission_type': 'view',
        },
    ]

    created_permissions = []
    for perm_data in permissions_data:
        permission, created = Permission.objects.get_or_create(
            codename=perm_data['codename'],
            defaults={
                'feature': rbac_management_feature,
                'name': perm_data['name'],
                'description': perm_data['description'],
                'permission_type': perm_data['permission_type'],
                'is_active': True,
            }
        )

        if created:
            print(f"Created permission: {perm_data['codename']}")
            created_permissions.append(permission)
        else:
            print(f"Permission '{perm_data['codename']}' already exists")

    # Grant these permissions to Executive roles
    try:
        executive_role = Role.objects.get(slug='oobc-executive-director')
        deputy_role = Role.objects.get(slug='oobc-deputy-executive-director')

        for permission in created_permissions:
            # Grant to Executive Director
            RolePermission.objects.get_or_create(
                role=executive_role,
                permission=permission,
                defaults={
                    'is_active': True,
                }
            )

            # Grant to Deputy Executive Director
            RolePermission.objects.get_or_create(
                role=deputy_role,
                permission=permission,
                defaults={
                    'is_active': True,
                }
            )

        print(f"Granted RBAC management permissions to Executive and Deputy roles")

    except Role.DoesNotExist:
        print("Executive roles not found - skipping permission grants")


def reverse_rbac_management_permissions(apps, schema_editor):
    """
    Remove RBAC management permissions (for rollback).
    """
    Permission = apps.get_model('common', 'Permission')
    Feature = apps.get_model('common', 'Feature')

    # Delete permissions
    Permission.objects.filter(
        codename__in=[
            'oobc_management.manage_user_permissions',
            'oobc_management.assign_user_roles',
            'oobc_management.manage_feature_access',
            'oobc_management.view_rbac_config',
        ]
    ).delete()

    # Delete feature if no other permissions reference it
    try:
        feature = Feature.objects.get(feature_key='rbac_management')
        if not feature.permissions.exists():
            feature.delete()
    except Feature.DoesNotExist:
        pass


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0040_add_oobc_staff_rbac_restrictions'),
    ]

    operations = [
        migrations.RunPython(
            create_rbac_management_permissions,
            reverse_rbac_management_permissions
        ),
    ]

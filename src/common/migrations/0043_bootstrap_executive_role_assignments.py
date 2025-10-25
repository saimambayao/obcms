# Generated manually to bootstrap RBAC role assignments for existing executives

from django.db import migrations


def assign_executive_roles(apps, schema_editor):
    """
    Assign RBAC roles to existing OOBC Executive and Deputy Executive users.

    This bootstraps the RBAC system by giving existing executives the proper
    roles so they can access the RBAC management interface.
    """
    User = apps.get_model('common', 'User')
    Role = apps.get_model('common', 'Role')
    UserRole = apps.get_model('common', 'UserRole')

    try:
        # Get the executive roles
        exec_role = Role.objects.get(slug='oobc-executive-director')
        deputy_role = Role.objects.get(slug='oobc-deputy-executive-director')

        print("\n=== Bootstrapping RBAC Role Assignments ===")

        # Assign Executive Director role to all oobc_executive users
        executives = User.objects.filter(
            user_type='oobc_executive',
            is_active=True
        )

        exec_count = 0
        for user in executives:
            # Check if already assigned
            existing = UserRole.objects.filter(
                user=user,
                role=exec_role,
                is_active=True
            ).exists()

            if not existing:
                UserRole.objects.create(
                    user=user,
                    role=exec_role,
                    is_active=True,
                    assigned_at=user.date_joined,
                    # No assigned_by since this is automatic bootstrap
                )
                full_name = f"{user.first_name} {user.last_name}".strip() or user.username
                print(f"✓ Assigned OOBC Executive Director role to {full_name}")
                exec_count += 1
            else:
                full_name = f"{user.first_name} {user.last_name}".strip() or user.username
                print(f"  Already assigned: {full_name}")

        # Assign Deputy Executive Director role to all oobc_deputy_executive users
        deputies = User.objects.filter(
            user_type='oobc_deputy_executive',
            is_active=True
        )

        deputy_count = 0
        for user in deputies:
            # Check if already assigned
            existing = UserRole.objects.filter(
                user=user,
                role=deputy_role,
                is_active=True
            ).exists()

            if not existing:
                UserRole.objects.create(
                    user=user,
                    role=deputy_role,
                    is_active=True,
                    assigned_at=user.date_joined,
                )
                full_name = f"{user.first_name} {user.last_name}".strip() or user.username
                print(f"✓ Assigned OOBC Deputy Executive Director role to {full_name}")
                deputy_count += 1
            else:
                full_name = f"{user.first_name} {user.last_name}".strip() or user.username
                print(f"  Already assigned: {full_name}")

        print(f"\n✅ Bootstrap complete:")
        print(f"   - {exec_count} Executive Director roles assigned")
        print(f"   - {deputy_count} Deputy Executive Director roles assigned")

    except Role.DoesNotExist:
        print("⚠️  Executive roles not found - skipping role assignments")
        print("   Run migration 0040_add_oobc_staff_rbac_restrictions first")


def reverse_executive_roles(apps, schema_editor):
    """
    Remove bootstrapped role assignments (for rollback).
    """
    User = apps.get_model('common', 'User')
    Role = apps.get_model('common', 'Role')
    UserRole = apps.get_model('common', 'UserRole')

    try:
        # Get the executive roles
        exec_role = Role.objects.get(slug='oobc-executive-director')
        deputy_role = Role.objects.get(slug='oobc-deputy-executive-director')

        # Find all executive users
        executive_users = User.objects.filter(
            user_type__in=['oobc_executive', 'oobc_deputy_executive']
        )

        # Remove role assignments (deactivate, don't delete for audit trail)
        removed_count = UserRole.objects.filter(
            user__in=executive_users,
            role__in=[exec_role, deputy_role],
            is_active=True
        ).update(is_active=False)

        print(f"Removed {removed_count} bootstrapped role assignments")

    except Role.DoesNotExist:
        pass


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0040_add_oobc_staff_rbac_restrictions'),
        ('common', '0041_add_rbac_management_permissions'),
        ('common', '0042_migrate_organization_to_moa_organization'),
    ]

    operations = [
        migrations.RunPython(
            assign_executive_roles,
            reverse_executive_roles
        ),
    ]

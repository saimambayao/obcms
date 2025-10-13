# Generated manually to assign OOBC Staff roles for RBAC restrictions

from django.db import migrations


def assign_oobc_staff_roles(apps, schema_editor):
    """
    Assign OOBC Staff role to all existing OOBC Staff users.

    This enforces RBAC restrictions on OOBC Staff users, limiting their
    access to specific modules based on the role permissions defined in
    migration 0040_add_oobc_staff_rbac_restrictions.

    RBAC Restrictions (from migration 0040):
    - ❌ NO access to: MANA, Recommendations, Planning & Budgeting,
      Project Management, User Approvals
    - ✅ Access to: Communities, Coordination, other common features
    """
    User = apps.get_model('common', 'User')
    Role = apps.get_model('common', 'Role')
    UserRole = apps.get_model('common', 'UserRole')

    try:
        # Get the OOBC Staff role
        staff_role = Role.objects.get(slug='oobc-staff')

        print("\n=== Assigning OOBC Staff Roles ===")

        # Find all OOBC Staff users
        staff_users = User.objects.filter(
            user_type='oobc_staff',
            is_active=True
        )

        assigned_count = 0
        skipped_count = 0

        for user in staff_users:
            # Check if role already assigned
            existing = UserRole.objects.filter(
                user=user,
                role=staff_role,
                is_active=True
            ).exists()

            if not existing:
                UserRole.objects.create(
                    user=user,
                    role=staff_role,
                    is_active=True,
                    assigned_at=user.date_joined,
                    # No assigned_by since this is automatic bootstrap
                )
                full_name = f"{user.first_name} {user.last_name}".strip() or user.username
                print(f"✓ Assigned OOBC Staff role to {full_name}")
                assigned_count += 1
            else:
                full_name = f"{user.first_name} {user.last_name}".strip() or user.username
                print(f"  Already assigned: {full_name}")
                skipped_count += 1

        print(f"\n✅ OOBC Staff role assignment complete:")
        print(f"   - {assigned_count} new role assignments")
        print(f"   - {skipped_count} already assigned")

        if assigned_count > 0:
            print("\n⚠️  IMPORTANT: OOBC Staff users now have RBAC restrictions:")
            print("   - No access to: MANA, Recommendations, Planning & Budgeting,")
            print("     Project Management, User Approvals")
            print("   - Executives can grant individual permissions via RBAC Management")

    except Role.DoesNotExist:
        print("⚠️  OOBC Staff role not found - skipping role assignments")
        print("   Run migration 0040_add_oobc_staff_rbac_restrictions first")


def reverse_oobc_staff_roles(apps, schema_editor):
    """
    Remove OOBC Staff role assignments (for rollback).

    IMPORTANT: This removes RBAC restrictions, giving OOBC Staff
    full access again. Use with caution.
    """
    User = apps.get_model('common', 'User')
    Role = apps.get_model('common', 'Role')
    UserRole = apps.get_model('common', 'UserRole')

    try:
        # Get the OOBC Staff role
        staff_role = Role.objects.get(slug='oobc-staff')

        # Find all OOBC Staff users
        staff_users = User.objects.filter(user_type='oobc_staff')

        # Deactivate role assignments (keep for audit trail)
        removed_count = UserRole.objects.filter(
            user__in=staff_users,
            role=staff_role,
            is_active=True
        ).update(is_active=False)

        print(f"\n✅ Removed {removed_count} OOBC Staff role assignments")
        print("⚠️  OOBC Staff now have full access again (no RBAC restrictions)")

    except Role.DoesNotExist:
        pass


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0043_bootstrap_executive_role_assignments'),
    ]

    operations = [
        migrations.RunPython(
            assign_oobc_staff_roles,
            reverse_oobc_staff_roles
        ),
    ]

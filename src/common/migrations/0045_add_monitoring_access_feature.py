# Generated manually to add monitoring_access RBAC feature

from django.db import migrations


def add_monitoring_access_feature(apps, schema_editor):
    """
    Add monitoring_access (M&E) feature to RBAC system.

    This feature controls access to the Monitoring & Evaluation module.
    OOBC Staff role will NOT have this permission by default.
    """
    Feature = apps.get_model('common', 'Feature')
    Permission = apps.get_model('common', 'Permission')
    Role = apps.get_model('common', 'Role')
    RolePermission = apps.get_model('common', 'RolePermission')

    print("\n=== Adding monitoring_access RBAC Feature ===")

    # Create monitoring_access feature
    monitoring_feature, created = Feature.objects.get_or_create(
        feature_key='monitoring_access',
        defaults={
            'name': 'Monitoring & Evaluation Module Access',
            'description': 'Access to M&E dashboards, metrics, and analytics',
            'module': 'monitoring',
            'category': 'module',
            'is_active': True,
            'sort_order': 40,
        }
    )

    if created:
        print(f"✓ Created feature: {monitoring_feature.name}")
    else:
        print(f"  Feature already exists: {monitoring_feature.name}")

    # Create view permission for monitoring
    view_permission, created = Permission.objects.get_or_create(
        feature=monitoring_feature,
        codename='view_monitoring',
        defaults={
            'name': 'View M&E Module',
            'description': 'Can view monitoring and evaluation dashboards',
            'permission_type': 'view',
            'is_active': True,
        }
    )

    if created:
        print(f"✓ Created permission: {view_permission.name}")
    else:
        print(f"  Permission already exists: {view_permission.name}")

    # Grant access to Executive roles ONLY (NOT OOBC Staff)
    try:
        exec_role = Role.objects.get(slug='oobc-executive-director')
        deputy_role = Role.objects.get(slug='oobc-deputy-executive-director')

        # Grant to Executive Director
        exec_perm, created = RolePermission.objects.get_or_create(
            role=exec_role,
            permission=view_permission,
            defaults={
                'is_granted': True,
                'is_active': True,
            }
        )
        if created:
            print(f"✓ Granted monitoring_access to: {exec_role.name}")
        else:
            print(f"  Already granted to: {exec_role.name}")

        # Grant to Deputy Executive Director
        deputy_perm, created = RolePermission.objects.get_or_create(
            role=deputy_role,
            permission=view_permission,
            defaults={
                'is_granted': True,
                'is_active': True,
            }
        )
        if created:
            print(f"✓ Granted monitoring_access to: {deputy_role.name}")
        else:
            print(f"  Already granted to: {deputy_role.name}")

        # Verify OOBC Staff does NOT have access
        staff_role = Role.objects.get(slug='oobc-staff')
        staff_has_access = RolePermission.objects.filter(
            role=staff_role,
            permission=view_permission,
            is_granted=True,
            is_active=True
        ).exists()

        if staff_has_access:
            print(f"⚠️  WARNING: OOBC Staff has monitoring_access - this should NOT happen!")
        else:
            print(f"✓ Confirmed: OOBC Staff does NOT have monitoring_access (correct)")

    except Role.DoesNotExist:
        print("⚠️  Executive roles not found - permissions not assigned")

    print("\n✅ monitoring_access feature setup complete")
    print("   - Executives: ✅ CAN access M&E")
    print("   - OOBC Staff: ❌ CANNOT access M&E")


def reverse_monitoring_access(apps, schema_editor):
    """Remove monitoring_access feature (for rollback)."""
    Feature = apps.get_model('common', 'Feature')

    try:
        feature = Feature.objects.get(feature_key='monitoring_access')
        # Just deactivate, don't delete (for audit trail)
        feature.is_active = False
        feature.save()
        print("Deactivated monitoring_access feature")
    except Feature.DoesNotExist:
        pass


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0044_assign_oobc_staff_roles'),
    ]

    operations = [
        migrations.RunPython(
            add_monitoring_access_feature,
            reverse_monitoring_access
        ),
    ]

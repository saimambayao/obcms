from django.db import migrations


def backfill_moa_organization(apps, schema_editor):
    """Backfill moa_organization FK from organization CharField."""
    User = apps.get_model('common', 'User')
    Organization = apps.get_model('coordination', 'Organization')

    # Get all MOA users
    moa_users = User.objects.filter(user_type__in=['bmoa', 'lgu', 'nga'])

    updated_count = 0
    for user in moa_users:
        if not user.organization:
            continue

        # Try to find matching organization by name
        try:
            org = Organization.objects.get(
                name__iexact=user.organization.strip(),
                organization_type='bmoa'
            )
            user.moa_organization = org
            user.save(update_fields=['moa_organization'])
            updated_count += 1
        except Organization.MultipleObjectsReturned:
            # Multiple orgs found - use the oldest one
            org = Organization.objects.filter(
                name__iexact=user.organization.strip(),
                organization_type='bmoa'
            ).order_by('created_at').first()
            if org:
                user.moa_organization = org
                user.save(update_fields=['moa_organization'])
                updated_count += 1
                print(f"Warning: Multiple orgs found for user {user.username}, using oldest")
            else:
                print(f"Warning: No org found for user {user.username} (org: {user.organization})")
        except Organization.DoesNotExist:
            print(f"Warning: No org found for user {user.username} (org: {user.organization})")

    print(f"Backfilled moa_organization for {updated_count} MOA users")


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0031_add_moa_organization_fk'),
    ]

    operations = [
        migrations.RunPython(backfill_moa_organization, migrations.RunPython.noop),
    ]

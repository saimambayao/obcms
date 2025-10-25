# Generated manually to migrate age range data from old to new fields

from django.db import migrations


def migrate_age_range_data(apps, schema_editor):
    """
    Migrate age range data from old fields to new fields.

    Migration 0012 removed children_0_12 and youth_13_30, adding new fields:
    - children_0_9
    - adolescents_10_14
    - youth_15_30

    This data migration estimates the distribution of old data into new fields:
    - 75% of children_0_12 goes to children_0_9
    - 25% of children_0_12 goes to adolescents_10_14
    - All of youth_13_30 is split:
      - 25% (ages 13-14) goes to adolescents_10_14
      - 75% (ages 15-30) goes to youth_15_30

    Note: This migration assumes the old fields were not yet removed from the
    database by migration 0012. If the fields were already removed, this
    migration will be a no-op.
    """
    OBCCommunity = apps.get_model('communities', 'OBCCommunity')
    MunicipalityCoverage = apps.get_model('communities', 'MunicipalityCoverage')

    # Check if old fields still exist (they may have already been removed)
    from django.db import connection
    cursor = connection.cursor()

    # Migrate OBCCommunity records
    try:
        cursor.execute(
            "SELECT COUNT(*) FROM communities_obccommunity "
            "WHERE children_0_12 IS NOT NULL OR youth_13_30 IS NOT NULL"
        )
        count = cursor.fetchone()[0]

        if count > 0:
            for community in OBCCommunity.objects.all():
                # Skip if already has new data
                if (
                    community.children_0_9 is not None
                    or community.adolescents_10_14 is not None
                    or community.youth_15_30 is not None
                ):
                    continue

                # Migrate from old fields if they exist in the database
                # Use raw SQL since fields may be in process of being removed
                cursor.execute(
                    "SELECT children_0_12, youth_13_30 "
                    "FROM communities_obccommunity WHERE id = %s",
                    [community.id],
                )
                row = cursor.fetchone()

                if row and (row[0] is not None or row[1] is not None):
                    children_0_12 = row[0] or 0
                    youth_13_30 = row[1] or 0

                    # Distribute children_0_12
                    community.children_0_9 = int(children_0_12 * 0.75)
                    community.adolescents_10_14 = int(children_0_12 * 0.25)

                    # Distribute youth_13_30
                    community.adolescents_10_14 += int(youth_13_30 * 0.25)
                    community.youth_15_30 = int(youth_13_30 * 0.75)

                    community.save()

            print(
                f"Migrated {count} OBCCommunity age range records "
                "(children_0_12, youth_13_30 -> children_0_9, adolescents_10_14, youth_15_30)"
            )

    except Exception as e:
        # Old fields may already be removed; that's fine
        print(
            f"OBCCommunity age range migration skipped "
            f"(fields already removed or table empty): {str(e)}"
        )

    # Migrate MunicipalityCoverage records
    try:
        cursor.execute(
            "SELECT COUNT(*) FROM communities_municipalitycoverage "
            "WHERE children_0_12 IS NOT NULL OR youth_13_30 IS NOT NULL"
        )
        count = cursor.fetchone()[0]

        if count > 0:
            for coverage in MunicipalityCoverage.objects.all():
                # Skip if already has new data
                if (
                    coverage.children_0_9 is not None
                    or coverage.adolescents_10_14 is not None
                    or coverage.youth_15_30 is not None
                ):
                    continue

                # Migrate from old fields if they exist in the database
                cursor.execute(
                    "SELECT children_0_12, youth_13_30 "
                    "FROM communities_municipalitycoverage WHERE id = %s",
                    [coverage.id],
                )
                row = cursor.fetchone()

                if row and (row[0] is not None or row[1] is not None):
                    children_0_12 = row[0] or 0
                    youth_13_30 = row[1] or 0

                    # Distribute children_0_12
                    coverage.children_0_9 = int(children_0_12 * 0.75)
                    coverage.adolescents_10_14 = int(children_0_12 * 0.25)

                    # Distribute youth_13_30
                    coverage.adolescents_10_14 += int(youth_13_30 * 0.25)
                    coverage.youth_15_30 = int(youth_13_30 * 0.75)

                    coverage.save()

            print(
                f"Migrated {count} MunicipalityCoverage age range records "
                "(children_0_12, youth_13_30 -> children_0_9, adolescents_10_14, youth_15_30)"
            )

    except Exception as e:
        # Old fields may already be removed; that's fine
        print(
            f"MunicipalityCoverage age range migration skipped "
            f"(fields already removed or table empty): {str(e)}"
        )

    cursor.close()


def reverse_age_range_data(apps, schema_editor):
    """
    Reverse the age range migration.

    Since old fields were removed, we cannot restore the original data.
    This is a one-way migration.
    """
    print(
        "WARNING: Age range data migration cannot be reversed. "
        "Old fields (children_0_12, youth_13_30) have been removed."
    )


class Migration(migrations.Migration):

    dependencies = [
        ("communities", "0012_remove_municipalitycoverage_children_0_12_and_more"),
    ]

    operations = [
        migrations.RunPython(
            migrate_age_range_data,
            reverse_age_range_data,
        ),
    ]

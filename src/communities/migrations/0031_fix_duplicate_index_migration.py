# Generated migration to fix duplicate index conflicts in test databases

from django.db import migrations, connection


def safe_rename_index(apps, schema_editor):
    """Safely rename index only if old name exists"""
    with connection.cursor() as cursor:
        # Check if old index exists before attempting to rename
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='index'
            AND name='communities_spatia_communi_8a49cd_idx'
        """)
        if cursor.fetchone():
            cursor.execute("""
                ALTER TABLE communities_spatialdatapoint
                RENAME INDEX communities_spatia_communi_8a49cd_idx
                TO communities_communi_896657_idx
            """)


def safe_rename_index_reverse(apps, schema_editor):
    """Reverse operation - safe rename only if new name exists"""
    with connection.cursor() as cursor:
        # Check if new index exists before attempting to rename back
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='index'
            AND name='communities_communi_896657_idx'
        """)
        if cursor.fetchone():
            cursor.execute("""
                ALTER TABLE communities_spatialdatapoint
                RENAME INDEX communities_communi_896657_idx
                TO communities_spatia_communi_8a49cd_idx
            """)


class Migration(migrations.Migration):

    dependencies = [
        ('communities', '0030_make_organization_required'),
    ]

    operations = [
        migrations.RunPython(safe_rename_index, safe_rename_index_reverse, atomic=False),
    ]
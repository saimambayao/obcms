"""Data migration to migrate MonitoringEntryTaskAssignment to StaffTask."""

from django.db import migrations


def _safe_get_model(apps, app_label, model_name):
    """Return historical model if available, else None."""

    try:
        return apps.get_model(app_label, model_name)
    except LookupError:
        return None


def migrate_monitoring_tasks(apps, schema_editor):
    """Migrate existing MonitoringEntryTaskAssignment records to StaffTask."""
    MonitoringEntryTaskAssignment = _safe_get_model(
        apps, 'monitoring', 'MonitoringEntryTaskAssignment'
    )
    StaffTask = _safe_get_model(apps, 'common', 'StaffTask')

    if not MonitoringEntryTaskAssignment or not StaffTask:
        # Historical model removed in new deployments; nothing to migrate.
        print("MonitoringEntryTaskAssignment model unavailable; skipping migration.")
        return

    migrated_count = 0
    
    for mta in MonitoringEntryTaskAssignment.objects.all():
        # Create corresponding StaffTask
        task = StaffTask.objects.create(
            title=mta.title,
            description=mta.notes or '',
            status='completed' if mta.status == 'completed' else 'in_progress' if mta.status == 'in_progress' else 'not_started',
            priority='medium',  # Default priority
            domain='monitoring',
            task_role=mta.role,
            estimated_hours=mta.estimated_hours,
            actual_hours=mta.actual_hours,
            completed_at=mta.completed_at,
            created_at=mta.created_at,
            updated_at=mta.updated_at,
            related_ppa=mta.monitoring_entry,
            created_by=mta.assigned_to,
        )
        
        # Add assignee
        if mta.assigned_to:
            task.assignees.add(mta.assigned_to)
        
        migrated_count += 1
    
    print(f"Migrated {migrated_count} MonitoringEntryTaskAssignment records to StaffTask")


def reverse_migration(apps, schema_editor):
    """Reverse migration - delete migrated StaffTasks."""
    StaffTask = _safe_get_model(apps, 'common', 'StaffTask')
    if not StaffTask:
        return
    
    # Delete all monitoring domain tasks (those migrated from MonitoringEntryTaskAssignment)
    deleted_count = StaffTask.objects.filter(domain='monitoring').delete()[0]
    print(f"Deleted {deleted_count} migrated StaffTask records")


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0014_tasktemplate_tasktemplateitem_stafftask_actual_hours_and_more'),
        ('monitoring', '0001_initial'),  # Adjust this to actual monitoring migration
    ]

    operations = [
        migrations.RunPython(migrate_monitoring_tasks, reverse_migration),
    ]

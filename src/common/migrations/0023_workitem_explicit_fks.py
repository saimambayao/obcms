# Generated migration for WorkItem explicit foreign key fields
# This migration adds explicit FK fields to replace generic FK usage for better performance

from django.db import migrations, models
import django.db.models.deletion


def migrate_generic_to_explicit_fks(apps, schema_editor):
    """
    Data migration: Convert existing GenericFK relationships to explicit FK fields.

    Maps content_type + object_id to appropriate explicit FK:
    - monitoring.MonitoringEntry -> related_ppa
    - mana.Assessment -> related_assessment
    - policy_tracking.PolicyRecommendation -> related_policy
    """
    WorkItem = apps.get_model('common', 'WorkItem')
    ContentType = apps.get_model('contenttypes', 'ContentType')

    # Get ContentType instances
    try:
        monitoring_ct = ContentType.objects.get(app_label='monitoring', model='monitoringentry')
    except ContentType.DoesNotExist:
        monitoring_ct = None

    try:
        assessment_ct = ContentType.objects.get(app_label='mana', model='assessment')
    except ContentType.DoesNotExist:
        assessment_ct = None

    try:
        policy_ct = ContentType.objects.get(app_label='policy_tracking', model='policyrecommendation')
    except ContentType.DoesNotExist:
        policy_ct = None

    # Migrate WorkItems with generic FK to explicit FK
    updated_count = 0

    for work_item in WorkItem.objects.select_related('content_type').filter(
        content_type__isnull=False,
        object_id__isnull=False
    ):
        if monitoring_ct and work_item.content_type_id == monitoring_ct.id:
            work_item.related_ppa_id = work_item.object_id
            work_item.save(update_fields=['related_ppa_id'])
            updated_count += 1

        elif assessment_ct and work_item.content_type_id == assessment_ct.id:
            work_item.related_assessment_id = work_item.object_id
            work_item.save(update_fields=['related_assessment_id'])
            updated_count += 1

        elif policy_ct and work_item.content_type_id == policy_ct.id:
            work_item.related_policy_id = work_item.object_id
            work_item.save(update_fields=['related_policy_id'])
            updated_count += 1

    if updated_count > 0:
        print(f"✓ Migrated {updated_count} WorkItem relationships from generic FK to explicit FK")


def reverse_migration(apps, schema_editor):
    """
    Reverse migration: Copy explicit FK back to generic FK fields.
    """
    WorkItem = apps.get_model('common', 'WorkItem')
    ContentType = apps.get_model('contenttypes', 'ContentType')

    # Get ContentType instances
    try:
        monitoring_ct = ContentType.objects.get(app_label='monitoring', model='monitoringentry')
    except ContentType.DoesNotExist:
        monitoring_ct = None

    try:
        assessment_ct = ContentType.objects.get(app_label='mana', model='assessment')
    except ContentType.DoesNotExist:
        assessment_ct = None

    try:
        policy_ct = ContentType.objects.get(app_label='policy_tracking', model='policyrecommendation')
    except ContentType.DoesNotExist:
        policy_ct = None

    # Restore generic FK from explicit FK
    updated_count = 0

    # Restore from related_ppa
    if monitoring_ct:
        for work_item in WorkItem.objects.filter(related_ppa_id__isnull=False):
            work_item.content_type = monitoring_ct
            work_item.object_id = work_item.related_ppa_id
            work_item.save(update_fields=['content_type', 'object_id'])
            updated_count += 1

    # Restore from related_assessment
    if assessment_ct:
        for work_item in WorkItem.objects.filter(related_assessment_id__isnull=False):
            work_item.content_type = assessment_ct
            work_item.object_id = work_item.related_assessment_id
            work_item.save(update_fields=['content_type', 'object_id'])
            updated_count += 1

    # Restore from related_policy
    if policy_ct:
        for work_item in WorkItem.objects.filter(related_policy_id__isnull=False):
            work_item.content_type = policy_ct
            work_item.object_id = work_item.related_policy_id
            work_item.save(update_fields=['content_type', 'object_id'])
            updated_count += 1

    if updated_count > 0:
        print(f"✓ Restored {updated_count} WorkItem relationships from explicit FK to generic FK")


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0022_eventproxy_projectworkflowproxy_stafftaskproxy'),
        ('monitoring', '0017_add_model_validation_constraints'),
        ('mana', '0021_add_needvote_model'),
        ('policy_tracking', '0007_policyrecommendation_target_barangay_and_more'),
    ]

    operations = [
        # ========== ADD MISSING EXPLICIT FOREIGN KEY FIELDS ==========
        # Note: related_ppa and budget fields already exist in model

        migrations.AddField(
            model_name='workitem',
            name='related_assessment',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='work_items',
                to='mana.assessment',
                help_text='Related MANA Assessment',
            ),
        ),
        migrations.AddField(
            model_name='workitem',
            name='related_policy',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='work_items',
                to='policy_tracking.policyrecommendation',
                help_text='Related Policy Recommendation',
            ),
        ),

        # ========== ADD DATABASE INDEXES FOR PERFORMANCE ==========

        migrations.AddIndex(
            model_name='workitem',
            index=models.Index(
                fields=['related_assessment'],
                name='workitem_related_assessment_idx',
            ),
        ),
        migrations.AddIndex(
            model_name='workitem',
            index=models.Index(
                fields=['related_policy'],
                name='workitem_related_policy_idx',
            ),
        ),

        # ========== DATA MIGRATION ==========

        migrations.RunPython(
            migrate_generic_to_explicit_fks,
            reverse_code=reverse_migration,
        ),
    ]

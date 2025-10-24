# Generated migration to fix case-sensitivity in WorkItem ForeignKey reference
# Migration fixes ValueError: budget_execution.workitem vs budget_execution.WorkItem

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('budget_execution', '0004_alter_workitem_estimated_cost'),
    ]

    operations = [
        migrations.AlterField(
            model_name='obligation',
            name='work_item',
            field=models.ForeignKey(
                blank=True,
                help_text='Execution work item covered by this obligation',
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='obligations',
                to='budget_execution.WorkItem',  # Fixed: Changed from 'workitem' to 'WorkItem'
            ),
        ),
    ]

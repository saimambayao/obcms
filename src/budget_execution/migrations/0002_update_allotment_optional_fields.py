from django.core.exceptions import FieldDoesNotExist
from django.db import migrations, models
import django.db.models.deletion


def column_exists(schema_editor, table_name, column_name):
    with schema_editor.connection.cursor() as cursor:
        cursor.execute(f"PRAGMA table_info({table_name})")
        return any(row[1] == column_name for row in cursor.fetchall())


class AlterFieldIfExists(migrations.AlterField):
    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        from_model = from_state.apps.get_model(app_label, self.model_name)
        try:
            from_field = from_model._meta.get_field(self.name)
        except FieldDoesNotExist:
            return
        table_name = from_model._meta.db_table
        if not column_exists(schema_editor, table_name, from_field.column):
            return
        super().database_forwards(app_label, schema_editor, from_state, to_state)

    def database_backwards(self, app_label, schema_editor, from_state, to_state):
        to_model = to_state.apps.get_model(app_label, self.model_name)
        try:
            to_field = to_model._meta.get_field(self.name)
        except FieldDoesNotExist:
            return
        table_name = to_model._meta.db_table
        if not column_exists(schema_editor, table_name, to_field.column):
            return
        super().database_backwards(app_label, schema_editor, from_state, to_state)


class Migration(migrations.Migration):

    dependencies = [
        ('budget_execution', '0001_initial'),
        ('common', '0001_initial'),
    ]

    operations = [
        AlterFieldIfExists(
            model_name='allotment',
            name='released_by',
            field=models.ForeignKey(
                blank=True,
                help_text='Budget execution user who released the allotment',
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='allotments_released',
                to='common.user',
            ),
        ),
        AlterFieldIfExists(
            model_name='disbursement',
            name='disbursed_by',
            field=models.ForeignKey(
                blank=True,
                help_text='User who processed the disbursement',
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='disbursements_processed',
                to='common.user',
            ),
        ),
        AlterFieldIfExists(
            model_name='obligation',
            name='work_item',
            field=models.ForeignKey(
                blank=True,
                help_text='Execution work item covered by this obligation',
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='obligations',
                to='budget_execution.WorkItem',  # Fixed: Changed from 'workitem' to 'WorkItem' for case-sensitivity
            ),
        ),
        AlterFieldIfExists(
            model_name='obligation',
            name='obligated_by',
            field=models.ForeignKey(
                blank=True,
                help_text='User who recorded the obligation',
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='obligations_recorded',
                to='common.user',
            ),
        ),
        AlterFieldIfExists(
            model_name='obligation',
            name='payee',
            field=models.CharField(
                blank=True,
                default='',
                help_text='Payee or supplier name',
                max_length=255,
            ),
        ),
    ]

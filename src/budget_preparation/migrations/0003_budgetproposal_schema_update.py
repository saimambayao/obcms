# Generated manually to align BudgetProposal schema with updated model fields.
from decimal import Decimal

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('budget_preparation', '0002_use_new_organization_model'),
    ]

    operations = [
        migrations.RenameField(
            model_name='budgetproposal',
            old_name='total_proposed_budget',
            new_name='total_requested_budget',
        ),
        migrations.RenameField(
            model_name='budgetproposal',
            old_name='reviewed_by',
            new_name='approved_by',
        ),
        migrations.RenameField(
            model_name='budgetproposal',
            old_name='reviewed_at',
            new_name='approved_at',
        ),
        migrations.AlterField(
            model_name='budgetproposal',
            name='fiscal_year',
            field=models.PositiveIntegerField(
                help_text='Fiscal year this budget proposal covers',
                validators=[django.core.validators.MinValueValidator(2024)],
            ),
        ),
        migrations.AddField(
            model_name='budgetproposal',
            name='total_approved_budget',
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                max_digits=15,
                null=True,
                validators=[django.core.validators.MinValueValidator(Decimal('0.00'))],
                help_text='Total budget amount approved (₱)',
            ),
        ),
        migrations.AlterField(
            model_name='budgetproposal',
            name='status',
            field=models.CharField(
                choices=[
                    ('draft', 'Draft'),
                    ('submitted', 'Submitted'),
                    ('under_review', 'Under Review'),
                    ('approved', 'Approved'),
                    ('rejected', 'Rejected'),
                ],
                default='draft',
                help_text='Current review status of the proposal',
                max_length=20,
            ),
        ),
        migrations.AlterField(
            model_name='budgetproposal',
            name='submitted_by',
            field=models.ForeignKey(
                blank=True,
                help_text='User who submitted this proposal',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='submitted_budget_proposals',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name='budgetproposal',
            name='total_requested_budget',
            field=models.DecimalField(
                decimal_places=2,
                max_digits=15,
                help_text='Total budget amount requested (₱)',
                validators=[django.core.validators.MinValueValidator(Decimal('0.00'))],
            ),
        ),
        migrations.AlterField(
            model_name='budgetproposal',
            name='approved_by',
            field=models.ForeignKey(
                blank=True,
                help_text='Approving authority',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='approved_budget_proposals',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]

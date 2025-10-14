# Generated manually for BMMS Phase 5 - Communities app migration (Step 3)
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0001_initial'),
        ('communities', '0029_add_organization_field'),
    ]

    operations = [
        # Make organization field required (NOT NULL) on all 11 models

        migrations.AlterField(
            model_name='obccommunity',
            name='organization',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name='communities_obccommunity_set',
                to='organizations.organization',
                help_text='Organization that owns this record'
            ),
        ),
        migrations.AlterField(
            model_name='communitylivelihood',
            name='organization',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name='communities_communitylivelihood_set',
                to='organizations.organization',
                help_text='Organization that owns this record'
            ),
        ),
        migrations.AlterField(
            model_name='communityinfrastructure',
            name='organization',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name='communities_communityinfrastructure_set',
                to='organizations.organization',
                help_text='Organization that owns this record'
            ),
        ),
        migrations.AlterField(
            model_name='stakeholder',
            name='organization',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name='communities_stakeholder_set',
                to='organizations.organization',
                help_text='Organization that owns this record'
            ),
        ),
        migrations.AlterField(
            model_name='stakeholderengagement',
            name='organization',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name='communities_stakeholderengagement_set',
                to='organizations.organization',
                help_text='Organization that owns this record'
            ),
        ),
        migrations.AlterField(
            model_name='municipalitycoverage',
            name='organization',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name='communities_municipalitycoverage_set',
                to='organizations.organization',
                help_text='Organization that owns this record'
            ),
        ),
        migrations.AlterField(
            model_name='provincecoverage',
            name='organization',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name='communities_provincecoverage_set',
                to='organizations.organization',
                help_text='Organization that owns this record'
            ),
        ),
        migrations.AlterField(
            model_name='geographicdatalayer',
            name='organization',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name='communities_geographicdatalayer_set',
                to='organizations.organization',
                help_text='Organization that owns this record'
            ),
        ),
        migrations.AlterField(
            model_name='mapvisualization',
            name='organization',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name='communities_mapvisualization_set',
                to='organizations.organization',
                help_text='Organization that owns this record'
            ),
        ),
        migrations.AlterField(
            model_name='spatialdatapoint',
            name='organization',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name='communities_spatialdatapoint_set',
                to='organizations.organization',
                help_text='Organization that owns this record'
            ),
        ),
        migrations.AlterField(
            model_name='communityevent',
            name='organization',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name='communities_communityevent_set',
                to='organizations.organization',
                help_text='Organization that owns this record'
            ),
        ),
    ]

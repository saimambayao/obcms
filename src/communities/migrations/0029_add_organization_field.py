# Generated manually for BMMS Phase 5 - Communities app migration
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0001_initial'),
        ('communities', '0028_clear_municipal_estimated_population'),
    ]

    operations = [
        # Add nullable organization field to all 11 organization-scoped models

        migrations.AddField(
            model_name='obccommunity',
            name='organization',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='communities_obccommunity_set',
                to='organizations.organization'
            ),
        ),
        migrations.AddField(
            model_name='communitylivelihood',
            name='organization',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='communities_communitylivelihood_set',
                to='organizations.organization'
            ),
        ),
        migrations.AddField(
            model_name='communityinfrastructure',
            name='organization',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='communities_communityinfrastructure_set',
                to='organizations.organization'
            ),
        ),
        migrations.AddField(
            model_name='stakeholder',
            name='organization',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='communities_stakeholder_set',
                to='organizations.organization'
            ),
        ),
        migrations.AddField(
            model_name='stakeholderengagement',
            name='organization',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='communities_stakeholderengagement_set',
                to='organizations.organization'
            ),
        ),
        migrations.AddField(
            model_name='municipalitycoverage',
            name='organization',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='communities_municipalitycoverage_set',
                to='organizations.organization'
            ),
        ),
        migrations.AddField(
            model_name='provincecoverage',
            name='organization',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='communities_provincecoverage_set',
                to='organizations.organization'
            ),
        ),
        migrations.AddField(
            model_name='geographicdatalayer',
            name='organization',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='communities_geographicdatalayer_set',
                to='organizations.organization'
            ),
        ),
        migrations.AddField(
            model_name='mapvisualization',
            name='organization',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='communities_mapvisualization_set',
                to='organizations.organization'
            ),
        ),
        migrations.AddField(
            model_name='spatialdatapoint',
            name='organization',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='communities_spatialdatapoint_set',
                to='organizations.organization'
            ),
        ),
        migrations.AddField(
            model_name='communityevent',
            name='organization',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='communities_communityevent_set',
                to='organizations.organization'
            ),
        ),

        # Add indexes for performance on key models
        migrations.AddIndex(
            model_name='obccommunity',
            index=models.Index(fields=['organization'], name='communities_communi_896657_idx'),
        ),
        migrations.AddIndex(
            model_name='stakeholder',
            index=models.Index(fields=['organization'], name='communities_stakeh_org_idx'),
        ),
        migrations.AddIndex(
            model_name='municipalitycoverage',
            index=models.Index(fields=['organization'], name='communities_munici_org_idx'),
        ),
    ]

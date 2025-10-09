from django.db import migrations, models
from django.db.models import Q


FUNDING_SOURCE_CHOICES = [
    (
        "gaab_2025",
        "General Appropriations Act of the Bangsamoro (GAAB) 2025",
    ),
    ("supplemental_budget", "Supplemental Budget (SB)"),
    ("sdf", "Special Development Fund (SDF)"),
    ("tdif", "Transitional Development Impact Fund (TDIF)"),
    ("allocation_for_mp", "Allocation for MP"),
    (
        "national_program",
        "National Program (from the National Government)",
    ),
    (
        "local_program",
        "Local Program (from the Local Government)",
    ),
    ("oda", "Official Development Assistance (ODA)"),
    ("other_sources", "Other Funding Sources"),
]


VALID_FUNDING_SOURCES = {choice[0] for choice in FUNDING_SOURCE_CHOICES}
GAAB_2025 = "gaab_2025"
OTHER_SOURCES = "other_sources"


def tag_gaab_funding(apps, schema_editor):
    MonitoringEntry = apps.get_model("monitoring", "MonitoringEntry")
    MonitoringEntryFunding = apps.get_model("monitoring", "MonitoringEntryFunding")

    gaab_update = {
        "funding_source": GAAB_2025,
        "funding_source_other": "",
    }
    MonitoringEntry.objects.filter(category="moa_ppa").update(**gaab_update)

    MonitoringEntry.objects.exclude(
        Q(funding_source__in=VALID_FUNDING_SOURCES) | Q(funding_source__exact="")
    ).update(
        funding_source=OTHER_SOURCES,
        funding_source_other="",
    )

    moa_entries = MonitoringEntry.objects.filter(category="moa_ppa")
    MonitoringEntryFunding.objects.filter(entry__in=moa_entries).update(
        funding_source=GAAB_2025,
        funding_source_other="",
    )

    MonitoringEntryFunding.objects.exclude(
        Q(funding_source__in=VALID_FUNDING_SOURCES) | Q(funding_source__exact="")
    ).update(
        funding_source=OTHER_SOURCES,
        funding_source_other="",
    )


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("monitoring", "0020_monitoringentry_auto_sync_progress_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="monitoringentry",
            name="funding_source",
            field=models.CharField(
                blank=True,
                choices=FUNDING_SOURCE_CHOICES,
                help_text="Primary funding source",
                max_length=32,
            ),
        ),
        migrations.AlterField(
            model_name="monitoringentry",
            name="funding_source_other",
            field=models.CharField(
                blank=True,
                help_text="Specify funding source when tagged as Other Funding Sources",
                max_length=255,
            ),
        ),
        migrations.AlterField(
            model_name="monitoringentryfunding",
            name="funding_source",
            field=models.CharField(
                blank=True,
                choices=FUNDING_SOURCE_CHOICES,
                help_text="Override funding source for this tranche",
                max_length=32,
            ),
        ),
        migrations.AlterField(
            model_name="monitoringentryfunding",
            name="funding_source_other",
            field=models.CharField(
                blank=True,
                help_text="Specify the funding source when using Other Funding Sources",
                max_length=255,
            ),
        ),
        migrations.RunPython(tag_gaab_funding, noop),
    ]

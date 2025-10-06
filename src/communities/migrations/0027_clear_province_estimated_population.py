from django.db import migrations


def clear_estimated_obc_population(apps, schema_editor):
    ProvinceCoverage = apps.get_model("communities", "ProvinceCoverage")
    ProvinceCoverage.objects.filter(
        estimated_obc_population__isnull=False
    ).update(estimated_obc_population=None)


def noop(apps, schema_editor):
    """Reverse noop placeholder."""


class Migration(migrations.Migration):

    dependencies = [
        ("communities", "0026_communityevent"),
    ]

    operations = [
        migrations.RunPython(clear_estimated_obc_population, noop),
    ]

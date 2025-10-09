from django.db import migrations


def link_sibling_related_items(apps, schema_editor):
    WorkItem = apps.get_model('common', 'WorkItem')

    # Fetch all non-root work items with their related links prefetched
    items = (
        WorkItem.objects
        .filter(parent__isnull=False)
        .select_related('parent')
        .prefetch_related('related_items')
    )

    # Group items by parent for efficient sibling iteration
    siblings_by_parent = {}
    for item in items:
        siblings_by_parent.setdefault(item.parent_id, []).append(item)

    for siblings in siblings_by_parent.values():
        for index, item in enumerate(siblings):
            for sibling in siblings[index + 1:]:
                if not item.related_items.filter(pk=sibling.pk).exists():
                    item.related_items.add(sibling)
                if not sibling.related_items.filter(pk=item.pk).exists():
                    sibling.related_items.add(item)


class Migration(migrations.Migration):

    dependencies = [
        ("common", "0032_backfill_moa_organization"),
    ]

    operations = [
        migrations.RunPython(
            link_sibling_related_items,
            migrations.RunPython.noop,
        ),
    ]

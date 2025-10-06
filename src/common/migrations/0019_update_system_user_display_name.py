from django.db import migrations


def update_system_user_name(apps, schema_editor):  # pragma: no cover - data fix
    User = apps.get_model("common", "User")

    try:
        user = User.objects.get(username="system")
    except User.DoesNotExist:
        return

    desired_values = {"first_name": "OBCMS", "last_name": "Admin"}
    updates = {}

    for field, value in desired_values.items():
        if getattr(user, field) != value:
            setattr(user, field, value)
            updates[field] = value

    if updates:
        user.save(update_fields=list(updates.keys()))


def restore_system_user_name(apps, schema_editor):  # pragma: no cover - data fix
    User = apps.get_model("common", "User")

    try:
        user = User.objects.get(username="system")
    except User.DoesNotExist:
        return

    original_values = {"first_name": "System", "last_name": "User"}
    updates = {}

    for field, value in original_values.items():
        if getattr(user, field) != value:
            setattr(user, field, value)
            updates[field] = value

    if updates:
        user.save(update_fields=list(updates.keys()))


class Migration(migrations.Migration):

    dependencies = [
        ("common", "0018_stafftask_task_context_and_more"),
    ]

    operations = [
        migrations.RunPython(update_system_user_name, restore_system_user_name),
    ]

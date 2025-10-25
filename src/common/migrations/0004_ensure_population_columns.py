from django.db import connection, migrations, models


def ensure_population_fields(apps, schema_editor):
    """
    Add population_total columns when they are missing due to legacy databases.

    Security:
    - Uses connection.ops.quote_name() for SQL identifier quoting
    - Uses parameterized queries for values
    - Prevents SQL injection via proper escaping
    """

    cursor = connection.cursor()
    introspection = connection.introspection

    def column_exists(table_name: str, column_name: str) -> bool:
        try:
            description = introspection.get_table_description(cursor, table_name)
        except Exception:
            return False
        return any(col.name == column_name for col in description)

    def add_column_if_missing(model_label: str, table_name: str, field_name: str):
        if column_exists(table_name, field_name):
            return

        model = apps.get_model("common", model_label)
        field = models.PositiveIntegerField(default=0)
        field.set_attributes_from_name(field_name)
        schema_editor.add_field(model, field)

        # Ensure nulls are backfilled to zero for compatibility
        # SECURITY FIX: Use quote_name() for identifiers and parameterized query for values
        sql = "UPDATE {} SET {} = %s WHERE {} IS NULL".format(
            connection.ops.quote_name(table_name),
            connection.ops.quote_name(field_name),
            connection.ops.quote_name(field_name)
        )
        cursor.execute(sql, [0])

    add_column_if_missing("Barangay", "common_barangay", "population_total")
    add_column_if_missing("Municipality", "common_municipality", "population_total")
    add_column_if_missing("Province", "common_province", "population_total")


class Migration(migrations.Migration):
    dependencies = [
        ("common", "0003_initial"),
    ]

    operations = [migrations.RunPython(ensure_population_fields, migrations.RunPython.noop)]

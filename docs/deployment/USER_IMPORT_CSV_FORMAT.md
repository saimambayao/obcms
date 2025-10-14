# Pilot User CSV Import Format

The `import_pilot_users` management command accepts UTF-8 CSV files using the schema
below. Download `data/examples/pilot_users_template.csv` for a ready-to-use template.

## Required Columns
- `email`
- `first_name`
- `last_name`
- `organization` (organization code, e.g., `MOH`)
- `role` (see [Pilot Role Assignment](ROLE_ASSIGNMENT.md))

## Optional Columns
- `phone`
- `department`
- `position`

## Example
```csv
email,first_name,last_name,organization,role,phone,department,position
jane.doe@moh.gov.ph,Jane,Doe,MOH,planner,+639171234567,Planning Division,Senior Planner
```

## Execution
```bash
python manage.py import_pilot_users pilot_users.csv --dry-run
python manage.py import_pilot_users pilot_users.csv --send-emails
```

Errors are reported with row numbers. The command stops after processing the file and
returns a non-zero exit code if any row fails when not running in dry-run mode.

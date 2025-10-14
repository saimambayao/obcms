# Pilot Role Assignment

The BMMS pilot leverages Django groups as role containers managed by
`PilotRoleService`. Each role bundles permissions across planning and budgeting apps.

## Role Definitions

| Role | Description | Key Permissions |
| --- | --- | --- |
| `pilot_admin` | Full pilot administration | Manage organizations, planning, budgeting |
| `planner` | Planning module lead | Create/update strategic plans and work plans |
| `budget_officer` | Budget execution focal | Manage program budgets and allotments |
| `me_officer` | Monitoring & Evaluation officer | Manage monitoring entries |
| `viewer` | Read-only | View planning and budgeting data |

Permissions synchronize automatically during role assignment. Missing permissions are
logged for investigation.

## Management Command
```bash
python manage.py assign_role <username> <role>
```

## Service API
```python
from organizations.services import PilotRoleService
service = PilotRoleService()
service.ensure_roles_exist()
service.assign_role(user, "planner")
```

## Governance
- Review group membership monthly during the pilot
- Use audit logs to trace changes (search for `organizations.services.role_service` in logs)
- Keep the role catalogue in sync with documentation to avoid drift

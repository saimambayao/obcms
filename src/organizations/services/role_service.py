"""Role management utilities for BMMS pilot onboarding."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Iterable, List

from django.contrib.auth.models import Group, Permission
from django.db import transaction

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class RoleDefinition:
    """Configuration describing a pilot role."""

    name: str
    description: str
    permissions: Iterable[str]


class PilotRoleService:
    """Utility helpers for provisioning pilot user roles."""

    DEFAULT_ROLES: List[RoleDefinition] = [
        RoleDefinition(
            name="pilot_admin",
            description="Pilot Administrator with full organization access",
            permissions=[
                "organizations.view_organization",
                "organizations.change_organization",
                "planning.view_strategicplan",
                "planning.add_strategicplan",
                "planning.change_strategicplan",
                "budget_preparation.view_budgetproposal",
                "budget_preparation.add_budgetproposal",
                "budget_execution.view_allotment",
                "budget_execution.add_allotment",
            ],
        ),
        RoleDefinition(
            name="planner",
            description="Planning officer with access to planning module",
            permissions=[
                "planning.view_strategicplan",
                "planning.add_strategicplan",
                "planning.change_strategicplan",
                "planning.view_annualworkplan",
                "planning.add_annualworkplan",
                "planning.change_annualworkplan",
            ],
        ),
        RoleDefinition(
            name="budget_officer",
            description="Budget officer managing allocations and execution",
            permissions=[
                "budget_preparation.view_budgetproposal",
                "budget_preparation.add_budgetproposal",
                "budget_preparation.change_budgetproposal",
                "budget_execution.view_allotment",
                "budget_execution.add_allotment",
                "budget_execution.change_allotment",
            ],
        ),
        RoleDefinition(
            name="me_officer",
            description="Monitoring and Evaluation officer",
            permissions=[
                "monitoring.view_monitoringentry",
                "monitoring.add_monitoringentry",
                "monitoring.change_monitoringentry",
            ],
        ),
        RoleDefinition(
            name="viewer",
            description="Read-only access across enabled modules",
            permissions=[
                "organizations.view_organization",
                "planning.view_strategicplan",
                "planning.view_annualworkplan",
                "budget_preparation.view_budgetproposal",
                "budget_execution.view_allotment",
            ],
        ),
    ]

    def __init__(self) -> None:
        self._role_map = {definition.name: definition for definition in self.DEFAULT_ROLES}

    def ensure_roles_exist(self) -> None:
        """Ensure that pilot role groups exist with the configured permissions."""

        for definition in self.DEFAULT_ROLES:
            with transaction.atomic():
                group, created = Group.objects.get_or_create(name=definition.name)
                if created:
                    logger.info("Created pilot role group '%s'", definition.name)
                self._synchronize_group_permissions(group, definition.permissions)

    def _synchronize_group_permissions(self, group: Group, permissions: Iterable[str]) -> None:
        """Sync Django group permissions with the configured codename list."""

        resolved_permissions = []
        for perm in permissions:
            try:
                app_label, codename = perm.split(".", 1)
            except ValueError:
                logger.warning("Invalid permission string '%s' - expected app_label.codename", perm)
                continue
            permission = Permission.objects.filter(
                content_type__app_label=app_label, codename=codename
            ).first()
            if permission:
                resolved_permissions.append(permission)
            else:
                logger.warning("Permission %s not found in database", perm)

        current_permissions = set(group.permissions.all())
        target_permissions = set(resolved_permissions)

        to_add = target_permissions - current_permissions
        to_remove = current_permissions - target_permissions

        if to_add:
            group.permissions.add(*to_add)
        if to_remove:
            group.permissions.remove(*to_remove)

        if to_add or to_remove:
            logger.info(
                "Updated permissions for group '%s' (added=%s, removed=%s)",
                group.name,
                len(to_add),
                len(to_remove),
            )

    def assign_role(self, user, role_name: str) -> Group:
        """Assign a role to a user, ensuring the group exists first."""

        if role_name not in self._role_map:
            raise ValueError(f"Unknown pilot role: {role_name}")

        self.ensure_roles_exist()
        group = Group.objects.get(name=role_name)
        user.groups.add(group)
        logger.info("Assigned role '%s' to user %s", role_name, user.username)
        return group

    def available_roles(self) -> List[str]:
        """Return list of registered pilot role identifiers."""

        return sorted(self._role_map)


__all__ = ["PilotRoleService", "RoleDefinition"]

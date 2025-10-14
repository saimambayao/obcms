"""Pilot user management service for Phase 7 onboarding."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Optional

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.db import transaction
from django.utils.crypto import get_random_string

from organizations.models import Organization, OrganizationMembership

from .role_service import PilotRoleService

logger = logging.getLogger(__name__)

UserModel = get_user_model()


@dataclass
class PilotUserResult:
    """Return value for created pilot users."""

    user: UserModel
    raw_password: str


class PilotUserService:
    """High-level orchestration for creating pilot users and memberships."""

    def __init__(self, role_service: Optional[PilotRoleService] = None) -> None:
        self.role_service = role_service or PilotRoleService()

    def generate_password(self, length: Optional[int] = None) -> str:
        length = length or getattr(settings, "PILOT_DEFAULT_PASSWORD_LENGTH", 16)
        return get_random_string(length, allowed_chars="abcdefghjkmnpqrstuvwxyzABCDEFGHJKMNPQRSTUVWXYZ23456789@#$%")

    @transaction.atomic
    def create_pilot_user(
        self,
        *,
        username: str,
        email: str,
        organization_code: str,
        role: str,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        phone: Optional[str] = None,
        position: Optional[str] = None,
        department: Optional[str] = None,
        password: Optional[str] = None,
        send_welcome_email: bool = True,
    ) -> PilotUserResult:
        """Create a pilot user with the supplied attributes."""

        organization = Organization.objects.filter(code__iexact=organization_code).first()
        if not organization:
            raise Organization.DoesNotExist(
                f"Organization with code '{organization_code}' not found. Run load_pilot_moas first."
            )

        if UserModel.objects.filter(username=username).exists():
            raise ValueError(f"Username '{username}' already exists")
        if UserModel.objects.filter(email=email).exists():
            raise ValueError(f"Email '{email}' already exists")

        raw_password = password or self.generate_password()

        user = UserModel(
            username=username,
            email=email,
            first_name=first_name or "",
            last_name=last_name or "",
            password=make_password(raw_password),
            user_type="bmoa",
            organization=organization.name,
            position=position or "",
            contact_number=phone or "",
            is_active=True,
            is_approved=True,
        )
        user.save()

        OrganizationMembership.objects.create(
            user=user,
            organization=organization,
            role="staff",
            is_primary=True,
            department=department or "",
            position=position or "",
            can_manage_users=role == "pilot_admin",
            can_approve_plans=role in {"pilot_admin", "planner"},
            can_approve_budgets=role in {"pilot_admin", "budget_officer"},
        )

        self.role_service.assign_role(user, role)

        if send_welcome_email:
            try:
                from organizations.tasks import send_pilot_welcome_email

                send_pilot_welcome_email.delay(user.pk, raw_password)
            except Exception:  # pragma: no cover - avoid failing user creation due to Celery issues
                logger.exception("Failed to queue welcome email for %s", user.email)

        logger.info("Created pilot user %s (%s) for organization %s", user.username, user.email, organization.code)
        return PilotUserResult(user=user, raw_password=raw_password)

    def update_role(self, user, role: str) -> None:
        """Update role assignments for an existing user."""

        self.role_service.assign_role(user, role)


__all__ = ["PilotUserService", "PilotUserResult"]

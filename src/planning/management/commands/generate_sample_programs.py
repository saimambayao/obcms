"""Generate planning sample data for pilot MOAs."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
import random

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from organizations.models import Organization
from planning.models import (
    StrategicPlan,
    StrategicGoal,
    AnnualWorkPlan,
    WorkPlanObjective,
)

UserModel = get_user_model()


class Command(BaseCommand):
    help = "Generate strategic plans, goals, and work plan objectives for a pilot organization"

    def add_arguments(self, parser):  # type: ignore[override]
        parser.add_argument("--organization", required=True, help="Organization code (e.g., MOH)")
        parser.add_argument("--programs", type=int, default=3, help="Number of objectives/programs to create")
        parser.add_argument("--year", type=int, default=timezone.now().year)

    def handle(self, *args, **options):  # type: ignore[override]
        try:
            organization = Organization.objects.get(code__iexact=options["organization"])
        except Organization.DoesNotExist as exc:
            raise CommandError("Organization not found. Run load_pilot_moas first.") from exc

        created_by = UserModel.objects.filter(is_superuser=True).first() or UserModel.objects.first()
        if not created_by:
            raise CommandError("At least one user is required to assign as creator")

        start_year = options["year"] - 1
        end_year = options["year"] + 3

        plan_title = f"{organization.name} Strategic Plan {start_year}-{end_year}"
        strategic_plan, created = StrategicPlan.objects.get_or_create(
            title=plan_title,
            defaults={
                "start_year": start_year,
                "end_year": end_year,
                "vision": f"Transformational services for {organization.name} communities",
                "mission": f"Deliver coordinated programs for {organization.name}",
                "status": "active",
                "created_by": created_by,
            },
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f"Created strategic plan '{plan_title}'"))

        annual_plan, created = AnnualWorkPlan.objects.get_or_create(
            strategic_plan=strategic_plan,
            year=options["year"],
            defaults={
                "title": f"{organization.name} Annual Work Plan {options['year']}",
                "description": "Auto-generated pilot work plan",
                "status": "active",
                "created_by": created_by,
            },
        )
        if created:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Created annual work plan for {organization.code} ({options['year']})"
                )
            )

        for index in range(options["programs"]):
            goal_title = f"{organization.name} Strategic Goal {index + 1}"
            goal, _ = StrategicGoal.objects.get_or_create(
                strategic_plan=strategic_plan,
                title=goal_title,
                defaults={
                    "description": f"Advance priority initiative {index + 1} for {organization.acronym}",
                    "target_metric": "beneficiaries_served",
                    "target_value": Decimal("100.00"),
                    "current_value": Decimal("0.00"),
                    "completion_percentage": Decimal("0"),
                    "priority": "high" if index == 0 else "medium",
                    "status": "in_progress",
                },
            )

            objective_title = f"{organization.name} Objective {index + 1}"
            WorkPlanObjective.objects.get_or_create(
                annual_work_plan=annual_plan,
                strategic_goal=goal,
                title=objective_title,
                defaults={
                    "description": f"Execute program {index + 1} for {organization.acronym}",
                    "target_date": date(options["year"], min(12, 3 * (index + 1)), 28),
                    "completion_percentage": Decimal(str(random.randint(10, 40))),
                    "indicator": "households_supported",
                    "baseline_value": Decimal("0.00"),
                    "target_value": Decimal("100.00"),
                    "current_value": Decimal("0.00"),
                    "status": "in_progress",
                },
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"Planning data ready for {organization.code} ({options['programs']} objectives)"
            )
        )

"""Backfill newly introduced planning and budgeting metadata."""

from __future__ import annotations

from collections import Counter
from datetime import date

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from monitoring.models import (
    MonitoringEntry,
    MonitoringEntryFunding,
    MonitoringEntryWorkflowStage,
)


class Command(BaseCommand):
    """Populate default workflow stages and funding flows for existing entries."""

    help = (
        "Backfill planning/budgeting metadata, funding flows, and workflow stages"
        " for existing monitoring entries."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Preview changes without writing to the database.",
        )

    def handle(self, *args, **options):
        dry_run: bool = options.get("dry_run", False)
        stats: Counter[str] = Counter()

        stage_keys = [
            stage for stage, _label in MonitoringEntryWorkflowStage.STAGE_CHOICES
        ]
        today: date = timezone.now().date()

        queryset = MonitoringEntry.objects.all()
        entry_total = queryset.count()

        for entry in queryset:
            with transaction.atomic():
                stats["entries"] += 1
                stats.update(self._backfill_entry_metadata(entry, dry_run))
                stats.update(self._ensure_workflow_stages(entry, stage_keys, dry_run))
                stats.update(self._ensure_funding_flows(entry, today, dry_run))

        summary_lines = [
            f"Processed entries: {stats['entries']} / {entry_total}",
            f"Updated entries: {stats['entry_updates']}",
            f"Stages created: {stats['stages_created']}",
            f"Allocation flows created: {stats['allocations_created']}",
        ]
        if stats.get("ceiling_backfill"):
            summary_lines.append(
                f"Budget ceilings defaulted: {stats['ceiling_backfill']}"
            )
        message = "\n".join(summary_lines)
        if dry_run:
            self.stdout.write(self.style.WARNING(f"[DRY-RUN] {message}"))
        else:
            self.stdout.write(self.style.SUCCESS(message))

    def _backfill_entry_metadata(
        self, entry: MonitoringEntry, dry_run: bool
    ) -> Counter[str]:
        updates: Counter[str] = Counter()
        fields_to_update: list[str] = []

        reference_date = (
            entry.start_date
            or entry.target_end_date
            or entry.actual_end_date
            or (entry.created_at.date() if entry.created_at else None)
        )
        if reference_date and not entry.plan_year:
            entry.plan_year = reference_date.year
            fields_to_update.append("plan_year")
            updates["plan_year_backfill"] += 1

        if entry.plan_year and not entry.fiscal_year:
            entry.fiscal_year = entry.plan_year
            fields_to_update.append("fiscal_year")
            updates["fiscal_year_backfill"] += 1

        if entry.budget_allocation and not entry.budget_ceiling:
            entry.budget_ceiling = entry.budget_allocation
            fields_to_update.append("budget_ceiling")
            updates["ceiling_backfill"] += 1

        if not entry.funding_source:
            entry.funding_source = MonitoringEntry.FUNDING_SOURCE_OTHERS
            fields_to_update.append("funding_source")
            updates["funding_source_default"] += 1

        if isinstance(entry.goal_alignment, str):
            goal_tags = [
                token.strip()
                for token in entry.goal_alignment.split(",")
                if token.strip()
            ]
            entry.goal_alignment = goal_tags
            fields_to_update.append("goal_alignment")
            updates["goal_alignment_normalised"] += 1

        if fields_to_update and not dry_run:
            entry.save(update_fields=fields_to_update)
            updates["entry_updates"] = 1
        elif fields_to_update:
            updates["entry_updates"] = 1

        return updates

    def _ensure_workflow_stages(
        self,
        entry: MonitoringEntry,
        stage_keys: list[str],
        dry_run: bool,
    ) -> Counter[str]:
        updates: Counter[str] = Counter()
        existing = set(entry.workflow_stages.values_list("stage", flat=True))
        missing = [stage for stage in stage_keys if stage not in existing]

        for stage in missing:
            updates["stages_created"] += 1
            if not dry_run:
                MonitoringEntryWorkflowStage.objects.create(
                    entry=entry,
                    stage=stage,
                    status=MonitoringEntryWorkflowStage.STATUS_NOT_STARTED,
                )
        return updates

    def _ensure_funding_flows(
        self,
        entry: MonitoringEntry,
        today: date,
        dry_run: bool,
    ) -> Counter[str]:
        updates: Counter[str] = Counter()
        has_allocation = entry.funding_flows.filter(
            tranche_type=MonitoringEntryFunding.TRANCHE_ALLOCATION
        ).exists()

        if entry.budget_allocation and not has_allocation:
            updates["allocations_created"] += 1
            scheduled = entry.start_date or entry.created_at.date() or today
            funding_source = (
                entry.funding_source or MonitoringEntry.FUNDING_SOURCE_OTHERS
            )
            if not dry_run:
                MonitoringEntryFunding.objects.create(
                    entry=entry,
                    tranche_type=MonitoringEntryFunding.TRANCHE_ALLOCATION,
                    amount=entry.budget_allocation,
                    funding_source=funding_source,
                    scheduled_date=scheduled,
                    created_by=entry.created_by,
                    updated_by=entry.updated_by,
                    remarks="Backfilled from existing budget allocation.",
                )
        return updates

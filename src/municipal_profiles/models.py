from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional

from django.conf import settings
from django.db import models
from django.utils import timezone

from common.models import Municipality
from .aggregation import flatten_metrics, normalise_reported_metrics


class TimeStampedModel(models.Model):
    """Abstract base model providing created/updated timestamps."""

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class MunicipalOBCProfile(TimeStampedModel):
    """Stores municipal level OBC information."""

    STATUS_DRAFT = "draft"
    STATUS_SUBMITTED = "submitted"
    STATUS_APPROVED = "approved"
    STATUS_RETURNED = "returned"

    STATUS_CHOICES = [
        (STATUS_DRAFT, "Draft"),
        (STATUS_SUBMITTED, "Submitted"),
        (STATUS_APPROVED, "Approved"),
        (STATUS_RETURNED, "Returned for Revision"),
    ]

    municipality = models.OneToOneField(
        Municipality,
        on_delete=models.CASCADE,
        related_name="obc_profile",
        help_text="Municipality or city covered by this profile.",
    )
    aggregated_metrics = models.JSONField(
        default=dict,
        blank=True,
        help_text="Roll-up metrics derived from all barangay OBC records.",
    )
    reported_metrics = models.JSONField(
        default=dict,
        blank=True,
        help_text="Municipal level metrics manually encoded by LGU partners.",
    )
    reported_notes = models.TextField(
        blank=True,
        help_text="Narrative notes accompanying the latest municipal submission.",
    )
    reported_status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_DRAFT,
        help_text="Workflow status for the latest municipal submission.",
    )
    reported_signatories = models.JSONField(
        default=list,
        blank=True,
        help_text="List of municipal signatories acknowledging the reported data.",
    )
    last_aggregated_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp of the most recent automatic aggregation run.",
    )
    last_reported_update = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp of the most recent manual municipal update.",
    )
    last_reported_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="municipal_profiles_reported",
        help_text="User who last submitted municipal reported metrics.",
    )
    reported_submitted_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp when the municipal report was submitted for review.",
    )
    aggregation_version = models.PositiveIntegerField(
        default=0,
        help_text="Version counter for the aggregation pipeline.",
    )
    is_locked = models.BooleanField(
        default=False,
        help_text="Lock manual edits while undergoing validation or review.",
    )

    class Meta:
        verbose_name = "Municipal OBC Profile"
        verbose_name_plural = "Municipal OBC Profiles"
        ordering = ["municipality__province__region__code", "municipality__name"]

    def __str__(self) -> str:
        return f"OBC Profile for {self.municipality.name}"

    # --- History helpers -------------------------------------------------
    def log_history(
        self,
        *,
        change_type: str,
        payload: Dict[str, Any],
        changed_by: Optional[models.Model] = None,
        note: str = "",
        diff: Optional[Dict[str, Any]] = None,
    ) -> "MunicipalOBCProfileHistory":
        """Persist a history entry for auditing purposes."""

        return MunicipalOBCProfileHistory.objects.create(
            profile=self,
            change_type=change_type,
            payload=payload or {},
            changed_by=changed_by,
            note=note,
            diff=diff or {},
        )

    def apply_aggregation(
        self,
        *,
        aggregated_payload: Dict[str, Any],
        changed_by: Optional[models.Model] = None,
        note: str = "",
        history_payload: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Persist aggregation results and capture an audit record."""

        previous_payload = self.aggregated_metrics or {}
        previous_sections = normalise_reported_metrics(previous_payload.get("sections"))
        previous_flat = flatten_metrics(previous_sections)
        previous_metadata = (
            previous_payload.get("metadata")
            if isinstance(previous_payload.get("metadata"), dict)
            else {}
        )

        current_sections = normalise_reported_metrics(
            (aggregated_payload or {}).get("sections")
        )
        current_flat = flatten_metrics(current_sections)
        current_metadata = (
            aggregated_payload.get("metadata")
            if isinstance(aggregated_payload.get("metadata"), dict)
            else {}
        )

        metrics_diff: Dict[str, Dict[str, Any]] = {}
        for key in sorted(set(previous_flat) | set(current_flat)):
            before_value = previous_flat.get(key, 0)
            after_value = current_flat.get(key, 0)
            if before_value != after_value:
                metrics_diff[key] = {
                    "before": before_value,
                    "after": after_value,
                    "delta": after_value - before_value,
                }

        metadata_diff: Dict[str, Dict[str, Any]] = {}
        metadata_keys = sorted(
            set(previous_metadata.keys()) | set(current_metadata.keys())
        )
        for key in metadata_keys:
            before_value = previous_metadata.get(key)
            after_value = current_metadata.get(key)
            if before_value != after_value:
                metadata_diff[key] = {
                    "before": before_value,
                    "after": after_value,
                }

        now = timezone.now()
        self.aggregated_metrics = aggregated_payload or {}
        self.last_aggregated_at = now
        self.aggregation_version = self.aggregation_version + 1
        self.save(
            update_fields=[
                "aggregated_metrics",
                "last_aggregated_at",
                "aggregation_version",
                "updated_at",
            ]
        )

        history_payload = history_payload or {}
        history_payload.setdefault("before", previous_payload)
        history_payload.setdefault("after", self.aggregated_metrics)
        history_payload.setdefault("metadata", current_metadata)
        history_payload.setdefault("timestamp", now.isoformat())
        history_payload["aggregation_version"] = self.aggregation_version

        diff_summary = {
            key: value
            for key, value in {
                "metrics": metrics_diff,
                "metadata": metadata_diff,
            }.items()
            if value
        }
        if diff_summary:
            history_payload.setdefault("diff", diff_summary)

        self.log_history(
            change_type=MunicipalOBCProfileHistory.CHANGE_AGGREGATED,
            payload=history_payload,
            changed_by=changed_by,
            note=note,
            diff=diff_summary,
        )

    def apply_reported_update(
        self,
        *,
        reported_payload: Dict[str, Any],
        changed_by: Optional[models.Model] = None,
        note: str = "",
        update_notes: bool = False,
    ) -> None:
        """Persist manual form updates with accompanying history."""

        payload = reported_payload or {}
        now = timezone.now()
        previous_payload = self.reported_metrics or {}
        previous_sections = normalise_reported_metrics(previous_payload.get("sections"))
        previous_flat = flatten_metrics(previous_sections)

        sections_payload = normalise_reported_metrics(payload.get("sections"))
        provided_fields_raw = payload.get("provided_fields", [])
        provided_fields = sorted(
            {field for field in provided_fields_raw if isinstance(field, str)}
        )

        metadata = payload.get("metadata")
        if not isinstance(metadata, dict):
            metadata = {}

        stored_payload: Dict[str, Any] = {
            "sections": sections_payload,
            "provided_fields": provided_fields,
            "metadata": metadata,
        }

        update_fields = {"reported_metrics", "last_reported_update", "updated_at"}

        signatories_payload = payload.get("signatories")
        if isinstance(signatories_payload, list):
            sanitised_signatories: List[Dict[str, Any]] = []
            for entry in signatories_payload:
                if isinstance(entry, dict):
                    sanitised_signatories.append(
                        {
                            key: value
                            for key, value in entry.items()
                            if isinstance(key, str)
                        }
                    )
            self.reported_signatories = sanitised_signatories
            update_fields.add("reported_signatories")

        status = payload.get("status") or payload.get("reported_status")
        valid_statuses = {choice for choice, _ in self.STATUS_CHOICES}
        if isinstance(status, str) and status in valid_statuses:
            self.reported_status = status
            update_fields.add("reported_status")
            if status == self.STATUS_SUBMITTED:
                self.reported_submitted_at = now
            elif status == self.STATUS_DRAFT:
                self.reported_submitted_at = None
            update_fields.add("reported_submitted_at")

        if changed_by is not None:
            self.last_reported_by = changed_by
            update_fields.add("last_reported_by")

        if update_notes:
            update_fields.add("reported_notes")

        self.reported_metrics = stored_payload
        self.last_reported_update = now
        self.save(update_fields=list(update_fields))
        current_flat = flatten_metrics(sections_payload)
        metrics_diff: Dict[str, Dict[str, Any]] = {}
        for key in sorted(set(previous_flat) | set(current_flat)):
            before_value = previous_flat.get(key, 0)
            after_value = current_flat.get(key, 0)
            if before_value != after_value:
                metrics_diff[key] = {
                    "before": before_value,
                    "after": after_value,
                    "delta": after_value - before_value,
                }

        history_payload = {
            "before": previous_payload,
            "after": self.reported_metrics,
            "provided_fields": provided_fields,
            "status": self.reported_status,
            "signatories": self.reported_signatories,
            "timestamp": now.isoformat(),
        }

        diff_summary = {"metrics": metrics_diff} if metrics_diff else {}

        self.log_history(
            change_type=MunicipalOBCProfileHistory.CHANGE_REPORTED,
            payload=history_payload,
            changed_by=changed_by,
            note=note,
            diff=diff_summary,
        )


class MunicipalOBCProfileHistory(TimeStampedModel):
    """Immutable audit log capturing all profile mutations."""

    CHANGE_REPORTED = "reported"
    CHANGE_AGGREGATED = "aggregated"
    CHANGE_IMPORT = "import"

    CHANGE_TYPE_CHOICES = [
        (CHANGE_REPORTED, "Manual municipal update"),
        (CHANGE_AGGREGATED, "Barangay aggregation"),
        (CHANGE_IMPORT, "Data import"),
    ]

    profile = models.ForeignKey(
        MunicipalOBCProfile,
        on_delete=models.CASCADE,
        related_name="history_entries",
    )
    change_type = models.CharField(max_length=20, choices=CHANGE_TYPE_CHOICES)
    payload = models.JSONField(default=dict, blank=True)
    diff = models.JSONField(default=dict, blank=True)
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="municipal_profile_changes",
    )
    note = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name = "Municipal OBC Profile History"
        verbose_name_plural = "Municipal OBC Profile History"
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover - trivial repr
        return f"{self.profile} – {self.change_type} @ {self.created_at:%Y-%m-%d %H:%M}"


class OBCCommunityHistory(TimeStampedModel):
    """Historical snapshots for barangay level OBC records."""

    SOURCE_MANUAL = "manual"
    SOURCE_IMPORT = "import"
    SOURCE_AGGREGATION = "aggregation"

    SOURCE_CHOICES = [
        (SOURCE_MANUAL, "Manual update"),
        (SOURCE_IMPORT, "Data import"),
        (SOURCE_AGGREGATION, "System aggregation"),
    ]

    community = models.ForeignKey(
        "communities.OBCCommunity",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="history_entries",
        help_text="OBC Community that this history entry references (preserved even if community is deleted).",
    )
    snapshot = models.JSONField(default=dict, blank=True)
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES)
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="obc_community_changes",
    )
    note = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name = "OBC Community History"
        verbose_name_plural = "OBC Community History"
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover - trivial repr
        community_name = self.community if self.community else "[Deleted Community]"
        return f"{community_name} snapshot @ {self.created_at:%Y-%m-%d %H:%M}"


@dataclass
class AggregationResult:
    municipality: Municipality
    aggregated_metrics: Dict[str, Any]
    barangay_count: int
    communities_considered: Iterable[int]
    aggregated_flat: Dict[str, int]

    def as_payload(
        self, *, discrepancies: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        return {
            "municipality": self.municipality.pk,
            "barangay_count": self.barangay_count,
            "communities": list(self.communities_considered),
            "aggregated_metrics": self.aggregated_metrics,
            "aggregated_flat": self.aggregated_flat,
            "discrepancies": discrepancies or {},
        }

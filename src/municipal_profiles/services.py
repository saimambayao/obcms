from __future__ import annotations

from datetime import date, datetime, time
from decimal import Decimal
from typing import Dict, Iterable, List, Optional, Tuple

from django.db import transaction
from django.db.models import Avg, F, FloatField, Sum
from django.forms.models import model_to_dict
from django.utils import timezone

from common.models import Municipality
from communities.models import OBCCommunity

from .models import (
    AggregationResult,
    MunicipalOBCProfile,
    OBCCommunityHistory,
)
from .aggregation import (
    build_empty_report,
    flatten_metrics,
    iter_metric_rules,
    normalise_reported_metrics,
)

# Numeric fields that should be summed when computing aggregates.
AGGREGATABLE_FIELDS = {
    "estimated_obc_population",
    "total_barangay_population",
    "households",
    "families",
    "children_0_9",
    "adolescents_10_14",
    "youth_15_30",
    "adults_31_59",
    "seniors_60_plus",
    "women_count",
    "solo_parents_count",
    "pwd_count",
    "farmers_count",
    "fisherfolk_count",
    "unemployed_count",
    "indigenous_peoples_count",
    "idps_count",
    "migrants_transients_count",
    "csos_count",
    "associations_count",
    "number_of_peoples_organizations",
    "number_of_cooperatives",
    "number_of_social_enterprises",
    "number_of_micro_enterprises",
    "number_of_unbanked_obc",
    "mosques_count",
    "madrasah_count",
    "asatidz_count",
    "religious_leaders_count",
}


def ensure_profile(municipality: Municipality) -> MunicipalOBCProfile:
    """Return the municipal profile instance, creating it when needed."""

    profile, _ = MunicipalOBCProfile.objects.get_or_create(municipality=municipality)
    return profile


def _normalise_json_value(value: object) -> object:
    """Return a JSON-serialisable representation for snapshots."""

    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, time):
        # Time objects use ISO without date
        return value.isoformat()
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, list):
        return [_normalise_json_value(item) for item in value]
    if isinstance(value, dict):
        return {key: _normalise_json_value(val) for key, val in value.items()}
    return value


def _serialise_community(instance: OBCCommunity) -> Dict[str, object]:
    """Return a JSON-friendly representation of the community."""

    field_names = [
        field.name
        for field in instance._meta.fields
        if field.concrete
        and field.editable
        and field.name not in {"created_at", "updated_at"}
    ]
    payload = model_to_dict(instance, fields=field_names)
    payload["id"] = instance.pk
    payload["barangay"] = instance.barangay_id
    payload["municipality"] = instance.barangay.municipality_id
    payload["province"] = instance.barangay.municipality.province_id
    payload["region"] = instance.barangay.municipality.province.region_id
    payload["updated_at"] = (
        instance.updated_at.isoformat() if instance.updated_at else None
    )
    payload["created_at"] = (
        instance.created_at.isoformat() if instance.created_at else None
    )

    return {key: _normalise_json_value(value) for key, value in payload.items()}


def record_community_history(
    *,
    instance: OBCCommunity,
    source: str,
    changed_by=None,
    note: str = "",
) -> OBCCommunityHistory:
    """Persist a barangay level history snapshot."""

    return OBCCommunityHistory.objects.create(
        community=instance,
        snapshot=_serialise_community(instance),
        source=source,
        changed_by=changed_by,
        note=note,
    )


def compute_aggregate_for_municipality(
    municipality: Municipality,
) -> AggregationResult:
    """Aggregate barangay metrics for a municipality."""

    queryset = (
        OBCCommunity.objects.filter(barangay__municipality=municipality)
        .select_related("barangay__municipality")
        .order_by("pk")
    )

    section_payload = build_empty_report()
    aggregate_kwargs: Dict[str, object] = {}
    metric_lookup: Dict[Tuple[str, str], str] = {}
    weighted_rules: List[Tuple[str, str, object]] = []

    for section_key, metric_key, rule in iter_metric_rules():
        if rule.aggregation == "sum":
            agg_name = f"{metric_key}__sum"
            aggregate_kwargs[agg_name] = Sum(rule.source)
            metric_lookup[(section_key, metric_key)] = agg_name
        elif rule.aggregation == "avg":
            agg_name = f"{metric_key}__avg"
            aggregate_kwargs[agg_name] = Avg(rule.source)
            metric_lookup[(section_key, metric_key)] = agg_name
        elif rule.aggregation == "weighted_mean" and rule.weight_source:
            weighted_rules.append((section_key, metric_key, rule))
        else:
            raise ValueError(
                f"Unsupported aggregation '{rule.aggregation}' for metric {metric_key}"
            )

    aggregates = queryset.aggregate(**aggregate_kwargs) if aggregate_kwargs else {}

    for section_key, metric_key, rule in iter_metric_rules():
        if rule.aggregation in {"sum", "avg"}:
            agg_name = metric_lookup[(section_key, metric_key)]
            value = aggregates.get(agg_name) or 0
            if rule.aggregation == "avg":
                section_payload[section_key][metric_key] = round(float(value), 2)
            else:
                section_payload[section_key][metric_key] = int(value)

    for section_key, metric_key, rule in weighted_rules:
        numerator = (
            queryset.aggregate(
                total=Sum(
                    F(rule.source) * F(rule.weight_source), output_field=FloatField()
                )
            )["total"]
            or 0.0
        )
        denominator = queryset.aggregate(total=Sum(rule.weight_source))["total"] or 0
        section_payload[section_key][metric_key] = (
            round(numerator / denominator, 2) if denominator else 0
        )

    community_ids: List[int] = list(queryset.values_list("id", flat=True))
    barangay_ids: List[int] = list(queryset.values_list("barangay_id", flat=True))

    aggregated_flat = flatten_metrics(section_payload)
    metadata = {
        "community_count": len(community_ids),
        "barangay_count": len(set(barangay_ids)),
        "last_source_update": timezone.now().isoformat(),
    }

    return AggregationResult(
        municipality=municipality,
        aggregated_metrics={
            "sections": section_payload,
            "metadata": metadata,
        },
        barangay_count=metadata["barangay_count"],
        communities_considered=community_ids,
        aggregated_flat=aggregated_flat,
    )


def aggregate_and_store(
    *,
    municipality: Municipality,
    changed_by=None,
    note: str = "",
) -> MunicipalOBCProfile:
    """Compute aggregation and persist it on the municipal profile."""

    profile = ensure_profile(municipality)
    result = compute_aggregate_for_municipality(municipality)
    discrepancies = calculate_discrepancies(
        aggregated_flat=result.aggregated_flat,
        profile=profile,
    )
    unassigned_totals = calculate_unassigned_barangay_totals(
        aggregated_flat=result.aggregated_flat,
        profile=profile,
    )
    metadata = result.aggregated_metrics.setdefault("metadata", {})
    if unassigned_totals["total"]:
        metadata["number_with_no_identified_barangay"] = unassigned_totals
    else:
        metadata.pop("number_with_no_identified_barangay", None)

    result.aggregated_metrics["discrepancies"] = discrepancies
    with transaction.atomic():
        profile.apply_aggregation(
            aggregated_payload=result.aggregated_metrics,
            changed_by=changed_by,
            note=note or "Automatic barangay roll-up",
            history_payload=result.as_payload(discrepancies=discrepancies),
        )
    return profile


def calculate_discrepancies(
    *, aggregated_flat: Dict[str, int], profile: MunicipalOBCProfile
) -> Dict[str, Dict[str, object]]:
    """Compare aggregated results with reported metrics to flag variances."""

    reported = profile.reported_metrics or {}
    reported_sections = normalise_reported_metrics(reported.get("sections"))
    provided_fields = set(reported.get("provided_fields", []))
    reported_flat = flatten_metrics(reported_sections)

    if not provided_fields and not any(reported_flat.values()):
        return {}

    discrepancies: Dict[str, Dict[str, object]] = {}

    for metric_key, aggregated_value in aggregated_flat.items():
        reported_present = metric_key in reported_flat
        reported_value = reported_flat.get(metric_key, 0)

        # Skip discrepancy if municipality has not provided a manual value yet.
        if provided_fields and metric_key not in provided_fields:
            continue

        if not reported_present and aggregated_value == 0:
            continue

        delta = aggregated_value - reported_value
        if delta == 0:
            continue

        baseline = reported_value if reported_value else aggregated_value or 1
        percent_delta = delta / baseline if baseline else 0

        severity = "info"
        if abs(percent_delta) >= 0.1 and abs(delta) >= 10:
            severity = "warning"

        discrepancies[metric_key] = {
            "aggregated": aggregated_value,
            "reported": reported_value,
            "delta": delta,
            "percent_delta": round(percent_delta, 4),
            "severity": severity,
        }

    return discrepancies


def calculate_unassigned_barangay_totals(
    *, aggregated_flat: Dict[str, int], profile: MunicipalOBCProfile
) -> Dict[str, object]:
    """Compute municipal totals not accounted for by barangay submissions."""

    reported_payload = profile.reported_metrics or {}
    reported_sections = normalise_reported_metrics(reported_payload.get("sections"))
    reported_flat = flatten_metrics(reported_sections)
    provided_fields_raw = reported_payload.get("provided_fields", [])
    provided_fields = {field for field in provided_fields_raw if isinstance(field, str)}

    gaps: Dict[str, object] = {}
    for metric_key, reported_value in reported_flat.items():
        if provided_fields and metric_key not in provided_fields:
            continue

        aggregated_value = aggregated_flat.get(metric_key, 0)
        gap = float(reported_value) - float(aggregated_value)
        if gap <= 0:
            continue

        gaps[metric_key] = int(gap) if gap.is_integer() else round(gap, 2)

    total_gap = sum(gaps.values()) if gaps else 0
    if isinstance(total_gap, float) and total_gap.is_integer():
        total_gap = int(total_gap)

    return {
        "metrics": gaps,
        "total": total_gap,
    }

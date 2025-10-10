"""
Utilities for working with coordination organizations across legacy databases.

Some migrated datasets store UUID primary keys without hyphen separators. When
running on PostgreSQL, Django normally casts UUID parameters which causes
``text = uuid`` comparison errors. These helpers normalize identifiers by
removing hyphens and comparing on a lowercase hex representation so existing
records continue to resolve correctly.
"""

from __future__ import annotations

from typing import Optional

from django.db import models
from django.db.models import QuerySet, Value
from django.db.models.functions import Cast, Lower, Replace
from django.http import Http404
from django.shortcuts import get_object_or_404

from coordination.models import Organization


def normalize_identifier(identifier: Optional[str]) -> str:
    """Return a lowercase hex-only identifier or an empty string when invalid."""

    if identifier is None:
        return ""

    if hasattr(identifier, "hex"):
        identifier = identifier.hex

    return str(identifier).replace("-", "").strip().lower()


def with_normalized_id(queryset: QuerySet) -> QuerySet:
    """
    Annotate a queryset with ``normalized_id`` that strips hyphens and lowercases.

    The annotation is safe for UUID-backed models that might store text values in
    legacy SQLite imports.
    """

    return queryset.annotate(
        normalized_id=Lower(
            Replace(
                Cast("id", output_field=models.TextField()),
                Value("-", output_field=models.TextField()),
                Value("", output_field=models.TextField()),
                output_field=models.TextField(),
            ),
            output_field=models.TextField(),
        ),
    )


def get_organization_or_404(identifier, queryset: Optional[QuerySet] = None) -> Organization:
    """
    Fetch an organization by UUID or 32-character hex string; raises 404 if missing.
    """

    normalized = normalize_identifier(identifier)
    if not normalized:
        raise Http404("Invalid organization identifier")

    base_queryset = queryset or Organization.objects.all()
    annotated_queryset = with_normalized_id(base_queryset)
    return get_object_or_404(annotated_queryset, normalized_id=normalized)


def get_organization(identifier, queryset: Optional[QuerySet] = None) -> Optional[Organization]:
    """
    Fetch an organization by identifier or return ``None`` when not found.
    """

    normalized = normalize_identifier(identifier)
    if not normalized:
        return None

    base_queryset = queryset or Organization.objects.all()
    return (
        with_normalized_id(base_queryset)
        .filter(normalized_id=normalized)
        .first()
    )


def get_oobc_organization() -> Optional[Organization]:
    """Return the OOBC organization record when available."""

    search_queries = [
        {"name__iexact": "Office for Other Bangsamoro Communities (OOBC)"},
        {"acronym__iexact": "OOBC"},
        {"name__icontains": "Other Bangsamoro Communities"},
    ]

    for query in search_queries:
        organization = Organization.objects.filter(**query).order_by("name").first()
        if organization:
            return organization
    return None

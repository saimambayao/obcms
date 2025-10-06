"""
Bulk sync utilities for optimized auto-sync operations.

These utilities reduce cascade sync overhead by batching province-level
syncs when multiple municipalities are updated.

Usage:
    from communities.utils import bulk_sync_communities, bulk_sync_municipalities

    # After bulk creating/updating communities
    bulk_sync_communities(community_list)

    # After bulk updating municipality coverages
    bulk_sync_municipalities(municipal_coverage_list)
"""

from collections import defaultdict
from typing import List, Iterable

from communities.models import (
    OBCCommunity,
    MunicipalityCoverage,
    ProvinceCoverage,
)


def bulk_sync_communities(
    communities: Iterable[OBCCommunity],
    sync_provincial: bool = True
) -> dict:
    """
    Sync municipality and province coverages for multiple communities efficiently.

    This function groups communities by municipality and province, then:
    1. Syncs each affected municipality once
    2. Syncs each affected province once (instead of once per municipality)

    Args:
        communities: Iterable of OBCCommunity instances
        sync_provincial: Whether to also sync provincial coverage (default: True)

    Returns:
        dict with sync statistics:
            {
                'municipalities_synced': int,
                'provinces_synced': int,
                'communities_processed': int,
            }

    Example:
        >>> communities = OBCCommunity.objects.filter(...)
        >>> stats = bulk_sync_communities(communities)
        >>> print(f"Synced {stats['municipalities_synced']} municipalities")
    """
    # Group communities by municipality
    municipalities_to_sync = set()
    provinces_to_sync = set()

    communities_list = list(communities)  # Evaluate queryset once

    for community in communities_list:
        municipality = community.barangay.municipality
        municipalities_to_sync.add(municipality)

        if sync_provincial and municipality.province:
            provinces_to_sync.add(municipality.province)

    # Sync all municipalities
    for municipality in municipalities_to_sync:
        MunicipalityCoverage.sync_for_municipality(municipality)

    # Sync all provinces (only once per province, not once per municipality!)
    if sync_provincial:
        for province in provinces_to_sync:
            ProvinceCoverage.sync_for_province(province)

    return {
        "municipalities_synced": len(municipalities_to_sync),
        "provinces_synced": len(provinces_to_sync) if sync_provincial else 0,
        "communities_processed": len(communities_list),
    }


def bulk_sync_municipalities(
    municipal_coverages: Iterable[MunicipalityCoverage],
) -> dict:
    """
    Sync provincial coverages for multiple municipality coverages efficiently.

    This function groups municipality coverages by province, then syncs each
    province only once (instead of once per municipality coverage).

    Args:
        municipal_coverages: Iterable of MunicipalityCoverage instances

    Returns:
        dict with sync statistics:
            {
                'provinces_synced': int,
                'municipalities_processed': int,
            }

    Example:
        >>> coverages = MunicipalityCoverage.objects.filter(...)
        >>> stats = bulk_sync_municipalities(coverages)
        >>> print(f"Synced {stats['provinces_synced']} provinces")
    """
    # Group municipality coverages by province
    provinces_to_sync = set()

    municipal_coverages_list = list(municipal_coverages)  # Evaluate queryset once

    for coverage in municipal_coverages_list:
        if coverage.municipality.province:
            provinces_to_sync.add(coverage.municipality.province)

    # Sync all provinces once
    for province in provinces_to_sync:
        ProvinceCoverage.sync_for_province(province)

    return {
        "provinces_synced": len(provinces_to_sync),
        "municipalities_processed": len(municipal_coverages_list),
    }


def bulk_refresh_municipalities(
    municipalities: Iterable,
    sync_provincial: bool = True
) -> dict:
    """
    Refresh multiple municipality coverages and optionally sync provinces.

    This is useful when you want to manually trigger sync for specific
    municipalities (e.g., after data import or migration).

    Args:
        municipalities: Iterable of Municipality instances
        sync_provincial: Whether to also sync provincial coverage (default: True)

    Returns:
        dict with sync statistics:
            {
                'municipalities_synced': int,
                'provinces_synced': int,
            }

    Example:
        >>> municipalities = Municipality.objects.filter(province__region__code='12')
        >>> stats = bulk_refresh_municipalities(municipalities)
    """
    municipalities_list = list(municipalities)  # Evaluate queryset once
    provinces_to_sync = set()

    # Sync all municipalities
    for municipality in municipalities_list:
        MunicipalityCoverage.sync_for_municipality(municipality)

        if sync_provincial and municipality.province:
            provinces_to_sync.add(municipality.province)

    # Sync all provinces once
    if sync_provincial:
        for province in provinces_to_sync:
            ProvinceCoverage.sync_for_province(province)

    return {
        "municipalities_synced": len(municipalities_list),
        "provinces_synced": len(provinces_to_sync) if sync_provincial else 0,
    }


def bulk_refresh_provinces(provinces: Iterable) -> dict:
    """
    Refresh multiple province coverages.

    Args:
        provinces: Iterable of Province instances

    Returns:
        dict with sync statistics:
            {
                'provinces_synced': int,
            }

    Example:
        >>> provinces = Province.objects.filter(region__code='12')
        >>> stats = bulk_refresh_provinces(provinces)
    """
    provinces_list = list(provinces)  # Evaluate queryset once

    # Sync all provinces
    for province in provinces_list:
        ProvinceCoverage.sync_for_province(province)

    return {
        "provinces_synced": len(provinces_list),
    }


# Convenience function for full hierarchy sync
def sync_entire_hierarchy(region=None) -> dict:
    """
    Sync all municipalities and provinces in a region (or all regions).

    This is useful for initial setup or after major data imports.

    Args:
        region: Optional Region instance. If None, syncs all regions.

    Returns:
        dict with sync statistics

    Example:
        >>> from common.models import Region
        >>> region = Region.objects.get(code='12')
        >>> stats = sync_entire_hierarchy(region)
        >>> print(f"Synced {stats['municipalities_synced']} municipalities")
    """
    from common.models import Municipality, Province

    # Get municipalities to sync
    if region:
        municipalities = Municipality.objects.filter(
            province__region=region,
            barangays__obc_communities__isnull=False
        ).distinct()
        provinces = Province.objects.filter(
            region=region,
            municipalities__barangays__obc_communities__isnull=False
        ).distinct()
    else:
        municipalities = Municipality.objects.filter(
            barangays__obc_communities__isnull=False
        ).distinct()
        provinces = Province.objects.filter(
            municipalities__barangays__obc_communities__isnull=False
        ).distinct()

    # Sync municipalities
    for municipality in municipalities:
        MunicipalityCoverage.sync_for_municipality(municipality)

    # Sync provinces
    for province in provinces:
        ProvinceCoverage.sync_for_province(province)

    return {
        "municipalities_synced": municipalities.count(),
        "provinces_synced": provinces.count(),
        "region": region.name if region else "All Regions",
    }

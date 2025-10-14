"""Common signals for the OBCMS application."""

import logging
from django.core.cache import cache
from django.db import models
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import (
    Municipality,
    Barangay,
    StaffLeave,
    CalendarResourceBooking,
    WorkItem,
)
from .services.deferred_geocoding import schedule_geocoding_if_needed

# DEPRECATED: StaffTask and Event imports removed
# Replaced by WorkItem system
# See: docs/refactor/WORKITEM_MIGRATION_COMPLETE.md

logger = logging.getLogger(__name__)


CALENDAR_CACHE_INDEX_KEY = "calendar:payload:index"


def _invalidate_calendar_cache():
    """Remove cached calendar payloads after data mutations."""

    cached_keys = cache.get(CALENDAR_CACHE_INDEX_KEY) or []

    if cached_keys:
        cache.delete_many(cached_keys)

    cache.delete(CALENDAR_CACHE_INDEX_KEY)


@receiver(post_save, sender=Municipality)
def municipality_post_save(sender, instance, created, **kwargs):
    """
    Signal handler for when a Municipality is saved.
    This will schedule geocoding for the municipality if it doesn't have coordinates.

    The geocoding is performed in the background to avoid blocking Django startup.
    """
    if not instance.center_coordinates:
        # Schedule geocoding in the background (non-blocking)
        scheduled = schedule_geocoding_if_needed(instance)
        if scheduled:
            logger.info(
                f"Scheduled background geocoding for Municipality {instance.name}"
            )
        else:
            logger.debug(
                f"Geocoding not needed or already in progress for Municipality {instance.name}"
            )


@receiver(post_save, sender=Barangay)
def barangay_post_save(sender, instance, created, **kwargs):
    """
    Signal handler for when a Barangay is saved.
    This will schedule geocoding for the barangay if it doesn't have coordinates.

    The geocoding is performed in the background to avoid blocking Django startup.
    """
    if not instance.center_coordinates:
        # Schedule geocoding in the background (non-blocking)
        scheduled = schedule_geocoding_if_needed(instance)
        if scheduled:
            logger.info(
                f"Scheduled background geocoding for Barangay {instance.name}"
            )
        else:
            logger.debug(
                f"Geocoding not needed or already in progress for Barangay {instance.name}"
            )


# StaffTask and Event signals removed - models deleted
# See: docs/refactor/WORKITEM_MIGRATION_COMPLETE.md

@receiver([post_save, post_delete], sender=StaffLeave)
@receiver([post_save, post_delete], sender=CalendarResourceBooking)
@receiver([post_save, post_delete], sender=WorkItem)
def calendar_cache_invalidator(sender, **kwargs):
    """Clear cached calendar payloads when core calendar data changes."""

    _invalidate_calendar_cache()


def connect_monitoring_signals():
    """Connect MonitoringEntry signals to avoid circular dependency."""
    from monitoring.models import MonitoringEntry
    from django.db.models.signals import post_save, post_delete

    post_save.connect(calendar_cache_invalidator, sender=MonitoringEntry)
    post_delete.connect(calendar_cache_invalidator, sender=MonitoringEntry)

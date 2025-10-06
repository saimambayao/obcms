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
from .services.enhanced_geocoding import enhanced_ensure_location_coordinates
from monitoring.models import MonitoringEntry

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
    This will automatically geocode the municipality if it doesn't have coordinates.
    """
    if not instance.center_coordinates:
        logger.info(
            f"Municipality {instance.name} has no coordinates. Triggering geocoding."
        )
        try:
            lat, lng, updated, source = enhanced_ensure_location_coordinates(instance)
            if updated:
                logger.info(
                    f"Successfully geocoded Municipality {instance.name} using {source}. New coordinates: [{lng}, {lat}]"
                )
            elif lat and lng:
                logger.info(
                    f"Municipality {instance.name} already had coordinates from {source}: [{lng}, {lat}]"
                )
            else:
                logger.warning(
                    f"Geocoding failed for Municipality {instance.name} from source {source}."
                )
        except Exception as e:
            logger.error(
                f"An error occurred during geocoding for Municipality {instance.name}: {e}",
                exc_info=True,
            )


@receiver(post_save, sender=Barangay)
def barangay_post_save(sender, instance, created, **kwargs):
    """
    Signal handler for when a Barangay is saved.
    This will automatically geocode the barangay if it doesn't have coordinates.
    """
    if not instance.center_coordinates:
        logger.info(
            f"Barangay {instance.name} has no coordinates. Triggering geocoding."
        )
        try:
            lat, lng, updated, source = enhanced_ensure_location_coordinates(instance)
            if updated:
                logger.info(
                    f"Successfully geocoded Barangay {instance.name} using {source}. New coordinates: [{lng}, {lat}]"
                )
            elif lat and lng:
                logger.info(
                    f"Barangay {instance.name} already had coordinates from {source}: [{lng}, {lat}]"
                )
            else:
                logger.warning(
                    f"Geocoding failed for Barangay {instance.name} from source {source}."
                )
        except Exception as e:
            logger.error(
                f"An error occurred during geocoding for Barangay {instance.name}: {e}",
                exc_info=True,
            )


# StaffTask and Event signals removed - models deleted
# See: docs/refactor/WORKITEM_MIGRATION_COMPLETE.md

@receiver([post_save, post_delete], sender=MonitoringEntry)
@receiver([post_save, post_delete], sender=StaffLeave)
@receiver([post_save, post_delete], sender=CalendarResourceBooking)
@receiver([post_save, post_delete], sender=WorkItem)
def calendar_cache_invalidator(sender, **kwargs):
    """Clear cached calendar payloads when core calendar data changes."""

    _invalidate_calendar_cache()

"""Deferred geocoding service to prevent blocking HTTP requests during Django startup."""

import logging
from typing import Optional
from celery import shared_task
from django.core.cache import cache
from django.db import transaction

from .enhanced_geocoding import enhanced_ensure_location_coordinates

logger = logging.getLogger(__name__)

# Cache key to track geocoding tasks and prevent duplicates
GEOCODING_TASK_LOCK_KEY = "geocoding_task_lock_{model}_{pk}"


def schedule_geocoding_if_needed(instance, timeout: int = 300) -> bool:
    """
    Schedule geocoding for a location instance if needed.

    This function is non-blocking and immediately returns, scheduling
    the actual geocoding to run in the background via Celery.

    Args:
        instance: A Municipality or Barangay instance
        timeout: Lock timeout in seconds to prevent duplicate tasks

    Returns:
        bool: True if geocoding was scheduled, False if not needed or already locked
    """
    # Skip if instance already has coordinates
    if instance.center_coordinates:
        logger.debug(f"{instance.__class__.__name__} {instance.pk} already has coordinates")
        return False

    # Create a lock to prevent multiple geocoding tasks for the same instance
    lock_key = GEOCODING_TASK_LOCK_KEY.format(
        model=instance.__class__.__name__.lower(),
        pk=instance.pk
    )

    # Check if geocoding is already in progress
    if cache.get(lock_key):
        logger.debug(f"Geocoding already in progress for {instance.__class__.__name__} {instance.pk}")
        return False

    # Set a lock to prevent duplicate tasks
    cache.set(lock_key, True, timeout)

    try:
        # Schedule the geocoding task
        _geocode_location_task.delay(
            app_label=instance._meta.app_label,
            model_name=instance.__class__.__name__,
            instance_pk=instance.pk
        )
        logger.info(f"Scheduled geocoding for {instance.__class__.__name__} {instance.pk}")
        return True

    except Exception as e:
        # Remove lock if task scheduling failed
        cache.delete(lock_key)
        logger.error(f"Failed to schedule geocoding for {instance.__class__.__name__} {instance.pk}: {e}")
        return False


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    # Don't store task results to save memory
    ignore_result=True,
    # Auto-expire task after 1 hour
    expires=3600,
)
def _geocode_location_task(
    self,
    app_label: str,
    model_name: str,
    instance_pk: int
) -> Optional[str]:
    """
    Background task to geocode a location instance.

    This task runs in the background and will not block Django startup.
    It handles all the HTTP requests to geocoding APIs.

    Args:
        app_label: Django app label (e.g., 'common')
        model_name: Model name (e.g., 'Municipality', 'Barangay')
        instance_pk: Primary key of the instance to geocode

    Returns:
        Optional[str]: Task result message (ignored due to ignore_result=True)
    """
    try:
        # Import here to avoid circular imports
        from django.apps import apps

        # Get the model class
        try:
            model_class = apps.get_model(app_label, model_name)
        except LookupError:
            logger.error(f"Model {app_label}.{model_name} not found")
            return "Model not found"

        # Get the instance from database
        try:
            instance = model_class.objects.get(pk=instance_pk)
        except model_class.DoesNotExist:
            logger.warning(f"{model_name} {instance_pk} no longer exists")
            return "Instance not found"

        # Check if coordinates were already added by another process
        if instance.center_coordinates:
            logger.info(f"{model_name} {instance_pk} already has coordinates")
            return "Already geocoded"

        # Perform the actual geocoding
        with transaction.atomic():
            # Get the latest instance state
            instance.refresh_from_db()

            # Double-check coordinates (might have been updated by another process)
            if instance.center_coordinates:
                logger.info(f"{model_name} {instance_pk} already has coordinates (double-check)")
                return "Already geocoded"

            # Perform geocoding using the enhanced service
            try:
                lat, lng, updated, source = enhanced_ensure_location_coordinates(instance)

                if updated:
                    logger.info(
                        f"Successfully geocoded {model_name} {instance_pk} ({instance.name}) "
                        f"using {source}: [{lng}, {lat}]"
                    )
                    return f"Geocoded successfully using {source}"
                elif lat and lng:
                    logger.info(
                        f"{model_name} {instance_pk} ({instance.name}) already had "
                        f"coordinates from {source}: [{lng}, {lat}]"
                    )
                    return f"Already had coordinates from {source}"
                else:
                    logger.warning(
                        f"Geocoding failed for {model_name} {instance_pk} ({instance.name}) "
                        f"from source {source}"
                    )
                    return f"Geocoding failed: {source}"

            except Exception as e:
                logger.error(
                    f"Error during geocoding for {model_name} {instance_pk}: {e}",
                    exc_info=True
                )
                # Retry the task if it's a temporary error
                if self.request.retries < self.max_retries:
                    raise self.retry(countdown=60 * (2 ** self.request.retries))
                return f"Geocoding error: {str(e)}"

    except Exception as e:
        logger.error(f"Unexpected error in geocoding task for {model_name} {instance_pk}: {e}", exc_info=True)
        return f"Unexpected error: {str(e)}"

    finally:
        # Always clean up the lock
        lock_key = GEOCODING_TASK_LOCK_KEY.format(
            model=model_name.lower(),
            pk=instance_pk
        )
        cache.delete(lock_key)


def is_geocoding_task_pending(instance) -> bool:
    """
    Check if a geocoding task is already pending for an instance.

    Args:
        instance: A Municipality or Barangay instance

    Returns:
        bool: True if a geocoding task is pending
    """
    lock_key = GEOCODING_TASK_LOCK_KEY.format(
        model=instance.__class__.__name__.lower(),
        pk=instance.pk
    )
    return cache.get(lock_key) is not None


def cancel_geocoding_task(instance) -> bool:
    """
    Cancel a pending geocoding task for an instance.

    Args:
        instance: A Municipality or Barangay instance

    Returns:
        bool: True if task was cancelled, False if no task was pending
    """
    lock_key = GEOCODING_TASK_LOCK_KEY.format(
        model=instance.__class__.__name__.lower(),
        pk=instance.pk
    )

    if cache.get(lock_key):
        cache.delete(lock_key)
        logger.info(f"Cancelled geocoding task for {instance.__class__.__name__} {instance.pk}")
        return True

    return False
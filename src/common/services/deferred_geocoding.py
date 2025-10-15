"""Deferred geocoding service to prevent blocking HTTP requests during Django startup."""

import logging
import sys
from typing import Optional
from threading import Thread
from django.core.cache import cache
from django.db import transaction
from django.apps import apps

# NOTE: DO NOT import enhanced_geocoding at module level!
# It imports models which causes circular import deadlock during Django startup.
# Import it lazily inside functions instead.

logger = logging.getLogger(__name__)


def is_management_command() -> bool:
    """
    Check if Django is running a management command or CLI utility.

    Returns True for commands like migrate, makemigrations, shell, etc., AND for flags like --version, --help.
    Returns False ONLY for server processes like runserver, gunicorn, uvicorn.
    """
    if len(sys.argv) < 2:
        return False

    command = sys.argv[1]

    # Flags are always considered management commands (--version, --help, etc.)
    if command.startswith('--') or command.startswith('-'):
        return True

    # Remove leading path and .py extension if present
    if '/' in command or '\\' in command:
        command = command.split('/')[-1].split('\\')[-1]
    if command.endswith('.py'):
        command = command[:-3]

    # Commands that should NOT trigger geocoding
    management_commands = {
        'migrate', 'makemigrations', 'shell', 'shell_plus',
        'dbshell', 'check', 'showmigrations', 'sqlmigrate',
        'test', 'collectstatic', 'createsuperuser', 'changepassword',
        'dumpdata', 'loaddata', 'flush', 'clearsessions',
    }

    # Geocoding should ONLY run for server commands
    server_commands = {'runserver', 'gunicorn', 'uvicorn', 'daphne', 'hypercorn'}

    # If it's explicitly a server command, return False (enable geocoding)
    if command in server_commands:
        return False

    # If it's in management_commands list, return True (disable geocoding)
    if command in management_commands:
        return True

    # For any other command, default to disabling geocoding (safer)
    # This ensures geocoding only runs for known server processes
    return True

# Cache key to track geocoding tasks and prevent duplicates
GEOCODING_TASK_LOCK_KEY = "geocoding_task_lock_{model}_{pk}"

# Global flag to track if Django startup is complete
_django_startup_complete = False


def schedule_geocoding_if_needed(instance, timeout: int = 300) -> bool:
    """
    Schedule geocoding for a location instance if needed.

    This function is non-blocking and immediately returns, scheduling
    the actual geocoding to run in the background via a thread.

    During Django startup, geocoding is completely deferred to avoid blocking.

    Args:
        instance: A Municipality or Barangay instance
        timeout: Lock timeout in seconds to prevent duplicate tasks

    Returns:
        bool: True if geocoding was scheduled, False if not needed or already locked
    """
    global _django_startup_complete

    # Skip if instance already has coordinates
    if instance.center_coordinates:
        logger.debug(f"{instance.__class__.__name__} {instance.pk} already has coordinates")
        return False

    # During Django startup, completely skip geocoding to prevent hanging
    if not _django_startup_complete:
        logger.info(f"Django startup in progress - deferring geocoding for {instance.__class__.__name__} {instance.pk}")
        # Schedule geocoding for after startup
        _schedule_post_startup_geocoding(instance, timeout)
        return True

    # Create a lock to prevent multiple geocoding tasks for the same instance
    lock_key = GEOCODING_TASK_LOCK_KEY.format(
        model=instance.__class__.__name__.lower(),
        pk=instance.pk
    )

    # Check if geocoding is already in progress
    try:
        if cache.get(lock_key):
            logger.debug(f"Geocoding already in progress for {instance.__class__.__name__} {instance.pk}")
            return False
    except Exception as cache_error:
        # Cache not available - proceed anyway (better to duplicate than to block)
        logger.warning(f"Cache check failed for {instance.__class__.__name__} {instance.pk}: {cache_error}")

    # Set a lock to prevent duplicate tasks
    try:
        cache.set(lock_key, True, timeout)
    except Exception as cache_error:
        # Cache not available - log warning but continue
        logger.warning(f"Failed to set cache lock for {instance.__class__.__name__} {instance.pk}: {cache_error}")

    try:
        # Schedule the geocoding task in a background thread
        thread = Thread(
            target=_geocode_location_in_background,
            args=(
                instance._meta.app_label,
                instance.__class__.__name__,
                instance.pk,
                lock_key
            ),
            daemon=True  # Thread will not prevent Django from shutting down
        )
        thread.start()

        logger.info(f"Scheduled geocoding for {instance.__class__.__name__} {instance.pk}")
        return True

    except Exception as e:
        # Remove lock if task scheduling failed
        cache.delete(lock_key)
        logger.error(f"Failed to schedule geocoding for {instance.__class__.__name__} {instance.pk}: {e}")
        return False


def _schedule_post_startup_geocoding(instance, timeout: int) -> None:
    """
    Schedule geocoding to run after Django startup is complete.

    This adds the instance to a queue that will be processed when Django startup finishes.

    NOTE: During Django startup, the cache backend might not be ready yet.
    This function handles cache unavailability gracefully.
    """
    try:
        # Add to a queue of instances that need geocoding after startup
        queue_key = "geocoding_startup_queue"

        # Try to access cache, but don't block if cache isn't ready
        try:
            queue_data = cache.get(queue_key, [])
        except Exception:
            # Cache not ready during startup - use empty list
            queue_data = []

        instance_info = {
            'app_label': instance._meta.app_label,
            'model_name': instance.__class__.__name__,
            'pk': instance.pk,
            'name': str(instance.name) if hasattr(instance, 'name') else f"PK {instance.pk}"
        }

        queue_data.append(instance_info)

        # Try to set cache, but don't block if cache isn't ready
        try:
            cache.set(queue_key, queue_data, 3600)  # Store for 1 hour
            logger.debug(f"Added {instance.__class__.__name__} {instance.pk} to post-startup geocoding queue")
        except Exception as cache_error:
            # Cache not available - log but don't fail
            logger.warning(
                f"Cache unavailable during startup - geocoding for {instance.__class__.__name__} "
                f"{instance.pk} will not be queued: {cache_error}"
            )

    except Exception as e:
        # Log error but don't fail - geocoding is non-critical
        logger.error(f"Failed to queue geocoding for {instance.__class__.__name__} {instance.pk}: {e}")


def mark_django_startup_complete():
    """
    Mark Django startup as complete and process any queued geocoding tasks.

    This should be called when Django startup is finished.

    NOTE: Cache backend may not be ready during app.ready() phase.
    All cache operations must be wrapped in try-except to avoid blocking.

    NOTE: Geocoding is DISABLED during management commands (migrate, makemigrations, etc.)
    to prevent unnecessary processing and verbose logging.

    NOTE: Queue processing runs in a background thread to avoid blocking server startup.
    """
    global _django_startup_complete

    # Skip geocoding for management commands (migrate, makemigrations, etc.)
    if is_management_command():
        _django_startup_complete = True
        # Silently skip geocoding for management commands
        return

    _django_startup_complete = True
    # Only log for server processes (runserver, gunicorn, etc.)
    logger.info("Django startup complete - processing queued geocoding tasks")

    # Process queued tasks in a background thread to avoid blocking server startup
    try:
        thread = Thread(target=_process_geocoding_queue, daemon=True)
        thread.start()
        logger.debug("Started background thread to process geocoding queue")
    except Exception as e:
        logger.error(f"Failed to start geocoding queue processor: {e}")


def _process_geocoding_queue():
    """
    Process queued geocoding tasks in a background thread.

    This function is called from mark_django_startup_complete() and runs
    asynchronously to avoid blocking server startup.
    """
    try:
        queue_key = "geocoding_startup_queue"

        # Try to get queue data - cache may not be ready yet
        try:
            queue_data = cache.get(queue_key, [])
        except Exception as cache_error:
            # Cache not ready during startup - skip processing
            logger.warning(f"Cache unavailable during startup completion - skipping geocoding queue: {cache_error}")
            return

        if queue_data:
            logger.info(f"Processing {len(queue_data)} queued geocoding tasks")

            for instance_info in queue_data:
                try:
                    # Get the model class
                    model_class = apps.get_model(instance_info['app_label'], instance_info['model_name'])
                    instance = model_class.objects.get(pk=instance_info['pk'])

                    # Schedule geocoding now that startup is complete
                    schedule_geocoding_if_needed(instance)

                except Exception as e:
                    logger.error(f"Failed to process queued geocoding for {instance_info['model_name']} {instance_info['pk']}: {e}")

            # Clear the queue - wrap in try-except
            try:
                cache.delete(queue_key)
            except Exception as cache_error:
                logger.warning(f"Failed to clear geocoding queue from cache: {cache_error}")

    except Exception as e:
        logger.error(f"Error processing geocoding queue: {e}")


def is_django_startup_complete() -> bool:
    """Check if Django startup is complete."""
    return _django_startup_complete


def _geocode_location_in_background(
    app_label: str,
    model_name: str,
    instance_pk: int,
    lock_key: str
) -> Optional[str]:
    """
    Background function to geocode a location instance.

    This function runs in a background thread and will not block Django startup.
    It handles all the HTTP requests to geocoding APIs.

    Args:
        app_label: Django app label (e.g., 'common')
        model_name: Model name (e.g., 'Municipality', 'Barangay')
        instance_pk: Primary key of the instance to geocode
        lock_key: Cache lock key for this geocoding task

    Returns:
        Optional[str]: Result message for logging
    """
    try:
        # Import here to avoid circular imports and ensure Django is fully loaded
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
            # Import here to avoid circular import during Django startup
            from .enhanced_geocoding import enhanced_ensure_location_coordinates

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
                return f"Geocoding error: {str(e)}"

    except Exception as e:
        logger.error(f"Unexpected error in geocoding for {model_name} {instance_pk}: {e}", exc_info=True)
        return f"Unexpected error: {str(e)}"

    finally:
        # Always clean up the lock
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
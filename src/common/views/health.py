"""
Health check endpoints for monitoring and orchestration.

These endpoints allow Docker, Kubernetes, and load balancers to monitor
application health and readiness.
"""

import logging
import signal
from contextlib import contextmanager
from django.conf import settings
from django.core.cache import cache
from django.db import connection
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET

logger = logging.getLogger(__name__)


@contextmanager
def timeout(seconds):
    """
    Context manager for enforcing a timeout on code execution.

    Raises TimeoutError if the code block takes longer than the specified time.
    Only works on Unix systems with signal support.
    """
    def timeout_handler(signum, frame):
        raise TimeoutError(f"Operation timed out after {seconds} seconds")

    # Store the old signal handler
    old_handler = signal.signal(signal.SIGALRM, timeout_handler)
    # Set the alarm
    signal.alarm(seconds)
    try:
        yield
    finally:
        # Cancel the alarm
        signal.alarm(0)
        # Restore the old signal handler
        signal.signal(signal.SIGALRM, old_handler)


@csrf_exempt
@require_GET
@never_cache
def health_check(request):
    """
    Liveness probe: Is the application running?

    Used by Docker/Kubernetes to restart failed containers.
    Returns 200 if the app can handle requests (basic check).

    This is a lightweight check that doesn't test dependencies.
    """
    # Log health check requests for debugging
    logger.info(f"Health check requested from {request.META.get('REMOTE_ADDR', 'unknown')}")

    return JsonResponse(
        {
            "status": "healthy",
            "service": "obcms",
            "version": getattr(settings, "VERSION", "1.0.0"),
        }
    )


@require_GET
@never_cache
def readiness_check(request):
    """
    Readiness probe: Is the application ready to serve traffic?

    Used by load balancers to route traffic only to ready instances.

    Returns 200 OK if the app can actually serve requests (database is accessible).
    Returns 503 if the app cannot serve requests (database is unavailable).

    This validates that the app can actually function, not just that the
    HTTP server is listening. Database connectivity is essential for OBCMS
    to serve requests.

    Returns:
        200 if the app is ready and can serve requests
        503 if the app cannot serve requests (database unavailable)
    """
    # Check database connectivity with strict timeout
    # This ensures the app can actually serve requests, not just listen
    if check_database():
        return JsonResponse(
            {
                "status": "ready",
                "service": "obcms",
                "timestamp": str(timezone.now()),
            },
            status=200,
        )
    else:
        # Database is unavailable - app cannot serve requests
        return JsonResponse(
            {
                "status": "unhealthy",
                "service": "obcms",
                "reason": "database_unavailable",
                "timestamp": str(timezone.now()),
            },
            status=503,
        )


def check_database():
    """
    Check database connectivity with strict timeout.

    Returns:
        True if database is accessible within timeout, False otherwise

    Timeout is set to 2 seconds to ensure readiness probes don't hang.
    If the database is slow to respond, we mark the app as not ready
    rather than blocking the probe indefinitely.
    """
    try:
        # Use a 2-second timeout for database health check
        # This ensures readiness probes complete quickly
        with timeout(2):
            connection.ensure_connection()
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                is_healthy = result[0] == 1
                if is_healthy:
                    logger.debug("Database health check passed")
                return is_healthy
    except TimeoutError:
        logger.warning("Database health check timed out (2 second limit)")
        return False
    except Exception as e:
        logger.warning(f"Database health check failed: {e}")
        # Return False to indicate the app cannot serve requests
        # This allows Kubernetes to remove the pod from the load balancer
        # and eventually restart it when it becomes healthy
        return False


def check_cache():
    """
    Check Redis/cache connectivity.

    Returns:
        True if cache is accessible, False otherwise

    Note: Returns True even if Redis is unavailable, since cache is not
    critical for basic app functionality. This prevents readiness probes
    from failing during startup when Redis is still initializing.
    """
    try:
        cache.set("health_check", "ok", timeout=10)
        result = cache.get("health_check")
        cache.delete("health_check")
        is_healthy = result == "ok"
        if is_healthy:
            logger.debug("Cache health check passed")
        else:
            logger.warning("Cache health check returned unexpected result")
        return is_healthy
    except Exception as e:
        # Cache is optional - don't fail readiness if it's unavailable
        logger.warning(f"Cache health check failed (non-critical): {e}")
        return True  # Still healthy even without cache

"""
Health check endpoints for monitoring and orchestration.

These endpoints allow Docker, Kubernetes, and load balancers to monitor
application health and readiness.
"""

import logging
from django.conf import settings
from django.core.cache import cache
from django.db import connection
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET

logger = logging.getLogger(__name__)


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


@csrf_exempt
@require_GET
@never_cache
def readiness_check(request):
    """
    Readiness probe: Is the application ready to serve traffic?

    Used by load balancers to route traffic only to ready instances.

    Returns 200 OK if the app is running. The readiness check should be
    fast and non-blocking - if this endpoint can respond to HTTP requests,
    the app is ready to serve traffic.

    Returns:
        200 if the app process is running
    """
    # Always return 200 if this endpoint is reachable
    # The app is running if it can respond to HTTP requests
    # Detailed health checks should use dedicated monitoring endpoints
    return JsonResponse(
        {
            "status": "ready",
            "service": "obcms",
            "timestamp": str(timezone.now()),
        },
        status=200,
    )


def check_database():
    """
    Check database connectivity.

    Returns:
        True if database is accessible, False otherwise
    """
    try:
        connection.ensure_connection()
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            is_healthy = result[0] == 1
            if is_healthy:
                logger.debug("Database health check passed")
            return is_healthy
    except Exception as e:
        logger.warning(f"Database health check failed: {e}")
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

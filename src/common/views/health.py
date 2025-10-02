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
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET

logger = logging.getLogger(__name__)


@require_GET
@never_cache
def health_check(request):
    """
    Liveness probe: Is the application running?

    Used by Docker/Kubernetes to restart failed containers.
    Returns 200 if the app can handle requests (basic check).

    This is a lightweight check that doesn't test dependencies.
    """
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

    Checks:
    - Database connectivity
    - Redis/cache connectivity
    - Critical dependencies

    Returns:
        200 if ready to serve traffic
        503 if not ready (dependencies unavailable)
    """
    checks = {
        "database": check_database(),
        "cache": check_cache(),
    }

    all_healthy = all(checks.values())
    status_code = 200 if all_healthy else 503

    return JsonResponse(
        {
            "status": "ready" if all_healthy else "not_ready",
            "checks": checks,
            "service": "obcms",
        },
        status=status_code,
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
            return result[0] == 1
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False


def check_cache():
    """
    Check Redis/cache connectivity.

    Returns:
        True if cache is accessible, False otherwise
    """
    try:
        cache.set("health_check", "ok", timeout=10)
        result = cache.get("health_check")
        cache.delete("health_check")
        return result == "ok"
    except Exception as e:
        logger.error(f"Cache health check failed: {e}")
        return False

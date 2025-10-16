"""
Health check endpoints for Kubernetes/Docker orchestration.

These endpoints provide liveness and readiness probes for container orchestration
systems like Kubernetes, Docker Swarm, and load balancers.
"""

import logging
from django.conf import settings
from django.core.cache import cache
from django.core.management import call_command
from django.db import connection
from django.http import JsonResponse
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET

logger = logging.getLogger(__name__)


@require_GET
@never_cache
def liveness_probe(request):
    """
    Liveness probe endpoint (/live/).

    Simple endpoint that indicates the application is running.
    Used by Docker/Kubernetes to restart failed containers.

    Returns:
        JsonResponse: {"status": "alive"} with HTTP 200
    """
    return JsonResponse({"status": "alive"})


@require_GET
@never_cache
def readiness_probe(request):
    """
    Readiness probe endpoint (/ready/).

    Comprehensive endpoint that checks if the application is ready to serve traffic.
    Used by load balancers to route traffic only to ready instances.

    Checks:
    - Database connectivity
    - Cache connectivity
    - Pending migrations

    Returns:
        JsonResponse: {"ready": true/false, "checks": {"database": bool, "cache": bool, "migrations": bool}}
        with HTTP 200 if ready, HTTP 503 if not ready
    """
    checks = {
        "database": check_database_connectivity(),
        "cache": check_cache_connectivity(),
        "migrations": check_pending_migrations(),
    }

    all_ready = all(checks.values())
    status_code = 200 if all_ready else 503

    return JsonResponse(
        {
            "ready": all_ready,
            "checks": checks,
        },
        status=status_code,
    )


def check_database_connectivity():
    """
    Check database connectivity.

    Returns:
        bool: True if database is accessible, False otherwise
    """
    try:
        connection.ensure_connection()
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            return result[0] == 1
    except Exception as e:
        logger.error(f"Database connectivity check failed: {e}")
        return False


def check_cache_connectivity():
    """
    Check cache connectivity.

    Returns:
        bool: True if cache is accessible, False otherwise
    """
    try:
        # Test cache set/get/delete operations
        test_key = "health_check_test"
        test_value = "ok"

        cache.set(test_key, test_value, timeout=10)
        result = cache.get(test_key)
        cache.delete(test_key)

        return result == test_value
    except Exception as e:
        logger.error(f"Cache connectivity check failed: {e}")
        return False


def check_pending_migrations():
    """
    Check if there are any pending Django migrations.

    Returns:
        bool: True if no pending migrations, False otherwise
    """
    try:
        # Use Django's built-in command to check for pending migrations
        call_command('showmigrations', '--plan', verbosity=0, stdout=None)
        return True
    except Exception as e:
        logger.error(f"Migration check failed: {e}")
        return False
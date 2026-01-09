"""
🏥 Health Check Views

Provides endpoints for system health monitoring.
Compatible with Kubernetes, Docker, and load balancers.
"""

import logging
import time

from django.core.cache import cache
from django.db import connection
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET

logger = logging.getLogger(__name__)


@never_cache
@require_GET
def health(request):
    """
    Basic health check endpoint.
    If requested via browser, returns a premium status page.
    If requested via script, returns JSON.
    """
    if "text/html" in request.headers.get("Accept", ""):
        return render(
            request,
            "health/pages/status/status.html",
            {
                "page_title": "System Status | DAEMON-ONE",
            },
        )

    return JsonResponse(
        {
            "status": "healthy",
            "service": "daemon-one",
            "version": "4.5.0",
            "timestamp": time.time(),
        }
    )


@never_cache
@require_GET
def readiness(request):
    """
    Readiness probe endpoint.

    Checks if the application is ready to receive traffic.
    Verifies database and cache connections.

    Used by Kubernetes readiness probes.
    """
    checks = {
        "database": _check_database(),
        "cache": _check_cache(),
    }

    all_healthy = all(check["status"] == "ok" for check in checks.values())

    response = {
        "status": "ready" if all_healthy else "not_ready",
        "checks": checks,
        "timestamp": time.time(),
    }

    status_code = 200 if all_healthy else 503
    return JsonResponse(response, status=status_code)


@never_cache
@require_GET
def liveness(request):
    """
    Liveness probe endpoint.

    Simple check that the application process is running.
    Should always return 200 if the app hasn't crashed.

    Used by Kubernetes liveness probes.
    """
    return JsonResponse(
        {
            "status": "alive",
            "timestamp": time.time(),
        }
    )


def _check_database() -> dict:
    """Check database connectivity."""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        return {"status": "ok", "latency_ms": 0}
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return {"status": "error", "message": str(e)}


def _check_cache() -> dict:
    """Check cache (Redis) connectivity."""
    try:
        cache_key = "_health_check_"
        cache.set(cache_key, "ok", timeout=10)
        result = cache.get(cache_key)
        if result == "ok":
            return {"status": "ok"}
        return {"status": "error", "message": "Cache read/write failed"}
    except Exception as e:
        logger.error(f"Cache health check failed: {e}")
        return {"status": "error", "message": str(e)}

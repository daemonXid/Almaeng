"""
🏥 Health Module - Public Interface

Type-safe public API for health checks using Pydantic schemas.

Import from here only:
    from domains.base.health.interface import check_health, HealthStatus
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel

from .pages.status.views import _check_cache, _check_database

# =============================================================================
# 📋 Pydantic Schemas
# =============================================================================


class ComponentCheck(BaseModel):
    """Individual component health check result."""

    status: Literal["ok", "error"]
    latency_ms: float | None = None
    message: str | None = None


class HealthStatus(BaseModel):
    """Overall system health status."""

    status: Literal["healthy", "unhealthy", "degraded"]
    checks: dict[str, ComponentCheck]

    @property
    def is_healthy(self) -> bool:
        return self.status == "healthy"


# =============================================================================
# 📖 Public Functions
# =============================================================================


def check_health() -> HealthStatus:
    """
    Check overall system health.

    Returns:
        HealthStatus with individual component checks
    """
    db_result = _check_database()
    cache_result = _check_cache()

    checks = {
        "database": ComponentCheck(
            status=db_result["status"],
            latency_ms=db_result.get("latency_ms"),
            message=db_result.get("error"),
        ),
        "cache": ComponentCheck(
            status=cache_result["status"],
            latency_ms=cache_result.get("latency_ms"),
            message=cache_result.get("error"),
        ),
    }

    all_ok = all(c.status == "ok" for c in checks.values())
    any_error = any(c.status == "error" for c in checks.values())

    if all_ok:
        overall_status = "healthy"
    elif any_error:
        overall_status = "unhealthy"
    else:
        overall_status = "degraded"

    return HealthStatus(status=overall_status, checks=checks)


def is_ready() -> bool:
    """
    Quick check if system is ready for traffic.

    Returns:
        True if all checks pass
    """
    return check_health().is_healthy


def is_alive() -> bool:
    """
    Quick liveness check.

    Always returns True if this code executes.
    """
    return True


__all__ = ["ComponentCheck", "HealthStatus", "check_health", "is_alive", "is_ready"]

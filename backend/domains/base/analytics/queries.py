"""
📊 Dashboard Data & Queries
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime

from django.db import connection
from django.utils import timezone

logger = logging.getLogger(__name__)


@dataclass
class DashboardStats:
    """Overall dashboard statistics."""

    total_views: int = 0
    unique_visitors: int = 0
    avg_response_time_ms: float = 0
    error_rate: float = 0
    updated_at: datetime = field(default_factory=timezone.now)


@dataclass
class PageStats:
    """Statistics for a single page."""

    path: str
    views: int
    avg_time_ms: float


@dataclass
class DatabaseStats:
    """Database statistics."""

    total_size_mb: float
    table_count: int
    largest_tables: list[dict]
    connection_count: int


def get_dashboard_stats() -> DashboardStats:
    """
    Get overall dashboard statistics.

    Note: This is a placeholder. In production, you would
    query from a PageView model or external analytics service.
    """
    # TODO: Implement actual tracking
    return DashboardStats(
        total_views=0,
        unique_visitors=0,
        avg_response_time_ms=0,
        error_rate=0,
    )


def get_popular_pages(limit: int = 10) -> list[PageStats]:
    """
    Get most popular pages.

    Note: Requires PageView model to be implemented.
    """
    # TODO: Implement with actual PageView model
    return []


def get_database_stats() -> DatabaseStats:
    """
    Get database statistics from PostgreSQL.
    """
    try:
        with connection.cursor() as cursor:
            # Database size
            cursor.execute("SELECT pg_size_pretty(pg_database_size(current_database()))")
            cursor.fetchone()[0]

            # Table count
            cursor.execute(
                """
                SELECT count(*) FROM information_schema.tables
                WHERE table_schema = 'public'
                """
            )
            table_count = cursor.fetchone()[0]

            # Largest tables
            cursor.execute(
                """
                SELECT
                    relname as table_name,
                    pg_size_pretty(pg_total_relation_size(relid)) as size,
                    n_live_tup as row_count
                FROM pg_catalog.pg_statio_user_tables
                ORDER BY pg_total_relation_size(relid) DESC
                LIMIT 5
                """
            )
            largest_tables = [{"name": row[0], "size": row[1], "rows": row[2]} for row in cursor.fetchall()]

            # Connection count
            cursor.execute("SELECT count(*) FROM pg_stat_activity")
            connection_count = cursor.fetchone()[0]

            return DatabaseStats(
                total_size_mb=0,  # Parse from db_size if needed
                table_count=table_count,
                largest_tables=largest_tables,
                connection_count=connection_count,
            )
    except Exception as e:
        logger.error(f"Failed to get database stats: {e}")
        return DatabaseStats(
            total_size_mb=0,
            table_count=0,
            largest_tables=[],
            connection_count=0,
        )


def get_slow_queries() -> list[dict]:
    """
    Get slow queries from PostgreSQL.
    Requires pg_stat_statements extension.
    """
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    query,
                    calls,
                    round(mean_exec_time::numeric, 2) as avg_time_ms,
                    round(total_exec_time::numeric, 2) as total_time_ms
                FROM pg_stat_statements
                WHERE mean_exec_time > 100
                ORDER BY mean_exec_time DESC
                LIMIT 10
                """
            )
            return [
                {
                    "query": row[0][:100],
                    "calls": row[1],
                    "avg_time_ms": row[2],
                    "total_time_ms": row[3],
                }
                for row in cursor.fetchall()
            ]
    except Exception as e:
        logger.debug(f"pg_stat_statements not available: {e}")
        return []

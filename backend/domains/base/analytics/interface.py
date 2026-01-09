"""
🔑 Public Interface - Analytics Module

Import from here for analytics functionality.
"""

from .conf import settings
from .queries import (
    DashboardStats,
    DatabaseStats,
    PageStats,
    get_dashboard_stats,
    get_database_stats,
    get_popular_pages,
    get_slow_queries,
)

__all__ = [
    # Types
    "DashboardStats",
    "DatabaseStats",
    "PageStats",
    # Functions
    "get_dashboard_stats",
    "get_database_stats",
    "get_popular_pages",
    "get_slow_queries",
    # Config
    "settings",
]

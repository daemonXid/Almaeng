"""
⚙️ Analytics Module Configuration
"""

import os
from dataclasses import dataclass


@dataclass
class AnalyticsSettings:
    """Analytics module settings."""

    # Tracking
    TRACK_ADMIN_REQUESTS: bool = False
    EXCLUDED_PATHS: list[str] = None

    # Performance
    SLOW_QUERY_THRESHOLD_MS: int = 100

    # Retention
    RETENTION_DAYS: int = 30

    # Refresh interval (seconds)
    REFRESH_INTERVAL: int = 30

    def __post_init__(self):
        if self.EXCLUDED_PATHS is None:
            self.EXCLUDED_PATHS = [
                "/static/",
                "/admin/jsi18n/",
                "/__reload__/",
            ]
        self.SLOW_QUERY_THRESHOLD_MS = int(os.getenv("ANALYTICS_SLOW_QUERY_MS", self.SLOW_QUERY_THRESHOLD_MS))


settings = AnalyticsSettings()

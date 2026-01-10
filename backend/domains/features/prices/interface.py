"""
💰 Prices Interface

외부 도메인에서 사용하는 공개 API.
다른 도메인에서는 반드시 이 파일을 통해서만 접근해야 합니다.

Usage:
    from domains.features.prices.interface import (
        get_current_prices,
        compare_prices,
        get_lowest_price,
    )
"""

from .models import PriceAlert, PriceHistory
from .schemas import (
    PriceAlertSchema,
    PriceCompareSchema,
    PriceHistorySchema,
    PricePerUnitSchema,
    PriceTrendSchema,
)
from .services import (
    calculate_price_per_serving,
    check_alerts,
    compare_prices,
    get_current_prices,
    get_lowest_price,
    get_price_trend,
)

__all__ = [
    "PriceAlert",
    "PriceAlertSchema",
    "PriceCompareSchema",
    # Models (read-only access)
    "PriceHistory",
    # Schemas
    "PriceHistorySchema",
    "PricePerUnitSchema",
    "PriceTrendSchema",
    "calculate_price_per_serving",
    "check_alerts",
    "compare_prices",
    # Services
    "get_current_prices",
    "get_lowest_price",
    "get_price_trend",
]

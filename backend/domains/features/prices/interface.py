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

from .integrations.base import CrawlResult
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
    get_active_alerts_count,
    get_current_prices,
    get_lowest_price,
    get_lowest_price_record,
    get_price_history,
    get_price_trend,
    get_total_price_records_count,
)


async def search_naver_prices(query: str, limit: int | None = None) -> list[CrawlResult]:
    """
    네이버 쇼핑 가격 검색 (외부 API 래퍼)
    
    Usage:
        from domains.features.prices.interface import search_naver_prices
        results = await search_naver_prices("비타민C", limit=4)
    """
    from .conf import settings
    from .integrations.naver import NaverCrawler
    
    if limit is None:
        limit = settings.DEFAULT_PRICE_SEARCH_LIMIT
    
    crawler = NaverCrawler()
    return await crawler.search(query)[:limit]

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
    # External API wrappers
    "CrawlResult",
    "search_naver_prices",
    # Services
    "calculate_price_per_serving",
    "check_alerts",
    "compare_prices",
    "get_active_alerts_count",
    "get_current_prices",
    "get_lowest_price",
    "get_lowest_price_record",
    "get_price_history",
    "get_price_trend",
    "get_total_price_records_count",
]

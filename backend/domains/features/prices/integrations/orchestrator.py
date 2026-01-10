"""
🕷️ Crawler Orchestrator

모든 크롤러를 통합하여 가격 수집 및 DB 저장.
"""

import asyncio
from decimal import Decimal

from django.utils import timezone

from ..models import PriceHistory
from .base import CrawlResult
from .coupang import CoupangCrawler
from .danawa import DanawaCrawler
from .iherb import IHerbCrawler


class CrawlerOrchestrator:
    """크롤러 오케스트레이터"""

    def __init__(self):
        self.crawlers = {
            "iherb": IHerbCrawler(),
            "danawa": DanawaCrawler(),
            "coupang": CoupangCrawler(),
        }

    async def search_all(self, keyword: str) -> dict[str, list[CrawlResult]]:
        """모든 플랫폼에서 검색"""
        results = {}
        tasks = []

        for name, crawler in self.crawlers.items():
            tasks.append(self._search_with_name(name, crawler, keyword))

        search_results = await asyncio.gather(*tasks, return_exceptions=True)

        for name, result in zip(self.crawlers.keys(), search_results, strict=False):
            if isinstance(result, Exception):
                results[name] = []
            else:
                results[name] = result

        return results

    async def _search_with_name(self, name: str, crawler, keyword: str) -> list[CrawlResult]:
        """이름과 함께 검색 실행"""
        return await crawler.search(keyword)

    async def get_prices(self, urls: dict[str, str]) -> dict[str, CrawlResult]:
        """플랫폼별 URL에서 가격 수집

        Args:
            urls: {"iherb": "https://...", "coupang": "https://..."}
        """
        results = {}
        tasks = []

        for platform, url in urls.items():
            if platform in self.crawlers:
                tasks.append(self._get_price_with_platform(platform, url))

        price_results = await asyncio.gather(*tasks, return_exceptions=True)

        for i, platform in enumerate(urls.keys()):
            result = price_results[i] if i < len(price_results) else None
            if isinstance(result, Exception) or result is None:
                results[platform] = None
            else:
                results[platform] = result

        return results

    async def _get_price_with_platform(self, platform: str, url: str) -> CrawlResult | None:
        """플랫폼으로 가격 수집"""
        crawler = self.crawlers.get(platform)
        if crawler:
            return await crawler.get_price(url)
        return None

    def save_prices(self, supplement_id: int, results: dict[str, CrawlResult]) -> list[PriceHistory]:
        """크롤링 결과를 DB에 저장"""
        saved = []

        for platform, result in results.items():
            if result and result.price > 0:
                price_history = PriceHistory.objects.create(
                    supplement_id=supplement_id,
                    platform=platform,
                    price=result.price,
                    original_price=result.original_price or Decimal(0),
                    discount_percent=result.discount_percent or 0,
                    url=result.url,
                    is_in_stock=result.is_in_stock,
                    recorded_at=timezone.now(),
                )
                saved.append(price_history)

        return saved

    async def crawl_and_save(self, supplement_id: int, urls: dict[str, str]) -> list[PriceHistory]:
        """플랫폼별 URL에서 가격 수집 후 저장"""
        results = await self.get_prices(urls)
        return self.save_prices(supplement_id, results)

    async def close_all(self):
        """모든 크롤러 종료"""
        for crawler in self.crawlers.values():
            await crawler.close()


# 싱글톤 인스턴스
_orchestrator: CrawlerOrchestrator | None = None


def get_orchestrator() -> CrawlerOrchestrator:
    """오케스트레이터 인스턴스 반환"""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = CrawlerOrchestrator()
    return _orchestrator


async def crawl_supplement_prices(supplement_id: int, urls: dict[str, str]) -> list[PriceHistory]:
    """영양제 가격 크롤링 (외부 인터페이스)"""
    orchestrator = get_orchestrator()
    return await orchestrator.crawl_and_save(supplement_id, urls)

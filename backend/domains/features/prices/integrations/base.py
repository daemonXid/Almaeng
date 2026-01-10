"""
🕷️ Base Crawler

공통 크롤러 베이스 클래스. Rate limiting, retry, error handling.
"""

import asyncio
import random
from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal

import httpx


@dataclass
class CrawlResult:
    """크롤링 결과"""

    product_name: str
    price: Decimal
    original_price: Decimal | None = None
    discount_percent: int | None = None
    url: str = ""
    is_in_stock: bool = True
    platform: str = ""
    error: str | None = None


class BaseCrawler(ABC):
    """크롤러 베이스 클래스"""

    PLATFORM_NAME = "base"
    BASE_URL = ""

    # Rate limiting
    MIN_DELAY = 1.0  # 최소 요청 간격 (초)
    MAX_DELAY = 3.0  # 최대 요청 간격 (초)
    MAX_RETRIES = 3

    # User agents rotation
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    ]

    def __init__(self):
        self._client: httpx.AsyncClient | None = None

    @property
    def headers(self) -> dict:
        """랜덤 User-Agent 포함 헤더"""
        return {
            "User-Agent": random.choice(self.USER_AGENTS),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
        }

    async def get_client(self) -> httpx.AsyncClient:
        """HTTP 클라이언트 (싱글톤)"""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                headers=self.headers,
                timeout=30.0,
                follow_redirects=True,
            )
        return self._client

    async def close(self):
        """클라이언트 종료"""
        if self._client:
            await self._client.aclose()

    async def delay(self):
        """Rate limiting delay"""
        await asyncio.sleep(random.uniform(self.MIN_DELAY, self.MAX_DELAY))

    async def fetch(self, url: str, retries: int = 0) -> str | None:
        """URL fetch with retry"""
        try:
            client = await self.get_client()
            response = await client.get(url)
            response.raise_for_status()
            await self.delay()
            return response.text
        except httpx.HTTPStatusError:
            if retries < self.MAX_RETRIES:
                await asyncio.sleep(2**retries)  # Exponential backoff
                return await self.fetch(url, retries + 1)
            return None
        except Exception:
            return None

    @abstractmethod
    async def search(self, keyword: str) -> list[CrawlResult]:
        """키워드로 제품 검색"""
        pass

    @abstractmethod
    async def get_price(self, product_url: str) -> CrawlResult | None:
        """제품 URL에서 가격 정보 추출"""
        pass

    def parse_price(self, price_text: str) -> Decimal:
        """가격 문자열 → Decimal 변환"""
        # "₩12,900" → 12900
        cleaned = "".join(c for c in price_text if c.isdigit())
        return Decimal(cleaned) if cleaned else Decimal(0)

    def calculate_discount(self, original: Decimal, current: Decimal) -> int:
        """할인율 계산"""
        if original <= 0:
            return 0
        return int(((original - current) / original) * 100)

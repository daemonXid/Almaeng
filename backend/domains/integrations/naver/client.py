"""
🛍️ Naver Shopping API Client

네이버 검색 API (쇼핑) 클라이언트.
https://developers.naver.com/docs/serviceapi/search/shopping/shopping.md
"""

import httpx
from django.conf import settings
from pydantic import BaseModel, ConfigDict
from decimal import Decimal

from ..base import BaseCrawler, CrawlResult


class NaverProduct(BaseModel):
    """네이버 쇼핑 상품 정보 (API 응답)"""

    model_config = ConfigDict(frozen=True)

    title: str
    link: str
    image: str
    lprice: str  # 최저가
    hprice: str  # 최고가
    mallName: str
    productId: str
    productType: str
    brand: str
    maker: str
    category1: str
    category2: str
    category3: str
    category4: str


class NaverClient(BaseCrawler):
    """네이버 쇼핑 검색 (API 기반)"""

    PLATFORM_NAME = "naver"
    BASE_URL = "https://openapi.naver.com/v1/search/shop.json"

    def __init__(self):
        super().__init__()
        self.client_id = getattr(settings, "NAVER_CLIENT_ID", "")
        self.client_secret = getattr(settings, "NAVER_CLIENT_SECRET", "")

    async def search(self, keyword: str, limit: int = 20) -> list[CrawlResult]:
        """
        네이버 쇼핑 검색 API 호출
        
        Args:
            keyword: 검색 키워드
            limit: 최대 결과 수 (10~100)
            
        Returns:
            list[CrawlResult]: 검색 결과 리스트
        """
        if not self.client_id or not self.client_secret:
            return []

        headers = {
            "X-Naver-Client-Id": self.client_id,
            "X-Naver-Client-Secret": self.client_secret,
        }

        params = {
            "query": keyword,
            "display": min(limit, 100),  # 10~100
            "start": 1,
            "sort": "sim",  # sim(유사도), date(날짜), asc(가격오름차순), dsc(가격내림차순)
        }

        results = []
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(self.BASE_URL, headers=headers, params=params)

                if response.status_code == 200:
                    data = response.json()
                    items = data.get("items", [])

                    for item in items:
                        try:
                            # HTML 태그 제거 (title에 <b> 포함됨)
                            title = item["title"].replace("<b>", "").replace("</b>", "")

                            # lprice가 빈 문자열이거나 0일 수 있음
                            lprice_str = item.get("lprice", "")
                            if not lprice_str:
                                continue

                            price = Decimal(lprice_str)
                            hprice = Decimal(item.get("hprice", lprice_str)) if item.get("hprice") else None
                            
                            # 할인율 계산
                            discount_percent = None
                            if hprice and hprice > price:
                                discount_percent = int(((hprice - price) / hprice) * 100)

                            results.append(
                                CrawlResult(
                                    product_name=title,
                                    price=price,
                                    original_price=hprice,
                                    discount_percent=discount_percent,
                                    url=item["link"],
                                    image_url=item.get("image", ""),
                                    platform=self.PLATFORM_NAME,
                                    is_in_stock=True,
                                    mall_name=item.get("mallName", ""),
                                )
                            )
                        except Exception:
                            continue

        except Exception:
            pass

        return results

    async def get_price(self, product_url: str) -> CrawlResult | None:
        """
        상세 가격 정보 조회
        네이버 API는 상세 조회 기능이 없음 (검색 결과 의존).
        """
        return None


# Singleton
naver_client = NaverClient()

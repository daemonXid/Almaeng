"""
🛍️ Naver Shopping API Client

네이버 검색 API (쇼핑) 클라이언트.
https://developers.naver.com/docs/serviceapi/search/shopping/shopping.md
"""

import httpx
from django.conf import settings
from pydantic import BaseModel, HttpUrl

from .base import BaseCrawler, CrawlResult


class NaverProduct(BaseModel):
    """네이버 쇼핑 상품 정보 (API 응답)"""
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


class NaverCrawler(BaseCrawler):
    """네이버 쇼핑 검색 (API 기반)"""
    
    PLATFORM_NAME = "naver"
    BASE_URL = "https://openapi.naver.com/v1/search/shop.json"

    def __init__(self):
        super().__init__()
        self.client_id = getattr(settings, "NAVER_CLIENT_ID", "")
        self.client_secret = getattr(settings, "NAVER_CLIENT_SECRET", "")

    async def search(self, keyword: str) -> list[CrawlResult]:
        """
        네이버 쇼핑 검색 API 호출
        """
        if not self.client_id or not self.client_secret:
            print("⚠️ NAVER_CLIENT_ID or NAVER_CLIENT_SECRET not configured.")
            return []

        headers = {
            "X-Naver-Client-Id": self.client_id,
            "X-Naver-Client-Secret": self.client_secret,
        }
        
        params = {
            "query": keyword,
            "display": 20,  # 10~100
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
                            price = self.parse_price(item["lprice"])
                            
                            results.append(CrawlResult(
                                product_name=title,
                                price=price,
                                url=item["link"],
                                image_url=item["image"],
                                platform=self.PLATFORM_NAME,
                                is_in_stock=True # API로는 재고 확인 불가, 기본 True
                            ))
                        except Exception:
                            continue
                else:
                    print(f"Server Error: {response.status_code} {response.text}")
                    
        except Exception as e:
            print(f"Connection Error: {str(e)}")
            
        return results

    async def get_price(self, product_url: str) -> CrawlResult | None:
        """
        상세 가격 정보 조회
        네이버 API는 상세 조회 기능이 없음 (검색 결과 의존).
        따라서 product_url이 주어지면 None을 반환하거나, Playwright 등으로 크롤링해야 함.
        현재는 구현하지 않음.
        """
        return None

"""
🛒 11번가 Open API Client

11번가 Open API 클라이언트 (PRD v2).
https://openapi.11st.co.kr/openapi/OpenApiService.tmall

API 문서: https://openapi.11st.co.kr/openapi/OpenApiGuide.tmall
"""

import logging
import xml.etree.ElementTree as ET
from decimal import Decimal

import httpx
from django.conf import settings

from ..base import BaseCrawler, CrawlResult

logger = logging.getLogger(__name__)


class ElevenStreetClient(BaseCrawler):
    """11번가 Open API 클라이언트"""

    PLATFORM_NAME = "11st"
    BASE_URL = "http://openapi.11st.co.kr/openapi/OpenApiService.tmall"

    def __init__(self):
        super().__init__()
        self.api_key = getattr(settings, "ELEVENST_API_KEY", "")

    async def search(self, keyword: str, limit: int = 20) -> list[CrawlResult]:
        """
        11번가 상품 검색

        Args:
            keyword: 검색 키워드
            limit: 최대 결과 수 (최대 200)

        Returns:
            list[CrawlResult]: 검색 결과 리스트
        """
        if not self.api_key:
            logger.warning("11번가 API key not configured")
            return []

        params = {
            "key": self.api_key,
            "apiCode": "ProductSearch",
            "keyword": keyword,
            "pageNum": 1,
            "pageSize": min(limit, 200),
            "sortCd": "CP",  # CP: 인기도순, A: 정확도순, L: 낮은가격순, H: 높은가격순
        }

        results = []
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(self.BASE_URL, params=params)

                if response.status_code == 200:
                    # XML 파싱
                    root = ET.fromstring(response.text)

                    # 에러 체크
                    error_code = root.find(".//ErrorCode")
                    if error_code is not None and error_code.text != "0":
                        error_msg = root.find(".//ErrorMessage")
                        logger.error(f"11번가 API 에러: {error_msg.text if error_msg is not None else 'Unknown'}")
                        return []

                    # 상품 목록 파싱
                    products = root.findall(".//Product")

                    for product in products:
                        try:
                            # 필수 필드 추출
                            product_name = self._get_text(product, "ProductName", "")
                            if not product_name:
                                continue

                            # 가격 정보
                            sale_price = self._get_text(product, "SalePrice", "0")
                            price = Decimal(sale_price.replace(",", "")) if sale_price else Decimal(0)

                            if price <= 0:
                                continue

                            # 원래 가격 (할인 전)
                            original_price_str = self._get_text(product, "Price", "0")
                            original_price = (
                                Decimal(original_price_str.replace(",", "")) if original_price_str else None
                            )

                            # 할인율
                            discount_percent = None
                            if original_price and original_price > price:
                                discount_percent = int(((original_price - price) / original_price) * 100)

                            # 상품 ID 및 URL
                            self._get_text(product, "ProductCode", "")
                            detail_page_url = self._get_text(product, "DetailPageUrl", "")

                            # 이미지
                            product_image = self._get_text(product, "ProductImage300", "")
                            if not product_image:
                                product_image = self._get_text(product, "ProductImage", "")

                            # 판매자 정보
                            seller_nm = self._get_text(product, "SellerNm", "11번가")

                            # 평점 (11번가 API에서 제공되는 경우)
                            rating = None
                            rating_str = self._get_text(product, "BuySatisfy", "")
                            if rating_str:
                                try:
                                    rating = float(rating_str)
                                except ValueError:
                                    pass

                            # 리뷰 수
                            review_count = 0
                            review_count_str = self._get_text(product, "ReviewCount", "0")
                            try:
                                review_count = int(review_count_str.replace(",", ""))
                            except ValueError:
                                pass

                            results.append(
                                CrawlResult(
                                    product_name=product_name,
                                    price=price,
                                    original_price=original_price,
                                    discount_percent=discount_percent,
                                    url=detail_page_url,
                                    image_url=product_image,
                                    platform=self.PLATFORM_NAME,
                                    is_in_stock=True,
                                    mall_name=seller_nm,
                                    rating=rating,
                                    review_count=review_count,
                                )
                            )
                        except Exception as e:
                            logger.debug(f"11번가 상품 파싱 실패: {e}")
                            continue

        except httpx.TimeoutException:
            logger.warning("11번가 API 타임아웃")
        except ET.ParseError as e:
            logger.error(f"11번가 API XML 파싱 에러: {e}")
        except Exception as e:
            logger.exception(f"11번가 API 호출 실패: {e}")

        return results

    def _get_text(self, element: ET.Element, tag: str, default: str = "") -> str:
        """XML 요소에서 텍스트 추출"""
        child = element.find(tag)
        if child is not None and child.text:
            return child.text.strip()
        return default

    async def get_price(self, product_url: str) -> CrawlResult | None:
        """
        상세 가격 정보 조회
        11번가 API는 상세 조회 기능이 없음 (검색 결과 의존).
        """
        return None


# Singleton
elevenst_client = ElevenStreetClient()

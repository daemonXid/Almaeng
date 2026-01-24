"""
🛒 Coupang Partners API Client

쿠팡 파트너스 API 클라이언트.
https://partners.coupang.com/api/docs
"""

import hashlib
import hmac
import time
from datetime import datetime, timezone

import httpx
from django.conf import settings
from pydantic import BaseModel, ConfigDict, Field


class CoupangProduct(BaseModel):
    """쿠팡 상품 정보"""
    model_config = ConfigDict(frozen=True)  # Immutable Data Flow 강제

    product_id: str = Field(..., alias="productId")
    product_name: str = Field(..., alias="productName")
    product_price: int = Field(..., alias="productPrice")
    product_image: str = Field("", alias="productImage")
    product_url: str = Field("", alias="productUrl")
    is_rocket: bool = Field(False, alias="isRocket")
    is_free_shipping: bool = Field(False, alias="isFreeShipping")
    category_name: str = Field("", alias="categoryName")

    class Config:
        populate_by_name = True


class CoupangSearchResult(BaseModel):
    """쿠팡 검색 결과"""
    model_config = ConfigDict(frozen=True)  # Immutable Data Flow 강제

    success: bool
    products: list[CoupangProduct] = []
    total_count: int = 0
    error_message: str = ""


class CoupangPartnersClient:
    """쿠팡 파트너스 API 클라이언트"""

    BASE_URL = "https://api-gateway.coupang.com"

    def __init__(self):
        self.access_key = getattr(settings, "COUPANG_ACCESS_KEY", "")
        self.secret_key = getattr(settings, "COUPANG_SECRET_KEY", "")

    def _generate_hmac(self, method: str, url: str, timestamp: str) -> str:
        """HMAC 서명 생성"""
        message = f"{timestamp}{method}{url}"
        signature = hmac.new(
            self.secret_key.encode("utf-8"),
            message.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        return signature

    def _get_auth_headers(self, method: str, path: str) -> dict:
        """인증 헤더 생성"""
        timestamp = datetime.now(timezone.utc).strftime("%y%m%dT%H%M%SZ")
        signature = self._generate_hmac(method, path, timestamp)

        return {
            "Authorization": f"CEA algorithm=HmacSHA256, access-key={self.access_key}, signed-date={timestamp}, signature={signature}",
            "Content-Type": "application/json",
        }

    async def search_products(
        self, keyword: str, limit: int = 20
    ) -> CoupangSearchResult:
        """
        상품 검색

        Args:
            keyword: 검색어
            limit: 최대 결과 수

        Returns:
            CoupangSearchResult
        """
        if not self.access_key or not self.secret_key:
            return CoupangSearchResult(
                success=False,
                error_message="Coupang API keys not configured",
            )

        path = "/v2/providers/affiliate_open_api/apis/openapi/products/search"
        url = f"{self.BASE_URL}{path}"

        params = {
            "keyword": keyword,
            "limit": limit,
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    url,
                    params=params,
                    headers=self._get_auth_headers("GET", path),
                )

                if response.status_code == 200:
                    data = response.json()
                    products = [
                        CoupangProduct(**p) for p in data.get("data", [])
                    ]
                    return CoupangSearchResult(
                        success=True,
                        products=products,
                        total_count=len(products),
                    )
                else:
                    return CoupangSearchResult(
                        success=False,
                        error_message=f"API error: {response.status_code}",
                    )

        except httpx.TimeoutException:
            return CoupangSearchResult(
                success=False,
                error_message="Request timeout",
            )
        except Exception as e:
            return CoupangSearchResult(
                success=False,
                error_message=str(e),
            )

    async def get_product_link(self, product_url: str) -> str | None:
        """
        파트너스 추적 링크 생성

        Args:
            product_url: 쿠팡 상품 URL

        Returns:
            파트너스 추적 링크 또는 None
        """
        if not self.access_key or not self.secret_key:
            return None

        path = "/v2/providers/affiliate_open_api/apis/openapi/deeplink"
        url = f"{self.BASE_URL}{path}"

        payload = {
            "coupangUrls": [product_url],
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    url,
                    json=payload,
                    headers=self._get_auth_headers("POST", path),
                )

                if response.status_code == 200:
                    data = response.json()
                    links = data.get("data", [])
                    if links:
                        return links[0].get("shortenUrl")
                return None

        except Exception:
            return None


# Singleton
coupang_client = CoupangPartnersClient()

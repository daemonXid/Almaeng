"""
🛒 Coupang Partners API Client

쿠팡 파트너스 API 클라이언트 (15만원 달성 후 사용)

API 문서: https://developers.coupangcorp.com/hc/ko/articles/360033973113
"""

import hashlib
import hmac
import time
from typing import Any
from urllib.parse import urlencode

import httpx
from django.conf import settings


class CoupangPartnersClient:
    """
    Coupang Partners API Client

    15만원 수익 달성 후 API 사용 가능
    그 전까지는 CoupangManualProduct 모델 사용
    """

    BASE_URL = "https://api-gateway.coupang.com"

    def __init__(
        self,
        access_key: str | None = None,
        secret_key: str | None = None,
    ):
        self.access_key = access_key or settings.COUPANG_ACCESS_KEY
        self.secret_key = secret_key or settings.COUPANG_SECRET_KEY

        if not self.access_key or not self.secret_key:
            raise ValueError(
                "Coupang API credentials not found. "
                "Please set COUPANG_ACCESS_KEY and COUPANG_SECRET_KEY in settings."
            )

    def _generate_hmac(
        self,
        method: str,
        path: str,
        query_params: dict[str, Any] | None = None,
    ) -> str:
        """
        Generate HMAC signature for Coupang API

        Args:
            method: HTTP method (GET, POST, etc.)
            path: API path
            query_params: Query parameters

        Returns:
            HMAC signature
        """
        datetime_str = time.strftime("%y%m%d") + "T" + time.strftime("%H%M%S") + "Z"

        # Build message
        message = datetime_str + method + path
        if query_params:
            message += "?" + urlencode(sorted(query_params.items()))

        # Generate HMAC
        signature = hmac.new(
            self.secret_key.encode("utf-8"),
            message.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

        return f"CEA algorithm=HmacSHA256, access-key={self.access_key}, signed-date={datetime_str}, signature={signature}"

    async def search_products(
        self,
        keyword: str,
        limit: int = 20,
    ) -> list[dict[str, Any]]:
        """
        Search products by keyword

        Args:
            keyword: Search keyword
            limit: Result limit (max: 100)

        Returns:
            List of products
        """
        path = "/v2/providers/affiliate_open_api/apis/openapi/products/search"
        query_params = {
            "keyword": keyword,
            "limit": min(limit, 100),
        }

        headers = {
            "Authorization": self._generate_hmac("GET", path, query_params),
            "Content-Type": "application/json;charset=UTF-8",
        }

        async with httpx.AsyncClient(proxies={}) as client:
            response = await client.get(
                f"{self.BASE_URL}{path}",
                params=query_params,
                headers=headers,
                timeout=30.0,
            )
            response.raise_for_status()
            data = response.json()

            return data.get("data", [])

    async def get_product_detail(
        self,
        product_id: str,
    ) -> dict[str, Any] | None:
        """
        Get product detail by product ID

        Args:
            product_id: Product ID

        Returns:
            Product detail
        """
        path = f"/v2/providers/affiliate_open_api/apis/openapi/products/{product_id}"

        headers = {
            "Authorization": self._generate_hmac("GET", path),
            "Content-Type": "application/json;charset=UTF-8",
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}{path}",
                headers=headers,
                timeout=30.0,
            )
            response.raise_for_status()
            data = response.json()

            return data.get("data")

    async def generate_deeplink(
        self,
        product_url: str,
    ) -> str | None:
        """
        Generate affiliate deeplink

        Args:
            product_url: Original product URL

        Returns:
            Affiliate deeplink
        """
        path = "/v2/providers/affiliate_open_api/apis/openapi/deeplink"

        headers = {
            "Authorization": self._generate_hmac("POST", path),
            "Content-Type": "application/json;charset=UTF-8",
        }

        payload = {
            "coupangUrls": [product_url],
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.BASE_URL}{path}",
                json=payload,
                headers=headers,
                timeout=30.0,
            )
            response.raise_for_status()
            data = response.json()

            links = data.get("data", [])
            return links[0] if links else None


# Singleton instance
_coupang_client: CoupangPartnersClient | None = None


def get_coupang_client() -> CoupangPartnersClient:
    """Get Coupang Partners API client singleton"""
    global _coupang_client
    if _coupang_client is None:
        _coupang_client = CoupangPartnersClient()
    return _coupang_client

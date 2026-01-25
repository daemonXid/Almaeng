"""
🛍️ Naver Shopping Schemas

Pydantic 스키마 정의.
"""

from pydantic import BaseModel, ConfigDict, Field


class NaverProductResult(BaseModel):
    """네이버 쇼핑 검색 결과 (PRD v2 스키마)"""

    model_config = ConfigDict(frozen=True)

    # JSON-LD for inter-domain compatibility
    context: str = Field(default="https://schema.org", alias="@context", exclude=True)
    type: str = Field(default="Product", alias="@type", exclude=True)

    id: str  # 플랫폼_상품ID
    platform: str = "naver"
    name: str  # 상품명
    price: int  # 가격
    original_price: int | None = None  # 원가 (할인 전)
    discount_rate: int | None = None  # 할인율
    rating: float | None = None  # 평점 (1.0-5.0)
    review_count: int = 0  # 리뷰 수
    image_url: str  # 상품 이미지
    product_url: str  # 상품 페이지 링크
    mall_name: str = ""  # 판매처명

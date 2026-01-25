"""
🔍 Search Schemas

Pydantic 스키마 정의 (PRD v2).
"""

from pydantic import BaseModel, ConfigDict, Field


class ProductResult(BaseModel):
    """통합 상품 검색 결과 (Schema.org Product)"""

    model_config = ConfigDict(frozen=True)

    # JSON-LD
    context: str = Field(default="https://schema.org", alias="@context", exclude=True)
    type: str = Field(default="Product", alias="@type", exclude=True)

    id: str  # 플랫폼_상품ID
    platform: str  # "naver" | "11st"
    name: str  # 상품명
    price: int  # 가격
    original_price: int | None = None  # 원가 (할인 전)
    discount_rate: int | None = None  # 할인율
    rating: float | None = None  # 평점 (1.0-5.0)
    review_count: int = 0  # 리뷰 수
    image_url: str  # 상품 이미지
    product_url: str  # 상품 페이지 링크
    mall_name: str = ""  # 판매처명


class CompareResult(BaseModel):
    """플랫폼 비교 결과"""

    model_config = ConfigDict(frozen=True)

    query: str  # 원본 질문
    keywords: list[str]  # 추출된 키워드
    products: list[ProductResult]  # 검색 결과
    recommendation: str  # AI 추천 메시지
    cheapest: ProductResult | None = None  # 최저가 상품
    best_rated: ProductResult | None = None  # 최고 평점 상품

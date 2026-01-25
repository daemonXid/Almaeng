"""
🔍 Search Schemas

Pydantic schema definitions (PRD v2).
"""

from pydantic import BaseModel, ConfigDict, Field


class ProductResult(BaseModel):
    """Unified product search result (Schema.org Product)"""

    model_config = ConfigDict(frozen=True)

    # JSON-LD
    context: str = Field(default="https://schema.org", alias="@context", exclude=True)
    type: str = Field(default="Product", alias="@type", exclude=True)

    id: str  # platform_product_id
    platform: str  # "naver" | "11st"
    name: str  # Product name
    price: int  # Price
    original_price: int | None = None  # Original price (before discount)
    discount_rate: int | None = None  # Discount rate
    rating: float | None = None  # Rating (1.0-5.0)
    review_count: int = 0  # Review count
    image_url: str  # Product image URL
    product_url: str  # Product page URL
    mall_name: str = ""  # Mall name


class CompareResult(BaseModel):
    """Platform comparison result"""

    model_config = ConfigDict(frozen=True)

    query: str  # Original query
    keywords: list[str]  # Extracted keywords
    products: list[ProductResult]  # Search results
    recommendation: str  # AI recommendation message
    cheapest: ProductResult | None = None  # Cheapest product
    best_rated: ProductResult | None = None  # Best rated product

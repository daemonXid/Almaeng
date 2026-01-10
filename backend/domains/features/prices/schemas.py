"""
💰 Prices Schemas

Pydantic 스키마 for API validation and serialization.
"""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class PriceHistorySchema(BaseModel):
    """가격 기록 스키마"""

    id: int
    supplement_id: int
    platform: str
    price: Decimal
    original_price: Decimal | None = None
    discount_percent: float | None = None
    url: str = ""
    is_in_stock: bool = True
    recorded_at: datetime


class PriceCompareSchema(BaseModel):
    """플랫폼별 가격 비교"""

    supplement_id: int
    platforms: list[PriceHistorySchema]
    lowest_price: Decimal
    lowest_platform: str
    average_price: Decimal


class PriceTrendSchema(BaseModel):
    """가격 추이"""

    dates: list[str]
    prices: list[Decimal]
    platform: str


class PricePerUnitSchema(BaseModel):
    """단위당 가격"""

    supplement_id: int
    total_price: Decimal
    servings_count: int
    price_per_serving: Decimal
    price_per_day: Decimal | None = None  # 1일 복용 기준


class PriceAlertSchema(BaseModel):
    """가격 알림 스키마"""

    id: int
    supplement_id: int
    target_price: Decimal
    is_active: bool
    current_lowest_price: Decimal | None = None

"""
💊 Supplements Schemas

Pydantic 스키마 for API validation and serialization.
"""

from decimal import Decimal

from pydantic import BaseModel


class IngredientSchema(BaseModel):
    """성분 정보 스키마"""

    name: str
    amount: Decimal
    unit: str
    daily_value_percent: Decimal | None = None


class SupplementSchema(BaseModel):
    """영양제 기본 정보 스키마"""

    id: int
    name: str
    brand: str
    image_url: str = ""
    serving_size: str
    servings_per_container: int


class SupplementDetailSchema(SupplementSchema):
    """영양제 상세 정보 (성분 포함)"""

    ingredients: list[IngredientSchema] = []


class SupplementCompareSchema(BaseModel):
    """성분 비교 결과 스키마"""

    product_a: SupplementDetailSchema
    product_b: SupplementDetailSchema
    matching_ingredients: list[str]
    different_ingredients: list[str]
    match_percentage: float


class OCRAnalysisRequest(BaseModel):
    """OCR 분석 요청"""

    image_base64: str | None = None


class OCRAnalysisResult(BaseModel):
    """OCR 분석 결과"""

    success: bool
    extracted_ingredients: list[IngredientSchema] = []
    raw_text: str = ""
    error_message: str | None = None

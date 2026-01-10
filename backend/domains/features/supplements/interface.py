"""
💊 Supplements Interface

외부 도메인에서 사용하는 공개 API.
다른 도메인에서는 반드시 이 파일을 통해서만 접근해야 합니다.

Usage:
    from domains.features.supplements.interface import (
        get_supplement,
        compare_supplements,
        find_similar_supplements,
    )
"""

from .models import Ingredient, Supplement
from .schemas import (
    IngredientSchema,
    OCRAnalysisResult,
    SupplementCompareSchema,
    SupplementDetailSchema,
    SupplementSchema,
)
from .services import (
    compare_supplements,
    find_similar_supplements,
    get_supplement_with_ingredients,
)

__all__ = [
    "Ingredient",
    "IngredientSchema",
    "OCRAnalysisResult",
    # Models (read-only access)
    "Supplement",
    "SupplementCompareSchema",
    "SupplementDetailSchema",
    # Schemas
    "SupplementSchema",
    "compare_supplements",
    "find_similar_supplements",
    # Services
    "get_supplement_with_ingredients",
]

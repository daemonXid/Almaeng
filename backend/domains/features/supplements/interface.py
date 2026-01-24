"""
💊 Supplements Interface

외부 도메인에서 사용하는 공개 API.
다른 도메인에서는 반드시 이 파일을 통해서만 접근해야 합니다.

Usage:
    from domains.features.supplements.interface import (
        get_supplement,
        compare_supplements,
        find_similar_supplements,
        get_mfds_count,
        search_mfds_products,
    )
"""

from typing import TYPE_CHECKING

from .models import Ingredient, MFDSHealthFood, Supplement
from .schemas import (
    IngredientSchema,
    OCRAnalysisResult,
    SupplementCompareSchema,
    SupplementDetailSchema,
    SupplementSchema,
)
from .services import (
    compare_by_ingredient_price,
    compare_supplements,
    find_similar_supplements,
    generate_embedding_for_mfds,
    generate_embedding_for_supplement,
    get_supplement_with_ingredients,
    search_by_ingredient,
    search_by_vector,
    search_mfds_by_vector,
)

if TYPE_CHECKING:
    from django.db.models import QuerySet


# ============================================================
# MFDS Health Food 관련 함수 (외부 도메인용)
# ============================================================


def get_mfds_count() -> int:
    """MFDS 건강기능식품 총 개수 조회"""
    return MFDSHealthFood.objects.count()


def search_mfds_products(query: str, limit: int = 10) -> "QuerySet[MFDSHealthFood]":
    """
    MFDS 건강기능식품 검색.

    Args:
        query: 검색어 (제품명 또는 회사명)
        limit: 최대 결과 수

    Returns:
        MFDSHealthFood QuerySet
    """
    return MFDSHealthFood.objects.filter(
        product_name__icontains=query
    ).select_related()[:limit]


def get_mfds_product(product_id: int) -> MFDSHealthFood | None:
    """
    MFDS 건강기능식품 단건 조회.

    Args:
        product_id: 제품 ID

    Returns:
        MFDSHealthFood 인스턴스 또는 None
    """
    return MFDSHealthFood.objects.filter(id=product_id).first()


def get_mfds_products_by_ids(product_ids: list[int]) -> "QuerySet[MFDSHealthFood]":
    """
    여러 MFDS 건강기능식품 조회.

    Args:
        product_ids: 제품 ID 목록

    Returns:
        MFDSHealthFood QuerySet
    """
    return MFDSHealthFood.objects.filter(id__in=product_ids)


# ============================================================
# Supplement 관련 함수 (외부 도메인용)
# ============================================================


def get_supplement(supplement_id: int) -> Supplement | None:
    """
    Supplement 단건 조회.

    Args:
        supplement_id: Supplement ID

    Returns:
        Supplement 인스턴스 또는 None
    """
    return Supplement.objects.filter(id=supplement_id).first()


def get_supplement_name(supplement_id: int) -> str:
    """
    Supplement 이름 조회.

    Args:
        supplement_id: Supplement ID

    Returns:
        제품 이름 또는 기본값
    """
    supplement = Supplement.objects.filter(id=supplement_id).values("name").first()
    return supplement["name"] if supplement else f"영양제 #{supplement_id}"


def get_all_supplements() -> "QuerySet[Supplement]":
    """
    모든 Supplement 조회 (배치 작업용).

    Args:
        None

    Returns:
        Supplement QuerySet
    """
    return Supplement.objects.all()


__all__ = [
    # Models (read-only access)
    "Ingredient",
    "MFDSHealthFood",
    "Supplement",
    # Schemas
    "IngredientSchema",
    "OCRAnalysisResult",
    "SupplementCompareSchema",
    "SupplementDetailSchema",
    "SupplementSchema",
    # Services
    "compare_by_ingredient_price",
    "compare_supplements",
    "find_similar_supplements",
    "get_supplement_with_ingredients",
    "search_by_ingredient",
    # MFDS 함수
    "get_mfds_count",
    "get_mfds_product",
    "get_mfds_products_by_ids",
    "search_mfds_products",
    # Supplement 함수
    "get_all_supplements",
    "get_supplement",
    "get_supplement_name",
    # Vector Search 함수
    "search_by_vector",
    "search_mfds_by_vector",
    "generate_embedding_for_supplement",
    "generate_embedding_for_mfds",
]

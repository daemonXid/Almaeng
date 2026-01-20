"""
💊 Supplements Services

비즈니스 로직: 성분 비교, OCR 분석 등.
"""

from decimal import Decimal

from .models import Supplement
from .schemas import IngredientSchema, SupplementCompareSchema, SupplementDetailSchema


def get_supplement_with_ingredients(supplement_id: int) -> SupplementDetailSchema | None:
    """영양제와 성분 정보를 함께 조회"""
    try:
        supplement = Supplement.objects.prefetch_related("ingredients").get(id=supplement_id)
    except Supplement.DoesNotExist:
        return None

    ingredients = [
        IngredientSchema(
            name=ing.name,
            amount=ing.amount,
            unit=ing.unit,
            daily_value_percent=ing.daily_value_percent,
        )
        for ing in supplement.ingredients.all()
    ]

    return SupplementDetailSchema(
        id=supplement.id,
        name=supplement.name,
        brand=supplement.brand,
        image_url=supplement.image_url,
        serving_size=supplement.serving_size,
        servings_per_container=supplement.servings_per_container,
        ingredients=ingredients,
    )


def compare_supplements(supplement_a_id: int, supplement_b_id: int) -> SupplementCompareSchema | None:
    """두 영양제의 성분을 비교"""
    product_a = get_supplement_with_ingredients(supplement_a_id)
    product_b = get_supplement_with_ingredients(supplement_b_id)

    if not product_a or not product_b:
        return None

    # 성분명 세트 생성
    ingredients_a = {ing.name.lower() for ing in product_a.ingredients}
    ingredients_b = {ing.name.lower() for ing in product_b.ingredients}

    # 일치/차이 계산
    matching = ingredients_a & ingredients_b
    different = (ingredients_a | ingredients_b) - matching

    # 일치율 계산
    total = len(ingredients_a | ingredients_b)
    match_percentage = (len(matching) / total * 100) if total > 0 else 0.0

    return SupplementCompareSchema(
        product_a=product_a,
        product_b=product_b,
        matching_ingredients=sorted(matching),
        different_ingredients=sorted(different),
        match_percentage=round(match_percentage, 1),
    )


def find_similar_supplements(supplement_id: int, min_match_percent: float = 70.0) -> list[dict]:
    """유사한 성분 구성을 가진 영양제 찾기"""
    source = get_supplement_with_ingredients(supplement_id)
    if not source:
        return []

    source_ingredients = {ing.name.lower() for ing in source.ingredients}
    results = []

    for supplement in Supplement.objects.exclude(id=supplement_id):
        target_ingredients = {ing.name.lower() for ing in supplement.ingredients.all()}
        matching = source_ingredients & target_ingredients
        total = len(source_ingredients | target_ingredients)

        if total > 0:
            match_percent = len(matching) / total * 100
            if match_percent >= min_match_percent:
                results.append(
                    {
                        "supplement_id": supplement.id,
                        "name": supplement.name,
                        "brand": supplement.brand,
                        "match_percentage": round(match_percent, 1),
                        "matching_count": len(matching),
                    }
                )

    return sorted(results, key=lambda x: x["match_percentage"], reverse=True)


def normalize_unit(amount: Decimal, unit: str) -> tuple[Decimal, str]:
    """단위 정규화 (mg, mcg 등)"""
    unit_lower = unit.lower()

    # mcg → mg 변환
    if unit_lower == "mcg":
        return amount / 1000, "mg"

    # g → mg 변환
    if unit_lower == "g":
        return amount * 1000, "mg"

    return amount, unit


# ============================================================
# OCR 결과 저장
# ============================================================

from django.db import transaction
from .models import Ingredient


@transaction.atomic
def create_supplement_from_ocr(
    product_name: str,
    brand: str,
    serving_size: str,
    servings_count: int,
    ingredients: list[dict],
) -> Supplement:
    """
    OCR 분석 결과를 Supplement + Ingredient로 저장.

    Args:
        product_name: 제품명
        brand: 브랜드명
        serving_size: 1회 섭취량 (예: "1정")
        servings_count: 총 섭취 횟수
        ingredients: 성분 목록 [{name, amount, unit, daily_value}, ...]

    Returns:
        생성된 Supplement 인스턴스
    """
    supplement = Supplement.objects.create(
        name=product_name,
        brand=brand or "Unknown",
        serving_size=serving_size or "1회",
        servings_per_container=servings_count or 1,
    )

    for ing_data in ingredients:
        name = ing_data.get("name", "").strip()
        if not name:
            continue

        # 함량 파싱
        amount_str = ing_data.get("amount", "0")
        try:
            amount = Decimal(str(amount_str)) if amount_str else Decimal(0)
        except (ValueError, TypeError):
            amount = Decimal(0)

        # 단위 정규화
        unit = ing_data.get("unit", "mg").lower()
        if unit not in ["mg", "mcg", "g", "iu", "cfu", "ml"]:
            unit = "mg"

        # 일일 권장량 % 파싱
        daily_value_str = ing_data.get("daily_value", "")
        daily_value = None
        if daily_value_str:
            try:
                # "50%" -> 50
                cleaned = str(daily_value_str).replace("%", "").strip()
                if cleaned:
                    daily_value = Decimal(cleaned)
            except (ValueError, TypeError):
                pass

        Ingredient.objects.create(
            supplement=supplement,
            name=name,
            amount=amount,
            unit=unit,
            daily_value_percent=daily_value,
        )

    return supplement

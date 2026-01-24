"""
💊 Supplements Services

비즈니스 로직 및 서비스 함수.
"""

from decimal import Decimal
from typing import TYPE_CHECKING

from django.db.models import Q, QuerySet
from pgvector.django import CosineDistance

from .conf import settings as supplements_settings
from .models import MFDSHealthFood, Supplement

if TYPE_CHECKING:
    from .logic.sets import ValueMetrics


def search_by_ingredient(ingredient_name: str, limit: int = 20) -> QuerySet[Supplement]:
    """
    성분명으로 영양제 검색
    
    Args:
        ingredient_name: 검색할 성분명 (예: "비타민C")
        limit: 최대 결과 수
        
    Returns:
        QuerySet[Supplement]
    """
    return Supplement.objects.filter(
        ingredients__name__icontains=ingredient_name
    ).distinct()[:limit]


def find_similar_supplements(
    supplement_id: int,
    min_match_percent: float = 50.0,
    limit: int = 10,
) -> list[Supplement]:
    """
    성분 구성이 유사한 영양제 찾기
    
    Args:
        supplement_id: 기준 영양제 ID
        min_match_percent: 최소 일치율 (%)
        limit: 최대 결과 수
        
    Returns:
        list[Supplement]
    """
    try:
        base_supplement = Supplement.objects.get(id=supplement_id)
    except Supplement.DoesNotExist:
        return []
    
    # 기준 영양제의 성분 목록
    base_ingredients = set(
        base_supplement.ingredients.values_list("name", flat=True)
    )
    
    if not base_ingredients:
        return []
    
    # 모든 영양제를 순회하며 유사도 계산
    all_supplements = Supplement.objects.exclude(id=supplement_id).prefetch_related(
        "ingredients"
    )
    
    similar_products = []
    for supplement in all_supplements:
        supplement_ingredients = set(
            supplement.ingredients.values_list("name", flat=True)
        )
        
        if not supplement_ingredients:
            continue
        
        # 교집합 / 합집합으로 유사도 계산
        intersection = base_ingredients & supplement_ingredients
        union = base_ingredients | supplement_ingredients
        
        if not union:
            continue
        
        match_percent = (len(intersection) / len(union)) * 100
        
        if match_percent >= min_match_percent:
            similar_products.append((supplement, match_percent))
    
    # 유사도 순으로 정렬
    similar_products.sort(key=lambda x: x[1], reverse=True)
    
    return [product for product, _ in similar_products[:limit]]


def compare_by_ingredient_price(
    ingredient_name: str,
    prices: dict[int, Decimal],
) -> list[dict]:
    """
    동일 성분 함량 대비 가격 비교
    
    Args:
        ingredient_name: 비교할 성분명
        prices: {supplement_id: price} 딕셔너리
        
    Returns:
        list[dict]: 가성비 순위 리스트
    """
    from .logic.sets import calculate_value_metrics
    
    supplements = Supplement.objects.filter(
        id__in=prices.keys()
    ).prefetch_related("ingredients")
    
    comparison_data = []
    
    for supplement in supplements:
        price = prices.get(supplement.id)
        if not price:
            continue
        
        # Value metrics 계산
        value_metrics = calculate_value_metrics(
            supplement,
            price,
            servings=30,  # 기본값
        )
        
        if value_metrics:
            comparison_data.append({
                "supplement_id": supplement.id,
                "name": supplement.name,
                "brand": supplement.brand,
                "image_url": supplement.image_url,
                "price": float(price),
                "amount_per_serving": float(value_metrics.amount_per_serving),
                "unit": value_metrics.unit,
                "unit_cost": float(value_metrics.unit_cost),
                "percentile": value_metrics.percentile,
                "rank_label": value_metrics.rank_label,
            })
    
    # unit_cost 기준으로 정렬 (낮을수록 좋음)
    comparison_data.sort(key=lambda x: x["unit_cost"])
    
    return comparison_data


def calculate_price_per_unit(
    supplement: Supplement,
    price: Decimal,
) -> dict | None:
    """
    단위당 가격 계산 (가성비 분석)
    
    Args:
        supplement: Supplement 인스턴스
        price: 제품 가격 (KRW)
        
    Returns:
        dict | None: 가성비 정보 또는 None
    """
    from .logic.sets import calculate_value_metrics
    
    value_metrics = calculate_value_metrics(supplement, price, servings=supplements_settings.DEFAULT_SERVINGS)
    
    if not value_metrics:
        return None
    
    return {
        "ingredient_name": value_metrics.primary_ingredient,
        "amount_per_serving": value_metrics.amount_per_serving,
        "unit": value_metrics.unit,
        "total_amount": value_metrics.amount_per_serving * supplements_settings.DEFAULT_SERVINGS,
        "price_per_unit": value_metrics.unit_cost,
        "price_per_serving": float(price) / supplements_settings.DEFAULT_SERVINGS,
    }


def search_by_vector(
    query_text: str,
    limit: int = 10,
    threshold: float = 0.7,
) -> list[Supplement]:
    """
    벡터 유사도 검색 (pgvector + Gemini embedding)
    
    Args:
        query_text: 검색 쿼리 텍스트
        limit: 최대 결과 수
        threshold: 최소 유사도 임계값 (0.0 ~ 1.0)
        
    Returns:
        list[Supplement]: 유사도 순으로 정렬된 영양제 리스트
    """
    from domains.ai.service.providers.gemini import GeminiProvider
    
    # 쿼리 텍스트를 벡터로 변환
    provider = GeminiProvider()
    query_embedding = provider.embed(query_text)
    
    if not query_embedding:
        return []
    
    # 벡터 유사도 검색 (Cosine Distance 사용)
    # Cosine Distance가 작을수록 유사함 (0 = 동일, 1 = 완전히 다름)
    # 따라서 threshold는 작을수록 엄격한 검색
    results = (
        Supplement.objects
        .filter(embedding__isnull=False)
        .annotate(
            distance=CosineDistance("embedding", query_embedding)
        )
        .filter(distance__lte=1.0 - threshold)  # similarity = 1 - distance
        .order_by("distance")
        [:limit]
    )
    
    return list(results)


def search_mfds_by_vector(
    query_text: str,
    limit: int = 10,
    threshold: float = 0.7,
) -> list[MFDSHealthFood]:
    """
    MFDS 데이터 벡터 유사도 검색
    
    Args:
        query_text: 검색 쿼리 텍스트
        limit: 최대 결과 수
        threshold: 최소 유사도 임계값 (0.0 ~ 1.0)
        
    Returns:
        list[MFDSHealthFood]: 유사도 순으로 정렬된 제품 리스트
    """
    from domains.ai.service.providers.gemini import GeminiProvider
    
    # 쿼리 텍스트를 벡터로 변환
    provider = GeminiProvider()
    query_embedding = provider.embed(query_text)
    
    if not query_embedding:
        return []
    
    # 벡터 유사도 검색
    results = (
        MFDSHealthFood.objects
        .filter(embedding__isnull=False)
        .annotate(
            distance=CosineDistance("embedding", query_embedding)
        )
        .filter(distance__lte=1.0 - threshold)
        .order_by("distance")
        [:limit]
    )
    
    return list(results)


def generate_embedding_for_supplement(supplement: Supplement) -> list[float] | None:
    """
    Supplement의 임베딩 벡터 생성 및 저장
    
    Args:
        supplement: Supplement 인스턴스
        
    Returns:
        list[float] | None: 생성된 임베딩 벡터 또는 None
    """
    from domains.ai.service.providers.gemini import GeminiProvider
    
    # 임베딩 생성용 텍스트 조합
    # 제품명, 브랜드, 설명, 성분 정보를 결합
    text_parts = [
        supplement.name,
        supplement.brand,
        supplement.description or "",
    ]
    
    # 성분 정보 추가
    ingredients_text = ", ".join(
        f"{ing.name} {ing.amount}{ing.unit}"
        for ing in supplement.ingredients.all()
    )
    if ingredients_text:
        text_parts.append(ingredients_text)
    
    embedding_text = " ".join(text_parts)
    
    # Gemini로 임베딩 생성
    provider = GeminiProvider()
    embedding = provider.embed(embedding_text)
    
    if embedding and len(embedding) == 768:  # Gemini embedding-001은 768차원
        # DB에 저장
        supplement.embedding = embedding
        supplement.save(update_fields=["embedding"])
        return embedding
    
    return None


def generate_embedding_for_mfds(mfds: MFDSHealthFood) -> list[float] | None:
    """
    MFDSHealthFood의 임베딩 벡터 생성 및 저장
    
    Args:
        mfds: MFDSHealthFood 인스턴스
        
    Returns:
        list[float] | None: 생성된 임베딩 벡터 또는 None
    """
    from domains.ai.service.providers.gemini import GeminiProvider
    
    # 임베딩 생성용 텍스트 조합
    text_parts = [
        mfds.product_name,
        mfds.company_name,
        mfds.functionality or "",
        mfds.raw_materials or "",
    ]
    
    embedding_text = " ".join(text_parts)
    
    # Gemini로 임베딩 생성
    provider = GeminiProvider()
    embedding = provider.embed(embedding_text)
    
    if embedding and len(embedding) == 768:  # Gemini embedding-001은 768차원
        # DB에 저장
        mfds.embedding = embedding
        mfds.save(update_fields=["embedding"])
        return embedding
    
    return None


def compare_supplements(
    supplement_a_id: int,
    supplement_b_id: int,
) -> dict:
    """
    두 영양제의 성분 비교
    
    Args:
        supplement_a_id: 첫 번째 영양제 ID
        supplement_b_id: 두 번째 영양제 ID
        
    Returns:
        dict: 비교 결과 (matching_ingredients, different_ingredients, match_percentage)
    """
    try:
        supplement_a = Supplement.objects.prefetch_related("ingredients").get(id=supplement_a_id)
        supplement_b = Supplement.objects.prefetch_related("ingredients").get(id=supplement_b_id)
    except Supplement.DoesNotExist:
        return {
            "matching_ingredients": [],
            "different_ingredients": [],
            "match_percentage": 0.0,
        }
    
    ingredients_a = set(supplement_a.ingredients.values_list("name", flat=True))
    ingredients_b = set(supplement_b.ingredients.values_list("name", flat=True))
    
    matching = ingredients_a & ingredients_b
    different_a = ingredients_a - ingredients_b
    different_b = ingredients_b - ingredients_a
    
    union = ingredients_a | ingredients_b
    match_percentage = (len(matching) / len(union) * 100) if union else 0.0
    
    return {
        "matching_ingredients": list(matching),
        "different_ingredients": list(different_a | different_b),
        "match_percentage": match_percentage,
    }


def get_supplement_with_ingredients(supplement_id: int) -> Supplement | None:
    """
    Supplement와 성분 정보를 함께 조회
    
    Args:
        supplement_id: Supplement ID
        
    Returns:
        Supplement 인스턴스 (ingredients prefetch) 또는 None
    """
    return Supplement.objects.prefetch_related("ingredients").filter(id=supplement_id).first()

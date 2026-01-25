"""
🔍 Search Services

검색 로직 (키워드 추출, 멀티 플랫폼 검색).
"""

import asyncio
from typing import Any

from domains.integrations.elevenst.interface import search_elevenst_products
from domains.integrations.gemini.interface import extract_keywords, generate_recommendation
from domains.integrations.naver.interface import search_naver_products

from .schemas import CompareResult, ProductResult


async def search_products(query: str, limit: int = 20) -> CompareResult:
    """
    자연어 질문으로 상품 검색 (멀티 플랫폼)

    Args:
        query: 사용자 자연어 질문
        limit: 플랫폼당 최대 결과 수

    Returns:
        CompareResult: 검색 결과 및 추천 메시지
    """
    # 1. 키워드 추출
    extraction = extract_keywords(query)
    keywords = extraction.keywords

    # 2. 병렬 API 호출
    naver_task = search_naver_products(keywords[0] if keywords else query, limit=limit)
    elevenst_task = search_elevenst_products(keywords[0] if keywords else query, limit=limit)

    naver_results: Any
    elevenst_results: Any
    naver_results, elevenst_results = await asyncio.gather(naver_task, elevenst_task, return_exceptions=True)

    # 3. 결과 통합 및 변환
    products: list[ProductResult] = []

    # 네이버 결과 변환
    if isinstance(naver_results, list):
        for item in naver_results:
            products.append(
                ProductResult(
                    id=f"naver_{item.product_name}",
                    platform="naver",
                    name=item.product_name,
                    price=int(item.price),
                    original_price=int(item.original_price) if item.original_price else None,
                    discount_rate=item.discount_percent,
                    image_url=item.image_url,
                    product_url=item.url,
                    mall_name=item.mall_name,
                )
            )

    # 11번가 결과 변환 (구현 후)
    if isinstance(elevenst_results, list):
        for item in elevenst_results:
            products.append(
                ProductResult(
                    id=f"11st_{item.product_name}",
                    platform="11st",
                    name=item.product_name,
                    price=int(item.price),
                    original_price=int(item.original_price) if item.original_price else None,
                    discount_rate=item.discount_percent,
                    image_url=item.image_url,
                    product_url=item.url,
                    mall_name=item.mall_name,
                )
            )

    # 4. 정렬 (가격순, 평점순)
    products_by_price = sorted(products, key=lambda x: x.price)
    products_by_rating = sorted([p for p in products if p.rating], key=lambda x: x.rating or 0, reverse=True)

    cheapest = products_by_price[0] if products_by_price else None
    best_rated = products_by_rating[0] if products_by_rating else None

    # 5. AI 추천 메시지 생성
    import json

    products_json = json.dumps([p.model_dump() for p in products[:5]], ensure_ascii=False)
    recommendation = generate_recommendation(query, products_json)

    return CompareResult(
        query=query,
        keywords=keywords,
        products=products,
        recommendation=recommendation,
        cheapest=cheapest,
        best_rated=best_rated,
    )

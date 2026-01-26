"""
🔍 Search Logic Services

Pure business logic for search operations (Stateless Processor).
This module contains pure functions without external dependencies.
"""

import random

from .schemas import ProductResult


def transform_naver_results(naver_results: list) -> list[ProductResult]:
    """
    Transform Naver API results to ProductResult schema

    Args:
        naver_results: Raw Naver API results

    Returns:
        list[ProductResult]: Transformed product results
    """
    products: list[ProductResult] = []
    if isinstance(naver_results, list):
        for item in naver_results:
            try:
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
            except (AttributeError, ValueError, TypeError):
                continue
    return products


def transform_elevenst_results(elevenst_results: list) -> list[ProductResult]:
    """
    Transform 11st API results to ProductResult schema

    Args:
        elevenst_results: Raw 11st API results

    Returns:
        list[ProductResult]: Transformed product results
    """
    products: list[ProductResult] = []
    if isinstance(elevenst_results, list):
        for item in elevenst_results:
            try:
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
            except (AttributeError, ValueError, TypeError):
                continue
    return products


def transform_coupang_manual_results(coupang_products: list) -> list[ProductResult]:
    """
    Transform Coupang manual DB products to ProductResult schema

    Args:
        coupang_products: Coupang manual product models

    Returns:
        list[ProductResult]: Transformed product results
    """
    products: list[ProductResult] = []
    for item in coupang_products:
        try:
            products.append(
                ProductResult(
                    id=f"coupang_{item.product_id}",
                    platform="coupang",
                    name=item.name,
                    price=item.price,
                    original_price=None,
                    discount_rate=None,
                    image_url=item.image_url,
                    product_url=item.affiliate_url,  # 파트너스 링크 사용
                    mall_name="쿠팡",
                )
            )
        except (AttributeError, ValueError, TypeError):
            continue
    return products


def aggregate_search_results(
    products: list[ProductResult],
) -> tuple[ProductResult | None, ProductResult | None]:
    """
    Aggregate search results and find cheapest/best rated products

    Args:
        products: List of products

    Returns:
        tuple: (cheapest, best_rated)
    """
    products_by_price = sorted(products, key=lambda x: x.price)
    products_by_rating = sorted([p for p in products if p.rating], key=lambda x: x.rating or 0, reverse=True)

    cheapest = products_by_price[0] if products_by_price else None
    best_rated = products_by_rating[0] if products_by_rating else None

    return cheapest, best_rated


def mix_search_results(
    coupang_products: list[ProductResult],
    naver_products: list[ProductResult],
    elevenst_products: list[ProductResult],
    coupang_ratio: float = 0.7,
    naver_ratio: float = 0.2,
    elevenst_ratio: float = 0.1,
) -> list[ProductResult]:
    """
    Mix search results from different platforms with specified ratios

    쿠팡: 70% (수동 DB + API 혼합)
    네이버: 20%
    11번가: 10%

    Args:
        coupang_products: Coupang products
        naver_products: Naver products
        elevenst_products: 11st products
        coupang_ratio: Coupang ratio (default: 0.7)
        naver_ratio: Naver ratio (default: 0.2)
        elevenst_ratio: 11st ratio (default: 0.1)

    Returns:
        list[ProductResult]: Mixed product results
    """
    total_count = len(coupang_products) + len(naver_products) + len(elevenst_products)
    if total_count == 0:
        return []

    # 각 플랫폼별 목표 개수 계산
    coupang_count = int(total_count * coupang_ratio)
    naver_count = int(total_count * naver_ratio)
    elevenst_count = total_count - coupang_count - naver_count

    # 각 플랫폼에서 랜덤 샘플링
    selected_coupang = random.sample(coupang_products, min(coupang_count, len(coupang_products)))
    selected_naver = random.sample(naver_products, min(naver_count, len(naver_products)))
    selected_elevenst = random.sample(elevenst_products, min(elevenst_count, len(elevenst_products)))

    # 결과 합치기 및 섞기
    mixed_results = selected_coupang + selected_naver + selected_elevenst
    random.shuffle(mixed_results)

    return mixed_results

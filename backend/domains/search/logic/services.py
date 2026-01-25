"""
🔍 Search Logic Services

Pure business logic for search operations (Stateless Processor).
This module contains pure functions without external dependencies.
"""

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

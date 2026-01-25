"""
⚖️ Compare Services

가격 비교 로직.
"""

from domains.search.logic.schemas import ProductResult


def sort_by_price(products: list[ProductResult], reverse: bool = False) -> list[ProductResult]:
    """가격순 정렬"""
    return sorted(products, key=lambda x: x.price, reverse=reverse)


def sort_by_rating(products: list[ProductResult], reverse: bool = True) -> list[ProductResult]:
    """평점순 정렬"""
    return sorted(
        products,
        key=lambda x: (x.rating or 0, x.review_count),
        reverse=reverse,
    )


def sort_by_review_count(products: list[ProductResult], reverse: bool = True) -> list[ProductResult]:
    """리뷰 수순 정렬"""
    return sorted(products, key=lambda x: x.review_count, reverse=reverse)

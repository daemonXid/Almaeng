from .models import WishlistItem


def get_wishlist_by_user(*, user_id: int):
    """
    특정 사용자의 찜 목록을 조회합니다.
    """
    return WishlistItem.objects.filter(user_id=user_id).order_by("-created_at")


def is_product_in_wishlist(*, user_id: int, product_id: str, platform: str) -> bool:
    """
    특정 상품이 찜 목록에 있는지 확인합니다.
    """
    return WishlistItem.objects.filter(
        user_id=user_id, product_id=product_id, platform=platform
    ).exists()

"""
❤️ Wishlist Services
"""

from decimal import Decimal

from .models import WishlistItem


def add_to_wishlist(
    user_id: int,
    supplement_id: int,
    notify_price_drop: bool = False,
    target_price: Decimal | None = None,
) -> WishlistItem:
    """찜 목록에 추가"""
    item, _created = WishlistItem.objects.get_or_create(
        user_id=user_id,
        supplement_id=supplement_id,
        defaults={
            "notify_price_drop": notify_price_drop,
            "target_price": target_price,
        },
    )
    return item


def remove_from_wishlist(user_id: int, supplement_id: int) -> bool:
    """찜 목록에서 제거"""
    deleted, _ = WishlistItem.objects.filter(user_id=user_id, supplement_id=supplement_id).delete()
    return deleted > 0


def is_in_wishlist(user_id: int, supplement_id: int) -> bool:
    """찜 여부 확인"""
    return WishlistItem.objects.filter(user_id=user_id, supplement_id=supplement_id).exists()


def get_user_wishlist(user_id: int) -> list[WishlistItem]:
    """사용자의 찜 목록 조회"""
    return list(WishlistItem.objects.filter(user_id=user_id))


def toggle_wishlist(user_id: int, supplement_id: int) -> tuple[bool, bool]:
    """찜 토글 - (is_added, is_now_in_wishlist)"""
    if is_in_wishlist(user_id, supplement_id):
        remove_from_wishlist(user_id, supplement_id)
        return False, False
    else:
        add_to_wishlist(user_id, supplement_id)
        return True, True

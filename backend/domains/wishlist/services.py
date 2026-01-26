from django.db import transaction

from .models import WishlistItem


@transaction.atomic
def toggle_wishlist_item(
    *,
    user_id: int,
    product_id: str,
    platform: str,
    name: str = "",
    price: int = 0,
    image_url: str = "",
    product_url: str = "",
) -> tuple[bool, str]:
    """
    찜 목록에 상품을 추가하거나 이미 있으면 제거합니다.

    Returns:
        tuple[bool, str]: (추가됨 여부, 메시지)
    """
    item, created = WishlistItem.objects.get_or_create(
        user_id=user_id,
        product_id=product_id,
        platform=platform,
        defaults={
            "name": name,
            "price": price,
            "image_url": image_url,
            "product_url": product_url,
        },
    )

    if not created:
        item.delete()
        return False, "찜 목록에서 삭제되었습니다."

    return True, "찜 목록에 추가되었습니다."

from .services import toggle_wishlist_item
from .selectors import get_wishlist_by_user


def toggle_wishlist(
    user_id: int,
    product_id: str,
    platform: str,
    name: str = "",
    price: int = 0,
    image_url: str = "",
    product_url: str = "",
) -> tuple[bool, str]:
    """Expose wishlist toggle logic"""
    return toggle_wishlist_item(
        user_id=user_id,
        product_id=product_id,
        platform=platform,
        name=name,
        price=price,
        image_url=image_url,
        product_url=product_url,
    )


def get_user_wishlist(user_id: int):
    """Expose wishlist listing logic"""
    return get_wishlist_by_user(user_id=user_id)

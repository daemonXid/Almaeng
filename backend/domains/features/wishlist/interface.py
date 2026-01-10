"""
❤️ Wishlist Interface
"""

from .models import WishlistItem
from .services import (
    add_to_wishlist,
    get_user_wishlist,
    is_in_wishlist,
    remove_from_wishlist,
    toggle_wishlist,
)

__all__ = [
    "WishlistItem",
    "add_to_wishlist",
    "get_user_wishlist",
    "is_in_wishlist",
    "remove_from_wishlist",
    "toggle_wishlist",
]

"""
🛒 Cart Interface

외부 도메인에서 사용하는 공개 API.
"""

from .models import Cart, CartItem
from .services import (
    add_item,
    clear_cart,
    get_or_create_cart,
    merge_carts,
    remove_item,
    update_quantity,
)

__all__ = [
    "Cart",
    "CartItem",
    "add_item",
    "clear_cart",
    "get_or_create_cart",
    "merge_carts",
    "remove_item",
    "update_quantity",
]

"""
🛒 Cart Services

장바구니 비즈니스 로직.
"""

from decimal import Decimal

from django.db import transaction

from .models import Cart, CartItem


def get_or_create_cart(user_id: int | None = None, session_key: str | None = None) -> Cart:
    """장바구니 조회 또는 생성"""
    if user_id:
        cart, _ = Cart.objects.get_or_create(user_id=user_id)
    elif session_key:
        cart, _ = Cart.objects.get_or_create(session_key=session_key)
    else:
        raise ValueError("user_id 또는 session_key 필요")
    return cart


def add_item(
    cart: Cart,
    supplement_id: int,
    platform: str,
    quantity: int = 1,
    unit_price: Decimal = Decimal(0),
) -> CartItem:
    """장바구니에 아이템 추가"""
    item, created = CartItem.objects.get_or_create(
        cart=cart,
        supplement_id=supplement_id,
        platform=platform,
        defaults={"quantity": quantity, "unit_price": unit_price},
    )
    if not created:
        item.quantity += quantity
        item.save()
    return item


def update_quantity(cart: Cart, item_id: int, quantity: int) -> CartItem | None:
    """수량 업데이트"""
    try:
        item = cart.items.get(id=item_id)
        if quantity <= 0:
            item.delete()
            return None
        item.quantity = quantity
        item.save()
        return item
    except CartItem.DoesNotExist:
        return None


def remove_item(cart: Cart, item_id: int) -> bool:
    """아이템 제거"""
    deleted, _ = cart.items.filter(id=item_id).delete()
    return deleted > 0


def clear_cart(cart: Cart) -> int:
    """장바구니 비우기"""
    deleted, _ = cart.items.all().delete()
    return deleted


@transaction.atomic
def merge_carts(session_cart: Cart, user_cart: Cart) -> Cart:
    """세션 장바구니를 사용자 장바구니로 병합 (로그인 시)"""
    for item in session_cart.items.all():
        existing = user_cart.items.filter(supplement_id=item.supplement_id, platform=item.platform).first()
        if existing:
            existing.quantity += item.quantity
            existing.save()
        else:
            item.cart = user_cart
            item.save()

    session_cart.delete()
    return user_cart

"""
🛒 Cart Page Views
"""

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST

from ...services import add_item, get_or_create_cart, remove_item, update_quantity


def _get_cart(request: HttpRequest):
    """현재 사용자/세션의 장바구니 가져오기"""
    if request.user.is_authenticated:
        return get_or_create_cart(user_id=request.user.id)

    # 익명 사용자: 세션이 없으면 생성
    if not request.session.session_key:
        request.session.create()

    return get_or_create_cart(session_key=request.session.session_key)


def cart_page(request: HttpRequest) -> HttpResponse:
    """장바구니 페이지"""
    cart = _get_cart(request)

    return render(
        request,
        "cart/pages/cart/cart.html",
        {
            "page_title": "장바구니 | ALMAENG",
            "cart": cart,
        },
    )


@require_POST
def add_to_cart(request: HttpRequest) -> HttpResponse:
    """HTMX: 장바구니에 추가"""
    from decimal import Decimal

    cart = _get_cart(request)

    supplement_id = int(request.POST.get("supplement_id", 0))
    platform = request.POST.get("platform", "iherb")
    quantity = int(request.POST.get("quantity", 1))
    unit_price = Decimal(request.POST.get("unit_price", 0))

    add_item(cart, supplement_id, platform, quantity, unit_price)

    # 장바구니 카운트 반환 (헤더 업데이트용)
    return HttpResponse(f"""
        <span id="cart-count" hx-swap-oob="true"
              class="px-2 py-0.5 rounded-full bg-emerald-500 text-white text-xs">
            {cart.total_items}
        </span>
        <div class="text-emerald-600">✅ 장바구니에 추가됨</div>
    """)


@require_POST
def update_cart_item(request: HttpRequest, item_id: int) -> HttpResponse:
    """HTMX: 수량 업데이트"""
    cart = _get_cart(request)
    quantity = int(request.POST.get("quantity", 1))

    update_quantity(cart, item_id, quantity)

    return render(
        request,
        "cart/pages/cart/_items.html",
        {"cart": cart},
    )


@require_POST
def remove_from_cart(request: HttpRequest, item_id: int) -> HttpResponse:
    """HTMX: 장바구니에서 제거"""
    cart = _get_cart(request)
    remove_item(cart, item_id)

    return render(
        request,
        "cart/pages/cart/_items.html",
        {"cart": cart},
    )


def cart_count(request: HttpRequest) -> HttpResponse:
    """HTMX: 장바구니 카운트 (헤더용)"""
    try:
        cart = _get_cart(request)
        count = cart.total_items

        if count > 0:
            return HttpResponse(f"""
                <span class="px-2 py-0.5 rounded-full bg-emerald-500 text-white text-xs">
                    {count}
                </span>
            """)
    except Exception:
        pass  # DB 에러 등 무시
    return HttpResponse("")

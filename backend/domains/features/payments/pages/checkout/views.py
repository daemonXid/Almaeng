"""
💳 Checkout Page Views
"""

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from domains.features.cart.interface import get_or_create_cart

from ...services import get_order_by_id, update_payment_status


@login_required
def checkout_page(request: HttpRequest) -> HttpResponse:
    """결제 페이지"""
    cart = get_or_create_cart(user_id=request.user.id)

    if not cart.items.exists():
        return redirect("cart:cart")

    # Toss Payments Client Key
    toss_client_key = getattr(settings, "TOSS_CLIENT_KEY", "test_ck_...")

    return render(
        request,
        "payments/pages/checkout/checkout.html",
        {
            "page_title": "결제 | ALMAENG",
            "cart": cart,
            "toss_client_key": toss_client_key,
        },
    )


# @require_POST -> Widget callback uses GET
def payment_confirm(request: HttpRequest) -> HttpResponse:
    """결제 승인 (Toss Widget Success Url Callback)"""
    import asyncio
    from ...integrations.toss import toss_client

    # Support both GET (Widget) and POST (API)
    data = request.GET if request.method == "GET" else request.POST
    
    payment_key = data.get("paymentKey", "")
    order_id = data.get("orderId", "")
    amount = int(data.get("amount", 0))

    order = get_order_by_id(order_id)
    if not order:
        return HttpResponse("주문을 찾을 수 없습니다", status=404)

    # Toss API 호출 (비동기 → 동기 변환)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(toss_client.confirm_payment(payment_key, order_id, amount))
    loop.close()

    if result.success:
        update_payment_status(
            order,
            payment_key=result.payment_key,
            status="done",
            method=result.method,
            approved_at=result.approved_at,
        )
        return redirect("payments:success")
    else:
        return redirect(f"/payments/fail/?code={result.error_code}&message={result.error_message}")


def payment_success(request: HttpRequest) -> HttpResponse:
    """결제 성공 페이지"""
    return render(
        request,
        "payments/pages/checkout/success.html",
        {"page_title": "결제 완료 | ALMAENG"},
    )


def payment_fail(request: HttpRequest) -> HttpResponse:
    """결제 실패 페이지"""
    error_code = request.GET.get("code", "UNKNOWN")
    error_message = request.GET.get("message", "결제에 실패했습니다")

    return render(
        request,
        "payments/pages/checkout/fail.html",
        {
            "page_title": "결제 실패 | ALMAENG",
            "error_code": error_code,
            "error_message": error_message,
        },
    )

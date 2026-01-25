"""
💳 Checkout Page Views

결제 페이지 (PRD v2).
"""

from django.conf import settings
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
import uuid

from ...state.interface import create_order, get_order_by_uuid, update_order_payment


def checkout_page(request: HttpRequest) -> HttpResponse:
    """
    결제 페이지

    GET: 결제 페이지 표시 (상품 정보를 쿼리 파라미터로 전달)
    """
    # GET: 결제 페이지 표시
    product_id = request.GET.get("product_id", "")
    product_name = request.GET.get("name", "")
    platform = request.GET.get("platform", "naver")
    product_url = request.GET.get("url", "")
    image_url = request.GET.get("image", "")
    amount = request.GET.get("price", "0")

    # 가격 파싱 (문자열에서 숫자만 추출)
    try:
        amount = int("".join(c for c in str(amount) if c.isdigit()) or "0")
    except (ValueError, TypeError):
        amount = 0

    if not product_id or amount <= 0:
        return render(
            request,
            "pages/checkout/checkout.html",
            {
                "page_title": "결제 오류",
                "error": "상품 정보가 올바르지 않습니다. 다시 시도해주세요.",
            },
        )

    # 주문 생성
    order = create_order(
        user_id=request.user.id if request.user.is_authenticated else None,
        product_id=product_id,
        product_name=product_name,
        platform=platform,
        product_url=product_url,
        amount=amount,
    )

    # Toss Payments Client Key (settings에서 가져오기)
    toss_client_key = getattr(settings, "TOSS_CLIENT_KEY", "test_ck_D5GePWvyJnrK0W0k6q8gLzN97Eoq")

    # Success/Fail URL
    success_url = request.build_absolute_uri(reverse("billing:success"))
    fail_url = request.build_absolute_uri(reverse("billing:fail"))

    return render(
        request,
        "pages/checkout/checkout.html",
        {
            "page_title": f"{product_name} 결제",
            "order_id": str(order.order_id),
            "product_id": product_id,
            "product_name": product_name,
            "platform": platform,
            "product_url": product_url,
            "image_url": image_url,
            "amount": amount,
            "toss_client_key": toss_client_key,
            "success_url": success_url,
            "fail_url": fail_url,
        },
    )


def payment_success(request: HttpRequest) -> HttpResponse:
    """
    결제 성공 페이지 (Toss Widget Success Callback)
    """
    payment_key = request.GET.get("paymentKey", "")
    order_id = request.GET.get("orderId", "")
    amount = request.GET.get("amount", "0")

    try:
        amount = int(amount)
    except (ValueError, TypeError):
        amount = 0

    # 주문 조회 및 결제 정보 업데이트
    if order_id:
        order = get_order_by_uuid(order_id)
        if order:
            update_order_payment(order, payment_key=payment_key, status="paid")

    return render(
        request,
        "pages/checkout/success.html",
        {
            "page_title": "결제 완료",
            "order_id": order_id,
            "payment_key": payment_key,
            "amount": amount,
        },
    )


def payment_fail(request: HttpRequest) -> HttpResponse:
    """
    결제 실패 페이지
    """
    error_code = request.GET.get("code", "UNKNOWN")
    error_message = request.GET.get("message", "결제에 실패했습니다")
    order_id = request.GET.get("orderId", "")

    return render(
        request,
        "pages/checkout/fail.html",
        {
            "page_title": "결제 실패",
            "error_code": error_code,
            "error_message": error_message,
            "order_id": order_id,
        },
    )

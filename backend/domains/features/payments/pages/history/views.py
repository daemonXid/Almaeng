"""
📋 Order History Page Views
"""

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render

from ...models import Order


@login_required
def order_history(request: HttpRequest) -> HttpResponse:
    """주문 내역 페이지"""
    orders = Order.objects.filter(user_id=request.user.id).prefetch_related("items").order_by("-created_at")

    return render(
        request,
        "payments/pages/history/history.html",
        {
            "page_title": "주문 내역 | ALMAENG",
            "orders": orders,
        },
    )


@login_required
def order_detail(request: HttpRequest, order_id: str) -> HttpResponse:
    """주문 상세 페이지"""
    order = get_object_or_404(Order, order_id=order_id, user_id=request.user.id)

    return render(
        request,
        "payments/pages/history/detail.html",
        {
            "page_title": f"주문 상세 | ALMAENG",
            "order": order,
        },
    )

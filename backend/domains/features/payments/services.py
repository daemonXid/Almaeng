"""
💳 Payments Services

주문 생성 및 결제 처리 로직.
"""

from decimal import Decimal

from django.db import transaction

from .models import Order, OrderItem, Payment


@transaction.atomic
def create_order_from_cart(
    user_id: int,
    cart_items: list[dict],
    shipping_info: dict,
) -> Order:
    """장바구니에서 주문 생성"""
    total = sum(Decimal(item["unit_price"]) * item["quantity"] for item in cart_items)

    order = Order.objects.create(
        user_id=user_id,
        total_amount=total,
        shipping_name=shipping_info.get("name", ""),
        shipping_phone=shipping_info.get("phone", ""),
        shipping_address=shipping_info.get("address", ""),
        shipping_memo=shipping_info.get("memo", ""),
    )

    for item in cart_items:
        OrderItem.objects.create(
            order=order,
            supplement_id=item["supplement_id"],
            platform=item.get("platform", ""),
            product_name=item.get("product_name", f"영양제 #{item['supplement_id']}"),
            quantity=item["quantity"],
            unit_price=item["unit_price"],
        )

    # 결제 레코드 생성 (대기 상태)
    Payment.objects.create(
        order=order,
        amount=total,
        method="card",  # 기본값
    )

    return order


def get_order_by_id(order_id: str) -> Order | None:
    """주문 조회"""
    try:
        return Order.objects.get(order_id=order_id)
    except Order.DoesNotExist:
        return None


def update_payment_status(
    order: Order,
    payment_key: str,
    status: str,
    method: str = "",
    approved_at: str | None = None,
) -> Payment:
    """결제 상태 업데이트"""
    payment = order.payment
    payment.payment_key = payment_key
    payment.status = status
    if method:
        payment.method = method
    if approved_at:
        from django.utils.dateparse import parse_datetime

        payment.approved_at = parse_datetime(approved_at)
    payment.save()

    # 주문 상태도 함께 업데이트
    if status == "done":
        order.status = "paid"
        order.save()
        # 주문 확인 알림 발송
        _send_order_confirmation(order)

    return payment


def _send_order_confirmation(order: Order) -> None:
    """주문 확인 알림 발송 (내부 함수)"""
    from django.contrib.auth import get_user_model

    from domains.base.notifications.interface import notify_user

    User = get_user_model()

    try:
        user = User.objects.get(id=order.user_id)
    except User.DoesNotExist:
        return

    # In-app 알림
    notify_user(
        user=user,
        title="주문이 완료되었습니다!",
        message=f"주문번호: {str(order.order_id)[:8]}... | 총 금액: {order.total_amount:,.0f}원",
        notification_type="success",
        link=f"/payments/orders/{order.order_id}/",
    )

    # 이메일 알림 (선택적)
    try:
        from domains.base.notifications.email.interface import send_email

        # 주문 상품 목록 가져오기
        items = list(order.items.values("product_name", "quantity", "unit_price"))

        send_email(
            to=user.email,
            subject=f"[ALMAENG] 주문 확인 (#{str(order.order_id)[:8]})",
            template="order_confirmation",
            context={
                "user_name": user.get_full_name() or user.username,
                "order_id": str(order.order_id),
                "total_amount": f"{order.total_amount:,.0f}",
                "shipping_name": order.shipping_name,
                "shipping_address": order.shipping_address,
                "items": items,
            },
        )
    except Exception:
        # 이메일 실패해도 주문 처리는 성공
        pass


def mark_order_cancelled(order: Order, reason: str = "") -> Order:
    """주문 취소 처리"""
    order.status = "cancelled"
    order.save()

    if hasattr(order, "payment"):
        order.payment.status = "cancelled"
        order.payment.save()

    return order

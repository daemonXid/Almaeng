"""
💳 Billing State Interface

Public API for billing (PRD v2).
"""

from django.utils import timezone

from .models import Order, Payment


def create_order(
    user_id: int | None,
    product_id: str,
    product_name: str,
    platform: str,
    product_url: str,
    amount: int,
) -> Order:
    """
    주문 생성

    Args:
        user_id: 사용자 ID (로그인 시)
        product_id: 상품 ID
        product_name: 상품명
        platform: 구매 플랫폼
        product_url: 상품 URL
        amount: 결제 금액

    Returns:
        Order: 생성된 주문
    """
    order = Order.objects.create(
        user_id=user_id,
        product_id=product_id,
        product_name=product_name,
        platform=platform,
        product_url=product_url,
        total_amount=amount,
    )

    # Payment 레코드 생성
    Payment.objects.create(
        order=order,
        amount=amount,
        status="PENDING",
    )

    return order


def get_order_by_uuid(order_id: str) -> Order | None:
    """
    주문 UUID로 주문 조회

    Args:
        order_id: 주문 UUID 문자열

    Returns:
        Order | None: 주문 또는 None
    """
    try:
        return Order.objects.get(order_id=order_id)
    except Order.DoesNotExist:
        return None


def update_order_payment(
    order: Order,
    payment_key: str,
    status: str,
) -> Order:
    """
    주문 결제 정보 업데이트

    Args:
        order: 주문 객체
        payment_key: 토스 결제 키
        status: 결제 상태 ("paid", "cancelled", etc.)

    Returns:
        Order: 업데이트된 주문
    """
    order.status = status
    order.save(update_fields=["status", "updated_at"])

    # Payment 업데이트
    try:
        payment = order.payment
        payment.payment_key = payment_key
        payment.status = "SUCCESS" if status == "paid" else "FAIL"
        payment.approved_at = timezone.now() if status == "paid" else None
        payment.save(update_fields=["payment_key", "status", "approved_at"])
    except Payment.DoesNotExist:
        pass

    return order


def get_user_orders(user_id: int) -> list[Order]:
    """
    사용자 주문 목록 조회

    Args:
        user_id: 사용자 ID

    Returns:
        list[Order]: 주문 목록
    """
    return list(Order.objects.filter(user_id=user_id).order_by("-created_at"))


def update_payment_by_key(
    payment_key: str,
    status: str,
    error_message: str = "",
) -> bool:
    """
    결제 키로 결제 상태 업데이트 (Webhook용)

    Args:
        payment_key: 토스 결제 키
        status: 결제 상태 ("SUCCESS", "FAIL", "CANCELED")
        error_message: 에러 메시지 (실패 시)

    Returns:
        bool: 업데이트 성공 여부
    """
    try:
        payment = Payment.objects.get(payment_key=payment_key)
        payment.status = status
        if error_message:
            payment.error_message = error_message
        if status == "SUCCESS":
            payment.approved_at = timezone.now()
        payment.save()

        # Order 상태도 업데이트
        order = payment.order
        if status == "SUCCESS":
            order.status = "paid"
        elif status == "CANCELED":
            order.status = "cancelled"
        order.save(update_fields=["status", "updated_at"])

        return True
    except Payment.DoesNotExist:
        return False

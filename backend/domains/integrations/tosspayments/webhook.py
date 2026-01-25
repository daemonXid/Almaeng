"""
💳 Toss Payments Webhook Handler

Webhook 수신 및 처리.
billing 도메인의 interface.py를 통해서만 통신 (DAEMON 원칙).
"""

from domains.billing.state.interface import (
    get_order_by_uuid,
    update_order_payment,
    update_payment_by_key,
)


async def handle_webhook(payload: dict) -> dict:
    """
    토스페이먼츠 Webhook 처리

    Args:
        payload: Webhook 페이로드

    Returns:
        dict: 처리 결과
    """
    event_type = payload.get("eventType")
    data = payload.get("data", {})

    if event_type == "PAYMENT_CONFIRMED":
        # 결제 승인 완료
        payment_key = data.get("paymentKey")
        order_id = data.get("orderId")

        if payment_key and order_id:
            order = get_order_by_uuid(order_id)
            if order:
                update_order_payment(order, payment_key, "paid")

    elif event_type == "PAYMENT_CANCELED":
        # 결제 취소
        payment_key = data.get("paymentKey")

        if payment_key:
            update_payment_by_key(payment_key, "CANCELED")

    elif event_type == "PAYMENT_FAILED":
        # 결제 실패
        payment_key = data.get("paymentKey")
        fail_reason = data.get("failReason", "")

        if payment_key:
            update_payment_by_key(payment_key, "FAIL", error_message=fail_reason)

    return {"status": "ok"}

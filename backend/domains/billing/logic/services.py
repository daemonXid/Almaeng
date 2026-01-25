"""
💳 Billing Services

결제 처리 로직.
"""

from domains.integrations.tosspayments.interface import cancel_payment, confirm_payment

from ..state.interface import get_order_by_id
from ..state.models import Payment


async def process_payment(payment_key: str, order_id: str, amount: int) -> dict:
    """
    결제 처리

    Args:
        payment_key: 토스페이먼츠 결제 키
        order_id: 주문 UUID 문자열
        amount: 결제 금액

    Returns:
        dict: 처리 결과
    """
    order = get_order_by_id(order_id)
    if not order:
        return {"success": False, "message": "주문을 찾을 수 없습니다"}

    # 금액 검증
    if int(order.total_amount) != amount:
        return {"success": False, "message": "결제 금액이 일치하지 않습니다"}

    # 결제 승인
    result = await confirm_payment(payment_key, order_id, amount)

    if result.success:
        # Payment 생성 또는 업데이트
        payment, created = Payment.objects.get_or_create(  # type: ignore
            order=order,
            defaults={
                "payment_key": result.payment_key,
                "method": result.method,
                "status": "SUCCESS",
                "amount": amount,
            },
        )

        if not created:
            payment.payment_key = result.payment_key
            payment.method = result.method
            payment.status = "SUCCESS"
            payment.save()

        # Order 상태 업데이트
        order.status = "paid"
        order.save()

        return {
            "success": True,
            "order_id": str(order.order_id),
            "payment_key": result.payment_key,
            "message": "결제가 완료되었습니다",
        }
    else:
        return {
            "success": False,
            "error_code": result.error_code,
            "message": result.error_message or "결제 승인 실패",
        }


async def cancel_order_payment(order_id: str, cancel_reason: str) -> dict:
    """
    주문 결제 취소

    Args:
        order_id: 주문 UUID 문자열
        cancel_reason: 취소 사유

    Returns:
        dict: 취소 결과
    """
    order = get_order_by_id(order_id)
    if not order:
        return {"success": False, "message": "주문을 찾을 수 없습니다"}

    if not hasattr(order, "payment") or not order.payment.payment_key:
        return {"success": False, "message": "결제 정보가 없습니다"}

    # 결제 취소
    result = await cancel_payment(order.payment.payment_key, cancel_reason)

    if result.success:
        order.payment.status = "CANCELED"
        order.payment.save()

        order.status = "cancelled"
        order.save()

        return {
            "success": True,
            "message": "결제가 취소되었습니다",
        }
    else:
        return {
            "success": False,
            "error_code": result.error_code,
            "message": result.error_message or "결제 취소 실패",
        }

"""
💳 Payments API

Django Ninja API 엔드포인트.
결제 승인, 취소, Webhook 처리.
"""

import hashlib
import hmac
import logging

from django.conf import settings
from django.http import HttpRequest
from ninja import Router

from .integrations.toss import toss_client
from .schemas import (
    PaymentCancelRequest,
    PaymentConfirmRequest,
    PaymentConfirmResponse,
    TossWebhookPayload,
    WebhookTransactionData,
)
from .services import get_order_by_id, mark_order_cancelled, update_payment_status

logger = logging.getLogger(__name__)

router = Router(tags=["payments"])


@router.post("/confirm/", response=PaymentConfirmResponse)
async def confirm_payment(request: HttpRequest, payload: PaymentConfirmRequest):
    """
    결제 승인 API

    프론트엔드에서 토스 결제 완료 후 서버에서 최종 승인.
    """
    order = get_order_by_id(payload.order_id)
    if not order:
        return PaymentConfirmResponse(
            success=False,
            order_id=payload.order_id,
            status="error",
            message="주문을 찾을 수 없습니다",
        )

    # 금액 검증
    if int(order.total_amount) != payload.amount:
        return PaymentConfirmResponse(
            success=False,
            order_id=payload.order_id,
            status="error",
            message="결제 금액이 일치하지 않습니다",
        )

    # Toss API 호출
    result = await toss_client.confirm_payment(
        payment_key=payload.payment_key,
        order_id=payload.order_id,
        amount=payload.amount,
    )

    if result.success:
        update_payment_status(
            order,
            payment_key=result.payment_key,
            status="done",
            method=result.method,
            approved_at=result.approved_at,
        )
        return PaymentConfirmResponse(
            success=True,
            order_id=payload.order_id,
            status="paid",
            message="결제가 완료되었습니다",
        )
    else:
        return PaymentConfirmResponse(
            success=False,
            order_id=payload.order_id,
            status="failed",
            message=result.error_message or "결제 승인 실패",
        )


@router.post("/cancel/", response=PaymentConfirmResponse)
async def cancel_payment(request: HttpRequest, payload: PaymentCancelRequest):
    """
    결제 취소 API
    """
    # Toss API 호출
    result = await toss_client.cancel_payment(
        payment_key=payload.payment_key,
        cancel_reason=payload.cancel_reason,
    )

    if result.success:
        # payment_key로 주문 찾기
        from .models import Payment

        try:
            payment = Payment.objects.get(payment_key=payload.payment_key)
            mark_order_cancelled(payment.order, reason=payload.cancel_reason)
        except Payment.DoesNotExist:
            logger.warning(f"Payment not found for key: {payload.payment_key}")

        return PaymentConfirmResponse(
            success=True,
            order_id=result.order_id,
            status="cancelled",
            message="결제가 취소되었습니다",
        )
    else:
        return PaymentConfirmResponse(
            success=False,
            order_id="",
            status="error",
            message=result.error_message or "결제 취소 실패",
        )


@router.post("/webhook/")
async def toss_webhook(request: HttpRequest, payload: TossWebhookPayload):
    """
    토스 Webhook 수신

    https://docs.tosspayments.com/guides/webhook

    > [!IMPORTANT]
    > Production에서는 IP 화이트리스트 또는 Signature 검증 필요.
    """
    # Webhook Secret 검증
    webhook_secret = getattr(settings, "TOSS_WEBHOOK_SECRET", "")
    if webhook_secret and payload.secret != webhook_secret:
        logger.warning("Invalid webhook secret")
        return {"status": "error", "message": "Invalid secret"}

    # 트랜잭션 데이터 파싱
    try:
        tx_data = WebhookTransactionData(**payload.data)
    except Exception as e:
        logger.error(f"Failed to parse webhook data: {e}")
        return {"status": "error", "message": "Invalid payload"}

    # 주문 조회 및 상태 업데이트
    order = get_order_by_id(tx_data.order_id)
    if not order:
        logger.warning(f"Order not found: {tx_data.order_id}")
        return {"status": "error", "message": "Order not found"}

    # 상태별 처리
    if tx_data.status == "DONE":
        update_payment_status(
            order,
            payment_key=tx_data.payment_key,
            status="done",
            method=tx_data.method,
            approved_at=tx_data.approved_at,
        )
        logger.info(f"Payment completed via webhook: {tx_data.order_id}")

    elif tx_data.status in ("CANCELED", "PARTIAL_CANCELED"):
        mark_order_cancelled(order)
        logger.info(f"Payment cancelled via webhook: {tx_data.order_id}")

    elif tx_data.status == "ABORTED":
        order.payment.status = "failed"
        order.payment.save()
        logger.info(f"Payment aborted via webhook: {tx_data.order_id}")

    return {"status": "ok"}

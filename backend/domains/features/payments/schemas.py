"""
💳 Payments Schemas

Pydantic 스키마 (Django Ninja API용).
"""

from pydantic import BaseModel, Field


class PaymentConfirmRequest(BaseModel):
    """결제 승인 요청"""

    payment_key: str = Field(..., alias="paymentKey")
    order_id: str = Field(..., alias="orderId")
    amount: int

    class Config:
        populate_by_name = True


class PaymentConfirmResponse(BaseModel):
    """결제 승인 응답"""

    success: bool
    order_id: str
    status: str
    message: str = ""


class PaymentCancelRequest(BaseModel):
    """결제 취소 요청"""

    payment_key: str = Field(..., alias="paymentKey")
    cancel_reason: str = Field(..., alias="cancelReason")

    class Config:
        populate_by_name = True


class TossWebhookPayload(BaseModel):
    """토스 Webhook 페이로드

    https://docs.tosspayments.com/guides/webhook
    """

    created_at: str = Field(..., alias="createdAt")
    secret: str
    # Transaction data nested
    data: dict


class WebhookTransactionData(BaseModel):
    """Webhook 트랜잭션 데이터"""

    payment_key: str = Field(..., alias="paymentKey")
    order_id: str = Field(..., alias="orderId")
    status: str
    method: str = ""
    approved_at: str | None = Field(None, alias="approvedAt")

    class Config:
        populate_by_name = True

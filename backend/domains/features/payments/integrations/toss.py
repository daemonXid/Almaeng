"""
💳 Toss Payments Integration

Toss Payments API 클라이언트.
https://docs.tosspayments.com/
"""

import base64

import httpx
from django.conf import settings
from pydantic import BaseModel, Field


class TossPaymentResult(BaseModel):
    """토스 결제 결과 (Pydantic + JSON-LD)"""

    # JSON-LD for inter-domain compatibility
    context: str = Field(default="https://schema.org", alias="@context", exclude=True)
    type: str = Field(default="PayAction", alias="@type", exclude=True)

    success: bool
    payment_key: str = ""
    order_id: str = ""
    status: str = ""
    method: str = ""
    approved_at: str | None = None
    error_code: str = ""
    error_message: str = ""

    class Config:
        populate_by_name = True


class TossPaymentsClient:
    """Toss Payments API Client"""

    BASE_URL = "https://api.tosspayments.com/v1"

    def __init__(self):
        self.secret_key = getattr(settings, "TOSS_SECRET_KEY", "")
        self.client_key = getattr(settings, "TOSS_CLIENT_KEY", "")

    def _get_auth_header(self) -> dict:
        """Basic Auth 헤더 생성"""
        credentials = base64.b64encode(f"{self.secret_key}:".encode()).decode()
        return {
            "Authorization": f"Basic {credentials}",
            "Content-Type": "application/json",
        }

    async def confirm_payment(self, payment_key: str, order_id: str, amount: int) -> TossPaymentResult:
        """
        결제 승인 요청

        프론트엔드에서 결제 완료 후 서버에서 최종 승인.
        """
        url = f"{self.BASE_URL}/payments/confirm"
        payload = {
            "paymentKey": payment_key,
            "orderId": order_id,
            "amount": amount,
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, json=payload, headers=self._get_auth_header())
                data = response.json()

                if response.status_code == 200:
                    return TossPaymentResult(
                        success=True,
                        payment_key=data.get("paymentKey", ""),
                        order_id=data.get("orderId", ""),
                        status=data.get("status", ""),
                        method=data.get("method", ""),
                        approved_at=data.get("approvedAt"),
                    )
                else:
                    return TossPaymentResult(
                        success=False,
                        error_code=data.get("code", "UNKNOWN"),
                        error_message=data.get("message", "결제 승인 실패"),
                    )
            except Exception as e:
                return TossPaymentResult(
                    success=False,
                    error_code="NETWORK_ERROR",
                    error_message=str(e),
                )

    async def cancel_payment(self, payment_key: str, cancel_reason: str) -> TossPaymentResult:
        """결제 취소"""
        url = f"{self.BASE_URL}/payments/{payment_key}/cancel"
        payload = {"cancelReason": cancel_reason}

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, json=payload, headers=self._get_auth_header())
                data = response.json()

                if response.status_code == 200:
                    return TossPaymentResult(
                        success=True,
                        payment_key=data.get("paymentKey", ""),
                        status="cancelled",
                    )
                else:
                    return TossPaymentResult(
                        success=False,
                        error_code=data.get("code", "UNKNOWN"),
                        error_message=data.get("message", "결제 취소 실패"),
                    )
            except Exception as e:
                return TossPaymentResult(
                    success=False,
                    error_code="NETWORK_ERROR",
                    error_message=str(e),
                )


# Singleton
toss_client = TossPaymentsClient()

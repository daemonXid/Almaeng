"""
💳 Billing Schemas

Pydantic 스키마 정의 (PRD v2).
"""

from pydantic import BaseModel, ConfigDict


class PaymentRequest(BaseModel):
    """결제 요청"""

    model_config = ConfigDict(frozen=True)

    product_id: str
    product_name: str
    amount: int
    platform: str  # "naver" | "11st"
    product_url: str


class PaymentConfirm(BaseModel):
    """결제 승인 요청"""

    model_config = ConfigDict(frozen=True)

    payment_key: str
    order_id: str
    amount: int


class PaymentResult(BaseModel):
    """결제 결과"""

    model_config = ConfigDict(frozen=True)

    status: str  # "SUCCESS" | "FAIL"
    order_id: str
    payment_key: str | None = None
    message: str

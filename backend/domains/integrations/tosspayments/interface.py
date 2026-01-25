"""
💳 Toss Payments Interface

Public API for Toss Payments integration.
"""

from .client import toss_client, TossPaymentResult


async def confirm_payment(payment_key: str, order_id: str, amount: int) -> TossPaymentResult:
    """
    결제 승인
    
    Args:
        payment_key: 토스페이먼츠 결제 키
        order_id: 주문 ID
        amount: 결제 금액
        
    Returns:
        TossPaymentResult: 결제 결과
    """
    return await toss_client.confirm_payment(payment_key, order_id, amount)


async def cancel_payment(payment_key: str, cancel_reason: str) -> TossPaymentResult:
    """
    결제 취소
    
    Args:
        payment_key: 토스페이먼츠 결제 키
        cancel_reason: 취소 사유
        
    Returns:
        TossPaymentResult: 취소 결과
    """
    return await toss_client.cancel_payment(payment_key, cancel_reason)

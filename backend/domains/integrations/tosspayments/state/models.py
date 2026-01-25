"""
💳 Toss Payments State Models

토스페이먼츠 관련 상태 모델 (선택사항).
"""

from django.db import models


class TossPaymentLog(models.Model):
    """토스페이먼츠 API 호출 로그"""

    payment_key = models.CharField(max_length=200, db_index=True)
    event_type = models.CharField(max_length=50)  # "PAYMENT_CONFIRMED", "PAYMENT_CANCELED", etc.
    payload = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "토스페이먼츠 로그"
        verbose_name_plural = "토스페이먼츠 로그 목록"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.event_type} - {self.payment_key}"

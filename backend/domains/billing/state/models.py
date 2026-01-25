"""
💳 Billing State Models

주문 및 결제 모델 (PRD v2).
"""

import uuid

from django.db import models


class Order(models.Model):
    """주문 (PRD v2)"""

    STATUS_CHOICES = [
        ("pending", "결제 대기"),
        ("paid", "결제 완료"),
        ("shipping", "배송중"),
        ("delivered", "배송 완료"),
        ("cancelled", "취소됨"),
        ("refunded", "환불됨"),
    ]

    order_id = models.UUIDField(default=uuid.uuid4, unique=True, db_index=True)
    user_id = models.IntegerField(db_index=True, null=True, blank=True, verbose_name="사용자 ID")

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    total_amount = models.DecimalField(max_digits=10, decimal_places=0, verbose_name="총 금액")

    # Product info (PRD v2)
    product_id = models.CharField(max_length=100, verbose_name="상품 ID")
    product_name = models.CharField(max_length=200, verbose_name="상품명")
    platform = models.CharField(max_length=20, verbose_name="구매 플랫폼")  # "naver" | "11st"
    product_url = models.URLField(verbose_name="상품 URL")

    # Shipping (선택사항)
    shipping_name = models.CharField(max_length=100, blank=True, verbose_name="받는 분")
    shipping_phone = models.CharField(max_length=20, blank=True, verbose_name="연락처")
    shipping_address = models.TextField(blank=True, verbose_name="배송 주소")
    shipping_memo = models.CharField(max_length=200, blank=True, verbose_name="배송 메모")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "주문"
        verbose_name_plural = "주문 목록"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Order {self.order_id} - {self.get_status_display()}"


class Payment(models.Model):
    """결제 (PRD v2)"""

    METHOD_CHOICES = [
        ("card", "카드"),
        ("transfer", "계좌이체"),
        ("virtual", "가상계좌"),
        ("phone", "휴대폰"),
        ("toss", "토스페이"),
    ]

    STATUS_CHOICES = [
        ("PENDING", "대기"),
        ("SUCCESS", "성공"),
        ("FAIL", "실패"),
        ("CANCELED", "취소"),
    ]

    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name="payment")

    # Toss Payments
    payment_key = models.CharField(max_length=200, blank=True, db_index=True)
    method = models.CharField(max_length=20, choices=METHOD_CHOICES, default="toss")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")

    amount = models.DecimalField(max_digits=10, decimal_places=0, verbose_name="결제 금액")
    approved_at = models.DateTimeField(null=True, blank=True, verbose_name="승인 시각")

    # Error handling
    error_code = models.CharField(max_length=50, blank=True)
    error_message = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "결제"
        verbose_name_plural = "결제 목록"

    def __str__(self) -> str:
        return f"Payment {self.payment_key or 'N/A'} - {self.get_status_display()}"

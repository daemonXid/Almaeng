"""
💰 Prices Models

가격 히스토리와 알림을 저장하는 모델.
도메인 간 FK 사용 금지 - supplement_id, user_id를 IntegerField로 저장.
"""

from django.db import models


class PriceHistory(models.Model):
    """가격 기록"""

    PLATFORM_CHOICES = [
        ("iherb", "iHerb"),
        ("coupang", "쿠팡"),
        ("naver", "네이버"),
        ("amazon", "Amazon"),
        ("costco", "코스트코"),
        ("other", "기타"),
    ]

    # 도메인 간 FK 대신 ID 사용 (DDD 원칙)
    supplement_id = models.IntegerField(db_index=True, verbose_name="영양제 ID")

    platform = models.CharField(max_length=50, choices=PLATFORM_CHOICES, verbose_name="판매 플랫폼")
    price = models.DecimalField(max_digits=10, decimal_places=0, verbose_name="가격(원)")
    original_price = models.DecimalField(max_digits=10, decimal_places=0, null=True, blank=True, verbose_name="정가")
    url = models.URLField(blank=True, verbose_name="상품 URL")
    is_in_stock = models.BooleanField(default=True, verbose_name="재고 여부")

    recorded_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = "가격 기록"
        verbose_name_plural = "가격 기록 목록"
        ordering = ["-recorded_at"]
        indexes = [
            models.Index(fields=["supplement_id", "platform", "-recorded_at"]),
        ]

    def __str__(self) -> str:
        return f"[{self.platform}] {self.supplement_id} - ₩{self.price:,.0f}"

    @property
    def discount_percent(self) -> float | None:
        """할인율 계산"""
        if self.original_price and self.original_price > 0:
            return round((1 - float(self.price) / float(self.original_price)) * 100, 1)
        return None


class PriceAlert(models.Model):
    """가격 알림 설정"""

    user_id = models.IntegerField(db_index=True, verbose_name="사용자 ID")
    supplement_id = models.IntegerField(db_index=True, verbose_name="영양제 ID")

    target_price = models.DecimalField(max_digits=10, decimal_places=0, verbose_name="목표 가격(원)")
    is_active = models.BooleanField(default=True, verbose_name="활성화")

    created_at = models.DateTimeField(auto_now_add=True)
    triggered_at = models.DateTimeField(null=True, blank=True, verbose_name="알림 발송 시각")

    class Meta:
        verbose_name = "가격 알림"
        verbose_name_plural = "가격 알림 목록"
        unique_together = ["user_id", "supplement_id"]

    def __str__(self) -> str:
        status = "🔔" if self.is_active else "🔕"
        return f"{status} User {self.user_id} - ₩{self.target_price:,.0f} 이하 알림"

"""
❤️ Wishlist Models

찜 목록 모델.
"""

from django.db import models


class WishlistItem(models.Model):
    """찜한 상품"""

    user_id = models.IntegerField(db_index=True, verbose_name="사용자 ID")
    supplement_id = models.IntegerField(db_index=True, verbose_name="영양제 ID")

    # 최저가 알림 옵션
    notify_price_drop = models.BooleanField(default=False, verbose_name="가격 하락 알림")
    target_price = models.DecimalField(max_digits=10, decimal_places=0, null=True, blank=True, verbose_name="목표 가격")

    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "찜"
        verbose_name_plural = "찜 목록"
        unique_together = ["user_id", "supplement_id"]
        ordering = ["-added_at"]

    def __str__(self) -> str:
        return f"User {self.user_id} ❤️ Supplement {self.supplement_id}"

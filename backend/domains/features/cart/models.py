"""
🛒 Cart Models

장바구니 모델. 세션 기반 또는 사용자 기반 장바구니 지원.
"""

from django.db import models


class Cart(models.Model):
    """장바구니"""

    user_id = models.IntegerField(null=True, blank=True, db_index=True, verbose_name="사용자 ID")
    session_key = models.CharField(max_length=40, null=True, blank=True, db_index=True, verbose_name="세션 키")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "장바구니"
        verbose_name_plural = "장바구니 목록"

    def __str__(self) -> str:
        if self.user_id:
            return f"Cart (User {self.user_id})"
        return f"Cart (Session {self.session_key[:8]}...)"

    @property
    def total_items(self) -> int:
        return sum(item.quantity for item in self.items.all())

    @property
    def total_price(self):
        return sum(item.subtotal for item in self.items.all())


class CartItem(models.Model):
    """장바구니 아이템"""

    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    supplement_id = models.IntegerField(db_index=True, verbose_name="영양제 ID")
    platform = models.CharField(max_length=50, verbose_name="구매 플랫폼")  # iherb, coupang 등

    quantity = models.PositiveIntegerField(default=1, verbose_name="수량")
    unit_price = models.DecimalField(max_digits=10, decimal_places=0, verbose_name="단가")

    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "장바구니 아이템"
        verbose_name_plural = "장바구니 아이템 목록"
        unique_together = ["cart", "supplement_id", "platform"]

    def __str__(self) -> str:
        return f"CartItem: {self.supplement_id} x {self.quantity}"

    @property
    def subtotal(self):
        return self.unit_price * self.quantity

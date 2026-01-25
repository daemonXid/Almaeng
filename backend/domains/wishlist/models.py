from django.db import models


class WishlistItem(models.Model):
    """
    찜한 상품 정보를 저장하는 모델.
    도메인 간 결합도를 낮추기 위해 User에 대한 ForeignKey 대신 user_id를 사용합니다.
    """

    user_id = models.IntegerField(db_index=True)
    product_id = models.CharField(max_length=255, db_index=True)
    platform = models.CharField(max_length=50)  # naver, 11st 등
    name = models.CharField(max_length=255)
    price = models.IntegerField()
    image_url = models.TextField(blank=True, null=True)
    product_url = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "wishlist_items"
        verbose_name = "Wishlist Item"
        unique_together = ("user_id", "product_id", "platform")

    def __str__(self):
        return f"[{self.platform}] {self.name}"


class PriceAlert(models.Model):
    """
    가격 알림 모델.
    찜한 상품의 가격이 하락했을 때 알림을 표시합니다.
    """

    user_id = models.IntegerField(db_index=True)
    wishlist_item = models.ForeignKey(WishlistItem, on_delete=models.CASCADE, related_name="price_alerts")
    original_price = models.IntegerField(verbose_name="Original Price")
    current_price = models.IntegerField(verbose_name="Current Price")
    price_drop_percent = models.FloatField(verbose_name="Price Drop Percent")
    is_read = models.BooleanField(default=False, verbose_name="Is Read")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")

    class Meta:
        db_table = "price_alerts"
        verbose_name = "Price Alert"
        verbose_name_plural = "Price Alerts"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Price Alert: {self.wishlist_item.name} ({self.price_drop_percent:.1f}% drop)"

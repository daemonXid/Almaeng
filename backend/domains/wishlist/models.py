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

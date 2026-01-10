"""
💊 Supplements Models

영양제 제품과 성분 정보를 저장하는 모델.
"""

from django.db import models


class Supplement(models.Model):
    """영양제 제품 정보"""

    name = models.CharField(max_length=200, verbose_name="제품명")
    brand = models.CharField(max_length=100, verbose_name="브랜드")
    image_url = models.URLField(blank=True, verbose_name="이미지 URL")
    serving_size = models.CharField(max_length=50, verbose_name="1회 섭취량")  # "1정", "2캡슐"
    servings_per_container = models.PositiveIntegerField(default=1, verbose_name="총 섭취횟수")

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "영양제"
        verbose_name_plural = "영양제 목록"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.brand} - {self.name}"


class Ingredient(models.Model):
    """영양제 성분 정보"""

    UNIT_CHOICES = [
        ("mg", "밀리그램"),
        ("mcg", "마이크로그램"),
        ("g", "그램"),
        ("IU", "국제단위"),
        ("CFU", "CFU"),  # 유산균
        ("ml", "밀리리터"),
    ]

    supplement = models.ForeignKey(
        Supplement,
        on_delete=models.CASCADE,
        related_name="ingredients",
        verbose_name="영양제",
    )
    name = models.CharField(max_length=100, verbose_name="성분명")  # "비타민 D3"
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="함량")
    unit = models.CharField(max_length=20, choices=UNIT_CHOICES, verbose_name="단위")
    daily_value_percent = models.DecimalField(
        max_digits=6, decimal_places=2, null=True, blank=True, verbose_name="일일 권장량 %"
    )

    class Meta:
        verbose_name = "성분"
        verbose_name_plural = "성분 목록"
        ordering = ["name"]

    def __str__(self) -> str:
        return f"{self.name} {self.amount}{self.unit}"

"""
🔍 Search State Models

Search history model & Coupang manual products.
"""

from django.db import models


class SearchHistory(models.Model):
    """Search history"""

    user_id = models.IntegerField(db_index=True, null=True, blank=True, verbose_name="User ID")
    query = models.TextField(verbose_name="Original Query")
    keywords = models.JSONField(default=list, verbose_name="Extracted Keywords")
    category = models.CharField(max_length=100, blank=True, verbose_name="Category")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")

    class Meta:
        verbose_name = "Search History"
        verbose_name_plural = "Search History List"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.query} ({self.created_at})"


class CoupangManualProduct(models.Model):
    """
    쿠팡 수동 등록 상품 (15만원 달성 전까지 사용)

    쿠팡 파트너스 API는 15만원 수익 달성 후 사용 가능하므로,
    그 전까지는 수동으로 상품 정보와 파트너스 링크를 등록하여 사용합니다.
    """

    product_id = models.CharField(
        max_length=100,
        unique=True,
        db_index=True,
        verbose_name="상품 ID",
        help_text="쿠팡 상품 고유 ID",
    )
    name = models.CharField(
        max_length=500,
        verbose_name="상품명",
    )
    price = models.IntegerField(
        verbose_name="가격",
        help_text="원 단위",
    )
    image_url = models.URLField(
        max_length=1000,
        verbose_name="이미지 URL",
    )
    affiliate_url = models.URLField(
        max_length=1000,
        verbose_name="파트너스 링크",
        help_text="수동 생성한 쿠팡 파트너스 링크",
    )
    category = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="카테고리",
        help_text="예: 건강식품, 운동용품, 전자제품 등",
    )
    keywords = models.JSONField(
        default=list,
        verbose_name="검색 키워드",
        help_text="검색에 사용될 키워드 리스트",
    )
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name="활성화",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="등록일",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="수정일",
    )

    class Meta:
        verbose_name = "쿠팡 수동 상품"
        verbose_name_plural = "쿠팡 수동 상품 목록"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["is_active", "-created_at"]),
            models.Index(fields=["category", "is_active"]),
        ]

    def __str__(self) -> str:
        return f"{self.name} ({self.price:,}원)"


class ProductCache(models.Model):
    """
    API 검색 결과 캐시 (네이버, 11번가)
    
    ✅ 전략:
    - API 호출 결과를 DB에 저장
    - 24시간 동안 재사용 (가격은 하루에 한 번만 업데이트)
    - 중복 API 호출 방지 → 속도 향상, 비용 절감
    
    ✅ DAEMON Pattern:
    - 도메인 내부 캐시 (외부에서 직접 접근 불가)
    - interface.py를 통해서만 사용
    """
    
    platform = models.CharField(
        max_length=20,
        db_index=True,
        verbose_name="플랫폼",
        help_text="naver, 11st",
    )
    product_id = models.CharField(
        max_length=200,
        db_index=True,
        verbose_name="상품 ID",
    )
    product_name = models.CharField(
        max_length=500,
        verbose_name="상품명",
    )
    price = models.IntegerField(verbose_name="가격")
    original_price = models.IntegerField(null=True, blank=True, verbose_name="원가")
    discount_percent = models.IntegerField(null=True, blank=True, verbose_name="할인율")
    image_url = models.URLField(max_length=1000, verbose_name="이미지 URL")
    product_url = models.URLField(max_length=1000, verbose_name="상품 URL")
    mall_name = models.CharField(max_length=100, blank=True, verbose_name="판매처")
    rating = models.FloatField(null=True, blank=True, verbose_name="평점")
    review_count = models.IntegerField(default=0, verbose_name="리뷰 수")
    
    # 캐시 메타데이터
    search_keyword = models.CharField(
        max_length=200,
        db_index=True,
        verbose_name="검색 키워드",
        help_text="이 상품을 찾은 검색어",
    )
    cached_at = models.DateTimeField(
        auto_now=True,
        db_index=True,
        verbose_name="캐시 시간",
    )
    
    class Meta:
        verbose_name = "상품 캐시"
        verbose_name_plural = "상품 캐시 목록"
        ordering = ["-cached_at"]
        unique_together = ("platform", "product_id")
        indexes = [
            models.Index(fields=["search_keyword", "-cached_at"]),
            models.Index(fields=["platform", "-cached_at"]),
        ]
    
    def __str__(self) -> str:
        return f"[{self.platform}] {self.product_name[:30]}"

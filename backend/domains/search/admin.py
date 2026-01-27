"""
🔍 Search Domain Admin
"""

from django.contrib import admin

from .state.models import CoupangManualProduct, SearchHistory


@admin.register(SearchHistory)
class SearchHistoryAdmin(admin.ModelAdmin):
    """Search History Admin"""

    list_display = ["query", "category", "user_id", "created_at"]
    list_filter = ["category", "created_at"]
    search_fields = ["query", "keywords"]
    readonly_fields = ["created_at"]
    date_hierarchy = "created_at"


@admin.register(CoupangManualProduct)
class CoupangManualProductAdmin(admin.ModelAdmin):
    """
    쿠팡 수동 상품 Admin
    
    사용법:
    1. 쿠팡 파트너스에서 상품 링크 생성
    2. Admin에서 상품 정보 입력
    3. 저장하면 즉시 검색 결과에 반영
    """

    list_display = [
        "name",
        "price_display",
        "category",
        "is_active",
        "created_at",
    ]
    list_filter = [
        "is_active",
        "category",
        "created_at",
    ]
    search_fields = [
        "name",
        "product_id",
        "keywords",
    ]
    readonly_fields = [
        "created_at",
        "updated_at",
    ]
    fieldsets = (
        (
            "✅ 기본 정보",
            {
                "fields": (
                    "product_id",
                    "name",
                    "price",
                    "category",
                ),
                "description": "쿠팡 상품 ID와 이름, 가격을 입력하세요."
            },
        ),
        (
            "🔗 이미지 & 파트너스 링크",
            {
                "fields": (
                    "image_url",
                    "affiliate_url",
                ),
                "description": "쿠팡 파트너스에서 생성한 제휴 링크를 입력하세요."
            },
        ),
        (
            "🔍 검색 설정",
            {
                "fields": (
                    "keywords",
                    "is_active",
                ),
                "description": "검색에 사용될 키워드를 JSON 배열로 입력하세요. 예: [\"비타민D\", \"칼슘\"]"
            },
        ),
        (
            "📅 메타 정보",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                ),
                "classes": ("collapse",),
            },
        ),
    )
    date_hierarchy = "created_at"
    list_per_page = 50
    actions = ["activate_products", "deactivate_products"]

    def price_display(self, obj):
        """가격 표시"""
        return f"₩{obj.price:,}"
    price_display.short_description = "가격"

    def activate_products(self, request, queryset):
        """상품 활성화"""
        count = queryset.update(is_active=True)
        self.message_user(request, f"{count}개 상품을 활성화했습니다.")
    activate_products.short_description = "선택된 상품 활성화"

    def deactivate_products(self, request, queryset):
        """상품 비활성화"""
        count = queryset.update(is_active=False)
        self.message_user(request, f"{count}개 상품을 비활성화했습니다.")
    deactivate_products.short_description = "선택된 상품 비활성화"

    def get_queryset(self, request):
        """Optimize queryset"""
        qs = super().get_queryset(request)
        return qs.select_related()

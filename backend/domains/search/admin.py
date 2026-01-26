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
    """쿠팡 수동 상품 Admin"""

    list_display = [
        "name",
        "price",
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
            "기본 정보",
            {
                "fields": (
                    "product_id",
                    "name",
                    "price",
                    "category",
                )
            },
        ),
        (
            "이미지 & 링크",
            {
                "fields": (
                    "image_url",
                    "affiliate_url",
                )
            },
        ),
        (
            "검색 설정",
            {
                "fields": (
                    "keywords",
                    "is_active",
                )
            },
        ),
        (
            "메타 정보",
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

    def get_queryset(self, request):
        """Optimize queryset"""
        qs = super().get_queryset(request)
        return qs.select_related()

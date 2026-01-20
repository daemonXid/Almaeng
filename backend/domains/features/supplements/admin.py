"""
💊 Supplements Admin

Django Admin 등록 - 영양제 및 식약처 데이터 관리
"""

from django.contrib import admin

from .models import Ingredient, MFDSHealthFood, Supplement


@admin.register(Supplement)
class SupplementAdmin(admin.ModelAdmin):
    list_display = ["name", "brand", "serving_size", "created_at"]
    search_fields = ["name", "brand"]
    list_filter = ["brand"]
    ordering = ["-created_at"]


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ["name", "amount", "unit", "supplement"]
    search_fields = ["name"]
    list_filter = ["unit"]


@admin.register(MFDSHealthFood)
class MFDSHealthFoodAdmin(admin.ModelAdmin):
    """식약처 건강기능식품 관리"""

    list_display = [
        "product_name",
        "company_name",
        "functionality_short",
        "report_date",
        "synced_at",
    ]
    search_fields = ["product_name", "company_name", "raw_materials", "functionality"]
    list_filter = ["report_date", "product_form"]
    ordering = ["-synced_at"]
    readonly_fields = ["synced_at", "created_at"]

    # 목록에서 기능성 요약 표시
    @admin.display(description="기능성 (요약)")
    def functionality_short(self, obj):
        if obj.functionality:
            return obj.functionality[:50] + "..." if len(obj.functionality) > 50 else obj.functionality
        return "-"

    # 상세 페이지 필드 그룹
    fieldsets = (
        ("기본 정보", {
            "fields": ("license_number", "report_number", "product_name", "company_name", "report_date")
        }),
        ("제품 정보", {
            "fields": ("functionality", "intake_method", "appearance", "product_form", "shape")
        }),
        ("원재료 및 규격", {
            "fields": ("raw_materials", "standard", "expiry_period", "storage_method"),
            "classes": ("collapse",),
        }),
        ("주의사항", {
            "fields": ("cautions",),
            "classes": ("collapse",),
        }),
        ("메타 정보", {
            "fields": ("synced_at", "created_at"),
        }),
    )

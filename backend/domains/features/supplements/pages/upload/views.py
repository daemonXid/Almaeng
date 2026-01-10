"""
📷 Upload Page Views

Vision AI OCR 업로드 페이지 - Gemini Vision 연동.
"""

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST

from ...vision_service import get_vision_service


def upload(request: HttpRequest) -> HttpResponse:
    """라벨 업로드 페이지"""
    return render(
        request,
        "supplements/pages/upload/upload.html",
        {
            "page_title": "라벨 스캔 | ALMAENG",
        },
    )


@require_POST
def analyze_image(request: HttpRequest) -> HttpResponse:
    """HTMX: 이미지 분석 API (Gemini Vision)"""
    uploaded_file = request.FILES.get("image")

    if not uploaded_file:
        return render(
            request,
            "supplements/pages/upload/_error.html",
            {"error": "이미지를 선택해주세요"},
        )

    try:
        # 이미지 바이트 읽기
        image_bytes = uploaded_file.read()

        # Vision AI 분석
        vision_service = get_vision_service()
        result = vision_service.analyze_label_bytes(image_bytes)

        if result.error:
            return render(
                request,
                "supplements/pages/upload/_error.html",
                {"error": f"분석 실패: {result.error}"},
            )

        # 성분 목록을 템플릿 형식으로 변환
        ingredients = [
            {
                "name": ing.name,
                "amount": str(ing.amount) if ing.amount else "",
                "unit": ing.unit,
                "daily_value": f"{ing.daily_value_percent}%" if ing.daily_value_percent else "",
            }
            for ing in result.ingredients
        ]

        return render(
            request,
            "supplements/pages/upload/_result.html",
            {
                "success": True,
                "product_name": result.product_name,
                "brand": result.brand,
                "serving_size": result.serving_size,
                "servings_count": result.servings_count,
                "ingredients": ingredients,
                "filename": uploaded_file.name,
            },
        )

    except Exception as e:
        return render(
            request,
            "supplements/pages/upload/_error.html",
            {"error": f"처리 중 오류: {e!s}"},
        )

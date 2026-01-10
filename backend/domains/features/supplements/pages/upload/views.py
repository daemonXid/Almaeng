"""
📷 Upload Page Views

Vision AI OCR 업로드 페이지.
"""

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST


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
    """HTMX: 이미지 분석 API

    실제 Vision AI 로직은 추후 구현.
    현재는 UI 스캐폴딩용 스텁.
    """
    uploaded_file = request.FILES.get("image")

    if not uploaded_file:
        return render(
            request,
            "supplements/pages/upload/_error.html",
            {"error": "이미지를 선택해주세요"},
        )

    # TODO: Vision AI (EasyOCR, Google Vision, Gemini) 연동
    # 현재는 스텁 응답
    mock_ingredients = [
        {"name": "비타민 D3", "amount": "1000", "unit": "IU"},
        {"name": "비타민 K2", "amount": "100", "unit": "mcg"},
        {"name": "칼슘", "amount": "500", "unit": "mg"},
    ]

    return render(
        request,
        "supplements/pages/upload/_result.html",
        {
            "success": True,
            "ingredients": mock_ingredients,
            "filename": uploaded_file.name,
        },
    )

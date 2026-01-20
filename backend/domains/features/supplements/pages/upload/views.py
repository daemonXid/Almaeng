"""
📷 Upload Page Views

Vision AI OCR 업로드 페이지 - Gemini Vision 연동.
"""

import json

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST

from ...services import create_supplement_from_ocr
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
                "ingredients_json": json.dumps(ingredients, ensure_ascii=False),
                "filename": uploaded_file.name,
            },
        )

    except Exception as e:
        return render(
            request,
            "supplements/pages/upload/_error.html",
            {"error": f"처리 중 오류: {e!s}"},
        )


@require_POST
@login_required
def save_ocr_result(request: HttpRequest) -> HttpResponse:
    """HTMX: OCR 결과를 Supplement으로 저장"""
    try:
        product_name = request.POST.get("product_name", "").strip()
        brand = request.POST.get("brand", "").strip()
        serving_size = request.POST.get("serving_size", "").strip()
        servings_count = int(request.POST.get("servings_count", 1) or 1)
        ingredients_json = request.POST.get("ingredients", "[]")

        if not product_name:
            return render(
                request,
                "supplements/pages/upload/_error.html",
                {"error": "제품명은 필수입니다"},
            )

        # JSON 파싱
        try:
            ingredients = json.loads(ingredients_json)
        except json.JSONDecodeError:
            ingredients = []

        # DB 저장
        supplement = create_supplement_from_ocr(
            product_name=product_name,
            brand=brand,
            serving_size=serving_size,
            servings_count=servings_count,
            ingredients=ingredients,
        )

        # 성공 응답
        return HttpResponse(f"""
            <div class="p-6 rounded-2xl bg-emerald-50 dark:bg-emerald-900/20 border border-emerald-200 dark:border-emerald-800 text-center">
                <span class="text-5xl mb-4 block">✅</span>
                <h3 class="text-xl font-bold text-emerald-800 dark:text-emerald-300 mb-2">
                    저장 완료!
                </h3>
                <p class="text-gray-600 dark:text-gray-400 mb-4">
                    <strong>{supplement.name}</strong>이(가) 등록되었습니다.
                </p>
                <div class="flex gap-3 justify-center">
                    <a href="/supplements/{supplement.id}/"
                       class="px-6 py-2.5 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl font-medium transition-colors">
                        상세 페이지 보기 →
                    </a>
                    <a href="/supplements/upload/"
                       class="px-6 py-2.5 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-300 rounded-xl font-medium transition-colors">
                        다른 제품 스캔
                    </a>
                </div>
            </div>
        """)

    except Exception as e:
        return render(
            request,
            "supplements/pages/upload/_error.html",
            {"error": f"저장 실패: {e!s}"},
        )

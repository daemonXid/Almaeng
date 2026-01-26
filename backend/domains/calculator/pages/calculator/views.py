"""
Body Calculator Views
"""

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

# ✅ DAEMON Rule: Import from interface.py only
from ...interface import (
    ActivityLevel,
    BodyInput,
    Gender,
    Goal,
    calculate_nutrition,
)


@require_http_methods(["GET", "POST"])
def calculator_view(request: HttpRequest) -> HttpResponse:
    """바디 계산기 페이지"""
    result = None
    error = None

    if request.method == "POST":
        try:
            # 폼 데이터 파싱
            body_input = BodyInput(
                gender=Gender(request.POST.get("gender", "male")),
                age=int(request.POST.get("age", 25)),
                height_cm=float(request.POST.get("height_cm", 170)),
                weight_kg=float(request.POST.get("weight_kg", 70)),
                body_fat_percent=(
                    float(bf)
                    if (bf := request.POST.get("body_fat_percent"))
                    else None
                ),
                activity_level=ActivityLevel(
                    request.POST.get("activity_level", "moderate")
                ),
                goal=Goal(request.POST.get("goal", "maintain")),
            )

            # 계산 실행
            result = calculate_nutrition(body_input)

        except (ValueError, KeyError) as e:
            error = f"입력 값이 올바르지 않습니다: {e}"

    context = {
        "result": result,
        "error": error,
        "genders": Gender,
        "activity_levels": ActivityLevel,
        "goals": Goal,
    }

    return render(request, "calculator/calculator.html", context)

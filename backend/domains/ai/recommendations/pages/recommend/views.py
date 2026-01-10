"""
🎯 Recommendation Page Views
"""

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST

from ...services import get_health_quiz_recommendations, get_personalized_recommendations


def recommend_page(request: HttpRequest) -> HttpResponse:
    """AI 추천 홈페이지"""
    user_id = request.user.id if request.user.is_authenticated else None
    recommendations = []

    if user_id:
        recommendations = get_personalized_recommendations(user_id, limit=6)

    return render(
        request,
        "recommendations/pages/recommend/recommend.html",
        {
            "page_title": "AI 추천 | ALMAENG",
            "recommendations": recommendations,
        },
    )


def quiz_page(request: HttpRequest) -> HttpResponse:
    """건강 설문 페이지"""
    return render(
        request,
        "recommendations/pages/recommend/quiz.html",
        {"page_title": "건강 설문 | ALMAENG"},
    )


@require_POST
def quiz_result(request: HttpRequest) -> HttpResponse:
    """HTMX: 설문 결과"""
    answers = {
        "sleep_issues": request.POST.get("sleep_issues") == "on",
        "low_energy": request.POST.get("low_energy") == "on",
        "stress": request.POST.get("stress") == "on",
        "digestion": request.POST.get("digestion") == "on",
        "skin_hair": request.POST.get("skin_hair") == "on",
    }

    recommendations = get_health_quiz_recommendations(answers)

    return render(
        request,
        "recommendations/pages/recommend/_quiz_result.html",
        {"recommendations": recommendations},
    )

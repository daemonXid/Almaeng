from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse as reversed
from django.views.decorators.http import require_POST

from ...data.quiz_questions import QUIZ_STEPS


def recommend_page(request: HttpRequest) -> HttpResponse:
    """추천 시작 페이지"""
    return render(request, "recommendations/pages/recommend/quiz_intro.html")


def quiz_intro(request: HttpRequest) -> HttpResponse:
    """건강 설문 소개 페이지 (Deprecated alias)"""
    return recommend_page(request)


def quiz_page(request: HttpRequest) -> HttpResponse:
    """설문 단계별 페이지 표시"""
    current_step = int(request.GET.get("step", 1))

    if current_step < 1 or current_step > len(QUIZ_STEPS):
        return redirect("recommendations:quiz")

    current_step_data = QUIZ_STEPS[current_step - 1]
    
    # Calculate progress for the progress bar
    progress_percent = int((current_step / len(QUIZ_STEPS)) * 100)

    return render(
        request,
        "recommendations/pages/recommend/quiz_step.html",
        {
            "page_title": f"건강 설문 ({current_step}/{len(QUIZ_STEPS)}) | ALMAENG",
            "step_data": current_step_data,
            "total_steps": len(QUIZ_STEPS),
            "current_step": current_step,
            "progress_percent": progress_percent,
            "next_step": current_step + 1 if current_step < len(QUIZ_STEPS) else None,
        },
    )


def quiz_result(request: HttpRequest) -> HttpResponse:
    """설문 결과 분석 및 표시 - Gemini AI 연동"""
    from ...services import get_ai_recommendation_report

    if request.method != "POST":
        return redirect("recommendations:quiz")

    current_step = int(request.POST.get("current_step", 1))

    # Save current step data to session
    step_data = QUIZ_STEPS[current_step - 1]
    for question in step_data["questions"]:
        qid = question["id"]
        value = request.POST.get(qid)
        if value:
            request.session[f"quiz_{qid}"] = value

    # If not last step, go to next
    if current_step < len(QUIZ_STEPS):
        return redirect(f"{reversed('recommendations:quiz')}?step={current_step + 1}")

    # --- Collect all quiz data ---
    data = {}
    for step in QUIZ_STEPS:
        for q in step["questions"]:
            qid = q["id"]
            data[qid] = request.session.get(f"quiz_{qid}")

    # --- AI-powered Analysis ---
    result = get_ai_recommendation_report(data)

    # Clear quiz session data
    for step in QUIZ_STEPS:
        for q in step["questions"]:
            request.session.pop(f"quiz_{q['id']}", None)

    return render(
        request,
        "recommendations/pages/recommend/_quiz_result.html",
        {
            "page_title": "건강 설문 분석 결과 | ALMAENG",
            "report": result.report,
            "products": result.products,
            "categories": result.categories,
            "user_name": request.user.get_full_name() if request.user.is_authenticated else "회원",
        },
    )

def get_gender_text(code):
    return "남성" if code == "male" else "여성" if code == "female" else ""

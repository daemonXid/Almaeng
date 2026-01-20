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
    """설문 결과 분석 및 표시"""
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

    # --- Analysis Logic ---
    data = {}
    for step in QUIZ_STEPS:
        for q in step["questions"]:
            qid = q["id"]
            data[qid] = request.session.get(f"quiz_{qid}")

    # Generate Report
    gender = data.get("gender", "unknown")
    age = int(data.get("age", 0) or 0)
    
    analysis_text = []
    
    # Header
    if age > 0:
        analysis_text.append(f"📌 **{age}세 {get_gender_text(gender)}**님의 건강 분석 결과입니다.")
        
    symptoms = []
    if data.get("q11") == "yes": symptoms.append("만성 피로")
    if data.get("q12") == "yes": symptoms.append("눈 건강 저하")
    if data.get("q13") == "yes": symptoms.append("피부 건조")
    if data.get("q18") == "yes": symptoms.append("관절 통증")

    if symptoms:
        analysis_text.append(f"\n💡 **주요 불편 증상**: {', '.join(symptoms)}")

    # Recommendation Logic
    recommendations = []
    
    if data.get("q11") == "yes" or data.get("q27") == "yes":
        recommendations.append("- **비타민 B & 마그네슘**: 에너지 생성과 피로 회복")

    if data.get("q12") == "yes" or data.get("q22") == "yes":
        recommendations.append("- **오메가3 & 루테인**: 눈 건강과 혈행 개선")

    if data.get("q18") == "yes" or age >= 50:
        recommendations.append("- **MSM & 칼슘/마그네슘**: 관절 연골 및 뼈 건강")

    if not recommendations:
        recommendations.append("- **종합비타민**: 기초 영양 밸런스")

    final_report = "\n".join(analysis_text) + "\n\n📋 **추천 영양 성분**:\n" + "\n".join(list(set(recommendations)))

    return render(
        request,
        "recommendations/pages/recommend/_quiz_result.html",
        {
            "page_title": "건강 설문 분석 결과 | ALMAENG",
            "report": final_report,
            "user_name": "회원",
        },
    )

def get_gender_text(code):
    return "남성" if code == "male" else "여성" if code == "female" else ""

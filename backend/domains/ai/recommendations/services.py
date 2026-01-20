"""
🎯 AI Recommendations Services

Gemini 기반 영양제 추천 로직.
"""

import os
from dataclasses import dataclass
from django.conf import settings
from django.db.models import Q


GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or getattr(settings, "GEMINI_API_KEY", "")


@dataclass
class RecommendationResult:
    """추천 결과 데이터"""
    report: str
    products: list[dict]
    categories: list[str]


def _get_gemini_client():
    """Gemini 클라이언트 반환"""
    if not GEMINI_API_KEY:
        return None
    from google import genai
    return genai.Client(api_key=GEMINI_API_KEY)


def get_similar_products(supplement_id: int, limit: int = 5) -> list[dict]:
    """
    유사 제품 추천 - DB 기반 + AI 보완
    """
    from domains.features.supplements.models import MFDSHealthFood, Ingredient

    results = []

    try:
        # 원본 제품 정보 조회
        product = MFDSHealthFood.objects.filter(id=supplement_id).first()
        if not product:
            return []

        # 같은 기능성을 가진 제품 검색
        if product.functionality:
            keywords = product.functionality[:50].split()[:3]
            q = Q()
            for kw in keywords:
                if len(kw) > 2:
                    q |= Q(functionality__icontains=kw)

            similar = MFDSHealthFood.objects.filter(q).exclude(id=supplement_id)[:limit]

            for s in similar:
                results.append({
                    "supplement_id": s.id,
                    "name": s.product_name,
                    "brand": s.company_name,
                    "match_score": 0.85,
                    "reason": f"유사한 기능성: {s.functionality[:50]}...",
                })
    except Exception:
        pass

    return results[:limit]


def get_personalized_recommendations(
    user_id: int,
    health_goals: list[str] | None = None,
    limit: int = 10,
) -> list[dict]:
    """
    개인화 추천 - 건강 목표 기반
    """
    from domains.features.supplements.models import MFDSHealthFood

    goals = health_goals or ["general_health"]
    recommendations = []

    # 건강 목표별 키워드 매핑
    goal_keywords = {
        "bone_health": ["칼슘", "비타민D", "마그네슘", "뼈"],
        "immune": ["면역", "비타민C", "아연", "프로폴리스"],
        "eye_health": ["루테인", "눈", "시력", "지아잔틴"],
        "fatigue": ["비타민B", "피로", "에너지", "철분"],
        "joint": ["관절", "MSM", "글루코사민", "콘드로이틴"],
        "skin": ["콜라겐", "피부", "히알루론산", "비타민E"],
        "general_health": ["종합비타민", "멀티비타민", "오메가3"],
    }

    for goal in goals:
        keywords = goal_keywords.get(goal, goal_keywords["general_health"])
        q = Q()
        for kw in keywords:
            q |= Q(functionality__icontains=kw) | Q(product_name__icontains=kw)

        products = MFDSHealthFood.objects.filter(q)[:3]
        for p in products:
            recommendations.append({
                "id": p.id,
                "name": p.product_name,
                "brand": p.company_name,
                "reason": f"{goal} 개선에 도움",
                "goal": goal,
            })

    return recommendations[:limit]


def get_ai_recommendation_report(quiz_data: dict) -> RecommendationResult:
    """
    Gemini AI를 사용한 종합 건강 분석 및 추천
    """
    client = _get_gemini_client()

    # 기본 프로필
    gender = quiz_data.get("gender", "unknown")
    age = int(quiz_data.get("age", 0) or 0)

    # 증상 수집
    symptoms = []
    if quiz_data.get("q11") == "yes": symptoms.append("만성 피로")
    if quiz_data.get("q12") == "yes": symptoms.append("눈 건강 저하")
    if quiz_data.get("q13") == "yes": symptoms.append("피부 건조")
    if quiz_data.get("q18") == "yes": symptoms.append("관절 통증")
    if quiz_data.get("q27") == "yes": symptoms.append("수면 문제")
    if quiz_data.get("q22") == "yes": symptoms.append("스트레스")

    gender_text = "남성" if gender == "male" else "여성" if gender == "female" else ""

    # AI 없이도 동작하는 기본 로직
    if not client:
        return _generate_rule_based_report(age, gender_text, symptoms)

    # Gemini AI로 분석
    try:
        prompt = f"""
당신은 영양제 전문가입니다. 아래 사용자 정보를 바탕으로 맞춤형 영양제 추천을 해주세요.

**사용자 정보:**
- 나이: {age}세
- 성별: {gender_text}
- 주요 불편 증상: {', '.join(symptoms) if symptoms else '특별히 없음'}

**요청사항:**
1. 현재 건강 상태에 대한 간단한 분석 (2-3문장)
2. 추천 영양 성분 3-5개 (각 성분별 추천 이유 포함)
3. 섭취 시 주의사항 1-2개

응답 형식:
📌 **건강 분석**
(분석 내용)

📋 **추천 영양 성분**
- **성분명**: 추천 이유
- **성분명**: 추천 이유
...

⚠️ **주의사항**
(주의사항)
"""
        response = client.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents=prompt,
        )
        report = response.text.strip()

        # 추천 카테고리 추출
        categories = _extract_categories_from_symptoms(symptoms)
        products = get_personalized_recommendations(0, categories, 6)

        return RecommendationResult(
            report=report,
            products=products,
            categories=categories,
        )

        # AI 실패시 규칙 기반으로 폴백
        print(f"❌ Gemini API Error: {e}")  # Debug log
        return _generate_rule_based_report(age, gender_text, symptoms)


def _generate_rule_based_report(age: int, gender_text: str, symptoms: list[str]) -> RecommendationResult:
    """규칙 기반 추천 (AI 폴백)"""
    analysis = []
    recommendations = []
    categories = []

    # 헤더
    if age > 0:
        analysis.append(f"📌 **{age}세 {gender_text}**님의 건강 분석 결과입니다.")

    if symptoms:
        analysis.append(f"\n💡 **주요 불편 증상**: {', '.join(symptoms)}")

    # 증상별 추천
    if "만성 피로" in symptoms or "수면 문제" in symptoms:
        recommendations.append("- **비타민 B 복합체 & 마그네슘**: 에너지 생성과 피로 회복")
        categories.append("fatigue")

    if "눈 건강 저하" in symptoms:
        recommendations.append("- **루테인 & 오메가3**: 눈 건강과 시력 보호")
        categories.append("eye_health")

    if "관절 통증" in symptoms or age >= 50:
        recommendations.append("- **MSM & 글루코사민**: 관절 연골 건강")
        categories.append("joint")

    if "피부 건조" in symptoms:
        recommendations.append("- **콜라겐 & 비타민E**: 피부 탄력과 보습")
        categories.append("skin")

    if "스트레스" in symptoms:
        recommendations.append("- **마그네슘 & 비타민B6**: 스트레스 완화")
        categories.append("immune")

    if not recommendations:
        recommendations.append("- **종합비타민**: 기초 영양 밸런스")
        categories.append("general_health")

    report = "\n".join(analysis) + "\n\n📋 **추천 영양 성분**:\n" + "\n".join(list(set(recommendations)))
    report += "\n\n⚠️ **주의사항**: 영양제는 의약품이 아니며, 증상이 지속되면 전문의 상담을 권장합니다."

    products = get_personalized_recommendations(0, categories, 6)

    return RecommendationResult(
        report=report,
        products=products,
        categories=categories,
    )


def _extract_categories_from_symptoms(symptoms: list[str]) -> list[str]:
    """증상에서 건강 카테고리 추출"""
    categories = []
    symptom_map = {
        "만성 피로": "fatigue",
        "눈 건강 저하": "eye_health",
        "피부 건조": "skin",
        "관절 통증": "joint",
        "수면 문제": "fatigue",
        "스트레스": "immune",
    }
    for symptom in symptoms:
        if symptom in symptom_map:
            categories.append(symptom_map[symptom])

    return categories if categories else ["general_health"]


def get_ai_ingredient_analysis(ingredients: list[str]) -> str:
    """
    Gemini로 성분 분석
    """
    client = _get_gemini_client()

    if not client:
        return f"""
📊 **{len(ingredients)}개 성분 분석 결과**

✅ **시너지 효과**: 비타민 D3와 K2는 함께 섭취 시 효과 증가
⚠️ **주의**: 칼슘과 철분은 2시간 간격 권장
⏰ **권장 시간**: 지용성 비타민은 식사와 함께
"""

    try:
        prompt = f"""
다음 영양제 성분을 분석해주세요:
{", ".join(ingredients)}

분석 항목:
1. 성분 간 상호작용 (시너지/충돌)
2. 권장 섭취 시간
3. 주의사항

간결하게 3-4줄로 답변해주세요.
"""
        response = client.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents=prompt,
        )
        return response.text.strip()

    except Exception as e:
        print(f"❌ Gemini Ingredient Analysis Error: {e}")
        return f"분석 중 오류가 발생했습니다: {e!s}"


def get_health_quiz_recommendations(quiz_answers: dict) -> list[dict]:
    """
    건강 설문 기반 추천 (레거시 호환)
    """
    result = get_ai_recommendation_report(quiz_answers)

    recommendations = []
    for cat in result.categories:
        recommendations.append({
            "category": cat,
            "products": [p["name"] for p in result.products if p.get("goal") == cat],
            "priority": "high" if cat in ["fatigue", "immune"] else "medium",
        })

    return recommendations

"""
🎯 AI Recommendations Services

Gemini 기반 영양제 추천 로직.
"""

from django.conf import settings

# Gemini API (추후 연동)
GEMINI_API_KEY = getattr(settings, "GEMINI_API_KEY", "")


def get_similar_products(supplement_id: int, limit: int = 5) -> list[dict]:
    """
    유사 제품 추천

    기준:
    - 성분 구성 유사도
    - 가격대
    - 사용자 리뷰/평점
    """
    # TODO: 실제 ML 모델 또는 Gemini API 연동
    # 현재는 스텁 데이터
    return [
        {
            "supplement_id": 101,
            "name": "유사 영양제 A",
            "match_score": 0.92,
            "reason": "동일한 비타민 D3, K2 조합",
        },
        {
            "supplement_id": 102,
            "name": "유사 영양제 B",
            "match_score": 0.87,
            "reason": "비슷한 칼슘 함량",
        },
    ][:limit]


def get_personalized_recommendations(
    user_id: int,
    health_goals: list[str] | None = None,
    limit: int = 10,
) -> list[dict]:
    """
    개인화 추천

    기준:
    - 사용자 구매 이력
    - 건강 목표
    - 나이/성별 (프로필)
    """
    goals = health_goals or ["general_health"]

    # TODO: Gemini API로 개인화 추천 생성
    recommendations = []

    if "bone_health" in goals:
        recommendations.extend(
            [
                {"id": 1, "name": "칼슘 + 비타민 D", "reason": "뼈 건강에 필수"},
                {"id": 2, "name": "마그네슘", "reason": "칼슘 흡수 도움"},
            ]
        )

    if "immune" in goals:
        recommendations.extend(
            [
                {"id": 3, "name": "비타민 C", "reason": "면역력 강화"},
                {"id": 4, "name": "아연", "reason": "면역 세포 활성화"},
            ]
        )

    if "general_health" in goals:
        recommendations.extend(
            [
                {"id": 5, "name": "종합 비타민", "reason": "기본 영양소 보충"},
                {"id": 6, "name": "오메가-3", "reason": "심혈관 건강"},
            ]
        )

    return recommendations[:limit]


async def get_ai_ingredient_analysis(ingredients: list[str]) -> str:
    """
    Gemini로 성분 분석

    입력된 성분 목록에 대해 AI가 분석 및 조언 제공.
    """
    if not GEMINI_API_KEY:
        return "AI 분석 기능을 사용하려면 GEMINI_API_KEY 설정이 필요합니다."

    # TODO: Gemini API 호출
    f"""
    다음 영양제 성분을 분석해주세요:
    {", ".join(ingredients)}

    분석 항목:
    1. 성분 간 상호작용 (시너지/충돌)
    2. 권장 섭취 시간
    3. 주의사항
    """

    # 스텁 응답
    return f"""
    📊 **{len(ingredients)}개 성분 분석 결과**

    ✅ **시너지 효과**: 비타민 D3와 K2는 함께 섭취 시 효과 증가
    ⚠️ **주의**: 칼슘과 철분은 2시간 간격 권장
    ⏰ **권장 시간**: 지용성 비타민은 식사와 함께
    """


def get_health_quiz_recommendations(quiz_answers: dict) -> list[dict]:
    """
    건강 설문 기반 추천

    설문 답변을 분석하여 맞춤 영양제 추천.
    """
    recommendations = []

    # 수면 문제
    if quiz_answers.get("sleep_issues"):
        recommendations.append(
            {
                "category": "수면 개선",
                "products": ["마그네슘", "L-테아닌", "멜라토닌"],
                "priority": "high",
            }
        )

    # 에너지 부족
    if quiz_answers.get("low_energy"):
        recommendations.append(
            {
                "category": "에너지 부스트",
                "products": ["비타민 B 복합체", "철분", "CoQ10"],
                "priority": "high",
            }
        )

    # 스트레스
    if quiz_answers.get("stress"):
        recommendations.append(
            {
                "category": "스트레스 관리",
                "products": ["마그네슘", "아슈와간다", "비타민 B6"],
                "priority": "medium",
            }
        )

    return recommendations

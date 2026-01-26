"""
Body Calculator Services

Mifflin-St Jeor 공식:
- 남성: BMR = 10 * 체중(kg) + 6.25 * 키(cm) - 5 * 나이 + 5
- 여성: BMR = 10 * 체중(kg) + 6.25 * 키(cm) - 5 * 나이 - 161

활동 계수:
- 거의 운동 안 함: 1.2
- 가벼운 운동: 1.375
- 중간 강도: 1.55
- 격렬한 운동: 1.725
- 매우 격렬: 1.9

목표별 조정:
- 벌크업: +15%
- 다이어트: -20%
- 린매스업: +5%
- 유지: 0%
"""

from .schemas import (
    ActivityLevel,
    BodyInput,
    Gender,
    Goal,
    NutritionResult,
)

# 활동 계수 매핑
ACTIVITY_MULTIPLIERS: dict[ActivityLevel, float] = {
    ActivityLevel.SEDENTARY: 1.2,
    ActivityLevel.LIGHT: 1.375,
    ActivityLevel.MODERATE: 1.55,
    ActivityLevel.ACTIVE: 1.725,
    ActivityLevel.VERY_ACTIVE: 1.9,
}

# 목표별 칼로리 조정 비율 (%)
GOAL_ADJUSTMENTS: dict[Goal, int] = {
    Goal.BULK: 15,
    Goal.CUT: -20,
    Goal.LEAN: 5,
    Goal.MAINTAIN: 0,
}

# 목표 라벨 (한글)
GOAL_LABELS: dict[Goal, str] = {
    Goal.BULK: "벌크업",
    Goal.CUT: "다이어트",
    Goal.LEAN: "린매스업",
    Goal.MAINTAIN: "유지",
}


def calculate_bmr(body: BodyInput) -> int:
    """
    Mifflin-St Jeor 공식으로 기초 대사량(BMR) 계산

    체지방률이 있으면 Katch-McArdle 공식 사용 (더 정확)
    """
    if body.body_fat_percent is not None:
        # Katch-McArdle 공식: BMR = 370 + 21.6 * 제지방량(kg)
        lean_mass = body.weight_kg * (1 - body.body_fat_percent / 100)
        return int(370 + 21.6 * lean_mass)

    # Mifflin-St Jeor 공식
    base = 10 * body.weight_kg + 6.25 * body.height_cm - 5 * body.age

    if body.gender == Gender.MALE:
        return int(base + 5)
    return int(base - 161)


def calculate_tdee(bmr: int, activity_level: ActivityLevel) -> int:
    """TDEE = BMR * 활동 계수"""
    multiplier = ACTIVITY_MULTIPLIERS[activity_level]
    return int(bmr * multiplier)


def calculate_target_calories(tdee: int, goal: Goal) -> int:
    """목표에 따른 권장 칼로리"""
    adjustment = GOAL_ADJUSTMENTS[goal]
    return int(tdee * (1 + adjustment / 100))


def calculate_macros(
    target_calories: int, weight_kg: float, goal: Goal
) -> tuple[int, int, int]:
    """
    매크로 영양소 계산 (단백질, 탄수화물, 지방)

    단백질: 목표별로 다름
    - 벌크업/린매스업: 체중 * 2.0g
    - 다이어트: 체중 * 2.2g (근손실 방지)
    - 유지: 체중 * 1.6g

    지방: 총 칼로리의 25%
    탄수화물: 나머지
    """
    # 단백질 (g)
    if goal in (Goal.BULK, Goal.LEAN):
        protein_g = int(weight_kg * 2.0)
    elif goal == Goal.CUT:
        protein_g = int(weight_kg * 2.2)
    else:
        protein_g = int(weight_kg * 1.6)

    # 지방 (g) - 총 칼로리의 25%
    fat_calories = target_calories * 0.25
    fat_g = int(fat_calories / 9)  # 1g 지방 = 9kcal

    # 탄수화물 (g) - 나머지
    protein_calories = protein_g * 4  # 1g 단백질 = 4kcal
    remaining_calories = target_calories - protein_calories - fat_calories
    carbs_g = int(remaining_calories / 4)  # 1g 탄수화물 = 4kcal

    return protein_g, carbs_g, fat_g


def calculate_nutrition(body: BodyInput) -> NutritionResult:
    """전체 영양 계산 실행"""
    bmr = calculate_bmr(body)
    tdee = calculate_tdee(bmr, body.activity_level)
    target_calories = calculate_target_calories(tdee, body.goal)
    protein_g, carbs_g, fat_g = calculate_macros(
        target_calories, body.weight_kg, body.goal
    )

    return NutritionResult(
        bmr=bmr,
        tdee=tdee,
        target_calories=target_calories,
        protein_g=protein_g,
        carbs_g=carbs_g,
        fat_g=fat_g,
        goal_label=GOAL_LABELS[body.goal],
        goal_adjustment_percent=GOAL_ADJUSTMENTS[body.goal],
    )

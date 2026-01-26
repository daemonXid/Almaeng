"""
Body Calculator Schemas (Pydantic Models)

Mifflin-St Jeor 공식 기반 BMR/TDEE 계산
"""

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"


class ActivityLevel(str, Enum):
    """활동량 수준"""

    SEDENTARY = "sedentary"  # 거의 운동 안 함 (1.2)
    LIGHT = "light"  # 가벼운 운동 1-3일/주 (1.375)
    MODERATE = "moderate"  # 중간 강도 3-5일/주 (1.55)
    ACTIVE = "active"  # 격렬한 운동 6-7일/주 (1.725)
    VERY_ACTIVE = "very_active"  # 매우 격렬, 육체 노동 (1.9)


class Goal(str, Enum):
    """목표"""

    BULK = "bulk"  # 벌크업 (+15%)
    CUT = "cut"  # 다이어트 (-20%)
    LEAN = "lean"  # 린매스업 (+5%)
    MAINTAIN = "maintain"  # 유지 (0%)


class BodyInput(BaseModel):
    """사용자 신체 정보 입력"""

    model_config = ConfigDict(frozen=True)

    gender: Gender
    age: int = Field(ge=10, le=100)
    height_cm: float = Field(ge=100, le=250)
    weight_kg: float = Field(ge=30, le=300)
    body_fat_percent: float | None = Field(default=None, ge=3, le=60)
    activity_level: ActivityLevel
    goal: Goal


class NutritionResult(BaseModel):
    """계산 결과"""

    model_config = ConfigDict(frozen=True)

    # 기초 대사량
    bmr: int  # kcal

    # 총 일일 에너지 소비량
    tdee: int  # kcal

    # 목표별 권장 칼로리
    target_calories: int  # kcal

    # 권장 영양소 (g)
    protein_g: int  # 단백질
    carbs_g: int  # 탄수화물
    fat_g: int  # 지방

    # 추가 정보
    goal_label: str
    goal_adjustment_percent: int

"""
📝 Health Quiz Questions Data

3 Steps, 10 Questions each.
"""

QUIZ_STEPS = [
    {
        "step": 1,
        "title": "기본 정보 입력",
        "description": "더 정확한 분석을 위해 기본 정보를 알려주세요.",
        "questions": [
            {
                "id": "gender",
                "text": "성별을 선택해주세요.",
                "type": "select",
                "options": [
                    {"value": "male", "label": "남성"},
                    {"value": "female", "label": "여성"},
                ],
            },
            {"id": "age", "text": "나이를 입력해주세요.", "type": "number", "unit": "세"},
            {"id": "height", "text": "키를 입력해주세요.", "type": "number", "unit": "cm"},
            {"id": "weight", "text": "몸무게를 입력해주세요.", "type": "number", "unit": "kg"},
        ],
    },
    {
        "step": 2,
        "title": "기본 건강 상태 Check",
        "description": "현재 당신의 기본적인 건강 상태를 알려주세요.",
        "questions": [
            {"id": "q1", "text": "최근 3개월 내에 크게 아프거나 입원한 적이 있나요?", "type": "yesno"},
            {"id": "q2", "text": "현재 복용 중인 처방약이 있나요?", "type": "yesno"},
            {"id": "q3", "text": "하루 평균 수면 시간이 6시간 미만인가요?", "type": "yesno"},
            {"id": "q4", "text": "규칙적으로 아침 식사를 하시나요?", "type": "yesno"},
            {"id": "q5", "text": "주 3회 이상 술을 마시나요?", "type": "yesno"},
            {"id": "q6", "text": "흡연을 하시나요?", "type": "yesno"},
            {"id": "q7", "text": "일주일에 3회 이상 운동을 하시나요?", "type": "yesno"},
            {"id": "q8", "text": "하루에 물을 1리터 이상 마시나요?", "type": "yesno"},
            {"id": "q9", "text": "소화가 잘 안 되거나 속이 자주 더부룩한가요?", "type": "yesno"},
            {"id": "q10", "text": "평소에 과일이나 채소를 자주 챙겨 드시나요?", "type": "yesno"},
        ],
    },
    {
        "step": 3,
        "title": "불편한 증상 상세 Check",
        "description": "개선하고 싶은 구체적인 증상을 선택해주세요.",
        "questions": [
            {"id": "q11", "text": "자고 일어나도 피곤함이 가시지 않나요?", "type": "yesno"},
            {"id": "q12", "text": "눈이 자주 침침하거나 건조한가요?", "type": "yesno"},
            {"id": "q13", "text": "피부가 건조하거나 트러블이 자주 생기나요?", "type": "yesno"},
            {"id": "q14", "text": "머리카락이 가늘어지거나 많이 빠지나요?", "type": "yesno"},
            {"id": "q15", "text": "손발이 자주 저리거나 차가운가요?", "type": "yesno"},
            {"id": "q16", "text": "감기에 자주 걸리거나 잔병치레가 많나요?", "type": "yesno"},
            {"id": "q17", "text": "입안이 자주 허나 혓바늘이 돋나요?", "type": "yesno"},
            {"id": "q18", "text": "관절이 뻣뻣하거나 통증이 느껴지나요?", "type": "yesno"},
            {"id": "q19", "text": "최근 체중 변화가 심한가요?", "type": "yesno"},
            {"id": "q20", "text": "변비나 설사가 자주 발생하나요?", "type": "yesno"},
        ],
    },
    {
        "step": 4,
        "title": "라이프스타일 & 목표 Check",
        "description": "당신의 생활 패턴과 영양제 섭취 목표를 알려주세요.",
        "questions": [
            {"id": "q21", "text": "하루 중 대부분의 시간을 실내에서 보내시나요?", "type": "yesno"},
            {"id": "q22", "text": "스마트폰이나 모니터를 하루 6시간 이상 보시나요?", "type": "yesno"},
            {"id": "q23", "text": "인스턴트나 배달 음식을 주 3회 이상 드시나요?", "type": "yesno"},
            {"id": "q24", "text": "스트레스를 많이 받는 환경에 있나요?", "type": "yesno"},
            {"id": "q25", "text": "현재 임신 중이거나 임신 준비 중이신가요?", "type": "yesno"},
            {"id": "q26", "text": "다이어트나 식단 조절을 하고 계신가요?", "type": "yesno"},
            {"id": "q27", "text": "활력 증진이 가장 큰 목표인가요?", "type": "yesno"},
            {"id": "q28", "text": "면역력 강화가 가장 큰 목표인가요?", "type": "yesno"},
            {"id": "q29", "text": "노화 방지나 항산화가 목표인가요?", "type": "yesno"},
            {"id": "q30", "text": "알약(정제) 크기가 크면 섭취하기 힘든가요?", "type": "yesno"},
        ],
    },
]

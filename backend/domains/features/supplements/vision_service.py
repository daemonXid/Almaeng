"""
📷 Vision AI Service

Gemini Vision API를 사용한 영양제 라벨 OCR 및 성분 추출.
"""

import os
import re
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path

from django.conf import settings
from google import genai


@dataclass
class ExtractedIngredient:
    """추출된 성분 정보"""

    name: str
    amount: Decimal | None = None
    unit: str = ""
    daily_value_percent: int | None = None


@dataclass
class LabelAnalysisResult:
    """라벨 분석 결과"""

    product_name: str
    brand: str
    serving_size: str
    servings_count: int
    ingredients: list[ExtractedIngredient]
    raw_text: str = ""
    error: str | None = None


class VisionService:
    """Gemini Vision 기반 라벨 분석 서비스"""

    PROMPT = """이 영양제 라벨 이미지를 분석해주세요.

다음 정보를 JSON 형식으로 추출해주세요:
{
    "product_name": "제품명",
    "brand": "브랜드명",
    "serving_size": "1회 섭취량 (예: 1정, 2캡슐)",
    "servings_count": 숫자 (총 몇 회분),
    "ingredients": [
        {
            "name": "성분명 (영어 또는 한글)",
            "amount": 숫자,
            "unit": "단위 (mg, mcg, IU 등)",
            "daily_value_percent": 숫자 또는 null
        }
    ]
}

중요:
- 성분명은 정확하게 추출 (예: Vitamin D3, 비타민 D3)
- 함량은 숫자만 (예: 1000)
- 단위는 정확하게 (mg, mcg, IU, %)
- 일일 권장량(%)이 있으면 포함
- JSON만 반환, 다른 텍스트 없이"""

    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY") or getattr(settings, "GEMINI_API_KEY", None)
        if not api_key:
            raise ValueError("GEMINI_API_KEY not configured")

        self.client = genai.Client(api_key=api_key)
        self.model = "gemini-2.0-flash"

    def analyze_label(self, image_path: str | Path) -> LabelAnalysisResult:
        """이미지 파일에서 라벨 분석"""
        try:
            image_path = Path(image_path)
            if not image_path.exists():
                return LabelAnalysisResult(
                    product_name="",
                    brand="",
                    serving_size="",
                    servings_count=0,
                    ingredients=[],
                    error="Image file not found",
                )

            # 이미지 업로드
            image_file = self.client.files.upload(file=str(image_path))

            # Vision API 호출
            response = self.client.models.generate_content(
                model=self.model,
                contents=[self.PROMPT, image_file],
            )
            raw_text = response.text.strip()

            # JSON 파싱
            return self._parse_response(raw_text)

        except Exception as e:
            return LabelAnalysisResult(
                product_name="",
                brand="",
                serving_size="",
                servings_count=0,
                ingredients=[],
                error=str(e),
            )

    def analyze_label_bytes(self, image_bytes: bytes, mime_type: str = "image/jpeg") -> LabelAnalysisResult:
        """이미지 바이트에서 라벨 분석"""
        import tempfile

        try:
            # 임시 파일로 저장
            with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
                f.write(image_bytes)
                temp_path = f.name

            result = self.analyze_label(temp_path)

            # 임시 파일 삭제
            Path(temp_path).unlink(missing_ok=True)

            return result

        except Exception as e:
            return LabelAnalysisResult(
                product_name="",
                brand="",
                serving_size="",
                servings_count=0,
                ingredients=[],
                error=str(e),
            )

    def _parse_response(self, raw_text: str) -> LabelAnalysisResult:
        """Gemini 응답 파싱"""
        import json

        try:
            # JSON 블록 추출
            json_match = re.search(r"\{[\s\S]*\}", raw_text)
            if not json_match:
                return LabelAnalysisResult(
                    product_name="",
                    brand="",
                    serving_size="",
                    servings_count=0,
                    ingredients=[],
                    raw_text=raw_text,
                    error="No JSON found in response",
                )

            data = json.loads(json_match.group())

            ingredients = []
            for ing in data.get("ingredients", []):
                amount = ing.get("amount")
                if amount is not None:
                    try:
                        amount = Decimal(str(amount))
                    except Exception:
                        amount = None

                ingredients.append(
                    ExtractedIngredient(
                        name=ing.get("name", ""),
                        amount=amount,
                        unit=ing.get("unit", ""),
                        daily_value_percent=ing.get("daily_value_percent"),
                    )
                )

            return LabelAnalysisResult(
                product_name=data.get("product_name", ""),
                brand=data.get("brand", ""),
                serving_size=data.get("serving_size", ""),
                servings_count=int(data.get("servings_count", 0)),
                ingredients=ingredients,
                raw_text=raw_text,
            )

        except json.JSONDecodeError as e:
            return LabelAnalysisResult(
                product_name="",
                brand="",
                serving_size="",
                servings_count=0,
                ingredients=[],
                raw_text=raw_text,
                error=f"JSON parse error: {e}",
            )


# 싱글톤 인스턴스
_vision_service: VisionService | None = None


def get_vision_service() -> VisionService:
    """Vision 서비스 인스턴스 반환"""
    global _vision_service
    if _vision_service is None:
        _vision_service = VisionService()
    return _vision_service


def analyze_supplement_label(image_path: str | Path) -> LabelAnalysisResult:
    """영양제 라벨 분석 (외부 인터페이스)"""
    service = get_vision_service()
    return service.analyze_label(image_path)

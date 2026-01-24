"""
📷 Vision AI Service

Gemini Vision API를 사용한 영양제 라벨 OCR 및 성분 추출.
Strictly Typed with Pydantic & JSON-LD.
"""

import os
import re
from decimal import Decimal
from pathlib import Path

from django.conf import settings
from google import genai
from pydantic import BaseModel, ConfigDict, Field, ValidationError


class ExtractedIngredient(BaseModel):
    """추출된 성분 정보 (Schema.org/NutritionInformation 호환)"""
    model_config = ConfigDict(populate_by_name=True)

    # JSON-LD
    type: str = Field(default="NutritionInformation", alias="@type")
    
    name: str = Field(description="성분명 (예: Vitamin C)")
    amount: Decimal | None = Field(None, description="함량 (숫자만)")
    unit: str = Field("", description="단위 (mg, mcg, g, IU 등)")
    daily_value_percent: int | None = Field(None, description="일일 권장량 퍼센트")


class LabelAnalysisResult(BaseModel):
    """라벨 분석 결과 (JSON-LD)"""
    model_config = ConfigDict(populate_by_name=True)

    # JSON-LD Context
    context: str = Field(default="https://schema.org", alias="@context")
    type: str = Field(default="Product", alias="@type")

    product_name: str = Field("", description="제품명")
    brand: str = Field("", description="브랜드사")
    serving_size: str = Field("", description="1회 섭취량")
    servings_count: int = Field(0, description="총 제공 횟수")
    
    # Nutrition
    ingredients: list[ExtractedIngredient] = Field(default_factory=list, description="영양 성분 목록")
    
    # Meta
    raw_text: str = Field("", exclude=True)
    error: str | None = Field(None, exclude=True)


class VisionService:
    """Gemini Vision 기반 라벨 분석 서비스"""

    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY") or getattr(settings, "GEMINI_API_KEY", None)
        if not api_key:
            raise ValueError("GEMINI_API_KEY not configured")

        self.client = genai.Client(api_key=api_key)
        self.model = "gemini-2.0-flash"

    def _get_prompt(self) -> str:
        return """Analyze this supplement label image and extract nutrition information.

Return a valid JSON-LD object matching this schema:
{
  "@context": "https://schema.org",
  "@type": "Product",
  "product_name": "Product Name",
  "brand": "Brand Name",
  "serving_size": "Serving Size (e.g. 2 Capsules)",
  "servings_count": 30,
  "ingredients": [
    {
      "@type": "NutritionInformation",
      "name": "Vitamin C",
      "amount": 1000,
      "unit": "mg",
      "daily_value_percent": 100
    }
  ]
}

Rules:
1. Extract "product_name" and "brand" accurately.
2. "amount" must be a number. separate "unit" (mg, mcg, IU).
3. If value is missing, use null or 0.
4. Return ONLY JSON."""

    def analyze_label(self, image_path: str | Path) -> LabelAnalysisResult:
        """이미지 파일에서 라벨 분석"""
        try:
            image_path = Path(image_path)
            if not image_path.exists():
                return LabelAnalysisResult(error="Image file not found")

            image_file = self.client.files.upload(file=str(image_path))
            
            from google.genai import types

            response = self.client.models.generate_content(
                model=self.model,
                contents=[self._get_prompt(), image_file],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )
            return self._parse_response(response.text)

        except Exception as e:
            return LabelAnalysisResult(error=str(e))

    def analyze_label_bytes(self, image_bytes: bytes, mime_type: str = "image/jpeg") -> LabelAnalysisResult:
        """이미지 바이트에서 라벨 분석"""
        try:
            from google.genai import types

            response = self.client.models.generate_content(
                model=self.model,
                contents=[
                    self._get_prompt(),
                    types.Part.from_bytes(data=image_bytes, mime_type=mime_type)
                ],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )
            
            if not response.text:
                 return LabelAnalysisResult(error="No text in response")

            return self._parse_response(response.text)

        except Exception as e:
            import traceback
            traceback.print_exc()
            return LabelAnalysisResult(error=f"Analysis failed: {str(e)}")

    def _parse_response(self, raw_text: str) -> LabelAnalysisResult:
        """JSON Response -> Pydantic Model"""
        try:
            # Clean markup if any (though response_mime_type=json usually avoids this)
            cleaned_text = re.sub(r"```json|```", "", raw_text).strip()
            
            # Validate with Pydantic
            result = LabelAnalysisResult.model_validate_json(cleaned_text)
            result.raw_text = raw_text
            return result

        except ValidationError as e:
            return LabelAnalysisResult(
                raw_text=raw_text,
                error=f"Validation Error: {e}"
            )
        except Exception as e:
            return LabelAnalysisResult(
                raw_text=raw_text,
                error=f"Parse Error: {e}"
            )


# 싱글톤
_vision_service: VisionService | None = None


def get_vision_service() -> VisionService:
    global _vision_service
    if _vision_service is None:
        _vision_service = VisionService()
    return _vision_service


def analyze_supplement_label(image_path: str | Path) -> LabelAnalysisResult:
    service = get_vision_service()
    return service.analyze_label(image_path)

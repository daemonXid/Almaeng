
import time
import json
from django.core.management.base import BaseCommand
from django.conf import settings
from domains.features.supplements.models import Supplement
from google import genai
from google.genai import types

class Command(BaseCommand):
    help = "Gemini를 사용하여 영양제 성분 및 효능을 분석하고 태깅합니다."

    def add_arguments(self, parser):
        parser.add_argument(
            "--limit",
            type=int,
            default=10,
            help="분석할 제품 수",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="이미 분석된 제품도 다시 분석",
        )

    def handle(self, *args, **options):
        limit = options["limit"]
        force = options["force"]

        api_key = getattr(settings, "GEMINI_API_KEY", "")
        if not api_key:
            self.stdout.write(self.style.ERROR("❌ GEMINI_API_KEY가 설정되지 않았습니다."))
            return

        client = genai.Client(api_key=api_key)

        if not force:
            qs = Supplement.objects.filter(description="")
        else:
            qs = Supplement.objects.all()
        
        target_products = qs[:limit]
        self.stdout.write(f"📊 분석 대상: {len(target_products)}건")

        # 모델 목록 확인 (디버깅용)
        try:
            self.stdout.write("🔍 Available models:")
            # google-genai SDK의 모델 리스트 조회 방식이 다를 수 있음.
            # 하지만 일단 실행해보고, 안 되면 넘어감.
            # 패키지 문서상 client.models.list() 가 존재함.
            for m in client.models.list():
                if "gemini" in m.name:
                    print(f" - {m.name}")
        except Exception as e:
            self.stdout.write(f"⚠️ 모델 목록 조회 실패: {e}")

        for product in target_products:
            self.stdout.write(f"Analyzing: {product.name}...")

            try:
                prompt = f"""
                You are an expert nutritionist AI. Analyze this supplement product and provide a summary in Korean JSON format.
                
                Product Name: "{product.name}"
                Brand: "{product.brand}"

                Output Format (JSON):
                {{
                    "description": "Write a compelling 1-2 sentence description including emojis. Focus on selling points.",
                    "benefits": ["Benefit 1", "Benefit 2", "Benefit 3"],
                    "target_audience": "Ideally suited for..."
                }}
                """

                response = client.models.generate_content(
                    model='gemini-2.0-flash', # 구체적인 버전 지정
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type='application/json'
                    )
                )
                
                result = json.loads(response.text)
                print(f"[DEBUG] Gemini Result Type: {type(result)}")
                if isinstance(result, list):
                    result = result[0] if result else {}
                
                # DB 업데이트
                product.description = result.get("description", "")
                product.benefits = result.get("benefits", [])
                product.target_audience = result.get("target_audience", "")
                product.save()

                self.stdout.write(self.style.SUCCESS(f"  ✅ Updated: {product.target_audience}"))
                
                # Rate Limiting
                time.sleep(1.0)
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"  ❌ Failed: {e}"))
                import traceback
                traceback.print_exc()

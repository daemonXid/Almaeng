
import asyncio
from asgiref.sync import async_to_sync, sync_to_async
from django.core.management.base import BaseCommand
from django.db import transaction
from domains.features.supplements.models import Supplement
from domains.features.prices.models import PriceHistory
from domains.features.prices.integrations.naver import NaverCrawler

class Command(BaseCommand):
    help = "네이버 쇼핑 인기 제품을 가져와서 Supplement DB를 구축합니다."

    KEYWORDS = [
        "오메가3",
        "알티지 오메가3",
        "비타민C",
        "종합비타민",
        "마그네슘",
        "유산균",
        "프로바이오틱스",
        "밀크씨슬",
        "루테인",
        "콜라겐",
        "비오틴",
    ]

    def add_arguments(self, parser):
        parser.add_argument(
            "--limit",
            type=int,
            default=10,
            help="키워드 당 가져올 제품 수",
        )
        parser.add_argument(
            "--clear",
            action="store_true",
            help="기존 데이터 삭제 후 시작",
        )

    def handle(self, *args, **options):
        limit = options["limit"]
        clear = options["clear"]

        if clear:
            self.stdout.write(self.style.WARNING("🧹 기존 Supplement 및 가격 데이터 초기화..."))
            Supplement.objects.all().delete()
            PriceHistory.objects.all().delete()

        async_to_sync(self.run_import)(limit)

    async def run_import(self, limit):
        crawler = NaverCrawler()
        total_created = 0

        self.stdout.write(self.style.NOTICE("🚀 네이버 인기 영양제 가져오기 시작..."))

        for keyword in self.KEYWORDS:
            self.stdout.write(f"\n🔍 키워드 검색: {keyword}")
            
            try:
                results = await crawler.search(keyword)
                # limit 만큼만 자르기
                results = results[:limit]

                for item in results:
                    # 저장 (Upsert or Create)
                    created = await self.save_product(keyword, item)
                    if created:
                        total_created += 1
                        print(f"  ✅ [추가] {item.product_name[:30]}... ({item.price:,}원)")
                    else:
                        print(f"  🔄 [업뎃] {item.product_name[:30]}...")
                
                # API 보호 딜레이
                await asyncio.sleep(1.0)
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"  ❌ 에러: {e}"))

        self.stdout.write(self.style.SUCCESS(f"\n✨ 총 {total_created}개 신규 제품 등록 완료!"))

    @staticmethod
    @sync_to_async
    def save_product(keyword: str, item) -> bool:
        """
        네이버 상품 정보를 Supplement 모델로 변환하여 저장
        """
        # 1. Supplement 생성/조회 (이름 기준)
        # 네이버 상품명은 보통 "[브랜드] 제품명" 형태가 많음
        # 간단히 파싱 시도
        brand = "기타"
        name = item.product_name
        
        # 이름 앞부분에 브랜드 추정 (대괄호나 띄어쓰기)
        # 예: "[종근당] 락토핏" -> brand: 종근당
        if "]" in name and name.startswith("["):
            parts = name.split("]")
            brand = parts[0].replace("[", "").strip()
            name = parts[1].strip()
        
        supplement, created = Supplement.objects.get_or_create(
            name=item.product_name, # 전체 이름을 고유 키로 사용 (네이버 상품명은 유니크하다고 가정)
            defaults={
                "brand": brand,
                "image_url": item.image_url,
                "serving_size": "상세페이지 참조", # 네이버 API에는 없음
                "servings_per_container": 30,
            }
        )

        # 2. 가격 히스토리 저장
        PriceHistory.objects.create(
            supplement_id=supplement.id,
            platform="naver",
            price=item.price,
            url=item.url,
            is_in_stock=True
        )

        return created

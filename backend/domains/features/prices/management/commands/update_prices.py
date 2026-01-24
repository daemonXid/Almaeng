
import asyncio
import time
from asgiref.sync import async_to_sync
from django.core.management.base import BaseCommand
from django.db.models import Q
from domains.features.supplements.models import Supplement
from domains.features.prices.models import PriceHistory
from domains.features.prices.integrations.naver import NaverCrawler

class Command(BaseCommand):
    help = "네이버 쇼핑 API를 통해 영양제 가격과 이미지를 업데이트합니다."

    def add_arguments(self, parser):
        parser.add_argument(
            "--limit",
            type=int,
            default=10,
            help="업데이트할 최대 제품 수",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="이미지가 이미 있는 제품도 강제 업데이트",
        )

    def handle(self, *args, **options):
        limit = options["limit"]
        force = options["force"]

        self.stdout.write(self.style.NOTICE(f"🔍 가격/이미지 업데이트 시작 (Limit: {limit})..."))

        # 업데이트 대상 조회
        # 이미지가 없거나, 강제 업데이트인 경우
        qs = Supplement.objects.all()
        if not force:
            qs = qs.filter(Q(image_url="") | Q(image_url__isnull=True))
        
        # 최신순으로 가져오거나, 랜덤으로 가져오는 게 좋을 수 있음
        target_products = qs.order_by("-created_at")[:limit]

        if not target_products:
            self.stdout.write("✨ 업데이트할 대상이 없습니다.")
            return

        # 비동기 실행을 위해 async_to_sync 사용
        async_to_sync(self.run_crawlers)(target_products)

        self.stdout.write(self.style.SUCCESS("✅ 업데이트 작업 완료!"))

    async def run_crawlers(self, products):
        crawler = NaverCrawler()
        success_count = 0
        
        self.stdout.write(f"📊 대상 제품: {len(products)}개")

        for product in products:
            # 검색어 정제 로직
            clean_brand = product.brand.replace("(주)", "").replace("주식회사", "").strip()
            clean_name = product.name.replace("(주)", "").replace("주식회사", "").strip()
            
            # 브랜드가 이름에 이미 포함된 경우 중복 제거
            if clean_brand in clean_name:
                keyword = clean_name
            else:
                keyword = f"{clean_brand} {clean_name}"
            
            # 괄호 안의 내용이 너무 길면 제거하는 등 추가 정제 가능하지만 일단 심플하게
            
            self.stdout.write(f"  검색: {keyword[:50]}... (원문: {product.name})")
            
            try:
                # 네이버 검색 (비동기)
                results = await crawler.search(keyword)
                
                if results:
                    best_match = results[0]  # 첫 번째 결과가 가장 정확하다고 가정 (네이버 'sim' 정렬)
                    
                    # 1. 이미지 업데이트
                    if not product.image_url or True: # 항상 최신 이미지로
                        product.image_url = best_match.image_url
                        await prod_save(product) # 비동기 컨텍스트에서 동기 ORM 호출 주의
                    
                    # 2. 가격 히스토리 저장
                    # 동기 ORM 호출을 위해 sync_to_async가 필요하지만, 
                    # 간단하게 여기서는 커맨드 라인이므로 DB 작업은 별도 래퍼 없이 시도 (Django 5.0+ 부터 일부 비동기 지원하지만 안전하게 분리)
                    await self.save_price(product.id, best_match)
                    
                    self.stdout.write(self.style.SUCCESS(f"    -> 찾음: {best_match.price:,}원"))
                    success_count += 1
                else:
                    self.stdout.write(self.style.WARNING("    -> 결과 없음"))
            
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"    ❌ 에러: {e}"))
            
            # API 쿼터 보호를 위한 딜레이
            await asyncio.sleep(0.5)

        self.stdout.write(f"📈 성공률: {success_count}/{len(products)}")

    @staticmethod
    async def save_price(supplement_id, result):
        """비동기 컨텍스트에서 DB 저장"""
        from asgiref.sync import sync_to_async
        
        @sync_to_async
        def _save():
            PriceHistory.objects.create(
                supplement_id=supplement_id,
                platform="naver",
                price=result.price,
                url=result.url,
                is_in_stock=True
            )
        await _save()
        
from asgiref.sync import sync_to_async

@sync_to_async
def prod_save(product):
    product.save()

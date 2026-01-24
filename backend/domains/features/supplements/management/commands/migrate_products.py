
import random
from django.core.management.base import BaseCommand
from django.db import transaction
from domains.features.supplements.models import MFDSHealthFood, Supplement

class Command(BaseCommand):
    help = "식약처 데이터(MFDSHealthFood)를 서비스용 모델(Supplement)로 이관합니다."

    def add_arguments(self, parser):
        parser.add_argument(
            "--limit",
            type=int,
            default=0,
            help="이관할 최대 제품 수 (0 = 전체, 랜덤 샘플링)",
        )
        parser.add_argument(
            "--clear",
            action="store_true",
            help="기존 Supplement 데이터를 모두 삭제하고 시작",
        )

    def handle(self, *args, **options):
        limit = options["limit"]
        clear = options["clear"]

        if clear:
            self.stdout.write(self.style.WARNING("🧹 기존 영양제 데이터 삭제 중..."))
            Supplement.objects.all().delete()

        # 식약처 데이터 조회
        qs = MFDSHealthFood.objects.all()
        total_count = qs.count()
        self.stdout.write(f"📊 식약처 원분 데이터: {total_count}건")

        if limit > 0:
            # 랜덤 샘플링 (ID 리스트 가져와서 셔플)
            all_ids = list(qs.values_list("id", flat=True))
            if len(all_ids) > limit:
                selected_ids = random.sample(all_ids, limit)
                qs = qs.filter(id__in=selected_ids)
                self.stdout.write(f"🎲 랜덤 샘플링: {limit}건 선택됨")

        products_to_create = []
        
        self.stdout.write("🚀 데이터 변환 시작...")
        
        for mfds_item in qs.iterator(chunk_size=1000):
            # 섭취 방법 텍스트 단순화 (예: "1일 1회, 1회 1캡슐을 물과 함께 섭취하십시오." -> "1일 1회, 1회 1캡슐")
            # 복잡하므로 일단 그대로 넣고 나중에 정제
            serving_info = mfds_item.intake_method[:50] 

            products_to_create.append(
                Supplement(
                    name=mfds_item.product_name,
                    brand=mfds_item.company_name,
                    serving_size=serving_info,
                    servings_per_container=30, # 기본값 30 (데이터 없음)
                    image_url="", # 크롤링으로 채움
                )
            )

        # Bulk Create
        with transaction.atomic():
            Supplement.objects.bulk_create(products_to_create, batch_size=1000)

        self.stdout.write(self.style.SUCCESS(f"✅ {len(products_to_create)}건 이관 완료!"))

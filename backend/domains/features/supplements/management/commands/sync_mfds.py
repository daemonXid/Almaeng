"""
🔄 식약처 건강기능식품 데이터 동기화

ETL: Extract → Transform → Load
식약처 API → PostgreSQL (MFDSHealthFood 모델)

Usage:
    python manage.py sync_mfds              # 전체 동기화 (최대 100건씩 배치)
    python manage.py sync_mfds --limit 1000 # 1000건만 동기화
    python manage.py sync_mfds --batch 500  # 500건씩 배치 처리
"""

import time
from datetime import datetime

import httpx
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction

from domains.features.supplements.models import MFDSHealthFood


class Command(BaseCommand):
    help = "식약처 건강기능식품 API 데이터를 PostgreSQL에 동기화합니다."

    def add_arguments(self, parser):
        parser.add_argument(
            "--limit",
            type=int,
            default=0,
            help="동기화할 최대 레코드 수 (0 = 전체)",
        )
        parser.add_argument(
            "--batch",
            type=int,
            default=100,
            help="한 번에 가져올 레코드 수 (API 호출당)",
        )

    def handle(self, *args, **options):
        limit = options["limit"]
        batch_size = options["batch"]

        self.stdout.write(self.style.NOTICE("🔄 식약처 데이터 동기화 시작..."))

        api_key = getattr(settings, "MFDS_API_KEY", "")
        if not api_key:
            self.stdout.write(self.style.ERROR("❌ MFDS_API_KEY가 설정되지 않았습니다."))
            return

        total_synced = self.sync_data(api_key, limit, batch_size)

        self.stdout.write(
            self.style.SUCCESS(f"✅ 동기화 완료! 총 {total_synced}건 처리됨.")
        )

    def sync_data(self, api_key: str, limit: int, batch_size: int) -> int:
        """API에서 데이터를 가져와 DB에 저장 (동기 방식)"""
        total_synced = 0
        start_index = 1
        errors = 0
        base_url = "http://openapi.foodsafetykorea.go.kr/api"

        with httpx.Client(timeout=60.0) as client:
            while True:
                end_index = start_index + batch_size - 1

                self.stdout.write(f"  📥 {start_index}~{end_index} 가져오는 중...")

                # API 호출
                url = f"{base_url}/{api_key}/C003/json/{start_index}/{end_index}"

                try:
                    response = client.get(url)
                    data = response.json()
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"  ❌ API 오류: {e}"))
                    errors += 1
                    if errors > 3:
                        break
                    start_index += batch_size
                    time.sleep(1)
                    continue

                # 응답 파싱
                result_data = data.get("C003", {})
                result_info = result_data.get("RESULT", {})
                result_code = result_info.get("CODE", "")

                if result_code == "INFO-200":
                    self.stdout.write("  📭 더 이상 데이터 없음")
                    break

                rows = result_data.get("row", [])
                if not rows:
                    self.stdout.write("  📭 더 이상 데이터 없음")
                    break

                # Transform & Load
                synced_count = self.save_products(rows)
                total_synced += synced_count

                self.stdout.write(
                    self.style.SUCCESS(f"  ✅ {synced_count}건 저장 (누적: {total_synced})")
                )

                # 다음 배치
                start_index += batch_size

                # 제한 체크
                if limit > 0 and total_synced >= limit:
                    self.stdout.write(f"  📊 제한({limit}건) 도달, 중단")
                    break

                # API 서버 부하 방지를 위한 대기
                time.sleep(0.5)

        return total_synced

    def save_products(self, products: list) -> int:
        """Transform & Load: API 응답을 DB에 저장 (Upsert)"""
        saved_count = 0

        with transaction.atomic():
            for product in products:
                try:
                    # 날짜 변환 (YYYYMMDD → Date)
                    report_date = None
                    prms_dt = product.get("PRMS_DT", "")
                    if prms_dt:
                        try:
                            report_date = datetime.strptime(prms_dt, "%Y%m%d").date()
                        except ValueError:
                            pass

                    license_number = product.get("LCNS_NO", "")
                    if not license_number:
                        continue

                    # Upsert (license_number 기준)
                    MFDSHealthFood.objects.update_or_create(
                        license_number=license_number,
                        defaults={
                            "report_number": product.get("PRDLST_REPORT_NO", "") or "",
                            "product_name": product.get("PRDLST_NM", "") or "",
                            "company_name": product.get("BSSH_NM", "") or "",
                            "report_date": report_date,
                            "expiry_period": product.get("POG_DAYCNT", "") or "",
                            "appearance": product.get("DISPOS", "") or "",
                            "intake_method": product.get("NTK_MTHD", "") or "",
                            "functionality": product.get("PRIMARY_FNCLTY", "") or "",
                            "cautions": product.get("IFTKN_ATNT_MATR_CN", "") or "",
                            "storage_method": product.get("CSTDY_MTHD", "") or "",
                            "shape": product.get("SHAP", "") or "",
                            "standard": product.get("STDR_STND", "") or "",
                            "raw_materials": product.get("RAWMTRL_NM", "") or "",
                            "product_form": product.get("PRDT_SHAP_CD_NM", "") or "",
                        },
                    )
                    saved_count += 1

                except Exception as e:
                    self.stdout.write(self.style.WARNING(f"  ⚠️ 저장 실패: {e}"))
                    continue

        return saved_count

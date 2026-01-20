"""
💊 Supplements Models

영양제 제품과 성분 정보를 저장하는 모델.
"""

from django.db import models


class Supplement(models.Model):
    """영양제 제품 정보"""

    name = models.CharField(max_length=200, verbose_name="제품명")
    brand = models.CharField(max_length=100, verbose_name="브랜드")
    image_url = models.URLField(blank=True, verbose_name="이미지 URL")
    serving_size = models.CharField(max_length=50, verbose_name="1회 섭취량")  # "1정", "2캡슐"
    servings_per_container = models.PositiveIntegerField(default=1, verbose_name="총 섭취횟수")

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "영양제"
        verbose_name_plural = "영양제 목록"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.brand} - {self.name}"


class Ingredient(models.Model):
    """영양제 성분 정보"""

    UNIT_CHOICES = [
        ("mg", "밀리그램"),
        ("mcg", "마이크로그램"),
        ("g", "그램"),
        ("IU", "국제단위"),
        ("CFU", "CFU"),  # 유산균
        ("ml", "밀리리터"),
    ]

    supplement = models.ForeignKey(
        Supplement,
        on_delete=models.CASCADE,
        related_name="ingredients",
        verbose_name="영양제",
    )
    name = models.CharField(max_length=100, verbose_name="성분명")  # "비타민 D3"
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="함량")
    unit = models.CharField(max_length=20, choices=UNIT_CHOICES, verbose_name="단위")
    daily_value_percent = models.DecimalField(
        max_digits=6, decimal_places=2, null=True, blank=True, verbose_name="일일 권장량 %"
    )

    class Meta:
        verbose_name = "성분"
        verbose_name_plural = "성분 목록"
        ordering = ["name"]

    def __str__(self) -> str:
        return f"{self.name} {self.amount}{self.unit}"


class MFDSHealthFood(models.Model):
    """
    식약처 건강기능식품 공식 데이터

    ETL: 식약처 API → PostgreSQL 동기화
    소스: http://openapi.foodsafetykorea.go.kr (C003 서비스)
    """

    # 고유 식별자 (Upsert 키)
    license_number = models.CharField(
        max_length=50, unique=True, db_index=True, verbose_name="인허가번호"
    )  # LCNS_NO
    report_number = models.CharField(
        max_length=100, db_index=True, verbose_name="품목제조번호"
    )  # PRDLST_REPORT_NO

    # 기본 정보
    product_name = models.CharField(
        max_length=500, db_index=True, verbose_name="품목명"
    )  # PRDLST_NM
    company_name = models.CharField(
        max_length=200, db_index=True, verbose_name="업소명"
    )  # BSSH_NM
    report_date = models.DateField(null=True, blank=True, verbose_name="보고일자")  # PRMS_DT

    # 상세 정보
    expiry_period = models.CharField(max_length=100, blank=True, verbose_name="소비기한")  # POG_DAYCNT
    appearance = models.TextField(blank=True, verbose_name="성상")  # DISPOS
    intake_method = models.TextField(blank=True, verbose_name="섭취방법")  # NTK_MTHD
    functionality = models.TextField(blank=True, verbose_name="주된기능성")  # PRIMARY_FNCLTY

    # 주의사항
    cautions = models.TextField(blank=True, verbose_name="섭취시주의사항")  # IFTKN_ATNT_MATR_CN
    storage_method = models.TextField(blank=True, verbose_name="보관방법")  # CSTDY_MTHD

    # 형태 및 규격
    shape = models.CharField(max_length=100, blank=True, verbose_name="형태")  # SHAP
    standard = models.TextField(blank=True, verbose_name="기준규격")  # STDR_STND
    raw_materials = models.TextField(blank=True, verbose_name="원재료")  # RAWMTRL_NM
    product_form = models.CharField(max_length=100, blank=True, verbose_name="제품형태")  # PRDT_SHAP_CD_NM

    # 메타 정보
    synced_at = models.DateTimeField(auto_now=True, verbose_name="동기화 시각")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="생성일")

    class Meta:
        verbose_name = "식약처 건강기능식품"
        verbose_name_plural = "식약처 건강기능식품 목록"
        ordering = ["-synced_at"]
        indexes = [
            models.Index(fields=["product_name"]),
            models.Index(fields=["company_name"]),
            models.Index(fields=["functionality"]),
        ]

    def __str__(self) -> str:
        return f"{self.company_name} - {self.product_name}"


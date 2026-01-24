"""
🏥 MFDS (식약처) API Client

식품의약품안전처 건강기능식품 품목제조신고(원재료) API 클라이언트.
https://foodsafetykorea.go.kr/api/openApiInfo.do
"""

import httpx
from django.conf import settings
from pydantic import BaseModel, ConfigDict, Field


class HealthFoodProduct(BaseModel):
    """건강기능식품 정보 (실제 API 응답 필드)"""
    model_config = ConfigDict(frozen=True)  # Immutable Data Flow 강제

    # 기본 정보
    lcns_no: str = Field("", alias="LCNS_NO")  # 인허가번호
    bssh_nm: str = Field("", alias="BSSH_NM")  # 업소명
    prdlst_report_no: str = Field("", alias="PRDLST_REPORT_NO")  # 품목제조번호
    prdlst_nm: str = Field("", alias="PRDLST_NM")  # 품목명
    prms_dt: str = Field("", alias="PRMS_DT")  # 보고일자

    # 상세 정보
    pog_daycnt: str = Field("", alias="POG_DAYCNT")  # 소비기한
    dispos: str = Field("", alias="DISPOS")  # 성상
    ntk_mthd: str = Field("", alias="NTK_MTHD")  # 섭취방법
    primary_fnclty: str = Field("", alias="PRIMARY_FNCLTY")  # 주된기능성

    # 주의사항
    iftkn_atnt_matr_cn: str = Field("", alias="IFTKN_ATNT_MATR_CN")  # 섭취시주의사항
    cstdy_mthd: str = Field("", alias="CSTDY_MTHD")  # 보관방법

    # 형태 및 규격
    shap: str = Field("", alias="SHAP")  # 형태
    stdr_stnd: str = Field("", alias="STDR_STND")  # 기준규격
    rawmtrl_nm: str = Field("", alias="RAWMTRL_NM")  # 원재료

    # 메타 정보
    cret_dtm: str = Field("", alias="CRET_DTM")  # 최초생성일시
    last_updt_dtm: str = Field("", alias="LAST_UPDT_DTM")  # 최종수정일시
    prdt_shap_cd_nm: str = Field("", alias="PRDT_SHAP_CD_NM")  # 제품형태

    class Config:
        populate_by_name = True


class MFDSSearchResult(BaseModel):
    """식약처 API 검색 결과"""
    model_config = ConfigDict(frozen=True)  # Immutable Data Flow 강제

    success: bool
    products: list[HealthFoodProduct] = []
    total_count: int = 0
    error_message: str = ""
    error_code: str = ""


class MFDSClient:
    """
    식약처 건강기능식품 품목제조신고(원재료) API 클라이언트

    API 문서: http://openapi.foodsafetykorea.go.kr/api/openApiInfo.do
    서비스명: C003 (건강기능식품 품목제조신고 원재료)
    """

    BASE_URL = "http://openapi.foodsafetykorea.go.kr/api"

    def __init__(self):
        self.api_key = getattr(settings, "MFDS_API_KEY", "")

    async def search_products(
        self,
        product_name: str = "",
        company_name: str = "",
        start_index: int = 1,
        end_index: int = 20,
    ) -> MFDSSearchResult:
        """
        건강기능식품 검색

        Args:
            product_name: 품목명 (PRDLST_NM)
            company_name: 업소명 (BSSH_NM)
            start_index: 시작 인덱스
            end_index: 종료 인덱스

        Returns:
            MFDSSearchResult
        """
        if not self.api_key:
            return MFDSSearchResult(
                success=False,
                error_message="MFDS API key not configured",
                error_code="NO_API_KEY",
            )

        # URL 구조: /api/{keyId}/{serviceId}/{dataType}/{startIdx}/{endIdx}
        url = f"{self.BASE_URL}/{self.api_key}/C003/json/{start_index}/{end_index}"

        # 선택적 검색 파라미터 추가
        params = {}
        if product_name:
            params["PRDLST_NM"] = product_name
        if company_name:
            params["BSSH_NM"] = company_name

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.get(url, params=params if params else None)

                if response.status_code == 200:
                    data = response.json()

                    # API 응답 구조 확인
                    result_data = data.get("C003", {})

                    # 결과 코드 확인
                    result_info = result_data.get("RESULT", {})
                    result_code = result_info.get("CODE", "")

                    if result_code == "INFO-000":
                        # 정상 처리
                        total_count = int(result_data.get("total_count", 0))
                        rows = result_data.get("row", [])
                        products = [HealthFoodProduct(**row) for row in rows]

                        return MFDSSearchResult(
                            success=True,
                            products=products,
                            total_count=total_count,
                        )
                    elif result_code == "INFO-200":
                        # 해당하는 데이터가 없습니다
                        return MFDSSearchResult(
                            success=True,
                            products=[],
                            total_count=0,
                        )
                    else:
                        # 기타 에러
                        return MFDSSearchResult(
                            success=False,
                            error_message=result_info.get("MSG", "Unknown error"),
                            error_code=result_code,
                        )
                else:
                    return MFDSSearchResult(
                        success=False,
                        error_message=f"HTTP error: {response.status_code}",
                        error_code=f"HTTP-{response.status_code}",
                    )

        except httpx.TimeoutException:
            return MFDSSearchResult(
                success=False,
                error_message="Request timeout",
                error_code="TIMEOUT",
            )
        except Exception as e:
            return MFDSSearchResult(
                success=False,
                error_message=str(e),
                error_code="EXCEPTION",
            )

    async def get_product_by_report_no(
        self, report_no: str
    ) -> HealthFoodProduct | None:
        """
        품목제조번호로 상세 정보 조회

        Args:
            report_no: 품목제조번호 (PRDLST_REPORT_NO)

        Returns:
            HealthFoodProduct 또는 None
        """
        if not self.api_key:
            return None

        url = f"{self.BASE_URL}/{self.api_key}/C003/json/1/1"
        params = {"PRDLST_REPORT_NO": report_no}

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.get(url, params=params)

                if response.status_code == 200:
                    data = response.json()
                    result_data = data.get("C003", {})
                    rows = result_data.get("row", [])

                    if rows:
                        return HealthFoodProduct(**rows[0])
                return None

        except Exception:
            return None

    async def get_products_by_date_range(
        self,
        start_date: str,
        end_date: str,
        start_index: int = 1,
        end_index: int = 100,
    ) -> MFDSSearchResult:
        """
        변경일자 기준으로 제품 조회

        Args:
            start_date: 시작일 (YYYYMMDD)
            end_date: 종료일 (YYYYMMDD)
            start_index: 시작 인덱스
            end_index: 종료 인덱스

        Returns:
            MFDSSearchResult
        """
        if not self.api_key:
            return MFDSSearchResult(
                success=False,
                error_message="MFDS API key not configured",
                error_code="NO_API_KEY",
            )

        url = f"{self.BASE_URL}/{self.api_key}/C003/json/{start_index}/{end_index}"
        params = {
            "CHNG_DT": f"{start_date}~{end_date}",
        }

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.get(url, params=params)

                if response.status_code == 200:
                    data = response.json()
                    result_data = data.get("C003", {})
                    result_info = result_data.get("RESULT", {})
                    result_code = result_info.get("CODE", "")

                    if result_code in ("INFO-000", ""):
                        total_count = int(result_data.get("total_count", 0))
                        rows = result_data.get("row", [])
                        products = [HealthFoodProduct(**row) for row in rows]

                        return MFDSSearchResult(
                            success=True,
                            products=products,
                            total_count=total_count,
                        )
                    else:
                        return MFDSSearchResult(
                            success=False,
                            error_message=result_info.get("MSG", "Unknown error"),
                            error_code=result_code,
                        )
                else:
                    return MFDSSearchResult(
                        success=False,
                        error_message=f"HTTP error: {response.status_code}",
                        error_code=f"HTTP-{response.status_code}",
                    )

        except Exception as e:
            return MFDSSearchResult(
                success=False,
                error_message=str(e),
                error_code="EXCEPTION",
            )


# Singleton
mfds_client = MFDSClient()

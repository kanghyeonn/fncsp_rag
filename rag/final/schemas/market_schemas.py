from pydantic import BaseModel, Field
from typing import List, Optional

class MarketSource(BaseModel):
    source_name: str | None = Field(
        description="시장 규모 또는 성장률 산출에 사용된 보고서 또는 자료의 명칭입니다."
    )

    issuing_organization: str | None = Field(
        description="시장 규모·성장률을 산출한 기관 또는 조직의 명칭입니다."
    )

    publish_year: int | None = Field(
        description="해당 자료가 발행된 연도입니다."
    )

    key_basis: str | None = Field(
        description=(
            "해당 자료에서 실제로 활용한 핵심 근거입니다. "
            "예: 기준연도 시장 규모, CAGR, 연평균 성장률, 예측 기간 등"
        )
    )

    link_or_id: str | None = Field(
        description="자료를 식별할 수 있는 링크(URL) 또는 문서 식별 정보입니다."
    )

class MarketForecast(BaseModel):
    currency: str | None = Field(
        description="시장 규모 산출에 사용된 통화입니다. 예: USD, KRW"
    )

    unit: str | None = Field(
        description="시장 규모 수치의 단위입니다. 예: million(백만), hundred_million(억원)"
    )

    years: List[int | None] = Field(
        description=(
            "외부 근거 자료에 명시된 예측 연도 목록입니다. "
            "반드시 연속될 필요는 없으며, 근거에 존재하는 연도만 포함합니다. "
            "최대 5개 연도까지 허용됩니다."
        )
    )

    values_int: List[int | None] = Field(
        description=(
            "각 연도별 시장 규모 예측치입니다. "
            "그래프 활용을 위해 반드시 정수(INT) 값만 사용합니다. "
            "years와 동일한 순서 및 길이를 가져야 합니다."
        )
    )

    method: str | None = Field(
        description=(
            "시장 규모 산출 방식입니다. "
            "예: '직접 인용', 'CAGR 기반 산출', '근거 부족'"
        )
    )

    sources: Optional[List[MarketSource]] = Field(
        description=(
            "시장 규모 예측에 사용된 외부 근거 자료 목록입니다. "
            "근거가 없는 경우 빈 리스트 또는 생략이 가능합니다."
        ),
        default=None
    )

class CompetitorSource(BaseModel):
    source_name: str | None = Field(
        description="경쟁사 정보를 확인한 출처의 명칭입니다."
    )

    publish_year: int | None = Field(
        description="해당 정보가 확인된 연도입니다."
    )

    link_or_id: str | None = Field(
        description=
            "검색 결과(grounding_chunks)에서 확인된 실제 URI입니다. "
            "만약 정확한 URI를 특정할 수 없다면 절대 임의로 생성하지 말고, "
            "대신 소스의 'title' 값만 적으세요. 가짜 URL 생성 시 오류로 간주됩니다."
    )

class CompetitorInfo(BaseModel):
    name: str | None = Field(
        description="유사한 제품 또는 서비스를 제공하는 경쟁사 명칭입니다."
    )

    country: str | None = Field(
        description="경쟁사가 주로 사업을 영위하는 국가 또는 권역입니다."
    )

    similarity_reason: str | None = Field(
        description=(
            "해당 경쟁사가 분석 대상 사업아이템 또는 사업서비스와 "
            "유사하다고 판단한 이유입니다. "
            "기능, 고객, 가치제안 관점에서 서술합니다."
        )
    )

    product_service_summary: str | None = Field(
        description="경쟁사의 제품 또는 서비스를 한 문장으로 요약한 설명입니다."
    )

    business_model: List[str | None] = Field(
        description="경쟁사의 주요 수익 모델입니다. 예: 광고, 구독, 중개수수료 등"
    )

    sources: List[CompetitorSource] = Field(
        description="경쟁사 정보의 근거가 되는 외부 출처 목록입니다."
    )

class MarketForecastAndCompetitors(BaseModel):
    overseas_market: MarketForecast | None = Field(
        description="외부 검색 근거 기반 해외 시장 규모 예측 결과입니다."
    )

    korea_market: MarketForecast | None = Field(
        description="외부 검색 근거 기반 국내 시장 규모 예측 결과입니다."
    )

    competitors: List[CompetitorInfo] | None = Field(
        description=(
            "사업계획서의 사업아이템 또는 사업서비스와 "
            "유사한 제품·서비스를 제공하는 경쟁사 정보 목록입니다."
        )
    )
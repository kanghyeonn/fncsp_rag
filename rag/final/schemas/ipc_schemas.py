from pydantic import BaseModel, Field
from typing import List, Optional

class IPCAnalysisItem(BaseModel):
    ipc_code: str = Field(
        description="국제특허분류(IPC) 코드 (예: G06Q50/16)"
    )
    ipc_name: str = Field(
        description="해당 IPC의 공식 분류 명칭"
    )
    linked_business_function: str = Field(
        description="사업계획서에 명시된 사업 서비스 또는 사업아이템의 기능 요약"
    )
    justification: str = Field(
        description=(
            "사업계획서 문구에 기반하여, "
            "해당 기능이 이 IPC에 포함되는 이유를 설명한 근거 문장"
        )
    )


class IPCAnalysisResult(BaseModel):
    ipc_analysis: List[IPCAnalysisItem] = Field(
        description="사업계획서의 사업 서비스/아이템과 연관성이 높은 IPC 분석 결과 목록"
    )

class YearSeries(BaseModel):
    years: List[int] = Field(..., description="Sorted years")
    values_int: List[int] = Field(..., description="Counts per year (aligned with years)")

class KiprisYearAggregates(BaseModel):
    application: YearSeries
    publication: YearSeries
    registration: YearSeries


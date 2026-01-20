from typing import Dict, Any, Optional
from rag.config import EMBEDDING_MODEL
from rag.final.cache_manager import get_or_create_cache_vf
from rag.final.prompts.marketing_prompt import MARKETING_PROMPT
from rag.final.queries import ITEM_DEFINITIONS
from rag.final.retriever import retrieve_context

from rag.final.generator import (
    generate_report_item_from_vectordb,
    generate_report_item_from_file,
    generate_report_item_from_googlesearch,
    generate_ipc_from_file_and_vectordb, generate_report_item_from_vf_cache
)

from rag.final.collectors.kipris_client import download_statistics_data_from_kipris
from rag.final.collectors.kipris_parser import run_kipris_pipeline, KIPRIS_DIR
from rag.final.prompts.future_prompt import FUTURE_PROMPT
from rag.final.prompts.ip_prompt import IP_PROMPT
from rag.final.prompts.market_prompt import MARKET_PROMPT
from rag.final.prompts.bm_prompt import BM_PROMPT

import time

def _resolve_source(
    item_id: int,
    item_source_map: dict[int, str] | None,
    default_source: str = "vectordb",
) -> str:
    if item_id == 3:
        return "googlesearch"  # 시장/경쟁은 고정
    if item_source_map and item_id in item_source_map:
        return item_source_map[item_id]
    return default_source

# =========================================================
# item_id 기준 generator 선택
# =========================================================

def _generate_by_item(
    item_id: int,
    company: str,
    title: str,
    task: str,
    context_blocks: list,
    source: str,
    business_plan_pdf: Optional[str],
):
    # IP 대응역량 + IPC/KIPRIS 파이프라인
    if item_id == 2 and source == "ipc+kipris":
        if not business_plan_pdf:
            raise ValueError("ipc+kipris source requires business_plan_pdf")

        ipc_result = run_ipc_kipris_pipeline(
            business_plan_pdf=business_plan_pdf,
            context_blocks=context_blocks
        )

        return {
            "title": title,
            "content": ipc_result,
        }

    # 시장 규모 / 경쟁사 → Google Search 전용
    if source == "googlesearch":
        result = generate_report_item_from_googlesearch(
            company=company,
            title=title,
            task=task,
            context_blocks=context_blocks,
            file_path=business_plan_pdf,
        )

        if title == "비즈니스 모델 역량진단":
            return {
                "title": title,
                "content": result.evaluation,
            }

        return {
            "title": title,
            "content": result["parsed"].model_dump(),
            "grounding": result["grounding"],
        }

    # 구조 분석 계열
    if source == "vectordb":
        r = generate_report_item_from_vectordb(
            company=company,
            title=title,
            task=task,
            context_blocks=context_blocks,
        )
        return {"title": title, "content": r.evaluation}

    if source == "file":
        if not business_plan_pdf:
            raise ValueError("file source requires business_plan_pdf")
        r = generate_report_item_from_file(
            company=company,
            title=title,
            task=task,
            file_path=business_plan_pdf,
        )
        return {"title": title, "content": r.evaluation}

    if source == "file+vectordb":
        if not business_plan_pdf:
            raise ValueError("file+vectordb source requires business_plan_pdf")

        cache_vf_id = get_or_create_cache_vf(
            company=company,
            business_plan_pdf=business_plan_pdf,
        )

        r = generate_report_item_from_vf_cache(
            company=company,
            title=title,
            task=task,
            context_blocks=context_blocks,
            cache_vf_id=cache_vf_id,
        )
        return {"title": title, "content": r.evaluation}

    raise ValueError(f"Unsupported source: {source}")

# =========================================================
# 키워드 생성 유틸
# =========================================================
def build_kipris_ipc_keyword(ipc_items) -> str:
    """
    IPCAnalysisItem 리스트 → KIPRIS용 IPC 검색 문자열 생성
    예: G06Q50/16*G06T19/00*G06Q10/06
    """
    ipc_codes = []

    for item in ipc_items:
        # 공백 제거 (G06Q 50/16 → G06Q50/16)
        normalized = item.ipc_code.replace(" ", "")
        ipc_codes.append(normalized)

    return "*".join(ipc_codes)

# =========================================================
# 특허 통계데이터
# =========================================================
def run_ipc_kipris_pipeline(
    business_plan_pdf: str,
    context_blocks: list
):
    """
    사업계획서 → IPC 1개 도출 → IPC OR 검색으로 KIPRIS 통계 수집
    """

    # 1. IPC 분석
    ipc_result = generate_ipc_from_file_and_vectordb(
        file_path=business_plan_pdf,
        context_blocks=context_blocks
    )

    # 2. IPC 키워드 하나로 결합
    ipc_keyword = build_kipris_ipc_keyword(
        ipc_result.ipc_analysis
    )

    # 예: G06Q50/16*G06T19/00*G06Q10/06
    print(f"KIPRIS IPC 검색 키워드: {ipc_keyword}")

    # 3. KIPRIS 통계 엑셀 다운로드 (딱 한 번)
    download_statistics_data_from_kipris(
        download_dir=str(KIPRIS_DIR),
        keyword=ipc_keyword,
    )
    time.sleep(3)
    # 4. 엑셀 정규화
    aggregates = run_kipris_pipeline()

    return {
        "ipc_analysis": [item.model_dump() for item in ipc_result.ipc_analysis],
        "statistics": aggregates.model_dump(),
    }

# =========================================================
# 항목별 프롬포트 매칭 MAP
# =========================================================
PROMPT_MAP = {
    "미래기술대응역량" : FUTURE_PROMPT,
    "IP 대응역량" : IP_PROMPT,
    "시장 규모 예측치 및 경쟁사" : MARKET_PROMPT,
    "비즈니스 모델 역량진단" : BM_PROMPT,
    "마케팅 역량진단" : MARKETING_PROMPT
}

# =========================================================
# 단일 엔트리포인트
# =========================================================

def generate(
    company: str,
    item_source_map: dict[int, str] | None = None,
    business_plan_pdf: Optional[str] = None,
    item_range: Optional[tuple[int, int]] = None,
) -> Dict[int, Any]:

    results: Dict[int, Any] = {}

    start, end = item_range or (1, len(ITEM_DEFINITIONS))

    for item_id in range(start, end + 1):
        item = ITEM_DEFINITIONS[item_id]

        print(f"\n{'=' * 60}")
        print(f"Processing Item {item_id}: {item['title']}")
        print(f"{'=' * 60}")

        # 1. query → embedding
        query = item["query"].format(company=company)
        query_vec = EMBEDDING_MODEL.embed_query(query)

        # 2. retrieve context
        context_blocks = retrieve_context(
            query_vec=query_vec,
            company=company,
            sections=item["sections"],
        )

        # 3. generate
        try:
            resolved_source = _resolve_source(
                item_id=item_id,
                item_source_map=item_source_map,
            )

            task_prompt = PROMPT_MAP.get(item["title"])

            output = _generate_by_item(
                item_id=item_id,
                source=resolved_source,
                company=company,
                title=item["title"],
                task=task_prompt,
                context_blocks=context_blocks,
                business_plan_pdf=business_plan_pdf,
            )
            results[item_id] = output
            print(f"✅ Item {item_id} completed")

        except Exception as e:
            results[item_id] = {
                "title": item["title"],
                "error": True,
                "message": str(e),
                "content": None,
            }
            print(f"❌ Item {item_id} failed: {e}")

    return results



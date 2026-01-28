import json
import time
from pathlib import Path
from typing import Optional, Callable, TypeVar

from google.genai.types import Tool, GenerateContentConfig, GoogleSearch
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from rag.final.prompts.ipc_prompt import IPC_PROMPT
from rag.final.prompts.strict_instruction import STRICT_JSON_INSTRUCTION
from rag.final.schemas.ipc_schemas import IPCAnalysisResult
from rag.config import LLM_A, GEMINI_CLIENT
from rag.final.utils import clean_json_string, has_valid_market_size, expand_market_keywords, guess_base_market
from rag.final.schemas.base_schemas import ReportItemResult
from rag.final.schemas.market_schemas import MarketForecastAndCompetitors
from rag.final.prompts.base_prompt import (
    VECTORDB_BASE_PROMPT,
    FILE_BASE_PROMPT,
    VECTORDB_AND_FILE_BASE_PROMPT,
    GOOGLE_SEARCH_BASE_PROMPT,
)

# =========================================================
# 공통 유틸
# =========================================================
T = TypeVar("T")

def retry_llm_call(
    fn: Callable[[int], T],
    max_retry: int = 3,
    sleep_sec: float = 1.0,
    error_prefix: str = "LLM 처리 실패"
) -> T:
    last_error: Exception | None = None

    for attempt in range(1, max_retry + 1):
        try:
            return fn(attempt)
        except Exception as e:
            last_error = e
            if attempt < max_retry:
                print(f"⚠️ {error_prefix} (시도 {attempt}/{max_retry}) → 재시도")
                time.sleep(sleep_sec)
            else:
                print(f"❌ {error_prefix} (최대 재시도 초과)")
                raise RuntimeError(
                    f"{error_prefix}: {e}"
                ) from e

    raise last_error

def _build_context_text(context_blocks: list, with_similarity: bool = False) -> str:
    if not context_blocks:
        return ""

    if with_similarity:
        return "\n\n".join(
            f"[{c['section']} | sim={c['similarity']}]\n{c['content']}"
            for c in context_blocks
        )
    return "\n\n".join(
        f"[{c['section']}]\n{c['content']}"
        for c in context_blocks
    )


def _parse_llm_json(
    raw_text: str,
    model_cls
):
    cleaned = clean_json_string(raw_text)
    parsed = json.loads(cleaned)
    return model_cls.model_validate(parsed)


def _invoke_langchain(
    prompt: PromptTemplate,
    llm,
    inputs: dict,
    model_cls
):
    def _call(attempt: int):
        final_inputs = dict(inputs)

        if attempt >= 2:
            final_inputs["task"] += (
                "\n\n"
                + STRICT_JSON_INSTRUCTION
            )

        response = (prompt | llm).invoke(final_inputs)
        raw_text = response.content if hasattr(response, "content") else str(response)
        return _parse_llm_json(raw_text, model_cls)

    return retry_llm_call(
        fn=_call,
        max_retry=3,
        sleep_sec=1.0,
        error_prefix="LangChain LLM 처리 실패"
    )


def _invoke_gemini(
    prompt_text: str,
    model_cls,
    file: Optional[Path] = None,
    use_google_search: bool = False
):
    def _call(attempt: int):
        final_prompt = prompt_text

        if attempt >= 2:
            final_prompt = (
                prompt_text
                + "\n\n"
                + STRICT_JSON_INSTRUCTION
            )

        contents = [final_prompt]
        if file:
            uploaded = GEMINI_CLIENT.files.upload(file=file)
            contents = [uploaded, final_prompt]

        config = None
        if use_google_search:
            config = GenerateContentConfig(
                tools=[Tool(google_search=GoogleSearch())]
            )

        response = GEMINI_CLIENT.models.generate_content(
            model="gemini-2.5-flash",
            contents=contents,
            config=config,
        )

        candidate = response.candidates[0]
        text = candidate.content.parts[0].text
        parsed = _parse_llm_json(text, model_cls)

        return parsed, candidate.grounding_metadata if use_google_search else None

    return retry_llm_call(
        fn=_call,
        max_retry=3,
        sleep_sec=1.5,
        error_prefix="Gemini 처리 실패"
    )

def _invoke_gemini_with_cache(
    cache_id: str,
    prompt_text: str,
    model_cls,
):
    def _call(attempt: int):
        final_prompt = prompt_text

        if attempt >= 2:
            final_prompt = (
                prompt_text
                + "\n\n"
                + STRICT_JSON_INSTRUCTION
            )

        response = GEMINI_CLIENT.models.generate_content(
            model="gemini-2.5-flash",
            contents=final_prompt,
            config=GenerateContentConfig(
                cached_content=cache_id,
            ),
        )

        candidate = response.candidates[0]
        text = candidate.content.parts[0].text
        return _parse_llm_json(text, model_cls)

    return retry_llm_call(
        fn=_call,
        max_retry=3,
        sleep_sec=1.5,
        error_prefix="Gemini(Cache) 처리 실패"
    )


# =========================================================
# IPC (사업계획서 기반 IPC 분석)
# =========================================================

def generate_ipc_from_business_plan(
    file_path: str,
) -> IPCAnalysisResult:
    """
    사업계획서 파일을 기반으로 IPC를 생성한다.
    """

    parser = JsonOutputParser(pydantic_object=IPCAnalysisResult)

    prompt = PromptTemplate(
        template=IPC_PROMPT,
        input_variables=[],  # 파일 기반 분석 → 변수 없음
        partial_variables={
            "format_instructions": parser.get_format_instructions()
        },
    )

    prompt_text = prompt.format()

    parsed, _ = _invoke_gemini(
        prompt_text=prompt_text,
        model_cls=IPCAnalysisResult,
        file=Path(file_path),
    )
    print(parsed)

    return parsed


# =========================================================
# IPC (벡터 디비 + 사업계획서 기반 IPC 분석)
# =========================================================
def generate_ipc_from_file_and_vectordb(
    file_path: str,
    context_blocks: list,
) -> IPCAnalysisResult:
    parser = JsonOutputParser(pydantic_object=IPCAnalysisResult)

    context_text = _build_context_text(context_blocks, with_similarity=True)

    prompt = PromptTemplate(
        template=IPC_PROMPT,
        input_variables=["context"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )

    prompt_text = prompt.format(context=context_text)

    parsed, _ = _invoke_gemini(
        prompt_text=prompt_text,
        model_cls=IPCAnalysisResult,
        file=Path(file_path),   # 보조 확인용
    )
    return parsed

# =========================================================
# Vector DB
# =========================================================

def generate_report_item_from_vectordb(
    company: str,
    title: str,
    task: str,
    context_blocks: list
) -> ReportItemResult:

    context_text = _build_context_text(context_blocks, with_similarity=True)

    parser = JsonOutputParser(pydantic_object=ReportItemResult)
    prompt = PromptTemplate(
        template=VECTORDB_BASE_PROMPT,
        input_variables=["company", "title", "task", "context"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )

    return _invoke_langchain(
        prompt=prompt,
        llm=LLM_A,
        inputs={
            "company": company,
            "title": title,
            "task": task,
            "context": context_text,
        },
        model_cls=ReportItemResult,
    )


# =========================================================
# File
# =========================================================

def generate_report_item_from_file(
    company: str,
    title: str,
    task: str,
    file_path: str
) -> ReportItemResult:

    parser = JsonOutputParser(pydantic_object=ReportItemResult)
    prompt = PromptTemplate(
        template=FILE_BASE_PROMPT,
        input_variables=["company", "title", "task"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )

    prompt_text = prompt.format(company=company, title=title, task=task)

    parsed, _ = _invoke_gemini(
        prompt_text=prompt_text,
        model_cls=ReportItemResult,
        file=Path(file_path),
    )
    return parsed


# =========================================================
# File + Vector DB
# =========================================================

def generate_report_item_from_file_and_vectordb(
    company: str,
    title: str,
    task: str,
    context_blocks: list,
    file_path: str
) -> ReportItemResult:

    context_text = _build_context_text(context_blocks, with_similarity=True)

    parser = JsonOutputParser(pydantic_object=ReportItemResult)
    prompt = PromptTemplate(
        template=VECTORDB_AND_FILE_BASE_PROMPT,
        input_variables=["company", "title", "task", "context"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )

    prompt_text = prompt.format(
        company=company,
        title=title,
        task=task,
        context=context_text,
    )

    parsed, _ = _invoke_gemini(
        prompt_text=prompt_text,
        model_cls=ReportItemResult,
        file=Path(file_path),
    )
    return parsed


# =========================================================
# Google Search (Market 전용 - 시장 규모 및 경쟁사 분석)
# =========================================================

def generate_report_item_from_googlesearch(
    company: str,
    title: str,
    task: str,
    context_blocks: list,
    file_path: str | None = None,
):
    context_text = _build_context_text(context_blocks)

    parser = JsonOutputParser(pydantic_object=MarketForecastAndCompetitors)

    if title == "비즈니스 모델 역량진단":
        parser = JsonOutputParser(pydantic_object=ReportItemResult)

    prompt = PromptTemplate(
        template=GOOGLE_SEARCH_BASE_PROMPT,
        input_variables=["company", "title", "task", "context"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )

    prompt_text = prompt.format(
        company=company,
        title=title,
        task=task,
        context=context_text,
    )

    if title == "비즈니스 모델 역량진단":
        parsed, _ = _invoke_gemini(
            prompt_text=prompt_text,
            model_cls=ReportItemResult,
            use_google_search=True,
            file=Path(file_path),
        )
        return parsed

    parsed, grounding = _invoke_gemini(
        prompt_text=prompt_text,
        model_cls=MarketForecastAndCompetitors,
        use_google_search=True,
        file=Path(file_path) if file_path else None,
    )

    return {
        "parsed": parsed,
        "grounding": grounding.to_json_dict() if grounding else None,
    }

def generate_market_with_fallback(
    company: str,
    title: str,
    task: str,
    context_blocks: list,
    file_path: str | None = None,
    max_level: int = 3,
):
    base_market = guess_base_market(context_blocks)  # 또는 context에서 추출한 시장명
    print("-" * 15)
    print("Base market : ", base_market)
    print("-" * 15)


    for level in range(max_level + 1):
        expanded_task = (
            task
            + f"\n\n[시장 범위]\n{expand_market_keywords(base_market, level)}"
        )

        result = generate_report_item_from_googlesearch(
            company=company,
            title=title,
            task=expanded_task,
            context_blocks=context_blocks,
            file_path=file_path,
        )

        parsed = result["parsed"]

        if (
            has_valid_market_size(parsed.overseas_market)
            or has_valid_market_size(parsed.korea_market)
        ):
            parsed.overseas_market.method = (
                parsed.overseas_market.method
                + f" (상위 시장 레벨 {level} 적용)"
                if parsed.overseas_market and parsed.overseas_market.method
                else None
            )
            return result

    # 전부 실패 시 → null 유지 (프롬프트 규칙 준수)
    return result


# =========================================================
# Cache + File + Vector DB
# =========================================================
def generate_report_item_from_vf_cache(
        company: str,
        title: str,
        task: str,
        context_blocks: list,
        cache_vf_id: str,
) -> ReportItemResult:

    context_text = _build_context_text(context_blocks, with_similarity=True)

    parser = JsonOutputParser(pydantic_object=ReportItemResult)

    prompt = PromptTemplate(
        template=VECTORDB_AND_FILE_BASE_PROMPT,
        input_variables=["company", "title", "task", "context"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )

    prompt_text = prompt.format(
        company=company,
        title=title,
        task=task,
        context=context_text,
    )

    return _invoke_gemini_with_cache(
        cache_id=cache_vf_id,
        prompt_text=prompt_text,
        model_cls=ReportItemResult,
    )
from typing import Dict
from google.genai import types
from pathlib import Path
import hashlib

from rag.config import GEMINI_CLIENT
from rag.final.prompts.cache_system_prompt import VF_CACHE_SYSTEM_PROMPT

# -----------------------------
# 메모리 캐시 저장소
# -----------------------------
# key: cache_key
# value: cache_id (cachedContents/xxxx)
_VF_CACHE_STORE: Dict[str, str] = {}

def _calc_file_hash(file_path: str) -> str:
    h = hashlib.sha256()
    with open(file_path, "rb") as f:
        h.update(f.read())
        return h.hexdigest()

def _build_cache_key(
        company: str,
        file_hash: str,
        prompt_version: str,
) -> str:
    return f"vf:{company}:{file_hash}:{prompt_version}"

def get_or_create_cache_vf(
        company: str,
        business_plan_pdf: str,
        prompt_version: str = "v1",
) -> str:
    """
    VF (미래기술 / BM / 마케팅) 공통 캐시를
    메모리에서 찾거나 없으면 새로 생성한다.
    """
    file_hash = _calc_file_hash(business_plan_pdf)
    cache_key = _build_cache_key(company, file_hash, prompt_version)

    cache_id = _VF_CACHE_STORE.get(cache_key)
    if cache_id:
        print(f"[VF CACHE HIT] {cache_key} -> {cache_id}")
        return cache_id

    print(f"[VF CACHE MISS] {cache_key} (creating new cache)")

    uploaded_pdf = GEMINI_CLIENT.files.upload(
        file=Path(business_plan_pdf),
    )

    cache = GEMINI_CLIENT.caches.create(
        model="gemini-2.5-flash",
        config=types.CreateCachedContentConfig(
            system_instruction=VF_CACHE_SYSTEM_PROMPT,
            contents=[uploaded_pdf],
        ),
    )

    _VF_CACHE_STORE[cache_key] = cache.name

    return cache.name

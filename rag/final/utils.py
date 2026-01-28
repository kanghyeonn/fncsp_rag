import re

def clean_json_string(text: str) -> str:
    # 코드블록 제거
    text = re.sub(r'```json\s*', '', text)
    text = re.sub(r'```\s*', '', text)

    # 스마트 따옴표 정규화
    text = (
        text.replace("“", '"')
            .replace("”", '"')
            .replace("‘", "'")
            .replace("’", "'")
    )

    # 잘못된 escape 제거
    text = text.replace("\\'", "'")

    # 공백 정리
    text = text.strip()

    # JSON 범위 추출
    start = text.find('{')
    end = text.rfind('}')
    if start != -1 and end != -1:
        text = text[start:end + 1]

    # evaluation 내부만 안전하게 처리
    def sanitize_evaluation(match):
        content = match.group(1)
        content = content.replace('"', '\\"')
        content = content.replace("\r\n", "\\n").replace("\n", "\\n")
        return f'"evaluation": "{content}"'

    text = re.sub(
        r'"evaluation"\s*:\s*"(.+?)"\s*}',
        sanitize_evaluation,
        text,
        flags=re.DOTALL
    )

    if text.strip().startswith("{") and not text.strip().endswith("}"):
        text = text.rstrip() + "\n}"

    return text


def expand_market_keywords(base_market: str, level: int) -> str:
    """
    level 0: 원래 시장
    level 1: 기술 단위 시장
    level 2: 산업 단위 시장
    level 3: 최상위 시장
    """
    expansions = {
        0: base_market,
        1: f"{base_market} 관련 기술 시장",
        2: f"{base_market} 산업 시장",
        3: f"{base_market} 전체 산업"
    }
    return expansions.get(level, base_market)

def has_valid_market_size(market) -> bool:
    if not market:
        return False
    if not market.years or not market.values_int:
        return False
    if all(v is None for v in market.values_int):
        return False
    return True

def guess_base_market(context_blocks: list) -> str:
    if not context_blocks:
        return "해당 산업"

    for c in context_blocks:
        if c["section"] in ("핵심 키워드", "창업아이템 소개"):
            return c["content"][:80].replace("\n", " ")

    return context_blocks[0]["content"][:80]

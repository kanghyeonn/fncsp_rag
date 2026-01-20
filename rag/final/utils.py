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
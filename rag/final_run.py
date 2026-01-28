from datetime import datetime
from typing import Dict
from pathlib import Path
from rag.mysql.config import MYSQL_CONFIG
from rag.mysql.mysql import fetch_cmp_list
import json

from rag.final.pipeline import generate

# 보고서 저장 디렉토리
REPORTS_DIR = Path("reports")
REPORTS_DIR.mkdir(exist_ok=True)


def _get_safe_filename(company: str, section: str) -> str:
    def _sanitize(text: str) -> str:
        return "".join(
            c if c.isalnum() or c in (" ", "_", "-") else "_"
            for c in text
        ).strip().replace(" ", "_")

    safe_company = _sanitize(company)
    safe_section = _sanitize(section)

    return f"{safe_company}_{safe_section}.json"


def save_report_to_json(company: str, results: Dict) -> list[str]:
    """
    item별로 JSON 파일 저장
    회사명_섹션명.json
    """

    saved_files = []

    for item_id, item in results.items():
        section_title = item["title"]
        filename = _get_safe_filename(company, section_title)
        filepath = REPORTS_DIR / filename

        report_data = {
            "metadata": {
                "company": company,
                "item_id": item_id,
                "section": section_title,
                "created_at": datetime.now().isoformat(),
                "filename": filename,
            },
            "content": item["content"],
        }

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)

        print(f"✅ Saved: {filepath}")
        saved_files.append(str(filepath))

    return saved_files


if __name__ == "__main__":

    biz_no = ""
    company = fetch_cmp_list(MYSQL_CONFIG, biz_no)[0].get("CMP_NM")

    # ✅ 단일 파이프라인 호출
    report = generate(
        company=company,
        biz_no=biz_no,
        item_source_map={
            1: "file+vectordb",  # 미래기술대응역량
            2: "ipc+kipris",  # IP 대응역량
            # 3은 자동 googlesearch # 시장 규모 및 경쟁사 분석
            4: "file+vectordb", # BM 역량
            5: "file+vectordb" # 마케팅 역량
        },         # vectordb | file | file+vectordb
        business_plan_pdf=r"C:\workspace\fncsp_rag\rag\business_plan\5\DIC2025_5.pdf",  # 필요 없으면 None
        item_range=(2, 2),
    )

    filepath = save_report_to_json(company, report)

    print(f"\n{'=' * 60}")
    print(filepath)
    print(f"{'=' * 60}")

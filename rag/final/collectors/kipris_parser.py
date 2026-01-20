import zipfile
import re
import shutil
from pathlib import Path
from lxml import etree
from collections import defaultdict
from typing import Optional, Tuple
import pandas as pd

from rag.final.schemas.ipc_schemas import (
    KiprisYearAggregates,
    YearSeries,
)

# ================================
# 설정
# ================================
KIPRIS_DIR = Path(r"/rag/ipc_statistics")

YEAR_COUNT_PATTERN = re.compile(r"(19\d{2}|20\d{2})\((\d+)\)")


# ================================
# 유틸
# ================================
def _parse_year_count(cell: object) -> Tuple[Optional[int], Optional[int]]:
    if cell is None:
        return None, None

    m = YEAR_COUNT_PATTERN.search(str(cell))
    if not m:
        return None, None

    return int(m.group(1)), int(m.group(2))


def cleanup_directory(dir_path: Path) -> None:
    """
    폴더 내 파일 전부 삭제 후 폴더 재생성
    (엑셀만 존재한다는 전제)
    """
    shutil.rmtree(dir_path)
    dir_path.mkdir(parents=True, exist_ok=True)


# ================================
# XLSX 파싱 (KIPRIS 전용)
# ================================
def read_kipris_excel_values(xlsx_path: Path) -> pd.DataFrame:
    with zipfile.ZipFile(xlsx_path, "r") as z:
        shared_strings = []

        if "xl/sharedStrings.xml" in z.namelist():
            sst_root = etree.fromstring(z.read("xl/sharedStrings.xml"))
            shared_strings = [
                "".join(si.itertext())
                for si in sst_root.findall(".//{*}si")
            ]

        sheet_root = etree.fromstring(z.read("xl/worksheets/sheet1.xml"))

        rows = []
        for row in sheet_root.findall(".//{*}row"):
            values = []
            for c in row.findall("{*}c"):
                v = c.find("{*}v")
                if v is None:
                    values.append(None)
                elif c.get("t") == "s":
                    values.append(shared_strings[int(v.text)])
                else:
                    values.append(v.text)
            rows.append(values)

    if not rows:
        return pd.DataFrame()

    return pd.DataFrame(rows[1:], columns=rows[0])


# ================================
# 연도별 집계
# ================================
def build_year_series_from_column(df: pd.DataFrame, col_name: str) -> YearSeries:
    year_sum = defaultdict(int)

    if col_name not in df.columns:
        return YearSeries(years=[], values_int=[])

    for cell in df[col_name]:
        year, cnt = _parse_year_count(cell)
        if year is None or cnt is None:
            continue
        year_sum[year] += cnt

    years = sorted(year_sum.keys())
    values = [year_sum[y] for y in years]

    return YearSeries(years=years, values_int=values)


def build_kipris_year_aggregates(xlsx_path: Path) -> KiprisYearAggregates:
    df = read_kipris_excel_values(xlsx_path)

    return KiprisYearAggregates(
        application=build_year_series_from_column(df, "출원년도"),
        publication=build_year_series_from_column(df, "공개년도"),
        registration=build_year_series_from_column(df, "등록년도"),
    )


# ================================
# 메인 실행 로직
# ================================
def run_kipris_pipeline() -> KiprisYearAggregates:
    excel_files = list(KIPRIS_DIR.glob("*.xlsx"))

    if not excel_files:
        raise FileNotFoundError("KIPRIS 엑셀 파일이 존재하지 않습니다.")

    # ✅ 하나만 존재한다고 보장
    excel_path = excel_files[0]
    print(f"처리 대상 파일: {excel_path.name}")

    try:
        aggregates = build_kipris_year_aggregates(excel_path)
        return aggregates

    finally:
        # ✅ 성공/실패 관계없이 폴더 정리
        cleanup_directory(KIPRIS_DIR)
        print("KIPRIS 디렉토리 정리 완료")


# ================================
# 엔트리포인트
# ================================
if __name__ == "__main__":
    agg = run_kipris_pipeline()

    print("=== Application ===")
    print(agg.application.model_dump())

    print("=== Publication ===")
    print(agg.publication.model_dump())

    print("=== Registration ===")
    print(agg.registration.model_dump())

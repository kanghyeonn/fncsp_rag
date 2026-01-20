# fncsp-rag



## Getting started

- **다중 데이터 소스 통합**
  - PostgreSQL 벡터 DB 기반 사업계획서 검색
  - PDF 파일 직접 분석
  - Google Search API를 통한 외부 시장 정보 수집
  - KIPRIS 특허청 통계 데이터 자동 수집

- **LLM 기반 보고서 생성**
  - Google Gemini 2.0/2.5 Flash 모델 활용
  - Gemini Cached Content를 통한 효율적인 프롬프트 관리
  - 구조화된 JSON 출력 (Pydantic 스키마 검증)

## 시스템 아키텍처

```
사업계획서 PDF
     ↓
[Vector DB 임베딩] ← HuggingFace kure-v1
     ↓
[컨텍스트 검색] → [LLM 분석] → JSON 보고서
     ↑              ↑
[KIPRIS 통계]  [Google Search]
```

## 프로젝트 구조

```
rag/
├── __init__.py
├── config.py                    # 전역 설정 (DB, LLM, 임베딩 모델)
├── final_run.py                 # 실행 엔트리포인트
│
├── business_plan/               # 사업계획서 PDF 저장소
├── ipc_statistics/              # KIPRIS 통계 엑셀 임시 저장소
├── reports/                     # 생성된 JSON 보고서 저장소
│
└── final/
    ├── collectors/
    │   ├── kipris_client.py     # Selenium 기반 KIPRIS 크롤러
    │   └── kipris_parser.py     # 엑셀 파싱 및 연도별 집계
    │
    ├── prompts/
    │   ├── base_prompt.py       # 공통 BASE 프롬프트
    │   ├── cache_system_prompt.py
    │   ├── future_prompt.py
    │   ├── ip_prompt.py
    │   ├── ipc_prompt.py
    │   ├── market_prompt.py
    │   ├── marketing_prompt.py
    │   ├── bm_prompt.py
    │   └── strict_instruction.py
    │
    ├── schemas/
    │   ├── base_schemas.py      # ReportItemResult
    │   ├── ipc_schemas.py       # IPC 분석 결과 스키마
    │   └── market_schemas.py    # 시장/경쟁사 분석 스키마
    │
    ├── cache_manager.py         # Gemini Cached Content 관리
    ├── retriever.py             # 벡터 DB 검색
    ├── queries.py               # 항목별 검색 쿼리 정의
    ├── generator.py             # LLM 호출 및 재시도 로직
    ├── pipeline.py              # 분석 파이프라인 오케스트레이션
    └── utils.py                 # JSON 정제 유틸리티
```

## 설치 방법

### 1. 사전 요구사항

- Python 3.10+
- PostgreSQL (pgvector 확장 활성화)
- CUDA 지원 GPU (임베딩 모델용)
- Chrome 브라우저 (KIPRIS 크롤링용)

### 2. 패키지 설치

```bash
pip install -r requirements.txt
```

**주요 의존성:**
- `langchain-core`, `langchain-community`, `langchain-google-genai`
- `google-genai`
- `psycopg[binary]`
- `pydantic`
- `undetected-chromedriver`, `selenium`
- `python-dotenv`

### 3. 환경 변수 설정

프로젝트 루트에 `.env` 파일 생성:

```env
# PostgreSQL 설정
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DATABASE=your_database
POSTGRES_USER=your_user
POSTGRES_PASSWORD=your_password

# Google API 키
GOOGLE_API_KEY=your_google_api_key
GEMINI_API_KEY=your_gemini_api_key  # 동일 키 사용 가능
```

## 사용 방법

### 기본 실행

```python
from rag.final.pipeline import generate

# 회사명과 PDF 경로 설정
company = "(주) 예시회사"
pdf_path = "rag/business_plan/example.pdf"

# 분석 실행
results = generate(
    company=company,
    business_plan_pdf=pdf_path,
    item_source_map={
        1: "file+vectordb",  # 미래기술대응역량
        2: "ipc+kipris",     # IP 대응역량 (특허 통계 포함)
        # 3: "googlesearch"  # 시장 규모 (자동 설정)
        4: "file+vectordb",  # 비즈니스 모델
        5: "file+vectordb"   # 마케팅 역량
    },
    item_range=(1, 5)  # 전체 항목 분석
)
```

### 소스 타입별 분석 방식

| Source Type | 설명 | 사용 시점 |
|------------|------|---------|
| `vectordb` | 벡터 DB 검색만 사용 | 일반적인 분석 |
| `file` | PDF 직접 분석 | 구조화된 문서 분석 |
| `file+vectordb` | 캐시 + 벡터 검색 병합 | 정밀 분석 (권장) |
| `googlesearch` | Google Search API 사용 | 시장 규모·경쟁사 (자동) |
| `ipc+kipris` | IPC 도출 + 특허 통계 | IP 대응역량 전용 |

### 결과 저장

```python
from rag.final_run import save_report_to_json

# JSON 파일로 저장
saved_files = save_report_to_json(company, results)

# 저장 경로: reports/회사명_항목명.json
```

## 출력 데이터 구조

### 기본 보고서 형식

```json
{
  "metadata": {
    "company": "(주) 예시회사",
    "item_id": 1,
    "section": "미래기술대응역량",
    "created_at": "2024-01-20T10:30:00",
    "filename": "예시회사_미래기술대응역량.json"
  },
  "content": {
    "evaluation": "500~600자 분량의 평가 내용..."
  }
}
```

### IP 대응역량 (item_id=2)

```json
{
  "content": {
    "ipc_analysis": [
      {
        "ipc_code": "G06Q50/16",
        "ipc_name": "Healthcare",
        "linked_business_function": "원격 진료 플랫폼",
        "justification": "..."
      }
    ],
    "statistics": {
      "application": {
        "years": [2020, 2021, 2022],
        "values_int": [120, 150, 180]
      },
      "publication": {...},
      "registration": {...}
    }
  }
}
```

### 시장 규모 및 경쟁사 (item_id=3)

```json
{
  "content": {
    "overseas_market": {
      "currency": "USD",
      "unit": "billion",
      "years": [2024, 2025, 2026, 2027, 2028],
      "values_int": [10, 12, 15, 18, 22],
      "method": "CAGR 기반 산출",
      "sources": [...]
    },
    "korea_market": {...},
    "competitors": [
      {
        "name": "경쟁사A",
        "country": "South Korea",
        "similarity_reason": "...",
        "product_service_summary": "...",
        "business_model": ["구독", "중개수수료"],
        "sources": [...]
      }
    ]
  },
  "grounding": {...}
}
```

## 주요 특징

### 1. Gemini Cached Content 활용
- 동일 사업계획서 재사용 시 비용 절감 (최대 90%)
- `cache_manager.py`에서 자동 관리

### 2. 재시도 메커니즘
- JSON 파싱 실패 시 자동 재시도 (최대 3회)
- 2회차부터 엄격한 JSON 지침 자동 주입

### 3. KIPRIS 자동화
- Selenium을 통한 특허청 통계 자동 수집
- IPC 코드 기반 출원/공개/등록 연도별 집계

### 4. 구조화된 프롬프트 관리
- 항목별 전문 프롬프트 분리
- 컨설팅 보고서 톤 강제
- 메타적 표현 금지 ("분석 불가", "정보 부족" 등)

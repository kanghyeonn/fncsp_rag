<<<<<<< HEAD
# fncsp-rag



## Getting started

To make it easy for you to get started with GitLab, here's a list of recommended next steps.

Already a pro? Just edit this README.md and make it your own. Want to make it easy? [Use the template at the bottom](#editing-this-readme)!

## Add your files

- [ ] [Create](https://docs.gitlab.com/ee/user/project/repository/web_editor.html#create-a-file) or [upload](https://docs.gitlab.com/ee/user/project/repository/web_editor.html#upload-a-file) files
- [ ] [Add files using the command line](https://docs.gitlab.com/topics/git/add_files/#add-files-to-a-git-repository) or push an existing Git repository with the following command:

```
cd existing_repo
git remote add origin http://192.168.50.247:6060/bigdata/fncsp-rag.git
git branch -M main
git push -uf origin main
```

## Integrate with your tools

- [ ] [Set up project integrations](http://192.168.50.247:6060/bigdata/fncsp-rag/-/settings/integrations)

## Collaborate with your team

- [ ] [Invite team members and collaborators](https://docs.gitlab.com/ee/user/project/members/)
- [ ] [Create a new merge request](https://docs.gitlab.com/ee/user/project/merge_requests/creating_merge_requests.html)
- [ ] [Automatically close issues from merge requests](https://docs.gitlab.com/ee/user/project/issues/managing_issues.html#closing-issues-automatically)
- [ ] [Enable merge request approvals](https://docs.gitlab.com/ee/user/project/merge_requests/approvals/)
- [ ] [Set auto-merge](https://docs.gitlab.com/user/project/merge_requests/auto_merge/)

## Test and Deploy

Use the built-in continuous integration in GitLab.

- [ ] [Get started with GitLab CI/CD](https://docs.gitlab.com/ee/ci/quick_start/)
- [ ] [Analyze your code for known vulnerabilities with Static Application Security Testing (SAST)](https://docs.gitlab.com/ee/user/application_security/sast/)
- [ ] [Deploy to Kubernetes, Amazon EC2, or Amazon ECS using Auto Deploy](https://docs.gitlab.com/ee/topics/autodevops/requirements.html)
- [ ] [Use pull-based deployments for improved Kubernetes management](https://docs.gitlab.com/ee/user/clusters/agent/)
- [ ] [Set up protected environments](https://docs.gitlab.com/ee/ci/environments/protected_environments.html)

***

# Editing this README

When you're ready to make this README your own, just edit this file and use the handy template below (or feel free to structure it however you want - this is just a starting point!). Thanks to [makeareadme.com](https://www.makeareadme.com/) for this template.

## Suggestions for a good README

Every project is different, so consider which of these sections apply to yours. The sections used in the template are suggestions for most open source projects. Also keep in mind that while a README can be too long and detailed, too long is better than too short. If you think your README is too long, consider utilizing another form of documentation rather than cutting out information.

## Name
Choose a self-explaining name for your project.

## Description
Let people know what your project can do specifically. Provide context and add a link to any reference visitors might be unfamiliar with. A list of Features or a Background subsection can also be added here. If there are alternatives to your project, this is a good place to list differentiating factors.

## Badges
On some READMEs, you may see small images that convey metadata, such as whether or not all the tests are passing for the project. You can use Shields to add some to your README. Many services also have instructions for adding a badge.

## Visuals
Depending on what you are making, it can be a good idea to include screenshots or even a video (you'll frequently see GIFs rather than actual videos). Tools like ttygif can help, but check out Asciinema for a more sophisticated method.

## Installation
Within a particular ecosystem, there may be a common way of installing things, such as using Yarn, NuGet, or Homebrew. However, consider the possibility that whoever is reading your README is a novice and would like more guidance. Listing specific steps helps remove ambiguity and gets people to using your project as quickly as possible. If it only runs in a specific context like a particular programming language version or operating system or has dependencies that have to be installed manually, also add a Requirements subsection.

## Usage
Use examples liberally, and show the expected output if you can. It's helpful to have inline the smallest example of usage that you can demonstrate, while providing links to more sophisticated examples if they are too long to reasonably include in the README.

## Support
Tell people where they can go to for help. It can be any combination of an issue tracker, a chat room, an email address, etc.

## Roadmap
If you have ideas for releases in the future, it is a good idea to list them in the README.

## Contributing
State if you are open to contributions and what your requirements are for accepting them.

For people who want to make changes to your project, it's helpful to have some documentation on how to get started. Perhaps there is a script that they should run or some environment variables that they need to set. Make these steps explicit. These instructions could also be useful to your future self.

You can also document commands to lint the code or run tests. These steps help to ensure high code quality and reduce the likelihood that the changes inadvertently break something. Having instructions for running tests is especially helpful if it requires external setup, such as starting a Selenium server for testing in a browser.

## Authors and acknowledgment
Show your appreciation to those who have contributed to the project.

## License
For open source projects, say how it is licensed.

## Project status
If you have run out of energy or time for your project, put a note at the top of the README saying that development has slowed down or stopped completely. Someone may choose to fork your project or volunteer to step in as a maintainer or owner, allowing your project to keep going. You can also make an explicit request for maintainers.
=======
# RAG 기반 사업계획서 분석 시스템

사업계획서를 기반으로 기업의 미래기술대응역량, IP 대응역량, 시장 규모, 비즈니스 모델, 마케팅 역량을 종합적으로 분석하여 컨설팅 보고서를 자동 생성하는 RAG(Retrieval-Augmented Generation) 시스템입니다.

## 주요 기능

- **5개 평가 항목 자동 분석**
  - 미래기술대응역량
  - IP 대응역량 (IPC 코드 도출 + KIPRIS 특허 통계 수집)
  - 시장 규모 예측치 및 경쟁사 분석
  - 비즈니스 모델 역량진단
  - 마케팅 역량진단

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

## 트러블슈팅

### PostgreSQL 연결 오류
```bash
# pgvector 확장 확인
psql -d your_database -c "SELECT * FROM pg_extension WHERE extname='vector';"
```

### KIPRIS 크롤링 실패
- Chrome 드라이버 버전 확인: `undetected-chromedriver` 최신 버전 사용
- 헤드리스 모드 비활성화 (KIPRIS는 일부 헤드리스 탐지)


### JSON 파싱 오류
- `utils.py`의 `clean_json_string()` 로직 확인
- LLM 응답에 마크다운 코드블록 포함 시 자동 제거

>>>>>>> 90e0eca (add readme)

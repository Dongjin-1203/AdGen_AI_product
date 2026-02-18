# AdGen Pipeline - AI 광고 생성 파이프라인

> 기존 AdGen AI에서 LangGraph 기반 파이프라인 + 실시간 모니터링으로 리팩토링

---

## 프로젝트 구조

```
adgen-pipeline/
├── backend/                    # FastAPI + LangGraph
│   ├── app/
│   │   ├── api/routes/
│   │   │   ├── pipeline.py     # 🆕 파이프라인 실행 엔드포인트
│   │   │   ├── websocket.py    # 🆕 실시간 상태 스트리밍
│   │   │   ├── auth.py         # 기존 유지
│   │   │   ├── contents.py     # 기존 유지
│   │   │   └── history.py      # 기존 유지
│   │   ├── services/
│   │   │   ├── pipeline/
│   │   │   │   ├── graph.py        # 🆕 LangGraph 그래프 정의
│   │   │   │   ├── state.py        # 🆕 PipelineState TypedDict
│   │   │   │   ├── nodes.py        # 🆕 각 단계 노드 함수
│   │   │   │   └── validators.py   # 🆕 단계별 검증 로직
│   │   │   ├── vision/         # 기존 복사
│   │   │   ├── generation/     # 기존 복사
│   │   │   ├── img_processing/ # 기존 복사 (RMBG-2.0 merge 예정)
│   │   │   └── html/           # 기존 복사
│   │   ├── models/             # 기존 복사
│   │   ├── core/               # 기존 복사
│   │   ├── db/                 # 기존 복사
│   │   └── templates/          # 기존 복사
│   ├── main.py
│   ├── config.py
│   └── requirements.txt
├── frontend/                   # Next.js + ReactFlow
│   ├── src/
│   │   ├── app/
│   │   ├── components/
│   │   │   └── pipeline/
│   │   │       ├── PipelineMonitor.tsx  # 🆕 ReactFlow 파이프라인 시각화
│   │   │       └── PipelineNode.tsx     # 🆕 노드 컴포넌트
│   │   ├── lib/
│   │   │   └── api.ts          # 기존 + pipeline API 추가
│   │   └── types/
│   ├── package.json
│   └── next.config.js
├── .github/workflows/
│   ├── backend.yml
│   └── frontend.yml
└── docs/
    └── architecture.md
```

---

## 기술 스택

| 레이어 | 기술 |
|--------|------|
| Backend Framework | FastAPI |
| Pipeline Orchestration | **LangGraph** 🆕 |
| Real-time | **WebSocket** (FastAPI 내장) 🆕 |
| AI Models | RMBG-2.0, IDM-VTON, RealvisXL |
| Caption/HTML | OpenAI GPT-4o |
| Vision AI | Google Gemini |
| Frontend | Next.js |
| Pipeline Visualization | **ReactFlow** 🆕 |
| Storage | GCP Cloud Storage |
| DB | PostgreSQL (Cloud SQL) |
| Deploy | Google Cloud Run |

---

## 파이프라인 흐름

```
사용자 요청 (content_id)
        │
        ▼
[LangGraph Orchestrator]
        │
        ├─ Node 1: select_image
        │    └─ post_check: 이미지 존재 여부, 해상도
        │
        ├─ Node 2: remove_background (RMBG-2.0)
        │    └─ post_check: 알파채널 정상 여부
        │
        ├─ Node 3: virtual_fitting (IDM-VTON)
        │    ├─ pre_check: 카테고리 충돌 감지 ← 핵심
        │    │   (상의 + 원피스 모델 → BLOCK)
        │    └─ post_check: 결과 이미지 품질
        │
        ├─ Node 4: generate_background (RealvisXL)
        │    └─ post_check: 배경 생성 완료
        │
        ├─ Node 5: generate_caption (OpenAI)
        │    └─ post_check: 캡션 생성 완료
        │
        ├─ Node 6: generate_html (OpenAI)
        │    └─ post_check: HTML 유효성
        │
        └─ Node 7: save_image (Playwright)
             └─ post_check: 이미지 저장 완료

각 노드 → WebSocket → ReactFlow UI (실시간 업데이트)
```

---

## 카테고리 충돌 감지 (Node 3 pre_check)

```python
CATEGORY_CONFLICT_MAP = {
    "상의": ["원피스", "드레스"],   # 상의 상품 → 원피스 모델 불가
    "하의": ["원피스", "드레스"],   # 하의 상품 → 원피스 모델 불가
}
```

---

## 초기 세팅

### 1. 레포 클론 후 기존 코드 복사

```bash
# 기존 AdGen AI에서 복사할 디렉토리
cp -r old-adgen/backend/app/services/vision/       backend/app/services/vision/
cp -r old-adgen/backend/app/services/generation/   backend/app/services/generation/
cp -r old-adgen/backend/app/services/img_processing/ backend/app/services/img_processing/
cp -r old-adgen/backend/app/services/html/         backend/app/services/html/
cp -r old-adgen/backend/app/models/                backend/app/models/
cp -r old-adgen/backend/app/core/                  backend/app/core/
cp -r old-adgen/backend/app/db/                    backend/app/db/
cp -r old-adgen/backend/app/templates/             backend/app/templates/
cp -r old-adgen/backend/app/api/routes/auth.py     backend/app/api/routes/
cp -r old-adgen/backend/app/api/routes/contents.py backend/app/api/routes/
cp -r old-adgen/backend/app/api/routes/history.py  backend/app/api/routes/
cp    old-adgen/backend/config.py                  backend/
cp    old-adgen/backend/alembic.ini                backend/

# RMBG-2.0 (하위 브랜치에서)
git checkout feature/rmbg-2.0 -- backend/app/services/img_processing/background_removal.py
```

### 2. 새로 작성할 파일

```
backend/app/services/pipeline/state.py      ← PipelineState
backend/app/services/pipeline/nodes.py      ← 7개 노드
backend/app/services/pipeline/validators.py ← 충돌 감지
backend/app/services/pipeline/graph.py      ← LangGraph 그래프
backend/app/api/routes/pipeline.py          ← 엔드포인트
backend/app/api/routes/websocket.py         ← WebSocket
frontend/src/components/pipeline/PipelineMonitor.tsx
frontend/src/components/pipeline/PipelineNode.tsx
```

### 3. 의존성 추가

```bash
# backend/requirements.txt에 추가
langgraph>=0.2.0
langchain-core>=0.3.0
```

```bash
# frontend
npm install reactflow
```

### 4. 환경 변수

기존 `.env.sample` 복사 후 그대로 사용 가능.

---

## 개발 순서 (4일 스프린트)

| Day | 작업 |
|-----|------|
| Day 1 (2/17) | `state.py`, `nodes.py`, `validators.py`, `graph.py` 작성 |
| Day 2 (2/18) | `pipeline.py` 엔드포인트 + `websocket.py` |
| Day 3 (2/19) | ReactFlow UI (`PipelineMonitor.tsx`) |
| Day 4 (2/20) | RMBG-2.0 merge + 통합 테스트 |

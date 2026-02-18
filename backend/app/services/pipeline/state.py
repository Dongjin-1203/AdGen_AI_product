"""
AdGen Pipeline State
LangGraph에서 각 노드 간 공유되는 상태 정의
"""
from typing import TypedDict, Optional, Literal
from datetime import datetime


# 각 단계 상태
StepStatus = Literal["pending", "running", "success", "failed", "skipped"]

# 파이프라인 전체 상태
PipelineStatus = Literal["pending", "running", "success", "failed"]


class StepState(TypedDict):
    """개별 단계 상태"""
    status: StepStatus
    started_at: Optional[str]
    completed_at: Optional[str]
    error: Optional[str]
    result_url: Optional[str]   # 이미지 결과물이 있는 경우


class PipelineState(TypedDict):
    """
    전체 파이프라인 상태
    LangGraph 노드 간 공유됨
    """
    # ===== 식별자 =====
    job_id: str                     # 파이프라인 실행 ID (UUID)
    user_id: str
    content_id: str                 # 선택된 상품 이미지

    # ===== 상품 메타데이터 (Node 1에서 로드) =====
    product_category: Optional[str]     # 상의/하의/원피스/아우터
    product_image_url: Optional[str]    # GCS 원본 이미지 URL

    # ===== 스타일 설정 (요청 파라미터) =====
    style: str                      # resort / retro / romantic
    model_index: Optional[int]      # K-Fashion 모델 인덱스 (None=랜덤)
    user_prompt: Optional[str]      # 사용자 추가 요청

    # ===== 각 단계 결과 이미지 =====
    removed_bg_url: Optional[str]       # Node 2: 배경제거 결과
    fitted_image_url: Optional[str]     # Node 3: 가상피팅 결과
    background_image_url: Optional[str] # Node 4: 배경생성 결과
    caption: Optional[str]              # Node 5: 생성된 캡션
    html_content: Optional[str]         # Node 6: 생성된 HTML
    final_image_url: Optional[str]      # Node 7: 최종 저장 이미지

    # ===== DB 저장 ID (중간 결과 추적용) =====
    generation_id: Optional[str]    # GenerationHistory ID
    caption_id: Optional[str]       # AdCaption ID
    ad_copy_id: Optional[str]       # AdCopyHistory ID

    # ===== 파이프라인 상태 =====
    status: PipelineStatus
    current_step: int               # 현재 실행 중인 단계 (1~7)
    error: Optional[str]            # 실패 시 에러 메시지
    error_step: Optional[int]       # 실패한 단계 번호

    # ===== 각 단계별 상세 상태 (WebSocket 전송용) =====
    steps: dict[str, StepState]     # key: "node1" ~ "node7"

    # ===== 메타 =====
    created_at: str
    updated_at: str


# ===== 단계 이름 매핑 =====
STEP_NAMES = {
    1: "select_image",
    2: "remove_background",
    3: "virtual_fitting",
    4: "generate_background",
    5: "generate_caption",
    6: "generate_html",
    7: "save_image",
}

STEP_LABELS = {
    1: "상품 이미지 선택",
    2: "배경 제거",
    3: "가상 모델 피팅",
    4: "배경 생성",
    5: "광고 캡션 생성",
    6: "HTML 광고 페이지 생성",
    7: "페이지 이미지 저장",
}


def create_initial_state(
    job_id: str,
    user_id: str,
    content_id: str,
    style: str,
    model_index: Optional[int] = None,
    user_prompt: Optional[str] = None,
) -> PipelineState:
    """초기 파이프라인 상태 생성"""
    now = datetime.utcnow().isoformat()

    return PipelineState(
        job_id=job_id,
        user_id=user_id,
        content_id=content_id,
        product_category=None,
        product_image_url=None,
        style=style,
        model_index=model_index,
        user_prompt=user_prompt,
        removed_bg_url=None,
        fitted_image_url=None,
        background_image_url=None,
        caption=None,
        html_content=None,
        final_image_url=None,
        generation_id=None,
        caption_id=None,
        ad_copy_id=None,
        status="pending",
        current_step=0,
        error=None,
        error_step=None,
        steps={
            name: StepState(
                status="pending",
                started_at=None,
                completed_at=None,
                error=None,
                result_url=None,
            )
            for name in STEP_NAMES.values()
        },
        created_at=now,
        updated_at=now,
    )

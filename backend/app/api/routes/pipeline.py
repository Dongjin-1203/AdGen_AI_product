"""
파이프라인 실행 API 엔드포인트
POST /api/v1/pipeline/run  → 파이프라인 실행
GET  /api/v1/pipeline/{job_id}/status → 상태 조회
WS   /ws/pipeline/{job_id} → 실시간 상태 스트리밍
"""
import uuid
import asyncio
import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.db.base import get_db
from app.models.schemas import User, UserContent
from app.api.routes.auth import get_current_user
from app.services.pipeline.state import create_initial_state, PipelineState
from app.services.pipeline.graph import get_pipeline_graph
from app.services.pipeline.nodes import set_ws_broadcast
from app.api.routes.websocket import manager

logger = logging.getLogger(__name__)

router = APIRouter()

# 실행 중인 파이프라인 상태 저장 (인메모리)
# 프로덕션에서는 Redis로 교체 권장
_pipeline_states: dict[str, PipelineState] = {}


# ===== Request/Response =====

class PipelineRunRequest(BaseModel):
    content_id: str
    style: str = "resort"           # resort / retro / romantic
    model_index: Optional[int] = None
    user_prompt: Optional[str] = None
    ad_inputs: Optional[dict] = None

    class Config:
        json_schema_extra = {
            "example": {
                "content_id": "uuid-here",
                "style": "resort",
                "model_index": None,
                "user_prompt": "밝고 화사한 느낌으로",
                "ad_inputs": {
                    "discount": "40% OFF",
                    "brand": "SPRING SALE"
                }
            }
        }


class PipelineRunResponse(BaseModel):
    job_id: str
    status: str
    message: str
    ws_url: str     # 프론트에서 WebSocket 연결할 URL


# ===== 파이프라인 실행 함수 =====

async def _run_pipeline(job_id: str, initial_state: PipelineState):
    """백그라운드에서 파이프라인 실행"""
    try:
        # WebSocket 브로드캐스트 함수 주입
        async def _broadcast(jid: str, state: PipelineState):
            _pipeline_states[jid] = state
            await manager.broadcast(jid, state)

        set_ws_broadcast(_broadcast)

        # LangGraph 실행
        graph = get_pipeline_graph()
        final_state = await graph.ainvoke(initial_state)

        # 최종 상태 업데이트
        if final_state["status"] != "failed":
            final_state["status"] = "success"

        _pipeline_states[job_id] = final_state
        await manager.broadcast(job_id, final_state)

        logger.info(f"[Pipeline] 완료: job_id={job_id}, status={final_state['status']}")

    except Exception as e:
        logger.error(f"[Pipeline] 오류: job_id={job_id}, error={e}", exc_info=True)
        if job_id in _pipeline_states:
            _pipeline_states[job_id]["status"] = "failed"
            _pipeline_states[job_id]["error"] = str(e)
            await manager.broadcast(job_id, _pipeline_states[job_id])


# ===== API 엔드포인트 =====

@router.post("/pipeline/run", response_model=PipelineRunResponse)
async def run_pipeline(
    request: PipelineRunRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    광고 생성 파이프라인 실행

    - content_id: 이미 업로드된 상품 이미지 ID
    - style: resort / retro / romantic
    - 실행 후 즉시 job_id 반환
    - 실시간 상태는 WebSocket으로 수신
    """
    # 상품 존재 확인
    content = db.query(UserContent).filter(
        UserContent.content_id == request.content_id,
        UserContent.user_id == current_user.user_id,
    ).first()

    if not content:
        raise HTTPException(status_code=404, detail="콘텐츠를 찾을 수 없습니다.")

    # 스타일 검증
    valid_styles = ["resort", "retro", "romantic"]
    if request.style not in valid_styles:
        raise HTTPException(
            status_code=400,
            detail=f"유효하지 않은 스타일입니다. 선택 가능: {valid_styles}"
        )

    # 초기 상태 생성
    job_id = str(uuid.uuid4())
    initial_state = create_initial_state(
        job_id=job_id,
        user_id=current_user.user_id,
        content_id=request.content_id,
        style=request.style,
        model_index=request.model_index,
        user_prompt=request.user_prompt,
        ad_inputs=request.ad_inputs,
    )

    _pipeline_states[job_id] = initial_state

    # 백그라운드 실행
    asyncio.create_task(_run_pipeline, job_id, initial_state)

    logger.info(f"[Pipeline] 시작: job_id={job_id}, content_id={request.content_id}")

    return PipelineRunResponse(
        job_id=job_id,
        status="pending",
        message="파이프라인 시작됨. WebSocket으로 실시간 상태를 확인하세요.",
        ws_url=f"/ws/pipeline/{job_id}",
    )


@router.get("/pipeline/{job_id}/status")
async def get_pipeline_status(
    job_id: str,
    current_user: User = Depends(get_current_user),
):
    """파이프라인 상태 조회 (폴링용)"""
    state = _pipeline_states.get(job_id)
    if not state:
        raise HTTPException(status_code=404, detail="파이프라인을 찾을 수 없습니다.")

    if state["user_id"] != current_user.user_id:
        raise HTTPException(status_code=403, detail="접근 권한이 없습니다.")

    return {
        "job_id": job_id,
        "status": state["status"],
        "current_step": state["current_step"],
        "steps": state["steps"],
        "error": state.get("error"),
        "final_image_url": state.get("final_image_url"),
    }


# ===== WebSocket 엔드포인트 =====

@router.websocket("/ws/pipeline/{job_id}")
async def pipeline_websocket(websocket: WebSocket, job_id: str):
    """
    파이프라인 실시간 상태 스트리밍

    연결 즉시 현재 상태 전송 후
    각 노드 완료 시마다 상태 업데이트 전송
    """
    await manager.connect(job_id, websocket)

    try:
        # 연결 즉시 현재 상태 전송
        current_state = _pipeline_states.get(job_id)
        if current_state:
            await manager.broadcast(job_id, current_state)

        # 연결 유지 (클라이언트 disconnect 대기)
        while True:
            try:
                await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
            except asyncio.TimeoutError:
                # 30초마다 ping
                await websocket.send_text('{"type": "ping"}')

    except WebSocketDisconnect:
        manager.disconnect(job_id, websocket)
    except Exception as e:
        logger.error(f"[WS] 오류: job_id={job_id}, error={e}")
        manager.disconnect(job_id, websocket)

"""
WebSocket 실시간 상태 스트리밍
파이프라인 각 단계 상태를 프론트엔드로 전송
"""
import json
import asyncio
import logging
from typing import Dict, Set
from fastapi import WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)


class PipelineConnectionManager:
    """
    WebSocket 연결 관리
    job_id 기준으로 연결 관리 (한 job에 여러 클라이언트 가능)
    """

    def __init__(self):
        # job_id → {WebSocket} 매핑
        self.connections: Dict[str, Set[WebSocket]] = {}

    async def connect(self, job_id: str, websocket: WebSocket):
        await websocket.accept()
        if job_id not in self.connections:
            self.connections[job_id] = set()
        self.connections[job_id].add(websocket)
        logger.info(f"[WS] 연결됨: job_id={job_id}")

    def disconnect(self, job_id: str, websocket: WebSocket):
        if job_id in self.connections:
            self.connections[job_id].discard(websocket)
            if not self.connections[job_id]:
                del self.connections[job_id]
        logger.info(f"[WS] 연결 해제: job_id={job_id}")

    async def broadcast(self, job_id: str, state: dict):
        """특정 job의 모든 연결에 상태 전송"""
        if job_id not in self.connections:
            return

        message = json.dumps({
            "job_id": job_id,
            "status": state.get("status"),
            "current_step": state.get("current_step"),
            "steps": state.get("steps", {}),
            "error": state.get("error"),
            "error_step": state.get("error_step"),
            "final_image_url": state.get("final_image_url"),
            "updated_at": state.get("updated_at"),
        }, ensure_ascii=False)

        dead_sockets = set()
        for ws in self.connections[job_id].copy():
            try:
                await ws.send_text(message)
            except Exception:
                dead_sockets.add(ws)

        for ws in dead_sockets:
            self.connections[job_id].discard(ws)


# 싱글톤
manager = PipelineConnectionManager()

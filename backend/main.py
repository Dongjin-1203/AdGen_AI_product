"""
AdGen Pipeline - FastAPI Entry Point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from app.api.routes import auth, contents, history
from app.api.routes.pipeline import router as pipeline_router

app = FastAPI(
    title="AdGen Pipeline API",
    description="LangGraph 기반 AI 광고 생성 파이프라인",
    version="2.0.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 기존 라우터
app.include_router(auth.router, prefix="/api/v1", tags=["auth"])
app.include_router(contents.router, prefix="/api/v1/contents", tags=["contents"])
app.include_router(history.router, prefix="/api/v1", tags=["history"])

# 🆕 파이프라인 라우터 (REST + WebSocket 포함)
app.include_router(pipeline_router, prefix="/api/v1", tags=["pipeline"])


@app.get("/health")
async def health():
    return {"status": "ok", "version": "2.0.0"}

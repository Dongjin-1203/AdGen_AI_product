"""
히스토리 API 라우터
/api/v1/history/{user_id} - 사용자별 생성 히스토리 목록
/api/v1/history/{history_id} (DELETE) - 히스토리 삭제
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response
from sqlalchemy.orm import Session
from typing import List
import zipfile
from io import BytesIO
from datetime import datetime, timedelta, timezone
import math

from app.db.base import get_db
from app.models.schemas import GenerationHistory, UserContent, User
from app.api.routes.auth import get_current_user
from app.models.caption_system import AdCopyHistory

router = APIRouter()


# ===== Response Schema =====
from pydantic import BaseModel

class HistoryResponse(BaseModel):
    """히스토리 응답 스키마"""
    history_id: str
    content_id: str
    user_id: str
    
    # 생성 정보
    style: str
    prompt: str | None
    result_url: str
    
    # 메타데이터
    processing_time: float | None
    created_at: datetime
    
    # 원본 콘텐츠 정보 (Join)
    original_image_url: str | None = None
    product_name: str | None = None
    
    class Config:
        from_attributes = True

class AdCopyDataSchema(BaseModel):
    headline: str
    discount: str | None = None
    period: str | None = None
    brand: str | None = None

class AdCopyHistoryItem(BaseModel):
    ad_copy_id: str
    template_used: str
    ad_copy_data: AdCopyDataSchema
    final_image_url: str | None
    created_at: datetime
    product_name: str | None = None
    category: str | None = None
    model_image_url: str | None = None

    class Config:
        from_attributes = True

class AdCopyHistoryResponse(BaseModel):
    results: list[AdCopyHistoryItem]
    total_pages: int

class AdCopyStatistics(BaseModel):
    total_count: int
    template_counts: dict
    recent_7days_count: int
    average_per_day: float

class AdCopyDetail(BaseModel):
    ad_copy_id: str
    template_used: str
    ad_copy_data: AdCopyDataSchema
    html_content: str | None
    final_image_url: str | None
    created_at: datetime
    processing_time: float | None

# ===== API 엔드포인트 =====

@router.get("/history/{user_id}", response_model=List[HistoryResponse])
async def get_user_history(
    user_id: str,
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    사용자별 생성 히스토리 목록 조회
    
    Args:
        user_id: 조회할 사용자 ID
        limit: 조회 개수 (기본 50)
        offset: 건너뛸 개수 (페이징)
    
    Returns:
        히스토리 목록 (최신순)
    """
    # 권한 확인: 본인의 히스토리만 조회 가능
    if current_user.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this user's history"
        )
    
    # GenerationHistory + UserContent JOIN
    histories = db.query(
        GenerationHistory,
        UserContent.image_url.label('original_image_url'),
        UserContent.product_name
    ).join(
        UserContent,
        GenerationHistory.content_id == UserContent.content_id
    ).filter(
        GenerationHistory.user_id == user_id
    ).order_by(
        GenerationHistory.created_at.desc()
    ).limit(limit).offset(offset).all()
    
    # 결과 변환
    result = []
    for history, original_image_url, product_name in histories:
        history_dict = {
            "history_id": history.generation_id,
            "content_id": history.content_id,
            "user_id": history.user_id,
            "style": history.style,
            "prompt": history.prompt,
            "result_url": history.result_url,
            "processing_time": float(history.processing_time) if history.processing_time else None,
            "created_at": history.created_at,
            "original_image_url": original_image_url,
            "product_name": product_name
        }
        result.append(HistoryResponse(**history_dict))
    
    return result


@router.delete("/history/{history_id}")
async def delete_history(
    history_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """히스토리 삭제"""
    from app.models.caption_system import AdCaption, AdCopyHistory
    
    # 본인 히스토리 확인
    history = db.query(GenerationHistory).filter(
        GenerationHistory.generation_id == history_id,
        GenerationHistory.user_id == current_user.user_id
    ).first()
    
    if not history:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="History not found or not authorized"
        )
    
    # ⭐ 관련 데이터 수동 삭제 (CASCADE 수동 구현)
    db.query(AdCaption).filter(
        AdCaption.generation_id == history_id
    ).delete(synchronize_session=False)
    
    db.query(AdCopyHistory).filter(
        AdCopyHistory.generation_id == history_id
    ).delete(synchronize_session=False)
    
    # 히스토리 삭제
    db.delete(history)
    db.commit()
    
    return {
        "success": True,
        "message": "History deleted successfully",
        "history_id": history_id
    }

def download_from_gcs(image_url: str) -> bytes:
    """
    GCS에서 이미지 다운로드
    
    Args:
        image_url: GCS URL (예: https://storage.googleapis.com/bucket/path/file.png)
    
    Returns:
        이미지 바이트
    """
    from google.cloud import storage
    from google.oauth2 import service_account
    from config import settings
    
    # GCS 클라이언트
    if settings.GOOGLE_APPLICATION_CREDENTIALS:
        credentials = service_account.Credentials.from_service_account_file(
            settings.GOOGLE_APPLICATION_CREDENTIALS
        )
        client = storage.Client(credentials=credentials)
    else:
        client = storage.Client()
    
    # URL에서 버킷명과 경로 추출
    # https://storage.googleapis.com/bucket-name/user_id/generations/file.png
    parts = image_url.replace("https://storage.googleapis.com/", "").split("/")
    bucket_name = parts[0]
    gcs_path = "/".join(parts[1:])
    
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(gcs_path)
    
    # 다운로드
    image_bytes = blob.download_as_bytes()
    
    return image_bytes

@router.get("/history/{history_id}/download")
async def download_vton_result(
    history_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    VTON 결과 이미지 다운로드 (단일)
    
    Args:
        history_id: GenerationHistory ID
    
    Returns:
        PNG 이미지 파일
    """
    
    print(f"\n📥 VTON 이미지 다운로드 요청: {history_id}")
    
    # 1. GenerationHistory 조회
    history = db.query(GenerationHistory).filter(
        GenerationHistory.generation_id == history_id,
        GenerationHistory.user_id == current_user.user_id
    ).first()
    
    if not history:
        raise HTTPException(
            status_code=404,
            detail="히스토리를 찾을 수 없거나 접근 권한이 없습니다."
        )
    
    if not history.result_url:
        raise HTTPException(
            status_code=400,
            detail="이미지 URL이 없습니다."
        )
    
    # 2. GCS에서 이미지 다운로드
    try:
        image_bytes = download_from_gcs(history.result_url)
        print(f"✅ 이미지 다운로드 완료: {len(image_bytes)} bytes")
    except Exception as e:
        print(f"❌ GCS 다운로드 실패: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"이미지 다운로드 실패: {str(e)}"
        )
    
    # 3. 파일명 생성
    created_date = history.created_at.strftime("%Y%m%d")
    filename = f"vton_{history.style}_{created_date}_{history_id[:8]}.png"
    
    # 4. 다운로드 응답
    return Response(
        content=image_bytes,
        media_type="image/png",
        headers={
            "Content-Disposition": f"attachment; filename={filename}",
            "Content-Length": str(len(image_bytes))
        }
    )


@router.post("/history/download-batch")
async def download_multiple_vton_results(
    history_ids: List[str],
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    여러 VTON 결과를 ZIP으로 일괄 다운로드
    
    Args:
        history_ids: GenerationHistory ID 목록
    
    Returns:
        ZIP 파일
    """
    
    print(f"\n📦 일괄 다운로드 요청: {len(history_ids)}개")
    
    if len(history_ids) > 50:
        raise HTTPException(
            status_code=400,
            detail="한 번에 최대 50개까지만 다운로드 가능합니다."
        )
    
    # ZIP 파일 생성
    zip_buffer = BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for idx, history_id in enumerate(history_ids, 1):
            # 히스토리 조회
            history = db.query(GenerationHistory).filter(
                GenerationHistory.generation_id == history_id,
                GenerationHistory.user_id == current_user.user_id
            ).first()
            
            if not history or not history.result_url:
                print(f"⚠️ {history_id}: 건너뜀 (없거나 URL 없음)")
                continue
            
            try:
                # GCS에서 다운로드
                image_bytes = download_from_gcs(history.result_url)
                
                # ZIP에 추가
                created_date = history.created_at.strftime("%Y%m%d")
                filename = f"{idx:02d}_vton_{history.style}_{created_date}.png"
                zip_file.writestr(filename, image_bytes)
                
                print(f"✅ {idx}/{len(history_ids)}: {filename} 추가")
                
            except Exception as e:
                print(f"❌ {history_id} 실패: {e}")
                continue
    
    # ZIP 버퍼 되돌리기
    zip_buffer.seek(0)
    
    # 다운로드 응답
    return Response(
        content=zip_buffer.getvalue(),
        media_type="application/zip",
        headers={
            "Content-Disposition": f"attachment; filename=vton_results_{len(history_ids)}.zip"
        }
    )


@router.get("/history/{history_id}/preview")
async def preview_vton_result(
    history_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    VTON 결과 이미지 미리보기 (다운로드 없이)
    
    Args:
        history_id: GenerationHistory ID
    
    Returns:
        PNG 이미지 (inline)
    """
    
    # GenerationHistory 조회
    history = db.query(GenerationHistory).filter(
        GenerationHistory.generation_id == history_id,
        GenerationHistory.user_id == current_user.user_id
    ).first()
    
    if not history:
        raise HTTPException(status_code=404, detail="Not found")
    
    if not history.result_url:
        raise HTTPException(status_code=400, detail="No image URL")
    
    # GCS에서 이미지 다운로드
    try:
        image_bytes = download_from_gcs(history.result_url)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load image: {str(e)}"
        )
    
    # 미리보기 응답 (inline)
    return Response(
        content=image_bytes,
        media_type="image/png",
        headers={
            "Content-Disposition": "inline"  # 다운로드 대신 표시
        }
    )

@router.get("/ad-copy-history", response_model=AdCopyHistoryResponse)
async def get_ad_copy_history(
    page: int = 1,
    limit: int = 12,
    template: str | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(AdCopyHistory, UserContent.product_name, UserContent.category).join(
        UserContent, AdCopyHistory.content_id == UserContent.content_id
    ).filter(AdCopyHistory.user_id == current_user.user_id)

    if template:
        query = query.filter(AdCopyHistory.template_used == template)

    total_count = query.count()
    total_pages = max(1, math.ceil(total_count / limit))
    offset = (page - 1) * limit
    rows = query.order_by(AdCopyHistory.created_at.desc()).limit(limit).offset(offset).all()

    results = []
    for ad_copy, product_name, category in rows:
        raw = ad_copy.ad_copy_data or {}
        results.append(AdCopyHistoryItem(
            ad_copy_id=ad_copy.ad_copy_id,
            template_used=ad_copy.template_used,
            ad_copy_data=AdCopyDataSchema(
                headline=raw.get("headline", ""),
                discount=raw.get("discount"),
                period=raw.get("period"),
                brand=raw.get("brand"),
            ),
            final_image_url=ad_copy.final_image_url,
            created_at=ad_copy.created_at,
            product_name=product_name,
            category=category,
        ))

    return AdCopyHistoryResponse(results=results, total_pages=total_pages)


@router.get("/ad-copy-statistics", response_model=AdCopyStatistics)
async def get_ad_copy_statistics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    from sqlalchemy import func as sa_func

    base_query = db.query(AdCopyHistory).filter(
        AdCopyHistory.user_id == current_user.user_id
    )
    total_count = base_query.count()

    template_rows = db.query(
        AdCopyHistory.template_used,
        sa_func.count(AdCopyHistory.ad_copy_id)
    ).filter(
        AdCopyHistory.user_id == current_user.user_id
    ).group_by(AdCopyHistory.template_used).all()

    template_counts = {style: cnt for style, cnt in template_rows}

    seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)
    recent_7days_count = base_query.filter(
        AdCopyHistory.created_at >= seven_days_ago
    ).count()

    if total_count > 0:
        first = base_query.order_by(AdCopyHistory.created_at.asc()).first()
        days_since = max(1, (datetime.now(timezone.utc) - first.created_at).days + 1)
        average_per_day = round(total_count / days_since, 1)
    else:
        average_per_day = 0.0

    return AdCopyStatistics(
        total_count=total_count,
        template_counts=template_counts,
        recent_7days_count=recent_7days_count,
        average_per_day=average_per_day,
    )


@router.get("/ad-copy-history/{ad_copy_id}", response_model=AdCopyDetail)
async def get_ad_copy_detail(
    ad_copy_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    ad_copy = db.query(AdCopyHistory).filter(
        AdCopyHistory.ad_copy_id == ad_copy_id,
        AdCopyHistory.user_id == current_user.user_id
    ).first()

    if not ad_copy:
        raise HTTPException(status_code=404, detail="Content not found")

    raw = ad_copy.ad_copy_data or {}
    return AdCopyDetail(
        ad_copy_id=ad_copy.ad_copy_id,
        template_used=ad_copy.template_used,
        ad_copy_data=AdCopyDataSchema(
            headline=raw.get("headline", ""),
            discount=raw.get("discount"),
            period=raw.get("period"),
            brand=raw.get("brand"),
        ),
        html_content=ad_copy.html_content,
        final_image_url=ad_copy.final_image_url,
        created_at=ad_copy.created_at,
        processing_time=float(ad_copy.processing_time) if ad_copy.processing_time else None,
    )


@router.delete("/ad-copy-history/{ad_copy_id}")
async def delete_ad_copy(
    ad_copy_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    ad_copy = db.query(AdCopyHistory).filter(
        AdCopyHistory.ad_copy_id == ad_copy_id,
        AdCopyHistory.user_id == current_user.user_id
    ).first()

    if not ad_copy:
        raise HTTPException(status_code=404, detail="Content not found")

    db.delete(ad_copy)
    db.commit()
    return {"success": True, "ad_copy_id": ad_copy_id}


@router.get("/ad-copy-history/{ad_copy_id}/download")
async def download_ad_copy_image(
    ad_copy_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    ad_copy = db.query(AdCopyHistory).filter(
        AdCopyHistory.ad_copy_id == ad_copy_id,
        AdCopyHistory.user_id == current_user.user_id
    ).first()

    if not ad_copy or not ad_copy.final_image_url:
        raise HTTPException(status_code=404, detail="Content not found")

    try:
        image_bytes = download_from_gcs(ad_copy.final_image_url)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"이미지 다운로드 실패: {str(e)}")

    filename = f"ad_{ad_copy.template_used}_{ad_copy_id[:8]}.png"
    return Response(
        content=image_bytes,
        media_type="image/png",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
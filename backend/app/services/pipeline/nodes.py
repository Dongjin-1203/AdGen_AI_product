"""
AdGen Pipeline Nodes
각 단계를 LangGraph 노드로 래핑
pre_check → 실행 → post_check → WebSocket 상태 전송
"""
import uuid
import logging
from datetime import datetime
from typing import Callable, Optional

from app.services.pipeline.state import PipelineState, STEP_NAMES
from app.services.pipeline.validators import PRE_CHECKS, POST_CHECKS
from app.utils.style_matcher import auto_match_style

logger = logging.getLogger(__name__)


# ===== WebSocket 상태 전송 (graph.py에서 주입됨) =====
_ws_broadcast: Optional[Callable] = None

def set_ws_broadcast(fn: Callable):
    """WebSocket 브로드캐스트 함수 주입"""
    global _ws_broadcast
    _ws_broadcast = fn

async def _broadcast(job_id: str, state: PipelineState):
    """현재 상태를 WebSocket으로 전송"""
    if _ws_broadcast:
        await _ws_broadcast(job_id, state)


# ===== 노드 래퍼 =====

def _now() -> str:
    return datetime.utcnow().isoformat()

async def _run_node(
    state: PipelineState,
    step_num: int,
    execute_fn: Callable,
) -> PipelineState:
    """
    공통 노드 실행 로직
    1. pre_check
    2. 상태 업데이트 (running)
    3. execute_fn 실행
    4. post_check
    5. 상태 업데이트 (success/failed)
    6. WebSocket 전송
    """
    step_name = STEP_NAMES[step_num]

    # 1. pre_check
    pre_check = PRE_CHECKS.get(step_name)
    if pre_check:
        ok, err = pre_check(state)
        if not ok:
            state["steps"][step_name]["status"] = "failed"
            state["steps"][step_name]["error"] = err
            state["status"] = "failed"
            state["error"] = err
            state["error_step"] = step_num
            state["updated_at"] = _now()
            await _broadcast(state["job_id"], state)
            logger.error(f"[Node {step_num}] pre_check 실패: {err}")
            return state

    # 2. 실행 중 상태
    state["current_step"] = step_num
    state["status"] = "running"
    state["steps"][step_name]["status"] = "running"
    state["steps"][step_name]["started_at"] = _now()
    state["updated_at"] = _now()
    await _broadcast(state["job_id"], state)
    logger.info(f"[Node {step_num}] {step_name} 시작")

    # 3. 실행
    try:
        state = await execute_fn(state)
    except Exception as e:
        err = str(e)
        state["steps"][step_name]["status"] = "failed"
        state["steps"][step_name]["error"] = err
        state["steps"][step_name]["completed_at"] = _now()
        state["status"] = "failed"
        state["error"] = err
        state["error_step"] = step_num
        state["updated_at"] = _now()
        await _broadcast(state["job_id"], state)
        logger.error(f"[Node {step_num}] {step_name} 실행 오류: {e}", exc_info=True)
        return state

    # 4. post_check
    post_check = POST_CHECKS.get(step_name)
    if post_check:
        ok, err = post_check(state)
        if not ok:
            state["steps"][step_name]["status"] = "failed"
            state["steps"][step_name]["error"] = err
            state["steps"][step_name]["completed_at"] = _now()
            state["status"] = "failed"
            state["error"] = err
            state["error_step"] = step_num
            state["updated_at"] = _now()
            await _broadcast(state["job_id"], state)
            logger.error(f"[Node {step_num}] post_check 실패: {err}")
            return state

    # 5. 성공
    state["steps"][step_name]["status"] = "success"
    state["steps"][step_name]["completed_at"] = _now()
    state["updated_at"] = _now()
    await _broadcast(state["job_id"], state)
    logger.info(f"[Node {step_num}] {step_name} 완료")
    return state


# ===== 각 노드 구현 =====

async def node_select_image(state: PipelineState) -> PipelineState:
    """Node 1: 상품 이미지 선택 및 메타데이터 로드"""
    async def _execute(state: PipelineState) -> PipelineState:
        from app.db.base import SessionLocal
        from app.models.schemas import UserContent

        db = SessionLocal()
        try:
            content = db.query(UserContent).filter(
                UserContent.content_id == state["content_id"]
            ).first()

            if not content:
                raise ValueError(f"content_id={state['content_id']} 를 찾을 수 없습니다.")

            state["product_image_url"] = content.image_url
            state["product_category"] = content.category
            state["steps"]["select_image"]["result_url"] = content.image_url
        finally:
            db.close()

        return state

    return await _run_node(state, 1, _execute)


async def node_remove_background(state: PipelineState) -> PipelineState:
    """Node 2: 배경 제거 (RMBG-2.0)"""
    async def _execute(state: PipelineState) -> PipelineState:
        import io
        import requests
        from PIL import Image
        from app.services.img_processing.background_removal import BackgroundRemovalService
        from app.core.storage import upload_to_gcs_async

        # 이미지 다운로드
        resp = requests.get(state["product_image_url"], timeout=30)
        resp.raise_for_status()
        original_image = Image.open(io.BytesIO(resp.content))

        # 배경 제거
        service = BackgroundRemovalService()
        removed = await service.remove_background(original_image)

        # GCS 업로드
        buf = io.BytesIO()
        removed.save(buf, format="PNG")
        result_url = await upload_to_gcs_async(
            file_data=buf.getvalue(),
            destination_path=f"pipeline/{state['job_id']}/removed_bg.png",
            content_type="image/png"
        )

        state["removed_bg_url"] = result_url
        state["steps"]["remove_background"]["result_url"] = result_url
        return state

    return await _run_node(state, 2, _execute)


async def node_virtual_fitting(state: PipelineState) -> PipelineState:
    """Node 3: 가상 모델 피팅 (IDM-VTON) - 카테고리 충돌 감지 포함"""
    async def _execute(state: PipelineState) -> PipelineState:
        import io
        import requests
        from PIL import Image
        from app.services.generation.vton_replicate_generator import get_vton_service
        from app.core.storage import upload_to_gcs_async

        # 배경 제거 이미지 로드
        resp = requests.get(state["removed_bg_url"], timeout=30)
        resp.raise_for_status()
        garment_image = Image.open(io.BytesIO(resp.content))

        # VTON 실행
        vton_service = get_vton_service()
        result_image = vton_service.generate_fashion_ad(
            garment_image=garment_image,
            style=state["style"],
            model_index=state.get("model_index"),
            user_prompt=state.get("user_prompt"),
        )

        # GCS 업로드
        buf = io.BytesIO()
        result_image.save(buf, format="PNG")
        result_url = await upload_to_gcs_async(
            file_data=buf.getvalue(),
            destination_path=f"pipeline/{state['job_id']}/fitted.png",
            content_type="image/png"
        )

        state["fitted_image_url"] = result_url
        state["steps"]["virtual_fitting"]["result_url"] = result_url
        return state

    return await _run_node(state, 3, _execute)


async def node_generate_background(state: PipelineState) -> PipelineState:
    """Node 4: 배경 생성 (Gemini 2.5 Flash Image)"""
    async def _execute(state: PipelineState) -> PipelineState:
        import io
        import requests
        from PIL import Image
        from app.services.generation.gemini_generator import GeminiImageGenerator  # ← 변경
        from app.core.storage import upload_to_gcs_async

        resp = requests.get(state["fitted_image_url"], timeout=30)
        resp.raise_for_status()
        fitted_image = Image.open(io.BytesIO(resp.content))

        # Gemini 이미지 생성 (GPU 서버 대신)
        generator = GeminiImageGenerator()
        result_image = generator.generate_fashion_ad(
            product_image=fitted_image,
            style=state["style"],
            user_prompt=state.get("user_prompt"),
        )

        buf = io.BytesIO()
        result_image.save(buf, format="PNG")
        result_url = await upload_to_gcs_async(
            file_data=buf.getvalue(),
            destination_path=f"pipeline/{state['job_id']}/background.png",
            content_type="image/png"
        )

        state["background_image_url"] = result_url
        state["steps"]["generate_background"]["result_url"] = result_url

        # GenerationHistory DB 저장
        import uuid as _uuid
        from app.db.base import SessionLocal
        from app.models.schemas import GenerationHistory
        db = SessionLocal()
        try:
            history = GenerationHistory(
                generation_id=str(_uuid.uuid4()),
                content_id=state["content_id"],
                user_id=state["user_id"],
                style=state["style"],
                result_url=result_url,
                processing_time=0,
            )
            db.add(history)
            db.commit()
            db.refresh(history)
            state["generation_id"] = history.generation_id
        finally:
            db.close()

        return state

    return await _run_node(state, 4, _execute)


async def node_generate_caption(state: PipelineState) -> PipelineState:
    """Node 5: 광고 캡션 생성 (OpenAI GPT-4o)"""
    async def _execute(state: PipelineState) -> PipelineState:
        import json
        from openai import OpenAI
        from config import settings

        client = OpenAI(api_key=settings.OPENAI_API_KEY, timeout=30.0)

        system_prompt = """당신은 패션 광고 카피라이터입니다.
1-2문장으로 간결하고 감성적인 한글 광고 캡션을 작성하세요. (최대 50자, 이모지 포함)
반드시 JSON으로만 응답: {"caption": "...", "confidence": 0.9}"""

        user_message = f"""스타일: {state['style']}
카테고리: {state.get('product_category', '패션')}
추가 요청: {state.get('user_prompt', '없음')}"""

        # ⭐ ad_inputs 추가
        ad_inputs = state.get('ad_inputs')
        if ad_inputs:
            print(f"📝 캡션 생성 시 사용자 입력 반영:")
            
            if ad_inputs.get('keywords'):
                keywords = ad_inputs['keywords']
                if isinstance(keywords, list):
                    keywords_str = ', '.join(keywords)
                else:
                    keywords_str = keywords
                user_message += f"\n\n반드시 포함할 키워드: {keywords_str}"
                print(f"   - 키워드: {keywords_str}")
            
            if ad_inputs.get('must_include'):
                must_include = ad_inputs['must_include']
                user_message += f"\n\n⚠️ 반드시 포함해야 할 문구: {must_include}"
                user_message += f"\n위 문구를 캡션에 자연스럽게 포함시키세요."
                print(f"   - 필수 문구: {must_include}")

        response = client.chat.completions.create(
            model="gpt-5-chat-latest",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            temperature=0.8,
            max_tokens=200,
            response_format={"type": "json_object"},
        )

        result = json.loads(response.choices[0].message.content)
        caption = result.get("caption", "").strip()

        if not caption:
            raise ValueError("캡션 생성 결과가 비어있습니다.")

        state["caption"] = caption

        # AdCaption DB 저장
        import uuid as _uuid
        from app.db.base import SessionLocal
        from app.models.caption_system import AdCaption
        db = SessionLocal()
        try:
            ad_caption = AdCaption(
                caption_id=str(_uuid.uuid4()),
                content_id=state["content_id"],
                user_id=state["user_id"],
                generation_id=state["generation_id"],
                ai_caption=caption,
                final_caption=caption,
                is_modified=False,
                style=state["style"],
            )
            db.add(ad_caption)
            db.commit()
            db.refresh(ad_caption)
            state["caption_id"] = ad_caption.caption_id
        finally:
            db.close()

        return state

    return await _run_node(state, 5, _execute)


async def node_generate_html(state: PipelineState) -> PipelineState:
    """Node 6: HTML 광고 페이지 생성 (OpenAI GPT-4o)"""
    async def _execute(state: PipelineState) -> PipelineState:
        from app.services.html.ad_generator import AdGenerator
        from app.db.base import SessionLocal
        from app.models.schemas import UserContent
        import uuid as _uuid
        from app.models.caption_system import AdCopyHistory

        # Vision AI 결과 조회
        db = SessionLocal()
        try:
            content = db.query(UserContent).filter(
                UserContent.content_id == state["content_id"]
            ).first()

            import json
            style_tags = content.style_tags or "[]"
            if isinstance(style_tags, str):
                try:
                    style_tags = json.loads(style_tags)
                except:
                    style_tags = []

            vision_result = {
                "category": content.category,
                "sub_category": content.sub_category,
                "color": content.color,
                "material": content.material,
                "fit": content.fit,
                "style_tags": style_tags,
            }

            print("=" * 50)
            print("🔍 스타일 선택 시작")
            print(f"📦 state.style = {state.get('style')}")
            print(f"📦 vision_result = {vision_result}")

            selected_style = state["style"]
            print(f"✅ 선택된 K-Fashion 컨셉: {selected_style}")

            print(f"✅ 최종 선택 스타일: {selected_style}")
            print("=" * 50)
            
            generator = AdGenerator()
            result = generator.generate_html_with_template(
                vision_result=vision_result,
                image_url=state["background_image_url"],
                template_name=selected_style,
                caption=state["caption"],
                ad_inputs=state.get("ad_inputs")
            )

            state["html_content"] = result["html"]
            state["selected_style"] = selected_style

            # AdCopyHistory DB 저장
            ad_copy = AdCopyHistory(
                ad_copy_id=str(_uuid.uuid4()),
                content_id=state["content_id"],
                user_id=state["user_id"],
                caption_id=state["caption_id"],
                generation_id=state["generation_id"],
                ad_copy_data=result["ad_copy"],
                template_used=selected_style,
                html_content=result["html"],
            )
            db.add(ad_copy)
            db.commit()
            db.refresh(ad_copy)
            state["ad_copy_id"] = ad_copy.ad_copy_id
        finally:
            db.close()

        return state

    return await _run_node(state, 6, _execute)


async def node_save_image(state: PipelineState) -> PipelineState:
    """Node 7: HTML → PNG 이미지 저장 (Playwright)"""
    async def _execute(state: PipelineState) -> PipelineState:
        from app.core.html_renderer import render_html_to_png
        from app.core.storage import upload_to_gcs_async  
        import uuid as _uuid
        from app.db.base import SessionLocal
        from app.models.caption_system import AdCopyHistory

        # HTML → PNG
        image_bytes = await render_html_to_png(state["html_content"], 1080, 1080)

        # GCS 업로드
        filename = f"ad_minimal_{_uuid.uuid4()}.png"
        destination_path = f"{state['user_id']}/ads/{filename}"

        image_url = await upload_to_gcs_async(
            file_data=image_bytes,
            destination_path=destination_path,
            content_type='image/png'
        )

        state["final_image_url"] = image_url
        state["steps"]["save_image"]["result_url"] = image_url

        # AdCopyHistory 업데이트
        db = SessionLocal()
        try:
            ad_copy = db.query(AdCopyHistory).filter(
                AdCopyHistory.ad_copy_id == state["ad_copy_id"]
            ).first()
            if ad_copy:
                ad_copy.final_image_url = image_url
                db.commit()
        finally:
            db.close()

        return state

    return await _run_node(state, 7, _execute)

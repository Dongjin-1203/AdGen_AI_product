"""
Replicate IDM-VTON 기반 패션 광고 생성 서비스
가상 피팅 (Virtual Try-On) + 스타일별 배경
"""
import replicate
from PIL import Image
import io
import logging
import requests
from typing import Optional
import random
import time

from config import settings
from app.core.storage import upload_to_gcs

logger = logging.getLogger(__name__)


class ReplicateVTONService:
    """Replicate IDM-VTON을 사용한 광고 생성"""
    
    def __init__(self):
        """Replicate 클라이언트 초기화"""
        if not settings.REPLICATE_API_TOKEN:
            raise ValueError("REPLICATE_API_TOKEN not found in settings")
        
        # ⭐ Client 인스턴스 생성
        self.client = replicate.Client(api_token=settings.REPLICATE_API_TOKEN)
        self.api_token = settings.REPLICATE_API_TOKEN
        
        logger.info(f"🔑 Replicate Client initialized")
        logger.info(f"   Token: {self.api_token[:10] if self.api_token else 'None'}...")
        
        # GCS 버킷 이름
        bucket_name = settings.GCS_BUCKET_NAME or "adgen-ai-storage"
        
        # ⭐ GCS에서 실제 존재하는 모델 이미지 목록 로드
        logger.info("📁 Loading K-Fashion models from GCS...")
        self.K_FASHION_MODELS = self._load_models_from_gcs(bucket_name)
        
        logger.info("✅ Replicate VTON Service initialized")
        logger.info(f"   Bucket: {bucket_name}")
        logger.info(f"   Models loaded: {sum(len(v) for v in self.K_FASHION_MODELS.values())} images")
        if self.K_FASHION_MODELS.get('resort'):
            logger.info(f"   Sample resort URL: {self.K_FASHION_MODELS['resort'][0]}")
    
    def _load_models_from_gcs(self, bucket_name: str) -> dict:
        """
        GCS에서 실제 존재하는 모델 이미지 목록 로드
        
        Returns:
            {
                'resort': ['https://...resort_00.jpg', ...],
                'retro': [...],
                'romantic': [...]
            }
        """
        from app.core.storage import get_storage_client
        
        client = get_storage_client()
        bucket = client.bucket(bucket_name)
        
        models = {}
        
        for style in ['resort', 'retro', 'romantic']:
            prefix = f"k-fashion-models/{style}/"
            blobs = list(bucket.list_blobs(prefix=prefix))
            
            # .jpg 파일만 필터링 (mask, json 제외)
            jpg_files = [
                f"https://storage.googleapis.com/{bucket_name}/{blob.name}"
                for blob in blobs
                if blob.name.endswith('.jpg') 
                and not blob.name.endswith('_mask.jpg')
                and not blob.name.endswith('.json')
            ]
            
            models[style] = jpg_files
            logger.info(f"   ✅ {style}: {len(jpg_files)} models loaded")
        
        total = sum(len(v) for v in models.values())
        logger.info(f"📁 Total models loaded: {total} images")
        
        return models
    
    def generate_fashion_ad(
        self,
        garment_image: Image.Image,
        style: str = "resort",
        model_index: Optional[int] = None,
        user_prompt: Optional[str] = None
    ) -> Image.Image:
        """패션 광고 이미지 생성 (VTON) """
        temp_garment_url = None
        
        try:
            logger.info(f"🎨 [VTON] Starting generation")
            logger.info(f"   [VTON] Style: {style}")
            logger.info(f"   [VTON] Model index: {model_index}")
            logger.info(f"   [VTON] Garment size: {garment_image.size}")
            
            # 1. 의류 이미지를 GCS에 임시 업로드
            timestamp = int(time.time())
            temp_filename = f"temp/garment_{timestamp}.png"
            
            garment_bytes = io.BytesIO()
            garment_image.save(garment_bytes, format='PNG')
            garment_bytes.seek(0)
            
            logger.info(f"[VTON] Step 1: Uploading garment to GCS: {temp_filename}")
            temp_garment_url = upload_to_gcs(
                file_data=garment_bytes.getvalue(),
                destination_path=temp_filename,
                content_type='image/png'
            )
            logger.info(f"[VTON] Step 1: ✅ Garment uploaded: {temp_garment_url}")
            
            if not temp_garment_url:
                raise ValueError("❌ Garment upload failed: temp_garment_url is None")
            
            # 2. K-Fashion 모델 선택
            logger.info(f"[VTON] Step 2: Selecting K-Fashion model...")
            model_image_url = self._get_model_image(style, model_index)
            logger.info(f"[VTON] Step 2: ✅ Selected model: {model_image_url}")
            
            if not model_image_url:
                raise ValueError(f"❌ Model URL is None for style={style}")
            
            # 3. Replicate IDM-VTON API 호출
            logger.info("[VTON] Step 3: Calling Replicate API...")
            
            output = self.client.run(
                "cuuupid/idm-vton:c871bb9b046607b680449ecbae55fd8c6d945e0a1948644bf2361b3d021d3ff4",
                input={
                    "garm_img": temp_garment_url,
                    "human_img": model_image_url,
                    "garment_des": f"A {style} style garment",
                    "category": "upper_body",
                    "steps": 30,
                    "seed": 42
                }
            )
            
            logger.info(f"[VTON] Step 3: ✅ API response received")
            
            # 4. 결과 이미지 다운로드
            if isinstance(output, str):
                result_url = output
            elif isinstance(output, list) and len(output) > 0:
                result_url = output[0]
            else:
                raise Exception(f"Unexpected output format: {type(output)}")
            
            logger.info(f"[VTON] Step 4: Downloading result from: {result_url}")
            
            response = requests.get(result_url, timeout=60)
            response.raise_for_status()
            
            result_image = Image.open(io.BytesIO(response.content))
            
            logger.info(f"✅ [VTON] Generation completed successfully")
            logger.info(f"   [VTON] Result size: {result_image.size}")
            
            return result_image
            
        except Exception as e:
            logger.error(f"❌ [VTON] Generation failed", exc_info=True)
            raise Exception(f"Replicate 가상 피팅 실패: {str(e)}")
        
        finally:
            if temp_garment_url:
                logger.info(f"[VTON] Temp file created: {temp_garment_url}")
    
    def _get_model_image(self, style: str, model_index: Optional[int] = None) -> str:
        """스타일에 맞는 K-Fashion 모델 이미지 가져오기"""
        logger.info(f"   [_get_model_image] Input: style={style}, model_index={model_index}")
        
        # 스타일 검증
        if style not in self.K_FASHION_MODELS:
            logger.warning(f"   [_get_model_image] ⚠️ Unknown style '{style}', defaulting to 'resort'")
            style = 'resort'
        
        models = self.K_FASHION_MODELS[style]
        logger.info(f"   [_get_model_image] Available models for '{style}': {len(models)} images")
        
        # 모델이 없는 경우
        if not models:
            logger.error(f"   [_get_model_image] ❌ No models found for style '{style}'")
            raise ValueError(f"No models available for style '{style}'")
        
        # 인덱스 처리
        if model_index is None:
            model_index = random.randint(0, len(models) - 1)
            logger.info(f"   [_get_model_image] Random index selected: {model_index}")
        else:
            model_index = model_index % len(models)
        
        model_url = models[model_index]
        
        logger.info(f"   [_get_model_image] ✅ Returning URL: {model_url}")
        
        return model_url
    
    def health_check(self) -> bool:
        """Replicate API 상태 확인"""
        try:
            if not self.api_token or not self.api_token.startswith('r8_'):
                logger.error("Invalid Replicate API token format")
                return False
            
            logger.info("Replicate health check passed")
            return True
            
        except Exception as e:
            logger.error(f"Replicate health check failed: {e}")
            return False


# 싱글톤 인스턴스
_vton_service = None

def get_vton_service() -> ReplicateVTONService:
    """VTON 서비스 싱글톤 가져오기"""
    global _vton_service
    
    if _vton_service is None:
        _vton_service = ReplicateVTONService()
    
    return _vton_service
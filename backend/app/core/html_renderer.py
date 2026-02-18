"""
HTML을 PNG로 렌더링하는 유틸리티
Windows 호환 버전 (html2image 사용)
"""
from html2image import Html2Image
from PIL import Image
import io
import logging
import tempfile
import os

logger = logging.getLogger(__name__)


def _render_html_to_png_sync(html_content: str, width: int = 1080, height: int = 1080) -> bytes:
    """
    HTML을 PNG 이미지로 변환 (동기 함수 - 내부용)
    
    Windows 호환성을 위해 html2image 사용
    
    Args:
        html_content: HTML 문자열
        width: 이미지 너비
        height: 이미지 높이
    
    Returns:
        PNG 이미지 바이트
    """
    try:
        # html2image 인스턴스 생성
        hti = Html2Image(size=(width, height))
        
        # 임시 디렉토리에 렌더링
        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = os.path.join(tmpdir, 'temp.png')
            
            # HTML → PNG 변환
            hti.screenshot(
                html_str=html_content,
                save_as='temp.png',
                size=(width, height)
            )
            
            # PNG 읽기
            png_path = os.path.join(hti.output_path, 'temp.png')
            
            with Image.open(png_path) as img:
                # RGB로 변환 (투명도 제거)
                if img.mode in ('RGBA', 'LA', 'P'):
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    img = background
                
                # bytes로 변환
                img_byte_arr = io.BytesIO()
                img.save(img_byte_arr, format='PNG')
                img_byte_arr.seek(0)
                png_bytes = img_byte_arr.getvalue()
        
        logger.info(f"✅ HTML rendered: {len(png_bytes)} bytes")
        return png_bytes
        
    except Exception as e:
        logger.error(f"❌ HTML rendering failed: {e}")
        raise Exception(f"HTML 렌더링 실패: {str(e)}")


# 비동기 인터페이스 (nodes.py에서 사용)
async def render_html_to_png(html_content: str, width: int = 1080, height: int = 1080) -> bytes:
    """
    HTML을 PNG 이미지로 변환 (비동기 인터페이스)
    
    내부적으로 동기 함수를 executor에서 실행
    
    Args:
        html_content: HTML 문자열
        width: 이미지 너비
        height: 이미지 높이
    
    Returns:
        PNG 이미지 바이트
    """
    import asyncio
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _render_html_to_png_sync, html_content, width, height)
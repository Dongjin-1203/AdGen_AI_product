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
    try:
        chrome_path = os.getenv('CHROME_BIN', '/usr/bin/chromium')
        logger.info(f"🔍 Chrome 경로: {chrome_path}")
        
        with tempfile.TemporaryDirectory() as tmpdir:
            hti = Html2Image(
                size=(width, height),
                browser_executable=chrome_path,
                output_path=tmpdir,
                custom_flags=[
                    '--headless=new',           # ⭐ 핵심 - 헤드리스 모드
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-gpu',            # ⭐ GPU 없는 환경 대응
                    '--disable-setuid-sandbox',
                    '--single-process',         # ⭐ Cloud Run 단일 프로세스
                    '--no-zygote',              # ⭐ zygote 프로세스 비활성화
                ]
            )
            
            hti.screenshot(
                html_str=html_content,
                save_as='temp.png',
                size=(width, height)
            )
            
            png_path = os.path.join(tmpdir, 'temp.png')
            
            if not os.path.exists(png_path):
                raise Exception(f"PNG 파일 생성 실패: {png_path}")
            
            with Image.open(png_path) as img:
                if img.mode in ('RGBA', 'LA', 'P'):
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    img = background
                
                img_byte_arr = io.BytesIO()
                img.save(img_byte_arr, format='PNG')
                img_byte_arr.seek(0)
                png_bytes = img_byte_arr.getvalue()
        
        logger.info(f"✅ HTML rendered: {len(png_bytes)} bytes")
        return png_bytes
        
    except Exception as e:
        logger.error(f"❌ HTML rendering failed: {e}", exc_info=True)
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
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, _render_html_to_png_sync, html_content, width, height)
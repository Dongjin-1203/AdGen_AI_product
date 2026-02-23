"""
HTML을 PNG로 렌더링하는 유틸리티
Playwright 사용 (Cloud Run 환경 최적화)
"""
import asyncio
import logging
import os

logger = logging.getLogger(__name__)


async def render_html_to_png(html_content: str, width: int = 1080, height: int = 1080) -> bytes:
    """
    HTML을 PNG 이미지로 변환 (Playwright 비동기)
    
    Args:
        html_content: HTML 문자열
        width: 이미지 너비
        height: 이미지 높이
    
    Returns:
        PNG 이미지 바이트
    """
    try:
        from playwright.async_api import async_playwright

        logger.info(f"🖥️ Playwright 렌더링 시작: {width}x{height}")

        async with async_playwright() as p:
            browser = await p.chromium.launch(
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-gpu',
                ]
            )
            
            page = await browser.new_page(
                viewport={"width": width, "height": height}
            )
            
            await page.set_content(html_content, wait_until="networkidle")
            
            screenshot_bytes = await page.screenshot(
                type="png",
                clip={"x": 0, "y": 0, "width": width, "height": height}
            )
            
            await browser.close()

        logger.info(f"✅ Playwright 렌더링 완료: {len(screenshot_bytes)} bytes")
        return screenshot_bytes

    except Exception as e:
        logger.error(f"❌ Playwright 렌더링 실패: {e}", exc_info=True)
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
    return await loop.run_in_executor(None, render_html_to_png, html_content, width, height)
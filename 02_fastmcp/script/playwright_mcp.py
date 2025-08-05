#!/usr/bin/env python3
"""
Playwright FastMCP 서버

Playwright를 사용하여 웹 브라우저 자동화 기능을 MCP 도구로 제공합니다.
LLM이 웹페이지를 탐색하고, 스크린샷을 찍고, 폼을 작성할 수 있습니다.
"""

import asyncio
import base64
import json
import os
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastmcp import FastMCP, Context
from playwright.async_api import async_playwright, Browser, Page, BrowserContext


# Playwright MCP 서버 인스턴스 생성
playwright_mcp = FastMCP("Playwright MCP 서버 🎭")

# 전역 변수들
browser: Optional[Browser] = None
context: Optional[BrowserContext] = None
current_page: Optional[Page] = None
playwright_instance = None


# =============================================================================
# 브라우저 관리 도구들
# =============================================================================

@playwright_mcp.tool
async def start_browser(headless: bool = True, browser_type: str = "chromium", ctx: Context = None) -> str:
    """브라우저를 시작합니다."""
    global browser, context, current_page, playwright_instance
    
    try:
        if ctx:
            await ctx.info(f"브라우저 시작 중... (타입: {browser_type}, 헤드리스: {headless})")
        
        playwright_instance = await async_playwright().start()
        
        if browser_type == "chromium":
            browser = await playwright_instance.chromium.launch(headless=headless)
        elif browser_type == "firefox":
            browser = await playwright_instance.firefox.launch(headless=headless)
        elif browser_type == "webkit":
            browser = await playwright_instance.webkit.launch(headless=headless)
        else:
            return f"지원되지 않는 브라우저 타입: {browser_type}"
        
        # 새 컨텍스트와 페이지 생성
        context = await browser.new_context(
            viewport={"width": 1280, "height": 720},
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        )
        current_page = await context.new_page()
        
        if ctx:
            await ctx.info("브라우저가 성공적으로 시작되었습니다!")
        
        return f"브라우저 ({browser_type})가 성공적으로 시작되었습니다. 헤드리스 모드: {headless}"
    
    except Exception as e:
        if ctx:
            await ctx.error(f"브라우저 시작 실패: {str(e)}")
        return f"브라우저 시작 실패: {str(e)}"


@playwright_mcp.tool
async def close_browser(ctx: Context = None) -> str:
    """브라우저를 종료합니다."""
    global browser, context, current_page, playwright_instance
    
    try:
        if ctx:
            await ctx.info("브라우저 종료 중...")
        
        if current_page:
            await current_page.close()
            current_page = None
        
        if context:
            await context.close()
            context = None
        
        if browser:
            await browser.close()
            browser = None
            
        if playwright_instance:
            await playwright_instance.stop()
            playwright_instance = None
        
        if ctx:
            await ctx.info("브라우저가 성공적으로 종료되었습니다!")
        
        return "브라우저가 성공적으로 종료되었습니다."
    
    except Exception as e:
        if ctx:
            await ctx.error(f"브라우저 종료 실패: {str(e)}")
        return f"브라우저 종료 실패: {str(e)}"


# =============================================================================
# 웹페이지 탐색 도구들
# =============================================================================

@playwright_mcp.tool
async def navigate_to_url(url: str, ctx: Context = None) -> str:
    """지정된 URL로 이동합니다."""
    if not current_page:
        return "브라우저가 시작되지 않았습니다. 먼저 start_browser를 호출하세요."
    
    try:
        if ctx:
            await ctx.info(f"URL로 이동 중: {url}")
        
        response = await current_page.goto(url, wait_until="domcontentloaded", timeout=30000)
        
        if response:
            status = response.status
            title = await current_page.title()
            current_url = current_page.url
            
            if ctx:
                await ctx.info(f"페이지 로드 완료: {title}")
            
            return f"성공적으로 페이지에 접근했습니다.\n제목: {title}\nURL: {current_url}\n상태 코드: {status}"
        else:
            return f"페이지 로드에 실패했습니다: {url}"
    
    except Exception as e:
        if ctx:
            await ctx.error(f"페이지 로드 실패: {str(e)}")
        return f"페이지 로드 실패: {str(e)}"


@playwright_mcp.tool
async def get_page_info(ctx: Context = None) -> str:
    """현재 페이지의 기본 정보를 가져옵니다."""
    if not current_page:
        return "브라우저가 시작되지 않았습니다."
    
    try:
        title = await current_page.title()
        url = current_page.url
        content = await current_page.content()
        
        page_info = {
            "title": title,
            "url": url,
            "content_length": len(content),
            "viewport": await current_page.evaluate("() => ({ width: window.innerWidth, height: window.innerHeight })")
        }
        
        if ctx:
            await ctx.info(f"페이지 정보 조회 완료: {title}")
        
        return json.dumps(page_info, ensure_ascii=False, indent=2)
    
    except Exception as e:
        if ctx:
            await ctx.error(f"페이지 정보 조회 실패: {str(e)}")
        return f"페이지 정보 조회 실패: {str(e)}"


@playwright_mcp.tool
async def get_page_text(selector: str = "body", ctx: Context = None) -> str:
    """페이지에서 텍스트를 추출합니다."""
    if not current_page:
        return "브라우저가 시작되지 않았습니다."
    
    try:
        if ctx:
            await ctx.info(f"텍스트 추출 중 (셀렉터: {selector})")
        
        # 요소가 존재하는지 확인
        element = await current_page.query_selector(selector)
        if not element:
            return f"셀렉터 '{selector}'에 해당하는 요소를 찾을 수 없습니다."
        
        text_content = await element.text_content()
        
        if ctx:
            await ctx.info(f"텍스트 추출 완료 (길이: {len(text_content) if text_content else 0})")
        
        return text_content or "텍스트가 없습니다."
    
    except Exception as e:
        if ctx:
            await ctx.error(f"텍스트 추출 실패: {str(e)}")
        return f"텍스트 추출 실패: {str(e)}"


# =============================================================================
# 스크린샷 도구들
# =============================================================================

@playwright_mcp.tool
async def take_screenshot(filename: str = None, full_page: bool = False, ctx: Context = None) -> str:
    """현재 페이지의 스크린샷을 찍습니다."""
    if not current_page:
        return "브라우저가 시작되지 않았습니다."
    
    try:
        if ctx:
            await ctx.info("스크린샷 촬영 중...")
        
        # 파일명이 지정되지 않았으면 자동 생성
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}.png"
        
        # 임시 디렉토리에 저장
        screenshot_path = Path(tempfile.gettempdir()) / f"playwright_{filename}"
        
        # 스크린샷 촬영
        await current_page.screenshot(
            path=str(screenshot_path), 
            full_page=full_page,
            type="png"
        )
        
        # 파일 크기 확인
        file_size = screenshot_path.stat().st_size
        
        if ctx:
            await ctx.info(f"스크린샷 저장 완료: {screenshot_path}")
        
        return f"스크린샷이 저장되었습니다.\n경로: {screenshot_path}\n크기: {file_size} bytes\n전체 페이지: {full_page}"
    
    except Exception as e:
        if ctx:
            await ctx.error(f"스크린샷 촬영 실패: {str(e)}")
        return f"스크린샷 촬영 실패: {str(e)}"


@playwright_mcp.tool
async def take_element_screenshot(selector: str, filename: str = None, ctx: Context = None) -> str:
    """특정 요소의 스크린샷을 찍습니다."""
    if not current_page:
        return "브라우저가 시작되지 않았습니다."
    
    try:
        if ctx:
            await ctx.info(f"요소 스크린샷 촬영 중 (셀렉터: {selector})")
        
        # 요소 찾기
        element = await current_page.query_selector(selector)
        if not element:
            return f"셀렉터 '{selector}'에 해당하는 요소를 찾을 수 없습니다."
        
        # 파일명이 지정되지 않았으면 자동 생성
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"element_screenshot_{timestamp}.png"
        
        # 임시 디렉토리에 저장
        screenshot_path = Path(tempfile.gettempdir()) / f"playwright_{filename}"
        
        # 요소 스크린샷 촬영
        await element.screenshot(path=str(screenshot_path))
        
        # 파일 크기 확인
        file_size = screenshot_path.stat().st_size
        
        if ctx:
            await ctx.info(f"요소 스크린샷 저장 완료: {screenshot_path}")
        
        return f"요소 스크린샷이 저장되었습니다.\n경로: {screenshot_path}\n크기: {file_size} bytes\n셀렉터: {selector}"
    
    except Exception as e:
        if ctx:
            await ctx.error(f"요소 스크린샷 촬영 실패: {str(e)}")
        return f"요소 스크린샷 촬영 실패: {str(e)}"


# =============================================================================
# 요소 상호작용 도구들
# =============================================================================

@playwright_mcp.tool
async def click_element(selector: str, ctx: Context = None) -> str:
    """지정된 셀렉터의 요소를 클릭합니다."""
    if not current_page:
        return "브라우저가 시작되지 않았습니다."
    
    try:
        if ctx:
            await ctx.info(f"요소 클릭 중 (셀렉터: {selector})")
        
        # 요소가 존재하고 클릭 가능한지 확인
        await current_page.wait_for_selector(selector, timeout=10000)
        await current_page.click(selector)
        
        if ctx:
            await ctx.info("요소 클릭 완료")
        
        return f"요소 '{selector}'를 성공적으로 클릭했습니다."
    
    except Exception as e:
        if ctx:
            await ctx.error(f"요소 클릭 실패: {str(e)}")
        return f"요소 클릭 실패: {str(e)}"


@playwright_mcp.tool
async def fill_input(selector: str, text: str, ctx: Context = None) -> str:
    """입력 필드에 텍스트를 입력합니다."""
    if not current_page:
        return "브라우저가 시작되지 않았습니다."
    
    try:
        if ctx:
            await ctx.info(f"텍스트 입력 중 (셀렉터: {selector})")
        
        # 요소가 존재하는지 확인
        await current_page.wait_for_selector(selector, timeout=10000)
        await current_page.fill(selector, text)
        
        if ctx:
            await ctx.info("텍스트 입력 완료")
        
        return f"'{selector}' 필드에 텍스트를 성공적으로 입력했습니다."
    
    except Exception as e:
        if ctx:
            await ctx.error(f"텍스트 입력 실패: {str(e)}")
        return f"텍스트 입력 실패: {str(e)}"


@playwright_mcp.tool
async def wait_for_element(selector: str, timeout: int = 10000, ctx: Context = None) -> str:
    """지정된 요소가 나타날 때까지 기다립니다."""
    if not current_page:
        return "브라우저가 시작되지 않았습니다."
    
    try:
        if ctx:
            await ctx.info(f"요소 대기 중 (셀렉터: {selector}, 타임아웃: {timeout}ms)")
        
        await current_page.wait_for_selector(selector, timeout=timeout)
        
        if ctx:
            await ctx.info("요소가 나타났습니다!")
        
        return f"요소 '{selector}'가 성공적으로 나타났습니다."
    
    except Exception as e:
        if ctx:
            await ctx.error(f"요소 대기 실패: {str(e)}")
        return f"요소 대기 실패: {str(e)}"


# =============================================================================
# 페이지 평가 도구들
# =============================================================================

@playwright_mcp.tool
async def evaluate_javascript(script: str, ctx: Context = None) -> str:
    """페이지에서 JavaScript 코드를 실행합니다."""
    if not current_page:
        return "브라우저가 시작되지 않았습니다."
    
    try:
        if ctx:
            await ctx.info("JavaScript 코드 실행 중...")
        
        result = await current_page.evaluate(script)
        
        if ctx:
            await ctx.info("JavaScript 코드 실행 완료")
        
        return json.dumps({"result": result}, ensure_ascii=False, indent=2)
    
    except Exception as e:
        if ctx:
            await ctx.error(f"JavaScript 실행 실패: {str(e)}")
        return f"JavaScript 실행 실패: {str(e)}"


@playwright_mcp.tool
async def get_elements_info(selector: str, ctx: Context = None) -> str:
    """지정된 셀렉터의 모든 요소 정보를 가져옵니다."""
    if not current_page:
        return "브라우저가 시작되지 않았습니다."
    
    try:
        if ctx:
            await ctx.info(f"요소 정보 조회 중 (셀렉터: {selector})")
        
        elements = await current_page.query_selector_all(selector)
        
        elements_info = []
        for i, element in enumerate(elements):
            text_content = await element.text_content()
            inner_html = await element.inner_html()
            tag_name = await element.evaluate("el => el.tagName")
            
            elements_info.append({
                "index": i,
                "tag_name": tag_name,
                "text_content": text_content[:100] + "..." if text_content and len(text_content) > 100 else text_content,
                "inner_html_length": len(inner_html) if inner_html else 0
            })
        
        if ctx:
            await ctx.info(f"{len(elements_info)}개의 요소 정보 조회 완료")
        
        return json.dumps({
            "selector": selector,
            "count": len(elements_info),
            "elements": elements_info
        }, ensure_ascii=False, indent=2)
    
    except Exception as e:
        if ctx:
            await ctx.error(f"요소 정보 조회 실패: {str(e)}")
        return f"요소 정보 조회 실패: {str(e)}"


# =============================================================================
# 리소스들
# =============================================================================

@playwright_mcp.resource("browser://status")
def get_browser_status() -> str:
    """현재 브라우저 상태를 반환합니다."""
    status = {
        "browser_started": browser is not None,
        "context_available": context is not None,
        "page_available": current_page is not None,
        "current_url": current_page.url if current_page else None,
        "playwright_instance": playwright_instance is not None
    }
    
    return json.dumps(status, ensure_ascii=False, indent=2)


@playwright_mcp.resource("screenshots://list")
def list_screenshots() -> str:
    """저장된 스크린샷 목록을 반환합니다."""
    try:
        temp_dir = Path(tempfile.gettempdir())
        screenshot_files = list(temp_dir.glob("playwright_*.png"))
        
        screenshots = []
        for file_path in screenshot_files:
            stat = file_path.stat()
            screenshots.append({
                "filename": file_path.name,
                "path": str(file_path),
                "size": stat.st_size,
                "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
            })
        
        return json.dumps({
            "count": len(screenshots),
            "screenshots": screenshots
        }, ensure_ascii=False, indent=2)
    
    except Exception as e:
        return f"스크린샷 목록 조회 실패: {str(e)}"


# =============================================================================
# 서버 실행 함수
# =============================================================================

if __name__ == "__main__":
    print("🎭 Playwright FastMCP 서버를 시작합니다...")
    print("\n🛠️ 브라우저 관리 도구:")
    print("- start_browser: 브라우저 시작")
    print("- close_browser: 브라우저 종료")
    
    print("\n🌐 웹페이지 탐색 도구:")
    print("- navigate_to_url: URL로 이동")
    print("- get_page_info: 페이지 정보 조회")
    print("- get_page_text: 페이지 텍스트 추출")
    
    print("\n📸 스크린샷 도구:")
    print("- take_screenshot: 페이지 스크린샷")
    print("- take_element_screenshot: 요소 스크린샷")
    
    print("\n🖱️ 요소 상호작용 도구:")
    print("- click_element: 요소 클릭")
    print("- fill_input: 텍스트 입력")
    print("- wait_for_element: 요소 대기")
    
    print("\n⚙️ 고급 도구:")
    print("- evaluate_javascript: JavaScript 실행")
    print("- get_elements_info: 요소 정보 조회")
    
    print("\n📋 리소스:")
    print("- browser://status: 브라우저 상태")
    print("- screenshots://list: 스크린샷 목록")
    
    print("\n서버가 실행됩니다...")
    
    # STDIO 모드로 실행
    playwright_mcp.run()
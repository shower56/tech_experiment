#!/usr/bin/env python3
"""
블로그 분석 Playwright MCP 서버

블로그 분석에 특화된 Playwright 기능들을 제공합니다.
- 블로그 포스트 목록 수집
- 포스트 내용 분석
- 댓글 및 반응 수집
- SEO 정보 분석
"""

import asyncio
import json
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from fastmcp import FastMCP, Context
from playwright.async_api import async_playwright, Browser, Page, BrowserContext


# 블로그 분석 MCP 서버 인스턴스 생성
blog_analyzer_mcp = FastMCP("블로그 분석 MCP 서버 📊")

# 전역 변수들
browser: Optional[Browser] = None
context: Optional[BrowserContext] = None
current_page: Optional[Page] = None
playwright_instance = None


# =============================================================================
# 기본 브라우저 관리 (playwright_mcp.py에서 복사)
# =============================================================================

@blog_analyzer_mcp.tool
async def start_browser(headless: bool = True, ctx: Context = None) -> str:
    """브라우저를 시작합니다."""
    global browser, context, current_page, playwright_instance
    
    try:
        if ctx:
            await ctx.info("블로그 분석용 브라우저 시작 중...")
        
        playwright_instance = await async_playwright().start()
        browser = await playwright_instance.chromium.launch(headless=headless)
        
        context = await browser.new_context(
            viewport={"width": 1400, "height": 900},
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        )
        current_page = await context.new_page()
        
        if ctx:
            await ctx.info("블로그 분석용 브라우저가 성공적으로 시작되었습니다!")
        
        return "블로그 분석용 브라우저가 성공적으로 시작되었습니다."
    
    except Exception as e:
        if ctx:
            await ctx.error(f"브라우저 시작 실패: {str(e)}")
        return f"브라우저 시작 실패: {str(e)}"


@blog_analyzer_mcp.tool
async def close_browser(ctx: Context = None) -> str:
    """브라우저를 종료합니다."""
    global browser, context, current_page, playwright_instance
    
    try:
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
        
        return "브라우저가 성공적으로 종료되었습니다."
    except Exception as e:
        return f"브라우저 종료 실패: {str(e)}"


# =============================================================================
# 블로그 분석 전용 도구들
# =============================================================================

@blog_analyzer_mcp.tool
async def analyze_blog_homepage(blog_url: str, ctx: Context = None) -> str:
    """블로그 홈페이지를 분석합니다."""
    if not current_page:
        return "브라우저가 시작되지 않았습니다. 먼저 start_browser를 호출하세요."
    
    try:
        if ctx:
            await ctx.info(f"블로그 홈페이지 분석 중: {blog_url}")
        
        # 페이지로 이동
        await current_page.goto(blog_url, wait_until="domcontentloaded", timeout=30000)
        
        # 기본 정보 수집
        title = await current_page.title()
        
        # 메타 태그 정보 수집
        meta_description = await current_page.get_attribute('meta[name="description"]', 'content') or "없음"
        meta_keywords = await current_page.get_attribute('meta[name="keywords"]', 'content') or "없음"
        
        # 블로그 제목 추출 (다양한 셀렉터 시도)
        blog_title_selectors = [
            '.blog-title', '.site-title', 'h1', '.header-title', '.blog-name'
        ]
        blog_title = "찾을 수 없음"
        for selector in blog_title_selectors:
            try:
                element = await current_page.query_selector(selector)
                if element:
                    text = await element.text_content()
                    if text and text.strip():
                        blog_title = text.strip()
                        break
            except:
                continue
        
        # 최근 포스트 개수 확인
        post_selectors = [
            '.list-item', '.post-item', '.entry', '.article-item', 'article'
        ]
        post_count = 0
        for selector in post_selectors:
            try:
                elements = await current_page.query_selector_all(selector)
                if elements:
                    post_count = len(elements)
                    break
            except:
                continue
        
        analysis_result = {
            "url": blog_url,
            "page_title": title,
            "blog_title": blog_title,
            "meta_description": meta_description,
            "meta_keywords": meta_keywords,
            "visible_posts_count": post_count,
            "analysis_timestamp": datetime.now().isoformat()
        }
        
        if ctx:
            await ctx.info(f"블로그 분석 완료: {blog_title}")
        
        return json.dumps(analysis_result, ensure_ascii=False, indent=2)
    
    except Exception as e:
        if ctx:
            await ctx.error(f"블로그 분석 실패: {str(e)}")
        return f"블로그 분석 실패: {str(e)}"


@blog_analyzer_mcp.tool
async def extract_blog_posts(blog_url: str, limit: int = 10, ctx: Context = None) -> str:
    """블로그 포스트 목록을 추출합니다."""
    if not current_page:
        return "브라우저가 시작되지 않았습니다."
    
    try:
        if ctx:
            await ctx.info(f"블로그 포스트 추출 중 (최대 {limit}개)")
        
        # 페이지로 이동
        await current_page.goto(blog_url, wait_until="domcontentloaded", timeout=30000)
        
        # 다양한 포스트 링크 셀렉터 시도
        post_link_selectors = [
            '.list-item .list-title a',
            '.post-item a',
            '.entry-title a',
            'h2 a',
            'h3 a',
            '.article-title a',
            '.post-title a'
        ]
        
        posts = []
        for selector in post_link_selectors:
            try:
                elements = await current_page.query_selector_all(selector)
                if elements:
                    for i, element in enumerate(elements[:limit]):
                        title = await element.text_content()
                        href = await element.get_attribute('href')
                        
                        if title and title.strip():
                            # 상대 URL을 절대 URL로 변환
                            if href and href.startswith('/'):
                                base_url = blog_url.rstrip('/')
                                href = base_url + href
                            
                            posts.append({
                                "index": i + 1,
                                "title": title.strip(),
                                "url": href,
                                "selector_used": selector
                            })
                    
                    if posts:  # 포스트를 찾았으면 중단
                        break
            except Exception as e:
                if ctx:
                    await ctx.error(f"셀렉터 {selector} 실패: {str(e)}")
                continue
        
        result = {
            "blog_url": blog_url,
            "posts_found": len(posts),
            "posts": posts[:limit],
            "extraction_timestamp": datetime.now().isoformat()
        }
        
        if ctx:
            await ctx.info(f"{len(posts)}개의 포스트를 찾았습니다!")
        
        return json.dumps(result, ensure_ascii=False, indent=2)
    
    except Exception as e:
        if ctx:
            await ctx.error(f"포스트 추출 실패: {str(e)}")
        return f"포스트 추출 실패: {str(e)}"


@blog_analyzer_mcp.tool
async def analyze_single_post(post_url: str, ctx: Context = None) -> str:
    """개별 블로그 포스트를 분석합니다."""
    if not current_page:
        return "브라우저가 시작되지 않았습니다."
    
    try:
        if ctx:
            await ctx.info(f"포스트 분석 중: {post_url}")
        
        await current_page.goto(post_url, wait_until="domcontentloaded", timeout=30000)
        
        # 포스트 제목
        title_selectors = ['h1', '.post-title', '.entry-title', '.article-title']
        post_title = "제목을 찾을 수 없음"
        for selector in title_selectors:
            try:
                element = await current_page.query_selector(selector)
                if element:
                    text = await element.text_content()
                    if text and text.strip():
                        post_title = text.strip()
                        break
            except:
                continue
        
        # 포스트 내용
        content_selectors = ['.post-content', '.entry-content', '.article-content', '.content']
        post_content = "내용을 찾을 수 없음"
        content_length = 0
        for selector in content_selectors:
            try:
                element = await current_page.query_selector(selector)
                if element:
                    text = await element.text_content()
                    if text and text.strip():
                        post_content = text.strip()
                        content_length = len(post_content)
                        post_content = post_content[:500] + "..." if len(post_content) > 500 else post_content
                        break
            except:
                continue
        
        # 이미지 개수
        try:
            images = await current_page.query_selector_all('img')
            image_count = len(images)
        except:
            image_count = 0
        
        # 링크 개수
        try:
            links = await current_page.query_selector_all('a')
            link_count = len(links)
        except:
            link_count = 0
        
        analysis_result = {
            "url": post_url,
            "title": post_title,
            "content_preview": post_content,
            "content_length": content_length,
            "image_count": image_count,
            "link_count": link_count,
            "analysis_timestamp": datetime.now().isoformat()
        }
        
        if ctx:
            await ctx.info(f"포스트 분석 완료: {post_title}")
        
        return json.dumps(analysis_result, ensure_ascii=False, indent=2)
    
    except Exception as e:
        if ctx:
            await ctx.error(f"포스트 분석 실패: {str(e)}")
        return f"포스트 분석 실패: {str(e)}"


@blog_analyzer_mcp.tool
async def take_blog_screenshot(blog_url: str, screenshot_type: str = "full", ctx: Context = None) -> str:
    """블로그의 스크린샷을 촬영합니다."""
    if not current_page:
        return "브라우저가 시작되지 않았습니다."
    
    try:
        if ctx:
            await ctx.info(f"블로그 스크린샷 촬영 중: {blog_url}")
        
        await current_page.goto(blog_url, wait_until="domcontentloaded", timeout=30000)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"blog_screenshot_{timestamp}.png"
        screenshot_path = Path(tempfile.gettempdir()) / f"playwright_{filename}"
        
        if screenshot_type == "full":
            await current_page.screenshot(path=str(screenshot_path), full_page=True)
        else:
            await current_page.screenshot(path=str(screenshot_path))
        
        file_size = screenshot_path.stat().st_size
        
        if ctx:
            await ctx.info(f"스크린샷 저장 완료: {screenshot_path}")
        
        return f"블로그 스크린샷이 저장되었습니다.\n경로: {screenshot_path}\n크기: {file_size} bytes\n타입: {screenshot_type}"
    
    except Exception as e:
        if ctx:
            await ctx.error(f"스크린샷 촬영 실패: {str(e)}")
        return f"스크린샷 촬영 실패: {str(e)}"


@blog_analyzer_mcp.tool
async def check_blog_seo(blog_url: str, ctx: Context = None) -> str:
    """블로그의 SEO 정보를 확인합니다."""
    if not current_page:
        return "브라우저가 시작되지 않았습니다."
    
    try:
        if ctx:
            await ctx.info(f"SEO 정보 확인 중: {blog_url}")
        
        await current_page.goto(blog_url, wait_until="domcontentloaded", timeout=30000)
        
        # SEO 관련 정보 수집
        seo_info = {}
        
        # 메타 태그들
        meta_tags = [
            ('description', 'meta[name="description"]'),
            ('keywords', 'meta[name="keywords"]'),
            ('author', 'meta[name="author"]'),
            ('robots', 'meta[name="robots"]'),
            ('viewport', 'meta[name="viewport"]'),
            ('og:title', 'meta[property="og:title"]'),
            ('og:description', 'meta[property="og:description"]'),
            ('og:url', 'meta[property="og:url"]'),
            ('og:image', 'meta[property="og:image"]'),
            ('twitter:card', 'meta[name="twitter:card"]'),
            ('twitter:title', 'meta[name="twitter:title"]')
        ]
        
        for tag_name, selector in meta_tags:
            try:
                element = await current_page.query_selector(selector)
                if element:
                    content = await element.get_attribute('content')
                    seo_info[tag_name] = content or "없음"
                else:
                    seo_info[tag_name] = "없음"
            except:
                seo_info[tag_name] = "오류"
        
        # 제목 태그
        try:
            title = await current_page.title()
            seo_info['title'] = title
            seo_info['title_length'] = len(title)
        except:
            seo_info['title'] = "없음"
            seo_info['title_length'] = 0
        
        # 헤딩 태그 개수
        for i in range(1, 7):
            try:
                headings = await current_page.query_selector_all(f'h{i}')
                seo_info[f'h{i}_count'] = len(headings)
            except:
                seo_info[f'h{i}_count'] = 0
        
        # 이미지 alt 태그 확인
        try:
            images = await current_page.query_selector_all('img')
            images_with_alt = 0
            total_images = len(images)
            
            for img in images:
                alt = await img.get_attribute('alt')
                if alt and alt.strip():
                    images_with_alt += 1
            
            seo_info['total_images'] = total_images
            seo_info['images_with_alt'] = images_with_alt
            seo_info['alt_coverage'] = f"{images_with_alt}/{total_images}" if total_images > 0 else "0/0"
        except:
            seo_info['total_images'] = 0
            seo_info['images_with_alt'] = 0
            seo_info['alt_coverage'] = "0/0"
        
        result = {
            "url": blog_url,
            "seo_analysis": seo_info,
            "analysis_timestamp": datetime.now().isoformat()
        }
        
        if ctx:
            await ctx.info("SEO 분석 완료!")
        
        return json.dumps(result, ensure_ascii=False, indent=2)
    
    except Exception as e:
        if ctx:
            await ctx.error(f"SEO 분석 실패: {str(e)}")
        return f"SEO 분석 실패: {str(e)}"


# =============================================================================
# 리소스들
# =============================================================================

@blog_analyzer_mcp.resource("blog://analysis-guide")
def get_blog_analysis_guide() -> str:
    """블로그 분석 가이드를 반환합니다."""
    guide = {
        "블로그 분석 단계": [
            "1. start_browser로 브라우저 시작",
            "2. analyze_blog_homepage로 블로그 홈페이지 분석",
            "3. extract_blog_posts로 포스트 목록 추출",
            "4. analyze_single_post로 개별 포스트 분석",
            "5. check_blog_seo로 SEO 상태 확인",
            "6. take_blog_screenshot로 스크린샷 촬영",
            "7. close_browser로 브라우저 종료"
        ],
        "주요 기능": {
            "홈페이지 분석": "블로그 제목, 메타 정보, 포스트 개수 등",
            "포스트 추출": "최근 포스트 목록과 URL 수집",
            "개별 분석": "포스트 제목, 내용, 이미지/링크 개수",
            "SEO 분석": "메타 태그, 헤딩 구조, 이미지 alt 태그",
            "스크린샷": "블로그 전체 또는 일부 화면 캡처"
        },
        "지원 플랫폼": [
            "Tistory", "네이버 블로그", "WordPress", "GitHub Pages", "기타 블로그"
        ]
    }
    
    return json.dumps(guide, ensure_ascii=False, indent=2)


# =============================================================================
# 서버 실행 함수
# =============================================================================

if __name__ == "__main__":
    print("📊 블로그 분석 Playwright MCP 서버를 시작합니다...")
    print("\n🔍 블로그 분석 도구:")
    print("- analyze_blog_homepage: 블로그 홈페이지 분석")
    print("- extract_blog_posts: 포스트 목록 추출")
    print("- analyze_single_post: 개별 포스트 분석")
    print("- check_blog_seo: SEO 정보 확인")
    print("- take_blog_screenshot: 블로그 스크린샷")
    
    print("\n🛠️ 기본 도구:")
    print("- start_browser: 브라우저 시작")
    print("- close_browser: 브라우저 종료")
    
    print("\n📋 리소스:")
    print("- blog://analysis-guide: 블로그 분석 가이드")
    
    print("\n서버가 실행됩니다...")
    
    # STDIO 모드로 실행
    blog_analyzer_mcp.run()
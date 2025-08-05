#!/usr/bin/env python3
"""
Playwright MCP 클라이언트 테스트

Playwright MCP 서버의 다양한 기능들을 테스트합니다.
"""

import asyncio
import json
from fastmcp import Client


async def test_basic_browser_functions():
    """기본 브라우저 기능 테스트"""
    
    print("🎭 Playwright MCP 기본 기능 테스트를 시작합니다...")
    
    # playwright_mcp.py 서버에 연결
    from playwright_mcp import playwright_mcp
    
    async with Client(playwright_mcp) as client:
        print("✅ Playwright MCP 서버에 성공적으로 연결되었습니다!")
        
        print("\n" + "="*60)
        print("🚀 브라우저 시작 테스트")
        print("="*60)
        
        # 브라우저 시작
        print("\n🌐 브라우저 시작 중...")
        result = await client.call_tool("start_browser", {
            "headless": True,  # 헤드리스 모드로 실행
            "browser_type": "chromium"
        })
        print(result.content[0].text)
        
        print("\n" + "="*60)
        print("🔍 웹페이지 탐색 테스트")
        print("="*60)
        
        # 웹페이지로 이동 (사용자 블로그)
        print("\n📂 metashower 블로그로 이동 중...")
        result = await client.call_tool("navigate_to_url", {
            "url": "https://metashower.tistory.com"
        })
        print(result.content[0].text)
        
        # 페이지 정보 조회
        print("\n📋 페이지 정보 조회:")
        result = await client.call_tool("get_page_info", {})
        try:
            page_info = json.loads(result.content[0].text)
            print(json.dumps(page_info, ensure_ascii=False, indent=2))
        except json.JSONDecodeError:
            print(f"페이지 정보: {result.content[0].text}")
        except Exception as e:
            print(f"페이지 정보 조회 오류: {e}")
        
        # 페이지 텍스트 추출
        print("\n📝 블로그 제목 추출:")
        result = await client.call_tool("get_page_text", {"selector": "h1, .blog-title, .title"})
        print(f"블로그 제목: {result.content[0].text[:100]}...")
        
        # 블로그 포스트 제목들 추출
        print("\n📰 최근 포스트 제목들:")
        result = await client.call_tool("get_elements_info", {
            "selector": ".list-item .list-title a, .entry-title a, h2 a"
        })
        try:
            elements_info = json.loads(result.content[0].text)
            print(f"포스트 개수: {elements_info['count']}")
            for i, element in enumerate(elements_info['elements'][:5]):  # 최근 5개만
                print(f"  {i+1}. {element['text_content']}")
        except:
            print(f"포스트 정보: {result.content[0].text[:200]}...")
        
        print("\n" + "="*60)
        print("📸 스크린샷 테스트")
        print("="*60)
        
        # 전체 페이지 스크린샷
        print("\n📷 metashower 블로그 전체 스크린샷 촬영:")
        result = await client.call_tool("take_screenshot", {
            "filename": "metashower_blog_full.png",
            "full_page": True
        })
        print(result.content[0].text)
        
        # 블로그 헤더 스크린샷
        print("\n🎯 블로그 헤더 스크린샷 촬영:")
        result = await client.call_tool("take_element_screenshot", {
            "selector": ".blog-header, .header, .blog-title",
            "filename": "metashower_header.png"
        })
        print(result.content[0].text)
        
        print("\n" + "="*60)
        print("⚙️ 고급 기능 테스트")
        print("="*60)
        
        # JavaScript 실행
        print("\n💻 JavaScript 실행 테스트:")
        result = await client.call_tool("evaluate_javascript", {
            "script": "document.title"
        })
        js_result = json.loads(result.content[0].text)
        print(f"페이지 타이틀: {js_result['result']}")
        
        # 요소 정보 조회
        print("\n🔍 블로그 네비게이션 링크 정보 조회:")
        result = await client.call_tool("get_elements_info", {
            "selector": ".menu a, .nav a, .navigation a"
        })
        try:
            elements_info = json.loads(result.content[0].text)
            print(f"네비게이션 링크 개수: {elements_info['count']}")
            for element in elements_info['elements'][:5]:  # 처음 5개만 출력
                print(f"  - {element['tag_name']}: {element['text_content']}")
        except:
            print(f"네비게이션 정보: {result.content[0].text[:200]}...")
        
        print("\n" + "="*60)
        print("📊 리소스 테스트")
        print("="*60)
        
        # 브라우저 상태 조회
        print("\n🖥️ 브라우저 상태:")
        result = await client.read_resource("browser://status")
        if hasattr(result, 'contents'):
            content = result.contents[0].text if result.contents else str(result)
        else:
            content = str(result)
        
        try:
            status = json.loads(content)
            print(json.dumps(status, ensure_ascii=False, indent=2))
        except:
            print(content)
        
        # 스크린샷 목록 조회
        print("\n📸 스크린샷 목록:")
        result = await client.read_resource("screenshots://list")
        if hasattr(result, 'contents'):
            content = result.contents[0].text if result.contents else str(result)
        else:
            content = str(result)
        
        try:
            screenshots = json.loads(content)
            print(f"총 스크린샷 수: {screenshots['count']}")
            for screenshot in screenshots['screenshots']:
                print(f"  - {screenshot['filename']} ({screenshot['size']} bytes)")
        except:
            print(content)
        
        print("\n" + "="*60)
        print("🛑 브라우저 종료 테스트")
        print("="*60)
        
        # 브라우저 종료
        print("\n🔚 브라우저 종료 중...")
        result = await client.call_tool("close_browser", {})
        print(result.content[0].text)
        
        print("\n" + "="*60)
        print("✅ 모든 기본 기능 테스트가 완료되었습니다!")
        print("="*60)


async def test_web_interaction():
    """웹 상호작용 테스트"""
    
    print("\n🎯 웹 상호작용 테스트를 시작합니다...")
    
    from playwright_mcp import playwright_mcp
    
    async with Client(playwright_mcp) as client:
        
        # 브라우저 시작
        print("\n🌐 브라우저 시작...")
        await client.call_tool("start_browser", {"headless": True})
        
        # Google로 이동
        print("\n🔍 Google로 이동...")
        result = await client.call_tool("navigate_to_url", {
            "url": "https://www.google.com"
        })
        print(result.content[0].text)
        
        # 검색 입력 필드 찾기 및 텍스트 입력
        print("\n⌨️ 검색어 입력 테스트:")
        try:
            # Google 검색 입력 필드에 텍스트 입력
            result = await client.call_tool("fill_input", {
                "selector": "input[name='q']",
                "text": "FastMCP Playwright"
            })
            print(result.content[0].text)
            
            # 스크린샷 촬영
            print("\n📷 검색어 입력 후 스크린샷:")
            result = await client.call_tool("take_screenshot", {
                "filename": "google_search_input.png"
            })
            print(result.content[0].text)
            
        except Exception as e:
            print(f"검색 입력 테스트 실패: {e}")
        
        # 브라우저 종료
        print("\n🔚 브라우저 종료...")
        await client.call_tool("close_browser", {})
        
        print("\n✅ 웹 상호작용 테스트가 완료되었습니다!")


async def test_github_exploration():
    """GitHub 탐색 테스트"""
    
    print("\n🐙 GitHub 탐색 테스트를 시작합니다...")
    
    from playwright_mcp import playwright_mcp
    
    async with Client(playwright_mcp) as client:
        
        # 브라우저 시작
        print("\n🌐 브라우저 시작...")
        await client.call_tool("start_browser", {"headless": True})
        
        # fastMCP GitHub 페이지로 이동
        print("\n🔗 fastMCP GitHub 페이지로 이동...")
        result = await client.call_tool("navigate_to_url", {
            "url": "https://github.com/jlowin/fastmcp"
        })
        print(result.content[0].text)
        
        # README 내용 일부 추출
        print("\n📖 README 내용 추출:")
        result = await client.call_tool("get_page_text", {
            "selector": "article.markdown-body"
        })
        readme_text = result.content[0].text
        print(f"README 텍스트 (처음 300자): {readme_text[:300]}...")
        
        # 스타 수 확인
        print("\n⭐ 스타 수 확인:")
        result = await client.call_tool("evaluate_javascript", {
            "script": "document.querySelector('#repo-stars-counter-star')?.textContent?.trim() || 'N/A'"
        })
        stars_result = json.loads(result.content[0].text)
        print(f"현재 스타 수: {stars_result['result']}")
        
        # 페이지 스크린샷
        print("\n📷 GitHub 페이지 스크린샷:")
        result = await client.call_tool("take_screenshot", {
            "filename": "fastmcp_github.png"
        })
        print(result.content[0].text)
        
        # 브라우저 종료
        print("\n🔚 브라우저 종료...")
        await client.call_tool("close_browser", {})
        
        print("\n✅ GitHub 탐색 테스트가 완료되었습니다!")


if __name__ == "__main__":
    print("🚀 Playwright MCP 테스트를 시작합니다...\n")
    
    # 기본 기능 테스트
    asyncio.run(test_basic_browser_functions())
    
    # 웹 상호작용 테스트
    asyncio.run(test_web_interaction())
    
    # GitHub 탐색 테스트
    asyncio.run(test_github_exploration())
    
    print("\n🎉 모든 Playwright MCP 테스트가 성공적으로 완료되었습니다!")
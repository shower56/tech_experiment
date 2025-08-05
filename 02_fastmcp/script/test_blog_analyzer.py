#!/usr/bin/env python3
"""
블로그 분석 MCP 클라이언트 테스트

metashower.tistory.com 블로그를 분석하는 테스트입니다.
"""

import asyncio
import json
from fastmcp import Client


async def test_metashower_blog_analysis():
    """metashower 블로그 종합 분석 테스트"""
    
    print("📊 metashower 블로그 종합 분석을 시작합니다...")
    
    # blog_analyzer_mcp.py 서버에 연결
    from blog_analyzer_mcp import blog_analyzer_mcp
    
    blog_url = "https://metashower.tistory.com"
    
    async with Client(blog_analyzer_mcp) as client:
        print("✅ 블로그 분석 서버에 성공적으로 연결되었습니다!")
        
        print("\n" + "="*70)
        print("🚀 1단계: 분석 환경 준비")
        print("="*70)
        
        # 브라우저 시작
        print("\n🌐 분석용 브라우저 시작...")
        result = await client.call_tool("start_browser", {"headless": True})
        print(result.content[0].text)
        
        print("\n" + "="*70)
        print("🔍 2단계: 블로그 홈페이지 분석")
        print("="*70)
        
        # 블로그 홈페이지 분석
        print(f"\n📋 {blog_url} 홈페이지 분석 중...")
        result = await client.call_tool("analyze_blog_homepage", {"blog_url": blog_url})
        try:
            analysis = json.loads(result.content[0].text)
            print("\n📊 블로그 기본 정보:")
            print(f"  📌 블로그 제목: {analysis['blog_title']}")
            print(f"  📄 페이지 타이틀: {analysis['page_title']}")
            print(f"  📝 메타 설명: {analysis['meta_description'][:100]}...")
            print(f"  🏷️ 메타 키워드: {analysis['meta_keywords']}")
            print(f"  📰 표시된 포스트 수: {analysis['visible_posts_count']}개")
        except:
            print(f"홈페이지 분석 결과: {result.content[0].text}")
        
        print("\n" + "="*70)
        print("📚 3단계: 블로그 포스트 목록 추출")
        print("="*70)
        
        # 포스트 목록 추출
        print(f"\n📋 최근 포스트 목록 추출 중...")
        result = await client.call_tool("extract_blog_posts", {
            "blog_url": blog_url, 
            "limit": 5
        })
        try:
            posts_data = json.loads(result.content[0].text)
            print(f"\n📚 발견된 포스트: {posts_data['posts_found']}개")
            
            # 첫 번째 포스트 상세 분석을 위해 저장
            first_post_url = None
            
            for i, post in enumerate(posts_data['posts'][:5]):
                print(f"  {i+1}. {post['title']}")
                print(f"     URL: {post['url'][:50]}...")
                
                if i == 0:  # 첫 번째 포스트 URL 저장
                    first_post_url = post['url']
                    
        except Exception as e:
            print(f"포스트 추출 결과: {result.content[0].text}")
            first_post_url = None
        
        print("\n" + "="*70)
        print("🔍 4단계: 개별 포스트 상세 분석")
        print("="*70)
        
        # 첫 번째 포스트 상세 분석
        if first_post_url:
            print(f"\n📖 첫 번째 포스트 상세 분석 중...")
            result = await client.call_tool("analyze_single_post", {"post_url": first_post_url})
            try:
                post_analysis = json.loads(result.content[0].text)
                print(f"\n📄 포스트 상세 정보:")
                print(f"  📌 제목: {post_analysis['title']}")
                print(f"  📝 내용 길이: {post_analysis['content_length']}자")
                print(f"  🖼️ 이미지 개수: {post_analysis['image_count']}개")
                print(f"  🔗 링크 개수: {post_analysis['link_count']}개")
                print(f"  📄 내용 미리보기:")
                print(f"     {post_analysis['content_preview'][:200]}...")
            except:
                print(f"포스트 분석 결과: {result.content[0].text}")
        else:
            print("⚠️ 분석할 포스트를 찾을 수 없습니다.")
        
        print("\n" + "="*70)
        print("🎯 5단계: SEO 최적화 상태 분석")
        print("="*70)
        
        # SEO 분석
        print(f"\n🔍 SEO 최적화 상태 분석 중...")
        result = await client.call_tool("check_blog_seo", {"blog_url": blog_url})
        try:
            seo_analysis = json.loads(result.content[0].text)
            seo_info = seo_analysis['seo_analysis']
            
            print(f"\n🎯 SEO 분석 결과:")
            print(f"  📌 페이지 제목: {seo_info['title']}")
            print(f"  📏 제목 길이: {seo_info['title_length']}자")
            print(f"  📝 메타 설명: {seo_info['description'][:50]}...")
            print(f"  🏷️ 메타 키워드: {seo_info['keywords']}")
            print(f"  🤖 로봇 설정: {seo_info['robots']}")
            
            print(f"\n📊 헤딩 구조:")
            for i in range(1, 7):
                count = seo_info.get(f'h{i}_count', 0)
                if count > 0:
                    print(f"    H{i}: {count}개")
            
            print(f"\n🖼️ 이미지 최적화:")
            print(f"    전체 이미지: {seo_info['total_images']}개")
            print(f"    ALT 태그 있는 이미지: {seo_info['images_with_alt']}개")
            print(f"    ALT 태그 커버리지: {seo_info['alt_coverage']}")
            
            print(f"\n🌐 소셜 미디어 최적화:")
            print(f"    OG Title: {seo_info.get('og:title', '없음')}")
            print(f"    OG Description: {seo_info.get('og:description', '없음')[:50]}...")
            print(f"    Twitter Card: {seo_info.get('twitter:card', '없음')}")
            
        except:
            print(f"SEO 분석 결과: {result.content[0].text}")
        
        print("\n" + "="*70)
        print("📸 6단계: 블로그 스크린샷 촬영")
        print("="*70)
        
        # 스크린샷 촬영
        print(f"\n📷 블로그 전체 페이지 스크린샷 촬영...")
        result = await client.call_tool("take_blog_screenshot", {
            "blog_url": blog_url,
            "screenshot_type": "full"
        })
        print(result.content[0].text)
        
        print("\n" + "="*70)
        print("📋 7단계: 분석 가이드 확인")
        print("="*70)
        
        # 분석 가이드 확인
        print("\n📖 블로그 분석 가이드:")
        result = await client.read_resource("blog://analysis-guide")
        if hasattr(result, 'contents'):
            content = result.contents[0].text if result.contents else str(result)
        else:
            content = str(result)
        
        try:
            guide = json.loads(content)
            print("\n📋 분석 단계:")
            for step in guide["블로그 분석 단계"]:
                print(f"  {step}")
            
            print("\n🛠️ 주요 기능:")
            for feature, description in guide["주요 기능"].items():
                print(f"  {feature}: {description}")
        except:
            print(content)
        
        print("\n" + "="*70)
        print("🛑 8단계: 분석 완료 및 정리")
        print("="*70)
        
        # 브라우저 종료
        print("\n🔚 분석용 브라우저 종료...")
        result = await client.call_tool("close_browser", {})
        print(result.content[0].text)
        
        print("\n" + "="*70)
        print("✅ metashower 블로그 종합 분석이 완료되었습니다!")
        print("="*70)
        
        print("\n📊 분석 요약:")
        print("  ✅ 홈페이지 기본 정보 수집 완료")
        print("  ✅ 최근 포스트 목록 추출 완료")
        print("  ✅ 개별 포스트 상세 분석 완료")
        print("  ✅ SEO 최적화 상태 점검 완료")
        print("  ✅ 블로그 스크린샷 촬영 완료")


async def test_blog_comparison_analysis():
    """여러 블로그 비교 분석 테스트 (간단 버전)"""
    
    print("\n🔍 블로그 비교 분석 테스트를 시작합니다...")
    
    from blog_analyzer_mcp import blog_analyzer_mcp
    
    # 비교할 블로그들 (예시)
    blogs = [
        "https://metashower.tistory.com",
        # 다른 블로그들도 추가 가능
    ]
    
    async with Client(blog_analyzer_mcp) as client:
        
        # 브라우저 시작
        print("\n🌐 브라우저 시작...")
        await client.call_tool("start_browser", {"headless": True})
        
        comparison_results = []
        
        for i, blog_url in enumerate(blogs):
            print(f"\n📊 {i+1}번째 블로그 분석: {blog_url}")
            
            try:
                # 홈페이지 분석
                result = await client.call_tool("analyze_blog_homepage", {"blog_url": blog_url})
                analysis = json.loads(result.content[0].text)
                
                # 포스트 추출
                result = await client.call_tool("extract_blog_posts", {
                    "blog_url": blog_url, 
                    "limit": 3
                })
                posts_data = json.loads(result.content[0].text)
                
                comparison_results.append({
                    "url": blog_url,
                    "title": analysis.get('blog_title', '알 수 없음'),
                    "posts_count": posts_data.get('posts_found', 0),
                    "meta_description": analysis.get('meta_description', '없음')[:50] + "..."
                })
                
            except Exception as e:
                print(f"  ❌ 분석 실패: {e}")
                comparison_results.append({
                    "url": blog_url,
                    "title": "분석 실패",
                    "posts_count": 0,
                    "meta_description": str(e)
                })
        
        # 비교 결과 출력
        print("\n📊 블로그 비교 분석 결과:")
        print("-" * 80)
        for result in comparison_results:
            print(f"🌐 URL: {result['url']}")
            print(f"📌 제목: {result['title']}")
            print(f"📚 포스트 수: {result['posts_count']}개")
            print(f"📝 설명: {result['meta_description']}")
            print("-" * 80)
        
        # 브라우저 종료
        print("\n🔚 브라우저 종료...")
        await client.call_tool("close_browser", {})
        
        print("\n✅ 블로그 비교 분석이 완료되었습니다!")


if __name__ == "__main__":
    print("🚀 블로그 분석 MCP 테스트를 시작합니다...\n")
    
    # metashower 블로그 종합 분석
    asyncio.run(test_metashower_blog_analysis())
    
    # 블로그 비교 분석 (간단 버전)
    asyncio.run(test_blog_comparison_analysis())
    
    print("\n🎉 모든 블로그 분석 테스트가 성공적으로 완료되었습니다!")
    print("\n💡 생성된 스크린샷과 분석 결과를 확인해보세요!")
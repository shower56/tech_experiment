#!/usr/bin/env python3
"""
fastMCP 고급 기능 테스트

advanced_features.py 서버의 고급 기능들을 테스트합니다.
"""

import asyncio
import json
from fastmcp import Client


async def test_advanced_features():
    """고급 기능들을 테스트합니다."""
    
    print("🔬 fastMCP 고급 기능 테스트를 시작합니다...")
    
    # advanced_features.py 서버에 연결
    from advanced_features import advanced_mcp
    
    async with Client(advanced_mcp) as client:
        print("✅ 고급 기능 서버에 성공적으로 연결되었습니다!")
        
        print("\n" + "="*60)
        print("📁 파일 관리 테스트")
        print("="*60)
        
        # 파일 생성 테스트
        print("\n📝 파일 생성 테스트:")
        result = await client.call_tool("create_file", {
            "filename": "test.txt",
            "content": "안녕하세요! 이것은 테스트 파일입니다.\n여러 줄의 내용을 포함합니다."
        })
        print(result.content[0].text)
        
        # 파일 목록 조회
        print("\n📋 파일 목록 조회:")
        result = await client.call_tool("list_files", {})
        files = json.loads(result.content[0].text)
        print(json.dumps(files, ensure_ascii=False, indent=2))
        
        # 파일 읽기 테스트
        print("\n📖 파일 읽기 테스트:")
        result = await client.call_tool("read_file_content", {"filename": "test.txt"})
        print(result.content[0].text)
        
        print("\n" + "="*60)
        print("🗄️ 데이터베이스 테스트")
        print("="*60)
        
        # 사용자 생성 테스트
        print("\n👤 사용자 생성 테스트:")
        result = await client.call_tool("create_user", {
            "name": "테스트 사용자",
            "email": "test@example.com"
        })
        print(result.content[0].text)
        
        # 사용자 조회
        print("\n👥 사용자 목록 조회:")
        result = await client.call_tool("get_users", {})
        users = json.loads(result.content[0].text)
        print(json.dumps(users, ensure_ascii=False, indent=2))
        
        # 게시글 생성
        print("\n📝 게시글 생성 테스트:")
        result = await client.call_tool("create_post", {
            "user_id": 1,
            "title": "fastMCP 테스트 게시글",
            "content": "이것은 fastMCP로 생성된 테스트 게시글입니다. 정말 멋지네요!"
        })
        print(result.content[0].text)
        
        # 사용자별 게시글 조회
        print("\n📄 사용자별 게시글 조회:")
        result = await client.call_tool("get_posts_by_user", {"user_id": 1})
        posts = json.loads(result.content[0].text)
        print(json.dumps(posts, ensure_ascii=False, indent=2))
        
        print("\n" + "="*60)
        print("🌐 외부 API 테스트")
        print("="*60)
        
        # 랜덤 팩트 조회
        print("\n🎯 랜덤 팩트 조회:")
        result = await client.call_tool("fetch_random_fact", {})
        print(result.content[0].text)
        
        # 날씨 정보 시뮬레이션
        print("\n🌤️ 날씨 정보 시뮬레이션:")
        result = await client.call_tool("get_weather_info", {"city": "서울"})
        weather = json.loads(result.content[0].text)
        print(json.dumps(weather, ensure_ascii=False, indent=2))
        
        print("\n" + "="*60)
        print("📊 데이터 분석 테스트")
        print("="*60)
        
        # 숫자 분석 테스트
        print("\n🔢 숫자 분석 테스트:")
        test_numbers = [1, 5, 3, 9, 2, 7, 4, 8, 6, 10]
        result = await client.call_tool("analyze_numbers", {"numbers": test_numbers})
        analysis = json.loads(result.content[0].text)
        print(f"분석 대상: {test_numbers}")
        print(json.dumps(analysis, ensure_ascii=False, indent=2))
        
        # 텍스트 분석 테스트
        print("\n📝 텍스트 분석 테스트:")
        test_text = """
        fastMCP는 정말 강력한 도구입니다. 
        Model Context Protocol을 통해 LLM과 외부 시스템을 연결할 수 있습니다.
        Python으로 쉽게 서버를 구축하고 다양한 기능을 제공할 수 있습니다.
        fastMCP를 사용하면 개발이 빨라집니다.
        """
        result = await client.call_tool("text_analysis", {"text": test_text.strip()})
        text_analysis = json.loads(result.content[0].text)
        print("분석 대상 텍스트:")
        print(test_text.strip())
        print("\n분석 결과:")
        print(json.dumps(text_analysis, ensure_ascii=False, indent=2))
        
        print("\n" + "="*60)
        print("📊 리소스 테스트")
        print("="*60)
        
        # 데이터베이스 리소스 테스트
        print("\n👥 DB 사용자 리소스:")
        result = await client.read_resource("db://users")
        if hasattr(result, 'contents'):
            content = result.contents[0].text if result.contents else str(result)
        else:
            content = str(result)
        try:
            users_resource = json.loads(content)
            print(json.dumps(users_resource, ensure_ascii=False, indent=2))
        except:
            print(content)
        
        print("\n📄 DB 게시글 리소스:")
        result = await client.read_resource("db://posts")
        if hasattr(result, 'contents'):
            content = result.contents[0].text if result.contents else str(result)
        else:
            content = str(result)
        try:
            posts_resource = json.loads(content)
            print(json.dumps(posts_resource, ensure_ascii=False, indent=2))
        except:
            print(content)
        
        print("\n📈 데이터베이스 통계:")
        result = await client.read_resource("stats://summary")
        if hasattr(result, 'contents'):
            content = result.contents[0].text if result.contents else str(result)
        else:
            content = str(result)
        try:
            stats = json.loads(content)
            print(json.dumps(stats, ensure_ascii=False, indent=2))
        except:
            print(content)
        
        print("\n" + "="*60)
        print("✅ 모든 고급 기능 테스트가 완료되었습니다!")
        print("="*60)


if __name__ == "__main__":
    print("🚀 fastMCP 고급 기능 테스트를 시작합니다...\n")
    
    # 고급 기능 테스트 실행
    asyncio.run(test_advanced_features())
    
    print("\n🎉 모든 고급 기능 테스트가 성공적으로 완료되었습니다!")
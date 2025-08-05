#!/usr/bin/env python3
"""
fastMCP 클라이언트 테스트

이 클라이언트는 fastMCP 서버에 연결하여 다양한 기능을 테스트합니다.
"""

import asyncio
import json
from fastmcp import Client


async def test_client():
    """fastMCP 서버와 상호작용하는 테스트 클라이언트"""
    
    print("🔧 fastMCP 클라이언트를 시작합니다...")
    
    # app.py 서버에 인메모리로 연결
    from app import mcp
    
    async with Client(mcp) as client:
        print("✅ 서버에 성공적으로 연결되었습니다!")
        
        # 1. 사용 가능한 도구 목록 확인
        print("\n📋 사용 가능한 도구들:")
        tools = await client.list_tools()
        if hasattr(tools, 'tools'):
            tool_list = tools.tools
        else:
            tool_list = tools
        
        for tool in tool_list:
            print(f"  - {tool.name}: {tool.description}")
        
        # 2. 사용 가능한 리소스 목록 확인
        print("\n📊 사용 가능한 리소스들:")
        resources = await client.list_resources()
        if hasattr(resources, 'resources'):
            resource_list = resources.resources
        else:
            resource_list = resources
            
        for resource in resource_list:
            print(f"  - {resource.uri}: {resource.description}")
        
        # 3. 사용 가능한 프롬프트 목록 확인
        print("\n💬 사용 가능한 프롬프트들:")
        prompts = await client.list_prompts()
        if hasattr(prompts, 'prompts'):
            prompt_list = prompts.prompts
        else:
            prompt_list = prompts
            
        for prompt in prompt_list:
            print(f"  - {prompt.name}: {prompt.description}")
        
        print("\n" + "="*60)
        print("🧪 도구 테스트를 시작합니다...")
        print("="*60)
        
        # 4. 기본 계산 도구 테스트
        print("\n➕ 숫자 더하기 테스트:")
        result = await client.call_tool("add_numbers", {"a": 15, "b": 25})
        print(f"  15 + 25 = {result.content[0].text}")
        
        print("\n✖️ 숫자 곱하기 테스트:")
        result = await client.call_tool("multiply_numbers", {"a": 7, "b": 8})
        print(f"  7 × 8 = {result.content[0].text}")
        
        print("\n🎯 거듭제곱 테스트:")
        result = await client.call_tool("calculate_power", {"base": 2, "exponent": 10})
        print(f"  2^10 = {result.content[0].text}")
        
        print("\n🎲 랜덤 숫자 생성 테스트:")
        result = await client.call_tool("generate_random_number", {"min_val": 1, "max_val": 10})
        print(f"  1-10 사이의 랜덤 숫자: {result.content[0].text}")
        
        print("\n⏰ 현재 시간 테스트:")
        result = await client.call_tool("get_current_time", {})
        print(f"  현재 시간: {result.content[0].text}")
        
        print("\n📝 JSON 데이터 생성 테스트:")
        result = await client.call_tool("create_json_data", {
            "name": "김개발",
            "age": 30,
            "city": "서울"
        })
        data = json.loads(result.content[0].text)
        print(f"  생성된 데이터: {json.dumps(data, ensure_ascii=False, indent=2)}")
        
        print("\n" + "="*60)
        print("📊 리소스 테스트를 시작합니다...")
        print("="*60)
        
        # 5. 리소스 테스트
        print("\n🖥️ 시스템 정보:")
        result = await client.read_resource("system://info")
        if hasattr(result, 'contents'):
            content = result.contents[0].text if result.contents else str(result)
        else:
            content = str(result)
        print(content)
        
        print("\n📈 서버 상태:")
        result = await client.read_resource("server://status")
        if hasattr(result, 'contents'):
            content = result.contents[0].text if result.contents else str(result)
        else:
            content = str(result)
        print(content)
        
        print("\n👥 샘플 사용자 데이터:")
        result = await client.read_resource("data://sample/users")
        if hasattr(result, 'contents'):
            content = result.contents[0].text if result.contents else str(result)
        else:
            content = str(result)
        try:
            users_data = json.loads(content)
            print(json.dumps(users_data, ensure_ascii=False, indent=2))
        except:
            print(content)
        
        print("\n📦 샘플 제품 데이터:")
        result = await client.read_resource("data://sample/products")
        if hasattr(result, 'contents'):
            content = result.contents[0].text if result.contents else str(result)
        else:
            content = str(result)
        try:
            products_data = json.loads(content)
            print(json.dumps(products_data, ensure_ascii=False, indent=2))
        except:
            print(content)
        
        print("\n" + "="*60)
        print("💬 프롬프트 테스트를 시작합니다...")
        print("="*60)
        
        # 6. 프롬프트 테스트
        print("\n🔍 코드 리뷰 프롬프트:")
        sample_code = """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
"""
        try:
            result = await client.get_prompt("code_review_prompt", {
                "code": sample_code,
                "language": "python"
            })
            if hasattr(result, 'messages') and result.messages:
                prompt_text = result.messages[0].content.text
                print(prompt_text[:200] + "...")
            else:
                print(f"프롬프트 결과: {str(result)[:200]}...")
        except Exception as e:
            print(f"프롬프트 테스트 오류: {e}")
        
        print("\n📊 데이터 분석 프롬프트:")
        try:
            result = await client.get_prompt("data_analysis_prompt", {
                "data_description": "월별 매출 데이터: 1월(100만원), 2월(120만원), 3월(90만원)"
            })
            if hasattr(result, 'messages') and result.messages:
                prompt_text = result.messages[0].content.text
                print(prompt_text[:200] + "...")
            else:
                print(f"프롬프트 결과: {str(result)[:200]}...")
        except Exception as e:
            print(f"프롬프트 테스트 오류: {e}")
        
        print("\n🔧 문제 해결 프롬프트:")
        try:
            result = await client.get_prompt("problem_solving_prompt", {
                "problem": "웹사이트 응답 속도가 느림",
                "context": "사용자 수가 급증하여 서버 부하가 증가함"
            })
            if hasattr(result, 'messages') and result.messages:
                prompt_text = result.messages[0].content.text
                print(prompt_text[:200] + "...")
            else:
                print(f"프롬프트 결과: {str(result)[:200]}...")
        except Exception as e:
            print(f"프롬프트 테스트 오류: {e}")
        
        print("\n" + "="*60)
        print("✅ 모든 테스트가 완료되었습니다!")
        print("="*60)


async def test_context_tool():
    """Context를 사용하는 도구 테스트"""
    print("\n🔄 Context를 사용하는 도구 테스트...")
    
    from app import mcp
    
    async with Client(mcp) as client:
        print("📤 데이터 처리 요청 중...")
        result = await client.call_tool("process_data_with_context", {
            "data": "안녕하세요! 이것은 테스트 데이터입니다."
        })
        print(f"📥 처리 결과: {result.content[0].text}")


if __name__ == "__main__":
    print("🚀 fastMCP 클라이언트 테스트를 시작합니다...\n")
    
    # 기본 테스트 실행
    asyncio.run(test_client())
    
    # Context 도구 테스트
    asyncio.run(test_context_tool())
    
    print("\n🎉 모든 테스트가 성공적으로 완료되었습니다!")
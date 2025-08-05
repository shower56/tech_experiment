#!/usr/bin/env python3
"""
fastMCP HTTP 클라이언트

HTTP 모드로 실행되는 fastMCP 서버에 연결하는 클라이언트입니다.
"""

import asyncio
import json
from fastmcp import Client


async def test_http_server():
    """HTTP MCP 서버와 상호작용하는 테스트 클라이언트"""
    
    print("🌐 fastMCP HTTP 서버 클라이언트를 시작합니다...")
    
    # HTTP MCP 서버에 연결 (SSE 방식)
    server_url = "http://localhost:8000/mcp"
    
    print(f"📡 서버 연결 중: {server_url}")
    
    try:
        async with Client(server_url) as client:
            print("✅ HTTP 서버에 성공적으로 연결되었습니다!")
            
            # 1. 사용 가능한 도구 목록 확인
            print("\n📋 사용 가능한 도구들:")
            tools = await client.list_tools()
            if hasattr(tools, 'tools'):
                tool_list = tools.tools
            else:
                tool_list = tools
            
            for tool in tool_list:
                print(f"  - {tool.name}: {tool.description}")
            
            # 2. 간단한 도구 테스트
            print("\n🧪 HTTP 서버 도구 테스트:")
            
            # 숫자 더하기 테스트
            print("\n➕ 숫자 더하기 테스트:")
            result = await client.call_tool("add_numbers", {"a": 10, "b": 20})
            if hasattr(result, 'content') and result.content:
                print(f"  10 + 20 = {result.content[0].text}")
            else:
                print(f"  결과: {result}")
            
            # 현재 시간 테스트
            print("\n⏰ 현재 시간 테스트:")
            result = await client.call_tool("get_current_time", {})
            if hasattr(result, 'content') and result.content:
                print(f"  현재 시간: {result.content[0].text}")
            else:
                print(f"  결과: {result}")
            
            # 3. 리소스 테스트
            print("\n📊 리소스 테스트:")
            
            # 시스템 정보
            print("\n🖥️ 시스템 정보:")
            result = await client.read_resource("system://info")
            if hasattr(result, 'contents') and result.contents:
                content = result.contents[0].text
                print(content[:200] + "..." if len(content) > 200 else content)
            else:
                print(f"  결과: {result}")
            
            print("\n✅ HTTP 서버 테스트가 완료되었습니다!")
            
    except Exception as e:
        print(f"❌ 연결 실패: {e}")
        print("\n💡 해결 방법:")
        print("1. HTTP 서버가 실행 중인지 확인하세요: python http_server.py")
        print("2. 포트 8000이 사용 가능한지 확인하세요")
        print("3. 방화벽 설정을 확인하세요")


async def test_different_connection_methods():
    """다양한 연결 방법 테스트"""
    
    print("\n🔍 다양한 연결 방법 테스트...")
    
    # 1. SSE 방식 (기본)
    print("\n1️⃣ SSE 방식 연결 시도:")
    try:
        async with Client("http://localhost:8000/mcp") as client:
            tools = await client.list_tools()
            print(f"✅ SSE 연결 성공! 도구 수: {len(tools) if hasattr(tools, '__len__') else 'N/A'}")
    except Exception as e:
        print(f"❌ SSE 연결 실패: {e}")
    
    # 2. 명시적 transport 지정
    print("\n2️⃣ 명시적 HTTP transport 연결 시도:")
    try:
        # 이 방법은 fastMCP 클라이언트에서 지원하는 경우에만 작동
        async with Client("http://localhost:8000/mcp", transport="http") as client:
            tools = await client.list_tools()
            print(f"✅ HTTP transport 연결 성공! 도구 수: {len(tools) if hasattr(tools, '__len__') else 'N/A'}")
    except Exception as e:
        print(f"❌ HTTP transport 연결 실패: {e}")


if __name__ == "__main__":
    print("🚀 fastMCP HTTP 클라이언트 테스트를 시작합니다...\n")
    
    # HTTP 서버 테스트
    asyncio.run(test_http_server())
    
    # 다양한 연결 방법 테스트
    asyncio.run(test_different_connection_methods())
    
    print("\n🎉 HTTP 클라이언트 테스트가 완료되었습니다!")
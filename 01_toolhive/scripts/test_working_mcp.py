#!/usr/bin/env python3
"""
작동하는 ToolHive Playwright MCP 연결 테스트
"""

import json
import requests
import re

BASE_URL = "http://127.0.0.1:44251"

def get_session_id():
    """SSE 엔드포인트에서 sessionId를 획득합니다."""
    try:
        response = requests.get(f"{BASE_URL}/sse", 
                              headers={"Accept": "text/event-stream"},
                              stream=True)
        
        for line in response.iter_lines(decode_unicode=True):
            if line and line.startswith("data:"):
                data = line.replace("data:", "").strip()
                match = re.search(r"sessionId=([a-f0-9\-]+)", data)
                if match:
                    session_id = match.group(1)
                    print(f"✅ 세션 ID 획득: {session_id}")
                    return session_id
    except Exception as e:
        print(f"❌ 세션 ID 획득 실패: {e}")
        return None
    
    return None

def parse_sse_response(response_text):
    """SSE 응답을 파싱하여 JSON 데이터 추출"""
    for line in response_text.split('\n'):
        if line.startswith('data: '):
            data_str = line[6:].strip()
            if data_str:
                try:
                    return json.loads(data_str)
                except json.JSONDecodeError:
                    continue
    return None

def jsonrpc_request(method, params=None, rpc_id=1, session_id=None):
    payload = {
        "jsonrpc": "2.0",
        "id": rpc_id,
        "method": method,
        "params": params or {}
    }
    
    response = requests.post(
        f"{BASE_URL}/messages?sessionId={session_id}",
        headers={
            "Accept": "application/json, text/event-stream",
            "Content-Type": "application/json"
        },
        data=json.dumps(payload)
    )
    
    if response.headers.get('content-type', '').startswith('text/event-stream'):
        # SSE 응답 파싱
        return parse_sse_response(response.text)
    else:
        try:
            return response.json()
        except json.JSONDecodeError:
            return {"error": "Failed to parse response", "text": response.text}

if __name__ == "__main__":
    # 1. 세션 ID 획득
    session_id = get_session_id()
    if not session_id:
        exit(1)
    
    print("\n=== MCP 표준 프로토콜 초기화 ===")
    
    # 2. initialize 호출
    print("🚀 서버 초기화 중...")
    init_result = jsonrpc_request("initialize", {
        "protocolVersion": "2024-11-05",
        "capabilities": {
            "roots": {
                "listChanged": True
            }
        },
        "clientInfo": {
            "name": "tistory-scraper",
            "version": "1.0.0"
        }
    }, rpc_id=1, session_id=session_id)
    
    if init_result and "result" in init_result:
        print("✅ 서버 초기화 성공!")
        print(f"서버 이름: {init_result['result']['serverInfo']['name']}")
        print(f"서버 버전: {init_result['result']['serverInfo']['version']}")
        print(f"프로토콜 버전: {init_result['result']['protocolVersion']}")
        
        # 3. initialized 알림 (올바른 메서드명 사용)
        print("\n📢 initialized 알림 전송...")
        # MCP 표준에 따르면 notification은 별도 메서드
        notification_payload = {
            "jsonrpc": "2.0",
            "method": "initialized"
        }
        
        notification_response = requests.post(
            f"{BASE_URL}/messages?sessionId={session_id}",
            headers={
                "Accept": "application/json, text/event-stream",
                "Content-Type": "application/json"
            },
            data=json.dumps(notification_payload)
        )
        print(f"알림 응답 상태: {notification_response.status_code}")
        
        # 4. tools/list 호출
        print("\n🔧 사용 가능한 도구 목록 조회...")
        tools_result = jsonrpc_request("tools/list", {}, rpc_id=2, session_id=session_id)
        
        if tools_result and "result" in tools_result:
            print("✅ 도구 목록 조회 성공!")
            tools = tools_result['result'].get('tools', [])
            print(f"사용 가능한 도구 수: {len(tools)}")
            for i, tool in enumerate(tools, 1):
                print(f"  {i}. {tool.get('name', 'Unknown')} - {tool.get('description', 'No description')}")
        else:
            print(f"❌ 도구 목록 조회 실패: {tools_result}")
            
        # 5. 실제 브라우저 명령 테스트
        if tools_result and "result" in tools_result:
            print("\n🌐 브라우저 navigate 테스트...")
            navigate_result = jsonrpc_request("tools/call", {
                "name": "navigate",
                "arguments": {
                    "url": "https://metashower.tistory.com/"
                }
            }, rpc_id=3, session_id=session_id)
            
            if navigate_result and "result" in navigate_result:
                print("✅ 브라우저 네비게이션 성공!")
                print("응답:", json.dumps(navigate_result, indent=2, ensure_ascii=False))
            else:
                print(f"❌ 브라우저 네비게이션 실패: {navigate_result}")
        
    else:
        print(f"❌ 서버 초기화 실패: {init_result}")
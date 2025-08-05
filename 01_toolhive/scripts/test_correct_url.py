#!/usr/bin/env python3
"""
ToolHive Playwright MCP의 올바른 URL 패턴 테스트
"""

import json
import requests
import re

# thv list에서 확인된 URL: http://127.0.0.1:44251/sse#playwright
BASE_URL = "http://127.0.0.1:44251"
SSE_URL = f"{BASE_URL}/sse#playwright"

def get_session_id():
    """SSE 엔드포인트에서 sessionId를 획득합니다."""
    try:
        # fragment (#playwright) 부분 제거하고 요청
        clean_sse_url = f"{BASE_URL}/sse"
        
        print(f"SSE URL: {clean_sse_url}")
        response = requests.get(clean_sse_url, 
                              headers={"Accept": "text/event-stream"},
                              stream=True)
        
        print(f"응답 상태: {response.status_code}")
        
        for line in response.iter_lines(decode_unicode=True):
            if line and line.startswith("data:"):
                data = line.replace("data:", "").strip()
                print(f"SSE 데이터: {data}")
                
                match = re.search(r"sessionId=([a-f0-9\-]+)", data)
                if match:
                    session_id = match.group(1)
                    print(f"세션 ID 획득: {session_id}")
                    return session_id
                    
    except Exception as e:
        print(f"세션 ID 획득 실패: {e}")
        return None
    
    print("❌ sessionId를 찾을 수 없습니다.")
    return None

def jsonrpc_request(method, params=None, rpc_id=1, session_id=None):
    # URL에 #playwright 추가해서 시도
    messages_url = f"{BASE_URL}/messages?sessionId={session_id}"
    
    payload = {
        "jsonrpc": "2.0",
        "id": rpc_id,
        "method": method,
        "params": params or {}
    }
    
    print(f"요청 URL: {messages_url}")
    print(f"페이로드: {json.dumps(payload, indent=2)}")
    
    response = requests.post(
        messages_url,
        headers={
            "Accept": "application/json, text/event-stream",
            "Content-Type": "application/json"
        },
        data=json.dumps(payload)
    )
    
    print(f"응답 상태: {response.status_code}")
    print(f"응답 헤더: {dict(response.headers)}")
    
    try:
        return response.json()
    except json.JSONDecodeError:
        print(f"응답 텍스트: {response.text}")
        return response.text

if __name__ == "__main__":
    # 1. SSE에서 sessionId 획득
    session_id = get_session_id()
    if not session_id:
        print("세션 ID를 획득할 수 없어 종료합니다.")
        exit(1)
    
    print("\n=== MCP 프로토콜 표준 초기화 시도 ===")
    
    # MCP 표준 초기화
    print("1. MCP 표준 initialize 호출...")
    init_result = jsonrpc_request("initialize", {
        "protocolVersion": "2024-11-05",
        "capabilities": {
            "roots": {
                "listChanged": True
            },
            "sampling": {}
        },
        "clientInfo": {
            "name": "tistory-scraper",
            "version": "1.0.0"
        }
    }, rpc_id=1, session_id=session_id)
    print("initialize 응답:", json.dumps(init_result, indent=2, ensure_ascii=False))
    
    print("\n2. initialized 알림 전송...")
    initialized_result = jsonrpc_request("notifications/initialized", {}, rpc_id=2, session_id=session_id)
    print("initialized 응답:", json.dumps(initialized_result, indent=2, ensure_ascii=False))
    
    print("\n3. tools/list 호출...")
    tools_result = jsonrpc_request("tools/list", {}, rpc_id=3, session_id=session_id)
    print("tools/list 응답:", json.dumps(tools_result, indent=2, ensure_ascii=False))
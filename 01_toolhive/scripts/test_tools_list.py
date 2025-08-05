#!/usr/bin/env python3
"""
ToolHive Playwright MCP의 사용 가능한 도구들을 확인하는 테스트
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
                    print(f"세션 ID 획득: {session_id}")
                    return session_id
    except Exception as e:
        print(f"세션 ID 획득 실패: {e}")
        return None
    
    print("❌ sessionId를 찾을 수 없습니다.")
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
    try:
        return response.json()
    except json.JSONDecodeError:
        return response.text

if __name__ == "__main__":
    # 1. SSE에서 sessionId 획득
    session_id = get_session_id()
    if not session_id:
        print("세션 ID를 획득할 수 없어 종료합니다.")
        exit(1)
    
    print("\n=== ToolHive Playwright MCP 도구 목록 확인 ===")
    
    # tools/list 호출
    print("1. tools/list 호출...")
    tools_list_result = jsonrpc_request("tools/list", {}, rpc_id=1, session_id=session_id)
    print("tools/list 응답:", json.dumps(tools_list_result, indent=2, ensure_ascii=False))
    
    # 다른 방법들도 시도
    print("\n2. tools/call 방식으로 list 호출...")
    tools_call_list_result = jsonrpc_request("tools/call", {
        "name": "list"
    }, rpc_id=2, session_id=session_id)
    print("tools/call list 응답:", json.dumps(tools_call_list_result, indent=2, ensure_ascii=False))
    
    print("\n3. 직접 navigate 시도 (초기화 없이)...")
    direct_navigate_result = jsonrpc_request("navigate", {
        "url": "https://metashower.tistory.com/"
    }, rpc_id=3, session_id=session_id)
    print("직접 navigate 응답:", json.dumps(direct_navigate_result, indent=2, ensure_ascii=False))
    
    print("\n4. tools/call navigate 시도...")
    tools_call_navigate_result = jsonrpc_request("tools/call", {
        "name": "navigate",
        "arguments": {"url": "https://metashower.tistory.com/"}
    }, rpc_id=4, session_id=session_id)
    print("tools/call navigate 응답:", json.dumps(tools_call_navigate_result, indent=2, ensure_ascii=False))
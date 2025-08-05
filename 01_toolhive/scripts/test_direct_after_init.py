#!/usr/bin/env python3
"""
initialize 직후 바로 도구 사용 테스트
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
    
    print("\n=== 빠른 초기화 및 도구 사용 ===")
    
    # 2. initialize 호출
    print("🚀 서버 초기화 중...")
    init_result = jsonrpc_request("initialize", {
        "protocolVersion": "2024-11-05",
        "capabilities": {},
        "clientInfo": {
            "name": "tistory-scraper",
            "version": "1.0.0"
        }
    }, rpc_id=1, session_id=session_id)
    
    if init_result and "result" in init_result:
        print("✅ 서버 초기화 성공!")
        
        # 3. 바로 브라우저 navigate 시도
        print("\n🌐 브라우저 navigate 시도...")
        navigate_result = jsonrpc_request("tools/call", {
            "name": "navigate",
            "arguments": {
                "url": "https://metashower.tistory.com/"
            }
        }, rpc_id=2, session_id=session_id)
        
        print(f"Navigate 결과: {json.dumps(navigate_result, indent=2, ensure_ascii=False)}")
        
        if navigate_result and "result" in navigate_result:
            print("✅ 브라우저 네비게이션 성공!")
            
            # 4. 페이지 스냅샷 시도
            print("\n📸 페이지 스냅샷 시도...")
            snapshot_result = jsonrpc_request("tools/call", {
                "name": "screenshot",
                "arguments": {}
            }, rpc_id=3, session_id=session_id)
            
            print(f"스냅샷 결과: {json.dumps(snapshot_result, indent=2, ensure_ascii=False)}")
            
            # 5. 다른 도구들 시도
            print("\n🔍 페이지 내용 추출 시도...")
            
            # HTML 추출
            html_result = jsonrpc_request("tools/call", {
                "name": "getPageContent",
                "arguments": {}
            }, rpc_id=4, session_id=session_id)
            
            if html_result and "error" in html_result:
                # 다른 메서드명 시도
                html_result = jsonrpc_request("tools/call", {
                    "name": "get_page_content",
                    "arguments": {}
                }, rpc_id=5, session_id=session_id)
            
            if html_result and "error" in html_result:
                # 또 다른 메서드명 시도
                html_result = jsonrpc_request("tools/call", {
                    "name": "content",
                    "arguments": {}
                }, rpc_id=6, session_id=session_id)
            
            print(f"HTML 추출 결과: {json.dumps(html_result, indent=2, ensure_ascii=False)}")
            
        else:
            print(f"❌ 브라우저 네비게이션 실패: {navigate_result}")
            
    else:
        print(f"❌ 서버 초기화 실패: {init_result}")
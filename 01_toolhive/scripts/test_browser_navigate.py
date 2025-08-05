#!/usr/bin/env python3
"""
browser_navigate 직접 호출 테스트
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
    
    print(f"📤 요청: {method}")
    print(f"📦 파라미터: {json.dumps(params, indent=2, ensure_ascii=False)}")
    
    response = requests.post(
        f"{BASE_URL}/messages?sessionId={session_id}",
        headers={
            "Accept": "application/json, text/event-stream",
            "Content-Type": "application/json"
        },
        data=json.dumps(payload)
    )
    
    print(f"📥 응답 상태: {response.status_code}")
    
    if response.headers.get('content-type', '').startswith('text/event-stream'):
        # SSE 응답 파싱
        result = parse_sse_response(response.text)
        print(f"📄 파싱된 응답: {json.dumps(result, indent=2, ensure_ascii=False)}")
        return result
    else:
        try:
            result = response.json()
            print(f"📄 JSON 응답: {json.dumps(result, indent=2, ensure_ascii=False)}")
            return result
        except json.JSONDecodeError:
            print(f"📄 텍스트 응답: {response.text}")
            return {"error": "Failed to parse response", "text": response.text}

if __name__ == "__main__":
    # 1. 세션 ID 획득
    session_id = get_session_id()
    if not session_id:
        exit(1)
    
    print("\n=== 다양한 브라우저 명령 시도 ===")
    
    # 2. initialize 호출
    print("\n🚀 서버 초기화...")
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
        
        # 3. 직접 browser_navigate 호출
        print("\n🌐 직접 browser_navigate 호출...")
        navigate_result = jsonrpc_request("browser_navigate", {
            "url": "https://metashower.tistory.com/"
        }, rpc_id=2, session_id=session_id)
        
        if navigate_result and "result" in navigate_result:
            print("✅ 브라우저 네비게이션 성공!")
            
            # 4. 브라우저 상태 확인
            print("\n📊 브라우저 상태 확인...")
            status_result = jsonrpc_request("browser_status", {}, rpc_id=3, session_id=session_id)
            
            # 5. 페이지 콘텐츠 가져오기
            print("\n📄 페이지 콘텐츠 가져오기...")
            content_result = jsonrpc_request("browser_content", {}, rpc_id=4, session_id=session_id)
            
            # 6. 다른 가능한 메서드들 시도
            possible_methods = [
                "get_content",
                "page_content", 
                "screenshot",
                "get_html",
                "extract_text"
            ]
            
            for i, method in enumerate(possible_methods, 5):
                print(f"\n🔧 {method} 시도...")
                result = jsonrpc_request(method, {}, rpc_id=i, session_id=session_id)
                
        else:
            print(f"❌ 브라우저 네비게이션 실패: {navigate_result}")
            
    else:
        print(f"❌ 서버 초기화 실패: {init_result}")
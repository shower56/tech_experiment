#!/usr/bin/env python3
"""
ToolHive playwright MCP 서버에 직접 연결하는 개선된 클라이언트
다양한 접근 방법을 시도하여 정확한 통신 방법을 찾아냅니다.
"""

import requests
import json
import re
import time
from typing import Optional, Dict, Any

BASE_URL = "http://127.0.0.1:19926"

class ToolHiveMCPClient:
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.session_id: Optional[str] = None
        self.session = requests.Session()
        
    def get_session_id(self) -> Optional[str]:
        """SSE 엔드포인트에서 sessionId를 획득"""
        try:
            print("🔗 SSE 연결 시도...")
            response = self.session.get(
                f"{self.base_url}/sse", 
                headers={"Accept": "text/event-stream"},
                stream=True,
                timeout=10
            )
            
            for line in response.iter_lines(decode_unicode=True, chunk_size=1):
                if line and line.startswith("data:"):
                    data = line.replace("data:", "").strip()
                    print(f"📡 SSE 데이터: {data}")
                    
                    # sessionId 패턴 매칭
                    match = re.search(r"sessionId=([a-f0-9\-]+)", data)
                    if match:
                        self.session_id = match.group(1)
                        print(f"✅ 세션 ID 획득: {self.session_id}")
                        response.close()
                        return self.session_id
                        
        except Exception as e:
            print(f"❌ SSE 연결 실패: {e}")
            return None
        
        print("❌ sessionId를 찾을 수 없습니다.")
        return None
    
    def send_request(self, endpoint: str, method: str, params: Dict[str, Any] = None, rpc_id: int = 1) -> Optional[Dict]:
        """MCP 서버에 요청 전송"""
        if not self.session_id:
            print("❌ 세션 ID가 없습니다.")
            return None
            
        url = f"{self.base_url}{endpoint}?sessionId={self.session_id}"
        payload = {
            "jsonrpc": "2.0",
            "id": rpc_id,
            "method": method,
            "params": params or {}
        }
        
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream"
        }
        
        try:
            print(f"📤 요청: {method} -> {url}")
            print(f"📦 페이로드: {json.dumps(payload, indent=2)}")
            
            response = self.session.post(url, headers=headers, json=payload, timeout=10)
            
            print(f"📥 응답 상태: {response.status_code}")
            print(f"📄 응답 내용: {response.text}")
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ HTTP 오류: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ 요청 실패: {e}")
            return None
    
    def test_all_endpoints(self):
        """다양한 엔드포인트와 메서드 조합 테스트"""
        if not self.session_id:
            print("❌ 세션 ID가 필요합니다.")
            return
        
        # 테스트할 엔드포인트들
        endpoints = ["/message", "/messages", "/rpc", "/jsonrpc"]
        
        # 테스트할 메서드들
        methods = [
            "initialize",
            "tools/list", 
            "list_tools",
            "call_tool",
            "browser_navigate",
            "ping",
            "status"
        ]
        
        print("\n🧪 === 다양한 엔드포인트/메서드 조합 테스트 ===")
        
        for endpoint in endpoints:
            print(f"\n📍 엔드포인트: {endpoint}")
            for method in methods:
                print(f"\n🔍 메서드: {method}")
                
                # 기본 파라미터
                params = {}
                if method == "initialize":
                    params = {
                        "capabilities": {},
                        "clientInfo": {"name": "toolhive-test-client", "version": "1.0.0"}
                    }
                elif method == "call_tool":
                    params = {"name": "browser_navigate", "arguments": {"url": "https://www.example.com"}}
                elif method == "browser_navigate":
                    params = {"url": "https://www.example.com"}
                
                result = self.send_request(endpoint, method, params)
                
                if result and "error" not in result:
                    print(f"✅ 성공! 엔드포인트: {endpoint}, 메서드: {method}")
                    return endpoint, method, result
                
                time.sleep(0.5)  # 요청 간 지연
        
        print("\n❌ 모든 조합에서 실패했습니다.")
        return None
    
    def test_navigate_to_classu(self):
        """클래스유 사이트로 이동 테스트"""
        if not self.session_id:
            print("❌ 세션 ID가 필요합니다.")
            return None
        
        print("\n🎯 === 클래스유 사이트 이동 테스트 ===")
        
        # 성공한 패턴이 있다면 그것을 사용, 아니면 표준 방법 시도
        navigate_methods = [
            ("browser_navigate", {"url": "https://www.classu.co.kr/new"}),
            ("call_tool", {"name": "browser_navigate", "arguments": {"url": "https://www.classu.co.kr/new"}}),
            ("navigate", {"url": "https://www.classu.co.kr/new"})
        ]
        
        for method, params in navigate_methods:
            print(f"\n🚀 {method} 시도...")
            result = self.send_request("/messages", method, params)
            
            if result and "error" not in result:
                print(f"✅ 네비게이션 성공!")
                return result
        
        return None

def main():
    client = ToolHiveMCPClient()
    
    # 1. 세션 ID 획득
    if not client.get_session_id():
        print("❌ 세션 생성 실패")
        return
    
    # 2. 다양한 엔드포인트/메서드 조합 테스트
    successful_combination = client.test_all_endpoints()
    
    if successful_combination:
        endpoint, method, result = successful_combination
        print(f"\n🎉 성공한 조합: {endpoint} + {method}")
        print(f"📋 결과: {json.dumps(result, indent=2, ensure_ascii=False)}")
    
    # 3. 클래스유 사이트 이동 시도
    navigate_result = client.test_navigate_to_classu()
    if navigate_result:
        print(f"\n🌐 네비게이션 결과: {json.dumps(navigate_result, indent=2, ensure_ascii=False)}")

if __name__ == "__main__":
    main()
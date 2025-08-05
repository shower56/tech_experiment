#!/usr/bin/env python3
"""
ToolHive MCP 서버 인증 방법 테스트
"""

import requests
import json
import re
import os
from typing import Optional, Dict, Any

BASE_URL = "http://127.0.0.1:38342"

class AuthenticatedMCPClient:
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.session_id: Optional[str] = None
        self.session = requests.Session()
        
    def get_session_id(self) -> Optional[str]:
        """SSE 엔드포인트에서 sessionId를 획득"""
        try:
            print("🔗 SSE 연결 시도...")
            
            # 다양한 헤더 조합 시도
            header_combinations = [
                # 기본
                {"Accept": "text/event-stream"},
                # 사용자 인증 헤더 추가
                {
                    "Accept": "text/event-stream",
                    "Authorization": f"Bearer local-user-{os.getenv('USER', 'default')}",
                    "X-User": os.getenv('USER', 'default')
                },
                # ToolHive 특화 헤더
                {
                    "Accept": "text/event-stream",
                    "X-ToolHive-User": os.getenv('USER', 'default'),
                    "X-ToolHive-Client": "python-direct-client"
                },
                # 추가 인증 헤더
                {
                    "Accept": "text/event-stream",
                    "User-Agent": "ToolHive-Python-Client/1.0",
                    "X-Requested-With": "ToolHive",
                    "X-Client-Type": "direct"
                }
            ]
            
            for i, headers in enumerate(header_combinations):
                print(f"\n🔄 헤더 조합 {i+1} 시도: {headers}")
                
                response = self.session.get(
                    f"{self.base_url}/sse", 
                    headers=headers,
                    stream=True,
                    timeout=5
                )
                
                print(f"응답 상태: {response.status_code}")
                print(f"응답 헤더: {dict(response.headers)}")
                
                if response.status_code == 200:
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
                
                response.close()
                        
        except Exception as e:
            print(f"❌ SSE 연결 실패: {e}")
            return None
        
        print("❌ sessionId를 찾을 수 없습니다.")
        return None
    
    def test_with_auth_headers(self):
        """인증 헤더를 포함한 요청 테스트"""
        if not self.session_id:
            print("❌ 세션 ID가 없습니다.")
            return None
        
        print(f"\n🔐 === 인증 헤더 포함 테스트 (세션: {self.session_id}) ===")
        
        # 다양한 인증 헤더 조합
        auth_header_sets = [
            # 기본
            {
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream"
            },
            # 사용자 인증
            {
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream",
                "Authorization": f"Bearer local-user-{os.getenv('USER', 'default')}",
                "X-User": os.getenv('USER', 'default')
            },
            # ToolHive 특화
            {
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream",
                "X-ToolHive-User": os.getenv('USER', 'default'),
                "X-ToolHive-Client": "python-direct-client",
                "X-ToolHive-Session": self.session_id
            },
            # 추가 메타데이터
            {
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream",
                "User-Agent": "ToolHive-Python-Client/1.0",
                "X-Requested-With": "ToolHive",
                "X-Client-Type": "direct",
                "X-Session-Id": self.session_id
            }
        ]
        
        # 간단한 initialize 요청
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "capabilities": {},
                "clientInfo": {
                    "name": "toolhive-auth-test-client",
                    "version": "1.0.0"
                }
            }
        }
        
        for i, headers in enumerate(auth_header_sets):
            print(f"\n🧪 인증 헤더 세트 {i+1} 테스트:")
            print(f"헤더: {json.dumps(headers, indent=2)}")
            
            url = f"{self.base_url}/messages?sessionId={self.session_id}"
            
            try:
                response = self.session.post(url, headers=headers, json=payload, timeout=10)
                
                print(f"📥 응답 상태: {response.status_code}")
                print(f"📄 응답 내용: {response.text}")
                
                if response.status_code == 200:
                    result = response.json()
                    if "error" not in result:
                        print(f"✅ 성공! 헤더 세트 {i+1}이 작동합니다!")
                        return headers, result
                
            except Exception as e:
                print(f"❌ 요청 실패: {e}")
        
        print("\n❌ 모든 인증 헤더 조합에서 실패했습니다.")
        return None

def main():
    client = AuthenticatedMCPClient()
    
    # 1. 세션 ID 획득 (다양한 헤더 조합으로)
    if not client.get_session_id():
        print("❌ 세션 생성 실패")
        return
    
    # 2. 인증 헤더 포함 요청 테스트
    auth_result = client.test_with_auth_headers()
    
    if auth_result:
        headers, result = auth_result
        print(f"\n🎉 성공한 인증 헤더:")
        print(json.dumps(headers, indent=2))
        print(f"\n📋 initialize 결과:")
        print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
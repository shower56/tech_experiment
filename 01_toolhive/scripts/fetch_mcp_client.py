#!/usr/bin/env python3
"""
ToolHive fetch MCP 서버를 사용하여 웹 콘텐츠를 가져오고 제목을 추출하는 클라이언트
"""

import requests
import json
import re
from bs4 import BeautifulSoup
from typing import Optional, Dict, Any

FETCH_MCP_URL = "http://127.0.0.1:44322"

class FetchMCPClient:
    def __init__(self, base_url: str = FETCH_MCP_URL):
        self.base_url = base_url
        self.session_id: Optional[str] = None
        self.session = requests.Session()
        
    def get_session_id(self) -> Optional[str]:
        """SSE 엔드포인트에서 sessionId를 획득"""
        try:
            print("🔗 fetch MCP SSE 연결 시도...")
            # fetch MCP는 다른 엔드포인트 패턴을 사용할 수 있음
            endpoints_to_try = ["/mcp", "/sse", "/"]
            
            for endpoint in endpoints_to_try:
                print(f"시도 중: {self.base_url}{endpoint}")
                try:
                    response = self.session.get(
                        f"{self.base_url}{endpoint}", 
                        headers={"Accept": "text/event-stream"},
                        stream=True,
                        timeout=5
                    )
                    
                    print(f"응답 상태: {response.status_code}")
                    
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
                    print(f"엔드포인트 {endpoint} 실패: {e}")
                    continue
                        
        except Exception as e:
            print(f"❌ SSE 연결 실패: {e}")
            return None
        
        print("❌ sessionId를 찾을 수 없습니다.")
        return None
    
    def send_request(self, method: str, params: Dict[str, Any] = None, rpc_id: int = 1) -> Optional[Dict]:
        """fetch MCP 서버에 요청 전송"""
        if not self.session_id:
            print("❌ 세션 ID가 없습니다.")
            return None
            
        # fetch MCP는 다른 URL 패턴을 사용할 수 있음
        url = f"{self.base_url}/mcp?sessionId={self.session_id}"
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
            
            response = self.session.post(url, headers=headers, json=payload, timeout=30)
            
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
    
    def initialize(self) -> bool:
        """MCP 서버 초기화"""
        print("\n🔧 === fetch MCP 서버 초기화 ===")
        
        result = self.send_request("initialize", {
            "capabilities": {},
            "clientInfo": {
                "name": "fetch-test-client",
                "version": "1.0.0"
            }
        })
        
        if result and "error" not in result:
            print("✅ fetch MCP 서버 초기화 성공!")
            return True
        else:
            print("❌ fetch MCP 서버 초기화 실패")
            return False
    
    def list_tools(self) -> Optional[Dict]:
        """사용 가능한 도구 목록 조회"""
        print("\n🛠️ === 사용 가능한 도구 목록 조회 ===")
        
        result = self.send_request("list_tools")
        
        if result and "error" not in result:
            print("✅ 도구 목록 조회 성공!")
            return result
        else:
            print("❌ 도구 목록 조회 실패")
            return None
    
    def fetch_url(self, url: str) -> Optional[str]:
        """URL에서 HTML 콘텐츠 가져오기"""
        print(f"\n🌐 === {url} 콘텐츠 가져오기 ===")
        
        # fetch MCP 서버의 도구를 사용하여 URL 콘텐츠 가져오기
        result = self.send_request("call_tool", {
            "name": "fetch",
            "arguments": {
                "url": url,
                "method": "GET"
            }
        })
        
        if result and "result" in result:
            print("✅ URL 콘텐츠 가져오기 성공!")
            return result["result"].get("content", "")
        else:
            print("❌ URL 콘텐츠 가져오기 실패")
            return None
    
    def extract_title_from_html(self, html_content: str) -> Optional[str]:
        """HTML에서 제목 추출"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            title_tag = soup.find('title')
            if title_tag:
                return title_tag.get_text().strip()
            else:
                print("❌ HTML에서 <title> 태그를 찾을 수 없습니다.")
                return None
        except Exception as e:
            print(f"❌ HTML 파싱 실패: {e}")
            return None
    
    def get_website_title(self, url: str) -> Optional[str]:
        """웹사이트의 제목을 가져오는 전체 프로세스"""
        print(f"\n🎯 === {url}의 제목 추출 시작 ===")
        
        # 1. HTML 콘텐츠 가져오기
        html_content = self.fetch_url(url)
        if not html_content:
            return None
        
        # 2. HTML에서 제목 추출
        title = self.extract_title_from_html(html_content)
        if title:
            print(f"🏆 제목 추출 성공: {title}")
            return title
        else:
            print("❌ 제목 추출 실패")
            return None

def main():
    """메인 실행 함수"""
    print("🚀 ToolHive fetch MCP 클라이언트 시작")
    
    client = FetchMCPClient()
    
    # 1. 세션 ID 획득
    if not client.get_session_id():
        print("❌ 세션 생성 실패")
        return
    
    # 2. 서버 초기화
    if not client.initialize():
        print("❌ 서버 초기화 실패")
        return
    
    # 3. 도구 목록 확인
    tools = client.list_tools()
    if tools:
        print("📋 사용 가능한 도구:")
        if "result" in tools and "tools" in tools["result"]:
            for tool in tools["result"]["tools"]:
                print(f"  - {tool.get('name', 'Unknown')}: {tool.get('description', 'No description')}")
    
    # 4. 클래스유 사이트 제목 추출
    classu_title = client.get_website_title("https://www.classu.co.kr/new")
    
    if classu_title:
        print(f"\n🎉 최종 결과: {classu_title}")
    else:
        print("\n❌ 클래스유 사이트 제목 추출 실패")

if __name__ == "__main__":
    main()
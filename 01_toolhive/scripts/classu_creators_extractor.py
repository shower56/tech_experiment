#!/usr/bin/env python3
"""
클래스유(classu.co.kr) 웹사이트에서 인기 크리에이터(선생님) TOP 50 정보를 추출하는 스크립트입니다.
이 스크립트는 ToolHive의 Playwright MCP 서버를 활용합니다.
"""

import json
import time
import sys
from urllib.parse import urljoin
import requests

# MCP 서버 URL 설정
# MCP 서버는 /sse 엔드포인트를 사용해야 합니다
MCP_SERVER_URL = "http://127.0.0.1:28632/sse"

def send_mcp_request(method, params=None):
    """MCP 서버에 요청을 보내고 응답을 받습니다."""
    if params is None:
        params = {}
    
    # 세션 ID를 먼저 가져옵니다
    try:
        print(f"MCP_SERVER_URL: {MCP_SERVER_URL}")
        session_response = requests.get(MCP_SERVER_URL)
        session_response.raise_for_status()
        
        # 응답에서 세션 ID 추출
        for line in session_response.text.split('\n'):
            if line.startswith('data: /sse?sessionId='):
                session_id = line.replace('data: /sse?sessionId=', '').strip()
                break
        else:
            raise Exception("세션 ID를 찾을 수 없습니다")
        
        print(f"세션 ID 획득: {session_id}")
        
        # 올바른 JSON-RPC 페이로드 구성
        # MCP 서버는 tool_ 접두사가 붙은 메서드 이름을 사용합니다
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": f"tool_{method}",
            "params": params
        }
        
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream"
        }
        
        # 메시지 엔드포인트로 요청을 보냅니다 (세션 ID 포함)
        # MCP 서버는 /messages 엔드포인트를 통해 JSON-RPC 요청을 처리합니다
        messages_url = MCP_SERVER_URL.replace("/sse", "/messages")
        print(f"요청 URL: {messages_url}")
        print(f"요청 페이로드: {json.dumps(payload)}")
        
        response = requests.post(messages_url, json=payload, headers=headers)
        response.raise_for_status()
        
        print(f"응답 상태 코드: {response.status_code}")
        print(f"응답 내용: {response.text[:200]}...")  # 응답의 처음 200자만 출력
        
        # JSON 응답 처리
        try:
            result = response.json()
            print(f"JSON 응답: {json.dumps(result)[:200]}...")
            return result
        except json.JSONDecodeError as e:
            print(f"JSON 디코딩 오류: {e}")
            
            # SSE 응답 형식 처리 시도
            lines = response.text.strip().split('\n')
            for line in lines:
                if line.startswith('data: '):
                    data = line[6:]  # 'data: ' 접두사 제거
                    try:
                        return json.loads(data)
                    except json.JSONDecodeError:
                        continue
            
            print(f"응답 형식 오류: {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"요청 오류: {e}")
        return None

def extract_creators_from_classu():
    """클래스유 웹사이트에서 크리에이터 정보를 추출합니다."""
    # 브라우저 시작
    print("브라우저를 시작합니다...")
    
    # 클래스유 메인 페이지로 이동
    print("클래스유 웹사이트로 이동합니다...")
    navigate_result = send_mcp_request("browser_navigate", {"url": "https://www.classu.co.kr/new"})
    if not navigate_result:
        print("웹사이트 이동에 실패했습니다.")
        return []
    
    # 페이지 로딩 대기
    time.sleep(5)
    
    # 스냅샷 가져오기
    print("페이지 스냅샷을 가져옵니다...")
    snapshot_result = send_mcp_request("browser_snapshot")
    if not snapshot_result:
        print("스냅샷 가져오기에 실패했습니다.")
        return []
    
    # 스냅샷 저장 (디버깅용)
    with open("classu_snapshot.json", "w", encoding="utf-8") as f:
        json.dump(snapshot_result, f, ensure_ascii=False, indent=2)
    
    # 크리에이터 정보 추출
    creators = []
    
    # 여기에 크리에이터 정보 추출 로직을 구현합니다.
    # 실제 웹사이트 구조에 따라 이 부분은 수정될 수 있습니다.
    
    return creators

def main():
    """메인 함수"""
    print("클래스유 크리에이터 정보 추출을 시작합니다...")
    
    creators = extract_creators_from_classu()
    
    if creators:
        print(f"총 {len(creators)}명의 크리에이터 정보를 추출했습니다.")
        with open("classu_creators.json", "w", encoding="utf-8") as f:
            json.dump(creators, f, ensure_ascii=False, indent=2)
        print("크리에이터 정보가 classu_creators.json 파일에 저장되었습니다.")
    else:
        print("크리에이터 정보를 추출하지 못했습니다.")

if __name__ == "__main__":
    main()
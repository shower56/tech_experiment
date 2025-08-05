import requests
import json
import re
import time

BASE_URL = "http://127.0.0.1:38342"

def create_session():
    headers = {"Accept": "text/event-stream, application/json"}
    resp = requests.get(f"{BASE_URL}/sse", headers=headers, stream=True)
    session_id = None
    for line in resp.iter_lines():
        if line and line.startswith(b"data:"):
            data_line = line.decode().replace("data: ", "")
            match = re.search(r"sessionId=([a-z0-9\-]+)", data_line)
            if match:
                session_id = match.group(1)
                print(f"✅ 세션 생성됨: {session_id}")
                resp.close()
                break
    return session_id

def send_rpc(session_id, method, params=None, rpc_id=1):
    url = f"{BASE_URL}/message?sessionId={session_id}"
    headers = {
        "Accept": "application/json, text/event-stream",
        "Content-Type": "application/json"
    }
    payload = {
        "jsonrpc": "2.0",
        "id": rpc_id,
        "method": method,
        "params": params or {}
    }
    response = requests.post(url, headers=headers, json=payload)
    print(f"🔎 {method} 응답:", response.status_code, response.text)
    return response.json() if response.status_code == 200 else None

if __name__ == "__main__":
    session_id = create_session()
    if session_id:
        # 1️⃣ 서버 초기화
        init_result = send_rpc(session_id, "initialize", {
            "capabilities": {},
            "clientInfo": {"name": "python-client", "version": "1.0"}
        })

        # 2️⃣ 사용 가능한 툴 확인
        tools = send_rpc(session_id, "list_tools")
        print("🛠️ 사용 가능한 툴:", tools)

        # 3️⃣ 페이지 이동
        nav_result = send_rpc(session_id, "call_tool", {
            "name": "navigate",
            "arguments": {"url": "https://www.classu.co.kr/new"}
        })

        # 잠깐 대기 (페이지 로딩)
        time.sleep(2)

        # 4️⃣ 제목 가져오기
        result = send_rpc(session_id, "call_tool", {
            "name": "get_title",
            "arguments": {}
        })

        if result and "result" in result:
            print("📌 사이트 제목:", result["result"])
        else:
            print("❌ 제목을 가져올 수 없습니다.")
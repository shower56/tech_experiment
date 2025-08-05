#!/usr/bin/env python3
"""
fastMCP HTTP 서버

HTTP 모드로 실행되는 fastMCP 서버입니다.
웹 브라우저나 HTTP 클라이언트에서 접근할 수 있습니다.
"""

from app import mcp  # 기본 서버 설정 가져오기


if __name__ == "__main__":
    print("🌐 fastMCP HTTP 서버를 시작합니다...")
    print("📡 서버 주소: http://localhost:8000")
    print("🔗 MCP 엔드포인트: http://localhost:8000/mcp")
    print("📖 문서: http://localhost:8000/docs")
    print("\n서버를 중지하려면 Ctrl+C를 누르세요.")
    
    # HTTP 모드로 서버 실행
    mcp.run(transport="http", host="0.0.0.0", port=8000)
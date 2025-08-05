# fastMCP 실험 프로젝트 🚀

**Model Context Protocol (MCP) 학습 및 실험을 위한 Python 프로젝트**

## 프로젝트 개요

이 프로젝트는 fastMCP 라이브러리를 사용하여 Model Context Protocol (MCP) 서버와 클라이언트를 구현하고 테스트하는 실험 프로젝트입니다.

### MCP란?
Model Context Protocol (MCP)는 LLM이 외부 데이터와 기능에 접근할 수 있도록 하는 표준화된 프로토콜입니다. "AI를 위한 USB-C 포트"라고 불리며, LLM과 다양한 리소스를 안전하고 표준화된 방식으로 연결합니다.

## 주요 기능

### 🛠️ 기본 도구 (Tools)
- 수학 계산 (덧셈, 곱셈, 거듭제곱)
- 랜덤 숫자 생성
- 시간 조회
- JSON 데이터 생성
- Context를 사용한 비동기 데이터 처리

### 📊 리소스 (Resources)
- 시스템 정보 조회
- 서버 상태 모니터링
- 샘플 데이터 제공 (사용자, 제품, 주문)

### 💬 프롬프트 (Prompts)
- 코드 리뷰용 프롬프트
- 데이터 분석용 프롬프트
- 문제 해결용 구조화된 프롬프트

### 🔬 고급 기능
- **파일 관리**: 파일 생성, 읽기, 목록 조회
- **데이터베이스**: SQLite 기반 CRUD 작업
- **외부 API 연동**: HTTP 클라이언트를 통한 외부 서비스 호출
- **데이터 분석**: 숫자 통계 분석, 텍스트 분석

### 🎭 Playwright 웹 자동화 (NEW!)
- **브라우저 제어**: Chromium, Firefox, WebKit 지원
- **웹 탐색**: URL 이동, 페이지 정보 수집, 텍스트 추출
- **스크린샷**: 전체 페이지 또는 특정 요소 캡처
- **요소 상호작용**: 클릭, 텍스트 입력, 대기
- **JavaScript 실행**: 페이지에서 동적 스크립트 실행
- **블로그 분석 특화**: 포스트 추출, SEO 분석, 컨텐츠 분석

## 설치 및 실행

### 1. 의존성 설치
```bash
cd 02_fastmcp
pip install -r requirements.txt
```

### 2. 기본 서버 실행 (STDIO 모드)
```bash
cd script
python app.py
```

### 3. HTTP 서버 실행
```bash
cd script
python http_server.py
```
- 서버 주소: http://localhost:8000
- MCP 엔드포인트: http://localhost:8000/mcp
- API 문서: http://localhost:8000/docs

### 4. 클라이언트 테스트
```bash
cd script
python client.py              # 기본 기능 테스트
python test_advanced.py       # 고급 기능 테스트
python test_playwright_mcp.py # Playwright 웹 자동화 테스트 🎭
python test_blog_analyzer.py  # 블로그 분석 테스트 📊
```

### 5. Playwright 웹 자동화 서버 실행
```bash
cd script
python playwright_mcp.py      # 기본 Playwright 서버
python blog_analyzer_mcp.py   # 블로그 분석 특화 서버
```

## 파일 구조

```
02_fastmcp/
├── README.md                      # 이 파일  
├── requirements.txt               # Python 의존성
├── script/
│   ├── app.py                    # 기본 MCP 서버
│   ├── client.py                 # 클라이언트 테스트
│   ├── http_server.py            # HTTP 모드 서버
│   ├── http_client.py            # HTTP 클라이언트 테스트
│   ├── advanced_features.py      # 고급 기능 서버
│   ├── test_advanced.py          # 고급 기능 테스트
│   ├── playwright_mcp.py         # Playwright MCP 서버 🎭
│   ├── test_playwright_mcp.py    # Playwright 기본 테스트
│   ├── blog_analyzer_mcp.py      # 블로그 분석 특화 서버 📊
│   └── test_blog_analyzer.py     # 블로그 분석 테스트
└── docs/
    └── fastMCP_실험_보고서.md     # 상세한 실험 보고서
```

## 사용 예시

### 기본 서버 구현
```python
from fastmcp import FastMCP

mcp = FastMCP("내 서버")

@mcp.tool
def add_numbers(a: float, b: float) -> float:
    """두 숫자를 더합니다."""
    return a + b

@mcp.resource("data://users")
def get_users() -> str:
    return '{"users": ["Alice", "Bob"]}'

@mcp.prompt
def help_prompt() -> str:
    return "도움이 필요하면 언제든 문의하세요!"

if __name__ == "__main__":
    mcp.run()
```

### 클라이언트 사용
```python
from fastmcp import Client
import asyncio

async def main():
    async with Client("./app.py") as client:
        # 도구 호출
        result = await client.call_tool("add_numbers", {"a": 5, "b": 3})
        print(f"결과: {result.content[0].text}")
        
        # 리소스 읽기
        result = await client.read_resource("data://users")
        print(f"사용자: {result.contents[0].text}")

asyncio.run(main())
```

## 테스트 결과

✅ **모든 테스트 통과** (2025.08.05 기준)

- **기본 기능**: 7개 도구, 3개 리소스, 3개 프롬프트 모두 정상 작동
- **고급 기능**: 파일 관리, 데이터베이스, API 연동, 데이터 분석 모두 성공
- **클라이언트 연동**: 인메모리 및 HTTP 통신 모두 정상
- **Playwright 웹 자동화**: 🎭
  - metashower.tistory.com 블로그 분석 성공
  - 포스트 5개 추출: "Toolhive MCP", "LangGraph", "MoE", "MCP", "Python decimal"
  - SEO 분석: 헤딩 구조, 이미지 최적화, 소셜 미디어 태그 모두 확인
  - 스크린샷 생성: 295KB 전체 페이지 캡처 성공
  - Google 검색, GitHub 탐색 모두 정상 작동

## 주요 학습 내용

1. **fastMCP 아키텍처**: 데코레이터 기반의 직관적인 API 설계
2. **비동기 처리**: asyncio를 활용한 고성능 비동기 서버
3. **타입 안전성**: Python 타입 힌트 완전 지원
4. **확장성**: 다양한 전송 모드 (STDIO, HTTP, SSE) 지원
5. **Context 활용**: 로깅, 샘플링 등 세션 기능

## 활용 시나리오

- 🔍 **데이터 분석 도구**: LLM이 실시간으로 데이터를 분석
- 📁 **파일 관리 시스템**: 자연어로 파일 조작
- 🗃️ **데이터베이스 인터페이스**: 자연어 쿼리 지원
- 🌐 **API 통합 허브**: 여러 외부 API를 단일 인터페이스로 통합
- 🎭 **웹 자동화**: LLM이 웹 브라우저를 직접 조작하여 정보 수집
- 📊 **블로그 분석**: 블로그 포스트 자동 분석 및 SEO 최적화 점검
- 🖼️ **화면 캡처**: 웹페이지 스크린샷 자동 생성 및 관리
- 🤖 **웹 스크래핑**: 동적 웹사이트에서 데이터 수집

## 기술 스택

- **언어**: Python 3.11+
- **프레임워크**: fastMCP 2.11.1
- **데이터베이스**: SQLite (인메모리)
- **HTTP 서버**: uvicorn
- **HTTP 클라이언트**: httpx
- **웹 자동화**: Playwright 1.54.0 🎭
- **브라우저**: Chromium, Firefox, WebKit
- **의존성 관리**: pip

## 향후 계획

- [ ] 프로덕션 배포 환경 구축
- [ ] 인증 및 보안 기능 추가
- [ ] 이미지/멀티미디어 처리 기능
- [ ] 대용량 데이터 처리 최적화
- [ ] 실시간 스트리밍 기능

## 참고 자료

- [fastMCP 공식 문서](https://gofastmcp.com)
- [fastMCP GitHub](https://github.com/jlowin/fastmcp)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [실험 보고서](./docs/fastMCP_실험_보고서.md)

## 라이선스

이 프로젝트는 개인 학습 및 실험 목적으로 만들어졌습니다.

---

**작성자**: 윤현철  
**작성일**: 2025년 8월 5일  
**버전**: 1.0.0
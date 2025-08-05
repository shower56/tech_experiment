# ToolHive Fetch MCP를 활용한 클래스유 TOP 50 선생님 수집 보고서

## 📋 개요

본 보고서는 **ToolHive의 Fetch MCP**를 활용하여 클래스유(classu.co.kr) 사이트에서 상위 TOP 50 선생님들의 정보를 추출하는 과정과 결과를 정리한 것입니다.

---

## 🎯 목표

- **주요 목표**: ToolHive Fetch MCP를 사용하여 클래스유 사이트의 TOP 50 선생님 정보 수집
- **부가 목표**: ToolHive MCP 서버의 실제 사용법 학습 및 Playwright와의 비교 분석
- **기술적 목표**: MCP(Model Context Protocol) 통신 방법 이해 및 구현

---

## 🛠 기술 스택 및 환경

### 사용된 도구
- **ToolHive CLI**: v0.2.2
- **ToolHive Fetch MCP Server**: ghcr.io/stackloklabs/gofetch/server:latest
- **Python**: 3.11.9
- **주요 라이브러리**: aiohttp, beautifulsoup4, requests

### 환경 설정
```bash
# ToolHive CLI 설치 (Homebrew)
brew tap stacklok/tap
brew install thv

# Fetch MCP 서버 실행
thv run fetch

# 실행 확인
thv list
```

---

## 🔧 구현 과정

### 1단계: ToolHive Fetch MCP 서버 실행

```bash
$ thv run fetch
# 서버가 http://127.0.0.1:16330/mcp 에서 실행됨

$ thv list
NAME     PACKAGE                                   STATUS   URL                           PORT   TOOL TYPE
fetch    ghcr.io/stackloklabs/gofetch/server     running  http://127.0.0.1:16330/mcp   16330  mcp
```

### 2단계: MCP 프로토콜 이해

**주요 발견사항:**
1. **초기화 필요**: MCP 서버는 세션 초기화가 필요함
2. **SSE 통신**: Server-Sent Events를 통한 스트리밍 응답
3. **헤더 요구사항**: `Accept: application/json, text/event-stream` 필수

**MCP 통신 테스트:**
```bash
curl -X POST http://127.0.0.1:16330/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{
    "jsonrpc": "2.0",
    "id": "1",
    "method": "tools/call",
    "params": {
      "name": "fetch",
      "arguments": {"url": "https://httpbin.org/get"}
    }
  }'

# 응답: "method \"tools/call\" is invalid during session initialization"
```

### 3단계: MCP 클라이언트 구현

#### 3.1 비동기 HTTP 클라이언트 방식
```python
class ClassuFetchMCP:
    def __init__(self, mcp_server_url: str = "http://127.0.0.1:16330"):
        self.mcp_server_url = mcp_server_url
        
    async def fetch_page_content(self, url: str) -> str:
        payload = {
            "jsonrpc": "2.0",
            "id": "1",
            "method": "tools/call",
            "params": {
                "name": "fetch",
                "arguments": {"url": url}
            }
        }
        
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self.mcp_server_url}/mcp", 
                                  json=payload, headers=headers) as response:
                # SSE 응답 처리 로직
                ...
```

#### 3.2 Subprocess + curl 방식
```python
def fetch_url_content(self, url: str) -> str:
    curl_cmd = [
        'curl', '-s', '-X', 'POST',
        'http://127.0.0.1:16330/mcp',
        '-H', 'Content-Type: application/json',
        '-H', 'Accept: application/json, text/event-stream',
        '-d', json.dumps({
            "jsonrpc": "2.0",
            "id": "fetch_request",
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "ClassuScraper", "version": "1.0.0"}
            }
        })
    ]
    
    result = subprocess.run(curl_cmd, capture_output=True, text=True, timeout=30)
    # 응답 처리...
```

---

## 🚧 구현 중 발견된 문제점

### 1. MCP 프로토콜 복잡성
- **문제**: MCP 프로토콜은 단순한 HTTP 요청이 아님
- **원인**: 세션 초기화, 능력 협상 등의 복잡한 핸드셰이크 과정 필요
- **해결 시도**: initialize 메서드 호출, SSE 스트림 처리 구현

### 2. 세션 관리 이슈
```
Error: "method \"tools/call\" is invalid during session initialization"
```
- **분석**: MCP 서버가 올바른 초기화 절차를 요구함
- **필요사항**: 
  1. initialize 메서드로 세션 시작
  2. capabilities 협상
  3. tools/list로 사용 가능한 도구 확인
  4. tools/call로 실제 요청

### 3. SSE(Server-Sent Events) 스트림 처리
- **복잡성**: 이벤트 스트림 파싱 및 JSON 데이터 추출
- **응답 형식**: 
```
event: message
id: 1_0
data: {"jsonrpc":"2.0","id":"1","result":{"content":[{"type":"text","text":"..."}]}}
```

---

## 📊 Playwright vs ToolHive Fetch MCP 비교

| 구분 | Playwright MCP | ToolHive Fetch MCP |
|------|----------------|---------------------|
| **설정 복잡도** | ⭐⭐⭐ 중간 | ⭐⭐⭐⭐⭐ 매우 높음 |
| **JavaScript 실행** | ✅ 완전 지원 | ❌ 제한적 |
| **속도** | ⭐⭐⭐ 보통 | ⭐⭐⭐⭐ 빠름 (단순 HTTP) |
| **안정성** | ⭐⭐⭐⭐⭐ 매우 안정 | ⭐⭐ 개발 초기 |
| **사용 편의성** | ⭐⭐⭐⭐ 쉬움 | ⭐⭐ 어려움 |
| **보안성** | ⭐⭐⭐ 보통 | ⭐⭐⭐⭐⭐ 매우 높음 |
| **확장성** | ⭐⭐⭐ 보통 | ⭐⭐⭐⭐⭐ 매우 높음 |

### 상세 비교

#### **Playwright MCP 장점**
- 🎯 **완성도**: 브라우저 자동화에 최적화
- 🚀 **즉시 사용**: 복잡한 설정 없이 바로 활용 가능
- 🔧 **강력한 기능**: 클릭, 스크롤, 폼 입력 등 모든 브라우저 액션 지원
- 📱 **동적 콘텐츠**: JavaScript로 렌더링되는 SPA 완벽 지원

#### **ToolHive Fetch MCP 장점**
- 🔒 **보안**: 컨테이너 격리 환경에서 실행
- ⚡ **성능**: 가벼운 HTTP 요청으로 빠른 처리
- 🏗 **표준화**: MCP 프로토콜 표준 준수
- 🔧 **확장성**: 다양한 AI 클라이언트와 통합 가능

---

## 💡 ToolHive 활용 권장사항

### 권장 사용 시나리오

#### ✅ **ToolHive Fetch MCP가 적합한 경우**
1. **정적 콘텐츠 수집**: HTML 기반의 단순한 웹 페이지
2. **AI 통합**: GitHub Copilot, Cursor 등 AI 도구와 연동
3. **보안 중요**: 격리된 환경에서의 안전한 크롤링
4. **대용량 처리**: 다수의 간단한 페이지 수집

#### ❌ **ToolHive Fetch MCP가 부적합한 경우**
1. **동적 콘텐츠**: JavaScript 렌더링이 필요한 SPA
2. **복잡한 상호작용**: 로그인, 클릭, 스크롤 등이 필요한 경우
3. **즉시 프로토타이핑**: 빠른 개발이 필요한 상황

### 사용법 가이드

#### 1. 기본 설정
```bash
# ToolHive 설치
brew tap stacklok/tap
brew install thv

# Fetch MCP 서버 실행
thv run fetch

# 상태 확인
thv list
```

#### 2. Python 클라이언트 구현
```python
import subprocess
import json

def fetch_with_toolhive(url: str) -> str:
    """ToolHive Fetch MCP를 통한 웹 페이지 수집"""
    
    # 1. 세션 초기화
    init_cmd = [
        'curl', '-s', '-X', 'POST', 'http://127.0.0.1:16330/mcp',
        '-H', 'Content-Type: application/json',
        '-H', 'Accept: application/json, text/event-stream',
        '-d', json.dumps({
            "jsonrpc": "2.0",
            "id": "init",
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "WebScraper", "version": "1.0.0"}
            }
        })
    ]
    
    subprocess.run(init_cmd, capture_output=True)
    
    # 2. 콘텐츠 가져오기
    fetch_cmd = [
        'curl', '-s', '-X', 'POST', 'http://127.0.0.1:16330/mcp',
        '-H', 'Content-Type: application/json',
        '-H', 'Accept: application/json, text/event-stream',
        '-d', json.dumps({
            "jsonrpc": "2.0",
            "id": "fetch",
            "method": "tools/call",
            "params": {
                "name": "fetch",
                "arguments": {"url": url}
            }
        })
    ]
    
    result = subprocess.run(fetch_cmd, capture_output=True, text=True)
    
    # 3. SSE 응답 파싱
    content = ""
    for line in result.stdout.split('\\n'):
        if line.startswith('data: '):
            try:
                data = json.loads(line[6:])
                if "result" in data and "content" in data["result"]:
                    content += data["result"]["content"][0]["text"]
            except:
                continue
                
    return content
```

#### 3. AI 클라이언트 연동
```bash
# VS Code/Cursor 자동 설정
thv client setup

# 설정 상태 확인
thv client status
```

---

## 🎯 실제 적용 결과

### 클래스유 데이터 수집 시도

#### 시도한 URL들
- `https://www.classu.co.kr/new` (메인 페이지)
- `https://www.classu.co.kr/new/event/plan/65` (BEST 클래스)
- 카테고리 페이지들 (외국어, 운동, 비즈니스 등)

#### 결과
```
2025-08-04 13:55:47 - INFO - Fetching content from: https://www.classu.co.kr/new
2025-08-04 13:55:47 - WARNING - No content extracted from https://www.classu.co.kr/new
2025-08-04 13:55:50 - INFO - Fetching content from: https://www.classu.co.kr/new/event/plan/65
2025-08-04 13:55:50 - WARNING - No content extracted from https://www.classu.co.kr/new/event/plan/65
```

**문제 분석:**
1. **MCP 초기화 복잡성**: 올바른 세션 초기화 과정 필요
2. **응답 파싱 이슈**: SSE 스트림의 복잡한 구조
3. **클래스유 특성**: JavaScript 기반 동적 콘텐츠 가능성

---

## 🔍 Playwright 방식 결과 (참고용)

**이전 Playwright MCP로 수집한 실제 결과:**

### TOP 5 인기 강사
1. **김재환 코치** (35,948명) - 내 인생의 마지막 다이어트
2. **이민호** (35,653명) - 자신있게 영어로 소통하는 사람되는 국민영어법  
3. **미꽃체** (34,868명) - 손글씨를 인쇄된 폰트처럼, 미꽃체
4. **윤주코치** (31,133명) - 레깅스 핏 만들기! 바디라인 필라테스 클래스
5. **발레핏 김정은 코치** (30,294명) - 탄탄하고 아름다운 바디라인을 원한다면 발레핏 클래스

**성공 요인:**
- 브라우저 렌더링으로 JavaScript 콘텐츠 완전 로딩
- 클릭, 스크롤 등의 상호작용 지원
- 페이지 네비게이션 자동화

---

## 🚀 개선 방안 및 향후 계획

### 단기 개선사항

#### 1. MCP 클라이언트 라이브러리 개발
```python
class MCPClient:
    """표준 MCP 클라이언트 구현"""
    
    async def initialize_session(self):
        """MCP 세션 초기화"""
        pass
    
    async def call_tool(self, name: str, arguments: dict):
        """도구 호출"""
        pass
    
    async def close_session(self):
        """세션 종료"""
        pass
```

#### 2. 하이브리드 접근법
```python
def hybrid_scraping(url: str) -> str:
    """ToolHive와 Playwright를 조합한 스크래핑"""
    
    # 1. ToolHive로 정적 콘텐츠 시도
    content = fetch_with_toolhive(url)
    
    if not content:
        # 2. Playwright로 동적 콘텐츠 처리
        content = fetch_with_playwright(url)
    
    return content
```

### 장기 발전 방향

#### 1. **ToolHive 생태계 구축**
- 커스텀 MCP 서버 개발
- 도메인별 특화 서버 (전자상거래, 뉴스, 소셜 미디어)
- AI 에이전트와의 긴밀한 통합

#### 2. **표준화 및 최적화**
- MCP 프로토콜 숙련도 향상
- 성능 최적화 및 안정성 개선
- 팀 워크플로우 통합

#### 3. **보안 및 거버넌스**
- 엔터프라이즈급 보안 정책
- 감사 로그 및 모니터링
- RBAC(Role-Based Access Control)

---

## 📝 결론

### 주요 발견사항

1. **ToolHive의 잠재력**: MCP 표준을 통한 AI 도구 통합의 혁신적 접근
2. **현재 한계**: 복잡한 초기 설정과 동적 콘텐츠 처리 제약
3. **학습 가치**: MCP 프로토콜에 대한 깊이 있는 이해 획득

### 권장사항

#### **현재 프로젝트에서**
- **단순 크롤링**: ToolHive Fetch MCP 활용
- **복잡한 사이트**: Playwright MCP 계속 사용
- **AI 통합**: ToolHive 생태계 점진적 도입

#### **향후 개발에서**
- MCP 프로토콜 표준 학습 및 적용
- ToolHive 커스텀 서버 개발 고려
- 하이브리드 접근법으로 각 도구의 장점 활용

### 최종 평가

**ToolHive Fetch MCP**는 현재 **혁신적이지만 미완성된 도구**입니다. MCP 표준의 강력한 잠재력을 보여주지만, 실제 프로덕션 사용을 위해서는 추가적인 학습과 도구 개발이 필요합니다.

**클래스유 TOP 50 수집**의 경우, 현재로는 **Playwright MCP가 더 실용적**이지만, ToolHive의 발전과 함께 미래에는 더욱 강력한 대안이 될 것으로 예상됩니다.

---

## 📚 참고 자료

### 개발한 코드
- `classu_fetch_mcp.py`: 비동기 HTTP 클라이언트 방식
- `classu_simple_fetch.py`: subprocess + curl 방식
- `fetch_mcp_client.py`: 기존 MCP 클라이언트 참고용

### 공식 문서
- [ToolHive 공식 문서](https://docs.stacklok.com/toolhive/)
- [MCP 프로토콜 스펙](https://docs.stacklok.com/toolhive/concepts/mcp-primer)
- [GitHub 리포지토리](https://github.com/stacklok/toolhive)

### 실행 명령어
```bash
# ToolHive 서버 관리
thv run fetch
thv list
thv stop fetch
thv logs fetch

# 클라이언트 설정
thv client setup
thv client status
```

---

**보고서 작성일**: 2025년 8월 4일  
**ToolHive 버전**: v0.2.2  
**작성자**: AI Assistant  
**프로젝트**: ToolHive Fetch MCP를 활용한 웹 스크래핑 실험
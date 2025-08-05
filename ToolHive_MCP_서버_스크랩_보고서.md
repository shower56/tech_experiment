# ToolHive MCP 서버 스크랩 보고서

## 📋 수집 개요
- **수집 일시**: 2025년 1월 27일
- **수집 사이트**: https://metashower.tistory.com/entry/Toolhive-MCP-Servers
- **수집 방법**: fetch MCP를 활용한 웹 스크래핑

## 🏗️ ToolHive 개요

### ToolHive란?
**ToolHive**는 Model Context Protocol (MCP) 서버의 배포와 관리를 단순화하는 플랫폼입니다. MCP 서버를 안전하고 일관성 있게 실행할 수 있도록 최소한의 권한으로 컨테이너 환경에서 동작하게 해줍니다.

### 핵심 가치
- **보안성**: 모든 MCP 서버가 격리된 컨테이너 환경에서 실행
- **편의성**: 원클릭 또는 단일 명령어로 MCP 서버 배포
- **확장성**: 로컬 개발부터 엔터프라이즈 환경까지 지원
- **호환성**: GitHub Copilot, Cursor 등 주요 AI 클라이언트와 자동 연동

## 🎯 지원 모드

ToolHive는 다양한 사용 환경에 맞춰 세 가지 모드로 제공됩니다:

### 1. ToolHive UI (Desktop App)
- **대상**: 개인 개발자
- **특징**: 직관적인 GUI 인터페이스
- **용도**: 로컬 환경에서 MCP 서버 관리

### 2. ToolHive CLI
- **대상**: 개발자, DevOps 엔지니어
- **특징**: 명령줄 인터페이스
- **용도**: 개발 환경, 자동화 스크립트

### 3. ToolHive Kubernetes Operator
- **대상**: 팀, 엔터프라이즈
- **특징**: 쿠버네티스 네이티브
- **용도**: 프로덕션 환경, 다중 사용자 지원

## 🏛️ 아키텍처

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   AI Client     │    │  ToolHive Proxy │    │  MCP Server     │
│ (Copilot/Cursor)│◄──►│     (HTTP)      │◄──►│  (Container)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### 주요 구성 요소
- **HTTP Proxy**: AI 클라이언트와 MCP 서버 간 통신 중계
- **Container Runtime**: Docker/Podman을 통한 MCP 서버 실행
- **Registry**: 검증된 MCP 서버 목록 관리

## ⚡ 핵심 기능

### 🚀 즉시 배포
```bash
# 단 하나의 명령어로 MCP 서버 실행
thv run fetch
```

### 🔒 기본 보안
- 컨테이너 격리 환경
- 최소 권한 원칙
- 암호화된 시크릿 관리

### 🔗 자동 연동
- GitHub Copilot, Cursor 자동 설정
- 수동 설정 없이 즉시 사용 가능

### 🛠 프로토콜 지원
- stdio (표준 입출력)
- SSE (Server-Sent Events)
- streamable-http (스트리밍 HTTP)

## 💻 설치 및 환경 구성

### 사전 요구사항
- **Docker** 또는 **Podman** 설치 및 실행 중
- **지원 OS**: macOS, Windows, Linux
- **지원 AI 클라이언트**: VS Code (GitHub Copilot), Cursor, Claude Code

### ToolHive CLI 설치

#### Homebrew (macOS/Linux)
```bash
brew tap stacklok/tap
brew install thv
```

#### WinGet (Windows)
```bash
winget install stacklok.toolhive
```

#### 설치 확인
```bash
thv version
# 출력 예시:
# ToolHive v0.1.1
# Commit: 18956ca1710e11c9952d13a8dde039d5d1d147d6
# Built: 2025-06-30 13:59:34 UTC
```

## 🚀 사용법

### CLI 기본 명령어
```bash
# 버전 확인
thv version

# 레지스트리 목록 조회
thv registry list

# MCP 서버 실행
thv run fetch

# 실행 중인 서버 목록
thv list

# 서버 중지
thv stop fetch

# 서버 완전 삭제
thv rm fetch
```

### 클라이언트 설정
```bash
# 클라이언트 자동 감지 및 설정
thv client setup

# 클라이언트 상태 확인
thv client status
```

## 🔧 고급 기능

### 권한 프로필
```bash
# 네트워크 접근 허용
thv run --permission-profile network fetch

# 파일시스템 접근 허용
thv run --permission-profile filesystem file-processor

# 제한된 권한 (기본값)
thv run --permission-profile restricted minimal-server
```

### 시크릿 관리
```bash
# 시크릿 설정
thv secret set API_KEY your_secret_value

# 시크릿 목록
thv secret list

# 서버 실행 시 시크릿 사용
thv run --env API_KEY=@secret:API_KEY my-server
```

### 네트워크 설정
```bash
# 특정 포트로 실행
thv run --port 9000 --target-port 8080 my-server

# 자동 포트 할당
thv run --port 0 my-server
```

## 🛠️ 나만의 MCP 서버 구축

### Python MCP 서버 예시
```python
from mcp.server import Server
from mcp.types import Tool, TextContent

app = Server("my-custom-server")

@app.list_tools()
async def list_tools():
    return [
        Tool(
            name="get_weather",
            description="Get current weather for a location",
            inputSchema={
                "type": "object",
                "properties": {
                    "location": {"type": "string"}
                },
                "required": ["location"]
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "get_weather":
        location = arguments["location"]
        weather_data = get_weather_data(location)
        return TextContent(
            type="text",
            text=f"Weather in {location}: {weather_data}"
        )

if __name__ == "__main__":
    app.run()
```

### Dockerfile 예시
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# 의존성 설치
COPY requirements.txt .
RUN pip install -r requirements.txt

# 소스 코드 복사
COPY . .

# 비루트 사용자 생성
RUN adduser --disabled-password --gecos '' appuser
USER appuser

# MCP 서버 실행
EXPOSE 8080
CMD ["python", "server.py"]
```

## 📊 실제 사용 예시

### 웹 콘텐츠 크롤링 (Fetch 서버)
```bash
# Fetch 서버 실행
thv run fetch

# AI 클라이언트에서 사용
# "https://example.com 사이트의 내용을 가져와서 요약해줘"
```

### GitHub 통합
```bash
# GitHub 토큰 설정
thv secret set GITHUB_TOKEN ghp_your_token_here

# GitHub 서버 실행
thv run github

# AI에서 사용
# "내 GitHub 리포지토리 목록을 보여줘"
```

## 🔍 문제 해결

### 일반적인 문제
```bash
# Docker 데몬 상태 확인
docker info

# ToolHive 상태 진단
thv doctor

# 포트 충돌 해결
thv run --port 8081 my-server
```

### 성능 최적화
```bash
# CPU 및 메모리 제한
thv run --cpu-limit 0.5 --memory-limit 512MB my-server
```

## 💡 사용 시나리오별 권장사항

### 개인 개발자
- **ToolHive UI** 사용 권장
- 로컬 개발 환경에서 빠른 프로토타이핑
- 다양한 MCP 서버 실험 가능

### 팀 개발
- **ToolHive CLI** + 스크립트 자동화
- CI/CD 파이프라인 통합
- 개발/스테이징 환경 관리

### 엔터프라이즈
- **Kubernetes Operator** 사용
- 중앙 집중식 관리
- RBAC, 네트워크 정책 적용
- 모니터링 및 감사 로그

## 🎯 주요 특징 및 장점

### ToolHive의 장점
1. **보안 우선**: 기본적으로 안전한 컨테이너 환경
2. **사용 편의성**: 원클릭/단일 명령어 배포
3. **확장성**: 개발부터 프로덕션까지 일관된 경험
4. **생태계**: 검증된 MCP 서버 레지스트리
5. **표준화**: MCP 프로토콜 준수로 호환성 보장

### 개발 모범 사례
1. **시작은 간단하게**: 기존 레지스트리 서버부터 시작
2. **점진적 확장**: 기본 기능 확인 후 고급 기능 추가
3. **보안 고려**: 최소 권한 원칙 적용
4. **문서화**: MCP 서버 기능과 사용법 명확히 기술
5. **테스트**: 다양한 AI 클라이언트에서 동작 확인

## 🔮 미래 발전 방향

ToolHive는 지속적으로 발전하고 있으며, 다음과 같은 영역에서 개선이 예상됩니다:

- **더 많은 AI 클라이언트 지원**
- **고급 보안 기능** (Zero Trust, OIDC 등)
- **성능 최적화** 도구
- **개발자 도구** 개선
- **클라우드 네이티브** 기능 강화

## 📚 참고 자료

- **원문 링크**: [ToolHive MCP Servers](https://metashower.tistory.com/entry/Toolhive-MCP-Servers)
- **공식 문서**: [ToolHive Documentation](https://docs.stacklok.com/toolhive/)
- **GitHub 저장소**: [ToolHive GitHub](https://github.com/stacklok/toolhive)

---

*본 보고서는 fetch MCP를 활용하여 2025년 1월 27일에 수집된 데이터를 기반으로 작성되었습니다.*
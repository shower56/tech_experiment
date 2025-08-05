# ToolHive 종합 사용 가이드 보고서

## 목차
1. [ToolHive 개요](#1-toolhive-개요)
2. [ToolHive 아키텍처 및 주요 기능](#2-toolhive-아키텍처-및-주요-기능)
3. [ToolHive 설치 및 환경 구성](#3-toolhive-설치-및-환경-구성)
4. [ToolHive 사용법](#4-toolhive-사용법)
5. [나만의 MCP 서버 구축 방법](#5-나만의-mcp-서버-구축-방법)
6. [실제 사용 예시](#6-실제-사용-예시)
7. [고급 기능 및 설정](#7-고급-기능-및-설정)
8. [문제 해결 및 팁](#8-문제-해결-및-팁)
9. [결론 및 권장사항](#9-결론-및-권장사항)

---

## 1. ToolHive 개요

### 1.1 ToolHive란?

**ToolHive**는 [Model Context Protocol (MCP)](https://docs.stacklok.com/toolhive/concepts/mcp-primer) 서버의 배포와 관리를 단순화하는 플랫폼입니다. MCP 서버를 안전하고 일관성 있게 실행할 수 있도록 최소한의 권한으로 컨테이너 환경에서 동작하게 해줍니다.

### 1.2 핵심 가치

- **보안성**: 모든 MCP 서버가 격리된 컨테이너 환경에서 실행
- **편의성**: 원클릭 또는 단일 명령어로 MCP 서버 배포
- **확장성**: 로컬 개발부터 엔터프라이즈 환경까지 지원
- **호환성**: GitHub Copilot, Cursor 등 주요 AI 클라이언트와 자동 연동

### 1.3 지원 모드

ToolHive는 다양한 사용 환경에 맞춰 세 가지 모드로 제공됩니다:

#### **ToolHive UI (Desktop App)**
- **대상**: 개인 개발자
- **특징**: 직관적인 GUI 인터페이스
- **용도**: 로컬 환경에서 MCP 서버 관리

#### **ToolHive CLI**
- **대상**: 개발자, DevOps 엔지니어
- **특징**: 명령줄 인터페이스
- **용도**: 개발 환경, 자동화 스크립트

#### **ToolHive Kubernetes Operator**
- **대상**: 팀, 엔터프라이즈
- **특징**: 쿠버네티스 네이티브
- **용도**: 프로덕션 환경, 다중 사용자 지원

---

## 2. ToolHive 아키텍처 및 주요 기능

### 2.1 아키텍처 개요

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   AI Client     │    │  ToolHive Proxy │    │  MCP Server     │
│ (Copilot/Cursor)│◄──►│     (HTTP)      │◄──►│  (Container)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

**주요 구성 요소:**
- **HTTP Proxy**: AI 클라이언트와 MCP 서버 간 통신 중계
- **Container Runtime**: Docker/Podman을 통한 MCP 서버 실행
- **Registry**: 검증된 MCP 서버 목록 관리

### 2.2 핵심 기능

#### **🚀 즉시 배포**
```bash
# 단 하나의 명령어로 MCP 서버 실행
thv run fetch
```

#### **🔒 기본 보안**
- 컨테이너 격리 환경
- 최소 권한 원칙
- 암호화된 시크릿 관리

#### **🔗 자동 연동**
- GitHub Copilot, Cursor 자동 설정
- 수동 설정 없이 즉시 사용 가능

#### **🛠 프로토콜 지원**
- `stdio` (표준 입출력)
- `SSE` (Server-Sent Events)
- `streamable-http` (스트리밍 HTTP)

---

## 3. ToolHive 설치 및 환경 구성

### 3.1 사전 요구사항

#### **시스템 요구사항**
- **Docker** 또는 **Podman** 설치 및 실행 중
- **지원 OS**: macOS, Windows, Linux
- **지원 AI 클라이언트**: VS Code (GitHub Copilot), Cursor, Claude Code

#### **필수 소프트웨어 설치**

**Docker 설치:**
```bash
# macOS (Homebrew)
brew install --cask docker

# Windows (Chocolatey)
choco install docker-desktop

# Linux (Ubuntu)
sudo apt-get update
sudo apt-get install docker.io
```

### 3.2 ToolHive UI 설치

#### **macOS**
```bash
# Apple Silicon Mac
curl -LO https://github.com/stacklok/toolhive-studio/releases/latest/download/ToolHive-arm64.dmg

# Intel Mac
curl -LO https://github.com/stacklok/toolhive-studio/releases/latest/download/ToolHive-x64.dmg
```

#### **Windows**
```bash
# 설치 프로그램 다운로드 및 실행
curl -LO https://github.com/stacklok/toolhive-studio/releases/latest/download/ToolHive.Setup.exe
```

#### **Linux**
```bash
# 최신 릴리스 페이지에서 RPM 또는 DEB 패키지 다운로드
# https://github.com/stacklok/toolhive-studio/releases/latest
```

### 3.3 ToolHive CLI 설치

#### **Homebrew (macOS/Linux)**
```bash
brew tap stacklok/tap
brew install thv
```

#### **WinGet (Windows)**
```bash
winget install stacklok.toolhive
```

#### **수동 설치**
```bash
# 바이너리 다운로드 후 PATH에 추가
# https://github.com/stacklok/toolhive/releases/latest
```

#### **설치 확인**
```bash
thv version
# 출력 예시:
# ToolHive v0.1.1
# Commit: 18956ca1710e11c9952d13a8dde039d5d1d147d6
# Built: 2025-06-30 13:59:34 UTC
```

---

## 4. ToolHive 사용법

### 4.1 ToolHive UI 사용법

#### **4.1.1 첫 번째 실행**

1. **앱 실행**: ToolHive 데스크톱 앱 시작
2. **레지스트리 탐색**: "Browse Registry" 클릭
3. **서버 선택**: 원하는 MCP 서버 선택 (예: fetch)
4. **설치**: "Install server" 버튼 클릭

#### **4.1.2 클라이언트 연결**

1. **Clients 페이지**: 상단 메뉴에서 "Clients" 선택
2. **클라이언트 활성화**: 사용할 AI 클라이언트 토글 스위치 ON
3. **자동 구성**: ToolHive가 자동으로 클라이언트 설정

#### **4.1.3 서버 관리**

- **서버 목록**: "MCP Servers" 페이지에서 실행 중인 서버 확인
- **서버 중지**: 서버 카드에서 정지 버튼 클릭
- **로그 확인**: 서버 상세 페이지에서 실행 로그 조회

### 4.2 ToolHive CLI 사용법

#### **4.2.1 기본 명령어**

```bash
# 버전 확인
thv version

# 도움말
thv help

# 레지스트리 목록 조회
thv registry list

# 특정 서버 정보 조회
thv registry info fetch

# MCP 서버 실행
thv run fetch

# 실행 중인 서버 목록
thv list

# 서버 중지
thv stop fetch

# 서버 완전 삭제
thv rm fetch
```

#### **4.2.2 클라이언트 설정**

```bash
# 클라이언트 자동 감지 및 설정
thv client setup

# 클라이언트 상태 확인
thv client status

# 출력 예시:
# ┌────────────────┬───────────┬────────────┐
# │ CLIENT TYPE    │ INSTALLED │ REGISTERED │
# ├────────────────┼───────────┼────────────┤
# │ vscode         │ ✅ Yes    │ ✅ Yes     │
# │ cursor         │ ✅ Yes    │ ❌ No      │
# └────────────────┴───────────┴────────────┘
```

#### **4.2.3 고급 옵션**

```bash
# 사용자 정의 이미지로 실행
thv run --image custom/mcp-server:latest myserver

# 환경 변수 전달
thv run --env API_KEY=secret fetch

# 포트 지정
thv run --port 9000 fetch

# 권한 프로필 지정
thv run --permission-profile network fetch
```

### 4.3 Kubernetes Operator 사용법

#### **4.3.1 Operator 설치**

```bash
# Helm으로 설치
helm repo add stacklok https://stacklok.github.io/toolhive
helm install toolhive-operator stacklok/toolhive-operator \
  --namespace toolhive-system \
  --create-namespace
```

#### **4.3.2 MCPServer 리소스 생성**

```yaml
# mcpserver-example.yaml
apiVersion: toolhive.stacklok.dev/v1alpha1
kind: MCPServer
metadata:
  name: fetch
  namespace: toolhive-system
spec:
  image: ghcr.io/stackloklabs/gofetch/server
  transport: streamable-http
  port: 8080
  targetPort: 8080
  permissionProfile:
    type: builtin
    name: network
  resources:
    limits:
      cpu: "100m"
      memory: "128Mi"
    requests:
      cpu: "50m"
      memory: "64Mi"
```

```bash
# 리소스 적용
kubectl apply -f mcpserver-example.yaml

# 상태 확인
kubectl get mcpserver -n toolhive-system

# 로그 확인
kubectl logs -l app=fetch -n toolhive-system
```

---

## 5. 나만의 MCP 서버 구축 방법

### 5.1 MCP 서버 개발 기초

#### **5.1.1 MCP 프로토콜 이해**

MCP(Model Context Protocol)는 AI 에이전트와 도구 간의 표준화된 통신 프로토콜입니다.

**주요 구성 요소:**
- **Tools**: AI가 호출할 수 있는 함수
- **Resources**: AI가 접근할 수 있는 데이터
- **Prompts**: AI에게 제공할 수 있는 템플릿

#### **5.1.2 기본 MCP 서버 구조**

```python
# Python MCP 서버 예시
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
        # 실제 날씨 API 호출 로직
        weather_data = get_weather_data(location)
        return TextContent(
            type="text",
            text=f"Weather in {location}: {weather_data}"
        )

if __name__ == "__main__":
    app.run()
```

### 5.2 컨테이너화

#### **5.2.1 Dockerfile 작성**

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

#### **5.2.2 이미지 빌드 및 푸시**

```bash
# 이미지 빌드
docker build -t myregistry/my-mcp-server:v1.0.0 .

# 이미지 푸시
docker push myregistry/my-mcp-server:v1.0.0
```

### 5.3 ToolHive와 통합

#### **5.3.1 로컬 테스트**

```bash
# 로컬 이미지로 테스트
thv run --image myregistry/my-mcp-server:v1.0.0 my-server

# 로그 확인
thv logs my-server

# 테스트
thv list
```

#### **5.3.2 Kubernetes 배포**

```yaml
# my-mcpserver.yaml
apiVersion: toolhive.stacklok.dev/v1alpha1
kind: MCPServer
metadata:
  name: my-server
  namespace: toolhive-system
spec:
  image: myregistry/my-mcp-server:v1.0.0
  transport: streamable-http
  port: 8080
  targetPort: 8080
  env:
    - name: API_KEY
      valueFrom:
        secretKeyRef:
          name: my-server-secrets
          key: api-key
  permissionProfile:
    type: builtin
    name: network
```

---

## 6. 실제 사용 예시

### 6.1 웹 콘텐츠 크롤링 서버 (Fetch)

#### **6.1.1 서버 실행**

```bash
# CLI로 Fetch 서버 실행
thv run fetch

# 실행 확인
thv list
# 출력:
# NAME   PACKAGE                                  STATUS   URL                              PORT   TOOL TYPE
# fetch  ghcr.io/stackloklabs/gofetch/server     running  http://127.0.0.1:15266/sse#fetch 15266  mcp
```

#### **6.1.2 AI 클라이언트에서 사용**

**VS Code (GitHub Copilot)에서:**
```
사용자: "https://toolhive.dev 사이트의 내용을 가져와서 요약해줘"

AI 응답: fetch 도구를 사용해서 웹사이트 내용을 가져오겠습니다.

[fetch 도구 실행]
- URL: https://toolhive.dev
- 응답: 웹사이트 HTML 내용

요약: ToolHive는 MCP 서버 배포를 간소화하는 플랫폼으로...
```

### 6.2 GitHub 통합 서버

#### **6.2.1 시크릿 설정**

```bash
# GitHub 토큰 설정
thv secret set GITHUB_TOKEN ghp_your_token_here

# GitHub 서버 실행 (토큰 필요)
thv run github
```

#### **6.2.2 사용 예시**

```
사용자: "내 GitHub 리포지토리 목록을 보여줘"

AI: GitHub API를 통해 리포지토리를 조회하겠습니다.

결과:
1. user/project1 - 주요 프로젝트
2. user/project2 - 실험 프로젝트
3. user/toolhive-examples - ToolHive 예시
```

### 6.3 데이터베이스 조회 서버

#### **6.3.1 커스텀 서버 구현**

```python
# database_mcp_server.py
import asyncio
import sqlite3
from mcp.server import Server
from mcp.types import Tool, TextContent

app = Server("database-query")

@app.list_tools()
async def list_tools():
    return [
        Tool(
            name="query_database",
            description="Execute SQL query on database",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "SQL query"},
                    "params": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["query"]
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "query_database":
        conn = sqlite3.connect('data.db')
        cursor = conn.cursor()
        
        query = arguments["query"]
        params = arguments.get("params", [])
        
        try:
            cursor.execute(query, params)
            results = cursor.fetchall()
            return TextContent(
                type="text",
                text=f"Query results: {results}"
            )
        finally:
            conn.close()

if __name__ == "__main__":
    app.run_sse(port=8080)
```

#### **6.3.2 배포 및 사용**

```bash
# 컨테이너화
docker build -t my-db-server .

# ToolHive로 실행
thv run --image my-db-server database-query

# AI에서 사용
# "사용자 테이블에서 최근 가입한 10명을 조회해줘"
```

---

## 7. 고급 기능 및 설정

### 7.1 권한 프로필 (Permission Profiles)

#### **7.1.1 내장 프로필**

```bash
# 네트워크 접근 허용
thv run --permission-profile network fetch

# 파일시스템 접근 허용  
thv run --permission-profile filesystem file-processor

# 제한된 권한 (기본값)
thv run --permission-profile restricted minimal-server
```

#### **7.1.2 커스텀 권한 프로필**

```json
{
  "version": "1",
  "name": "custom-profile",
  "capabilities": {
    "network": {
      "allowOutbound": true,
      "allowedHosts": ["api.example.com", "*.trusted-domain.com"]
    },
    "filesystem": {
      "allowRead": ["/tmp", "/data"],
      "allowWrite": ["/tmp"]
    },
    "environment": {
      "allowedVars": ["API_KEY", "CONFIG_PATH"]
    }
  }
}
```

### 7.2 시크릿 관리

#### **7.2.1 내장 시크릿 저장소**

```bash
# 시크릿 설정
thv secret set API_KEY your_secret_value

# 시크릿 목록
thv secret list

# 시크릿 삭제
thv secret delete API_KEY

# 서버 실행 시 시크릿 사용
thv run --env API_KEY=@secret:API_KEY my-server
```

#### **7.2.2 1Password 통합**

```bash
# 1Password CLI 설치 및 설정 후
thv config set secrets-provider 1password

# 1Password에서 시크릿 참조
thv run --env API_KEY=@1password:vault/item/field my-server
```

### 7.3 네트워크 설정

#### **7.3.1 포트 매핑**

```bash
# 특정 포트로 실행
thv run --port 9000 --target-port 8080 my-server

# 여러 포트 노출
thv run --port 9000,9001 --target-port 8080,8081 multi-port-server
```

#### **7.3.2 네트워크 정책**

```yaml
# Kubernetes에서 네트워크 정책 적용
apiVersion: toolhive.stacklok.dev/v1alpha1
kind: MCPServer
metadata:
  name: restricted-server
spec:
  image: my-server:latest
  networkPolicy:
    egress:
      - to:
        - namespaceSelector:
            matchLabels:
              name: allowed-namespace
        ports:
        - protocol: TCP
          port: 443
```

### 7.4 모니터링 및 로깅

#### **7.4.1 로그 관리**

```bash
# 실시간 로그 스트림
thv logs --follow my-server

# 특정 기간 로그
thv logs --since 1h my-server

# 로그 레벨 설정
thv run --log-level debug my-server
```

#### **7.4.2 메트릭 수집**

```yaml
# Prometheus 메트릭 활성화
apiVersion: toolhive.stacklok.dev/v1alpha1
kind: MCPServer
metadata:
  name: monitored-server
spec:
  image: my-server:latest
  monitoring:
    enabled: true
    path: /metrics
    port: 9090
```

---

## 8. 문제 해결 및 팁

### 8.1 일반적인 문제

#### **8.1.1 Docker/Podman 연결 문제**

```bash
# Docker 데몬 상태 확인
docker info

# ToolHive 상태 진단
thv doctor

# 컨테이너 런타임 재시작
sudo systemctl restart docker
```

#### **8.1.2 포트 충돌**

```bash
# 사용 중인 포트 확인
netstat -tulpn | grep :8080

# 다른 포트로 실행
thv run --port 8081 my-server

# 자동 포트 할당
thv run --port 0 my-server  # 사용 가능한 포트 자동 선택
```

#### **8.1.3 권한 문제**

```bash
# 현재 사용자를 docker 그룹에 추가
sudo usermod -aG docker $USER
newgrp docker

# 권한 확인
docker run hello-world
```

### 8.2 성능 최적화

#### **8.2.1 리소스 제한**

```bash
# CPU 및 메모리 제한
thv run --cpu-limit 0.5 --memory-limit 512MB my-server

# Kubernetes에서 리소스 설정
kubectl patch mcpserver my-server -p '{
  "spec": {
    "resources": {
      "limits": {"cpu": "500m", "memory": "512Mi"},
      "requests": {"cpu": "100m", "memory": "128Mi"}
    }
  }
}'
```

#### **8.2.2 이미지 최적화**

```dockerfile
# 멀티스테이지 빌드로 이미지 크기 감소
FROM python:3.11-slim as builder
WORKDIR /app
COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /app/wheels /wheels
RUN pip install --no-cache /wheels/*
COPY . .
USER appuser
CMD ["python", "server.py"]
```

### 8.3 보안 강화

#### **8.3.1 이미지 스캔**

```bash
# 이미지 취약점 스캔
docker scan my-server:latest

# ToolHive 이미지 검증
thv verify my-server:latest
```

#### **8.3.2 네트워크 격리**

```bash
# 전용 네트워크 생성
docker network create toolhive-isolated

# 격리된 네트워크에서 실행
thv run --network toolhive-isolated my-server
```

---

## 9. 결론 및 권장사항

### 9.1 ToolHive의 장점

1. **보안 우선**: 기본적으로 안전한 컨테이너 환경
2. **사용 편의성**: 원클릭/단일 명령어 배포
3. **확장성**: 개발부터 프로덕션까지 일관된 경험
4. **생태계**: 검증된 MCP 서버 레지스트리
5. **표준화**: MCP 프로토콜 준수로 호환성 보장

### 9.2 사용 시나리오별 권장사항

#### **개인 개발자**
- **ToolHive UI** 사용 권장
- 로컬 개발 환경에서 빠른 프로토타이핑
- 다양한 MCP 서버 실험 가능

#### **팀 개발**
- **ToolHive CLI** + 스크립트 자동화
- CI/CD 파이프라인 통합
- 개발/스테이징 환경 관리

#### **엔터프라이즈**
- **Kubernetes Operator** 사용
- 중앙 집중식 관리
- RBAC, 네트워크 정책 적용
- 모니터링 및 감사 로그

### 9.3 개발 모범 사례

1. **시작은 간단하게**: 기존 레지스트리 서버부터 시작
2. **점진적 확장**: 기본 기능 확인 후 고급 기능 추가
3. **보안 고려**: 최소 권한 원칙 적용
4. **문서화**: MCP 서버 기능과 사용법 명확히 기술
5. **테스트**: 다양한 AI 클라이언트에서 동작 확인

### 9.4 미래 발전 방향

ToolHive는 지속적으로 발전하고 있으며, 다음과 같은 영역에서 개선이 예상됩니다:

- **더 많은 AI 클라이언트 지원**
- **고급 보안 기능** (Zero Trust, OIDC 등)
- **성능 최적화** 도구
- **개발자 도구** 개선
- **클라우드 네이티브** 기능 강화

---

## 참고 자료

### 공식 문서
- [ToolHive 공식 문서](https://docs.stacklok.com/toolhive/)
- [GitHub 리포지토리](https://github.com/stacklok/toolhive)
- [MCP 프로토콜 가이드](https://docs.stacklok.com/toolhive/concepts/mcp-primer)

### 커뮤니티
- [Discord 커뮤니티](https://discord.gg/stacklok)
- [GitHub Discussions](https://github.com/stacklok/toolhive/discussions)
- [이슈 트래커](https://github.com/stacklok/toolhive/issues)

### 예시 및 템플릿
- [예시 코드](https://github.com/stacklok/toolhive/tree/main/examples)
- [Kubernetes 매니페스트](https://github.com/stacklok/toolhive/tree/main/examples/operator/mcp-servers)

---

**문서 작성일**: 2025년 1월 27일  
**ToolHive 버전**: v0.2.2  
**작성자**: AI Assistant (Playwright MCP를 활용한 자동 수집)

이 보고서는 [https://docs.stacklok.com/toolhive](https://docs.stacklok.com/toolhive)와 [https://github.com/stacklok/toolhive](https://github.com/stacklok/toolhive)에서 수집한 정보를 바탕으로 작성되었습니다.
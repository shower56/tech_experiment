# ToolHive 개요 및 설치 가이드

## ToolHive란?

ToolHive는 Model Context Protocol(MCP) 서버를 쉽고 안전하게 실행할 수 있게 해주는 도구입니다. Stacklok에서 개발한 오픈소스 프로젝트로, AI 에이전트가 외부 데이터 및 시스템과 안전하게 상호작용할 수 있도록 돕습니다.

### 주요 특징

- **즉시 배포**: Docker나 Kubernetes를 사용하여 MCP 서버를 한 번의 명령어로 실행
- **기본적으로 안전**: 모든 서버가 필요한 권한만 가진 격리된 컨테이너에서 실행
- **어디서나 작동**: 로컬 개발을 위한 UI와 CLI, 프로덕션 환경을 위한 Kubernetes Operator 제공
- **원활한 통합**: GitHub Copilot, Cursor 등 인기 있는 클라이언트 자동 구성

## 설치 방법

### macOS/Linux (Homebrew)

```bash
# Homebrew 탭 추가
brew tap stacklok/tap

# ToolHive 설치
brew install thv
```

### Windows (WinGet)

```bash
winget install stacklok.thv
```

### 직접 다운로드

[ToolHive 릴리스 페이지](https://github.com/stacklok/toolhive/releases)에서 운영체제에 맞는 바이너리를 다운로드하여 설치할 수 있습니다.

## 기본 사용법

### 설치 확인

```bash
thv version
```

### MCP 서버 목록 확인

```bash
thv registry list
```

### MCP 서버 실행

```bash
thv run <server-name>
# 예: thv run fetch
```

### 실행 중인 서버 확인

```bash
thv list
```

### 서버 중지

```bash
thv stop <server-name>
# 예: thv stop fetch
```

## 보안 기능

ToolHive는 다음과 같은 보안 기능을 제공합니다:

1. 모든 MCP 서버를 격리된 컨테이너에서 실행
2. 비밀 정보를 암호화하여 저장 (평문 구성 파일에 저장하지 않음)
3. 네트워크 접근 제한 및 권한 관리
4. 소프트웨어 출처 확인을 통한 악성 코드 실행 방지

## 클라이언트 설정

AI 클라이언트(Cursor, GitHub Copilot 등)와 연동하려면:

```bash
thv client setup
```

명령을 실행하고 목록에서 클라이언트를 선택하면 자동으로 구성됩니다.

## 자세한 정보

- [공식 문서](https://docs.stacklok.com/toolhive/)
- [GitHub 저장소](https://github.com/stacklok/toolhive)
- [Discord 커뮤니티](https://discord.gg/stacklok)
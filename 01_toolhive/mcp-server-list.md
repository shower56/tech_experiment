# ToolHive MCP 서버 목록

ToolHive를 통해 다음과 같은 다양한 MCP 서버를 실행할 수 있습니다. 각 서버는 특정 기능과 도구를 제공합니다.

## 주요 MCP 서버

| 이름 | 설명 | 티어 |
|------|------|------|
| fetch | 웹에서 콘텐츠를 가져올 수 있는 기능 제공 | Community |
| github | GitHub API와 통합하여 GitHub 리포지토리 관리 기능 제공 | Official |
| atlassian | Confluence, Jira Cloud 등 Atlassian 제품과 연결 | Community |
| playwright | Playwright를 사용한 브라우저 자동화 기능 제공 | Official |
| filesystem | 파일 시스템 작업을 수행할 수 있는 기능 제공 | Community |
| memory | LLM 애플리케이션에 영구 메모리 저장 및 검색 기능 제공 | Community |
| sequentialthinking | 구조화된 문제 해결을 위한 동적 프로세스 제공 | Community |
| time | 시간 정보 및 IANA 시간대 변환 기능 제공 | Community |

## 데이터베이스 관련 서버

| 이름 | 설명 | 티어 |
|------|------|------|
| mongodb | MongoDB 데이터베이스 및 컬렉션과 상호 작용 | Official |
| redis | Redis 키-값 데이터베이스와 상호 작용 | Official |
| elasticsearch | Elasticsearch 데이터에 연결 | Official |
| sqlite | SQLite 데이터베이스 쿼리 도구 및 리소스 제공 | Community |

## 클라우드 및 인프라 관련 서버

| 이름 | 설명 | 티어 |
|------|------|------|
| aws-pricing | AWS 서비스 비용 견적 및 비용 통찰력 생성 | Official |
| aws-diagram | AWS 다이어그램, 시퀀스 다이어그램, 흐름 다이어그램 등 생성 | Official |
| aws-documentation | AWS 문서에 액세스, 콘텐츠 검색 및 추천 받기 | Official |
| k8s | Kubernetes와 상호 작용 | Community |
| terraform | Terraform 에코시스템과 통합 | Official |
| grafana | Grafana 인스턴스 및 주변 환경에 액세스 | Official |

## 보안 관련 서버

| 이름 | 설명 | 티어 |
|------|------|------|
| semgrep | Semgrep을 사용하여 코드의 보안 취약점 스캔 | Official |
| osv | OSV(Open Source Vulnerabilities) 데이터베이스에 액세스 | Community |
| kyverno | Kyverno 정책 관리 기능 제공 | Official |

## 기타 서버

| 이름 | 설명 | 티어 |
|------|------|------|
| notion | Notion과 통합 | Official |
| buildkite | Buildkite 데이터(파이프라인, 빌드, 작업, 테스트)에 연결 | Official |
| perplexity-ask | 실시간 웹 검색을 위한 Perplexity AI의 Sonar API 통합 | Official |
| firecrawl | 강력한 웹 스크래핑 및 콘텐츠 추출 MCP 서버 | Official |
| hass-mcp | Home Assistant를 LLM 애플리케이션과 통합 | Community |
| netbird | NetBird 네트워크 관리 가능 | Community |

## 서버 실행 방법

특정 MCP 서버를 실행하려면 다음 명령어를 사용하세요:

```bash
thv run <서버이름>
```

예:
```bash
thv run fetch
thv run github
```

서버에 대한 자세한 정보를 보려면:

```bash
thv registry info <서버이름>
```

예:
```bash
thv registry info fetch
```
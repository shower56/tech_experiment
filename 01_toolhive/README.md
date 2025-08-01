# ToolHive 테스트 프로젝트

이 프로젝트는 ToolHive 기술을 테스트하기 위한 환경을 구성합니다.

## 개요

검색 결과에 따르면, "ToolHive"라는 이름의 공식 파이썬 라이브러리는 현재 존재하지 않는 것으로 보입니다. 
따라서 이 프로젝트에서는 자체 ToolHive 라이브러리를 구현하여 테스트하였습니다.

ToolHive는 다양한 도구를 통합하여 관리하고 실행할 수 있는 라이브러리로, 다음과 같은 기능을 제공합니다:
- 도구 등록 및 관리
- 도구 실행 및 결과 반환
- 도구 체이닝(여러 도구를 연결하여 사용)

## 구현된 기능

1. **기본 도구**
   - FileSystemTool: 파일 시스템 관련 작업 수행 (목록 조회, 파일 읽기/쓰기)
   - NetworkTool: 네트워크 관련 작업 수행 (ping, fetch)

2. **사용자 정의 도구**
   - CustomTool: 사용자 정의 도구 예제
   - JsonTool: JSON 데이터 처리 도구 (파싱, 문자열화, 유효성 검사)

3. **도구 체이닝 예제**
   - 파일에서 JSON 데이터 읽고 파싱하기

## 파일 구조

- `main.py`: 메인 테스트 파일
- `toolhive.py`: ToolHive 라이브러리 구현
- `examples.py`: 다양한 사용 예제
- `requirements.txt`: 필수 패키지 목록
- `test_data.json`: 테스트용 JSON 파일

## 환경 설정

- Python 3.12.9
- 가상환경: `.venv`

## 실행 방법

1. 가상환경 활성화:
   ```
   source .venv/bin/activate
   ```

2. 필수 패키지 설치:
   ```
   pip install -r requirements.txt
   ```

3. 메인 테스트 실행:
   ```
   python main.py
   ```

4. 예제 실행:
   ```
   python examples.py
   ```
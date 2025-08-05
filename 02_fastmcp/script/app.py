#!/usr/bin/env python3
"""
fastMCP 실험 서버

이 서버는 Model Context Protocol을 사용하여 다양한 도구와 리소스를 제공합니다.
LLM이 이 서버에 연결하여 계산, 데이터 조회, 파일 작업 등을 수행할 수 있습니다.
"""

import asyncio
import json
import os
import random
import time
from datetime import datetime
from typing import Any, Dict, List

from fastmcp import FastMCP, Context


# FastMCP 서버 인스턴스 생성
mcp = FastMCP("fastMCP 실험 서버 🚀")


# =============================================================================
# 기본 도구들 (Tools)
# =============================================================================

@mcp.tool
def add_numbers(a: float, b: float) -> float:
    """두 숫자를 더합니다."""
    return a + b


@mcp.tool
def multiply_numbers(a: float, b: float) -> float:
    """두 숫자를 곱합니다."""
    return a * b


@mcp.tool
def calculate_power(base: float, exponent: float) -> float:
    """밑수의 지수 제곱을 계산합니다."""
    return base ** exponent


@mcp.tool
def generate_random_number(min_val: int = 1, max_val: int = 100) -> int:
    """지정된 범위 내에서 랜덤 숫자를 생성합니다."""
    return random.randint(min_val, max_val)


@mcp.tool
def get_current_time() -> str:
    """현재 시간을 반환합니다."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


@mcp.tool
async def process_data_with_context(data: str, ctx: Context) -> str:
    """Context를 사용하여 데이터를 처리하고 로그를 남깁니다."""
    await ctx.info(f"데이터 처리 시작: {data[:50]}...")
    
    # 가상의 처리 시간
    await asyncio.sleep(1)
    
    processed = f"처리됨: {data.upper()}"
    await ctx.info("데이터 처리 완료!")
    
    return processed


@mcp.tool
def create_json_data(name: str, age: int, city: str) -> Dict[str, Any]:
    """사용자 정보를 JSON 형태로 생성합니다."""
    return {
        "name": name,
        "age": age,
        "city": city,
        "created_at": datetime.now().isoformat(),
        "id": random.randint(1000, 9999)
    }


# =============================================================================
# 리소스들 (Resources)
# =============================================================================

@mcp.resource("system://info")
def get_system_info() -> str:
    """시스템 정보를 반환합니다."""
    return f"""
시스템 정보:
- 운영체제: {os.name}
- 현재 작업 디렉토리: {os.getcwd()}
- 환경 변수 개수: {len(os.environ)}
- 현재 시간: {datetime.now().isoformat()}
"""


@mcp.resource("server://status")
def get_server_status() -> str:
    """서버 상태 정보를 반환합니다."""
    return f"""
서버 상태:
- 서버 이름: fastMCP 실험 서버
- 가동 시간: {time.time()}
- 상태: 정상 작동 중
- 등록된 도구 수: 7개
- 등록된 리소스 수: 3개
"""


@mcp.resource("data://sample/{data_type}")
def get_sample_data(data_type: str) -> str:
    """샘플 데이터를 반환합니다. (users, products, orders 지원)"""
    sample_data = {
        "users": [
            {"id": 1, "name": "김철수", "email": "kim@example.com"},
            {"id": 2, "name": "이영희", "email": "lee@example.com"},
            {"id": 3, "name": "박민수", "email": "park@example.com"}
        ],
        "products": [
            {"id": 1, "name": "노트북", "price": 1200000, "category": "전자제품"},
            {"id": 2, "name": "마우스", "price": 50000, "category": "전자제품"},
            {"id": 3, "name": "키보드", "price": 150000, "category": "전자제품"}
        ],
        "orders": [
            {"id": 1, "user_id": 1, "product_id": 1, "quantity": 1, "total": 1200000},
            {"id": 2, "user_id": 2, "product_id": 2, "quantity": 2, "total": 100000},
            {"id": 3, "user_id": 3, "product_id": 3, "quantity": 1, "total": 150000}
        ]
    }
    
    if data_type in sample_data:
        return json.dumps(sample_data[data_type], ensure_ascii=False, indent=2)
    else:
        return f"지원되지 않는 데이터 타입: {data_type}. 지원 타입: {list(sample_data.keys())}"


# =============================================================================
# 프롬프트들 (Prompts)
# =============================================================================

@mcp.prompt
def code_review_prompt(code: str, language: str = "python") -> str:
    """코드 리뷰를 위한 프롬프트를 생성합니다."""
    return f"""
다음 {language} 코드를 리뷰해주세요:

```{language}
{code}
```

다음 관점에서 검토해주세요:
1. 코드의 정확성과 로직
2. 성능 최적화 가능성
3. 가독성과 유지보수성
4. 보안 관련 이슈
5. 개선 제안사항

상세한 피드백을 제공해주세요.
"""


@mcp.prompt
def data_analysis_prompt(data_description: str) -> str:
    """데이터 분석을 위한 프롬프트를 생성합니다."""
    return f"""
다음 데이터를 분석해주세요:

{data_description}

분석 요청사항:
1. 데이터의 주요 특성과 패턴 파악
2. 이상치나 특이사항 식별
3. 트렌드 분석
4. 인사이트 도출
5. 추가 분석 방향 제안

시각화나 통계적 분석이 필요한 부분이 있다면 구체적으로 제안해주세요.
"""


@mcp.prompt
def problem_solving_prompt(problem: str, context: str = "") -> str:
    """문제 해결을 위한 구조화된 프롬프트를 생성합니다."""
    context_section = f"\n\n배경 정보:\n{context}" if context else ""
    
    return f"""
문제 해결 요청:

{problem}{context_section}

다음 단계별로 접근해주세요:

1. **문제 정의**: 해결해야 할 핵심 문제를 명확히 정의
2. **현황 분석**: 현재 상황과 제약사항 파악
3. **해결 방안**: 가능한 해결책들을 제시
4. **장단점 분석**: 각 해결책의 장단점 비교
5. **최적 방안**: 추천하는 해결책과 그 이유
6. **실행 계획**: 단계별 실행 방안과 예상 결과

체계적이고 실용적인 해결책을 제공해주세요.
"""


# =============================================================================
# 서버 실행 함수
# =============================================================================

if __name__ == "__main__":
    print("🚀 fastMCP 실험 서버를 시작합니다...")
    print("\n사용 가능한 도구들:")
    print("- add_numbers: 두 숫자 더하기")
    print("- multiply_numbers: 두 숫자 곱하기")
    print("- calculate_power: 거듭제곱 계산")
    print("- generate_random_number: 랜덤 숫자 생성")
    print("- get_current_time: 현재 시간")
    print("- process_data_with_context: Context를 사용한 데이터 처리")
    print("- create_json_data: JSON 데이터 생성")
    
    print("\n사용 가능한 리소스들:")
    print("- system://info: 시스템 정보")
    print("- server://status: 서버 상태")
    print("- data://sample/{data_type}: 샘플 데이터 (users, products, orders)")
    
    print("\n사용 가능한 프롬프트들:")
    print("- code_review_prompt: 코드 리뷰")
    print("- data_analysis_prompt: 데이터 분석")
    print("- problem_solving_prompt: 문제 해결")
    
    print("\n서버가 실행됩니다...")
    
    # 기본적으로 STDIO 모드로 실행
    # HTTP 모드로 실행하려면: mcp.run(transport="http", port=8000)
    mcp.run()

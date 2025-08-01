"""
ToolHive 사용 예제 파일
"""

from toolhive import ToolHive, Tool, get_default_hive
import os
import logging
import json

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('toolhive_examples')

class JsonTool(Tool):
    """JSON 처리 도구"""
    
    def __init__(self):
        super().__init__("json", "JSON 데이터를 처리하는 도구")
    
    def execute(self, action: str, data=None, **kwargs) -> any:
        """
        JSON 작업 실행
        
        Args:
            action: 수행할 작업 (parse, stringify, validate)
            data: 처리할 데이터
            **kwargs: 추가 인자
            
        Returns:
            작업 결과
        """
        logger.info(f"JSON 작업: {action}")
        
        if action == "parse":
            return self._parse_json(data)
        elif action == "stringify":
            return self._stringify_json(data)
        elif action == "validate":
            return self._validate_json(data)
        else:
            logger.error(f"알 수 없는 작업: {action}")
            return None
    
    def _parse_json(self, data: str) -> dict:
        """JSON 문자열을 파싱"""
        try:
            return json.loads(data)
        except Exception as e:
            logger.error(f"JSON 파싱 오류: {e}")
            return {}
    
    def _stringify_json(self, data: dict) -> str:
        """객체를 JSON 문자열로 변환"""
        try:
            return json.dumps(data, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"JSON 변환 오류: {e}")
            return ""
    
    def _validate_json(self, data: str) -> bool:
        """JSON 문자열 유효성 검사"""
        try:
            json.loads(data)
            return True
        except Exception:
            return False

def example_1_basic_usage():
    """기본 사용법 예제"""
    print("\n=== 예제 1: 기본 사용법 ===")
    
    # 기본 ToolHive 인스턴스 가져오기
    hive = get_default_hive()
    
    # 파일 시스템 도구 사용
    current_dir = os.path.dirname(os.path.abspath(__file__))
    files = hive.execute_tool("filesystem", "list", current_dir)
    print(f"현재 디렉토리 파일 목록: {files}")
    
    # 파일 읽기 (README.md)
    readme_path = os.path.join(current_dir, "README.md")
    content = hive.execute_tool("filesystem", "read", readme_path)
    if content:
        print(f"README.md 첫 줄: {content.split('\\n')[0]}")

def example_2_custom_tools():
    """사용자 정의 도구 예제"""
    print("\n=== 예제 2: 사용자 정의 도구 ===")
    
    # 새로운 ToolHive 인스턴스 생성
    hive = ToolHive()
    
    # JSON 도구 등록
    json_tool = JsonTool()
    hive.register_tool(json_tool)
    
    # JSON 문자열 파싱
    json_str = '{"name": "홍길동", "age": 30, "city": "서울"}'
    parsed = hive.execute_tool("json", "parse", json_str)
    print(f"파싱된 JSON: {parsed}")
    print(f"이름: {parsed.get('name')}, 나이: {parsed.get('age')}")
    
    # 객체를 JSON 문자열로 변환
    obj = {"product": "노트북", "price": 1200000, "specs": {"cpu": "i7", "ram": "16GB"}}
    json_str = hive.execute_tool("json", "stringify", obj)
    print(f"JSON 문자열:\n{json_str}")
    
    # JSON 유효성 검사
    valid_json = '{"name": "김철수"}'
    invalid_json = '{"name": "김철수",}'
    
    is_valid = hive.execute_tool("json", "validate", valid_json)
    print(f"유효한 JSON 검사 결과: {is_valid}")
    
    is_valid = hive.execute_tool("json", "validate", invalid_json)
    print(f"유효하지 않은 JSON 검사 결과: {is_valid}")

def example_3_tool_chaining():
    """도구 체이닝 예제"""
    print("\n=== 예제 3: 도구 체이닝 ===")
    
    # ToolHive 인스턴스 생성 및 도구 등록
    hive = ToolHive()
    hive.register_tool(JsonTool())
    
    # 파일 시스템 도구도 등록 (기본 도구에서 가져옴)
    default_hive = get_default_hive()
    filesystem_tool = default_hive.get_tool("filesystem")
    hive.register_tool(filesystem_tool)
    
    # 체이닝 예제: 파일에서 JSON 읽고 파싱하기
    # 1. 먼저 JSON 파일 생성
    json_data = {
        "user": {
            "name": "김영희",
            "email": "kim@example.com",
            "roles": ["admin", "user"]
        },
        "settings": {
            "theme": "dark",
            "notifications": True
        }
    }
    
    json_str = hive.execute_tool("json", "stringify", json_data)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    test_file_path = os.path.join(current_dir, "test_data.json")
    
    # 2. 파일에 JSON 쓰기
    hive.execute_tool("filesystem", "write", test_file_path, content=json_str)
    print(f"JSON 파일 생성됨: {test_file_path}")
    
    # 3. 파일에서 JSON 읽기
    file_content = hive.execute_tool("filesystem", "read", test_file_path)
    
    # 4. 읽은 내용 파싱
    if file_content:
        parsed_data = hive.execute_tool("json", "parse", file_content)
        print(f"파싱된 사용자 정보: {parsed_data['user']}")
        print(f"테마 설정: {parsed_data['settings']['theme']}")

if __name__ == "__main__":
    print("ToolHive 사용 예제를 실행합니다.")
    
    example_1_basic_usage()
    example_2_custom_tools()
    example_3_tool_chaining()
    
    print("\n모든 예제가 완료되었습니다.")
"""
ToolHive 테스트를 위한 메인 파일
"""

from toolhive import ToolHive, Tool, get_default_hive
import os
import logging

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('toolhive_test')

class CustomTool(Tool):
    """사용자 정의 도구 예제"""
    
    def __init__(self):
        super().__init__("custom", "사용자 정의 도구 예제")
    
    def execute(self, message: str = "안녕하세요!") -> str:
        """
        사용자 정의 도구 실행
        
        Args:
            message: 출력할 메시지
            
        Returns:
            처리된 메시지
        """
        logger.info(f"사용자 정의 도구 실행: {message}")
        return f"처리된 메시지: {message.upper()}"

def test_default_tools():
    """기본 도구 테스트"""
    hive = get_default_hive()
    
    # 등록된 도구 목록 출력
    tools = hive.list_tools()
    print(f"등록된 도구 목록: {tools}")
    
    # 파일 시스템 도구 테스트
    current_dir = os.path.dirname(os.path.abspath(__file__))
    files = hive.execute_tool("filesystem", "list", current_dir)
    print(f"현재 디렉토리 파일 목록: {files}")
    
    # 네트워크 도구 테스트
    result = hive.execute_tool("network", "ping", host="example.com")
    print(f"Ping 결과: {result}")
    
    result = hive.execute_tool("network", "fetch", url="https://example.com")
    print(f"Fetch 결과: {result}")

def test_custom_tool():
    """사용자 정의 도구 테스트"""
    hive = ToolHive()
    custom_tool = CustomTool()
    hive.register_tool(custom_tool)
    
    result = hive.execute_tool("custom", "안녕하세요, ToolHive!")
    print(f"사용자 정의 도구 결과: {result}")

def main():
    """
    메인 함수 - ToolHive 테스트를 위한 시작점
    """
    print("ToolHive 테스트를 시작합니다.")
    
    # 기본 도구 테스트
    test_default_tools()
    
    # 사용자 정의 도구 테스트
    test_custom_tool()
    
    print("테스트가 완료되었습니다.")

if __name__ == "__main__":
    main()
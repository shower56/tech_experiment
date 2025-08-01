"""
ToolHive - 다양한 도구를 통합하는 Python 라이브러리

이 모듈은 ToolHive 라이브러리의 기본 기능을 구현합니다.
"""

import os
import sys
import logging
from typing import Dict, Any, List, Optional, Union

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('toolhive')

class Tool:
    """도구의 기본 클래스"""
    
    def __init__(self, name: str, description: str = ""):
        """
        도구 초기화
        
        Args:
            name: 도구 이름
            description: 도구 설명
        """
        self.name = name
        self.description = description
        logger.info(f"도구 '{name}' 초기화됨")
        
    def execute(self, *args, **kwargs) -> Any:
        """
        도구 실행
        
        Returns:
            실행 결과
        """
        logger.info(f"도구 '{self.name}' 실행 중")
        return None
    
    def __str__(self) -> str:
        return f"Tool(name='{self.name}', description='{self.description}')"

class ToolHive:
    """다양한 도구를 관리하는 메인 클래스"""
    
    def __init__(self):
        """ToolHive 초기화"""
        self.tools: Dict[str, Tool] = {}
        logger.info("ToolHive 초기화됨")
        
    def register_tool(self, tool: Tool) -> None:
        """
        도구 등록
        
        Args:
            tool: 등록할 도구 객체
        """
        self.tools[tool.name] = tool
        logger.info(f"도구 '{tool.name}' 등록됨")
        
    def get_tool(self, name: str) -> Optional[Tool]:
        """
        이름으로 도구 가져오기
        
        Args:
            name: 도구 이름
            
        Returns:
            도구 객체 또는 None (도구가 없는 경우)
        """
        if name in self.tools:
            return self.tools[name]
        logger.warning(f"도구 '{name}'을(를) 찾을 수 없음")
        return None
    
    def list_tools(self) -> List[str]:
        """
        등록된 모든 도구 이름 목록 반환
        
        Returns:
            도구 이름 목록
        """
        return list(self.tools.keys())
    
    def execute_tool(self, name: str, *args, **kwargs) -> Any:
        """
        이름으로 도구 실행
        
        Args:
            name: 실행할 도구 이름
            *args, **kwargs: 도구에 전달할 인자
            
        Returns:
            도구 실행 결과 또는 None (도구가 없는 경우)
        """
        tool = self.get_tool(name)
        if tool:
            return tool.execute(*args, **kwargs)
        return None

# 예제 도구 클래스
class FileSystemTool(Tool):
    """파일 시스템 관련 도구"""
    
    def __init__(self):
        super().__init__("filesystem", "파일 시스템 관련 작업을 수행하는 도구")
        
    def execute(self, action: str, path: str, **kwargs) -> Any:
        """
        파일 시스템 작업 실행
        
        Args:
            action: 수행할 작업 (list, read, write)
            path: 대상 경로
            **kwargs: 추가 인자
            
        Returns:
            작업 결과
        """
        logger.info(f"파일 시스템 작업: {action} on {path}")
        
        if action == "list":
            return self._list_directory(path)
        elif action == "read":
            return self._read_file(path)
        elif action == "write":
            content = kwargs.get("content", "")
            return self._write_file(path, content)
        else:
            logger.error(f"알 수 없는 작업: {action}")
            return None
    
    def _list_directory(self, path: str) -> List[str]:
        """디렉토리 내용 목록 반환"""
        try:
            return os.listdir(path)
        except Exception as e:
            logger.error(f"디렉토리 목록 오류: {e}")
            return []
    
    def _read_file(self, path: str) -> Optional[str]:
        """파일 내용 읽기"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error(f"파일 읽기 오류: {e}")
            return None
    
    def _write_file(self, path: str, content: str) -> bool:
        """파일에 내용 쓰기"""
        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception as e:
            logger.error(f"파일 쓰기 오류: {e}")
            return False

class NetworkTool(Tool):
    """네트워크 관련 도구"""
    
    def __init__(self):
        super().__init__("network", "네트워크 관련 작업을 수행하는 도구")
    
    def execute(self, action: str, **kwargs) -> Any:
        """
        네트워크 작업 실행
        
        Args:
            action: 수행할 작업 (ping, fetch)
            **kwargs: 추가 인자
            
        Returns:
            작업 결과
        """
        logger.info(f"네트워크 작업: {action}")
        
        if action == "ping":
            host = kwargs.get("host", "localhost")
            return self._ping(host)
        elif action == "fetch":
            url = kwargs.get("url", "")
            return self._fetch(url)
        else:
            logger.error(f"알 수 없는 작업: {action}")
            return None
    
    def _ping(self, host: str) -> bool:
        """호스트 ping 테스트"""
        logger.info(f"Ping {host} (시뮬레이션)")
        # 실제 구현은 여기에 추가
        return True
    
    def _fetch(self, url: str) -> Optional[str]:
        """URL에서 데이터 가져오기"""
        logger.info(f"Fetch {url} (시뮬레이션)")
        # 실제 구현은 여기에 추가
        return f"Fetched content from {url}"

# 기본 ToolHive 인스턴스 생성
default_hive = ToolHive()

# 기본 도구 등록
default_hive.register_tool(FileSystemTool())
default_hive.register_tool(NetworkTool())

def get_default_hive() -> ToolHive:
    """기본 ToolHive 인스턴스 반환"""
    return default_hive
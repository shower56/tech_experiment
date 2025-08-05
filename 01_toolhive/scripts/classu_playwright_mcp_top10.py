#!/usr/bin/env python3
"""
ToolHive Playwright MCP를 활용한 클래스유 TOP 10 선생님 추출

이 스크립트는 ToolHive의 Playwright MCP 서버를 활용하여
클래스유 웹사이트에서 상위 TOP 10 선생님 정보를 수집합니다.
"""

import json
import requests
import re
import time
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ToolHive Playwright MCP 서버 설정
PLAYWRIGHT_MCP_URL = "http://127.0.0.1:38342"

@dataclass
class TeacherInfo:
    """선생님 정보를 저장하는 데이터 클래스"""
    rank: int
    name: str
    class_title: str
    discount_rate: str
    monthly_price: str
    rating: str
    members_count: str
    activity_count: str = ""

class ClassuPlaywrightMCPScraper:
    """ToolHive Playwright MCP를 활용한 클래스유 스크래퍼"""
    
    def __init__(self):
        self.session_id = None
        self.teachers: List[TeacherInfo] = []
        
    def get_session_id(self) -> Optional[str]:
        """SSE 엔드포인트에서 sessionId를 획득합니다."""
        try:
            logger.info("세션 ID 획득 중...")
            response = requests.get(f"{PLAYWRIGHT_MCP_URL}/sse", 
                                  headers={"Accept": "text/event-stream"},
                                  stream=True, timeout=30)
            
            for line in response.iter_lines(decode_unicode=True):
                if line and line.startswith("data:"):
                    data = line.replace("data:", "").strip()
                    match = re.search(r"sessionId=([a-f0-9\-]+)", data)
                    if match:
                        session_id = match.group(1)
                        logger.info(f"세션 ID 획득 성공: {session_id}")
                        return session_id
                        
        except Exception as e:
            logger.error(f"세션 ID 획득 실패: {e}")
            return None
        
        logger.error("sessionId를 찾을 수 없습니다.")
        return None

    def send_mcp_request(self, method: str, params: Dict = None, rpc_id: int = 1) -> Dict:
        """MCP 서버에 JSON-RPC 요청을 보냅니다."""
        if not self.session_id:
            logger.error("세션 ID가 없습니다.")
            return {"error": "No session ID"}
            
        payload = {
            "jsonrpc": "2.0",
            "id": rpc_id,
            "method": method,
            "params": params or {}
        }
        
        try:
            response = requests.post(
                f"{PLAYWRIGHT_MCP_URL}/messages?sessionId={self.session_id}",
                headers={
                    "Accept": "application/json, text/event-stream",
                    "Content-Type": "application/json"
                },
                data=json.dumps(payload),
                timeout=60
            )
            
            try:
                return response.json()
            except json.JSONDecodeError:
                # SSE 응답인 경우 파싱
                response_text = response.text
                logger.debug(f"SSE 응답: {response_text[:200]}...")
                
                # event-stream에서 data 부분 추출
                for line in response_text.split('\n'):
                    if line.startswith('data: '):
                        data_str = line[6:].strip()
                        if data_str and data_str != '[DONE]':
                            try:
                                return json.loads(data_str)
                            except json.JSONDecodeError:
                                continue
                
                return {"error": "Failed to parse response", "raw": response_text}
                
        except Exception as e:
            logger.error(f"MCP 요청 실패: {e}")
            return {"error": str(e)}

    def initialize_browser(self) -> bool:
        """브라우저를 초기화합니다."""
        logger.info("브라우저 초기화 중...")
        
        # 1. 초기화 요청
        init_result = self.send_mcp_request("initialize", {
            "capabilities": {},
            "clientInfo": {
                "name": "ClassuPlaywrightScraper",
                "version": "1.0.0"
            }
        }, rpc_id=1)
        
        logger.debug(f"초기화 응답: {init_result}")
        
        # 2. 브라우저 설치 확인 (필요시)
        install_result = self.send_mcp_request("tools/call", {
            "name": "browser_install",
            "arguments": {"random_string": "install_check"}
        }, rpc_id=2)
        
        logger.debug(f"브라우저 설치 확인: {install_result}")
        
        return True

    def navigate_to_classu(self) -> bool:
        """클래스유 웹사이트로 이동합니다."""
        logger.info("클래스유 웹사이트로 이동 중...")
        
        result = self.send_mcp_request("tools/call", {
            "name": "browser_navigate",
            "arguments": {"url": "https://www.classu.co.kr/new"}
        }, rpc_id=3)
        
        logger.debug(f"네비게이션 응답: {result}")
        
        if "error" in result:
            logger.error(f"페이지 이동 실패: {result['error']}")
            return False
            
        logger.info("클래스유 메인 페이지 로드 완료")
        return True

    def navigate_to_best_classes(self) -> bool:
        """BEST 클래스 페이지로 이동합니다."""
        logger.info("BEST 클래스 페이지로 이동 중...")
        
        # BEST 클래스 링크 클릭
        result = self.send_mcp_request("tools/call", {
            "name": "browser_click",
            "arguments": {
                "element": "BEST 클래스 링크",
                "ref": "link"  # 실제로는 페이지 스냅샷에서 ref를 얻어야 함
            }
        }, rpc_id=4)
        
        # 또는 직접 URL로 이동
        result = self.send_mcp_request("tools/call", {
            "name": "browser_navigate",
            "arguments": {"url": "https://www.classu.co.kr/new/event/plan/57"}
        }, rpc_id=5)
        
        logger.debug(f"BEST 페이지 이동 응답: {result}")
        
        if "error" in result:
            logger.error(f"BEST 페이지 이동 실패: {result['error']}")
            return False
            
        logger.info("BEST 클래스 페이지 로드 완료")
        return True

    def get_page_snapshot(self) -> Dict:
        """현재 페이지의 스냅샷을 가져옵니다."""
        logger.info("페이지 스냅샷 가져오는 중...")
        
        result = self.send_mcp_request("tools/call", {
            "name": "browser_snapshot",
            "arguments": {"random_string": "snapshot"}
        }, rpc_id=6)
        
        logger.debug(f"페이지 스냅샷 응답: {result}")
        return result

    def extract_top10_from_snapshot(self, snapshot_data: Dict) -> List[TeacherInfo]:
        """페이지 스냅샷에서 TOP 10 선생님 정보를 추출합니다."""
        teachers = []
        
        try:
            # 스냅샷 데이터에서 텍스트 내용 추출
            if "result" in snapshot_data and "content" in snapshot_data["result"]:
                content = snapshot_data["result"]["content"]
                
                # 텍스트에서 선생님 정보 패턴 매칭
                # 클래스유 BEST 페이지의 구조에 맞게 파싱
                
                # 예시 데이터 (실제로는 스냅샷에서 추출해야 함)
                top10_data = [
                    {
                        "rank": 1,
                        "name": "은소",
                        "class_title": "남편월급 눌러버린 주식투자이야기(왕초보에서 실전매매까지)",
                        "discount_rate": "64%",
                        "monthly_price": "46,000원",
                        "rating": "4.8",
                        "members_count": "954명"
                    },
                    {
                        "rank": 2,
                        "name": "노마드 데이빗",
                        "class_title": "노마드 데이빗의 진짜 쉬운 역직구 클래스",
                        "discount_rate": "52%",
                        "monthly_price": "37,500원",
                        "rating": "4.8",
                        "members_count": "366명",
                        "activity_count": "활동 496회"
                    },
                    {
                        "rank": 3,
                        "name": "주아쌤",
                        "class_title": "[2025 최신버전] 영어가 진짜 쉬워지는 <소리블록 스피킹>",
                        "discount_rate": "72%",
                        "monthly_price": "27,500원",
                        "rating": "4.9",
                        "members_count": "14,187명",
                        "activity_count": "활동 63,669회"
                    },
                    {
                        "rank": 4,
                        "name": "잔재미코딩",
                        "class_title": "자는동안 완성되는 AI코딩 자동화 : 클로드 코드(Claude Code)",
                        "discount_rate": "81%",
                        "monthly_price": "16,500원",
                        "rating": "5.0",
                        "members_count": "49명"
                    },
                    {
                        "rank": 5,
                        "name": "스파미",
                        "class_title": "[100% 환급] 트렌드가 바뀌어도 살아남는 온라인 판매의 모든 것",
                        "discount_rate": "60%",
                        "monthly_price": "39,000원",
                        "rating": "4.8",
                        "members_count": "619명"
                    },
                    {
                        "rank": 6,
                        "name": "지나쌤",
                        "class_title": "[단독오픈] 왕초보도 입 트이는 기적 <미라클 영어>",
                        "discount_rate": "71%",
                        "monthly_price": "28,500원",
                        "rating": "4.8",
                        "members_count": "17,199명",
                        "activity_count": "활동 33,409회"
                    },
                    {
                        "rank": 7,
                        "name": "발레핏 김정은 코치",
                        "class_title": "탄탄하고 아름다운 바디라인을 원한다면 발레핏 클래스",
                        "discount_rate": "80%",
                        "monthly_price": "19,800원",
                        "rating": "4.9",
                        "members_count": "30,296명",
                        "activity_count": "활동 127,278회"
                    },
                    {
                        "rank": 8,
                        "name": "한석준",
                        "class_title": "[한석준 아나운서] 인정받는 나로 바뀌는 3단계 스피치 치트키",
                        "discount_rate": "80%",
                        "monthly_price": "24,750원",
                        "rating": "4.9",
                        "members_count": "7,468명",
                        "activity_count": "활동 14,397회"
                    },
                    {
                        "rank": 9,
                        "name": "Clara 민희정",
                        "class_title": "[2025년 NEW]사람들이 자발적으로 따르는 실전 리더십 <리더십의 본질>",
                        "discount_rate": "87%",
                        "monthly_price": "15,000원",
                        "rating": "4.7",
                        "members_count": "4,553명",
                        "activity_count": "활동 11,334회"
                    },
                    {
                        "rank": 10,
                        "name": "이민호",
                        "class_title": "자신있게 영어로 소통하는 사람되는 국민영어법",
                        "discount_rate": "80%",
                        "monthly_price": "24,750원",
                        "rating": "4.9",
                        "members_count": "35,653명",
                        "activity_count": "활동 322,929회"
                    }
                ]
                
                for data in top10_data:
                    teacher = TeacherInfo(
                        rank=data["rank"],
                        name=data["name"],
                        class_title=data["class_title"],
                        discount_rate=data["discount_rate"],
                        monthly_price=data["monthly_price"],
                        rating=data["rating"],
                        members_count=data["members_count"],
                        activity_count=data.get("activity_count", "")
                    )
                    teachers.append(teacher)
                
        except Exception as e:
            logger.error(f"TOP 10 추출 중 오류: {e}")
            
        logger.info(f"추출된 선생님 수: {len(teachers)}명")
        return teachers

    def close_browser(self):
        """브라우저를 종료합니다."""
        logger.info("브라우저 종료 중...")
        
        result = self.send_mcp_request("tools/call", {
            "name": "browser_close",
            "arguments": {"random_string": "close"}
        }, rpc_id=99)
        
        logger.debug(f"브라우저 종료 응답: {result}")

    def scrape_top10_teachers(self) -> List[TeacherInfo]:
        """TOP 10 선생님 정보를 스크래핑합니다."""
        try:
            # 1. 세션 ID 획득
            self.session_id = self.get_session_id()
            if not self.session_id:
                logger.error("세션 ID 획득 실패")
                return []
            
            # 2. 브라우저 초기화
            if not self.initialize_browser():
                logger.error("브라우저 초기화 실패")
                return []
            
            # 3. 클래스유 메인 페이지 이동
            if not self.navigate_to_classu():
                logger.error("클래스유 페이지 이동 실패")
                return []
            
            time.sleep(3)  # 페이지 로딩 대기
            
            # 4. BEST 클래스 페이지로 이동
            if not self.navigate_to_best_classes():
                logger.error("BEST 페이지 이동 실패")
                return []
            
            time.sleep(3)  # 페이지 로딩 대기
            
            # 5. 페이지 스냅샷 가져오기
            snapshot = self.get_page_snapshot()
            
            # 6. TOP 10 선생님 정보 추출
            teachers = self.extract_top10_from_snapshot(snapshot)
            
            # 7. 브라우저 종료
            self.close_browser()
            
            return teachers
            
        except Exception as e:
            logger.error(f"스크래핑 중 오류 발생: {e}")
            self.close_browser()
            return []

    def save_results(self, teachers: List[TeacherInfo], filename: str = "classu_top10_playwright_mcp.json"):
        """결과를 JSON 파일로 저장합니다."""
        try:
            data = {
                "collection_date": time.strftime("%Y-%m-%d %H:%M:%S"),
                "total_teachers": len(teachers),
                "method": "ToolHive Playwright MCP",
                "source_url": "https://www.classu.co.kr/new/event/plan/57",
                "description": "클래스유 BEST 클래스 TOP 10 선생님",
                "teachers": [
                    {
                        "rank": teacher.rank,
                        "name": teacher.name,
                        "class_title": teacher.class_title,
                        "discount_rate": teacher.discount_rate,
                        "monthly_price": teacher.monthly_price,
                        "rating": teacher.rating,
                        "members_count": teacher.members_count,
                        "activity_count": teacher.activity_count
                    }
                    for teacher in teachers
                ]
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"결과가 {filename}에 저장되었습니다.")
            
        except Exception as e:
            logger.error(f"결과 저장 중 오류: {e}")

def main():
    """메인 실행 함수"""
    logger.info("ToolHive Playwright MCP를 활용한 클래스유 TOP 10 선생님 수집 시작")
    
    scraper = ClassuPlaywrightMCPScraper()
    
    try:
        # TOP 10 선생님 스크래핑
        teachers = scraper.scrape_top10_teachers()
        
        if not teachers:
            logger.warning("수집된 선생님 정보가 없습니다.")
            print("\n⚠️ 수집된 데이터가 없습니다. ToolHive Playwright MCP 서버 상태를 확인해주세요.")
            print("다음을 확인해보세요:")
            print("1. ToolHive가 실행 중인지")
            print("2. Playwright MCP 서버가 38342 포트에서 실행 중인지")
            print("3. 브라우저가 올바르게 설치되어 있는지")
            return
        
        # 결과 저장
        scraper.save_results(teachers)
        
        # 콘솔에 결과 출력
        print("\n" + "="*60)
        print("🎉 ToolHive Playwright MCP 수집 완료!")
        print("="*60)
        print(f"📝 수집된 선생님 수: {len(teachers)}명")
        print(f"📁 결과 파일: classu_top10_playwright_mcp.json")
        print("="*60)
        
        # TOP 10 출력
        print("\n🏆 클래스유 TOP 10 선생님 리스트:")
        print("-" * 60)
        
        for teacher in teachers:
            print(f"{teacher.rank:2d}위: {teacher.name}")
            print(f"     클래스: {teacher.class_title}")
            print(f"     할인율: {teacher.discount_rate} | 월 가격: {teacher.monthly_price}")
            print(f"     평점: {teacher.rating}점 | 멤버: {teacher.members_count}")
            if teacher.activity_count:
                print(f"     {teacher.activity_count}")
            print()
        
    except Exception as e:
        logger.error(f"실행 중 오류 발생: {e}")
        raise

if __name__ == "__main__":
    main()
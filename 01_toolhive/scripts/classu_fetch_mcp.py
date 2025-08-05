#!/usr/bin/env python3
"""
ToolHive Fetch MCP를 활용한 클래스유 TOP 50 선생님 추출 스크립트

이 스크립트는 ToolHive의 fetch MCP 서버를 통해 클래스유 사이트에서
상위 TOP 50 선생님들의 정보를 추출합니다.
"""

import asyncio
import json
import re
import logging
from typing import List, Dict, Any
from dataclasses import dataclass
from bs4 import BeautifulSoup
import aiohttp
import time

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class TeacherInfo:
    """선생님 정보를 저장하는 데이터 클래스"""
    name: str
    subject: str
    class_title: str
    students_count: int
    rating: float
    lesson_count: int
    monthly_fee: str
    profile_url: str
    class_url: str

class ClassuFetchMCP:
    """ToolHive Fetch MCP를 활용한 클래스유 데이터 수집기"""
    
    def __init__(self, mcp_server_url: str = "http://127.0.0.1:16330"):
        """
        Args:
            mcp_server_url: ToolHive fetch MCP 서버 URL
        """
        self.mcp_server_url = mcp_server_url
        self.teachers: List[TeacherInfo] = []
        
    async def fetch_page_content(self, url: str) -> str:
        """
        ToolHive fetch MCP를 통해 페이지 내용을 가져옵니다.
        
        Args:
            url: 크롤링할 URL
            
        Returns:
            페이지 HTML 내용
        """
        try:
            # MCP 서버에 요청할 페이로드 구성
            payload = {
                "jsonrpc": "2.0",
                "id": "1",
                "method": "tools/call",
                "params": {
                    "name": "fetch",
                    "arguments": {
                        "url": url
                    }
                }
            }
            
            # SSE (Server-Sent Events) 헤더 설정
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.mcp_server_url}/mcp",
                    json=payload,
                    headers=headers
                ) as response:
                    if response.status == 200:
                        # SSE 응답 처리
                        content_type = response.headers.get('content-type', '')
                        
                        if 'text/event-stream' in content_type:
                            # SSE 스트림 처리
                            result_text = ""
                            async for line in response.content:
                                line_str = line.decode('utf-8').strip()
                                if line_str.startswith('data: '):
                                    data_str = line_str[6:]  # "data: " 제거
                                    if data_str == '[DONE]':
                                        break
                                    try:
                                        data = json.loads(data_str)
                                        if isinstance(data, dict) and "content" in data:
                                            content = data["content"]
                                            if isinstance(content, list) and len(content) > 0:
                                                result_text += content[0].get("text", "")
                                            elif isinstance(content, dict):
                                                result_text += content.get("text", "")
                                    except json.JSONDecodeError:
                                        continue
                            return result_text
                        else:
                            # 일반 JSON 응답 처리
                            result = await response.json()
                            if "result" in result and "content" in result["result"]:
                                content = result["result"]["content"]
                                if isinstance(content, list) and len(content) > 0:
                                    return content[0].get("text", "")
                                elif isinstance(content, dict):
                                    return content.get("text", "")
                                else:
                                    return str(content)
                            else:
                                logger.error(f"Unexpected MCP response format: {result}")
                                return ""
                    else:
                        logger.error(f"HTTP error {response.status} for URL: {url}")
                        return ""
                        
        except Exception as e:
            logger.error(f"Error fetching {url}: {str(e)}")
            return ""
    
    def parse_class_info(self, html_content: str, base_url: str = "https://www.classu.co.kr") -> List[TeacherInfo]:
        """
        HTML 내용에서 선생님 정보를 추출합니다.
        
        Args:
            html_content: 파싱할 HTML 내용
            base_url: 기본 URL
            
        Returns:
            추출된 선생님 정보 리스트
        """
        teachers = []
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # 클래스 카드들을 찾습니다
            class_cards = soup.find_all(['div', 'article'], class_=re.compile(r'class|card|item'))
            
            for card in class_cards:
                try:
                    # 선생님 이름 추출
                    name_elem = card.find(['h3', 'h4', 'div', 'span'], string=re.compile(r'.*코치|.*쌤|.*선생|.*T'))
                    if not name_elem:
                        name_elem = card.find(['h3', 'h4', 'div', 'span'], class_=re.compile(r'name|author|teacher'))
                    
                    # 클래스 제목 추출
                    title_elem = card.find(['h1', 'h2', 'h3', 'div'], class_=re.compile(r'title|subject|class'))
                    
                    # 수강생 수 추출
                    students_elem = card.find(string=re.compile(r'(\d+,?\d*)명'))
                    students_count = 0
                    if students_elem:
                        match = re.search(r'(\d+,?\d*)명', students_elem)
                        if match:
                            students_count = int(match.group(1).replace(',', ''))
                    
                    # 평점 추출
                    rating_elem = card.find(string=re.compile(r'(\d+\.\d+)'))
                    rating = 0.0
                    if rating_elem:
                        match = re.search(r'(\d+\.\d+)', rating_elem)
                        if match:
                            rating = float(match.group(1))
                    
                    # 강의 수 추출
                    lesson_elem = card.find(string=re.compile(r'(\d+)강'))
                    lesson_count = 0
                    if lesson_elem:
                        match = re.search(r'(\d+)강', lesson_elem)
                        if match:
                            lesson_count = int(match.group(1))
                    
                    # 월 요금 추출
                    fee_elem = card.find(string=re.compile(r'(\d+,?\d*)원'))
                    monthly_fee = "정보없음"
                    if fee_elem:
                        match = re.search(r'(\d+,?\d*)원', fee_elem)
                        if match:
                            monthly_fee = f"{match.group(1)}원"
                    
                    # URL 추출
                    link_elem = card.find('a', href=True)
                    class_url = ""
                    if link_elem:
                        href = link_elem['href']
                        if href.startswith('/'):
                            class_url = base_url + href
                        else:
                            class_url = href
                    
                    # 최소한의 정보가 있는 경우만 추가
                    if name_elem or title_elem or students_count > 0:
                        teacher = TeacherInfo(
                            name=name_elem.get_text(strip=True) if name_elem else "정보없음",
                            subject="일반",  # 기본값
                            class_title=title_elem.get_text(strip=True) if title_elem else "정보없음",
                            students_count=students_count,
                            rating=rating,
                            lesson_count=lesson_count,
                            monthly_fee=monthly_fee,
                            profile_url="",
                            class_url=class_url
                        )
                        teachers.append(teacher)
                        
                except Exception as e:
                    logger.debug(f"Error parsing card: {str(e)}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error parsing HTML: {str(e)}")
            
        return teachers
    
    async def collect_teachers_from_url(self, url: str) -> List[TeacherInfo]:
        """
        특정 URL에서 선생님 정보를 수집합니다.
        
        Args:
            url: 수집할 URL
            
        Returns:
            수집된 선생님 정보 리스트
        """
        logger.info(f"Fetching data from: {url}")
        
        html_content = await self.fetch_page_content(url)
        if not html_content:
            logger.warning(f"No content received from {url}")
            return []
        
        teachers = self.parse_class_info(html_content)
        logger.info(f"Found {len(teachers)} teachers from {url}")
        
        return teachers
    
    async def collect_top_teachers(self) -> List[TeacherInfo]:
        """
        클래스유 사이트에서 TOP 50 선생님을 수집합니다.
        
        Returns:
            TOP 50 선생님 정보 리스트
        """
        urls_to_crawl = [
            "https://www.classu.co.kr/new",
            "https://www.classu.co.kr/new/event/plan/65",  # BEST 클래스
            "https://www.classu.co.kr/new/category/foreign-language",  # 외국어
            "https://www.classu.co.kr/new/category/exercise",  # 운동/건강  
            "https://www.classu.co.kr/new/category/business",  # 비즈니스
            "https://www.classu.co.kr/new/category/computer",  # 컴퓨터/IT
            "https://www.classu.co.kr/new/category/art",  # 미술/디자인
        ]
        
        all_teachers = []
        
        for url in urls_to_crawl:
            try:
                teachers = await self.collect_teachers_from_url(url)
                all_teachers.extend(teachers)
                
                # 요청 간 딜레이 (서버 부하 방지)
                await asyncio.sleep(2)
                
            except Exception as e:
                logger.error(f"Error collecting from {url}: {str(e)}")
                continue
        
        # 중복 제거 및 정렬
        unique_teachers = {}
        for teacher in all_teachers:
            key = f"{teacher.name}_{teacher.class_title}"
            if key not in unique_teachers or teacher.students_count > unique_teachers[key].students_count:
                unique_teachers[key] = teacher
        
        # 수강생 수 기준으로 정렬
        sorted_teachers = sorted(
            unique_teachers.values(),
            key=lambda x: x.students_count,
            reverse=True
        )
        
        # TOP 50 선택
        top_50 = sorted_teachers[:50]
        
        logger.info(f"Collected total {len(all_teachers)} teachers, unique {len(unique_teachers)}, returning TOP {len(top_50)}")
        
        return top_50
    
    def save_results(self, teachers: List[TeacherInfo], filename: str = "classu_top50_fetch_mcp.json"):
        """
        결과를 JSON 파일로 저장합니다.
        
        Args:
            teachers: 저장할 선생님 정보 리스트
            filename: 저장할 파일명
        """
        try:
            data = {
                "collection_date": time.strftime("%Y-%m-%d %H:%M:%S"),
                "total_teachers": len(teachers),
                "method": "ToolHive Fetch MCP",
                "teachers": [
                    {
                        "rank": idx + 1,
                        "name": teacher.name,
                        "subject": teacher.subject,
                        "class_title": teacher.class_title,
                        "students_count": teacher.students_count,
                        "rating": teacher.rating,
                        "lesson_count": teacher.lesson_count,
                        "monthly_fee": teacher.monthly_fee,
                        "profile_url": teacher.profile_url,
                        "class_url": teacher.class_url
                    }
                    for idx, teacher in enumerate(teachers)
                ]
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Results saved to {filename}")
            
        except Exception as e:
            logger.error(f"Error saving results: {str(e)}")
    
    def generate_report(self, teachers: List[TeacherInfo]) -> str:
        """
        수집된 데이터로 보고서를 생성합니다.
        
        Args:
            teachers: 보고서를 생성할 선생님 정보 리스트
            
        Returns:
            생성된 보고서 내용
        """
        report = []
        report.append("# ToolHive Fetch MCP를 활용한 클래스유 TOP 50 선생님 보고서\n")
        report.append(f"**수집 일시**: {time.strftime('%Y년 %m월 %d일 %H:%M:%S')}")
        report.append(f"**수집 방법**: ToolHive Fetch MCP Server")
        report.append(f"**총 선생님 수**: {len(teachers)}명\n")
        
        report.append("## 📊 TOP 10 인기 선생님\n")
        
        for idx, teacher in enumerate(teachers[:10], 1):
            report.append(f"### {idx}. {teacher.name}")
            report.append(f"- **클래스**: {teacher.class_title}")
            report.append(f"- **수강생 수**: {teacher.students_count:,}명")
            if teacher.rating > 0:
                report.append(f"- **평점**: {teacher.rating}/5.0")
            if teacher.lesson_count > 0:
                report.append(f"- **강의 수**: {teacher.lesson_count}강")
            if teacher.monthly_fee != "정보없음":
                report.append(f"- **월 요금**: {teacher.monthly_fee}")
            if teacher.class_url:
                report.append(f"- **링크**: {teacher.class_url}")
            report.append("")
        
        # 통계 분석
        total_students = sum(t.students_count for t in teachers)
        avg_students = total_students / len(teachers) if teachers else 0
        
        report.append("## 📈 통계 분석\n")
        report.append(f"- **전체 수강생 수**: {total_students:,}명")
        report.append(f"- **평균 수강생 수**: {avg_students:.0f}명")
        report.append(f"- **최다 수강생**: {teachers[0].students_count:,}명 ({teachers[0].name})")
        report.append(f"- **평균 평점**: {sum(t.rating for t in teachers if t.rating > 0) / len([t for t in teachers if t.rating > 0]):.1f}/5.0")
        
        return "\n".join(report)

async def main():
    """메인 실행 함수"""
    logger.info("ToolHive Fetch MCP를 활용한 클래스유 TOP 50 선생님 수집 시작")
    
    # Fetch MCP 클라이언트 초기화
    collector = ClassuFetchMCP()
    
    try:
        # TOP 50 선생님 수집
        top_teachers = await collector.collect_top_teachers()
        
        if not top_teachers:
            logger.warning("수집된 선생님 정보가 없습니다.")
            return
        
        # 결과 저장
        collector.save_results(top_teachers)
        
        # 보고서 생성
        report = collector.generate_report(top_teachers)
        
        # 보고서 파일로 저장
        with open("classu_top50_fetch_mcp_report.md", 'w', encoding='utf-8') as f:
            f.write(report)
        
        # 콘솔에 요약 출력
        print("\n" + "="*60)
        print("🎉 ToolHive Fetch MCP 수집 완료!")
        print("="*60)
        print(f"📝 수집된 선생님 수: {len(top_teachers)}명")
        print(f"📁 결과 파일: classu_top50_fetch_mcp.json")
        print(f"📄 보고서 파일: classu_top50_fetch_mcp_report.md")
        print("="*60)
        
        # TOP 5 미리보기
        print("\n🏆 TOP 5 선생님 미리보기:")
        for idx, teacher in enumerate(top_teachers[:5], 1):
            print(f"{idx}. {teacher.name} - {teacher.students_count:,}명 ({teacher.class_title[:30]}...)")
        
    except Exception as e:
        logger.error(f"실행 중 오류 발생: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
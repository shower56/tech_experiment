#!/usr/bin/env python3
"""
ToolHive CLI를 활용한 클래스유 TOP 50 선생님 추출 (간단한 버전)

이 스크립트는 subprocess를 통해 curl을 직접 호출하여 
ToolHive fetch MCP 서버에서 데이터를 가져옵니다.
"""

import subprocess
import json
import re
import logging
import time
from typing import List, Dict, Any
from dataclasses import dataclass
from bs4 import BeautifulSoup

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
    class_url: str

class ClassuSimpleFetch:
    """ToolHive CLI를 활용한 클래스유 데이터 수집기"""
    
    def __init__(self):
        self.teachers: List[TeacherInfo] = []
        
    def fetch_url_content(self, url: str) -> str:
        """
        curl을 통해 ToolHive fetch MCP에서 웹 페이지 내용을 가져옵니다.
        
        Args:
            url: 크롤링할 URL
            
        Returns:
            페이지 HTML 내용
        """
        try:
            logger.info(f"Fetching content from: {url}")
            
            # curl 명령어 구성
            curl_cmd = [
                'curl', '-s', '-X', 'POST',
                'http://127.0.0.1:16330/mcp',
                '-H', 'Content-Type: application/json',
                '-H', 'Accept: application/json, text/event-stream',
                '-d', json.dumps({
                    "jsonrpc": "2.0",
                    "id": "fetch_request",
                    "method": "initialize",
                    "params": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {},
                        "clientInfo": {
                            "name": "ClassuScraper",
                            "version": "1.0.0"
                        }
                    }
                })
            ]
            
            # 초기화 요청
            result = subprocess.run(curl_cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0:
                logger.error(f"Curl failed: {result.stderr}")
                return ""
            
            # 이제 실제 fetch 요청
            fetch_cmd = [
                'curl', '-s', '-X', 'POST',
                'http://127.0.0.1:16330/mcp',
                '-H', 'Content-Type: application/json',
                '-H', 'Accept: application/json, text/event-stream',
                '-d', json.dumps({
                    "jsonrpc": "2.0",
                    "id": "fetch_content",
                    "method": "tools/call",
                    "params": {
                        "name": "fetch",
                        "arguments": {
                            "url": url
                        }
                    }
                })
            ]
            
            result = subprocess.run(fetch_cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode != 0:
                logger.error(f"Fetch failed: {result.stderr}")
                return ""
            
            # SSE 응답 파싱
            response_text = result.stdout
            logger.debug(f"Raw response: {response_text[:500]}...")
            
            # event-stream에서 data 부분 추출
            content = ""
            for line in response_text.split('\n'):
                if line.startswith('data: '):
                    data_str = line[6:].strip()
                    if data_str and data_str != '[DONE]':
                        try:
                            data = json.loads(data_str)
                            if isinstance(data, dict):
                                # result > content 구조에서 텍스트 추출
                                if "result" in data and "content" in data["result"]:
                                    content_data = data["result"]["content"]
                                    if isinstance(content_data, list) and len(content_data) > 0:
                                        content += content_data[0].get("text", "")
                                    elif isinstance(content_data, dict):
                                        content += content_data.get("text", "")
                        except json.JSONDecodeError:
                            continue
            
            if not content:
                logger.warning(f"No content extracted from {url}")
                logger.debug(f"Full response: {response_text}")
            else:
                logger.info(f"Successfully fetched {len(content)} characters from {url}")
            
            return content
            
        except subprocess.TimeoutExpired:
            logger.error(f"Timeout while fetching {url}")
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
        
        if not html_content.strip():
            return teachers
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # 클래스 정보가 포함된 다양한 요소들 찾기
            potential_elements = soup.find_all(['div', 'article', 'section'], 
                                             class_=re.compile(r'class|card|item|content', re.I))
            
            logger.info(f"Found {len(potential_elements)} potential class elements")
            
            for element in potential_elements:
                try:
                    # 텍스트에서 패턴 매칭으로 정보 추출
                    element_text = element.get_text()
                    
                    # 수강생 수 패턴 (가장 중요한 지표)
                    student_matches = re.findall(r'(\d+,?\d*)\s*명', element_text)
                    if not student_matches:
                        continue
                    
                    students_count = max([int(match.replace(',', '')) for match in student_matches])
                    
                    # 선생님 이름 패턴
                    name_patterns = [
                        r'([가-힣]+(?:코치|쌤|선생|T\b))',
                        r'([가-힣]{2,4})\s*(?:코치|쌤|선생)',
                        r'(\b[가-힣]{2,4})\s+\d+,?\d*명'
                    ]
                    
                    name = "정보없음"
                    for pattern in name_patterns:
                        match = re.search(pattern, element_text)
                        if match:
                            name = match.group(1)
                            break
                    
                    # 클래스 제목 추출 (길고 설명적인 텍스트)
                    sentences = re.split(r'[.!?]', element_text)
                    class_title = "정보없음"
                    for sentence in sentences:
                        if len(sentence.strip()) > 20 and not re.search(r'\d+명', sentence):
                            class_title = sentence.strip()[:100]
                            break
                    
                    # 평점 추출
                    rating_match = re.search(r'(\d+\.\d+)', element_text)
                    rating = float(rating_match.group(1)) if rating_match else 0.0
                    
                    # 강의 수 추출
                    lesson_match = re.search(r'(\d+)강', element_text)
                    lesson_count = int(lesson_match.group(1)) if lesson_match else 0
                    
                    # 월 요금 추출
                    fee_match = re.search(r'(\d+,?\d*)\s*원', element_text)
                    monthly_fee = f"{fee_match.group(1)}원" if fee_match else "정보없음"
                    
                    # URL 추출
                    link = element.find('a', href=True)
                    class_url = ""
                    if link:
                        href = link['href']
                        if href.startswith('/'):
                            class_url = base_url + href
                        else:
                            class_url = href
                    
                    # 최소 조건 확인 (수강생 수가 있으면 추가)
                    if students_count > 0:
                        teacher = TeacherInfo(
                            name=name,
                            subject="일반",
                            class_title=class_title,
                            students_count=students_count,
                            rating=rating,
                            lesson_count=lesson_count,
                            monthly_fee=monthly_fee,
                            class_url=class_url
                        )
                        teachers.append(teacher)
                        logger.debug(f"Added teacher: {name} - {students_count} students")
                        
                except Exception as e:
                    logger.debug(f"Error parsing element: {str(e)}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error parsing HTML: {str(e)}")
            
        logger.info(f"Extracted {len(teachers)} teachers from HTML")
        return teachers
    
    def collect_top_teachers(self) -> List[TeacherInfo]:
        """
        클래스유 사이트에서 TOP 50 선생님을 수집합니다.
        
        Returns:
            TOP 50 선생님 정보 리스트
        """
        urls_to_crawl = [
            "https://www.classu.co.kr/new",
            "https://www.classu.co.kr/new/event/plan/65",  # BEST 클래스
        ]
        
        all_teachers = []
        
        for url in urls_to_crawl:
            try:
                html_content = self.fetch_url_content(url)
                if html_content:
                    teachers = self.parse_class_info(html_content)
                    all_teachers.extend(teachers)
                    logger.info(f"Found {len(teachers)} teachers from {url}")
                
                # 요청 간 딜레이
                time.sleep(3)
                
            except Exception as e:
                logger.error(f"Error collecting from {url}: {str(e)}")
                continue
        
        # 중복 제거 및 정렬
        unique_teachers = {}
        for teacher in all_teachers:
            key = f"{teacher.name}_{teacher.students_count}"
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
    
    def save_results(self, teachers: List[TeacherInfo], filename: str = "classu_top50_simple.json"):
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
                "method": "ToolHive Fetch MCP + Simple Parsing",
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

def main():
    """메인 실행 함수"""
    logger.info("ToolHive Fetch MCP를 활용한 클래스유 TOP 50 선생님 수집 시작 (Simple Version)")
    
    collector = ClassuSimpleFetch()
    
    try:
        # TOP 50 선생님 수집
        top_teachers = collector.collect_top_teachers()
        
        if not top_teachers:
            logger.warning("수집된 선생님 정보가 없습니다.")
            print("\n⚠️ 수집된 데이터가 없습니다. ToolHive fetch MCP 서버 상태를 확인해주세요.")
            return
        
        # 결과 저장
        collector.save_results(top_teachers)
        
        # 콘솔에 요약 출력
        print("\n" + "="*60)
        print("🎉 ToolHive Fetch MCP 수집 완료!")
        print("="*60)
        print(f"📝 수집된 선생님 수: {len(top_teachers)}명")
        print(f"📁 결과 파일: classu_top50_simple.json")
        print("="*60)
        
        # TOP 10 미리보기
        print("\n🏆 TOP 10 선생님 미리보기:")
        for idx, teacher in enumerate(top_teachers[:10], 1):
            print(f"{idx}. {teacher.name} - {teacher.students_count:,}명")
            print(f"   📚 {teacher.class_title[:50]}...")
            if teacher.rating > 0:
                print(f"   ⭐ 평점: {teacher.rating}/5.0")
            print()
        
    except Exception as e:
        logger.error(f"실행 중 오류 발생: {str(e)}")
        raise

if __name__ == "__main__":
    main()
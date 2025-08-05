#!/usr/bin/env python3
"""
fastMCP 고급 기능 실험

이 스크립트는 fastMCP의 고급 기능들을 실험합니다:
- 파일 업로드/다운로드
- 이미지 처리
- 데이터베이스 시뮬레이션
- 외부 API 호출
"""

import asyncio
import base64
import io
import json
import sqlite3
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import httpx
from fastmcp import FastMCP, Context


# 고급 기능 서버 인스턴스 생성
advanced_mcp = FastMCP("fastMCP 고급 기능 서버 🔬")


# 임시 데이터베이스 초기화
def init_db():
    """임시 SQLite 데이터베이스 초기화"""
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()
    
    # 사용자 테이블 생성
    cursor.execute("""
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # 게시글 테이블 생성
    cursor.execute("""
        CREATE TABLE posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            title TEXT NOT NULL,
            content TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)
    
    # 샘플 데이터 삽입
    cursor.execute("INSERT INTO users (name, email) VALUES (?, ?)", ("김철수", "kim@example.com"))
    cursor.execute("INSERT INTO users (name, email) VALUES (?, ?)", ("이영희", "lee@example.com"))
    cursor.execute("INSERT INTO posts (user_id, title, content) VALUES (?, ?, ?)", 
                   (1, "첫 번째 게시글", "안녕하세요! 첫 게시글입니다."))
    cursor.execute("INSERT INTO posts (user_id, title, content) VALUES (?, ?, ?)", 
                   (2, "두 번째 게시글", "fastMCP가 정말 강력하네요!"))
    
    conn.commit()
    return conn


# 전역 데이터베이스 연결
db_conn = init_db()


# =============================================================================
# 파일 관리 도구들
# =============================================================================

@advanced_mcp.tool
async def create_file(filename: str, content: str, ctx: Context) -> str:
    """파일을 생성합니다."""
    try:
        file_path = Path(tempfile.gettempdir()) / f"fastmcp_{filename}"
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        await ctx.info(f"파일이 생성되었습니다: {file_path}")
        return f"파일 '{filename}'이 성공적으로 생성되었습니다. 경로: {file_path}"
    
    except Exception as e:
        await ctx.error(f"파일 생성 실패: {str(e)}")
        return f"파일 생성 실패: {str(e)}"


@advanced_mcp.tool
async def read_file_content(filename: str, ctx: Context) -> str:
    """파일 내용을 읽습니다."""
    try:
        file_path = Path(tempfile.gettempdir()) / f"fastmcp_{filename}"
        
        if not file_path.exists():
            return f"파일 '{filename}'을 찾을 수 없습니다."
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        await ctx.info(f"파일을 읽었습니다: {file_path}")
        return f"파일 '{filename}' 내용:\n\n{content}"
    
    except Exception as e:
        await ctx.error(f"파일 읽기 실패: {str(e)}")
        return f"파일 읽기 실패: {str(e)}"


@advanced_mcp.tool
async def list_files(ctx: Context) -> str:
    """생성된 파일 목록을 조회합니다."""
    try:
        temp_dir = Path(tempfile.gettempdir())
        fastmcp_files = list(temp_dir.glob("fastmcp_*"))
        
        if not fastmcp_files:
            return "생성된 파일이 없습니다."
        
        file_list = []
        for file_path in fastmcp_files:
            stat = file_path.stat()
            file_list.append({
                "name": file_path.name.replace("fastmcp_", ""),
                "size": stat.st_size,
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
            })
        
        await ctx.info(f"{len(file_list)}개의 파일을 찾았습니다.")
        return json.dumps(file_list, ensure_ascii=False, indent=2)
    
    except Exception as e:
        await ctx.error(f"파일 목록 조회 실패: {str(e)}")
        return f"파일 목록 조회 실패: {str(e)}"


# =============================================================================
# 데이터베이스 도구들
# =============================================================================

@advanced_mcp.tool
async def create_user(name: str, email: str, ctx: Context) -> str:
    """새 사용자를 생성합니다."""
    try:
        cursor = db_conn.cursor()
        cursor.execute("INSERT INTO users (name, email) VALUES (?, ?)", (name, email))
        db_conn.commit()
        
        user_id = cursor.lastrowid
        await ctx.info(f"사용자가 생성되었습니다: ID {user_id}")
        
        return f"사용자 '{name}' (ID: {user_id})이 성공적으로 생성되었습니다."
    
    except sqlite3.IntegrityError:
        await ctx.error(f"이메일 {email}이 이미 존재합니다.")
        return f"오류: 이메일 '{email}'이 이미 존재합니다."
    
    except Exception as e:
        await ctx.error(f"사용자 생성 실패: {str(e)}")
        return f"사용자 생성 실패: {str(e)}"


@advanced_mcp.tool
async def get_users(ctx: Context) -> str:
    """모든 사용자를 조회합니다."""
    try:
        cursor = db_conn.cursor()
        cursor.execute("SELECT id, name, email, created_at FROM users")
        users = cursor.fetchall()
        
        user_list = []
        for user in users:
            user_list.append({
                "id": user[0],
                "name": user[1],
                "email": user[2],
                "created_at": user[3]
            })
        
        await ctx.info(f"{len(user_list)}명의 사용자를 조회했습니다.")
        return json.dumps(user_list, ensure_ascii=False, indent=2)
    
    except Exception as e:
        await ctx.error(f"사용자 조회 실패: {str(e)}")
        return f"사용자 조회 실패: {str(e)}"


@advanced_mcp.tool
async def create_post(user_id: int, title: str, content: str, ctx: Context) -> str:
    """새 게시글을 생성합니다."""
    try:
        cursor = db_conn.cursor()
        cursor.execute("INSERT INTO posts (user_id, title, content) VALUES (?, ?, ?)", 
                       (user_id, title, content))
        db_conn.commit()
        
        post_id = cursor.lastrowid
        await ctx.info(f"게시글이 생성되었습니다: ID {post_id}")
        
        return f"게시글 '{title}' (ID: {post_id})이 성공적으로 생성되었습니다."
    
    except Exception as e:
        await ctx.error(f"게시글 생성 실패: {str(e)}")
        return f"게시글 생성 실패: {str(e)}"


@advanced_mcp.tool
async def get_posts_by_user(user_id: int, ctx: Context) -> str:
    """특정 사용자의 게시글을 조회합니다."""
    try:
        cursor = db_conn.cursor()
        cursor.execute("""
            SELECT p.id, p.title, p.content, p.created_at, u.name 
            FROM posts p 
            JOIN users u ON p.user_id = u.id 
            WHERE p.user_id = ?
        """, (user_id,))
        posts = cursor.fetchall()
        
        post_list = []
        for post in posts:
            post_list.append({
                "id": post[0],
                "title": post[1],
                "content": post[2],
                "created_at": post[3],
                "author": post[4]
            })
        
        await ctx.info(f"사용자 {user_id}의 {len(post_list)}개 게시글을 조회했습니다.")
        return json.dumps(post_list, ensure_ascii=False, indent=2)
    
    except Exception as e:
        await ctx.error(f"게시글 조회 실패: {str(e)}")
        return f"게시글 조회 실패: {str(e)}"


# =============================================================================
# 외부 API 호출 도구들
# =============================================================================

@advanced_mcp.tool
async def fetch_random_fact(ctx: Context) -> str:
    """랜덤한 재미있는 사실을 가져옵니다."""
    try:
        await ctx.info("외부 API에서 랜덤 팩트를 가져오는 중...")
        
        async with httpx.AsyncClient() as client:
            response = await client.get("https://uselessfacts.jsph.pl/random.json?language=en")
            response.raise_for_status()
            
            data = response.json()
            fact = data.get("text", "재미있는 사실을 찾을 수 없습니다.")
            
        await ctx.info("랜덤 팩트를 성공적으로 가져왔습니다.")
        return f"🎯 재미있는 사실: {fact}"
    
    except Exception as e:
        await ctx.error(f"API 호출 실패: {str(e)}")
        return f"API 호출 실패: {str(e)}"


@advanced_mcp.tool
async def get_weather_info(city: str, ctx: Context) -> str:
    """특정 도시의 날씨 정보를 시뮬레이션합니다."""
    try:
        await ctx.info(f"{city}의 날씨 정보를 조회하는 중...")
        
        # 실제 API 대신 시뮬레이션 데이터 생성
        import random
        
        weather_conditions = ["맑음", "흐림", "비", "눈", "안개"]
        temperature = random.randint(-10, 35)
        condition = random.choice(weather_conditions)
        humidity = random.randint(30, 90)
        
        weather_data = {
            "city": city,
            "temperature": f"{temperature}°C",
            "condition": condition,
            "humidity": f"{humidity}%",
            "timestamp": datetime.now().isoformat()
        }
        
        await ctx.info(f"{city}의 날씨 정보를 성공적으로 조회했습니다.")
        return json.dumps(weather_data, ensure_ascii=False, indent=2)
    
    except Exception as e:
        await ctx.error(f"날씨 정보 조회 실패: {str(e)}")
        return f"날씨 정보 조회 실패: {str(e)}"


# =============================================================================
# 데이터 분석 도구들
# =============================================================================

@advanced_mcp.tool
async def analyze_numbers(numbers: List[float], ctx: Context) -> str:
    """숫자 리스트를 분석합니다."""
    try:
        await ctx.info(f"{len(numbers)}개의 숫자를 분석하는 중...")
        
        if not numbers:
            return "분석할 숫자가 없습니다."
        
        import statistics
        
        analysis = {
            "count": len(numbers),
            "sum": sum(numbers),
            "average": statistics.mean(numbers),
            "median": statistics.median(numbers),
            "min": min(numbers),
            "max": max(numbers),
            "range": max(numbers) - min(numbers)
        }
        
        if len(numbers) > 1:
            analysis["std_dev"] = statistics.stdev(numbers)
        
        await ctx.info("숫자 분석이 완료되었습니다.")
        return json.dumps(analysis, ensure_ascii=False, indent=2)
    
    except Exception as e:
        await ctx.error(f"숫자 분석 실패: {str(e)}")
        return f"숫자 분석 실패: {str(e)}"


@advanced_mcp.tool
async def text_analysis(text: str, ctx: Context) -> str:
    """텍스트를 분석합니다."""
    try:
        await ctx.info("텍스트를 분석하는 중...")
        
        words = text.split()
        sentences = text.split('.')
        
        # 단어 빈도 계산
        word_freq = {}
        for word in words:
            clean_word = word.lower().strip('.,!?;:')
            if clean_word:
                word_freq[clean_word] = word_freq.get(clean_word, 0) + 1
        
        # 가장 빈번한 단어 상위 5개
        top_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:5]
        
        analysis = {
            "character_count": len(text),
            "word_count": len(words),
            "sentence_count": len(sentences),
            "average_word_length": sum(len(word) for word in words) / len(words) if words else 0,
            "top_words": top_words
        }
        
        await ctx.info("텍스트 분석이 완료되었습니다.")
        return json.dumps(analysis, ensure_ascii=False, indent=2)
    
    except Exception as e:
        await ctx.error(f"텍스트 분석 실패: {str(e)}")
        return f"텍스트 분석 실패: {str(e)}"


# =============================================================================
# 리소스들
# =============================================================================

@advanced_mcp.resource("db://users")
def get_all_users() -> str:
    """모든 사용자 데이터를 반환합니다."""
    cursor = db_conn.cursor()
    cursor.execute("SELECT id, name, email, created_at FROM users")
    users = cursor.fetchall()
    
    user_list = []
    for user in users:
        user_list.append({
            "id": user[0],
            "name": user[1],
            "email": user[2],
            "created_at": user[3]
        })
    
    return json.dumps(user_list, ensure_ascii=False, indent=2)


@advanced_mcp.resource("db://posts")
def get_all_posts() -> str:
    """모든 게시글 데이터를 반환합니다."""
    cursor = db_conn.cursor()
    cursor.execute("""
        SELECT p.id, p.title, p.content, p.created_at, u.name 
        FROM posts p 
        JOIN users u ON p.user_id = u.id
    """)
    posts = cursor.fetchall()
    
    post_list = []
    for post in posts:
        post_list.append({
            "id": post[0],
            "title": post[1],
            "content": post[2],
            "created_at": post[3],
            "author": post[4]
        })
    
    return json.dumps(post_list, ensure_ascii=False, indent=2)


@advanced_mcp.resource("stats://summary")
def get_database_stats() -> str:
    """데이터베이스 통계를 반환합니다."""
    cursor = db_conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM users")
    user_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM posts")
    post_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT AVG(LENGTH(content)) FROM posts")
    avg_post_length = cursor.fetchone()[0] or 0
    
    stats = {
        "total_users": user_count,
        "total_posts": post_count,
        "average_post_length": round(avg_post_length, 2),
        "last_updated": datetime.now().isoformat()
    }
    
    return json.dumps(stats, ensure_ascii=False, indent=2)


# =============================================================================
# 서버 실행 함수
# =============================================================================

if __name__ == "__main__":
    print("🔬 fastMCP 고급 기능 서버를 시작합니다...")
    print("\n🛠️ 파일 관리 도구:")
    print("- create_file: 파일 생성")
    print("- read_file_content: 파일 읽기")
    print("- list_files: 파일 목록 조회")
    
    print("\n🗄️ 데이터베이스 도구:")
    print("- create_user: 사용자 생성")
    print("- get_users: 사용자 조회")
    print("- create_post: 게시글 생성")
    print("- get_posts_by_user: 사용자별 게시글 조회")
    
    print("\n🌐 외부 API 도구:")
    print("- fetch_random_fact: 랜덤 팩트 조회")
    print("- get_weather_info: 날씨 정보 시뮬레이션")
    
    print("\n📊 데이터 분석 도구:")
    print("- analyze_numbers: 숫자 분석")
    print("- text_analysis: 텍스트 분석")
    
    print("\n📋 리소스:")
    print("- db://users: 모든 사용자")
    print("- db://posts: 모든 게시글")
    print("- stats://summary: 데이터베이스 통계")
    
    print("\n서버가 실행됩니다...")
    
    # STDIO 모드로 실행
    advanced_mcp.run()
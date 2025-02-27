# test_db_connection.py
import os
import psycopg2
from dotenv import load_dotenv
# .env 파일에서 환경 변수 로드
load_dotenv()

# 데이터베이스 URL 가져오기
db_url = os.environ.get('DATABASE_URL')
print(f"사용 중인 데이터베이스 URL: {db_url}")

try:
    # 데이터베이스 연결 시도
    conn = psycopg2.connect(db_url)
    
    # 연결 성공 시 커서 생성
    cursor = conn.cursor()
    
    # 간단한 쿼리 실행 (PostgreSQL 버전 확인)
    cursor.execute('SELECT version();')
    
    # 결과 가져오기
    db_version = cursor.fetchone()
    
    # 결과 출력
    print("데이터베이스 연결 성공!")
    print(f"PostgreSQL 버전: {db_version[0]}")
    
    # 커서와 연결 닫기
    cursor.close()
    conn.close()
    
except Exception as e:
    print("데이터베이스 연결 실패:")
    print(e)
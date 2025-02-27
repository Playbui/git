import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """애플리케이션 설정 클래스"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'default-secret-key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = True  # SQL 쿼리 로깅 활성화
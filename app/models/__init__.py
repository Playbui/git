from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from app.config import Config

# 데이터베이스 객체 생성
db = SQLAlchemy()

# 로그인 관리자 생성
login_manager = LoginManager()
login_manager.login_view = 'auth.login'

def create_app(config_class=Config):
    """애플리케이션 팩토리 함수"""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # 확장 초기화
    db.init_app(app)
    login_manager.init_app(app)
    
    # 블루프린트 등록
    from app.routes.auth import auth_bp
    from app.routes.admin import admin_bp
    from app.routes.dashboard import dashboard_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(dashboard_bp)
    
    @app.route('/')
    def index():
        return 'GFEM - GMT 필드 엔지니어 매니징 시스템에 오신 것을 환영합니다!'
    
    return app
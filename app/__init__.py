# app/__init__.py
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from app.config import Config


db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    db.init_app(app)
    login_manager.init_app(app)
    
    # 블루프린트 등록 - 각 블루프린트는 한 번만 등록
    from app.routes.auth import auth_bp
    app.register_blueprint(auth_bp)
    
    from app.routes.admin import admin_bp
    app.register_blueprint(admin_bp)
    
    from app.routes.dashboard import dashboard_bp
    app.register_blueprint(dashboard_bp)

    from app.routes.projects import projects_bp
    app.register_blueprint(projects_bp)

    from app.routes.locations import locations_bp
    app.register_blueprint(locations_bp)

    from app.routes.companies import companies_bp
    app.register_blueprint(companies_bp)

    from app.routes.client_contacts import client_contacts_bp
    app.register_blueprint(client_contacts_bp)
    
    @app.route('/')
    def index():
        return render_template('index.html')
    
    return app
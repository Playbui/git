from app import create_app, db
from app.models.user import User

app = create_app()

with app.app_context():
    # 관리자 사용자가 이미 있는지 확인
    admin = User.query.filter_by(username='admin').first()
    
    if not admin:
        admin = User(
            username='admin',
            name='시스템 관리자',
            email='admin@example.com',
            user_type='admin',
            is_active=True
        )
        admin.set_password('password123')  # 실제 환경에서는 더 안전한 비밀번호 사용
        db.session.add(admin)
        db.session.commit()
        print('관리자 계정이 생성되었습니다!')
    else:
        print('관리자 계정이 이미 존재합니다!')
        
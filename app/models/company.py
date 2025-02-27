from app import db
from datetime import datetime

class Company(db.Model):
    __tablename__ = 'companies'
    
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(200), nullable=False)
    business_number = db.Column(db.String(50))
    company_type = db.Column(db.String(50))
    industry = db.Column(db.String(100))
    address = db.Column(db.Text)
    postal_code = db.Column(db.String(20))
    region = db.Column(db.String(100))
    main_phone = db.Column(db.String(20))
    main_email = db.Column(db.String(100))
    website = db.Column(db.String(255))
    logo_url = db.Column(db.String(255))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 직접적인 관계 설정을 제거하고 대신 메서드 사용
    def get_contacts(self):
        from app.models.user import User
        return User.query.filter_by(company=self.company_name, user_type='client').all()
    
    def __repr__(self):
        return f'<Company {self.id}: {self.company_name}>'
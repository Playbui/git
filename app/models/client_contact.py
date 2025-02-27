from app import db
from datetime import datetime

class ClientContact(db.Model):
    __tablename__ = 'client_contacts'
    
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    location_id = db.Column(db.Integer, db.ForeignKey('locations.id'))
    department = db.Column(db.String(100))
    name = db.Column(db.String(100), nullable=False)
    position = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 관계 설정
    company = db.relationship('Company', backref='contacts')
    location = db.relationship('Location', backref='client_contacts')
    
    def __repr__(self):
        return f'<ClientContact {self.id}: {self.name}>'
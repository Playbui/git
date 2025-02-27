from app import db
from datetime import datetime

# 장소-담당자 연결 테이블 (다대다 관계)
location_managers = db.Table('location_managers',
    db.Column('location_id', db.Integer, db.ForeignKey('locations.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('created_at', db.DateTime, default=datetime.utcnow)
)

# 장소-클라이언트 연결 테이블 (다대다 관계)
location_clients = db.Table('location_clients',
    db.Column('location_id', db.Integer, db.ForeignKey('locations.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('created_at', db.DateTime, default=datetime.utcnow)
)

class Location(db.Model):
    __tablename__ = 'locations'
    
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'))  # 거래처 ID 추가
    location_name = db.Column(db.String(200), nullable=False)
    region = db.Column(db.String(100), nullable=False)
    district = db.Column(db.String(100))
    city = db.Column(db.String(100))
    work_type = db.Column(db.String(100))
    safety_bureau_name = db.Column(db.String(100))
    relay_station = db.Column(db.String(100))
    address = db.Column(db.Text, nullable=False)
    address_detail = db.Column(db.Text)
    postal_code = db.Column(db.String(20))
    contact_person = db.Column(db.String(100))
    office_phone = db.Column(db.String(20))
    contact_phone = db.Column(db.String(20))
    latitude = db.Column(db.Numeric(10, 8))
    longitude = db.Column(db.Numeric(11, 8))
    access_info = db.Column(db.Text)
    special_instructions = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 관계 설정
    company = db.relationship('Company', backref='locations')
    managers = db.relationship('User', secondary=location_managers, 
                              backref=db.backref('managed_locations', lazy='dynamic'))
    clients = db.relationship('User', secondary=location_clients,
                             backref=db.backref('client_locations', lazy='dynamic'))
    
    def __repr__(self):
        return f'<Location {self.id}: {self.location_name}>'
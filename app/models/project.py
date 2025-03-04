from app import db
from datetime import datetime
from sqlalchemy.orm import relationship

# 프로젝트-장소 연결 테이블 (다대다 관계)
project_locations = db.Table(
    'project_locations',
    db.Column('project_id', db.Integer, db.ForeignKey('projects.id'), primary_key=True),
    db.Column('location_id', db.Integer, db.ForeignKey('locations.id'), primary_key=True)
)

class Project(db.Model):
    __tablename__ = 'projects'
    
    id = db.Column(db.Integer, primary_key=True)
    project_year = db.Column(db.Integer, nullable=False)
    project_code = db.Column(db.String(50), nullable=False, unique=True)
    project_name = db.Column(db.String(100), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    budget = db.Column(db.Float)
    client_company_id = db.Column(db.Integer, db.ForeignKey('companies.id'))
    client_contact_id = db.Column(db.Integer, db.ForeignKey('client_contacts.id'))
    department_in_charge = db.Column(db.String(100))
    pm_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    status = db.Column(db.String(20), default='planning')
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 관계 정의
    client_company = relationship('Company', foreign_keys=[client_company_id])
    client_contact = relationship('ClientContact', foreign_keys=[client_contact_id])
    pm = relationship('User', foreign_keys=[pm_id])
    
    # 다대다 관계 (프로젝트-장소)
    locations = relationship('Location', secondary=project_locations, lazy='dynamic',
                            backref=db.backref('projects', lazy='dynamic'))
    
    def __init__(self, project_year, project_name, project_code, start_date, end_date, 
                 client_company_id=None, client_contact_id=None, department_in_charge=None, 
                 pm_id=None, status='planning', budget=None, description=None):
        self.project_year = project_year
        self.project_name = project_name
        self.project_code = project_code
        self.start_date = start_date
        self.end_date = end_date
        self.client_company_id = client_company_id
        self.client_contact_id = client_contact_id
        self.department_in_charge = department_in_charge
        self.pm_id = pm_id
        self.status = status
        self.budget = budget
        self.description = description
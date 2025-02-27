from app import db
from datetime import datetime

class Project(db.Model):
    __tablename__ = 'projects'
    
    id = db.Column(db.Integer, primary_key=True)
    project_year = db.Column(db.Integer, nullable=False)
    project_name = db.Column(db.String(255), nullable=False)
    project_code = db.Column(db.String(50), nullable=False, unique=True)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    budget = db.Column(db.Numeric(15, 2))
    client_name = db.Column(db.String(100), nullable=False)
    client_contact_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    department_in_charge = db.Column(db.String(100))
    pm_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    status = db.Column(db.String(20), default='planning')
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 관계 설정
    pm = db.relationship('User', foreign_keys=[pm_id], backref='managed_projects')
    client_contact = db.relationship('User', foreign_keys=[client_contact_id], backref='client_projects')
    locations = db.relationship('Location', secondary='project_locations', backref='projects')
    
    def __repr__(self):
        return f'<Project {self.project_code}: {self.project_name}>'
    
project_location = db.Table('project_locations',
    db.Column('project_id', db.Integer, db.ForeignKey('projects.id'), primary_key=True),
    db.Column('location_id', db.Integer, db.ForeignKey('locations.id'), primary_key=True),
    db.Column('created_at', db.DateTime, default=datetime.utcnow)
)
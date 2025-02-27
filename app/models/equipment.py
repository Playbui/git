from app import db
from datetime import datetime

class Equipment(db.Model):
    __tablename__ = 'equipment'
    
    id = db.Column(db.Integer, primary_key=True)
    location_id = db.Column(db.Integer, db.ForeignKey('locations.id'), nullable=False)
    equipment_group = db.Column(db.String(100), nullable=False)
    equipment_name = db.Column(db.String(255), nullable=False)
    hostname = db.Column(db.String(100))
    ip_address = db.Column(db.String(15))
    equipment_type = db.Column(db.String(100))
    manufacturer = db.Column(db.String(100))
    model_number = db.Column(db.String(100))
    os_type = db.Column(db.String(100))
    os_version = db.Column(db.String(50))
    serial_number = db.Column(db.String(100))
    installation_date = db.Column(db.Date)
    warranty_end_date = db.Column(db.Date)
    maintenance_cycle = db.Column(db.String(50))
    status = db.Column(db.String(50), default='active')
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Equipment {self.id}: {self.equipment_name}>'
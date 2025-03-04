from app import db
from datetime import datetime


class EquipmentAttributeDefinition(db.Model):
    __tablename__ = 'equipment_attribute_definitions'
    
    id = db.Column(db.Integer, primary_key=True)
    equipment_group = db.Column(db.String(100), nullable=False)
    attribute_name = db.Column(db.String(100), nullable=False)
    attribute_label = db.Column(db.String(100), nullable=False)
    attribute_type = db.Column(db.String(50), nullable=False)  # text, number, date, select, etc.
    required = db.Column(db.Boolean, default=False)
    options = db.Column(db.Text)  # JSON string for select options
    default_value = db.Column(db.String(255))
    display_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<EquipmentAttributeDefinition {self.equipment_group}.{self.attribute_name}>'

class EquipmentAttribute(db.Model):
    __tablename__ = 'equipment_attributes'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.id'), nullable=False)
    definition_id = db.Column(db.Integer, db.ForeignKey('equipment_attribute_definitions.id'), nullable=False)
    attribute_value = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 관계 설정
    equipment = db.relationship('Equipment', backref='attributes')
    definition = db.relationship('EquipmentAttributeDefinition')
    
    def __repr__(self):
        return f'<EquipmentAttribute {self.definition.attribute_name}: {self.attribute_value}>'
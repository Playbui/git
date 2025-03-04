from app import db
from datetime import datetime
import json

class EquipmentGroup(db.Model):
    """장비 그룹 모델 - 장비의 카테고리(서버, 무전기 등)를 정의합니다"""
    __tablename__ = 'equipment_groups'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 관계 설정
    equipment = db.relationship('Equipment', backref='group', lazy='dynamic')
    attributes = db.relationship('app.models.equipment.EquipmentAttribute', backref='group', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<EquipmentGroup {self.id}: {self.name}>'

class EquipmentAttribute(db.Model):
    """장비 그룹에 속한 커스텀 속성을 정의합니다"""
    __tablename__ = 'equipment_attributes'
    
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('equipment_groups.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    label = db.Column(db.String(100), nullable=False)  # 화면에 표시될 이름
    field_type = db.Column(db.String(50), nullable=False)  # text, number, date, select 등
    required = db.Column(db.Boolean, default=False)
    options = db.Column(db.Text)  # select 타입인 경우 옵션 목록(JSON)
    order = db.Column(db.Integer, default=1)  # 표시 순서
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 그룹 내에서 속성명 중복 방지
    __table_args__ = (
        db.UniqueConstraint('group_id', 'name', name='uq_attribute_group_name'),
    )
    
    def __repr__(self):
        return f'<EquipmentAttribute {self.id}: {self.name}>'
    
    def get_options_list(self):
        """옵션 문자열을 파이썬 리스트로 변환"""
        if self.options:
            try:
                return json.loads(self.options)
            except:
                return []
        return []

class Equipment(db.Model):
    """장비 모델"""
    __tablename__ = 'equipment'
    
    id = db.Column(db.Integer, primary_key=True)
    location_id = db.Column(db.Integer, db.ForeignKey('locations.id'), nullable=False)
    equipment_group_id = db.Column(db.Integer, db.ForeignKey('equipment_groups.id'), nullable=False)
    equipment_name = db.Column(db.String(255), nullable=False)
    serial_number = db.Column(db.String(100))
    manufacturer = db.Column(db.String(100))
    model_number = db.Column(db.String(100))
    installation_date = db.Column(db.Date)
    warranty_end_date = db.Column(db.Date)
    status = db.Column(db.String(50), default='active')
    notes = db.Column(db.Text)
    custom_attributes = db.Column(db.Text)  # JSON 형태로 저장된 커스텀 속성값
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Equipment {self.id}: {self.equipment_name}>'
    
    def get_custom_attributes(self):
        """커스텀 속성을 딕셔너리로 반환"""
        if self.custom_attributes:
            try:
                return json.loads(self.custom_attributes)
            except:
                return {}
        return {}
    
    def set_custom_attributes(self, attributes_dict):
        """커스텀 속성을 JSON 문자열로 저장"""
        self.custom_attributes = json.dumps(attributes_dict)
    
    def get_attribute_value(self, attribute_name):
        """특정 커스텀 속성의 값을 가져오는 편의 메서드"""
        attrs = self.get_custom_attributes()
        return attrs.get(attribute_name)
    
    def get_formatted_attributes(self):
        """커스텀 속성을 포맷팅하여 반환"""
        attrs = self.get_custom_attributes()
        result = {}
        
        # 이 장비 그룹에 정의된 모든 속성 가져오기
        group_attributes = EquipmentAttribute.query.filter_by(group_id=self.equipment_group_id).all()
        
        # 각 속성 정의를 result에 추가
        for attr_def in group_attributes:
            result[attr_def.name] = {
                'label': attr_def.label,
                'value': attrs.get(attr_def.name, ''),
                'type': attr_def.field_type
            }
            
        return result
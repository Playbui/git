from app import db

# 모델 임포트
from app.models.user import User
from app.models.company import Company
from app.models.project import Project
from app.models.location import Location
from app.models.client_contact import ClientContact
from app.models.equipment import Equipment, EquipmentGroup, EquipmentAttribute
from app.models.equipment_attribute import EquipmentAttributeDefinition, EquipmentAttribute as EqAttr
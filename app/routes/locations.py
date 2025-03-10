from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from sqlalchemy import or_
from app import db
from app.models.location import Location, location_managers, location_clients
from app.models.company import Company
from app.models.user import User
from app.forms import LocationForm, EquipmentForm
from app.models.equipment import Equipment, EquipmentAttribute, EquipmentGroup
from datetime import datetime
import json

locations_bp = Blueprint('locations', __name__, url_prefix='/locations')

@locations_bp.route('/')
@login_required
def index():
    # 검색어 파라미터 받기
    search_query = request.args.get('search', '').strip()
    
    if search_query:
        # 다양한 필드에서 검색
        locations = Location.query.join(Company).filter(
            or_(
                Location.location_name.ilike(f'%{search_query}%'),
                Location.region.ilike(f'%{search_query}%'),
                Location.work_type.ilike(f'%{search_query}%'),
                Location.safety_bureau_name.ilike(f'%{search_query}%'),
                Location.relay_station.ilike(f'%{search_query}%'),
                Location.address.ilike(f'%{search_query}%'),
                Company.company_name.ilike(f'%{search_query}%')  # 거래처명으로 검색
            )
        ).all()
    else:
        # 검색어 없으면 모든 위치 조회
        locations = Location.query.all()
    
    return render_template('locations/index.html', locations=locations, search_query=search_query)

@locations_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    form = LocationForm()
    
    if form.validate_on_submit():
        try:
            new_location = Location(
                company_id=form.company_id.data,
                location_name=form.location_name.data,
                region=form.region.data,
                work_type=form.work_type.data,
                safety_bureau_name=form.safety_bureau_name.data,
                relay_station=form.relay_station.data,
                address=form.address.data,
                office_phone=form.office_phone.data,
                special_instructions=form.special_instructions.data
            )
            
            # 본사 담당자 연결
            if form.manager_ids.data:
                for user_id in form.manager_ids.data:
                    user = User.query.get(user_id)
                    if user:
                        new_location.managers.append(user)
            
            # 거래처 담당자 연결
            if form.client_ids.data:
                for user_id in form.client_ids.data:
                    user = User.query.get(user_id)
                    if user:
                        new_location.clients.append(user)
            
            # 디버깅: 생성되는 객체 정보 출력
            print(f"새 장소 생성: {new_location.location_name}")
            
            db.session.add(new_location)
            db.session.commit()
            
            flash('장소가 성공적으로 등록되었습니다.', 'success')
            return redirect(url_for('locations.index'))
        except Exception as e:
            db.session.rollback()
            print(f"오류 발생: {str(e)}")
            flash(f'장소 등록 중 오류가 발생했습니다: {str(e)}', 'danger')
    
    return render_template('locations/create.html', form=form)

@locations_bp.route('/<int:id>')
@login_required
def view(id):
    location = Location.query.get_or_404(id)
    return render_template('locations/detail.html', location=location)

@locations_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    location = Location.query.get_or_404(id)
    form = LocationForm(obj=location)
    
    if request.method == 'GET':
        # 폼 로드 시 기존 담당자들 선택
        form.manager_ids.data = [user.id for user in location.managers]
        form.client_ids.data = [user.id for user in location.clients]
    
    if form.validate_on_submit():
        try:
            # 폼에서 데이터 가져와서 업데이트
            form.populate_obj(location)
            
            # 담당자 관계 업데이트
            # 1. 기존 담당자 관계 삭제
            location.managers.clear()
            location.clients.clear()
            
            # 2. 새로운 담당자 관계 설정
            if form.manager_ids.data:
                for user_id in form.manager_ids.data:
                    user = User.query.get(user_id)
                    if user:
                        location.managers.append(user)
            
            if form.client_ids.data:
                for user_id in form.client_ids.data:
                    user = User.query.get(user_id)
                    if user:
                        location.clients.append(user)
            
            # DB에 저장
            db.session.commit()
            
            flash('장소 정보가 성공적으로 업데이트되었습니다.', 'success')
            return redirect(url_for('locations.view', id=location.id))
        except Exception as e:
            db.session.rollback()
            print(f"오류 발생: {str(e)}")
            flash(f'장소 정보 업데이트 중 오류가 발생했습니다: {str(e)}', 'danger')
    
    return render_template('locations/edit.html', form=form, location=location)

@locations_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    location = Location.query.get_or_404(id)
    
    try:
        # 관련된 담당자 연결 삭제
        location.managers.clear()
        location.clients.clear()
        
        # 장소 삭제
        db.session.delete(location)
        db.session.commit()
        
        flash('장소가 성공적으로 삭제되었습니다.', 'success')
    except Exception as e:
        db.session.rollback()
        print(f"오류 발생: {str(e)}")
        flash(f'장소 삭제 중 오류가 발생했습니다. 관련된 데이터가 있을 수 있습니다: {str(e)}', 'danger')
    
    return redirect(url_for('locations.index'))

@locations_bp.route('/equipment/<int:equipment_id>')
@login_required
def equipment_detail(equipment_id):
    equipment = Equipment.query.get_or_404(equipment_id)
    return render_template('locations/equipment_detail.html', equipment=equipment)

@locations_bp.route('/equipment/<int:equipment_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_equipment(equipment_id):
    equipment = Equipment.query.get_or_404(equipment_id)
    form = EquipmentForm(obj=equipment)
    
    if form.validate_on_submit():
        try:
            form.populate_obj(equipment)
            db.session.commit()
            
            flash('장비 정보가 성공적으로 업데이트되었습니다.', 'success')
            return redirect(url_for('locations.equipment_detail', equipment_id=equipment.id))
        except Exception as e:
            db.session.rollback()
            print(f"오류 발생: {str(e)}")
            flash(f'장비 정보 업데이트 중 오류가 발생했습니다: {str(e)}', 'danger')
    
    return render_template('locations/edit_equipment.html', form=form, equipment=equipment)

@locations_bp.route('/<int:location_id>/equipment/create', methods=['GET', 'POST'])
@login_required
def create_equipment(location_id):
    location = Location.query.get_or_404(location_id)
    form = EquipmentForm()
    
    # 장비 그룹 목록 가져오기
    equipment_groups = EquipmentGroup.query.all()
    
    if request.method == 'POST':
        if form.validate_on_submit():
            try:
                # 새 장비 생성
                new_equipment = Equipment(
                    location_id=location.id,
                    equipment_group_id=form.equipment_group_id.data,
                    equipment_name=form.equipment_name.data,
                    manufacturer=form.manufacturer.data,
                    model_number=form.model_number.data,
                    serial_number=form.serial_number.data,
                    installation_date=form.installation_date.data,
                    warranty_end_date=form.warranty_end_date.data,
                    status=form.status.data,
                    notes=form.notes.data
                )
                
                db.session.add(new_equipment)
                db.session.commit()
                
                flash('장비가 성공적으로 등록되었습니다.', 'success')
                return redirect(url_for('locations.view', id=location.id))
            except Exception as e:
                db.session.rollback()
                print(f"오류 발생: {str(e)}")
                flash(f'장비 등록 중 오류가 발생했습니다: {str(e)}', 'danger')
    
    return render_template(
        'locations/create_equipment.html', 
        form=form, 
        location=location, 
        equipment_groups=equipment_groups
    )

@locations_bp.route('/api/equipment-attributes/<int:group_id>')
@login_required
def get_equipment_attributes(group_id):
    # 해당 장비 그룹의 속성 정의 목록 가져오기
    group = EquipmentGroup.query.get_or_404(group_id)
    attributes = EquipmentAttribute.query.filter_by(
        group_id=group.id
    ).order_by(EquipmentAttribute.order).all()
    
    attributes_list = []
    for attr in attributes:
        attr_data = {
            'id': attr.id,
            'name': attr.name,
            'label': attr.label,
            'type': attr.field_type,
            'required': attr.required,
            'options': attr.get_options_list()
        }
        attributes_list.append(attr_data)
    
    return jsonify(attributes_list)
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.equipment import Equipment, EquipmentGroup, EquipmentAttribute
from app.forms import EquipmentGroupForm, EquipmentAttributeForm, EquipmentForm
from app.models.location import Location
import json

equipment_bp = Blueprint('equipment', __name__, url_prefix='/equipment')

# 장비 그룹 관리
@equipment_bp.route('/groups')
@login_required
def group_list():
    """장비 그룹 목록 페이지"""
    # 필요한 테이블 존재 여부 확인
    try:
        # 테이블이 존재하는지 확인 (예외 발생시 테이블이 없는 것)
        groups = EquipmentGroup.query.order_by(EquipmentGroup.name).all()
        return render_template('equipment/group_list.html', groups=groups)
    except Exception as e:
        # 데이터베이스 관련 오류 발생시 오류 페이지로 리디렉션
        print(f"데이터베이스 오류: {str(e)}")
        return render_template('equipment/error_page.html')

@equipment_bp.route('/groups/create', methods=['GET', 'POST'])
@login_required
def create_group():
    """장비 그룹 생성 페이지"""
    form = EquipmentGroupForm()
    
    if form.validate_on_submit():
        try:
            group = EquipmentGroup(
                name=form.name.data,
                description=form.description.data
            )
            db.session.add(group)
            db.session.commit()
            
            flash('장비 그룹이 성공적으로 생성되었습니다.', 'success')
            return redirect(url_for('equipment.group_detail', id=group.id))
        except Exception as e:
            db.session.rollback()
            flash(f'장비 그룹 생성 중 오류가 발생했습니다: {str(e)}', 'danger')
    
    return render_template('equipment/group_create.html', form=form)

@equipment_bp.route('/groups/<int:id>')
@login_required
def group_detail(id):
    """장비 그룹 상세 페이지"""
    try:
        group = EquipmentGroup.query.get_or_404(id)
        attributes = group.attributes.order_by(EquipmentAttribute.order).all() if group.attributes else []
        equipment_count = group.equipment.count() if group.equipment else 0
        
        return render_template('equipment/group_detail.html', 
                            group=group, 
                            attributes=attributes, 
                            equipment_count=equipment_count)
    except Exception as e:
        flash(f'장비 그룹 정보를 불러오는 중 오류가 발생했습니다: {str(e)}', 'danger')
        return redirect(url_for('equipment.group_list'))

@equipment_bp.route('/groups/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_group(id):
    """장비 그룹 수정 페이지"""
    try:
        group = EquipmentGroup.query.get_or_404(id)
        form = EquipmentGroupForm(obj=group)
        
        if form.validate_on_submit():
            try:
                form.populate_obj(group)
                db.session.commit()
                
                flash('장비 그룹이 성공적으로 업데이트되었습니다.', 'success')
                return redirect(url_for('equipment.group_detail', id=group.id))
            except Exception as e:
                db.session.rollback()
                flash(f'장비 그룹 업데이트 중 오류가 발생했습니다: {str(e)}', 'danger')
        
        return render_template('equipment/group_edit.html', form=form, group=group)
    except Exception as e:
        flash(f'장비 그룹 수정 페이지를 불러오는 중 오류가 발생했습니다: {str(e)}', 'danger')
        return redirect(url_for('equipment.group_list'))

@equipment_bp.route('/groups/<int:id>/delete', methods=['POST'])
@login_required
def delete_group(id):
    """장비 그룹 삭제"""
    group = EquipmentGroup.query.get_or_404(id)
    
    if group.equipment.count() > 0:
        flash('이 그룹에 장비가 등록되어 있어 삭제할 수 없습니다.', 'danger')
        return redirect(url_for('equipment.group_detail', id=group.id))
    
    try:
        db.session.delete(group)
        db.session.commit()
        flash('장비 그룹이 성공적으로 삭제되었습니다.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'장비 그룹 삭제 중 오류가 발생했습니다: {str(e)}', 'danger')
    
    return redirect(url_for('equipment.group_list'))

# 장비 그룹 속성 관리
@equipment_bp.route('/groups/<int:group_id>/attributes/create', methods=['GET', 'POST'])
@login_required
def create_attribute(group_id):
    """장비 그룹 속성 생성 페이지"""
    try:
        group = EquipmentGroup.query.get_or_404(group_id)
        form = EquipmentAttributeForm()
        
        if form.validate_on_submit():
            try:
                # 같은 이름의 속성이 이미 있는지 확인
                existing_attr = EquipmentAttribute.query.filter_by(
                    group_id=group.id, 
                    name=form.name.data
                ).first()
                
                if existing_attr:
                    flash(f'이미 같은 이름의 속성이 존재합니다: {form.name.data}', 'danger')
                    return render_template('equipment/attribute_create.html', form=form, group=group)
                
                # 옵션 값 처리
                options = None
                if form.field_type.data == 'select' and form.options.data:
                    options_list = [opt.strip() for opt in form.options.data.split('\n') if opt.strip()]
                    options = json.dumps(options_list)
                
                # order 값이 지정되지 않은 경우 자동 할당 (가장 큰 값 + 1)
                order = form.order.data
                if not order:
                    max_order = db.session.query(db.func.max(EquipmentAttribute.order)).filter_by(group_id=group.id).scalar()
                    order = 1 if max_order is None else max_order + 1
                
                attribute = EquipmentAttribute(
                    group_id=group.id,
                    name=form.name.data,
                    label=form.label.data,
                    field_type=form.field_type.data,
                    required=form.required.data,
                    options=options,
                    order=order
                )
                
                db.session.add(attribute)
                db.session.commit()
                
                flash('속성이 성공적으로 추가되었습니다.', 'success')
                return redirect(url_for('equipment.group_detail', id=group.id))
            except Exception as e:
                db.session.rollback()
                flash(f'속성 추가 중 오류가 발생했습니다: {str(e)}', 'danger')
        
        return render_template('equipment/attribute_create.html', form=form, group=group)
    except Exception as e:
        flash(f'속성 생성 페이지를 불러오는 중 오류가 발생했습니다: {str(e)}', 'danger')
        return redirect(url_for('equipment.group_detail', id=group_id))

@equipment_bp.route('/attributes/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_attribute(id):
    """장비 그룹 속성 수정 페이지"""
    try:
        attribute = EquipmentAttribute.query.get_or_404(id)
        group = attribute.group
        
        # 옵션 값 처리
        if attribute.options:
            try:
                options_list = json.loads(attribute.options)
                options_text = '\n'.join(options_list)
            except:
                options_text = ''
        else:
            options_text = ''
        
        form = EquipmentAttributeForm(obj=attribute)
        form.options.data = options_text
        
        if form.validate_on_submit():
            try:
                # 같은 이름의 다른 속성이 이미 있는지 확인 (자신 제외)
                existing_attr = EquipmentAttribute.query.filter(
                    EquipmentAttribute.group_id == group.id,
                    EquipmentAttribute.name == form.name.data,
                    EquipmentAttribute.id != attribute.id
                ).first()
                
                if existing_attr:
                    flash(f'이미 같은 이름의 속성이 존재합니다: {form.name.data}', 'danger')
                    return render_template('equipment/attribute_edit.html', form=form, attribute=attribute, group=group)
                
                # 기본 필드 값 업데이트
                attribute.name = form.name.data
                attribute.label = form.label.data
                attribute.field_type = form.field_type.data
                attribute.required = form.required.data
                
                # order 값이 변경된 경우
                if form.order.data != attribute.order:
                    attribute.order = form.order.data or 1
                
                # 옵션 값 처리
                if form.field_type.data == 'select' and form.options.data:
                    options_list = [opt.strip() for opt in form.options.data.split('\n') if opt.strip()]
                    attribute.options = json.dumps(options_list)
                else:
                    attribute.options = None
                
                db.session.commit()
                
                flash('속성이 성공적으로 업데이트되었습니다.', 'success')
                return redirect(url_for('equipment.group_detail', id=group.id))
            except Exception as e:
                db.session.rollback()
                flash(f'속성 업데이트 중 오류가 발생했습니다: {str(e)}', 'danger')
        
        return render_template('equipment/attribute_edit.html', form=form, attribute=attribute, group=group)
    except Exception as e:
        flash(f'속성 수정 페이지를 불러오는 중 오류가 발생했습니다: {str(e)}', 'danger')
        return redirect(url_for('equipment.group_list'))

@equipment_bp.route('/attributes/<int:id>/delete', methods=['POST'])
@login_required
def delete_attribute(id):
    """장비 그룹 속성 삭제"""
    attribute = EquipmentAttribute.query.get_or_404(id)
    group_id = attribute.group_id
    
    try:
        db.session.delete(attribute)
        db.session.commit()
        flash('속성이 성공적으로 삭제되었습니다.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'속성 삭제 중 오류가 발생했습니다: {str(e)}', 'danger')
    
    return redirect(url_for('equipment.group_detail', id=group_id))

# 장비 관리
@equipment_bp.route('/list')
@login_required
def list():
    """장비 목록 페이지"""
    try:
        # 검색어 처리
        search_query = request.args.get('search', '').strip()
        group_id = request.args.get('group_id', 0, type=int)
        location_id = request.args.get('location_id', 0, type=int)
        
        # 기본 쿼리 설정
        query = Equipment.query
        
        # 필터 적용
        if group_id > 0:
            query = query.filter(Equipment.equipment_group_id == group_id)
        
        if location_id > 0:
            query = query.filter(Equipment.location_id == location_id)
        
        if search_query:
            query = query.filter(Equipment.equipment_name.ilike(f'%{search_query}%'))
        
        # 정렬 및 실행
        equipment_list = query.order_by(Equipment.equipment_name).all()
        
        # 선택 옵션 데이터 준비
        groups = EquipmentGroup.query.order_by(EquipmentGroup.name).all()
        locations = Location.query.order_by(Location.location_name).all()
        
        return render_template('equipment/list.html', 
                            equipment_list=equipment_list,
                            groups=groups,
                            locations=locations,
                            search_query=search_query,
                            selected_group_id=group_id,
                            selected_location_id=location_id)
    except Exception as e:
        # 데이터베이스 관련 오류 발생시 오류 페이지로 리디렉션
        print(f"데이터베이스 오류: {str(e)}")
        return render_template('equipment/error_page.html')

@equipment_bp.route('/location/<int:location_id>')
@login_required
def location_equipment(location_id):
    """특정 장소의 장비 목록 페이지"""
    location = Location.query.get_or_404(location_id)
    equipment_list = Equipment.query.filter_by(location_id=location_id).all()
    
    # 장비 그룹 목록 조회 (필터링용)
    groups = EquipmentGroup.query.order_by(EquipmentGroup.name).all()
    
    return render_template('equipment/location_equipment.html', 
                          location=location, 
                          equipment_list=equipment_list,
                          groups=groups)

@equipment_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """장비 생성 페이지"""
    # 장소 ID 가져오기
    location_id = request.args.get('location_id', 0, type=int)
    if not location_id:
        flash('장비 등록을 위해 장소를 선택해주세요.', 'warning')
        return redirect(url_for('equipment.list'))
        
    location = Location.query.get_or_404(location_id)
    
    # 그룹 ID 가져오기
    group_id = request.args.get('group_id', 0, type=int)
    equipment_group = None
    
    if group_id > 0:
        equipment_group = EquipmentGroup.query.get(group_id)
    
    form = EquipmentForm(equipment_group=equipment_group)
    
    if form.validate_on_submit():
        try:
            # 선택된 그룹 확인
            selected_group_id = form.equipment_group_id.data
            if selected_group_id == 0:
                flash('올바른 장비 그룹을 선택해주세요.', 'danger')
                return render_template('equipment/create.html', form=form, location=location)
            
            # 이전에 선택된 그룹과 다른 그룹이 선택된 경우 해당 그룹으로 진행
            # 리다이렉트 하지 않고 현재 폼 정보로 진행
            if equipment_group and equipment_group.id != selected_group_id:
                new_group = EquipmentGroup.query.get(selected_group_id)
                equipment_group = new_group
            
            # 새 장비 객체 생성
            new_equipment = Equipment(
                location_id=location.id,
                equipment_group_id=selected_group_id,
                equipment_name=form.equipment_name.data,
                manufacturer=form.manufacturer.data,
                model_number=form.model_number.data,
                serial_number=form.serial_number.data,
                installation_date=form.installation_date.data,
                warranty_end_date=form.warranty_end_date.data,
                status=form.status.data,
                notes=form.notes.data
            )
            
            # 커스텀 속성 수집
            group = EquipmentGroup.query.get(selected_group_id)
            custom_attributes = {}
            
            for attr in group.attributes.all():
                field_name = f'custom_{attr.name}'
                if hasattr(form, field_name):
                    value = getattr(form, field_name).data
                    custom_attributes[attr.name] = value
            
            # 커스텀 속성 저장
            new_equipment.set_custom_attributes(custom_attributes)
            
            db.session.add(new_equipment)
            db.session.commit()
            
            flash('장비가 성공적으로 추가되었습니다.', 'success')
            return redirect(url_for('equipment.location_equipment', location_id=location.id))
        except Exception as e:
            db.session.rollback()
            flash(f'장비 추가 중 오류가 발생했습니다: {str(e)}', 'danger')
    
    return render_template('equipment/create.html', form=form, location=location, equipment_group=equipment_group)

@equipment_bp.route('/<int:id>')
@login_required
def detail(id):
    """장비 상세 페이지"""
    try:
        equipment = Equipment.query.get_or_404(id)
        group = equipment.group
        custom_attributes = equipment.get_custom_attributes()
        
        # 해당 그룹의 속성 정보 가져오기
        group_attributes = group.attributes.order_by(EquipmentAttribute.order).all()
        
        return render_template('equipment/detail.html', 
                            equipment=equipment, 
                            group=group,
                            group_attributes=group_attributes,
                            custom_attributes=custom_attributes)
    except Exception as e:
        flash(f'장비 정보를 불러오는 중 오류가 발생했습니다: {str(e)}', 'danger')
        return redirect(url_for('equipment.list'))

@equipment_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    """장비 수정 페이지"""
    try:
        equipment = Equipment.query.get_or_404(id)
        group = equipment.group
        
        # 폼 생성 및 데이터 채우기
        form = EquipmentForm(obj=equipment, equipment_group=group)
        
        # GET 요청 시 커스텀 속성 값 채우기
        if request.method == 'GET':
            custom_attributes = equipment.get_custom_attributes()
            
            for attr in group.attributes.all():
                field_name = f'custom_{attr.name}'
                if hasattr(form, field_name) and attr.name in custom_attributes:
                    field = getattr(form, field_name)
                    field.data = custom_attributes[attr.name]
        
        if form.validate_on_submit():
            try:
                # 폼에서 기본 데이터 업데이트
                form.populate_obj(equipment)
                
                # 커스텀 속성 업데이트
                custom_attributes = {}
                
                for attr in group.attributes.all():
                    field_name = f'custom_{attr.name}'
                    if hasattr(form, field_name):
                        value = getattr(form, field_name).data
                        custom_attributes[attr.name] = value
                
                equipment.set_custom_attributes(custom_attributes)
                
                db.session.commit()
                
                flash('장비 정보가 성공적으로 업데이트되었습니다.', 'success')
                return redirect(url_for('equipment.detail', id=equipment.id))
            except Exception as e:
                db.session.rollback()
                flash(f'장비 정보 업데이트 중 오류가 발생했습니다: {str(e)}', 'danger')
        
        return render_template('equipment/edit.html', 
                            form=form, 
                            equipment=equipment, 
                            group=group)
    except Exception as e:
        flash(f'장비 수정 페이지를 불러오는 중 오류가 발생했습니다: {str(e)}', 'danger')
        return redirect(url_for('equipment.list'))

@equipment_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    """장비 삭제"""
    equipment = Equipment.query.get_or_404(id)
    location_id = equipment.location_id
    
    try:
        db.session.delete(equipment)
        db.session.commit()
        flash('장비가 성공적으로 삭제되었습니다.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'장비 삭제 중 오류가 발생했습니다: {str(e)}', 'danger')
    
    return redirect(url_for('equipment.location_equipment', location_id=location_id))

# AJAX 요청 처리
@equipment_bp.route('/api/group/<int:group_id>/attributes')
@login_required
def api_group_attributes(group_id):
    """특정 그룹의 속성 정보를 JSON으로 반환"""
    group = EquipmentGroup.query.get_or_404(group_id)
    attributes = []
    
    for attr in group.attributes.order_by(EquipmentAttribute.order).all():
        attr_data = {
            'id': attr.id,
            'name': attr.name,
            'label': attr.label,
            'field_type': attr.field_type,
            'required': attr.required,
            'order': attr.order
        }
        
        if attr.field_type == 'select':
            attr_data['options'] = attr.get_options_list()
        
        attributes.append(attr_data)
    
    return jsonify({'group_id': group_id, 'attributes': attributes})
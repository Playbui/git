from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.client_contact import ClientContact
from app.models.company import Company
from app.models.location import Location
from app.forms import ClientContactForm

client_contacts_bp = Blueprint('client_contacts', __name__, url_prefix='/client-contacts')

@client_contacts_bp.route('/')
@login_required
def index():
    # 검색 파라미터 처리
    company_id = request.args.get('company_id', type=int)
    location_id = request.args.get('location_id', type=int)
    search_query = request.args.get('search', '').strip()
    
    # 기본 쿼리 생성
    query = ClientContact.query
    
    # 필터 적용
    if company_id:
        query = query.filter_by(company_id=company_id)
    
    if location_id:
        query = query.filter_by(location_id=location_id)
    
    if search_query:
        # 여러 필드에서 검색
        query = query.filter(
            db.or_(
                ClientContact.name.ilike(f'%{search_query}%'),
                ClientContact.department.ilike(f'%{search_query}%'),
                ClientContact.position.ilike(f'%{search_query}%'),
                ClientContact.email.ilike(f'%{search_query}%'),
                ClientContact.phone.ilike(f'%{search_query}%')
            )
        )
    
    # 정렬 및 실행
    contacts = query.order_by(ClientContact.name).all()
    
    # 회사 및 장소 목록 (필터용)
    companies = Company.query.order_by(Company.company_name).all()
    locations = Location.query.order_by(Location.location_name).all()
    
    return render_template('client_contacts/index.html', 
                          contacts=contacts, 
                          companies=companies, 
                          locations=locations)

@client_contacts_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    form = ClientContactForm()
    company_id = request.args.get('company_id', type=int)
    if company_id:
        form.company_id.data = company_id
        # 해당 거래처의 장소 목록 로드
        locations = Location.query.filter_by(company_id=company_id).all()
        form.location_id.choices = [(0, '선택하세요')] + [(l.id, l.location_name) for l in locations]
    
    # 폼 제출 전 먼저 선택된 company_id에 맞는 location 목록 설정
    if request.method == 'POST' and form.company_id.data:
        locations = Location.query.filter_by(company_id=form.company_id.data).all()
        form.location_id.choices = [(0, '선택하세요')] + [(l.id, l.location_name) for l in locations]
    
    if form.validate_on_submit():
        try:
            # location_id는 validate_location_id 메서드에서 0->None으로 처리됨
            new_contact = ClientContact(
                company_id=form.company_id.data,
                location_id=form.location_id.data,
                department=form.department.data,
                name=form.name.data,
                position=form.position.data,
                phone=form.phone.data,
                email=form.email.data
            )
            
            db.session.add(new_contact)
            db.session.commit()
            
            flash('거래처 담당자가 성공적으로 등록되었습니다.', 'success')
            
            # 거래처 페이지를 통해 등록한 경우 해당 거래처 페이지로 리다이렉트
            if company_id:
                return redirect(url_for('companies.view', id=company_id))
                
            return redirect(url_for('client_contacts.index'))
        except Exception as e:
            db.session.rollback()
            print(f"오류 발생: {str(e)}")
            flash(f'담당자 등록 중 오류가 발생했습니다: {str(e)}', 'danger')
    
    return render_template('client_contacts/create.html', form=form)

@client_contacts_bp.route('/get-locations/<int:company_id>')
@login_required
def get_locations(company_id):
    locations = Location.query.filter_by(company_id=company_id).all()
    return jsonify([{'id': l.id, 'name': l.location_name} for l in locations])

@client_contacts_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    contact = ClientContact.query.get_or_404(id)
    form = ClientContactForm(obj=contact)
    
    # 장소 목록 로드
    locations = Location.query.filter_by(company_id=contact.company_id).all()
    form.location_id.choices = [(0, '선택하세요')] + [(l.id, l.location_name) for l in locations]
    
    # 폼 제출 전 먼저 선택된 company_id에 맞는 location 목록 설정
    if request.method == 'POST' and form.company_id.data:
        locations = Location.query.filter_by(company_id=form.company_id.data).all()
        form.location_id.choices = [(0, '선택하세요')] + [(l.id, l.location_name) for l in locations]
    
    if form.validate_on_submit():
        try:
            # 기본 필드 업데이트
            contact.company_id = form.company_id.data
            contact.location_id = form.location_id.data  # 이미 validate_location_id에서 처리됨
            contact.department = form.department.data
            contact.name = form.name.data
            contact.position = form.position.data
            contact.phone = form.phone.data
            contact.email = form.email.data
                
            db.session.commit()
            
            flash('담당자 정보가 성공적으로 업데이트되었습니다.', 'success')
            return redirect(url_for('client_contacts.view', id=contact.id))
        except Exception as e:
            db.session.rollback()
            print(f"오류 발생: {str(e)}")
            flash(f'담당자 정보 업데이트 중 오류가 발생했습니다: {str(e)}', 'danger')
    
    return render_template('client_contacts/edit.html', form=form, contact=contact)

@client_contacts_bp.route('/<int:id>')
@login_required
def view(id):
    contact = ClientContact.query.get_or_404(id)
    return render_template('client_contacts/view.html', contact=contact)

@client_contacts_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    contact = ClientContact.query.get_or_404(id)
    company_id = contact.company_id
    
    try:
        db.session.delete(contact)
        db.session.commit()
        flash('담당자가 성공적으로 삭제되었습니다.', 'success')
    except Exception as e:
        db.session.rollback()
        print(f"오류 발생: {str(e)}")
        flash(f'담당자 삭제 중 오류가 발생했습니다: {str(e)}', 'danger')
    
    # 리퍼러 URL이 있으면 해당 페이지로 돌아가기
    referrer = request.referrer
    if referrer and 'companies' in referrer:
        return redirect(url_for('companies.view', id=company_id))
        
    return redirect(url_for('client_contacts.index'))
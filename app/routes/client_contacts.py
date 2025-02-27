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
    contacts = ClientContact.query.all()
    return render_template('client_contacts/index.html', contacts=contacts)

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
    
    if form.validate_on_submit():
        try:
            new_contact = ClientContact(
                company_id=form.company_id.data,
                location_id=form.location_id.data if form.location_id.data != 0 else None,
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
    
    if form.validate_on_submit():
        try:
            form.populate_obj(contact)
            if form.location_id.data == 0:
                contact.location_id = None
                
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
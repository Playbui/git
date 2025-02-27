from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models.company import Company
from app.models.user import User
from app.forms import CompanyForm  # app/forms.py에서 CompanyForm 가져오기
from datetime import datetime

companies_bp = Blueprint('companies', __name__, url_prefix='/companies')

@companies_bp.route('/')
@login_required
def index():
    companies = Company.query.all()
    return render_template('companies/index.html', companies=companies)

@companies_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    form = CompanyForm()
    
    if form.validate_on_submit():
        try:
            new_company = Company(
                company_name=form.company_name.data,
                business_number=form.business_number.data,
                company_type=form.company_type.data,
                industry=form.industry.data,
                address=form.address.data,
                postal_code=form.postal_code.data,
                region=form.region.data,
                main_phone=form.main_phone.data,
                main_email=form.main_email.data,
                website=form.website.data,
                notes=form.notes.data
            )
            
            # 디버깅: 생성되는 객체 정보 출력
            print(f"새 거래처 생성: {new_company.company_name}")
            
            db.session.add(new_company)
            db.session.commit()
            
            flash('거래처가 성공적으로 등록되었습니다.', 'success')
            return redirect(url_for('companies.index'))
        except Exception as e:
            db.session.rollback()
            print(f"오류 발생: {str(e)}")
            flash(f'거래처 등록 중 오류가 발생했습니다: {str(e)}', 'danger')
    
    return render_template('companies/create.html', form=form)
@companies_bp.route('/<int:id>')
@login_required
def view(id):
    company = Company.query.get_or_404(id)
    contacts = company.get_contacts()
    return render_template('companies/view.html', company=company, contacts=contacts)

@companies_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    company = Company.query.get_or_404(id)
    form = CompanyForm(obj=company)
    
    if form.validate_on_submit():
        try:
            # 폼에서 데이터 가져와서 업데이트
            form.populate_obj(company)
            
            # DB에 저장
            db.session.commit()
            
            flash('거래처 정보가 성공적으로 업데이트되었습니다.', 'success')
            return redirect(url_for('companies.view', id=company.id))
        except Exception as e:
            db.session.rollback()
            print(f"오류 발생: {str(e)}")
            flash(f'거래처 정보 업데이트 중 오류가 발생했습니다: {str(e)}', 'danger')
    
    return render_template('companies/edit.html', form=form, company=company)

@companies_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    company = Company.query.get_or_404(id)
    
    try:
        db.session.delete(company)
        db.session.commit()
        flash('거래처가 성공적으로 삭제되었습니다.', 'success')
    except Exception as e:
        db.session.rollback()
        print(f"오류 발생: {str(e)}")
        flash(f'거래처 삭제 중 오류가 발생했습니다. 관련된 데이터가 있을 수 있습니다: {str(e)}', 'danger')
    
    return redirect(url_for('companies.index'))
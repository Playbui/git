from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models.project import Project
from app.models.user import User
from app.models.company import Company
from app.models.location import Location
from datetime import datetime, date

projects_bp = Blueprint('projects', __name__, url_prefix='/projects')

@projects_bp.route('/')
@login_required
def index():
    projects = Project.query.all()
    return render_template('projects/index.html', projects=projects)

@projects_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        try:
            # 폼에서 데이터 가져오기
            project_year = request.form.get('project_year')
            project_name = request.form.get('project_name')
            project_code = request.form.get('project_code')
            start_date = datetime.strptime(request.form.get('start_date'), '%Y-%m-%d').date()
            end_date = datetime.strptime(request.form.get('end_date'), '%Y-%m-%d').date()
            budget = request.form.get('budget')
            client_company_id = request.form.get('client_company_id')
            client_contact_id = request.form.get('client_contact_id')
            department_in_charge = request.form.get('department_in_charge')
            pm_id = request.form.get('pm_id')
            status = request.form.get('status', 'planning')
            description = request.form.get('description')
            
            # 새 프로젝트 생성
            new_project = Project(
                project_year=project_year,
                project_name=project_name,
                project_code=project_code,
                start_date=start_date,
                end_date=end_date,
                budget=budget,
                client_company_id=client_company_id,
                client_contact_id=client_contact_id,
                department_in_charge=department_in_charge,
                pm_id=pm_id,
                status=status,
                description=description
            )
            
            # DB에 저장
            db.session.add(new_project)
            db.session.commit()
            
            flash('프로젝트가 성공적으로 생성되었습니다.', 'success')
            return redirect(url_for('projects.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'프로젝트 생성 중 오류가 발생했습니다: {str(e)}', 'danger')
    
    # GET 요청 처리
    users = User.query.all()
    companies = Company.query.all()
    today = date.today()
    return render_template('projects/create.html', users=users, companies=companies, today=today)

@projects_bp.route('/<int:id>')
@login_required
def view(id):
    project = Project.query.get_or_404(id)
    return render_template('projects/view.html', project=project)

@projects_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    project = Project.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            # 폼에서 데이터 가져와서 업데이트
            project.project_year = request.form.get('project_year')
            project.project_name = request.form.get('project_name')
            project.project_code = request.form.get('project_code')
            project.start_date = datetime.strptime(request.form.get('start_date'), '%Y-%m-%d').date()
            project.end_date = datetime.strptime(request.form.get('end_date'), '%Y-%m-%d').date()
            project.budget = request.form.get('budget')
            project.client_company_id = request.form.get('client_company_id')
            project.client_contact_id = request.form.get('client_contact_id')
            project.department_in_charge = request.form.get('department_in_charge')
            project.pm_id = request.form.get('pm_id')
            project.status = request.form.get('status')
            project.description = request.form.get('description')
            
            # DB에 저장
            db.session.commit()
            
            flash('프로젝트가 성공적으로 업데이트되었습니다.', 'success')
            return redirect(url_for('projects.view', id=project.id))
        except Exception as e:
            db.session.rollback()
            flash(f'프로젝트 업데이트 중 오류가 발생했습니다: {str(e)}', 'danger')
    
    # GET 요청 처리
    users = User.query.all()
    companies = Company.query.all()
    return render_template('projects/edit.html', project=project, users=users, companies=companies)

@projects_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    project = Project.query.get_or_404(id)
    
    try:
        db.session.delete(project)
        db.session.commit()
        flash('프로젝트가 성공적으로 삭제되었습니다.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'프로젝트 삭제 중 오류가 발생했습니다: {str(e)}', 'danger')
    
    return redirect(url_for('projects.index'))
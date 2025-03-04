from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models.project import Project
from app.models.user import User
from app.models.company import Company
from app.models.location import Location
from app.models.client_contact import ClientContact  # ClientContact 모델 임포트 추가
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
            client_company_id = request.form.get('client_company_id') or None
            client_contact_id = request.form.get('client_contact_id') or None
            department_in_charge = request.form.get('department_in_charge')
            pm_id = request.form.get('pm_id')
            status = request.form.get('status', 'planning')
            description = request.form.get('description')
            
            # 디버깅: 수신된 데이터 확인
            print(f"생성 데이터 - client_company_id: {client_company_id}, client_contact_id: {client_contact_id}")
            
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
            print(f"프로젝트 생성 오류: {str(e)}")
            flash(f'프로젝트 생성 중 오류가 발생했습니다: {str(e)}', 'danger')
    
    # GET 요청 처리
    users = User.query.all()  # PM용 사용자 목록
    companies = Company.query.all()
    today = date.today()
    
    # 거래처 담당자 목록 가져오기 (ClientContact 테이블에서)
    client_contacts = ClientContact.query.all()
    
    # 디버깅: 거래처 담당자 정보 확인
    print(f"거래처 담당자 수: {len(client_contacts)}")
    for contact in client_contacts:
        print(f"  - ID: {contact.id}, 이름: {contact.name}, 회사 ID: {contact.company_id}")
    
    return render_template('projects/create.html', 
                          users=users, 
                          companies=companies, 
                          client_contacts=client_contacts,  # 거래처 담당자 목록 전달
                          today=today)

@projects_bp.route('/<int:id>')
@login_required
def view(id):
    try:
        project = Project.query.get_or_404(id)
        
        # 디버깅: 프로젝트 관계 정보 로깅
        print(f"프로젝트 ID: {project.id}, 이름: {project.project_name}")
        print(f"client_company_id: {project.client_company_id}, client_contact_id: {project.client_contact_id}, pm_id: {project.pm_id}")
        
        if project.client_company_id:
            company = Company.query.get(project.client_company_id)
            print(f"client_company: {company and company.company_name}")
        
        if project.client_contact_id:
            # ClientContact 테이블에서 담당자 정보 조회
            contact = ClientContact.query.get(project.client_contact_id)
            print(f"client_contact: {contact and contact.name}")
        
        if project.pm_id:
            pm = User.query.get(project.pm_id)
            print(f"project_manager: {pm and pm.name}")
        
        return render_template('projects/view.html', project=project)
    except Exception as e:
        print(f"프로젝트 조회 오류: {str(e)}")
        flash(f'프로젝트 조회 중 오류가 발생했습니다: {str(e)}', 'danger')
        return redirect(url_for('projects.index'))

@projects_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    try:
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
                project.client_company_id = request.form.get('client_company_id') or None
                project.client_contact_id = request.form.get('client_contact_id') or None
                project.department_in_charge = request.form.get('department_in_charge')
                project.pm_id = request.form.get('pm_id')
                project.status = request.form.get('status')
                project.description = request.form.get('description')
                
                # 디버깅: 수정된 데이터 확인
                print(f"수정 데이터 - client_company_id: {project.client_company_id}, client_contact_id: {project.client_contact_id}")
                
                # DB에 저장
                db.session.commit()
                
                flash('프로젝트가 성공적으로 업데이트되었습니다.', 'success')
                return redirect(url_for('projects.view', id=project.id))
            except Exception as e:
                db.session.rollback()
                print(f"프로젝트 업데이트 오류: {str(e)}")
                flash(f'프로젝트 업데이트 중 오류가 발생했습니다: {str(e)}', 'danger')
        
        # GET 요청 처리
        users = User.query.all()
        companies = Company.query.all()
        
        # 거래처 담당자 목록 가져오기 (ClientContact 테이블에서)
        client_contacts = ClientContact.query.all()
        
        return render_template('projects/edit.html', 
                              project=project, 
                              users=users, 
                              companies=companies,
                              client_contacts=client_contacts)  # 거래처 담당자 목록 전달
    except Exception as e:
        print(f"프로젝트 편집 페이지 로드 오류: {str(e)}")
        flash(f'프로젝트 편집 페이지 로드 중 오류가 발생했습니다: {str(e)}', 'danger')
        return redirect(url_for('projects.index'))

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
        print(f"프로젝트 삭제 오류: {str(e)}")
        flash(f'프로젝트 삭제 중 오류가 발생했습니다: {str(e)}', 'danger')
    
    return redirect(url_for('projects.index'))
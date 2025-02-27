from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models.user import User
from app.forms import RegistrationForm, UserEditForm, UserFilterForm
from app import db
from sqlalchemy import or_

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/')
@login_required
def index():
    if not current_user.is_admin():
        flash('관리자 권한이 필요합니다.', 'danger')
        return redirect(url_for('dashboard.index'))
    
    return render_template('admin/dashboard.html')

@admin_bp.route('/users', methods=['GET'])
@login_required
def users():
    if not current_user.is_admin():
        flash('관리자 권한이 필요합니다.', 'danger')
        return redirect(url_for('dashboard.index'))
    
    form = UserFilterForm(request.args, meta={'csrf': False})
    
    # 쿼리 기본 설정
    query = User.query
    
    # 필터 적용
    if form.validate():
        # 사용자 유형 필터
        if form.user_type.data:
            query = query.filter(User.user_type == form.user_type.data)
        
        # 부서 필터
        if form.department.data:
            query = query.filter(User.department.like(f'%{form.department.data}%'))
        
        # 검색어 (이름, 사용자명, 이메일로 검색)
        if form.search.data:
            search = f'%{form.search.data}%'
            query = query.filter(
                or_(
                    User.name.like(search),
                    User.username.like(search),
                    User.email.like(search)
                )
            )
    
    # 사용자 목록 조회
    users = query.all()
    
    # 부서 목록 가져오기 (필터 드롭다운용)
    departments = db.session.query(User.department).distinct().all()
    department_list = [dept[0] for dept in departments if dept[0]]
    
    return render_template('admin/users.html', users=users, form=form, departments=department_list)

@admin_bp.route('/users/<int:user_id>')
@login_required
def user_detail(user_id):
    if not current_user.is_admin():
        flash('관리자 권한이 필요합니다.', 'danger')
        return redirect(url_for('dashboard.index'))
    
    user = User.query.get_or_404(user_id)
    return render_template('admin/user_detail.html', user=user)

@admin_bp.route('/create-user', methods=['GET', 'POST'])
@login_required
def create_user():
    if not current_user.is_admin():
        flash('관리자 권한이 필요합니다.', 'danger')
        return redirect(url_for('dashboard.index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            name=form.name.data,
            email=form.email.data,
            user_type=form.user_type.data,
            department=form.department.data,
            position=form.position.data,
            phone=form.phone.data,
            company=form.company.data,
            telegram_id=form.telegram_id.data
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('새 사용자가 생성되었습니다.', 'success')
        return redirect(url_for('admin.users'))
    
    return render_template('admin/create_user.html', form=form)

@admin_bp.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    if not current_user.is_admin():
        flash('관리자 권한이 필요합니다.', 'danger')
        return redirect(url_for('dashboard.index'))
    
    user = User.query.get_or_404(user_id)
    form = UserEditForm(original_email=user.email, obj=user)
    
    if form.validate_on_submit():
        user.name = form.name.data
        user.email = form.email.data
        user.user_type = form.user_type.data
        user.department = form.department.data
        user.position = form.position.data
        user.phone = form.phone.data
        user.company = form.company.data
        user.telegram_id = form.telegram_id.data
        user.is_active = form.is_active.data
        
        # 비밀번호 변경이 있는 경우
        if form.new_password.data:
            user.set_password(form.new_password.data)
            flash('비밀번호가 변경되었습니다.', 'success')
        
        db.session.commit()
        flash('사용자 정보가 업데이트되었습니다.', 'success')
        return redirect(url_for('admin.user_detail', user_id=user.id))
    
    return render_template('admin/edit_user.html', form=form, user=user)
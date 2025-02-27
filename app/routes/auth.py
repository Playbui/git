from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from app.models.user import User
from app import db
from urllib.parse import urlparse
from app.forms import RegistrationForm, ChangePasswordForm
from datetime import datetime

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.is_admin():
            return redirect(url_for('admin.index'))
        else:
            return redirect(url_for('dashboard.index'))
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        
        if user is None or not user.check_password(password):
            flash('잘못된 사용자 이름 또는 비밀번호입니다.', 'danger')
            return redirect(url_for('auth.login'))
        
        # 사용자 활성화 상태 확인
        if not user.is_active:
            flash('이 계정은 비활성화되었습니다. 관리자에게 문의하세요.', 'warning')
            return redirect(url_for('auth.login'))

        # 로그인 시간 업데이트
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        login_user(user, remember=request.form.get('remember_me'))
        
        next_page = request.args.get('next')
        if not next_page or urlparse(next_page).netloc != '':
            if user.is_admin():
                next_page = url_for('admin.index')
            else:
                next_page = url_for('dashboard.index')
                
        return redirect(next_page)
    
    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
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
        flash('사용자 등록이 완료되었습니다! 이제 로그인할 수 있습니다.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html', form=form)

@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.check_password(form.current_password.data):
            current_user.set_password(form.new_password.data)
            db.session.commit()
            flash('비밀번호가 변경되었습니다.', 'success')
            return redirect(url_for('dashboard.index'))
        else:
            flash('현재 비밀번호가 올바르지 않습니다.', 'danger')
    return render_template('auth/change_password.html', form=form)
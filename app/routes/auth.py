from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from app.models.user import User
from app import db
from urllib.parse import urlparse
from app.forms import RegistrationForm, ChangePasswordForm, LoginForm
from datetime import datetime
import time

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

# 로그인 시도 추적을 위한 딕셔너리
login_attempts = {}
MAX_ATTEMPTS = 5  # 최대 로그인 시도 횟수
LOCKOUT_TIME = 300  # 잠금 시간(초)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.is_admin():
            return redirect(url_for('admin.index'))
        else:
            return redirect(url_for('dashboard.index'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        username = form.username.data
        
        # 로그인 시도 제한 확인
        client_ip = request.remote_addr
        current_time = time.time()
        attempts_key = f"{client_ip}:{username}"
        
        # 로그인 시도 기록이 있는지 확인
        if attempts_key in login_attempts:
            attempts, lockout_time = login_attempts[attempts_key]
            
            # 잠금 시간이 지났는지 확인
            if lockout_time > current_time:
                remaining_time = int(lockout_time - current_time)
                flash(f'계정이 일시적으로 잠겼습니다. {remaining_time}초 후에 다시 시도하세요.', 'warning')
                return render_template('auth/login.html', form=form)
            
            # 잠금 시간이 지났으면 초기화
            if attempts >= MAX_ATTEMPTS:
                login_attempts[attempts_key] = (0, 0)
                attempts = 0
        else:
            attempts = 0
        
        user = User.query.filter_by(username=username).first()
        
        if user is None or not user.check_password(form.password.data):
            # 로그인 실패 횟수 증가
            attempts += 1
            
            # 최대 시도 횟수 초과 시 계정 잠금
            if attempts >= MAX_ATTEMPTS:
                lockout_time = current_time + LOCKOUT_TIME
                login_attempts[attempts_key] = (attempts, lockout_time)
                flash(f'로그인 시도 횟수를 초과했습니다. {LOCKOUT_TIME}초 동안 계정이 잠깁니다.', 'danger')
            else:
                login_attempts[attempts_key] = (attempts, 0)
                flash('잘못된 사용자 이름 또는 비밀번호입니다.', 'danger')
                
            return render_template('auth/login.html', form=form)
        
        # 사용자 활성화 상태 확인
        if not user.is_active:
            flash('이 계정은 비활성화되었습니다. 관리자에게 문의하세요.', 'warning')
            return render_template('auth/login.html', form=form)

        # 로그인 성공 시 시도 횟수 초기화
        if attempts_key in login_attempts:
            login_attempts.pop(attempts_key)
        
        # 로그인 시간 업데이트
        try:
            user.last_login = datetime.utcnow()
            db.session.commit()
        except Exception as e:
            # 오류가 발생해도 로그인은 진행
            db.session.rollback()
            print(f"로그인 시간 업데이트 오류: {e}")
        
        login_user(user, remember=form.remember_me.data)
        
        next_page = request.args.get('next')
        if not next_page or urlparse(next_page).netloc != '':
            if user.is_admin():
                next_page = url_for('admin.index')
            else:
                next_page = url_for('dashboard.index')
                
        return redirect(next_page)
    
    return render_template('auth/login.html', form=form)

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
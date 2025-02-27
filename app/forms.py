from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, SubmitField, BooleanField, TextAreaField, DecimalField, SelectMultipleField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, Optional
from app.models.user import User
from wtforms import DateField
from app.models.company import Company

class RegistrationForm(FlaskForm):
    username = StringField('사용자명', validators=[DataRequired(), Length(min=4, max=50)])
    name = StringField('이름', validators=[DataRequired(), Length(max=100)])
    email = StringField('이메일', validators=[DataRequired(), Email(), Length(max=100)])
    user_type = SelectField('사용자 유형', choices=[
        ('admin', '관리자'),
        ('pm', '프로젝트 매니저'),
        ('engineer', '엔지니어'),
        ('client', '클라이언트')
    ])
    password = PasswordField('비밀번호', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('비밀번호 확인', 
                                    validators=[DataRequired(), EqualTo('password')])
    department = StringField('부서', validators=[Length(max=100)])
    position = StringField('직책', validators=[Length(max=100)])
    phone = StringField('전화번호', validators=[Length(max=20)])
    company = StringField('회사명', validators=[Length(max=100)])
    telegram_id = StringField('텔레그램 ID', validators=[Optional(), Length(max=100)])
    submit = SubmitField('사용자 등록')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('이미 사용 중인 사용자명입니다. 다른 사용자명을 선택하세요.')
            
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('이미 사용 중인 이메일입니다. 다른 이메일을 입력하세요.')

class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('현재 비밀번호', validators=[DataRequired()])
    new_password = PasswordField('새 비밀번호', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('새 비밀번호 확인', 
                                    validators=[DataRequired(), EqualTo('new_password')])
    submit = SubmitField('비밀번호 변경')

class UserEditForm(FlaskForm):
    name = StringField('이름', validators=[DataRequired(), Length(max=100)])
    email = StringField('이메일', validators=[DataRequired(), Email(), Length(max=100)])
    user_type = SelectField('사용자 유형', choices=[
        ('admin', '관리자'),
        ('pm', '프로젝트 매니저'),
        ('engineer', '엔지니어'),
        ('client', '클라이언트')
    ])
    department = StringField('부서', validators=[Optional(), Length(max=100)])
    position = StringField('직책', validators=[Optional(), Length(max=100)])
    phone = StringField('전화번호', validators=[Optional(), Length(max=20)])
    company = StringField('회사명', validators=[Optional(), Length(max=100)])
    telegram_id = StringField('텔레그램 ID', validators=[Optional(), Length(max=100)])
    is_active = BooleanField('활성 상태')
    new_password = PasswordField('새 비밀번호', validators=[Optional(), Length(min=6)])
    confirm_password = PasswordField('새 비밀번호 확인', 
                                    validators=[Optional(), EqualTo('new_password')])
    submit = SubmitField('사용자 정보 수정')

    def __init__(self, original_email=None, *args, **kwargs):
        super(UserEditForm, self).__init__(*args, **kwargs)
        self.original_email = original_email

    def validate_email(self, email):
        if email.data != self.original_email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('이미 사용 중인 이메일입니다. 다른 이메일을 입력하세요.')

class UserFilterForm(FlaskForm):
    user_type = SelectField('사용자 유형', choices=[
        ('', '모든 유형'),
        ('admin', '관리자'),
        ('pm', '프로젝트 매니저'),
        ('engineer', '엔지니어'),
        ('client', '클라이언트')
    ], validators=[Optional()])
    department = StringField('부서', validators=[Optional()])
    search = StringField('검색어', validators=[Optional()])
    submit = SubmitField('필터링')

class ProjectForm(FlaskForm):
    project_year = StringField('프로젝트 연도', validators=[DataRequired(), Length(max=4)])
    project_name = StringField('프로젝트명', validators=[DataRequired(), Length(max=255)])
    project_code = StringField('프로젝트 코드', validators=[DataRequired(), Length(max=50)])
    start_date = DateField('시작일', format='%Y-%m-%d', validators=[DataRequired()])
    end_date = DateField('종료일', format='%Y-%m-%d', validators=[DataRequired()])
    budget = DecimalField('예산', places=2, validators=[Optional()])
    client_name = StringField('발주처명', validators=[DataRequired(), Length(max=100)])
    client_contact_id = SelectField('발주처 담당자', coerce=int, validators=[Optional()])
    department_in_charge = StringField('담당 부서', validators=[Length(max=100)])
    pm_id = SelectField('담당 PM', coerce=int, validators=[Optional()])
    status = SelectField('상태', choices=[
        ('planning', '계획중'),
        ('in_progress', '진행중'),
        ('completed', '완료'),
        ('suspended', '중단')
    ])
    description = TextAreaField('설명')
    submit = SubmitField('프로젝트 저장')
    
    def __init__(self, *args, **kwargs):
        super(ProjectForm, self).__init__(*args, **kwargs)
        self.client_contact_id.choices = [(0, '선택하세요')] + [
            (u.id, f"{u.name} ({u.company})") 
            for u in User.query.filter_by(user_type='client').all()
        ]
        self.pm_id.choices = [(0, '선택하세요')] + [
            (u.id, f"{u.name} ({u.department})") 
            for u in User.query.filter(User.user_type.in_(['admin', 'pm'])).all()
        ]

class LocationForm(FlaskForm):
    company_id = SelectField('거래처', coerce=int, validators=[DataRequired()])
    location_name = StringField('장소명', validators=[DataRequired(), Length(max=200)])
    region = SelectField('지역', choices=[
        ('본부', '본부'),
        ('서해', '서해'),
        ('남해', '남해'),
        ('동해', '동해')
    ], validators=[DataRequired()])
    work_type = SelectField('업무 구분', choices=[
        ('안전국', '안전국'),
        ('중계소', '중계소')
    ], validators=[DataRequired()])
    safety_bureau_name = StringField('안전국명/중계소명', validators=[Length(max=100)])
    relay_station = StringField('송신소/수신소', validators=[Length(max=100)])
    address = TextAreaField('주소', validators=[DataRequired()])
    office_phone = StringField('사무실 연락처', validators=[Length(max=20)])
    manager_ids = SelectMultipleField('본사 담당자', coerce=int, validators=[Optional()])
    client_ids = SelectMultipleField('거래처 담당자', coerce=int, validators=[Optional()])
    special_instructions = TextAreaField('특별 지시사항')
    submit = SubmitField('장소 저장')
    
    def __init__(self, *args, **kwargs):
        super(LocationForm, self).__init__(*args, **kwargs)
        # 거래처 목록 조회
        self.company_id.choices = [(0, '선택하세요')] + [
            (c.id, c.company_name) for c in Company.query.order_by(Company.company_name).all()
        ]
        # 본사 담당자 목록 (admin, pm, engineer)
        self.manager_ids.choices = [
            (u.id, f"{u.name} ({u.department or '부서없음'})") 
            for u in User.query.filter(User.user_type.in_(['admin', 'pm', 'engineer'])).all()
        ]
        # 거래처 담당자 목록 (client)
        self.client_ids.choices = [
            (u.id, f"{u.name} ({u.company or '미지정'})") 
            for u in User.query.filter_by(user_type='client').all()
        ]

class EquipmentForm(FlaskForm):
    equipment_group = StringField('장비 그룹', validators=[DataRequired(), Length(max=100)])
    equipment_name = StringField('장비명', validators=[DataRequired(), Length(max=255)])
    hostname = StringField('호스트명', validators=[Length(max=100)])
    ip_address = StringField('IP 주소', validators=[Length(max=15)])
    equipment_type = StringField('장비 종류', validators=[Length(max=100)])
    manufacturer = StringField('제조사', validators=[Length(max=100)])
    model_number = StringField('모델번호', validators=[Length(max=100)])
    os_type = StringField('OS 종류', validators=[Length(max=100)])
    os_version = StringField('OS 버전', validators=[Length(max=50)])
    serial_number = StringField('시리얼 번호', validators=[Length(max=100)])
    installation_date = DateField('설치일', format='%Y-%m-%d', validators=[Optional()])
    warranty_end_date = DateField('보증 만료일', format='%Y-%m-%d', validators=[Optional()])
    maintenance_cycle = StringField('유지보수 주기', validators=[Length(max=50)])
    status = SelectField('상태', choices=[
        ('active', '활성'),
        ('inactive', '비활성'),
        ('maintenance', '유지보수'),
        ('broken', '고장')
    ])
    notes = TextAreaField('비고')
    submit = SubmitField('장비 저장')

class CompanyForm(FlaskForm):
    company_name = StringField('회사명', validators=[DataRequired(), Length(max=200)])
    business_number = StringField('사업자 번호', validators=[Length(max=50)])
    company_type = SelectField('회사 유형', choices=[
        ('', '선택하세요'),
        ('대기업', '대기업'),
        ('중견기업', '중견기업'),
        ('중소기업', '중소기업'),
        ('공공기관', '공공기관'),
        ('비영리단체', '비영리단체'),
        ('기타', '기타')
    ], validators=[Optional()])
    industry = StringField('업종', validators=[Length(max=100)])
    address = TextAreaField('주소')
    postal_code = StringField('우편번호', validators=[Length(max=20)])
    region = SelectField('지역', choices=[
        ('', '선택하세요'),
        ('서울', '서울'),
        ('부산', '부산'),
        ('대구', '대구'),
        ('인천', '인천'),
        ('광주', '광주'),
        ('대전', '대전'),
        ('울산', '울산'),
        ('세종', '세종'),
        ('경기', '경기'),
        ('강원', '강원'),
        ('충북', '충북'),
        ('충남', '충남'),
        ('전북', '전북'),
        ('전남', '전남'),
        ('경북', '경북'),
        ('경남', '경남'),
        ('제주', '제주')
    ], validators=[Optional()])
    main_phone = StringField('대표 전화', validators=[Length(max=20)])
    main_email = StringField('대표 이메일', validators=[Length(max=100), Optional(), Email()])
    website = StringField('웹사이트', validators=[Length(max=255)])
    notes = TextAreaField('비고')
    submit = SubmitField('회사 저장')

class ClientContactForm(FlaskForm):
    company_id = SelectField('거래처', coerce=int, validators=[DataRequired()])
    location_id = SelectField('근무지', coerce=int, validators=[Optional()])
    department = StringField('부서', validators=[Length(max=100)])
    name = StringField('이름', validators=[DataRequired(), Length(max=100)])
    position = StringField('직급', validators=[Length(max=100)])
    phone = StringField('전화번호', validators=[Length(max=20)])
    email = StringField('이메일', validators=[Email(), Length(max=100)])
    submit = SubmitField('담당자 저장')
    
    def __init__(self, *args, **kwargs):
        super(ClientContactForm, self).__init__(*args, **kwargs)
        # 거래처 목록 조회
        self.company_id.choices = [(0, '선택하세요')] + [
            (c.id, c.company_name) for c in Company.query.order_by(Company.company_name).all()
        ]
        # 장소 목록은 거래처 선택 시 동적으로 변경됨
        self.location_id.choices = [(0, '선택하세요')]
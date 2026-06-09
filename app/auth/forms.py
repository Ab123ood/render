from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, EmailField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from app.models import User
from app.auth.security import check_password_strength


class RegisterForm(FlaskForm):
    username = StringField(
        'اسم المستخدم',
        validators=[
            DataRequired(message='اسم المستخدم مطلوب'),
            Length(min=3, max=80, message='اسم المستخدم يجب أن يكون بين 3 و 80 حرف')
        ],
        render_kw={"placeholder": "اسم المستخدم", "autocomplete": "username"}
    )
    email = EmailField(
        'البريد الإلكتروني',
        validators=[
            DataRequired(message='البريد الإلكتروني مطلوب'),
            Email(message='بريد إلكتروني غير صالح'),
            Length(max=120, message='البريد الإلكتروني طويل جدًا')
        ],
        render_kw={"placeholder": "example@domain.com", "autocomplete": "email"}
    )
    password = PasswordField(
        'كلمة المرور',
        validators=[
            DataRequired(message='كلمة المرور مطلوبة'),
            Length(min=12, message='كلمة المرور يجب أن تكون 12 حرفًا على الأقل')
        ],
        render_kw={"placeholder": "كلمة مرور قوية (12+ حرف)", "autocomplete": "new-password"}
    )
    confirm_password = PasswordField(
        'تأكيد كلمة المرور',
        validators=[
            DataRequired(message='تأكيد كلمة المرور مطلوب'),
            EqualTo('password', message='كلمتا المرور غير متطابقتين')
        ],
        render_kw={"placeholder": "أعد إدخال كلمة المرور", "autocomplete": "new-password"}
    )
    submit = SubmitField('إنشاء حساب')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('اسم المستخدم مستخدم بالفعل')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('البريد الإلكتروني مسجل بالفعل')
    
    def validate_password(self, password):
        is_strong, message = check_password_strength(password.data)
        if not is_strong:
            raise ValidationError(message)


class LoginForm(FlaskForm):
    username = StringField(
        'اسم المستخدم أو البريد الإلكتروني',
        validators=[
            DataRequired(message='مطلوب')
        ],
        render_kw={"placeholder": "اسم المستخدم أو البريد الإلكتروني", "autocomplete": "username"}
    )
    password = PasswordField(
        'كلمة المرور',
        validators=[
            DataRequired(message='مطلوبة')
        ],
        render_kw={"placeholder": "كلمة المرور", "autocomplete": "current-password"}
    )
    remember_me = StringField('تذكرني', render_kw={"type": "checkbox"})
    submit = SubmitField('تسجيل الدخول')
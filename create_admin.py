import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app, db
from app.models import User
from app.auth.security import hash_password

USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
EMAIL = os.environ.get('ADMIN_EMAIL', 'admin@example.com')
PASSWORD = os.environ.get('ADMIN_PASSWORD', 'Admin@12345678')


def create_admin():
    app = create_app()
    with app.app_context():
        if User.query.filter_by(username=USERNAME).first():
            print(f'المستخدم {USERNAME} موجود بالفعل.')
            return
        
        if User.query.filter_by(email=EMAIL).first():
            print(f'البريد {EMAIL} مسجل بالفعل.')
            return
        
        admin = User(
            username=USERNAME,
            email=EMAIL,
            password_hash=hash_password(PASSWORD),
            is_admin=True
        )
        db.session.add(admin)
        db.session.commit()
        print(f'تم إنشاء المشرف بنجاح!')
        print(f'اسم المستخدم: {USERNAME}')
        print(f'البريد الإلكتروني: {EMAIL}')
        print(f'كلمة المرور: {PASSWORD}')


if __name__ == '__main__':
    create_admin()

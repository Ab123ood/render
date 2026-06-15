import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app, db
from app.models import User
from app.auth.security import hash_password


def create_admin():
    app = create_app()
    with app.app_context():
        username = input('اسم المستخدم للمشرف: ').strip()
        email = input('البريد الإلكتروني للمشرف: ').strip()
        password = input('كلمة المرور: ').strip()
        
        if User.query.filter_by(username=username).first():
            print(f'خطأ: المستخدم {username} موجود بالفعل.')
            return
        
        if User.query.filter_by(email=email).first():
            print(f'خطأ: البريد {email} مسجل بالفعل.')
            return
        
        admin = User(
            username=username,
            email=email,
            password_hash=hash_password(password),
            is_admin=True
        )
        db.session.add(admin)
        db.session.commit()
        print(f'تم إنشاء المشرف {username} بنجاح!')


if __name__ == '__main__':
    create_admin()

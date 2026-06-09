from datetime import datetime, timedelta
from flask import render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from app.auth import bp
from app.auth.forms import RegisterForm, LoginForm
from app.auth.security import hash_password, verify_password
from app.models import User
from app import db, limiter


MAX_FAILED_ATTEMPTS = 5
LOCKOUT_DURATION = timedelta(minutes=15)


@bp.route('/register', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            password_hash=hash_password(form.password.data)
        )
        db.session.add(user)
        db.session.commit()
        flash('تم إنشاء الحساب بنجاح! يمكنك الآن تسجيل الدخول.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html', form=form)


@bp.route('/login', methods=['GET', 'POST'])
@limiter.limit("10 per minute")
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        identifier = form.username.data
        password = form.password.data
        
        user = User.query.filter(
            (User.username == identifier) | (User.email == identifier)
        ).first()
        
        if user is None:
            flash('اسم المستخدم أو كلمة المرور غير صحيحة', 'error')
            return render_template('auth/login.html', form=form)
        
        if user.locked_until and user.locked_until > datetime.utcnow():
            remaining = (user.locked_until - datetime.utcnow()).seconds // 60
            flash(f'الحساب مقفل مؤقتًا. حاول مرة أخرى بعد {remaining} دقيقة.', 'error')
            return render_template('auth/login.html', form=form)
        
        if not verify_password(user.password_hash, password):
            user.failed_login_attempts += 1
            
            if user.failed_login_attempts >= MAX_FAILED_ATTEMPTS:
                user.locked_until = datetime.utcnow() + LOCKOUT_DURATION
                flash(f'تم قفل الحساب بسبب محاولات فاشلة متكررة. حاول بعد {LOCKOUT_DURATION.seconds // 60} دقيقة.', 'error')
            else:
                remaining = MAX_FAILED_ATTEMPTS - user.failed_login_attempts
                flash(f'كلمة مرور غير صحيحة. تبقى {remaining} محاولة قبل القفل.', 'error')
            
            db.session.commit()
            return render_template('auth/login.html', form=form)
        
        user.failed_login_attempts = 0
        user.locked_until = None
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        login_user(user, remember=form.remember_me.data == 'y')
        flash('مرحبًا بك! تم تسجيل الدخول بنجاح.', 'success')
        
        next_page = request.args.get('next')
        if not next_page or not next_page.startswith('/'):
            next_page = url_for('main.index')
        return redirect(next_page)
    
    return render_template('auth/login.html', form=form)


@bp.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    flash('تم تسجيل الخروج بنجاح.', 'info')
    return redirect(url_for('auth.login'))


@bp.route('/profile')
@login_required
def profile():
    return render_template('auth/profile.html', user=current_user)
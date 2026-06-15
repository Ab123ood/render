from datetime import datetime, timezone
from flask import render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app.admin import bp
from app.admin.decorators import admin_required
from app.models import User
from app import db


@bp.route('/')
@admin_required
def dashboard():
    total_users = User.query.count()
    active_users = User.query.filter_by(is_active_column=True).count()
    locked_users = User.query.filter(User.locked_until > datetime.now(timezone.utc)).count()
    admin_users = User.query.filter_by(is_admin=True).count()
    
    stats = {
        'total': total_users,
        'active': active_users,
        'locked': locked_users,
        'admin': admin_users,
    }
    
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html', stats=stats, recent_users=recent_users)


@bp.route('/users')
@admin_required
def users():
    all_users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=all_users)


@bp.route('/user/<int:user_id>/toggle', methods=['POST'])
@admin_required
def toggle_user(user_id):
    user = User.query.get_or_404(user_id)
    
    if user.id == current_user.id:
        flash('لا يمكنك حظر نفسك.', 'error')
        return redirect(url_for('admin.users'))
    
    if user.is_admin:
        flash('لا يمكنك حظر مشرف آخر.', 'error')
        return redirect(url_for('admin.users'))
    
    user.is_active = not user.is_active
    db.session.commit()
    
    status = 'تفعيل' if user.is_active else 'حظر'
    flash(f'تم {status} المستخدم {user.username} بنجاح.', 'success')
    return redirect(url_for('admin.users'))


@bp.route('/user/<int:user_id>/delete', methods=['POST'])
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    
    if user.id == current_user.id:
        flash('لا يمكنك حذف نفسك.', 'error')
        return redirect(url_for('admin.users'))
    
    if user.is_admin:
        flash('لا يمكنك حذف مشرف آخر.', 'error')
        return redirect(url_for('admin.users'))
    
    username = user.username
    db.session.delete(user)
    db.session.commit()
    
    flash(f'تم حذف المستخدم {username} بنجاح.', 'success')
    return redirect(url_for('admin.users'))


@bp.route('/user/<int:user_id>/make-admin', methods=['POST'])
@admin_required
def make_admin(user_id):
    user = User.query.get_or_404(user_id)
    
    if user.id == current_user.id:
        flash('أنت مشرف بالفعل.', 'error')
        return redirect(url_for('admin.users'))
    
    user.is_admin = True
    db.session.commit()
    
    flash(f'تم ترقية {user.username} إلى مشرف.', 'success')
    return redirect(url_for('admin.users'))


@bp.route('/user/<int:user_id>/remove-admin', methods=['POST'])
@admin_required
def remove_admin(user_id):
    user = User.query.get_or_404(user_id)
    
    if user.id == current_user.id:
        flash('لا يمكنك إزالة صلاحياتك الإدارية.', 'error')
        return redirect(url_for('admin.users'))
    
    user.is_admin = False
    db.session.commit()
    
    flash(f'تم إزالة صلاحيات الإدارية من {user.username}.', 'success')
    return redirect(url_for('admin.users'))

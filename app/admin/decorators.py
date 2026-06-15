from functools import wraps
from flask import redirect, url_for, flash
from flask_login import login_required, current_user


def admin_required(f):
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            flash('غير مصرح لك بالوصول إلى هذه الصفحة.', 'error')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

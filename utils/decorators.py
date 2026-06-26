"""
utils/decorators.py
Decorator untuk Role-Based Access Control (RBAC).
"""

from functools import wraps
from flask import abort, flash, redirect, url_for
from flask_login import current_user


def admin_required(f):
    """Hanya user dengan role='admin' yang boleh mengakses route ini."""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("Silakan login terlebih dahulu.", "warning")
            return redirect(url_for("auth.login"))
        if not current_user.is_admin():
            abort(403)
        return f(*args, **kwargs)

    return decorated_function


def staff_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("Silakan login terlebih dahulu.", "warning")
            return redirect(url_for("auth.login"))
        if not current_user.is_staff():
            abort(403)
        return f(*args, **kwargs)

    return decorated_function


def order_staff_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("Silakan login terlebih dahulu.", "warning")
            return redirect(url_for("auth.login"))
        if not current_user.can_manage_orders():
            abort(403)
        return f(*args, **kwargs)

    return decorated_function


def active_user_required(f):
    """Tolak akses jika akun user dinonaktifkan admin."""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.is_authenticated and not current_user.is_active:
            flash("Akun Anda dinonaktifkan. Hubungi admin.", "danger")
            return redirect(url_for("auth.logout"))
        return f(*args, **kwargs)

    return decorated_function

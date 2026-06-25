"""
routes/admin/user_admin.py
Blueprint Manajemen User admin: lihat user, aktifkan/nonaktifkan.
"""

from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user

from utils.decorators import admin_required
from services.user_admin_service import get_all_users, toggle_user_active, UserAdminError
from services.activity_log_service import log_activity

admin_user_bp = Blueprint("admin_user", __name__, url_prefix="/admin/users")


@admin_user_bp.route("/")
@login_required
@admin_required
def index():
    users = get_all_users()
    return render_template("admin/user_list.html", users=users)


@admin_user_bp.route("/<int:user_id>/toggle-active", methods=["POST"])
@login_required
@admin_required
def toggle_active(user_id):
    try:
        user = toggle_user_active(user_id)
        status = "diaktifkan" if user.is_active else "dinonaktifkan"
        log_activity(current_user.id, "toggle_user", f"User '{user.username}' {status}")
        flash(f"User '{user.username}' telah {status}.", "info")
    except UserAdminError as e:
        flash(str(e), "danger")
    return redirect(url_for("admin_user.index"))

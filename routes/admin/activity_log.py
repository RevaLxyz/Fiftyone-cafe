"""
routes/admin/activity_log.py
Blueprint untuk melihat riwayat seluruh aktivitas admin.
"""

from flask import Blueprint, render_template
from flask_login import login_required

from utils.decorators import admin_required
from services.activity_log_admin_service import get_logs

admin_log_bp = Blueprint("admin_log", __name__, url_prefix="/admin/activity-logs")


@admin_log_bp.route("/")
@login_required
@admin_required
def index():
    logs = get_logs()
    return render_template("admin/activity_log_list.html", logs=logs)

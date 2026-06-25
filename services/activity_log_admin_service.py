"""
services/activity_log_admin_service.py
Logic untuk menampilkan riwayat activity log ke admin (paginated sederhana).
"""

from database.models import ActivityLog


def get_logs(limit: int = 100):
    return ActivityLog.query.order_by(ActivityLog.created_at.desc()).limit(limit).all()

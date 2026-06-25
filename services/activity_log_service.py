"""
services/activity_log_service.py
Service untuk mencatat seluruh aktivitas penting admin ke tabel activity_logs.
Dipanggil dari service lain (product_service, order_service, dll), bukan
langsung dari routes, agar konsisten dan mudah ditelusuri (mudah debugging).
"""

from flask import request
from database.db import db
from database.models import ActivityLog


def log_activity(user_id: int, action: str, description: str = "") -> None:
    """Simpan satu baris log aktivitas.

    Dipanggil contoh: log_activity(current_user.id, "create_product", "Menambah produk Es Kopi Susu")
    """
    try:
        ip = request.remote_addr if request else None
    except RuntimeError:
        # Dipanggil di luar application context (misal dari seeder/CLI)
        ip = None

    log = ActivityLog(
        user_id=user_id,
        action=action,
        description=description,
        ip_address=ip,
    )
    db.session.add(log)
    db.session.commit()

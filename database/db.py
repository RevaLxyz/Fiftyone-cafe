"""
database/db.py
Inisialisasi instance SQLAlchemy & LoginManager secara terpisah dari app.py
agar tidak terjadi circular import antar modul (routes, services, models).
"""

from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()

# Konfigurasi default LoginManager
login_manager.login_view = "auth.login"
login_manager.login_message = "Silakan login untuk mengakses halaman ini."
login_manager.login_message_category = "warning"


@login_manager.user_loader
def load_user(user_id):
    """Dipanggil otomatis oleh Flask-Login di setiap request untuk
    mengambil object User dari session user_id yang tersimpan."""
    from database.models import User
    return User.query.get(int(user_id))

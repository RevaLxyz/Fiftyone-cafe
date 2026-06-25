"""
services/user_admin_service.py
Logic admin untuk melihat & mengaktifkan/menonaktifkan user.
"""

from database.db import db
from database.models import User


class UserAdminError(Exception):
    pass


def get_all_users():
    return User.query.filter_by(role="user").order_by(User.created_at.desc()).all()


def get_user_by_id(user_id: int) -> User:
    user = User.query.get(user_id)
    if not user:
        raise UserAdminError("User tidak ditemukan.")
    return user


def toggle_user_active(user_id: int) -> User:
    user = get_user_by_id(user_id)
    if user.is_admin():
        raise UserAdminError("Tidak bisa menonaktifkan akun admin.")
    user.is_active = not user.is_active
    db.session.commit()
    return user

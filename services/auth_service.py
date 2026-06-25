"""
services/auth_service.py
Business logic untuk register, login, dan update profil.
Route HANYA memanggil fungsi di sini -- tidak ada query DB langsung di routes/auth.py.
"""

import logging
from database.db import db
from database.models import User

logger = logging.getLogger(__name__)


class AuthError(Exception):
    """Exception khusus untuk error pada proses autentikasi."""
    pass


def register_user(name: str, username: str, email: str, phone: str, password: str) -> User:
    if User.query.filter_by(email=email).first():
        raise AuthError("Email sudah terdaftar. Gunakan email lain.")
    if User.query.filter_by(username=username).first():
        raise AuthError("Username sudah dipakai. Pilih username lain.")

    user = User(name=name, username=username, email=email, phone=phone, role="user", is_active=True)
    user.set_password(password)

    db.session.add(user)
    db.session.commit()

    logger.info("User baru terdaftar: %s (%s)", username, email)
    return user


def authenticate_user(identifier: str, password: str) -> User:
    """identifier bisa berupa username ATAU email."""
    user = User.query.filter(
        (User.username == identifier) | (User.email == identifier)
    ).first()

    if not user or not user.check_password(password):
        raise AuthError("Username/Email atau password salah.")

    if not user.is_active:
        raise AuthError("Akun Anda telah dinonaktifkan. Hubungi admin cafe.")

    logger.info("User login: %s", identifier)
    return user


def update_profile(user: User, name: str, phone: str, address: str) -> User:
    user.name = name
    user.phone = phone
    user.address = address
    db.session.commit()

    logger.info("Profil diperbarui: %s", user.email)
    return user

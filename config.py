"""
config.py
Konfigurasi aplikasi berbasis environment variable.
Pisahkan config per environment agar mudah maintenance (dev/prod/test).
"""

import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class BaseConfig:
    """Konfigurasi dasar yang dipakai semua environment."""

    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-jangan-dipakai-di-produksi")

    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "3306")
    DB_NAME = os.getenv("DB_NAME", "cafe_db")
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")

    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,  # cegah koneksi MySQL "stale" timeout
    }

    # Upload
    UPLOAD_FOLDER_PRODUCTS = os.path.join(BASE_DIR, "static", "uploads", "products")
    UPLOAD_FOLDER_PROFILES = os.path.join(BASE_DIR, "static", "uploads", "profiles")
    UPLOAD_FOLDER_PAYMENT_PROOFS = os.path.join(BASE_DIR, "static", "uploads", "payment_proofs")
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 MB

    # CSRF (Flask-WTF aktif by default jika SECRET_KEY ada)
    WTF_CSRF_ENABLED = True

    # Logging
    LOG_FILE = os.path.join(BASE_DIR, "logs", "app.log")


class DevelopmentConfig(BaseConfig):
    DEBUG = True


class ProductionConfig(BaseConfig):
    DEBUG = False
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"


class TestingConfig(BaseConfig):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False


config_by_name = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
}


def get_config():
    env = os.getenv("FLASK_ENV", "development")
    return config_by_name.get(env, DevelopmentConfig)

"""
app.py
Entry point aplikasi Cafe Management System.
Tugas file ini HANYA: membuat Flask app, init extension, register blueprint,
setup logging, dan error handler global. Tidak ada business logic di sini.
"""

import os
import logging
from logging.handlers import RotatingFileHandler

from flask import Flask, render_template
from flask_wtf import CSRFProtect

from config import get_config
from database.db import db, login_manager


def create_app():
    app = Flask(__name__)
    app.config.from_object(get_config())

    # --- Init extensions ---
    db.init_app(app)
    login_manager.init_app(app)
    CSRFProtect(app)

    # --- Setup folder upload jika belum ada ---
    os.makedirs(app.config["UPLOAD_FOLDER_PRODUCTS"], exist_ok=True)
    os.makedirs(app.config["UPLOAD_FOLDER_PROFILES"], exist_ok=True)
    os.makedirs(app.config["UPLOAD_FOLDER_PAYMENT_PROOFS"], exist_ok=True)
    os.makedirs(os.path.dirname(app.config["LOG_FILE"]), exist_ok=True)

    # --- Setup logging ---
    setup_logging(app)

    # --- Register blueprint ---
    register_blueprints(app)

    # --- Register error handler ---
    register_error_handlers(app)

    # --- Template filter global (format rupiah dipakai di banyak halaman) ---
    from utils.helpers import format_rupiah
    app.jinja_env.filters["rupiah"] = format_rupiah

    return app


def setup_logging(app):
    handler = RotatingFileHandler(
        app.config["LOG_FILE"], maxBytes=1_000_000, backupCount=5
    )
    handler.setFormatter(
        logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    )
    handler.setLevel(logging.INFO)

    app.logger.addHandler(handler)
    app.logger.setLevel(logging.INFO)

    # Pastikan logger di modul services juga ikut tercatat ke file yang sama
    logging.getLogger().addHandler(handler)


def register_blueprints(app):
    from routes.public import public_bp
    from routes.auth import auth_bp
    from routes.menu import menu_bp
    from routes.cart import cart_bp
    from routes.order import order_bp
    from routes.review import review_bp
    from routes.admin.dashboard import admin_dashboard_bp
    from routes.admin.product import admin_product_bp
    from routes.admin.category import admin_category_bp
    from routes.admin.order_admin import admin_order_bp
    from routes.admin.user_admin import admin_user_bp
    from routes.admin.activity_log import admin_log_bp

    app.register_blueprint(public_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(menu_bp)
    app.register_blueprint(cart_bp)
    app.register_blueprint(order_bp)
    app.register_blueprint(review_bp)
    app.register_blueprint(admin_dashboard_bp)
    app.register_blueprint(admin_product_bp)
    app.register_blueprint(admin_category_bp)
    app.register_blueprint(admin_order_bp)
    app.register_blueprint(admin_user_bp)
    app.register_blueprint(admin_log_bp)


def register_error_handlers(app):
    @app.errorhandler(403)
    def forbidden(e):
        return render_template("errors/403.html"), 403

    @app.errorhandler(404)
    def not_found(e):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def server_error(e):
        app.logger.exception("Internal server error: %s", e)
        return render_template("errors/500.html"), 500


app = create_app()

if __name__ == "__main__":
    app.run(debug=app.config.get("DEBUG", True))

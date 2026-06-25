"""
routes/admin/dashboard.py
Halaman dashboard admin: ringkasan statistik + grafik penjualan.
"""

from flask import Blueprint, render_template, jsonify
from flask_login import login_required

from utils.decorators import admin_required
from services.dashboard_service import (
    get_summary,
    get_sales_chart_data,
    get_best_seller_products,
)

admin_dashboard_bp = Blueprint("admin_dashboard", __name__, url_prefix="/admin")


@admin_dashboard_bp.route("/dashboard")
@login_required
@admin_required
def index():
    summary = get_summary()
    best_sellers = get_best_seller_products()
    return render_template(
        "admin/dashboard.html",
        summary=summary,
        best_sellers=best_sellers,
    )


@admin_dashboard_bp.route("/dashboard/sales-chart")
@login_required
@admin_required
def sales_chart():
    """Endpoint JSON dikonsumsi oleh Chart.js via fetch()."""
    data = get_sales_chart_data(days=7)
    return jsonify(data)

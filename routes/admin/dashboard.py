"""
routes/admin/dashboard.py
Halaman dashboard admin: ringkasan statistik + grafik penjualan.
"""

import csv
from io import StringIO

from flask import Blueprint, render_template, jsonify, request, Response, redirect, url_for, flash
from flask_login import login_required

from utils.decorators import admin_required
from services.dashboard_service import (
    get_summary,
    get_sales_chart_data,
    get_sales_report,
    get_sales_report_summary,
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
    period = request.args.get("period", "daily")
    if period not in ("daily", "monthly"):
        period = "daily"
    data = get_sales_chart_data(period=period)
    return jsonify(data)


@admin_dashboard_bp.route("/dashboard/report/export")
@login_required
@admin_required
def export_report():
    start_date = request.args.get("start_date", "")
    end_date = request.args.get("end_date", "")
    try:
        orders = get_sales_report(start_date or None, end_date or None)
    except ValueError:
        flash("Format tanggal tidak valid.", "danger")
        return redirect(url_for("admin_dashboard.index"))

    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["Kode", "Tanggal", "Pelanggan", "Pembayaran", "Status", "Total"])
    for order in orders:
        writer.writerow([
            order.order_code,
            order.created_at.strftime("%Y-%m-%d %H:%M"),
            order.user.name,
            order.payment_method,
            order.status,
            float(order.total_price),
        ])

    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=laporan-penjualan.csv"},
    )


@admin_dashboard_bp.route("/dashboard/report/print")
@login_required
@admin_required
def print_report():
    start_date = request.args.get("start_date", "")
    end_date = request.args.get("end_date", "")
    try:
        orders = get_sales_report(start_date or None, end_date or None)
    except ValueError:
        flash("Format tanggal tidak valid.", "danger")
        return redirect(url_for("admin_dashboard.index"))
    summary = get_sales_report_summary(orders)
    return render_template(
        "admin/report_print.html",
        orders=orders,
        summary=summary,
        start_date=start_date,
        end_date=end_date,
    )

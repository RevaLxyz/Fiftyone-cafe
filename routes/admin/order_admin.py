"""
routes/admin/order_admin.py
Blueprint Manajemen Pesanan admin: lihat semua, detail, update status.
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user

from utils.decorators import order_staff_required
from services.order_admin_service import get_all_orders, get_order_by_id, update_order_status, OrderAdminError
from services.activity_log_service import log_activity
from database.models import Order

admin_order_bp = Blueprint("admin_order", __name__, url_prefix="/admin/orders")


@admin_order_bp.route("/")
@login_required
@order_staff_required
def index():
    status_filter = request.args.get("status", "")
    start_date = request.args.get("start_date", "")
    end_date = request.args.get("end_date", "")
    try:
        orders = get_all_orders(status_filter or None, start_date or None, end_date or None)
    except ValueError:
        flash("Format tanggal tidak valid.", "danger")
        return redirect(url_for("admin_order.index"))
    return render_template(
        "admin/order_list.html",
        orders=orders,
        status_filter=status_filter,
        start_date=start_date,
        end_date=end_date,
        status_choices=Order.STATUS_CHOICES,
    )


@admin_order_bp.route("/<int:order_id>")
@login_required
@order_staff_required
def detail(order_id):
    try:
        order = get_order_by_id(order_id)
    except OrderAdminError as e:
        flash(str(e), "danger")
        return redirect(url_for("admin_order.index"))
    return render_template("admin/order_detail.html", order=order, status_choices=Order.STATUS_CHOICES)


@admin_order_bp.route("/<int:order_id>/receipt")
@login_required
@order_staff_required
def receipt(order_id):
    try:
        order = get_order_by_id(order_id)
    except OrderAdminError as e:
        flash(str(e), "danger")
        return redirect(url_for("admin_order.index"))
    return render_template("admin/order_receipt.html", order=order)


@admin_order_bp.route("/<int:order_id>/update-status", methods=["POST"])
@login_required
@order_staff_required
def update_status(order_id):
    new_status = request.form.get("status")
    try:
        order = update_order_status(order_id, new_status)
        log_activity(current_user.id, "update_order_status", f"Pesanan {order.order_code} -> {new_status}")
        flash(f"Status pesanan {order.order_code} diperbarui menjadi '{new_status}'.", "success")
    except OrderAdminError as e:
        flash(str(e), "danger")
    return redirect(url_for("admin_order.detail", order_id=order_id))

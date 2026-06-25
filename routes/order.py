"""
routes/order.py
Blueprint untuk checkout, riwayat pesanan, dan detail status pesanan.
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user

from services.cart_service import get_cart_details
from services.order_service import checkout, get_user_orders, get_order_detail, upload_payment_proof, cancel_order, OrderError

order_bp = Blueprint("order", __name__, url_prefix="")


@order_bp.route("/checkout", methods=["GET", "POST"])
@login_required
def checkout_view():
    cart = get_cart_details()

    if request.method == "POST":
        payment_method = request.form.get("payment_method", "Tunai")
        notes = request.form.get("notes", "")
        try:
            order = checkout(current_user.id, payment_method, notes)
            flash(f"Pesanan {order.order_code} berhasil dibuat!", "success")
            return redirect(url_for("order.detail", order_code=order.order_code))
        except OrderError as e:
            flash(str(e), "danger")
            return redirect(url_for("cart.index"))

    return render_template("user/checkout.html", cart=cart)


@order_bp.route("/orders")
@login_required
def history():
    orders = get_user_orders(current_user.id)
    return render_template("user/order_history.html", orders=orders)


@order_bp.route("/orders/<order_code>")
@login_required
def detail(order_code):
    try:
        order = get_order_detail(order_code, current_user.id)
    except OrderError as e:
        flash(str(e), "danger")
        return redirect(url_for("order.history"))
    return render_template("user/order_detail.html", order=order)


@order_bp.route("/orders/<order_code>/payment-proof", methods=["POST"])
@login_required
def payment_proof(order_code):
    try:
        upload_payment_proof(
            order_code,
            current_user.id,
            request.files.get("payment_proof"),
            current_app.config["UPLOAD_FOLDER_PAYMENT_PROOFS"],
        )
        flash("Bukti pembayaran berhasil diupload.", "success")
    except OrderError as e:
        flash(str(e), "danger")
    return redirect(url_for("order.detail", order_code=order_code))


@order_bp.route("/orders/<order_code>/cancel", methods=["POST"])
@login_required
def cancel(order_code):
    try:
        cancel_order(order_code, current_user.id)
        flash("Pesanan berhasil dibatalkan.", "info")
    except OrderError as e:
        flash(str(e), "danger")
    return redirect(url_for("order.detail", order_code=order_code))

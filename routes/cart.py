"""
routes/cart.py
Blueprint untuk tambah, edit jumlah, dan hapus produk dari keranjang.
"""

from flask import Blueprint, render_template, redirect, url_for, request, flash

from services.cart_service import (
    add_to_cart, update_quantity, remove_from_cart, get_cart_details,
)

cart_bp = Blueprint("cart", __name__, url_prefix="/cart")


@cart_bp.route("/")
def index():
    cart = get_cart_details()
    return render_template("user/cart.html", cart=cart)


@cart_bp.route("/add", methods=["POST"])
def add():
    product_id = request.form.get("product_id", type=int)
    quantity = request.form.get("quantity", default=1, type=int)

    if not product_id:
        flash("Produk tidak valid.", "danger")
        return redirect(url_for("menu.index"))

    add_to_cart(product_id, quantity)
    flash("Produk ditambahkan ke keranjang.", "success")
    return redirect(request.referrer or url_for("menu.index"))


@cart_bp.route("/update/<int:product_id>", methods=["POST"])
def update(product_id):
    quantity = request.form.get("quantity", default=1, type=int)
    update_quantity(product_id, quantity)
    return redirect(url_for("cart.index"))


@cart_bp.route("/remove/<int:product_id>", methods=["POST"])
def remove(product_id):
    remove_from_cart(product_id)
    flash("Produk dihapus dari keranjang.", "info")
    return redirect(url_for("cart.index"))

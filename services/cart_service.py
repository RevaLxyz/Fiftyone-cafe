"""
services/cart_service.py
Keranjang belanja disimpan di session (per-browser, belum login pun bisa isi).
Struktur session['cart'] = { "<product_id>": quantity, ... }
Checkout baru memvalidasi user login.
"""

from flask import session
from database.models import Product


CART_KEY = "cart"


def _get_cart() -> dict:
    return session.get(CART_KEY, {})


def add_to_cart(product_id: int, quantity: int = 1) -> None:
    cart = _get_cart()
    pid = str(product_id)
    cart[pid] = cart.get(pid, 0) + quantity
    session[CART_KEY] = cart


def update_quantity(product_id: int, quantity: int) -> None:
    cart = _get_cart()
    pid = str(product_id)
    if quantity <= 0:
        cart.pop(pid, None)
    else:
        cart[pid] = quantity
    session[CART_KEY] = cart


def remove_from_cart(product_id: int) -> None:
    cart = _get_cart()
    cart.pop(str(product_id), None)
    session[CART_KEY] = cart


def clear_cart() -> None:
    session.pop(CART_KEY, None)


def get_cart_details() -> dict:
    """Kembalikan detail keranjang lengkap dengan info produk & subtotal,
    sekaligus membersihkan entry yang produknya sudah dihapus/nonaktif."""
    cart = _get_cart()
    items = []
    total = 0

    for pid, qty in list(cart.items()):
        product = Product.query.get(int(pid))
        if not product or not product.is_active:
            cart.pop(pid, None)
            continue

        subtotal = float(product.price) * qty
        total += subtotal
        items.append({
            "product": product,
            "quantity": qty,
            "subtotal": subtotal,
        })

    session[CART_KEY] = cart
    return {"lines": items, "total": total}


def get_cart_count() -> int:
    return sum(_get_cart().values())

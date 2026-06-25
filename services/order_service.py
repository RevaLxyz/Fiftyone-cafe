"""
services/order_service.py
Logic checkout, simpan pesanan ke database, riwayat, dan status pesanan.
"""

import logging
from database.db import db
from database.models import Order, OrderItem
from utils.helpers import generate_order_code
from services.cart_service import get_cart_details, clear_cart
from services.upload_service import save_uploaded_image, delete_image, UploadError

logger = logging.getLogger(__name__)


class OrderError(Exception):
    pass


def checkout(user_id: int, payment_method: str, notes: str = "") -> Order:
    cart = get_cart_details()

    if not cart["lines"]:
        raise OrderError("Keranjang Anda kosong. Tambahkan menu terlebih dahulu.")

    order = Order(
        order_code=generate_order_code(),
        user_id=user_id,
        status="menunggu",
        total_price=cart["total"],
        payment_method=payment_method,
        notes=notes,
    )
    db.session.add(order)
    db.session.flush()  # supaya order.id tersedia sebelum commit

    for item in cart["lines"]:
        order_item = OrderItem(
            order_id=order.id,
            product_id=item["product"].id,
            quantity=item["quantity"],
            price_at_order=item["product"].price,
            subtotal=item["subtotal"],
        )
        db.session.add(order_item)

    db.session.commit()
    clear_cart()

    logger.info("Order baru dibuat: %s oleh user_id=%s", order.order_code, user_id)
    return order


def get_user_orders(user_id: int):
    return (
        Order.query.filter_by(user_id=user_id)
        .order_by(Order.created_at.desc())
        .all()
    )


def get_order_detail(order_code: str, user_id: int = None) -> Order:
    query = Order.query.filter_by(order_code=order_code)
    if user_id is not None:
        query = query.filter_by(user_id=user_id)
    order = query.first()
    if not order:
        raise OrderError("Pesanan tidak ditemukan.")
    return order


def upload_payment_proof(order_code: str, user_id: int, file, upload_folder: str) -> Order:
    order = get_order_detail(order_code, user_id)
    if order.payment_method == "Tunai":
        raise OrderError("Pesanan tunai tidak memerlukan bukti pembayaran.")

    try:
        filename = save_uploaded_image(file, upload_folder, prefix="payment-proof")
    except UploadError as e:
        raise OrderError(str(e))

    delete_image(upload_folder, order.payment_proof)
    order.payment_proof = filename
    order.status = "diproses"
    db.session.commit()
    logger.info("Bukti pembayaran diupload: %s", order_code)
    return order


def cancel_order(order_code: str, user_id: int) -> Order:
    order = get_order_detail(order_code, user_id)
    if order.status not in ("menunggu", "diproses"):
        raise OrderError("Pesanan ini sudah tidak bisa dibatalkan.")
    order.status = "dibatalkan"
    db.session.commit()
    logger.info("Order dibatalkan: %s", order_code)
    return order

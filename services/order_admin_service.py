"""
services/order_admin_service.py
Logic admin untuk melihat semua pesanan dan update status pesanan.
"""

from database.db import db
from database.models import Order


class OrderAdminError(Exception):
    pass


def get_all_orders(status_filter: str = None):
    query = Order.query
    if status_filter:
        query = query.filter_by(status=status_filter)
    return query.order_by(Order.created_at.desc()).all()


def get_order_by_id(order_id: int) -> Order:
    order = Order.query.get(order_id)
    if not order:
        raise OrderAdminError("Pesanan tidak ditemukan.")
    return order


def update_order_status(order_id: int, new_status: str) -> Order:
    if new_status not in Order.STATUS_CHOICES:
        raise OrderAdminError("Status tidak valid.")

    order = get_order_by_id(order_id)
    order.status = new_status
    db.session.commit()
    return order

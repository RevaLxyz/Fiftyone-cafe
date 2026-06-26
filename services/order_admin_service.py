"""
services/order_admin_service.py
Logic admin untuk melihat semua pesanan dan update status pesanan.
"""

from datetime import datetime, time

from database.db import db
from database.models import Order


class OrderAdminError(Exception):
    pass


def get_all_orders(status_filter: str = None, start_date: str = None, end_date: str = None):
    query = Order.query
    if status_filter:
        query = query.filter_by(status=status_filter)
    if start_date:
        start = datetime.combine(datetime.strptime(start_date, "%Y-%m-%d").date(), time.min)
        query = query.filter(Order.created_at >= start)
    if end_date:
        end = datetime.combine(datetime.strptime(end_date, "%Y-%m-%d").date(), time.max)
        query = query.filter(Order.created_at <= end)
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
    if new_status == "dibatalkan" and order.status != "dibatalkan":
        for item in order.items:
            item.product.stock += item.quantity
    elif order.status == "dibatalkan" and new_status != "dibatalkan":
        for item in order.items:
            if item.product.stock < item.quantity:
                raise OrderAdminError(f"Stok {item.product.name} tidak mencukupi. Sisa stok: {item.product.stock}.")
        for item in order.items:
            item.product.stock -= item.quantity
    order.status = new_status
    db.session.commit()
    return order

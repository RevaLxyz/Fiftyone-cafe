"""
services/dashboard_service.py
Logic agregasi data untuk dashboard admin: total user, produk, pesanan,
pendapatan, dan data grafik penjualan.
"""

from datetime import datetime, time
from sqlalchemy import func
from database.db import db
from database.models import User, Product, Order, OrderItem


def get_summary() -> dict:
    total_user = User.query.filter_by(role="user").count()
    total_produk = Product.query.count()
    total_pesanan = Order.query.count()
    total_pendapatan = (
        db.session.query(func.coalesce(func.sum(Order.total_price), 0))
        .filter(Order.status == "selesai")
        .scalar()
    )
    return {
        "total_user": total_user,
        "total_produk": total_produk,
        "total_pesanan": total_pesanan,
        "total_pendapatan": float(total_pendapatan),
    }


def get_sales_chart_data(period: str = "daily") -> dict:
    date_expr = func.date(Order.created_at)
    limit = 7

    if period == "monthly":
        date_expr = func.date_format(Order.created_at, "%Y-%m")
        limit = 12

    results = (
        db.session.query(
            date_expr.label("periode"),
            func.sum(Order.total_price).label("total"),
        )
        .filter(Order.status == "selesai")
        .group_by(date_expr)
        .order_by(date_expr.desc())
        .limit(limit)
        .all()
    )
    results = list(reversed(results))
    return {
        "labels": [str(r.periode) for r in results],
        "values": [float(r.total) for r in results],
    }


def _parse_report_dates(start_date: str = None, end_date: str = None):
    start = None
    end = None
    if start_date:
        start = datetime.combine(datetime.strptime(start_date, "%Y-%m-%d").date(), time.min)
    if end_date:
        end = datetime.combine(datetime.strptime(end_date, "%Y-%m-%d").date(), time.max)
    return start, end


def get_sales_report(start_date: str = None, end_date: str = None) -> list:
    start, end = _parse_report_dates(start_date, end_date)
    query = Order.query.filter(Order.status == "selesai")
    if start:
        query = query.filter(Order.created_at >= start)
    if end:
        query = query.filter(Order.created_at <= end)
    return query.order_by(Order.created_at.desc()).all()


def get_sales_report_summary(orders: list) -> dict:
    return {
        "total_orders": len(orders),
        "total_revenue": sum(float(order.total_price) for order in orders),
    }


def get_best_seller_products(limit: int = 5) -> list:
    results = (
        db.session.query(
            Product.id,
            Product.name,
            func.sum(OrderItem.quantity).label("total_terjual"),
        )
        .join(OrderItem, OrderItem.product_id == Product.id)
        .group_by(Product.id, Product.name)
        .order_by(func.sum(OrderItem.quantity).desc())
        .limit(limit)
        .all()
    )
    return [{"id": r.id, "name": r.name, "total_terjual": int(r.total_terjual)} for r in results]

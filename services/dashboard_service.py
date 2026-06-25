"""
services/dashboard_service.py
Logic agregasi data untuk dashboard admin: total user, produk, pesanan,
pendapatan, dan data grafik penjualan.
"""

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


def get_sales_chart_data(days: int = 7) -> dict:
    """Data penjualan harian N hari terakhir, untuk Chart.js."""
    results = (
        db.session.query(
            func.date(Order.created_at).label("tanggal"),
            func.sum(Order.total_price).label("total"),
        )
        .filter(Order.status == "selesai")
        .group_by(func.date(Order.created_at))
        .order_by(func.date(Order.created_at).desc())
        .limit(days)
        .all()
    )
    results = list(reversed(results))
    return {
        "labels": [str(r.tanggal) for r in results],
        "values": [float(r.total) for r in results],
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

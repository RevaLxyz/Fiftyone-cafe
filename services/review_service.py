"""
services/review_service.py
Logic untuk menambah review/testimoni produk. Hanya user yang sudah
pernah memesan produk tersebut (status selesai) yang boleh memberi review,
agar testimoni kredibel.
"""

from database.db import db
from database.models import Review, OrderItem, Order


class ReviewError(Exception):
    pass


def can_review(user_id: int, product_id: int) -> bool:
    return (
        db.session.query(OrderItem)
        .join(Order, Order.id == OrderItem.order_id)
        .filter(
            Order.user_id == user_id,
            Order.status == "selesai",
            OrderItem.product_id == product_id,
        )
        .first()
        is not None
    )


def add_review(user_id: int, product_id: int, rating: int, comment: str) -> Review:
    if not can_review(user_id, product_id):
        raise ReviewError("Anda hanya bisa memberi review setelah pesanan selesai.")

    if rating < 1 or rating > 5:
        raise ReviewError("Rating harus antara 1 sampai 5.")

    review = Review(user_id=user_id, product_id=product_id, rating=rating, comment=comment)
    db.session.add(review)
    db.session.commit()
    return review

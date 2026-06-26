"""
routes/review.py
Blueprint untuk submit review/testimoni produk.
"""

from flask import Blueprint, redirect, url_for, flash, request
from flask_login import login_required, current_user

from services.review_service import add_review, ReviewError
from database.models import Product

review_bp = Blueprint("review", __name__, url_prefix="/review")


@review_bp.route("/<int:product_id>", methods=["POST"])
@login_required
def submit(product_id):
    product = Product.query.get_or_404(product_id)
    rating = request.form.get("rating", type=int, default=5)
    comment = request.form.get("comment", "")

    try:
        add_review(current_user.id, product_id, rating, comment)
        flash("Terima kasih atas review Anda!", "success")
    except ReviewError as e:
        flash(str(e), "danger")

    order_code = request.form.get("order_code")
    if order_code:
        return redirect(url_for("order.detail", order_code=order_code))

    return redirect(url_for("menu.index"))

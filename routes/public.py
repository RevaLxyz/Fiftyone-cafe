"""
routes/public.py
Halaman publik: landing page, about, contact.
"""

from flask import Blueprint, render_template
from database.models import Review
from services.menu_service import get_best_seller_products

public_bp = Blueprint("public", __name__, url_prefix="")


@public_bp.route("/")
def landing():
    best_sellers = get_best_seller_products(limit=6)
    testimonials = Review.query.order_by(Review.created_at.desc()).limit(5).all()
    return render_template(
        "public/landing.html",
        best_sellers=best_sellers,
        testimonials=testimonials,
    )


@public_bp.route("/about")
def about():
    return render_template("public/about.html")


@public_bp.route("/contact")
def contact():
    return render_template("public/contact.html")

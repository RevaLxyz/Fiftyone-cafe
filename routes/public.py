"""
routes/public.py
Halaman publik: landing page, about, contact.
"""

from flask import Blueprint, render_template
from database.models import Product, Review

public_bp = Blueprint("public", __name__, url_prefix="")


@public_bp.route("/")
def landing():
    best_sellers = (
        Product.query.filter_by(is_active=True).limit(6).all()
    )
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

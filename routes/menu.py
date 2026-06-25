"""
routes/menu.py
Blueprint untuk lihat semua menu, search, filter kategori, dan detail menu.
"""

from flask import Blueprint, render_template, request

from services.menu_service import get_menu, get_all_categories, get_product_by_slug

menu_bp = Blueprint("menu", __name__, url_prefix="/menu")


@menu_bp.route("/")
def index():
    search = request.args.get("q", "").strip()
    category_id = request.args.get("category", type=int)

    produk_list = get_menu(search=search, category_id=category_id)
    categories = get_all_categories()

    return render_template(
        "user/menu_list.html",
        produk_list=produk_list,
        categories=categories,
        search=search,
        category_id=category_id,
    )


@menu_bp.route("/<slug>")
def detail(slug):
    produk = get_product_by_slug(slug)
    if not produk:
        from flask import abort
        abort(404)
    return render_template("user/menu_detail.html", produk=produk)

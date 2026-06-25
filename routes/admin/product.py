"""
routes/admin/product.py
Blueprint untuk Manajemen Produk admin: tambah, edit, hapus, toggle aktif,
dan upload+crop foto produk (Cropper.js mengirim hasil crop sebagai base64
lewat field hidden 'cropped_image').
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user

from utils.decorators import admin_required
from forms.product_forms import ProductForm
from services.menu_service import (
    get_all_products_admin, get_product_by_id, create_product,
    update_product, delete_product, toggle_product_active,
    get_all_categories, MenuError,
)
from services.upload_service import UploadError
from services.activity_log_service import log_activity

admin_product_bp = Blueprint("admin_product", __name__, url_prefix="/admin/products")


def _populate_category_choices(form):
    form.category_id.choices = [(c.id, c.name) for c in get_all_categories()]


@admin_product_bp.route("/")
@login_required
@admin_required
def index():
    products = get_all_products_admin()
    return render_template("admin/product_list.html", products=products)


@admin_product_bp.route("/create", methods=["GET", "POST"])
@login_required
@admin_required
def create():
    form = ProductForm()
    _populate_category_choices(form)

    if form.validate_on_submit():
        try:
            product = create_product(
                name=form.name.data,
                category_id=form.category_id.data,
                description=form.description.data,
                price=form.price.data,
                stock=form.stock.data or 0,
                cropped_image_data=form.cropped_image.data or None,
                upload_folder=current_app.config["UPLOAD_FOLDER_PRODUCTS"],
            )
            log_activity(current_user.id, "create_product", f"Menambah produk '{product.name}'")
            flash("Produk berhasil ditambahkan.", "success")
            return redirect(url_for("admin_product.index"))
        except (MenuError, UploadError) as e:
            flash(str(e), "danger")

    return render_template("admin/product_form.html", form=form, mode="create")


@admin_product_bp.route("/<int:product_id>/edit", methods=["GET", "POST"])
@login_required
@admin_required
def edit(product_id):
    product = get_product_by_id(product_id)
    form = ProductForm(obj=product)
    _populate_category_choices(form)

    if request.method == "GET":
        form.category_id.data = product.category_id

    if form.validate_on_submit():
        try:
            update_product(
                product_id=product_id,
                name=form.name.data,
                category_id=form.category_id.data,
                description=form.description.data,
                price=form.price.data,
                stock=form.stock.data or 0,
                cropped_image_data=form.cropped_image.data or None,
                upload_folder=current_app.config["UPLOAD_FOLDER_PRODUCTS"],
            )
            log_activity(current_user.id, "update_product", f"Mengubah produk '{form.name.data}'")
            flash("Produk berhasil diperbarui.", "success")
            return redirect(url_for("admin_product.index"))
        except (MenuError, UploadError) as e:
            flash(str(e), "danger")

    return render_template("admin/product_form.html", form=form, mode="edit", product=product)


@admin_product_bp.route("/<int:product_id>/delete", methods=["POST"])
@login_required
@admin_required
def delete(product_id):
    try:
        product = get_product_by_id(product_id)
        nama = product.name
        delete_product(product_id, upload_folder=current_app.config["UPLOAD_FOLDER_PRODUCTS"])
        log_activity(current_user.id, "delete_product", f"Menghapus produk '{nama}'")
        flash("Produk berhasil dihapus.", "info")
    except MenuError as e:
        flash(str(e), "danger")
    return redirect(url_for("admin_product.index"))


@admin_product_bp.route("/<int:product_id>/toggle-active", methods=["POST"])
@login_required
@admin_required
def toggle_active(product_id):
    product = toggle_product_active(product_id)
    status = "diaktifkan" if product.is_active else "dinonaktifkan"
    log_activity(current_user.id, "toggle_product", f"Produk '{product.name}' {status}")
    flash(f"Produk '{product.name}' telah {status}.", "info")
    return redirect(url_for("admin_product.index"))

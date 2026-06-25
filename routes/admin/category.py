"""
routes/admin/category.py
Blueprint Manajemen Kategori admin.
"""

from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user

from utils.decorators import admin_required
from forms.product_forms import CategoryForm
from services.menu_service import (
    get_all_categories, create_category, update_category,
    delete_category, get_category_by_id, MenuError,
)
from services.activity_log_service import log_activity

admin_category_bp = Blueprint("admin_category", __name__, url_prefix="/admin/categories")


@admin_category_bp.route("/")
@login_required
@admin_required
def index():
    categories = get_all_categories()
    return render_template("admin/category_list.html", categories=categories)


@admin_category_bp.route("/create", methods=["POST"])
@login_required
@admin_required
def create():
    form = CategoryForm()
    if form.validate_on_submit():
        try:
            create_category(form.name.data)
            log_activity(current_user.id, "create_category", f"Menambah kategori '{form.name.data}'")
            flash("Kategori berhasil ditambahkan.", "success")
        except MenuError as e:
            flash(str(e), "danger")
    else:
        flash("Nama kategori tidak valid.", "danger")
    return redirect(url_for("admin_category.index"))


@admin_category_bp.route("/<int:category_id>/edit", methods=["POST"])
@login_required
@admin_required
def edit(category_id):
    form = CategoryForm()
    if form.validate_on_submit():
        try:
            update_category(category_id, form.name.data)
            log_activity(current_user.id, "update_category", f"Mengubah kategori id={category_id}")
            flash("Kategori berhasil diperbarui.", "success")
        except MenuError as e:
            flash(str(e), "danger")
    return redirect(url_for("admin_category.index"))


@admin_category_bp.route("/<int:category_id>/delete", methods=["POST"])
@login_required
@admin_required
def delete(category_id):
    try:
        category = get_category_by_id(category_id)
        nama = category.name
        delete_category(category_id)
        log_activity(current_user.id, "delete_category", f"Menghapus kategori '{nama}'")
        flash("Kategori berhasil dihapus.", "info")
    except MenuError as e:
        flash(str(e), "danger")
    return redirect(url_for("admin_category.index"))

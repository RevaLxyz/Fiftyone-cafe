"""
services/menu_service.py
Logic pencarian, filter kategori, dan detail menu untuk user.
Juga berisi fungsi CRUD produk & kategori yang dipakai modul admin.
"""

import logging
from database.db import db
from database.models import Product, Category, Order, OrderItem, Review
from utils.helpers import slugify
from services.upload_service import save_cropped_image, delete_image

logger = logging.getLogger(__name__)


class MenuError(Exception):
    pass




def get_menu(search: str = "", category_id: int = None):
    query = Product.query.filter_by(is_active=True)

    if search:
        query = query.filter(Product.name.ilike(f"%{search}%"))

    if category_id:
        query = query.filter_by(category_id=category_id)

    return query.order_by(Product.name.asc()).all()


def get_all_categories():
    return Category.query.order_by(Category.name.asc()).all()


def get_product_by_slug(slug: str):
    return Product.query.filter_by(slug=slug, is_active=True).first()


# ---------------------------------------------------------------------------
# CRUD ADMIN - PRODUK
# ---------------------------------------------------------------------------
def get_all_products_admin():
    return Product.query.order_by(Product.created_at.desc()).all()


def get_product_by_id(product_id: int) -> Product:
    product = Product.query.get(product_id)
    if not product:
        raise MenuError("Produk tidak ditemukan.")
    return product


def create_product(name, category_id, description, price, stock, cropped_image_data=None, upload_folder=None) -> Product:
    slug = slugify(name)
    if Product.query.filter_by(slug=slug).first():
        slug = f"{slug}-{Product.query.count() + 1}"

    product = Product(
        name=name,
        slug=slug,
        category_id=category_id,
        description=description,
        price=price,
        stock=stock,
        is_active=True,
    )

    if cropped_image_data and upload_folder:
        filename = save_cropped_image(cropped_image_data, upload_folder, prefix="product")
        product.image = filename

    db.session.add(product)
    db.session.commit()
    logger.info("Produk dibuat: %s", name)
    return product


def update_product(product_id, name, category_id, description, price, stock, cropped_image_data=None, upload_folder=None) -> Product:
    product = get_product_by_id(product_id)

    product.name = name
    product.category_id = category_id
    product.description = description
    product.price = price
    product.stock = stock

    if cropped_image_data and upload_folder:
        delete_image(upload_folder, product.image)
        filename = save_cropped_image(cropped_image_data, upload_folder, prefix="product")
        product.image = filename

    db.session.commit()
    logger.info("Produk diperbarui: %s (id=%s)", name, product_id)
    return product


def delete_product(product_id, upload_folder=None) -> None:
    product = get_product_by_id(product_id)
    affected_order_ids = [item.order_id for item in OrderItem.query.filter_by(product_id=product_id).all()]

    Review.query.filter_by(product_id=product_id).delete(synchronize_session=False)
    OrderItem.query.filter_by(product_id=product_id).delete(synchronize_session=False)

    for order_id in affected_order_ids:
        order = Order.query.get(order_id)
        if not order:
            continue
        if not order.items:
            db.session.delete(order)
            continue
        order.total_price = sum(item.subtotal for item in order.items)

    if upload_folder:
        delete_image(upload_folder, product.image)
    db.session.delete(product)
    db.session.commit()
    logger.info("Produk dihapus: id=%s", product_id)


def toggle_product_active(product_id) -> Product:
    product = get_product_by_id(product_id)
    product.is_active = not product.is_active
    db.session.commit()
    return product


# ---------------------------------------------------------------------------
# CRUD ADMIN - KATEGORI
# ---------------------------------------------------------------------------
def get_category_by_id(category_id: int) -> Category:
    category = Category.query.get(category_id)
    if not category:
        raise MenuError("Kategori tidak ditemukan.")
    return category


def create_category(name: str) -> Category:
    slug = slugify(name)
    if Category.query.filter_by(name=name).first():
        raise MenuError("Kategori dengan nama ini sudah ada.")
    category = Category(name=name, slug=slug)
    db.session.add(category)
    db.session.commit()
    return category


def update_category(category_id: int, name: str) -> Category:
    category = get_category_by_id(category_id)
    category.name = name
    category.slug = slugify(name)
    db.session.commit()
    return category


def delete_category(category_id: int) -> None:
    category = get_category_by_id(category_id)
    if category.products.count() > 0:
        raise MenuError("Kategori tidak bisa dihapus karena masih memiliki produk.")
    db.session.delete(category)
    db.session.commit()

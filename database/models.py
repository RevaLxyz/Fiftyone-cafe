"""
database/models.py
Seluruh model SQLAlchemy untuk sistem Cafe Management.
Relasi dan constraint mengikuti ERD: users, categories, products,
orders, order_items, reviews, activity_logs.
"""

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from database.db import db
from utils.helpers import now_jakarta


# ---------------------------------------------------------------------------
# USERS
# ---------------------------------------------------------------------------
class User(db.Model, UserMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    email = db.Column(db.String(150), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    profile_photo = db.Column(db.String(255), default="default.png")
    role = db.Column(db.Enum("admin", "staff", "kasir", "user", name="role_enum"), default="user", nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=now_jakarta)
    updated_at = db.Column(db.DateTime, default=now_jakarta, onupdate=now_jakarta)

    orders = db.relationship("Order", backref="user", lazy="dynamic")
    reviews = db.relationship("Review", backref="user", lazy="dynamic")
    activity_logs = db.relationship("ActivityLog", backref="user", lazy="dynamic")

    def set_password(self, raw_password: str) -> None:
        self.password_hash = generate_password_hash(raw_password)

    def check_password(self, raw_password: str) -> bool:
        return check_password_hash(self.password_hash, raw_password)

    def is_admin(self) -> bool:
        return self.role == "admin"

    def is_staff(self) -> bool:
        return self.role in ("admin", "staff", "kasir")

    def can_manage_orders(self) -> bool:
        return self.role in ("admin", "staff", "kasir")

    def __repr__(self):
        return f"<User {self.email} ({self.role})>"


# ---------------------------------------------------------------------------
# CATEGORIES
# ---------------------------------------------------------------------------
class Category(db.Model):
    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    slug = db.Column(db.String(120), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=now_jakarta)

    products = db.relationship("Product", backref="category", lazy="dynamic")

    def __repr__(self):
        return f"<Category {self.name}>"


# ---------------------------------------------------------------------------
# PRODUCTS
# ---------------------------------------------------------------------------
class Product(db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=False)
    name = db.Column(db.String(150), nullable=False)
    slug = db.Column(db.String(170), unique=True, nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    image = db.Column(db.String(255), default="default-product.png")
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    stock = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=now_jakarta)
    updated_at = db.Column(db.DateTime, default=now_jakarta, onupdate=now_jakarta)

    order_items = db.relationship("OrderItem", backref="product", lazy="dynamic")
    reviews = db.relationship("Review", backref="product", lazy="dynamic")

    def average_rating(self) -> float:
        reviews = self.reviews.all()
        if not reviews:
            return 0.0
        return round(sum(r.rating for r in reviews) / len(reviews), 1)

    def __repr__(self):
        return f"<Product {self.name}>"


# ---------------------------------------------------------------------------
# ORDERS
# ---------------------------------------------------------------------------
class Order(db.Model):
    __tablename__ = "orders"

    STATUS_CHOICES = (
        "menunggu",
        "diproses",
        "sedang_dibuat",
        "siap_diambil",
        "selesai",
        "dibatalkan",
    )

    id = db.Column(db.Integer, primary_key=True)
    order_code = db.Column(db.String(30), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    status = db.Column(
        db.Enum(*STATUS_CHOICES, name="order_status_enum"),
        default="menunggu",
        nullable=False,
    )
    total_price = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    payment_method = db.Column(db.String(50))
    payment_proof = db.Column(db.String(255))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=now_jakarta)
    updated_at = db.Column(db.DateTime, default=now_jakarta, onupdate=now_jakarta)

    items = db.relationship(
        "OrderItem", backref="order", lazy="select", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Order {self.order_code} - {self.status}>"


# ---------------------------------------------------------------------------
# ORDER ITEMS
# ---------------------------------------------------------------------------
class OrderItem(db.Model):
    __tablename__ = "order_items"

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    price_at_order = db.Column(db.Numeric(10, 2), nullable=False)  # snapshot harga
    subtotal = db.Column(db.Numeric(10, 2), nullable=False)

    def __repr__(self):
        return f"<OrderItem order={self.order_id} product={self.product_id}>"


# ---------------------------------------------------------------------------
# REVIEWS
# ---------------------------------------------------------------------------
class Review(db.Model):
    __tablename__ = "reviews"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    rating = db.Column(db.SmallInteger, nullable=False)  # 1-5
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=now_jakarta)

    __table_args__ = (
        db.CheckConstraint("rating >= 1 AND rating <= 5", name="check_rating_range"),
    )

    def __repr__(self):
        return f"<Review product={self.product_id} rating={self.rating}>"


# ---------------------------------------------------------------------------
# ACTIVITY LOGS
# ---------------------------------------------------------------------------
class ActivityLog(db.Model):
    __tablename__ = "activity_logs"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    action = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    ip_address = db.Column(db.String(45))
    created_at = db.Column(db.DateTime, default=now_jakarta)

    def __repr__(self):
        return f"<ActivityLog {self.action} by user={self.user_id}>"

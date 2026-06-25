"""
database/seeders.py
Seeder data dummy realistis (bukan "Produk 1", "Produk 2") agar demo lomba
terlihat profesional. Jalankan dengan: flask --app app.py shell, lalu:
    from database.seeders import run_seeder; run_seeder()
atau buat CLI command terpisah jika diinginkan di fase lanjutan.
"""

from database.db import db
from database.models import User, Category, Product
from utils.helpers import slugify


def run_seeder():
    # --- Admin default ---
    if not User.query.filter_by(email="admin@cafe.com").first():
        admin = User(name="Admin Cafe", username="admin", email="admin@cafe.com", role="admin", is_active=True)
        admin.set_password("admin123")
        db.session.add(admin)

    # --- User demo ---
    if not User.query.filter_by(email="user@cafe.com").first():
        user = User(name="Budi Santoso", username="budisantoso", email="user@cafe.com", role="user", is_active=True)
        user.set_password("user1234")
        db.session.add(user)

    db.session.commit()

    # --- Kategori ---
    kategori_list = ["Kopi", "Non-Kopi", "Makanan Berat", "Snack", "Dessert"]
    kategori_objs = {}
    for nama in kategori_list:
        existing = Category.query.filter_by(name=nama).first()
        if not existing:
            existing = Category(name=nama, slug=slugify(nama))
            db.session.add(existing)
        kategori_objs[nama] = existing

    db.session.commit()

    # --- Produk ---
    produk_list = [
        ("Es Kopi Susu Gula Aren", "Kopi", 22000, "Kopi susu signature dengan gula aren asli."),
        ("Americano", "Kopi", 18000, "Espresso dengan air panas, ringan dan kuat."),
        ("Matcha Latte", "Non-Kopi", 25000, "Matcha premium dengan susu segar."),
        ("Chocolate Frappe", "Non-Kopi", 27000, "Coklat blended dingin, manis dan creamy."),
        ("Nasi Goreng Cafe", "Makanan Berat", 32000, "Nasi goreng spesial dengan telur dan ayam."),
        ("Croissant Almond", "Snack", 20000, "Croissant renyah dengan topping almond."),
        ("Tiramisu Cup", "Dessert", 28000, "Tiramisu lembut dalam cup, favorit pelanggan."),
    ]
    for nama, kategori, harga, desc in produk_list:
        if not Product.query.filter_by(name=nama).first():
            produk = Product(
                category_id=kategori_objs[kategori].id,
                name=nama,
                slug=slugify(nama),
                description=desc,
                price=harga,
                is_active=True,
                stock=50,
            )
            db.session.add(produk)

    db.session.commit()
    print("Seeder selesai. Login admin: admin@cafe.com / admin123")

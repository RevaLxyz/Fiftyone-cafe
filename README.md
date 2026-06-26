# D'51 Cafe - Cafe Management System

Sistem manajemen cafe berbasis **Flask + MySQL + SQLAlchemy**, dibangun dengan
Clean Architecture (Route → Service → Model) agar mudah dikembangkan dan didebug.

## Status Pengerjaan — SELESAI ✅

✅ Fase 0 — Setup project, struktur folder, config
✅ Fase 1 — Database models (users, categories, products, orders, order_items, reviews, activity_logs)
✅ Fase 2 — Auth & RBAC (register, login pakai username/email, logout, edit profil, show/hide password, hashing password)
✅ Fase 3 — Menu (search & filter), Cart (session-based), Checkout, Riwayat & Detail Status Pesanan
✅ Fase 4 — Modul admin lengkap: CRUD Produk, Kategori, Pesanan (update status), User (aktif/nonaktif)
✅ Fase 5 — Upload & Crop foto produk (Cropper.js, rasio wajib 1:1), Activity Log, Review/testimoni
✅ Dashboard admin dengan Chart.js (grafik penjualan 7 hari + produk terlaris)

## Cara Menjalankan

1. **Buat virtual environment & install dependency**
   ```bash
   python -m venv venv
   source venv/bin/activate   # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Siapkan database MySQL**
   ```sql
   CREATE DATABASE cafe_db;
   ```

3. **Copy `.env.example` ke `.env`** lalu sesuaikan kredensial database:
   ```bash
   cp .env.example .env
   ```

4. **Buat tabel & isi data demo**
   ```bash
   flask --app app.py shell
   >>> from database.db import db
   >>> db.create_all()
   >>> from database.seeders import run_seeder
   >>> run_seeder()
   >>> exit()
   ```

5. **Jalankan server**
   ```bash
   flask --app app.py run --debug
   ```
   Buka `http://127.0.0.1:5000`

## Akun Demo (setelah seeder)
| Role | Username | Password |
|---|---|---|
| Admin | `admin` | `admin123` |
| User | `budisantoso` | `user1234` |

Login bisa pakai **username ATAU email**, keduanya berfungsi sesuai preferensi.

## Struktur Arsitektur

```
Routes (HTTP layer)  →  Services (business logic)  →  Models (ORM/data layer)
```

Routes **tidak pernah** melakukan query database langsung — semua lewat
`services/`. Ini membuat logic mudah ditest, mudah dipindah, dan mudah
didebug karena satu fungsi = satu tanggung jawab.

## Keamanan yang Diterapkan
- Password hashing (`werkzeug.security`, PBKDF2)
- CSRF protection di semua form (Flask-WTF)
- Validasi form server-side (WTForms validators)
- RBAC via decorator `@admin_required`
- Session management via Flask-Login
- Validasi rasio gambar 1:1 divalidasi ulang di server (bukan hanya client)

## Fitur Lengkap

**User:**
- Landing page (hero, about, best seller, testimoni, kontak) dengan branding D'51 Cafe
- Register/Login (username atau email) dengan toggle show/hide password
- Menu: search, filter kategori, detail produk + review
- Keranjang: tambah, edit jumlah, hapus
- Checkout → simpan ke database
- Riwayat pesanan + tracking status (menunggu → diproses → sedang dibuat → siap diambil → selesai/dibatalkan)

**Admin:**
- Dashboard: total user/produk/pesanan/pendapatan + grafik penjualan + produk terlaris
- CRUD Produk + Upload & Crop foto (Cropper.js, rasio wajib 1:1)
- CRUD Kategori
- Manajemen Pesanan (update status)
- Manajemen User (aktif/nonaktif)
- Activity Log (mencatat semua aksi admin otomatis)

## Catatan Teknis
- Semua aktivitas penting (tambah/edit/hapus produk, update pesanan, dll) otomatis
  tercatat ke `activity_logs` lewat `services/activity_log_service.py`.
- Logging aplikasi tersimpan di `logs/app.log` (rotating file handler).
- Sudah diuji end-to-end (auth, cart, checkout, admin CRUD, upload+crop) menggunakan
  SQLite in-memory sebelum dikirim — siap dijalankan dengan MySQL sesuai konfigurasi `.env`.

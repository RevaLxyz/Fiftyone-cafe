"""
services/upload_service.py
Logic simpan file upload hasil crop (dari Cropper.js, dikirim sebagai base64
dataURL via form) untuk foto produk maupun foto profil.
Validasi: rasio 1:1 dipaksa di sisi client (Cropper.js), di server kita
re-validasi dimensi sebagai pertahanan kedua.
"""

import os
import uuid
import base64
import io
from werkzeug.utils import secure_filename
from PIL import Image

ALLOWED_EXT = {"png", "jpg", "jpeg", "webp"}


class UploadError(Exception):
    pass


def _decode_base64_image(data_url: str) -> Image.Image:
    """data_url contoh: 'data:image/png;base64,iVBORw0KG...' """
    try:
        header, encoded = data_url.split(",", 1)
        binary_data = base64.b64decode(encoded)
        image = Image.open(io.BytesIO(binary_data))
        return image
    except Exception:
        raise UploadError("Format gambar tidak valid.")


def save_cropped_image(data_url: str, folder: str, prefix: str = "product") -> str:
    """Simpan gambar hasil crop (base64 dataURL) ke folder upload.
    Mengembalikan nama file yang tersimpan (bukan path lengkap)."""

    image = _decode_base64_image(data_url)

    # Validasi rasio 1:1 (toleransi kecil untuk pembulatan)
    width, height = image.size
    if abs(width - height) > 5:
        raise UploadError("Gambar harus berbentuk persegi (rasio 1:1).")

    image = image.convert("RGB")  # hindari error simpan PNG transparan ke JPG

    filename = f"{prefix}-{uuid.uuid4().hex[:10]}.jpg"
    filepath = os.path.join(folder, filename)

    os.makedirs(folder, exist_ok=True)
    image.save(filepath, "JPEG", quality=85)

    return filename


def save_uploaded_image(file, folder: str, prefix: str = "upload") -> str:
    if not file or not file.filename:
        raise UploadError("File gambar wajib diisi.")

    filename = secure_filename(file.filename)
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext not in ALLOWED_EXT:
        raise UploadError("Format gambar harus png, jpg, jpeg, atau webp.")

    image = Image.open(file.stream)
    image.verify()
    file.stream.seek(0)

    filename = f"{prefix}-{uuid.uuid4().hex[:10]}.{ext}"
    filepath = os.path.join(folder, filename)
    os.makedirs(folder, exist_ok=True)
    file.save(filepath)
    return filename


def delete_image(folder: str, filename: str) -> None:
    if not filename or filename.startswith("default"):
        return
    filepath = os.path.join(folder, filename)
    if os.path.exists(filepath):
        os.remove(filepath)

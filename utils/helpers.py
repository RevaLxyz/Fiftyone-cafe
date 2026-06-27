"""
utils/helpers.py
Fungsi bantu lintas modul: generate kode pesanan, slug, format rupiah.
"""

import re
import uuid
from datetime import datetime
from zoneinfo import ZoneInfo


def now_jakarta():
    return datetime.now(ZoneInfo("Asia/Jakarta")).replace(tzinfo=None)


def generate_order_code() -> str:
    """Hasilkan kode unik: CFE-20260622-AB12CD"""
    today = now_jakarta().strftime("%Y%m%d")
    unique_part = uuid.uuid4().hex[:6].upper()
    return f"CFE-{today}-{unique_part}"


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


def format_rupiah(amount) -> str:
    try:
        amount = float(amount)
    except (TypeError, ValueError):
        amount = 0
    return f"Rp{amount:,.0f}".replace(",", ".")

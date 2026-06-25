"""
forms/product_forms.py
Form validasi untuk CRUD Produk & Kategori di admin.
"""

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DecimalField, IntegerField, SelectField
from wtforms.validators import DataRequired, Length, NumberRange, Optional


class ProductForm(FlaskForm):
    name = StringField("Nama Produk", validators=[DataRequired(), Length(min=3, max=150)])
    category_id = SelectField("Kategori", coerce=int, validators=[DataRequired()])
    description = TextAreaField("Deskripsi", validators=[Optional(), Length(max=500)])
    price = DecimalField("Harga", validators=[DataRequired(), NumberRange(min=0)])
    stock = IntegerField("Stok", validators=[Optional(), NumberRange(min=0)], default=0)
    cropped_image = StringField("Gambar (base64)", validators=[Optional()])


class CategoryForm(FlaskForm):
    name = StringField("Nama Kategori", validators=[DataRequired(), Length(min=2, max=100)])

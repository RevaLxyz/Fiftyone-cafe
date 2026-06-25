"""
forms/auth_forms.py
Form validasi untuk Register, Login, dan Edit Profil menggunakan Flask-WTF.
CSRF token otomatis aktif selama app punya SECRET_KEY.
"""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField
from wtforms.validators import (
    DataRequired,
    Email,
    Length,
    EqualTo,
    Optional,
    Regexp,
)


class RegisterForm(FlaskForm):
    name = StringField("Nama Lengkap", validators=[DataRequired(), Length(min=3, max=100)])
    username = StringField(
        "Username",
        validators=[DataRequired(), Length(min=3, max=50), Regexp(
            r"^[a-zA-Z0-9_]+$", message="Username hanya boleh huruf, angka, dan underscore."
        )],
    )
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=150)])
    phone = StringField("No. HP", validators=[Optional(), Length(max=20)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField(
        "Konfirmasi Password",
        validators=[DataRequired(), EqualTo("password", message="Password tidak cocok.")],
    )


class LoginForm(FlaskForm):
    identifier = StringField("Username atau Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])


class EditProfileForm(FlaskForm):
    name = StringField("Nama Lengkap", validators=[DataRequired(), Length(min=3, max=100)])
    phone = StringField("No. HP", validators=[Optional(), Length(max=20)])
    address = TextAreaField("Alamat", validators=[Optional(), Length(max=500)])

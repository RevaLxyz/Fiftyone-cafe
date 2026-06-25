"""
routes/auth.py
Blueprint untuk Register, Login, Logout, Edit Profil.
HANYA menangani request/response -- semua logic ada di services/auth_service.py
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user

from forms.auth_forms import RegisterForm, LoginForm, EditProfileForm
from services.auth_service import register_user, authenticate_user, update_profile, AuthError

auth_bp = Blueprint("auth", __name__, url_prefix="")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("public.landing"))

    form = RegisterForm()
    if form.validate_on_submit():
        try:
            register_user(
                name=form.name.data,
                username=form.username.data,
                email=form.email.data,
                phone=form.phone.data,
                password=form.password.data,
            )
            flash("Registrasi berhasil! Silakan login.", "success")
            return redirect(url_for("auth.login"))
        except AuthError as e:
            flash(str(e), "danger")

    return render_template("auth/register.html", form=form)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("public.landing"))

    form = LoginForm()
    if form.validate_on_submit():
        try:
            user = authenticate_user(form.identifier.data, form.password.data)
            login_user(user)
            flash(f"Selamat datang, {user.name}!", "success")

            if user.is_admin():
                return redirect(url_for("admin_dashboard.index"))
            next_page = request.args.get("next")
            return redirect(next_page or url_for("public.landing"))
        except AuthError as e:
            flash(str(e), "danger")

    return render_template("auth/login.html", form=form)


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Anda telah logout.", "info")
    return redirect(url_for("public.landing"))


@auth_bp.route("/profile/edit", methods=["GET", "POST"])
@login_required
def edit_profile():
    form = EditProfileForm(obj=current_user)
    if form.validate_on_submit():
        update_profile(
            current_user,
            name=form.name.data,
            phone=form.phone.data,
            address=form.address.data,
        )
        flash("Profil berhasil diperbarui.", "success")
        return redirect(url_for("auth.edit_profile"))

    if request.method == "GET":
        form.name.data = current_user.name
        form.phone.data = current_user.phone
        form.address.data = current_user.address

    return render_template("auth/edit_profile.html", form=form)

from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/signup", methods=["GET", "POST"])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for("tables.my_tables"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")

        # Validation
        errors = []
        if not username or len(username) < 3:
            errors.append("Username must be at least 3 characters.")
        if not email or "@" not in email:
            errors.append("Valid email is required.")
        if not password or len(password) < 6:
            errors.append("Password must be at least 6 characters.")
        if password != confirm:
            errors.append("Passwords do not match.")
        if User.query.filter_by(username=username).first():
            errors.append("Username already taken.")
        if User.query.filter_by(email=email).first():
            errors.append("Email already registered.")

        if errors:
            for e in errors:
                flash(e, "danger")
            return render_template("auth/signup.html", username=username, email=email)

        pw_hash = current_app.extensions['bcrypt'].generate_password_hash(password).decode("utf-8")
        user = User(username=username, email=email, password_hash=pw_hash)
        db.session.add(user)
        db.session.commit()

        login_user(user)
        flash("Account created! Welcome to the tavern.", "success")
        return redirect(url_for("tables.my_tables"))

    return render_template("auth/signup.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("tables.my_tables"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        user = User.query.filter_by(username=username).first()
        if user and current_app.extensions['bcrypt'].check_password_hash(user.password_hash, password):
            login_user(user)
            flash("Welcome back, adventurer!", "success")
            next_page = request.args.get("next")
            return redirect(next_page or url_for("tables.my_tables"))

        flash("Invalid username or password.", "danger")
        return render_template("auth/login.html", username=username)

    return render_template("auth/login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have left the tavern.", "info")
    return redirect(url_for("auth.login"))

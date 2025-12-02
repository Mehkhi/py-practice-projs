"""Authentication routes."""

import logging
from typing import Tuple

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from app.services.auth_service import authenticate_user, register_user
from app.utils.exceptions import ValidationError

logger = logging.getLogger(__name__)

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["GET", "POST"])
def register() -> str | redirect:
    """Handle user registration.

    Returns:
        Registration form or redirect to login on success
    """
    if current_user.is_authenticated:
        return redirect(url_for("tasks.list_tasks"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        # Validation
        if not username or not email or not password:
            flash("All fields are required.", "error")
            return render_template("auth/register.html")

        if len(password) < 6:
            flash("Password must be at least 6 characters long.", "error")
            return render_template("auth/register.html")

        try:
            user = register_user(username, email, password)
            login_user(user)
            flash("Registration successful! Welcome!", "success")
            logger.info(f"User {username} registered and logged in")
            return redirect(url_for("tasks.list_tasks"))
        except ValidationError as e:
            flash(str(e), "error")
            logger.warning(f"Registration failed: {e}")

    return render_template("auth/register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login() -> str | redirect:
    """Handle user login.

    Returns:
        Login form or redirect to tasks on success
    """
    if current_user.is_authenticated:
        return redirect(url_for("tasks.list_tasks"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not username or not password:
            flash("Username and password are required.", "error")
            return render_template("auth/login.html")

        user = authenticate_user(username, password)

        if user:
            remember = request.form.get("remember") == "on"
            login_user(user, remember=remember)
            flash("Login successful!", "success")
            logger.info(f"User {username} logged in")
            next_page = request.args.get("next")
            return redirect(next_page or url_for("tasks.list_tasks"))
        else:
            flash("Invalid username or password.", "error")
            logger.warning(f"Failed login attempt for user: {username}")

    return render_template("auth/login.html")


@auth_bp.route("/logout")
@login_required
def logout() -> redirect:
    """Handle user logout.

    Returns:
        Redirect to login page
    """
    username = current_user.username
    logout_user()
    flash("You have been logged out.", "info")
    logger.info(f"User {username} logged out")
    return redirect(url_for("auth.login"))

"""Route definitions for the microblog application."""

from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_user, logout_user, login_required, current_user
from microblog import db, login_manager
from microblog.models import User, Post
from microblog.forms import LoginForm, RegistrationForm, PostForm
from urllib.parse import urlparse, urljoin
import logging

# Create blueprints
main_bp = Blueprint("main", __name__)
auth_bp = Blueprint("auth", __name__)

# Configure logger
logger = logging.getLogger(__name__)


def _is_safe_redirect(target: str) -> bool:
    """Ensure redirect target stays within application host."""
    if not target:
        return False
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return (
        test_url.scheme in ("http", "https")
        and ref_url.netloc == test_url.netloc
    )


@login_manager.user_loader
def load_user(user_id: int):
    """Load user by ID for Flask-Login.

    Args:
        user_id: User ID to load

    Returns:
        User object or None
    """
    return User.query.get(int(user_id))


@main_bp.route("/")
def index():
    """Home page showing all posts."""
    try:
        page = request.args.get("page", 1, type=int)
        posts = Post.query.order_by(Post.created_at.desc()).paginate(
            page=page, per_page=10, error_out=False
        )
        logger.info(f"Home page accessed, showing {len(posts.items)} posts")
        return render_template("index.html", posts=posts)
    except Exception as e:
        logger.error(f"Error loading home page: {e}")
        flash("Error loading posts. Please try again.", "error")
        return render_template("index.html", posts=None)


@main_bp.route("/post/<int:post_id>")
def view_post(post_id: int):
    """View a single post.

    Args:
        post_id: ID of the post to view
    """
    try:
        post = Post.query.get_or_404(post_id)
        logger.info(f"Post {post_id} viewed")
        return render_template("view_post.html", post=post)
    except Exception as e:
        logger.error(f"Error viewing post {post_id}: {e}")
        abort(404)


@main_bp.route("/create", methods=["GET", "POST"])
@login_required
def create_post():
    """Create a new post."""
    form = PostForm()
    if form.validate_on_submit():
        try:
            post = Post(
                title=form.title.data,
                content=form.content.data,
                user_id=current_user.id
            )
            db.session.add(post)
            db.session.commit()
            logger.info(f"Post created: {post.title} by user {current_user.username}")
            flash("Your post has been created!", "success")
            return redirect(url_for("main.index"))
        except Exception as e:
            logger.error(f"Error creating post: {e}")
            db.session.rollback()
            flash("Error creating post. Please try again.", "error")

    return render_template("create_post.html", form=form)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """User login page."""
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            logger.info(f"User {user.username} logged in")
            flash("Login successful!", "success")
            next_page = request.args.get("next")
            if next_page and _is_safe_redirect(next_page):
                return redirect(next_page)
            return redirect(url_for("main.index"))
        else:
            logger.warning(f"Failed login attempt for username: {form.username.data}")
            flash("Invalid username or password", "error")

    return render_template("login.html", form=form)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    """User registration page."""
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    form = RegistrationForm()
    if form.validate_on_submit():
        try:
            user = User(
                username=form.username.data,
                email=form.email.data,
                password=form.password.data,
                bio=form.bio.data
            )
            db.session.add(user)
            db.session.commit()
            logger.info(f"New user registered: {user.username}")
            flash("Registration successful! Please log in.", "success")
            return redirect(url_for("auth.login"))
        except Exception as e:
            logger.error(f"Error registering user: {e}")
            db.session.rollback()
            flash("Registration failed. Please try again.", "error")

    return render_template("register.html", form=form)


@auth_bp.route("/logout")
@login_required
def logout():
    """User logout."""
    username = current_user.username
    logout_user()
    logger.info(f"User {username} logged out")
    flash("You have been logged out.", "info")
    return redirect(url_for("main.index"))


@main_bp.route("/profile/<username>")
def profile(username: str):
    """View user profile.

    Args:
        username: Username to view profile for
    """
    try:
        user = User.query.filter_by(username=username).first_or_404()
        page = request.args.get("page", 1, type=int)
        posts = Post.query.filter_by(user_id=user.id).order_by(
            Post.created_at.desc()
        ).paginate(page=page, per_page=10, error_out=False)

        logger.info(f"Profile viewed: {username}")
        return render_template("profile.html", user=user, posts=posts)
    except Exception as e:
        logger.error(f"Error viewing profile {username}: {e}")
        abort(404)

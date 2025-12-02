"""Database models for the microblog application."""

from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from microblog import db


def current_utc_time() -> datetime:
    """Return the current UTC time as a timezone-aware datetime."""
    return datetime.now(timezone.utc)


class User(UserMixin, db.Model):
    """User model for authentication and user information."""

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    bio = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), default=current_utc_time)

    # Relationships
    posts = db.relationship("Post", backref="author", lazy="dynamic", cascade="all, delete-orphan")

    def __init__(self, username: str, email: str, password: str, bio: str = None):
        """Initialize a new user.

        Args:
            username: Unique username
            email: Unique email address
            password: Plain text password (will be hashed)
            bio: Optional user biography
        """
        self.username = username
        self.email = email
        self.set_password(password)
        self.bio = bio

    def set_password(self, password: str) -> None:
        """Set password hash from plain text password.

        Args:
            password: Plain text password
        """
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Check if provided password matches stored hash.

        Args:
            password: Plain text password to check

        Returns:
            True if password matches, False otherwise
        """
        return check_password_hash(self.password_hash, password)

    def __repr__(self) -> str:
        """Return string representation of user."""
        return f"<User {self.username}>"


class Post(db.Model):
    """Post model for blog posts."""

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=current_utc_time, index=True)
    updated_at = db.Column(
        db.DateTime(timezone=True),
        default=current_utc_time,
        onupdate=current_utc_time,
    )

    # Foreign key
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    def __init__(self, title: str, content: str, user_id: int):
        """Initialize a new post.

        Args:
            title: Post title
            content: Post content
            user_id: ID of the author
        """
        self.title = title
        self.content = content
        self.user_id = user_id

    def __repr__(self) -> str:
        """Return string representation of post."""
        return f"<Post {self.title}>"

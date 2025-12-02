"""User model with authentication support."""

from datetime import datetime
from typing import TYPE_CHECKING

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from app import db

if TYPE_CHECKING:
    from app.models.task import Task


class User(UserMixin, db.Model):  # type: ignore
    """User model for authentication and task ownership.

    Attributes:
        id: Primary key
        username: Unique username
        email: Unique email address
        password_hash: Hashed password
        created_at: Account creation timestamp
        tasks: Relationship to user's tasks
    """

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationship
    tasks = db.relationship(
        "Task",
        back_populates="user",
        lazy="dynamic",
        cascade="all, delete-orphan",
        foreign_keys="Task.user_id",
    )
    time_entries = db.relationship("TimeEntry", back_populates="user", cascade="all")
    audit_logs = db.relationship("AuditLog", back_populates="user", cascade="all")
    templates = db.relationship("TaskTemplate", backref="creator", cascade="all")
    notes = db.relationship("TaskNote", back_populates="author", cascade="all")
    attachments = db.relationship("TaskAttachment", back_populates="author", cascade="all")

    def set_password(self, password: str) -> None:
        """Set password hash from plain text password.

        Args:
            password: Plain text password to hash
        """
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Check if provided password matches stored hash.

        Args:
            password: Plain text password to verify

        Returns:
            True if password matches, False otherwise
        """
        return check_password_hash(self.password_hash, password)

    def __repr__(self) -> str:
        """String representation of User."""
        return f"<User {self.username}>"

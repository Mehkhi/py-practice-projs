"""Task model for to-do items."""

from datetime import datetime
from typing import TYPE_CHECKING

from app import db

if TYPE_CHECKING:
    from app.models.user import User


class Task(db.Model):  # type: ignore
    """Task model representing a to-do item with rich workflow metadata."""

    __tablename__ = "tasks"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    completed = db.Column(db.Boolean, default=False, nullable=False, index=True)
    status = db.Column(db.String(20), default="backlog", nullable=False, index=True)
    priority = db.Column(db.String(20), default="medium", nullable=False, index=True)
    category = db.Column(db.String(50), default="General", nullable=True, index=True)
    due_date = db.Column(db.DateTime, nullable=True, index=True)
    started_at = db.Column(db.DateTime, nullable=True, index=True)
    completed_at = db.Column(db.DateTime, nullable=True, index=True)
    size_points = db.Column(db.Integer, default=1, nullable=False)
    recurrence_interval_days = db.Column(db.Integer, nullable=True)
    recurrence_end_date = db.Column(db.Date, nullable=True)
    requires_approval = db.Column(db.Boolean, default=False, nullable=False)
    approved_at = db.Column(db.DateTime, nullable=True)
    approved_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    blocked_reason = db.Column(db.Text, nullable=True)
    blocked_started_at = db.Column(db.DateTime, nullable=True)
    blocked_minutes_total = db.Column(db.Integer, default=0, nullable=False)
    kanban_order = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    template_id = db.Column(db.Integer, db.ForeignKey("task_templates.id"), nullable=True)

    # Foreign key
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)

    # Relationship
    user = db.relationship("User", back_populates="tasks", foreign_keys=[user_id])
    approver = db.relationship("User", foreign_keys=[approved_by])
    template = db.relationship("TaskTemplate", back_populates="tasks")
    dependencies = db.relationship(
        "TaskDependency",
        foreign_keys="TaskDependency.task_id",
        back_populates="task",
        cascade="all, delete-orphan",
        lazy="joined",
    )
    dependents = db.relationship(
        "TaskDependency",
        foreign_keys="TaskDependency.depends_on_id",
        back_populates="depends_on",
        cascade="all, delete-orphan",
        lazy="joined",
    )
    time_entries = db.relationship(
        "TimeEntry", back_populates="task", cascade="all, delete-orphan"
    )
    notes = db.relationship("TaskNote", back_populates="task", cascade="all, delete-orphan")
    attachments = db.relationship(
        "TaskAttachment", back_populates="task", cascade="all, delete-orphan"
    )
    audit_logs = db.relationship("AuditLog", back_populates="task", cascade="all, delete-orphan")

    def toggle_completed(self) -> None:
        """Toggle the completion status of the task."""
        new_status = not self.completed
        self.set_completion(new_status)

    def set_completion(self, value: bool) -> None:
        """Set completion value and manage lifecycle timestamps."""
        self.completed = value
        self.status = "done" if value else "backlog"
        now = datetime.utcnow()
        if value:
            self.completed_at = now
        else:
            self.completed_at = None
        self.updated_at = now

    def enter_status(self, status: str) -> None:
        """Move task to a new status and bookend lifecycle values."""
        now = datetime.utcnow()
        if status == "in_progress" and not self.started_at:
            self.started_at = now
        if status == "done":
            self.set_completion(True)
        else:
            self.status = status
            self.completed = status == "done"
            self.updated_at = now

        if status == "blocked":
            self.blocked_started_at = now
        elif self.blocked_started_at:
            delta = now - self.blocked_started_at
            self.blocked_minutes_total += max(0, int(delta.total_seconds() // 60))
            self.blocked_started_at = None

    def __repr__(self) -> str:
        """String representation of Task."""
        return f"<Task {self.id}: {self.title[:30]}>"

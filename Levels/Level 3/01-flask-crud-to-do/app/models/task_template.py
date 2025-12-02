"""Task templates for reusable workflows."""

from datetime import datetime

from app import db


class TaskTemplate(db.Model):  # type: ignore
    """Reusable template that can stamp out new tasks with defaults."""

    __tablename__ = "task_templates"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False, unique=True, index=True)
    description = db.Column(db.Text, nullable=True)
    default_priority = db.Column(db.String(20), default="medium", nullable=False)
    default_status = db.Column(db.String(20), default="backlog", nullable=False)
    default_size_points = db.Column(db.Integer, default=1, nullable=False)
    default_recurrence_interval_days = db.Column(db.Integer, nullable=True)
    default_requires_approval = db.Column(db.Boolean, default=False, nullable=False)
    default_checklist = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)

    # Relationships
    tasks = db.relationship("Task", back_populates="template", lazy="dynamic")

    def __repr__(self) -> str:
        return f"<TaskTemplate {self.name}>"

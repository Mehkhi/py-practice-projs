"""Task attachments for knowledge hub."""

from datetime import datetime

from app import db


class TaskAttachment(db.Model):  # type: ignore
    """A simple link-style attachment for a task."""

    __tablename__ = "task_attachments"

    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey("tasks.id"), nullable=False, index=True)
    title = db.Column(db.String(255), nullable=False)
    url = db.Column(db.Text, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)

    task = db.relationship("Task", back_populates="attachments")
    author = db.relationship("User", back_populates="attachments")

    def __repr__(self) -> str:  # pragma: no cover - simple repr
        return f"<Attachment {self.title} for task {self.task_id}>"

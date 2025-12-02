"""Knowledge hub notes attached to tasks."""

from datetime import datetime

from app import db


class TaskNote(db.Model):  # type: ignore
    """Rich note or acceptance criteria entry for a task."""

    __tablename__ = "task_notes"

    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey("tasks.id"), nullable=False, index=True)
    content = db.Column(db.Text, nullable=False)
    kind = db.Column(db.String(32), default="note", nullable=False, index=True)
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)

    task = db.relationship("Task", back_populates="notes")
    author = db.relationship("User", back_populates="notes")

    def __repr__(self) -> str:  # pragma: no cover - simple repr
        return f"<TaskNote task={self.task_id} kind={self.kind}>"

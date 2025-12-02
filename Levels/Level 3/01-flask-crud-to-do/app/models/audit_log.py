"""Audit trail entries for collaboration and approvals."""

from datetime import datetime

from app import db


class AuditLog(db.Model):  # type: ignore
    """Tracks who did what and when."""

    __tablename__ = "audit_logs"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True, index=True)
    task_id = db.Column(db.Integer, db.ForeignKey("tasks.id"), nullable=True, index=True)
    action = db.Column(db.String(120), nullable=False)
    details = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)

    user = db.relationship("User", back_populates="audit_logs")
    task = db.relationship("Task", back_populates="audit_logs")

    def __repr__(self) -> str:  # pragma: no cover - simple repr
        return f"<AuditLog {self.action} task={self.task_id}>"

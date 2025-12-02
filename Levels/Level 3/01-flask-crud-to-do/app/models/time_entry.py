"""Time tracking entries for tasks."""

from datetime import datetime

from app import db


class TimeEntry(db.Model):  # type: ignore
    """Represents a time tracking session."""

    __tablename__ = "time_entries"

    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey("tasks.id"), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    started_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    ended_at = db.Column(db.DateTime, nullable=True)
    duration_minutes = db.Column(db.Integer, nullable=True)

    task = db.relationship("Task", back_populates="time_entries")
    user = db.relationship("User", back_populates="time_entries")

    def close(self, end_time: datetime | None = None) -> None:
        """Stop the timer and set duration."""
        if self.ended_at:
            return
        self.ended_at = end_time or datetime.utcnow()
        duration_seconds = (self.ended_at - self.started_at).total_seconds()
        self.duration_minutes = max(1, int(duration_seconds // 60))

    def __repr__(self) -> str:  # pragma: no cover - simple repr
        return f"<TimeEntry task={self.task_id} user={self.user_id}>"

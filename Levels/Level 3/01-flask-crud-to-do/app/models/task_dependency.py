"""Task dependency mapping for critical path calculations."""

from datetime import datetime

from app import db


class TaskDependency(db.Model):  # type: ignore
    """Represents a blocking relationship between two tasks."""

    __tablename__ = "task_dependencies"

    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey("tasks.id"), nullable=False, index=True)
    depends_on_id = db.Column(db.Integer, db.ForeignKey("tasks.id"), nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    task = db.relationship("Task", foreign_keys=[task_id], back_populates="dependencies")
    depends_on = db.relationship(
        "Task", foreign_keys=[depends_on_id], back_populates="dependents"
    )

    __table_args__ = (db.UniqueConstraint("task_id", "depends_on_id", name="uq_task_dep"),)

    def __repr__(self) -> str:  # pragma: no cover - simple repr
        return f"<Dependency {self.task_id}->{self.depends_on_id}>"

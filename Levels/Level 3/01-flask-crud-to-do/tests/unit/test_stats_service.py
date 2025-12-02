"""Unit tests for stats service analytics."""

from datetime import datetime, timedelta

from app import db
from app.models.task import Task
from app.models.task_dependency import TaskDependency
from app.models.time_entry import TimeEntry
from app.services.stats_service import (
    get_burndown,
    get_dependency_overview,
    get_flow_metrics,
    get_time_insights,
)


def test_stats_overview(app, user):
    """Ensure analytics helpers return sane payloads."""
    with app.app_context():
        now = datetime.utcnow()
        task1 = Task(
            title="Complete docs",
            user_id=user.id,
            created_at=now - timedelta(days=2),
            started_at=now - timedelta(days=1, hours=2),
            completed=True,
            completed_at=now - timedelta(days=1),
            size_points=3,
        )
        task2 = Task(
            title="Blocked item",
            user_id=user.id,
            created_at=now - timedelta(days=1),
            status="blocked",
            blocked_minutes_total=30,
        )
        task3 = Task(
            title="Dependency child",
            user_id=user.id,
            created_at=now - timedelta(days=3),
            started_at=now - timedelta(days=3, hours=5),
            completed=True,
            completed_at=now - timedelta(days=2, hours=5),
        )
        db.session.add_all([task1, task2, task3])
        db.session.flush()
        db.session.add(TaskDependency(task_id=task1.id, depends_on_id=task3.id))
        db.session.add(TimeEntry(task_id=task1.id, user_id=user.id, started_at=now - timedelta(hours=1), ended_at=now, duration_minutes=60))
        db.session.commit()

        burndown = get_burndown(user.id, days=3)
        flow = get_flow_metrics(user.id)
        deps = get_dependency_overview(user.id)
        time_insights = get_time_insights(user.id)

        assert len(burndown) == 3
        assert flow["average_lead_days"] >= 0
        assert deps["longest_chain_length"] >= 1
        assert time_insights["total_minutes"] >= 60

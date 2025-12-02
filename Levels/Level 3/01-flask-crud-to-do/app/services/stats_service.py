"""Statistics service for task analytics, flow metrics, and insights."""

import logging
from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

from app import db
from app.models.task import Task
from app.models.task_dependency import TaskDependency
from app.models.time_entry import TimeEntry

logger = logging.getLogger(__name__)


def calculate_streak(user_id: int) -> int:
    """Calculate consecutive days with completed tasks.

    A streak is maintained if the user completes at least one task per day.
    The streak counts backwards from today.

    Args:
        user_id: User ID to calculate streak for

    Returns:
        Number of consecutive days with completed tasks (0 if none)
    """
    logger.info(f"Calculating streak for user {user_id}")

    completed_tasks = Task.query.filter_by(user_id=user_id, completed=True).all()

    if not completed_tasks:
        return 0

    completion_dates = set()
    for task in completed_tasks:
        completion_date_source = task.completed_at or task.updated_at
        if completion_date_source:
            completion_date = completion_date_source.date()
            completion_dates.add(completion_date)

    if not completion_dates:
        return 0

    # Sort dates in descending order
    sorted_dates = sorted(completion_dates, reverse=True)

    # Calculate streak going backwards from today
    today = date.today()
    streak = 0

    # Check if today has completed tasks
    if today in sorted_dates:
        current_date = today
    elif (today - timedelta(days=1)) in sorted_dates:
        # If no tasks today, start from yesterday
        current_date = today - timedelta(days=1)
    else:
        # No recent activity, streak is broken
        return 0

    # Count consecutive days backwards
    check_date = current_date
    while check_date in sorted_dates:
        streak += 1
        check_date -= timedelta(days=1)

    logger.info(f"User {user_id} has a streak of {streak} days")
    return streak


def get_today_stats(user_id: int) -> Dict[str, Any]:
    """Get today's task completion statistics.

    Args:
        user_id: User ID

    Returns:
        Dictionary with 'completed', 'total', and 'ratio' keys
    """
    logger.info(f"Getting today's stats for user {user_id}")

    from datetime import time

    today_start = datetime.combine(date.today(), time.min)
    today_end = datetime.combine(date.today(), time.max)

    # Get all tasks created today
    total_today = Task.query.filter(
        Task.user_id == user_id,
        Task.created_at >= today_start,
        Task.created_at <= today_end
    ).count()

    completed_today = Task.query.filter(
        Task.user_id == user_id,
        Task.completed == True,
        Task.completed_at >= today_start,
        Task.completed_at <= today_end
    ).count()

    ratio = (completed_today / total_today * 100) if total_today > 0 else 0

    return {
        'completed': completed_today,
        'total': total_today,
        'ratio': round(ratio, 1)
    }


def get_weekly_activity(user_id: int) -> List[Dict[str, Any]]:
    """Get activity data for the last 7 days.

    Args:
        user_id: User ID

    Returns:
        List of dictionaries with 'date', 'completed', 'total' keys
        Ordered from oldest to newest (7 days ago to today)
    """
    logger.info(f"Getting weekly activity for user {user_id}")

    activity = []
    today = date.today()

    from datetime import time

    for i in range(6, -1, -1):  # 6 days ago to today
        check_date = today - timedelta(days=i)
        date_start = datetime.combine(check_date, time.min)
        date_end = datetime.combine(check_date, time.max)

        # Count tasks created on this date
        total = Task.query.filter(
            Task.user_id == user_id,
            Task.created_at >= date_start,
            Task.created_at <= date_end
        ).count()

        completed = Task.query.filter(
            Task.user_id == user_id,
            Task.completed == True,
            Task.completed_at >= date_start,
            Task.completed_at <= date_end
        ).count()

        activity.append({
            'date': check_date,
            'completed': completed,
            'total': total,
            'day_name': check_date.strftime('%a')  # Mon, Tue, etc.
        })

    return activity


def get_completion_rate(user_id: int) -> float:
    """Get overall task completion rate.

    Args:
        user_id: User ID

    Returns:
        Completion rate as a percentage (0-100)
    """
    logger.info(f"Getting completion rate for user {user_id}")

    total_tasks = Task.query.filter_by(user_id=user_id).count()

    if total_tasks == 0:
        return 0.0

    completed_tasks = Task.query.filter_by(user_id=user_id, completed=True).count()

    rate = (completed_tasks / total_tasks) * 100
    return round(rate, 1)


def get_total_tasks(user_id: int) -> int:
    """Get total number of tasks for a user.

    Args:
        user_id: User ID

    Returns:
        Total task count
    """
    return Task.query.filter_by(user_id=user_id).count()


def get_recent_activity(user_id: int, limit: int = 5) -> List[Task]:
    """Get recent tasks for activity feed.

    Args:
        user_id: User ID
        limit: Maximum number of tasks to return

    Returns:
        List of recent tasks ordered by updated_at descending
    """
    return Task.query.filter_by(
        user_id=user_id
    ).order_by(
        Task.updated_at.desc()
    ).limit(limit).all()


def get_burndown(user_id: int, days: int = 7) -> List[Dict[str, Any]]:
    """Approximate burndown data using creation and completion timestamps."""
    today = date.today()
    data: List[Dict[str, Any]] = []

    for i in range(days - 1, -1, -1):
        day = today - timedelta(days=i)
        day_start = datetime.combine(day, datetime.min.time())
        day_end = datetime.combine(day, datetime.max.time())
        created_to_date = (
            Task.query.filter(
                Task.user_id == user_id,
                Task.created_at <= day_end,
            ).count()
        )
        completed_to_date = (
            Task.query.filter(
                Task.user_id == user_id,
                Task.completed == True,
                Task.completed_at <= day_end,
            ).count()
        )
        remaining = max(0, created_to_date - completed_to_date)
        data.append(
            {
                "date": day,
                "remaining": remaining,
                "completed": completed_to_date,
            }
        )
    return data


def get_flow_metrics(user_id: int) -> Dict[str, float]:
    """Compute lead time, cycle time, and blocked time averages."""
    completed_tasks = Task.query.filter_by(user_id=user_id, completed=True).all()
    lead_times: List[float] = []
    cycle_times: List[float] = []
    blocked_minutes: List[int] = []

    for task in completed_tasks:
        if task.completed_at and task.created_at:
            lead_times.append((task.completed_at - task.created_at).total_seconds() / 86400)
        if task.completed_at and task.started_at:
            cycle_times.append((task.completed_at - task.started_at).total_seconds() / 86400)
        blocked_minutes.append(task.blocked_minutes_total)

    avg_lead = round(sum(lead_times) / len(lead_times), 2) if lead_times else 0.0
    avg_cycle = round(sum(cycle_times) / len(cycle_times), 2) if cycle_times else 0.0
    avg_blocked = round(sum(blocked_minutes) / len(blocked_minutes), 1) if blocked_minutes else 0.0

    return {
        "average_lead_days": avg_lead,
        "average_cycle_days": avg_cycle,
        "average_blocked_minutes": avg_blocked,
    }


def get_dependency_overview(user_id: int) -> Dict[str, Any]:
    """Summaries for dependency graph and critical path."""
    # Build dependency map without importing task_service to avoid cycles
    tasks = Task.query.filter_by(user_id=user_id).all()
    dep_map: dict[int, list[int]] = {task.id: [] for task in tasks}
    for link in TaskDependency.query.join(Task, TaskDependency.task_id == Task.id).filter(
        Task.user_id == user_id
    ):
        dep_map.setdefault(link.task_id, []).append(link.depends_on_id)

    memo: dict[int, List[int]] = {}

    def dfs(node: int) -> List[int]:
        if node in memo:
            return memo[node]
        children = dep_map.get(node, [])
        if not children:
            memo[node] = [node]
            return memo[node]
        longest: List[int] = [node]
        for child in children:
            candidate = [node] + dfs(child)
            if len(candidate) > len(longest):
                longest = candidate
        memo[node] = longest
        return longest

    best_path: List[int] = []
    for task in tasks:
        if task.completed:
            continue
        path = dfs(task.id)
        if len(path) > len(best_path):
            best_path = path

    dependency_count = (
        TaskDependency.query.join(Task, TaskDependency.task_id == Task.id)
        .filter(Task.user_id == user_id)
        .count()
    )

    return {
        "critical_path": best_path,
        "dependency_count": dependency_count,
        "longest_chain_length": len(best_path),
    }


def get_time_insights(user_id: int) -> Dict[str, Any]:
    """Aggregate time tracking for reporting and burndown."""
    entries = (
        TimeEntry.query.join(Task, TimeEntry.task_id == Task.id)
        .filter(Task.user_id == user_id)
        .all()
    )
    total_minutes = sum(e.duration_minutes or 0 for e in entries)
    by_task: Dict[int, int] = {}
    for entry in entries:
        if entry.duration_minutes:
            by_task[entry.task_id] = by_task.get(entry.task_id, 0) + entry.duration_minutes

    # Produce a simple leaderboard of the top three focus areas
    top_tasks = sorted(by_task.items(), key=lambda x: x[1], reverse=True)[:3]
    leaderboard = []
    for task_id, minutes in top_tasks:
        task = Task.query.get(task_id)
        if task:
            leaderboard.append({"title": task.title, "minutes": minutes})

    return {
        "total_minutes": total_minutes,
        "leaderboard": leaderboard,
        "session_count": len(entries),
        "average_session": round(total_minutes / len(entries), 1) if entries else 0,
    }

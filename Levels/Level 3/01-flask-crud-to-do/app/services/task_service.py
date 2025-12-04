"""Task service for CRUD operations and advanced flows."""

import logging
from datetime import date, datetime, timedelta
from typing import Dict, List, Optional, Sequence, Tuple

from sqlalchemy import or_
from sqlalchemy.orm import Query

from app import db
from app.models import (
    AuditLog,
    Task,
    TaskAttachment,
    TaskDependency,
    TaskNote,
    TaskTemplate,
    TimeEntry,
    User,
)
from app.utils.exceptions import TaskAccessDeniedError, TaskNotFoundError

logger = logging.getLogger(__name__)

KANBAN_STATUSES = ["backlog", "in_progress", "blocked", "review", "done"]
PRIORITIES = ["low", "medium", "high", "urgent"]


def _record_audit(user_id: int | None, task_id: int | None, action: str, details: str | None) -> None:
    """Persist an audit event scoped to a task."""
    audit = AuditLog(user_id=user_id, task_id=task_id, action=action, details=details)
    db.session.add(audit)


def _detect_cycle(task_id: int, depends_on_id: int) -> bool:
    """Detect if adding a dependency would create a cycle."""
    to_visit = [depends_on_id]
    seen: set[int] = set()
    while to_visit:
        current = to_visit.pop()
        if current == task_id:
            return True
        if current in seen:
            continue
        seen.add(current)
        child_links = TaskDependency.query.filter_by(task_id=current).all()
        to_visit.extend(dep.depends_on_id for dep in child_links)
    return False


def _smart_due_date(user_id: int, priority: str, size_points: int) -> datetime:
    """Guess a due date based on workload, priority, and size."""
    open_tasks = Task.query.filter_by(user_id=user_id, completed=False).count()
    urgency_bias = {"urgent": 1, "high": 2, "medium": 4, "low": 6}.get(priority, 4)
    load_penalty = max(0, open_tasks // 4)
    days = max(1, urgency_bias + size_points + load_penalty)
    return datetime.utcnow() + timedelta(days=days)


def _ai_triage(user_id: int, title: str, description: Optional[str]) -> Dict[str, object]:
    """Lightweight heuristic triage for priority, size, and acceptance criteria."""
    text = f"{title} {description or ''}".lower()
    priority = "medium"
    size_points = 2
    tags: list[str] = []

    if any(keyword in text for keyword in ["urgent", "blocker", "outage", "p0"]):
        priority = "urgent"
        size_points = 3
        tags.append("hotfix")
    elif any(keyword in text for keyword in ["bug", "issue", "defect", "fix"]):
        priority = "high"
        tags.append("bug")
    elif any(keyword in text for keyword in ["research", "spike", "investigate"]):
        priority = "medium"
        size_points = 1
        tags.append("research")
    elif any(keyword in text for keyword in ["refactor", "cleanup", "debt"]):
        priority = "medium"
        size_points = 2
        tags.append("quality")

    if len(title) < 25:
        size_points = max(1, size_points - 1)

    due_date = _smart_due_date(user_id=user_id, priority=priority, size_points=size_points)

    acceptance_criteria = [
        f"Outcome is clearly verifiable for '{title}'.",
        "Edge cases are covered and linked evidence is attached.",
        "Task owner added a short retro note after completion.",
    ]

    if "api" in text:
        acceptance_criteria.append("API contract is documented and tested.")
        tags.append("api")
    if "ui" in text or "frontend" in text:
        acceptance_criteria.append("UI states (empty/loading/error) are covered.")
        tags.append("ui")

    return {
        "priority": priority,
        "size_points": size_points,
        "due_date": due_date,
        "acceptance_criteria": acceptance_criteria,
        "tags": tags,
    }


def create_task(
    user_id: int,
    title: str,
    description: Optional[str] = None,
    **options: object,
) -> Task:
    """Create a new task for a user with smart defaults and triage."""
    logger.info(f"Creating task '{title}' for user {user_id}")
    status = str(options.get("status", "backlog"))
    if status not in KANBAN_STATUSES:
        status = "backlog"

    priority = options.get("priority")
    priority = str(priority) if priority else None
    category = options.get("category")
    category = str(category) if category else "General"
    due_date = options.get("due_date")
    size_points = int(options.get("size_points", 1) or 1)
    recurrence_interval_days = options.get("recurrence_interval_days")
    recurrence_end_date = options.get("recurrence_end_date")
    requires_approval = bool(options.get("requires_approval", False))
    template_id = options.get("template_id")
    blocked_reason = options.get("blocked_reason")
    auto_schedule = bool(options.get("auto_schedule", True))
    auto_triage = bool(options.get("auto_triage", True))

    template: TaskTemplate | None = None
    if template_id:
        template = TaskTemplate.query.get(template_id)
        if template:
            priority = priority or template.default_priority
            status = options.get("status", template.default_status)  # type: ignore
            size_points = int(options.get("size_points", template.default_size_points) or 1)
            recurrence_interval_days = options.get(
                "recurrence_interval_days", template.default_recurrence_interval_days
            )
            requires_approval = bool(
                options.get("requires_approval", template.default_requires_approval)
            )
            if description is None and template.description:
                description = template.description

    triage_data = _ai_triage(user_id, title, description) if auto_triage else {}
    triaged_priority = triage_data.get("priority")
    triaged_due = triage_data.get("due_date")
    triaged_size = triage_data.get("size_points")

    if priority is None:
        priority = str(triaged_priority or "medium")
    if size_points <= 0:
        size_points = int(triaged_size or 1)
    if not due_date:
        # recompute due date with real user id if triage supplied placeholder
        if triaged_due and isinstance(triaged_due, datetime):
            due_date = triaged_due
        elif auto_schedule:
            due_date = _smart_due_date(user_id, priority, size_points)

    task = Task(
        title=title,
        description=description,
        user_id=user_id,
        status=status,
        priority=priority,
        category=category,
        due_date=due_date,
        size_points=size_points,
        recurrence_interval_days=recurrence_interval_days,
        recurrence_end_date=recurrence_end_date,
        requires_approval=requires_approval,
        template_id=template.id if template else None,
        blocked_reason=blocked_reason,
    )

    db.session.add(task)
    db.session.flush()

    # Seed acceptance criteria and checklist as notes
    acceptance_criteria = triage_data.get("acceptance_criteria") or []
    for criterion in acceptance_criteria:
        db.session.add(
            TaskNote(task_id=task.id, content=str(criterion), kind="acceptance", created_by=user_id)
        )

    if template and template.default_checklist:
        for line in template.default_checklist.splitlines():
            trimmed = line.strip()
            if trimmed:
                db.session.add(
                    TaskNote(task_id=task.id, content=trimmed, kind="checklist", created_by=user_id)
                )

    _record_audit(user_id, task.id, "create_task", f"Status {status}, priority {priority}")
    db.session.commit()

    logger.info(f"Task {task.id} created successfully")
    return task


def get_task(task_id: int, user_id: int) -> Task:
    """Get a task by ID, ensuring user ownership."""
    task = Task.query.get(task_id)

    if not task:
        logger.warning(f"Task {task_id} not found")
        raise TaskNotFoundError(f"Task {task_id} not found")

    if task.user_id != user_id:
        logger.warning(f"User {user_id} attempted to access task {task_id} owned by {task.user_id}")
        raise TaskAccessDeniedError("You don't have permission to access this task")

    return task


def get_tasks(
    user_id: int,
    completed: Optional[bool] = None,
    search: Optional[str] = None,
    sort_by: str = "created_at",
    order: str = "desc",
    page: int = 1,
    per_page: int = 10,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    category: Optional[str] = None,
    due_before: Optional[datetime] = None,
    due_after: Optional[datetime] = None,
) -> tuple[List[Task], int]:
    """Get tasks for a user with filtering, sorting, and pagination."""
    logger.info(f"Fetching tasks for user {user_id}")

    query: Query = Task.query.filter_by(user_id=user_id)

    if completed is not None:
        query = query.filter_by(completed=completed)

    if status:
        query = query.filter_by(status=status)

    if priority:
        query = query.filter_by(priority=priority)

    if category:
        query = query.filter_by(category=category)

    if due_before:
        query = query.filter(Task.due_date <= due_before)
    if due_after:
        query = query.filter(Task.due_date >= due_after)

    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            or_(Task.title.ilike(search_pattern), Task.description.ilike(search_pattern))
        )

    sort_column = getattr(Task, sort_by, Task.created_at)
    if order.lower() == "asc":
        query = query.order_by(sort_column.asc())
    else:
        query = query.order_by(sort_column.desc())

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    return pagination.items, pagination.total


def update_task(
    task_id: int,
    user_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    category: Optional[str] = None,
    due_date: Optional[datetime] = None,
    size_points: Optional[int] = None,
    recurrence_interval_days: Optional[int] = None,
    recurrence_end_date: Optional[date] = None,
    requires_approval: Optional[bool] = None,
    blocked_reason: Optional[str] = None,
) -> Task:
    """Update a task and audit changes."""
    task = get_task(task_id, user_id)

    if title is not None:
        task.title = title
    if description is not None:
        task.description = description
    if status is not None:
        normalized_status = status if status in KANBAN_STATUSES else "backlog"
        previous_status = task.status
        task.enter_status(normalized_status)
        _record_audit(
            user_id,
            task.id,
            "change_status",
            f"{previous_status} -> {normalized_status}",
        )
    if priority is not None:
        task.priority = priority
    if category is not None:
        task.category = category
    if due_date is not None:
        task.due_date = due_date
    if size_points is not None:
        task.size_points = size_points
    if recurrence_interval_days is not None:
        task.recurrence_interval_days = recurrence_interval_days
    if recurrence_end_date is not None:
        task.recurrence_end_date = recurrence_end_date
    if requires_approval is not None:
        task.requires_approval = requires_approval
    if blocked_reason is not None:
        task.blocked_reason = blocked_reason

    task.updated_at = datetime.utcnow()
    _record_audit(user_id, task.id, "update_task", "Fields updated")

    db.session.commit()
    logger.info(f"Task {task_id} updated successfully")
    return task


def change_status(
    task_id: int,
    user_id: int,
    status: str,
    blocked_reason: Optional[str] = None,
) -> Task:
    """Move a task to a new kanban status."""
    if status not in KANBAN_STATUSES:
        status = "backlog"

    task = get_task(task_id, user_id)
    if status == "done" and task.requires_approval and not task.approved_at:
        raise TaskAccessDeniedError("Task requires approval before moving to Done.")
    previous_status = task.status
    task.enter_status(status)
    if blocked_reason:
        task.blocked_reason = blocked_reason

    _record_audit(
        user_id,
        task.id,
        "change_status",
        f"{previous_status} -> {status}",
    )
    db.session.commit()
    return task


def delete_task(task_id: int, user_id: int) -> None:
    """Delete a task and its dependencies."""
    task = get_task(task_id, user_id)
    db.session.delete(task)
    _record_audit(user_id, task_id, "delete_task", "Task removed")
    db.session.commit()
    logger.info(f"Task {task_id} deleted successfully")


def toggle_task_completion(task_id: int, user_id: int) -> Task:
    """Toggle the completion status of a task."""
    task = get_task(task_id, user_id)
    was_completed = task.completed
    if not task.completed and task.requires_approval and not task.approved_at:
        raise TaskAccessDeniedError("Task requires approval before completion.")
    task.toggle_completed()
    if task.completed and task.recurrence_interval_days:
        apply_recurrence(task)

    _record_audit(
        user_id,
        task.id,
        "toggle_completion",
        f"Completed={task.completed}",
    )
    db.session.commit()
    logger.info(f"Task {task_id} completion toggled from {was_completed} to {task.completed}")
    return task


def apply_recurrence(task: Task) -> Optional[Task]:
    """Create the next occurrence of a recurring task."""
    if not task.recurrence_interval_days:
        return None
    if task.recurrence_end_date and date.today() > task.recurrence_end_date:
        return None

    base_date = task.due_date or datetime.utcnow()
    next_due = base_date + timedelta(days=int(task.recurrence_interval_days))
    new_task = Task(
        title=task.title,
        description=task.description,
        user_id=task.user_id,
        status="backlog",
        priority=task.priority,
        category=task.category,
        due_date=next_due,
        size_points=task.size_points,
        recurrence_interval_days=task.recurrence_interval_days,
        recurrence_end_date=task.recurrence_end_date,
        requires_approval=task.requires_approval,
        template_id=task.template_id,
    )
    db.session.add(new_task)
    db.session.flush()
    _record_audit(task.user_id, new_task.id, "spawn_recurrence", f"From task {task.id}")
    return new_task


def add_dependency(task_id: int, dependency_id: int, user_id: int) -> TaskDependency:
    """Link a dependency between two tasks with cycle protection."""
    if task_id == dependency_id:
        raise ValueError("A task cannot depend on itself.")

    task = get_task(task_id, user_id)
    dependency = get_task(dependency_id, user_id)

    if _detect_cycle(task_id, dependency_id):
        raise ValueError("Adding this dependency would create a cycle.")

    existing = TaskDependency.query.filter_by(
        task_id=task.id, depends_on_id=dependency.id
    ).first()
    if existing:
        return existing

    link = TaskDependency(task_id=task.id, depends_on_id=dependency.id)
    db.session.add(link)
    _record_audit(user_id, task.id, "add_dependency", f"Depends on {dependency.id}")
    db.session.commit()
    return link


def remove_dependency(task_id: int, dependency_id: int, user_id: int) -> None:
    """Remove a dependency edge."""
    get_task(task_id, user_id)
    get_task(dependency_id, user_id)
    link = TaskDependency.query.filter_by(task_id=task_id, depends_on_id=dependency_id).first()
    if link:
        db.session.delete(link)
        _record_audit(user_id, task_id, "remove_dependency", f"Removed {dependency_id}")
        db.session.commit()


def calculate_critical_path(user_id: int) -> Tuple[List[int], int]:
    """Calculate a simple critical path based on dependency length."""
    tasks = Task.query.filter_by(user_id=user_id).all()
    dep_map: dict[int, list[int]] = {task.id: [] for task in tasks}
    for task in tasks:
        dep_map[task.id] = [d.depends_on_id for d in task.dependencies]

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

    return best_path, len(best_path)


def start_timer(task_id: int, user_id: int) -> TimeEntry:
    """Start a time tracking entry for a task."""
    task = get_task(task_id, user_id)
    existing = TimeEntry.query.filter_by(task_id=task.id, user_id=user_id, ended_at=None).first()
    if existing:
        return existing

    entry = TimeEntry(task_id=task.id, user_id=user_id, started_at=datetime.utcnow())
    db.session.add(entry)
    _record_audit(user_id, task.id, "start_timer", "Timer started")
    db.session.commit()
    return entry


def stop_timer(task_id: int, user_id: int) -> Optional[TimeEntry]:
    """Stop the active timer for a task."""
    entry = TimeEntry.query.filter_by(task_id=task_id, user_id=user_id, ended_at=None).first()
    if not entry:
        return None
    entry.close()
    _record_audit(user_id, task_id, "stop_timer", "Timer stopped")
    db.session.commit()
    return entry


def get_time_summary(user_id: int) -> Dict[str, float]:
    """Get total time and average session for a user."""
    entries: Sequence[TimeEntry] = TimeEntry.query.filter_by(user_id=user_id).all()
    total_minutes = sum(e.duration_minutes or 0 for e in entries)
    avg = total_minutes / len(entries) if entries else 0
    return {"total_minutes": total_minutes, "average_session_minutes": round(avg, 1)}


def add_note(task_id: int, user_id: int, content: str, kind: str = "note") -> TaskNote:
    """Attach a note or acceptance criteria to a task."""
    get_task(task_id, user_id)
    note = TaskNote(task_id=task_id, content=content, kind=kind, created_by=user_id)
    db.session.add(note)
    _record_audit(user_id, task_id, "add_note", f"Kind {kind}")
    db.session.commit()
    return note


def add_attachment(task_id: int, user_id: int, title: str, url: str) -> TaskAttachment:
    """Attach a link-style attachment to a task."""
    get_task(task_id, user_id)
    attachment = TaskAttachment(task_id=task_id, title=title, url=url, created_by=user_id)
    db.session.add(attachment)
    _record_audit(user_id, task_id, "add_attachment", title)
    db.session.commit()
    return attachment

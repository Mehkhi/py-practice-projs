"""Task CRUD, kanban, scheduling, and collaboration routes."""

import logging
from datetime import date, datetime
from typing import Tuple

from flask import Blueprint, flash, jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app import db
from app.models import AuditLog, Task
from app.models.task_template import TaskTemplate
from app.services.task_service import (
    KANBAN_STATUSES,
    add_attachment,
    add_dependency,
    add_note,
    calculate_critical_path,
    change_status,
    create_task,
    delete_task,
    get_task,
    get_tasks,
    get_time_summary,
    start_timer,
    stop_timer,
    toggle_task_completion,
    update_task,
)
from app.utils.exceptions import TaskAccessDeniedError, TaskNotFoundError

logger = logging.getLogger(__name__)

tasks_bp = Blueprint("tasks", __name__)


def _parse_datetime(date_str: str | None) -> datetime | None:
    """Parse ISO date or datetime string to datetime."""
    if not date_str:
        return None
    try:
        return datetime.fromisoformat(date_str)
    except ValueError:
        try:
            date_val = date.fromisoformat(date_str)
            return datetime.combine(date_val, datetime.min.time())
        except ValueError:
            return None


def _parse_date(date_str: str | None) -> date | None:
    """Parse ISO date string to date."""
    if not date_str:
        return None
    try:
        return date.fromisoformat(date_str)
    except ValueError:
        return None


@tasks_bp.route("/")
@login_required
def list_tasks() -> str:
    """List all tasks with filtering, sorting, and pagination."""
    completed_filter = request.args.get("completed")
    search = request.args.get("search", "").strip()
    sort_by = request.args.get("sort_by", "created_at")
    order = request.args.get("order", "desc")
    page = request.args.get("page", 1, type=int)
    status_filter = request.args.get("status") or None
    priority_filter = request.args.get("priority") or None

    completed: bool | None = None
    if completed_filter == "true":
        completed = True
    elif completed_filter == "false":
        completed = False

    valid_sort_fields = ["created_at", "title", "completed", "due_date", "priority"]
    if sort_by not in valid_sort_fields:
        sort_by = "created_at"

    if order not in ["asc", "desc"]:
        order = "desc"

    tasks, total = get_tasks(
        user_id=current_user.id,
        completed=completed,
        status=status_filter,
        priority=priority_filter,
        search=search if search else None,
        sort_by=sort_by,
        order=order,
        page=page,
        per_page=10,
    )

    total_pages = (total + 9) // 10
    has_prev = page > 1
    has_next = page < total_pages
    critical_path_ids, critical_length = calculate_critical_path(current_user.id)
    time_summary = get_time_summary(current_user.id)

    return render_template(
        "tasks/list.html",
        tasks=tasks,
        total=total,
        page=page,
        total_pages=total_pages,
        has_prev=has_prev,
        has_next=has_next,
        completed_filter=completed_filter,
        search=search,
        sort_by=sort_by,
        order=order,
        status_filter=status_filter,
        priority_filter=priority_filter,
        statuses=KANBAN_STATUSES,
        critical_path_ids=critical_path_ids,
        critical_length=critical_length,
        time_summary=time_summary,
        current_time=datetime.utcnow(),
    )


@tasks_bp.route("/new", methods=["GET"])
@login_required
def new_task() -> str:
    """Show form to create a new task."""
    templates = TaskTemplate.query.order_by(TaskTemplate.created_at.desc()).all()
    return render_template("tasks/create.html", templates=templates, statuses=KANBAN_STATUSES)


@tasks_bp.route("/create", methods=["POST"])
@login_required
def create_task_route() -> redirect:
    """Create a new task."""
    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip() or None
    status = request.form.get("status", "backlog")
    priority = request.form.get("priority") or None
    due_date = _parse_datetime(request.form.get("due_date"))
    size_points = int(request.form.get("size_points", 1) or 1)
    recurrence_days = request.form.get("recurrence_interval_days")
    recurrence_interval_days = int(recurrence_days) if recurrence_days else None
    recurrence_end_date = _parse_date(request.form.get("recurrence_end_date"))
    requires_approval = request.form.get("requires_approval") == "on"
    blocked_reason = request.form.get("blocked_reason") or None
    template_id = request.form.get("template_id")
    auto_schedule = request.form.get("auto_schedule", "on") != "off"
    auto_triage = request.form.get("auto_triage", "on") != "off"

    template_id_int = int(template_id) if template_id else None

    if not title:
        flash("Title is required.", "error")
        return redirect(url_for("tasks.new_task"))

    try:
        task = create_task(
            current_user.id,
            title,
            description,
            status=status,
            priority=priority,
            due_date=due_date,
            size_points=size_points,
            recurrence_interval_days=recurrence_interval_days,
            recurrence_end_date=recurrence_end_date,
            requires_approval=requires_approval,
            blocked_reason=blocked_reason,
            template_id=template_id_int,
            auto_schedule=auto_schedule,
            auto_triage=auto_triage,
        )
        flash(
            f"Task '{task.title}' created with {task.priority} priority, due "
            f"{task.due_date.strftime('%b %d') if task.due_date else 'TBD'}.",
            "success",
        )
        logger.info(f"Task {task.id} created by user {current_user.id}")
        return redirect(url_for("tasks.list_tasks"))
    except Exception as e:
        flash("An error occurred while creating the task.", "error")
        logger.error(f"Error creating task: {e}")
        return redirect(url_for("tasks.new_task"))


@tasks_bp.route("/<int:task_id>/edit", methods=["GET"])
@login_required
def edit_task(task_id: int) -> str | redirect:
    """Show form to edit a task and manage advanced fields."""
    try:
        task = get_task(task_id, current_user.id)
        templates = TaskTemplate.query.order_by(TaskTemplate.created_at.desc()).all()
        other_tasks = (
            Task.query.filter(Task.user_id == current_user.id, Task.id != task_id)
            .order_by(Task.title.asc())
            .all()
        )
        return render_template(
            "tasks/edit.html",
            task=task,
            templates=templates,
            statuses=KANBAN_STATUSES,
            other_tasks=other_tasks,
        )
    except TaskNotFoundError:
        flash("Task not found.", "error")
        return redirect(url_for("tasks.list_tasks"))
    except TaskAccessDeniedError:
        flash("You don't have permission to edit this task.", "error")
        return redirect(url_for("tasks.list_tasks"))


@tasks_bp.route("/<int:task_id>/update", methods=["POST"])
@login_required
def update_task_route(task_id: int) -> redirect:
    """Update a task."""
    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip() or None
    status = request.form.get("status")
    priority = request.form.get("priority")
    due_date = _parse_datetime(request.form.get("due_date"))
    size_points = int(request.form.get("size_points", 1) or 1)
    recurrence_days = request.form.get("recurrence_interval_days")
    recurrence_interval_days = int(recurrence_days) if recurrence_days else None
    recurrence_end_date = _parse_date(request.form.get("recurrence_end_date"))
    requires_approval = request.form.get("requires_approval") == "on"
    blocked_reason = request.form.get("blocked_reason") or None

    if not title:
        flash("Title is required.", "error")
        return redirect(url_for("tasks.edit_task", task_id=task_id))

    try:
        update_task(
            task_id,
            current_user.id,
            title=title,
            description=description,
            status=status,
            priority=priority,
            due_date=due_date,
            size_points=size_points,
            recurrence_interval_days=recurrence_interval_days,
            recurrence_end_date=recurrence_end_date,
            requires_approval=requires_approval,
            blocked_reason=blocked_reason,
        )
        flash("Task updated successfully!", "success")
        logger.info(f"Task {task_id} updated by user {current_user.id}")
        return redirect(url_for("tasks.view_task", task_id=task_id))
    except TaskNotFoundError:
        flash("Task not found.", "error")
        return redirect(url_for("tasks.list_tasks"))
    except TaskAccessDeniedError:
        flash("You don't have permission to update this task.", "error")
        return redirect(url_for("tasks.list_tasks"))


@tasks_bp.route("/<int:task_id>/delete", methods=["POST"])
@login_required
def delete_task_route(task_id: int) -> redirect:
    """Delete a task."""
    try:
        delete_task(task_id, current_user.id)
        flash("Task deleted successfully!", "success")
        logger.info(f"Task {task_id} deleted by user {current_user.id}")
    except TaskNotFoundError:
        flash("Task not found.", "error")
    except TaskAccessDeniedError:
        flash("You don't have permission to delete this task.", "error")

    return redirect(url_for("tasks.list_tasks"))


@tasks_bp.route("/<int:task_id>/toggle", methods=["POST"])
@login_required
def toggle_task_route(task_id: int) -> redirect:
    """Toggle task completion status."""
    try:
        task = toggle_task_completion(task_id, current_user.id)
        status = "completed" if task.completed else "incomplete"
        flash(f"Task marked as {status}!", "success")
        logger.info(f"Task {task_id} toggled by user {current_user.id}")
    except TaskNotFoundError:
        flash("Task not found.", "error")
    except TaskAccessDeniedError:
        flash("You don't have permission to modify this task.", "error")

    return redirect(url_for("tasks.list_tasks"))


@tasks_bp.route("/board")
@login_required
def board_view() -> str:
    """Kanban view with swimlanes and WIP limits."""
    tasks_by_status = {}
    for status in KANBAN_STATUSES:
        tasks, _ = get_tasks(
            user_id=current_user.id, status=status, sort_by="kanban_order", order="asc", per_page=200
        )
        tasks_by_status[status] = tasks

    critical_path_ids, critical_length = calculate_critical_path(current_user.id)

    return render_template(
        "tasks/board.html",
        statuses=KANBAN_STATUSES,
        tasks_by_status=tasks_by_status,
        critical_path_ids=critical_path_ids,
        critical_length=critical_length,
    )


@tasks_bp.route("/<int:task_id>/status", methods=["POST"])
@login_required
def change_status_route(task_id: int) -> redirect:
    """Update task status from kanban or list actions."""
    new_status = request.form.get("status", "backlog")
    blocked_reason = request.form.get("blocked_reason") or None
    try:
        task = change_status(task_id, current_user.id, new_status, blocked_reason)
        flash(f"Task moved to {task.status}", "success")
    except TaskNotFoundError:
        flash("Task not found.", "error")
    except TaskAccessDeniedError:
        flash("You don't have permission to move this task.", "error")

    referrer = request.referrer or url_for("tasks.board_view")
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify({"status": "ok"})
    return redirect(referrer)


@tasks_bp.route("/<int:task_id>/dependencies", methods=["POST"])
@login_required
def add_dependency_route(task_id: int) -> redirect:
    """Add a dependency to a task."""
    dependency_id = request.form.get("dependency_id")
    if not dependency_id:
        flash("Select a dependency first.", "error")
        return redirect(url_for("tasks.edit_task", task_id=task_id))

    try:
        add_dependency(task_id, int(dependency_id), current_user.id)
        flash("Dependency added.", "success")
    except ValueError as ve:
        flash(str(ve), "error")
    except (TaskAccessDeniedError, TaskNotFoundError):
        flash("You don't have access to that task.", "error")

    return redirect(url_for("tasks.edit_task", task_id=task_id))


@tasks_bp.route("/<int:task_id>/timer/start", methods=["POST"])
@login_required
def start_timer_route(task_id: int) -> redirect:
    """Start tracking time on a task."""
    try:
        start_timer(task_id, current_user.id)
        flash("Timer started.", "success")
    except (TaskAccessDeniedError, TaskNotFoundError):
        flash("Unable to start timer for this task.", "error")
    return redirect(request.referrer or url_for("tasks.list_tasks"))


@tasks_bp.route("/<int:task_id>/timer/stop", methods=["POST"])
@login_required
def stop_timer_route(task_id: int) -> redirect:
    """Stop active timer on a task."""
    try:
        entry = stop_timer(task_id, current_user.id)
        if entry:
            flash(f"Logged {entry.duration_minutes} minutes.", "success")
        else:
            flash("No active timer found.", "error")
    except (TaskAccessDeniedError, TaskNotFoundError):
        flash("Unable to stop timer for this task.", "error")
    return redirect(request.referrer or url_for("tasks.list_tasks"))


@tasks_bp.route("/<int:task_id>/notes", methods=["POST"])
@login_required
def add_note_route(task_id: int) -> redirect:
    """Add a knowledge note to the task."""
    content = request.form.get("content", "").strip()
    kind = request.form.get("kind", "note")
    if not content:
        flash("Note cannot be empty.", "error")
        return redirect(url_for("tasks.edit_task", task_id=task_id))

    try:
        add_note(task_id, current_user.id, content, kind=kind)
        flash("Note added.", "success")
    except (TaskAccessDeniedError, TaskNotFoundError):
        flash("Unable to add note.", "error")
    return redirect(url_for("tasks.edit_task", task_id=task_id))


@tasks_bp.route("/<int:task_id>/attachments", methods=["POST"])
@login_required
def add_attachment_route(task_id: int) -> redirect:
    """Attach a link to the task knowledge hub."""
    title = request.form.get("title", "").strip()
    url = request.form.get("url", "").strip()
    if not title or not url:
        flash("Attachment title and URL are required.", "error")
        return redirect(url_for("tasks.edit_task", task_id=task_id))

    try:
        add_attachment(task_id, current_user.id, title, url)
        flash("Attachment added.", "success")
    except (TaskAccessDeniedError, TaskNotFoundError):
        flash("Unable to add attachment.", "error")
    return redirect(url_for("tasks.edit_task", task_id=task_id))


@tasks_bp.route("/<int:task_id>/approve", methods=["POST"])
@login_required
def approve_task(task_id: int) -> redirect:
    """Approve a task that requires signoff."""
    try:
        task = get_task(task_id, current_user.id)
        task.approved_at = datetime.utcnow()
        task.approved_by = current_user.id
        db.session.add(
            AuditLog(
                user_id=current_user.id,
                task_id=task.id,
                action="approve_task",
                details="Workflow approval",
            )
        )
        db.session.commit()
        flash("Task approved.", "success")
    except (TaskAccessDeniedError, TaskNotFoundError):
        flash("Unable to approve this task.", "error")
    return redirect(url_for("tasks.edit_task", task_id=task_id))


@tasks_bp.route("/templates", methods=["GET", "POST"])
@login_required
def templates() -> str:
    """Manage task templates and create new ones."""
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        description = request.form.get("description", "").strip() or None
        default_priority = request.form.get("default_priority", "medium")
        default_status = request.form.get("default_status", "backlog")
        recurrence_days = request.form.get("default_recurrence_interval_days")
        default_recurrence_interval_days = int(recurrence_days) if recurrence_days else None
        default_requires_approval = request.form.get("default_requires_approval") == "on"
        default_checklist = request.form.get("default_checklist", "").strip() or None

        if not name:
            flash("Template name is required.", "error")
            return redirect(url_for("tasks.templates"))

        template = TaskTemplate(
            name=name,
            description=description,
            default_priority=default_priority,
            default_status=default_status,
            default_size_points=int(request.form.get("default_size_points", 1) or 1),
            default_recurrence_interval_days=default_recurrence_interval_days,
            default_requires_approval=default_requires_approval,
            default_checklist=default_checklist,
            created_by=current_user.id,
        )
        db.session.add(template)
        db.session.commit()
        flash("Template created.", "success")
        return redirect(url_for("tasks.templates"))

    templates = TaskTemplate.query.order_by(TaskTemplate.created_at.desc()).all()
    return render_template("tasks/templates.html", templates=templates, statuses=KANBAN_STATUSES)


@tasks_bp.route("/<int:task_id>")
@login_required
def view_task(task_id: int) -> str | redirect:
    """Detailed view for collaboration, notes, and dependencies."""
    try:
        task = get_task(task_id, current_user.id)
        dependencies = [link.depends_on for link in task.dependencies]
        dependents = [link.task for link in task.dependents]
        time_entries = task.time_entries
        return render_template(
            "tasks/detail.html",
            task=task,
            dependencies=dependencies,
            dependents=dependents,
            time_entries=time_entries,
            critical_path_ids=calculate_critical_path(current_user.id)[0],
        )
    except (TaskAccessDeniedError, TaskNotFoundError):
        flash("Task not available.", "error")
        return redirect(url_for("tasks.list_tasks"))

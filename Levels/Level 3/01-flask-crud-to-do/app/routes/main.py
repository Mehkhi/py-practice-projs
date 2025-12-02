"""Main routes and error handlers."""

import logging
from typing import Tuple

from flask import Blueprint, Response, redirect, render_template, url_for
from flask_login import current_user

from app.services.stats_service import (
    calculate_streak,
    get_completion_rate,
    get_dependency_overview,
    get_flow_metrics,
    get_burndown,
    get_recent_activity,
    get_today_stats,
    get_time_insights,
    get_total_tasks,
    get_weekly_activity,
)

logger = logging.getLogger(__name__)

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index() -> str | Response:
    """Home page dashboard.

    Returns:
        Dashboard template for authenticated users, or redirect to login
    """
    if not current_user.is_authenticated:
        return redirect(url_for("auth.login"))

    # Calculate all stats
    streak = calculate_streak(current_user.id)
    today_stats = get_today_stats(current_user.id)
    weekly_activity = get_weekly_activity(current_user.id)
    completion_rate = get_completion_rate(current_user.id)
    total_tasks = get_total_tasks(current_user.id)
    recent_tasks = get_recent_activity(current_user.id, limit=5)
    burndown = get_burndown(current_user.id, days=7)
    flow_metrics = get_flow_metrics(current_user.id)
    dependency_overview = get_dependency_overview(current_user.id)
    time_insights = get_time_insights(current_user.id)

    return render_template(
        "index.html",
        streak=streak,
        today_stats=today_stats,
        weekly_activity=weekly_activity,
        completion_rate=completion_rate,
        total_tasks=total_tasks,
        recent_tasks=recent_tasks,
        burndown=burndown,
        flow_metrics=flow_metrics,
        dependency_overview=dependency_overview,
        time_insights=time_insights,
    )


@main_bp.errorhandler(404)
def not_found_error(error: Exception) -> Tuple[str, int]:
    """Handle 404 errors.

    Args:
        error: Error object

    Returns:
        404 error page template
    """
    logger.warning(f"404 error: {error}")
    return render_template("errors/404.html"), 404


@main_bp.errorhandler(500)
def internal_error(error: Exception) -> Tuple[str, int]:
    """Handle 500 errors.

    Args:
        error: Error object

    Returns:
        500 error page template
    """
    logger.error(f"500 error: {error}")
    return render_template("errors/500.html"), 500

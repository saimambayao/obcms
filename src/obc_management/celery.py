"""
Celery configuration for OBCMS.

This module configures Celery for background task processing and scheduled jobs.
It automatically discovers tasks from all installed Django apps.

For more information on using Celery with Django:
https://docs.celeryq.dev/en/stable/django/first-steps-with-django.html
"""

import os
from celery import Celery
from celery.schedules import crontab

# Set default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "obc_management.settings")

# Create Celery app instance
app = Celery("obc_management")

# Load configuration from Django settings with 'CELERY_' prefix
# Example: CELERY_BROKER_URL in settings.py
app.config_from_object("django.conf:settings", namespace="CELERY")

# Auto-discover tasks from all installed apps
# This will look for tasks.py in each app directory
app.autodiscover_tasks()


# Celery Beat Schedule (Periodic Tasks)
# Add scheduled tasks here
app.conf.beat_schedule = {
    # Example: Cleanup expired sessions daily at 3 AM
    "cleanup-expired-sessions": {
        "task": "common.tasks.cleanup_expired_sessions",
        "schedule": crontab(hour=3, minute=0),  # 3:00 AM daily
        "options": {"expires": 3600},  # Task expires after 1 hour
    },
    # Workflow deadline reminders daily at 7 AM
    "workflow-deadline-reminders": {
        "task": "monitoring.send_workflow_deadline_reminders",
        "schedule": crontab(hour=7, minute=0),  # 7:00 AM daily
        "options": {"expires": 3600},
    },
    # Task assignment reminders daily at 7:30 AM
    "task-assignment-reminders": {
        "task": "monitoring.send_task_assignment_reminders",
        "schedule": crontab(hour=7, minute=30),  # 7:30 AM daily
        "options": {"expires": 3600},
    },
    # Calendar: Process event reminders every 15 minutes
    "process-event-reminders": {
        "task": "common.tasks.process_scheduled_reminders",
        "schedule": crontab(minute="*/15"),  # Every 15 minutes
        "options": {"expires": 900},  # 15 minutes
    },
    # Calendar: Send daily digest at 7:00 AM
    "send-daily-calendar-digest": {
        "task": "common.tasks.send_daily_digest",
        "schedule": crontab(hour=7, minute=0),  # 7:00 AM daily
        "options": {"expires": 3600},
    },
    # Calendar: Clean expired share links daily at 2:00 AM
    "clean-expired-calendar-shares": {
        "task": "common.tasks.clean_expired_calendar_shares",
        "schedule": crontab(hour=2, minute=0),  # 2:00 AM daily
        "options": {"expires": 3600},
    },
    # Project Management Portal: Generate daily alerts at 6:00 AM
    "generate-daily-alerts": {
        "task": "project_central.generate_daily_alerts",
        "schedule": crontab(hour=6, minute=0),  # 6:00 AM daily
        "options": {"expires": 3600},
    },
    # Project Management Portal: Deactivate resolved alerts at 6:30 AM
    "deactivate-resolved-alerts": {
        "task": "project_central.deactivate_resolved_alerts",
        "schedule": crontab(hour=6, minute=30),  # 6:30 AM daily
        "options": {"expires": 3600},
    },
    # Project Management Portal: Update budget ceiling allocations at 5:00 AM
    "update-budget-ceilings": {
        "task": "project_central.update_budget_ceiling_allocations",
        "schedule": crontab(hour=5, minute=0),  # 5:00 AM daily
        "options": {"expires": 3600},
    },
    # Project Management Portal: Check workflow deadlines at 7:00 AM
    "check-workflow-deadlines": {
        "task": "project_central.check_workflow_deadlines",
        "schedule": crontab(hour=7, minute=0),  # 7:00 AM daily
        "options": {"expires": 3600},
    },
    # Example: Send daily summary reports at 8 AM
    # 'send-daily-reports': {
    #     'task': 'monitoring.tasks.send_daily_reports',
    #     'schedule': crontab(hour=8, minute=0),  # 8:00 AM daily
    # },
    # Example: Weekly data backup on Sundays at 2 AM
    # 'weekly-backup': {
    #     'task': 'common.tasks.backup_database',
    #     'schedule': crontab(hour=2, minute=0, day_of_week='sunday'),
    # },
}


# Celery Signal Handlers (for debugging and monitoring)
@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """Debug task to test Celery worker connectivity."""
    print(f"Request: {self.request!r}")


# Task execution hooks (optional - useful for logging/monitoring)
from celery.signals import task_prerun, task_postrun, task_failure


@task_prerun.connect
def task_prerun_handler(
    sender=None, task_id=None, task=None, args=None, kwargs=None, **extra
):
    """Called before a task is executed."""
    print(f"Task {task.name}[{task_id}] starting...")


@task_postrun.connect
def task_postrun_handler(
    sender=None, task_id=None, task=None, args=None, kwargs=None, retval=None, **extra
):
    """Called after a task is executed successfully."""
    print(f"Task {task.name}[{task_id}] completed successfully")


@task_failure.connect
def task_failure_handler(
    sender=None,
    task_id=None,
    exception=None,
    args=None,
    kwargs=None,
    traceback=None,
    einfo=None,
    **extra,
):
    """Called when a task fails."""
    print(f"Task {sender.name}[{task_id}] failed: {exception}")

"""
Context processors for Project Management Portal app.

Adds project-related data to all templates.
"""


def project_central_context(request):
    """
    Add Project Management Portal data to all templates.

    Provides:
    - unacknowledged_alerts_count: Count of unacknowledged alerts
    """
    if request.user.is_authenticated:
        # Import here to avoid circular imports
        from .models import Alert

        unacknowledged_alerts_count = Alert.objects.filter(
            is_acknowledged=False
        ).count()
    else:
        unacknowledged_alerts_count = 0

    return {
        "unacknowledged_alerts_count": unacknowledged_alerts_count,
    }

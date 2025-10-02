"""
Auditlog configuration for OBCMS.

Registers models for automatic audit trail logging.
This provides comprehensive tracking of all changes to sensitive data
for compliance and forensic purposes.
"""

from auditlog.registry import auditlog


def register_auditlog_models():
    """
    Register models with auditlog for automatic change tracking.

    Call this function during app initialization to enable audit logging
    for all security-sensitive models.
    """
    # Import models here to avoid circular imports
    from common.models import User, Region, Province, Municipality, Barangay
    from communities.models import BarangayOBC, MunicipalOBC, ProvincialOBC
    from mana.models import Assessment, AssessmentResponse, Workshop
    from coordination.models import Partnership, Stakeholder
    from project_central.models import Task, Workflow, Project

    # User and Authentication
    auditlog.register(
        User,
        exclude_fields=['password', 'last_login'],  # Don't log sensitive fields
        serialize_data=True,
    )

    # Geographic Data
    auditlog.register(Region, serialize_data=True)
    auditlog.register(Province, serialize_data=True)
    auditlog.register(Municipality, serialize_data=True)
    auditlog.register(Barangay, serialize_data=True)

    # OBC Community Data (High Value)
    auditlog.register(
        BarangayOBC,
        serialize_data=True,
        serialize_kwargs={'fields': '__all__'},
    )
    auditlog.register(
        MunicipalOBC,
        serialize_data=True,
        serialize_kwargs={'fields': '__all__'},
    )
    auditlog.register(
        ProvincialOBC,
        serialize_data=True,
        serialize_kwargs={'fields': '__all__'},
    )

    # MANA Assessment Data (High Value)
    auditlog.register(
        Assessment,
        serialize_data=True,
    )
    auditlog.register(
        AssessmentResponse,
        serialize_data=True,
    )
    auditlog.register(
        Workshop,
        serialize_data=True,
    )

    # Coordination Data
    auditlog.register(Partnership, serialize_data=True)
    auditlog.register(Stakeholder, serialize_data=True)

    # Project Management
    auditlog.register(Task, serialize_data=True)
    auditlog.register(Workflow, serialize_data=True)
    auditlog.register(Project, serialize_data=True)

    print("✅ Auditlog registered for all security-sensitive models")

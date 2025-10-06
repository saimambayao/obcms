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
    from communities.models import (
        OBCCommunity,
        MunicipalityCoverage,
        ProvinceCoverage,
        CommunityLivelihood,
        CommunityInfrastructure,
    )
    from mana.models import (
        Assessment,
        Survey,
        SurveyResponse,
        WorkshopSession,
        WorkshopResponse,
        WorkshopParticipant,
    )
    from coordination.models import (
        Partnership,
        StakeholderEngagement,
        Organization,
        MAOFocalPerson,
    )
    from project_central.models import (
        # ProjectWorkflow,  # DEPRECATED: Replaced by WorkItem system
        BudgetCeiling,
        BudgetScenario,
        Alert,
    )

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
        OBCCommunity,
        serialize_data=True,
        serialize_kwargs={'fields': '__all__'},
    )
    auditlog.register(
        MunicipalityCoverage,
        serialize_data=True,
        serialize_kwargs={'fields': '__all__'},
    )
    auditlog.register(
        ProvinceCoverage,
        serialize_data=True,
        serialize_kwargs={'fields': '__all__'},
    )
    auditlog.register(
        CommunityLivelihood,
        serialize_data=True,
    )
    auditlog.register(
        CommunityInfrastructure,
        serialize_data=True,
    )

    # MANA Assessment Data (High Value)
    auditlog.register(
        Assessment,
        serialize_data=True,
    )
    auditlog.register(
        Survey,
        serialize_data=True,
    )
    auditlog.register(
        SurveyResponse,
        serialize_data=True,
    )
    auditlog.register(
        WorkshopSession,
        serialize_data=True,
    )
    auditlog.register(
        WorkshopResponse,
        serialize_data=True,
    )
    auditlog.register(
        WorkshopParticipant,
        serialize_data=True,
    )

    # Coordination Data
    auditlog.register(Partnership, serialize_data=True)
    auditlog.register(StakeholderEngagement, serialize_data=True)
    auditlog.register(Organization, serialize_data=True)
    auditlog.register(MAOFocalPerson, serialize_data=True)

    # Project Management
    # auditlog.register(ProjectWorkflow, serialize_data=True)  # DEPRECATED: Replaced by WorkItem
    auditlog.register(BudgetCeiling, serialize_data=True)
    auditlog.register(BudgetScenario, serialize_data=True)
    auditlog.register(Alert, serialize_data=True)

    # Register WorkItem instead of deprecated ProjectWorkflow (with specific fields for compliance)
    from common.models import WorkItem
    auditlog.register(
        WorkItem,
        include_fields=[
            'title',
            'work_type',
            'status',
            'priority',
            'progress',
            'related_ppa',
            'allocated_budget',
            'actual_expenditure',
            'parent',
            'start_date',
            'due_date',
        ],
        serialize_data=True,
    )

    # Register MonitoringEntry for PPA compliance tracking
    from monitoring.models import MonitoringEntry
    auditlog.register(
        MonitoringEntry,
        include_fields=[
            'title',
            'category',
            'status',
            'approval_status',
            'budget_allocation',
            'budget_obc_allocation',
            'implementing_moa',
            'lead_organization',
            'fiscal_year',
            'plan_year',
            'funding_source',
            'appropriation_class',
        ],
        serialize_data=True,
    )

    print("✅ Auditlog registered for all security-sensitive models")

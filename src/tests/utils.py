"""
Test utilities for BMMS organization testing.

This module provides helper functions and utilities for testing
organization-scoped functionality in OBCMS/BMMS.
"""
from contextlib import contextmanager
from organizations.models.scoped import (
    set_current_organization,
    get_current_organization,
    clear_current_organization
)


@contextmanager
def organization_context(organization):
    """
    Context manager for temporarily setting organization context.

    Usage:
        with organization_context(my_org):
            # Code here runs with my_org as current organization
            communities = OBCCommunity.objects.all()
        # Organization context is automatically cleared

    Args:
        organization: Organization instance to set as current

    Yields:
        Organization: The current organization
    """
    previous_org = get_current_organization()
    try:
        set_current_organization(organization)
        yield organization
    finally:
        if previous_org:
            set_current_organization(previous_org)
        else:
            clear_current_organization()


def switch_organization(organization):
    """
    Switch to a different organization context.

    Args:
        organization: Organization to switch to

    Returns:
        Organization: The organization that was set
    """
    set_current_organization(organization)
    return organization


def create_test_data_for_org(organization, model_class, count=5, **defaults):
    """
    Create test data for a specific organization.

    Args:
        organization: Organization to create data for
        model_class: Model class to create instances of
        count: Number of instances to create
        **defaults: Default field values

    Returns:
        list: Created model instances
    """
    with organization_context(organization):
        instances = []
        for i in range(count):
            # Merge index into defaults
            data = defaults.copy()
            if 'name' in defaults:
                data['name'] = f"{defaults['name']} {i}"

            instance = model_class.objects.create(**data)
            instances.append(instance)

        return instances


def assert_organization_isolation(model_class, org1, org2, count1, count2):
    """
    Assert that two organizations have proper data isolation.

    Args:
        model_class: Model class to check
        org1: First organization
        org2: Second organization
        count1: Expected count for org1
        count2: Expected count for org2

    Raises:
        AssertionError: If counts don't match
    """
    with organization_context(org1):
        actual_count1 = model_class.objects.count()
        assert actual_count1 == count1, (
            f"Expected {count1} records for {org1.code}, "
            f"got {actual_count1}"
        )

    with organization_context(org2):
        actual_count2 = model_class.objects.count()
        assert actual_count2 == count2, (
            f"Expected {count2} records for {org2.code}, "
            f"got {actual_count2}"
        )


def assert_no_cross_org_access(model_class, org1, org2, org1_data, org2_data):
    """
    Assert that data from one org is not accessible from another.

    Args:
        model_class: Model class to check
        org1: First organization
        org2: Second organization
        org1_data: Data belonging to org1
        org2_data: Data belonging to org2

    Raises:
        AssertionError: If cross-organization access is detected
    """
    with organization_context(org1):
        # Org1 should see only org1 data
        visible_data = model_class.objects.all()
        visible_ids = set(visible_data.values_list('id', flat=True))
        org2_ids = set([item.id for item in org2_data])

        assert not visible_ids.intersection(org2_ids), (
            f"Organization {org1.code} can see data from {org2.code}"
        )

    with organization_context(org2):
        # Org2 should see only org2 data
        visible_data = model_class.objects.all()
        visible_ids = set(visible_data.values_list('id', flat=True))
        org1_ids = set([item.id for item in org1_data])

        assert not visible_ids.intersection(org1_ids), (
            f"Organization {org2.code} can see data from {org1.code}"
        )


def assert_all_objects_unfiltered(model_class, expected_total):
    """
    Assert that all_objects manager returns unfiltered results.

    Args:
        model_class: Model class to check
        expected_total: Expected total count across all orgs

    Raises:
        AssertionError: If all_objects is filtered
    """
    clear_current_organization()
    actual_total = model_class.all_objects.count()
    assert actual_total == expected_total, (
        f"Expected {expected_total} total records, "
        f"got {actual_total}"
    )


def get_org_from_user(user):
    """
    Get the primary organization for a user.

    Args:
        user: User instance

    Returns:
        Organization or None: User's primary organization
    """
    from organizations.models import OrganizationMembership

    membership = OrganizationMembership.objects.filter(
        user=user,
        is_primary=True,
        is_active=True
    ).first()

    return membership.organization if membership else None


def create_org_membership(user, organization, role='staff', **kwargs):
    """
    Create organization membership for a user.

    Args:
        user: User instance
        organization: Organization instance
        role: User role in organization
        **kwargs: Additional membership fields

    Returns:
        OrganizationMembership: Created membership
    """
    from organizations.models import OrganizationMembership

    defaults = {
        'role': role,
        'is_primary': True,
        'is_active': True,
    }
    defaults.update(kwargs)

    membership = OrganizationMembership.objects.create(
        user=user,
        organization=organization,
        **defaults
    )

    return membership


def assert_user_org_access(client, user, organization, url, should_access=True):
    """
    Assert whether a user can access a URL for a specific organization.

    Args:
        client: Django test client
        user: User instance
        organization: Organization instance
        url: URL to test
        should_access: Whether user should have access

    Raises:
        AssertionError: If access doesn't match expectation
    """
    client.force_login(user)

    with organization_context(organization):
        response = client.get(url)

        if should_access:
            assert response.status_code in [200, 302], (
                f"User {user.username} should access {url} "
                f"for org {organization.code}, got {response.status_code}"
            )
        else:
            assert response.status_code in [403, 404], (
                f"User {user.username} should NOT access {url} "
                f"for org {organization.code}, got {response.status_code}"
            )


def bulk_create_for_org(organization, model_class, items_data):
    """
    Bulk create instances for an organization.

    Args:
        organization: Organization instance
        model_class: Model class to create instances of
        items_data: List of dicts with field values

    Returns:
        list: Created instances
    """
    with organization_context(organization):
        instances = [model_class(**data) for data in items_data]
        created = model_class.objects.bulk_create(instances)
        return created


def get_queryset_for_org(model_class, organization):
    """
    Get queryset for a specific organization.

    Args:
        model_class: Model class
        organization: Organization instance

    Returns:
        QuerySet: Filtered queryset
    """
    with organization_context(organization):
        return model_class.objects.all()


def verify_org_field_set(instance, expected_org):
    """
    Verify that an instance has the correct organization field.

    Args:
        instance: Model instance
        expected_org: Expected organization

    Raises:
        AssertionError: If organization doesn't match
    """
    assert hasattr(instance, 'organization'), (
        f"{instance.__class__.__name__} missing organization field"
    )
    assert instance.organization == expected_org, (
        f"Expected organization {expected_org.code}, "
        f"got {instance.organization.code if instance.organization else None}"
    )


class OrganizationTestDataFactory:
    """
    Factory for creating test data with organization context.
    """

    def __init__(self, organization):
        """
        Initialize factory for an organization.

        Args:
            organization: Organization instance
        """
        self.organization = organization

    def create_community(self, **kwargs):
        """Create OBCCommunity for this organization."""
        from communities.models import OBCCommunity

        defaults = {'barangay_id': 1}
        defaults.update(kwargs)

        with organization_context(self.organization):
            return OBCCommunity.objects.create(**defaults)

    def create_assessment(self, **kwargs):
        """Create Assessment for this organization."""
        from mana.models import Assessment

        defaults = {
            'title': 'Test Assessment',
            'assessment_type': 'needs',
            'status': 'draft'
        }
        defaults.update(kwargs)

        with organization_context(self.organization):
            return Assessment.objects.create(**defaults)

    def create_engagement(self, **kwargs):
        """Create StakeholderEngagement for this organization."""
        from coordination.models import StakeholderEngagement

        defaults = {
            'title': 'Test Engagement',
            'engagement_type': 'consultation',
            'status': 'planned'
        }
        defaults.update(kwargs)

        with organization_context(self.organization):
            return StakeholderEngagement.objects.create(**defaults)

    def create_ppa(self, **kwargs):
        """Create PPA for this organization."""
        from monitoring.models import PPA

        defaults = {
            'title': 'Test PPA',
            'ppa_type': 'program',
            'status': 'active'
        }
        defaults.update(kwargs)

        with organization_context(self.organization):
            return PPA.objects.create(**defaults)


def clear_org_data(organization, *model_classes):
    """
    Clear all data for an organization.

    Args:
        organization: Organization instance
        *model_classes: Model classes to clear
    """
    with organization_context(organization):
        for model_class in model_classes:
            model_class.objects.all().delete()

"""
Tests for organization scoping and auto-filtering.

This module tests the OrganizationScopedModel functionality,
ensuring proper data isolation between organizations.
"""
import pytest
from organizations.models.scoped import (
    set_current_organization,
    clear_current_organization,
    get_current_organization
)


@pytest.mark.django_db
class TestOrganizationScoping:
    """Test organization-based data isolation."""

    def test_obccommunity_auto_filters_by_organization(
        self, default_organization, pilot_moh_organization
    ):
        """Test OBCCommunity filters by current organization."""
        from communities.models import OBCCommunity

        # Create communities for different orgs
        set_current_organization(default_organization)
        oobc_comm = OBCCommunity.objects.create(
            name='OOBC Community',
            barangay_id=1,
        )

        set_current_organization(pilot_moh_organization)
        moh_comm = OBCCommunity.objects.create(
            name='MOH Community',
            barangay_id=2,
        )

        # Test OOBC context
        set_current_organization(default_organization)
        communities = OBCCommunity.objects.all()
        assert communities.count() == 1
        assert communities.first().name == 'OOBC Community'

        # Test MOH context
        set_current_organization(pilot_moh_organization)
        communities = OBCCommunity.objects.all()
        assert communities.count() == 1
        assert communities.first().name == 'MOH Community'

        # Test all_objects manager (no filter)
        all_communities = OBCCommunity.all_objects.all()
        assert all_communities.count() == 2

        clear_current_organization()

    def test_assessment_auto_filters_by_organization(
        self, default_organization, pilot_moh_organization
    ):
        """Test Assessment filters by current organization."""
        from mana.models import Assessment

        set_current_organization(default_organization)
        oobc_assess = Assessment.objects.create(
            title='OOBC Assessment',
            assessment_type='needs',
            status='draft',
        )

        set_current_organization(pilot_moh_organization)
        moh_assess = Assessment.objects.create(
            title='MOH Assessment',
            assessment_type='needs',
            status='draft',
        )

        # Test isolation
        set_current_organization(default_organization)
        assessments = Assessment.objects.all()
        assert assessments.count() == 1
        assert assessments.first().title == 'OOBC Assessment'

        set_current_organization(pilot_moh_organization)
        assessments = Assessment.objects.all()
        assert assessments.count() == 1
        assert assessments.first().title == 'MOH Assessment'

        clear_current_organization()

    def test_stakeholder_engagement_auto_filters(
        self, default_organization, pilot_moh_organization
    ):
        """Test StakeholderEngagement filters by current organization."""
        from coordination.models import StakeholderEngagement

        set_current_organization(default_organization)
        oobc_engagement = StakeholderEngagement.objects.create(
            title='OOBC Engagement',
            engagement_type='consultation',
            status='planned',
        )

        set_current_organization(pilot_moh_organization)
        moh_engagement = StakeholderEngagement.objects.create(
            title='MOH Engagement',
            engagement_type='consultation',
            status='planned',
        )

        # Test isolation
        set_current_organization(default_organization)
        engagements = StakeholderEngagement.objects.all()
        assert engagements.count() == 1
        assert engagements.first().title == 'OOBC Engagement'

        set_current_organization(pilot_moh_organization)
        engagements = StakeholderEngagement.objects.all()
        assert engagements.count() == 1
        assert engagements.first().title == 'MOH Engagement'

        clear_current_organization()

    def test_ppa_auto_filters_by_organization(
        self, default_organization, pilot_moh_organization
    ):
        """Test PPA filters by current organization."""
        from monitoring.models import PPA

        set_current_organization(default_organization)
        oobc_ppa = PPA.objects.create(
            title='OOBC PPA',
            ppa_type='program',
            status='active',
        )

        set_current_organization(pilot_moh_organization)
        moh_ppa = PPA.objects.create(
            title='MOH PPA',
            ppa_type='program',
            status='active',
        )

        # Test isolation
        set_current_organization(default_organization)
        ppas = PPA.objects.all()
        assert ppas.count() == 1
        assert ppas.first().title == 'OOBC PPA'

        set_current_organization(pilot_moh_organization)
        ppas = PPA.objects.all()
        assert ppas.count() == 1
        assert ppas.first().title == 'MOH PPA'

        clear_current_organization()

    def test_cross_organization_data_leak_prevented(
        self, default_organization, pilot_moh_organization
    ):
        """Test that switching organizations doesn't leak data."""
        from communities.models import OBCCommunity

        # Create data for OOBC
        set_current_organization(default_organization)
        for i in range(10):
            OBCCommunity.objects.create(
                name=f'OOBC Community {i}',
                barangay_id=i+1,
            )

        # Create data for MOH
        set_current_organization(pilot_moh_organization)
        for i in range(5):
            OBCCommunity.objects.create(
                name=f'MOH Community {i}',
                barangay_id=i+11,
            )

        # Verify OOBC sees only 10
        set_current_organization(default_organization)
        assert OBCCommunity.objects.count() == 10

        # Verify MOH sees only 5
        set_current_organization(pilot_moh_organization)
        assert OBCCommunity.objects.count() == 5

        # Verify admin sees all 15
        clear_current_organization()
        assert OBCCommunity.all_objects.count() == 15

    def test_all_objects_manager_bypass_filter(
        self, default_organization, pilot_moh_organization
    ):
        """Test all_objects manager bypasses organization filter."""
        from communities.models import OBCCommunity

        set_current_organization(default_organization)
        for i in range(3):
            OBCCommunity.objects.create(name=f'OOBC {i}', barangay_id=i+1)

        set_current_organization(pilot_moh_organization)
        for i in range(3):
            OBCCommunity.objects.create(name=f'MOH {i}', barangay_id=i+11)

        # Normal manager sees filtered
        set_current_organization(default_organization)
        assert OBCCommunity.objects.count() == 3

        # all_objects sees all
        assert OBCCommunity.all_objects.count() == 6

        clear_current_organization()

    def test_organization_auto_set_on_save(
        self, default_organization
    ):
        """Test organization is auto-set when saving new object."""
        from communities.models import OBCCommunity

        set_current_organization(default_organization)

        # Create without explicitly setting organization
        comm = OBCCommunity.objects.create(
            name='Auto Org Community',
            barangay_id=1,
        )

        # Organization should be auto-set
        assert comm.organization == default_organization

        clear_current_organization()

    def test_for_organization_method(
        self, default_organization, pilot_moh_organization
    ):
        """Test for_organization() method works correctly."""
        from communities.models import OBCCommunity

        set_current_organization(default_organization)
        OBCCommunity.objects.create(name='OOBC Comm', barangay_id=1)

        set_current_organization(pilot_moh_organization)
        OBCCommunity.objects.create(name='MOH Comm', barangay_id=2)

        clear_current_organization()

        # Explicitly filter by organization
        oobc_communities = OBCCommunity.objects.for_organization(default_organization)
        assert oobc_communities.count() == 1
        assert oobc_communities.first().name == 'OOBC Comm'

        moh_communities = OBCCommunity.objects.for_organization(pilot_moh_organization)
        assert moh_communities.count() == 1
        assert moh_communities.first().name == 'MOH Comm'

    def test_get_current_organization(
        self, default_organization
    ):
        """Test get_current_organization() utility function."""
        # Initially no organization
        assert get_current_organization() is None

        # Set organization
        set_current_organization(default_organization)
        assert get_current_organization() == default_organization

        # Clear organization
        clear_current_organization()
        assert get_current_organization() is None

    def test_multiple_model_types_isolated(
        self, default_organization, pilot_moh_organization
    ):
        """Test that different model types maintain isolation."""
        from communities.models import OBCCommunity
        from mana.models import Assessment

        set_current_organization(default_organization)
        OBCCommunity.objects.create(name='OOBC Comm', barangay_id=1)
        Assessment.objects.create(
            title='OOBC Assessment',
            assessment_type='needs',
            status='draft'
        )

        set_current_organization(pilot_moh_organization)
        OBCCommunity.objects.create(name='MOH Comm', barangay_id=2)
        Assessment.objects.create(
            title='MOH Assessment',
            assessment_type='needs',
            status='draft'
        )

        # Verify OOBC sees only its data
        set_current_organization(default_organization)
        assert OBCCommunity.objects.count() == 1
        assert Assessment.objects.count() == 1

        # Verify MOH sees only its data
        set_current_organization(pilot_moh_organization)
        assert OBCCommunity.objects.count() == 1
        assert Assessment.objects.count() == 1

        clear_current_organization()

    def test_bulk_create_with_organization(
        self, default_organization
    ):
        """Test bulk_create respects organization context."""
        from communities.models import OBCCommunity

        set_current_organization(default_organization)

        # Bulk create
        communities = [
            OBCCommunity(name=f'Bulk Community {i}', barangay_id=i+1)
            for i in range(5)
        ]
        OBCCommunity.objects.bulk_create(communities)

        # All should belong to default organization
        created = OBCCommunity.objects.all()
        assert created.count() == 5
        for comm in created:
            assert comm.organization == default_organization

        clear_current_organization()

    def test_organization_filter_in_related_queries(
        self, default_organization, pilot_moh_organization
    ):
        """Test organization filtering works in related queries."""
        from communities.models import OBCCommunity
        from mana.models import Assessment

        # Create communities and assessments
        set_current_organization(default_organization)
        oobc_comm = OBCCommunity.objects.create(name='OOBC Comm', barangay_id=1)

        set_current_organization(pilot_moh_organization)
        moh_comm = OBCCommunity.objects.create(name='MOH Comm', barangay_id=2)

        # Query from OOBC context
        set_current_organization(default_organization)
        communities = OBCCommunity.objects.select_related('organization').all()
        assert communities.count() == 1
        assert communities.first().organization == default_organization

        clear_current_organization()

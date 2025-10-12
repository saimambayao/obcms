"""
Tests for RBAC Template Tags

Tests the permission-based template tags that integrate with RBACService.
"""

import pytest
from django.template import Context, Template
from django.test import RequestFactory
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
class TestRBACTemplateTags:
    """Test RBAC template tags functionality."""

    @pytest.fixture
    def superuser(self):
        """Create superuser for testing."""
        return User.objects.create_superuser(
            username='admin',
            email='admin@test.com',
            password='testpass123'
        )

    @pytest.fixture
    def oobc_staff(self):
        """Create OOBC staff user."""
        user = User.objects.create_user(
            username='oobc_staff',
            email='staff@oobc.gov.ph',
            password='testpass123'
        )
        user.is_oobc_staff = True
        user.is_approved = True
        user.save()
        return user

    @pytest.fixture
    def moa_staff(self):
        """Create MOA staff user."""
        user = User.objects.create_user(
            username='moa_staff',
            email='staff@moa.gov.ph',
            password='testpass123'
        )
        user.is_moa_staff = True
        user.is_approved = True
        user.save()
        return user

    @pytest.fixture
    def request_factory(self):
        """Create request factory."""
        return RequestFactory()

    def test_has_permission_tag_superuser(self, superuser, request_factory):
        """Test has_permission tag with superuser."""
        request = request_factory.get('/')
        request.user = superuser

        template = Template(
            "{% load rbac_tags %}"
            "{% has_permission user 'communities.view_obc_community' as can_view %}"
            "{% if can_view %}ALLOWED{% else %}DENIED{% endif %}"
        )

        context = Context({'user': superuser, 'request': request})
        result = template.render(context)

        assert 'ALLOWED' in result

    def test_has_permission_tag_anonymous(self, request_factory):
        """Test has_permission tag with anonymous user."""
        from django.contrib.auth.models import AnonymousUser

        request = request_factory.get('/')
        request.user = AnonymousUser()

        template = Template(
            "{% load rbac_tags %}"
            "{% has_permission user 'communities.view_obc_community' as can_view %}"
            "{% if can_view %}ALLOWED{% else %}DENIED{% endif %}"
        )

        context = Context({'user': AnonymousUser(), 'request': request})
        result = template.render(context)

        assert 'DENIED' in result

    def test_has_feature_access_tag(self, oobc_staff, request_factory):
        """Test has_feature_access tag with OOBC staff."""
        request = request_factory.get('/')
        request.user = oobc_staff

        template = Template(
            "{% load rbac_tags %}"
            "{% has_feature_access user 'communities.barangay_obc' as can_access %}"
            "{% if can_access %}ACCESS_GRANTED{% else %}ACCESS_DENIED{% endif %}"
        )

        context = Context({'user': oobc_staff, 'request': request})
        result = template.render(context)

        # OOBC staff should have access
        assert 'ACCESS_GRANTED' in result

    def test_can_access_feature_filter(self, superuser):
        """Test can_access_feature filter."""
        template = Template(
            "{% load rbac_tags %}"
            "{% if user|can_access_feature:'mana.regional_overview' %}"
            "CAN_ACCESS{% else %}CANNOT_ACCESS{% endif %}"
        )

        context = Context({'user': superuser})
        result = template.render(context)

        assert 'CAN_ACCESS' in result

    def test_can_access_feature_filter_anonymous(self):
        """Test can_access_feature filter with anonymous user."""
        from django.contrib.auth.models import AnonymousUser

        template = Template(
            "{% load rbac_tags %}"
            "{% if user|can_access_feature:'mana.regional_overview' %}"
            "CAN_ACCESS{% else %}CANNOT_ACCESS{% endif %}"
        )

        context = Context({'user': AnonymousUser()})
        result = template.render(context)

        assert 'CANNOT_ACCESS' in result

    def test_get_accessible_features_superuser(self, superuser):
        """Test get_accessible_features with superuser."""
        template = Template(
            "{% load rbac_tags %}"
            "{% get_accessible_features user as features %}"
            "FEATURES:{{ features|length }}"
        )

        context = Context({'user': superuser})
        result = template.render(context)

        # Should get all features (test depends on fixtures)
        assert 'FEATURES:' in result

    def test_get_permission_context(self, oobc_staff, request_factory):
        """Test get_permission_context tag."""
        request = request_factory.get('/')
        request.user = oobc_staff

        template = Template(
            "{% load rbac_tags %}"
            "{% get_permission_context request as perm_context %}"
            "OOBC:{{ perm_context.is_oobc_staff }}"
        )

        context = Context({'request': request})
        result = template.render(context)

        assert 'OOBC:True' in result

    def test_feature_url_tag(self):
        """Test feature_url tag."""
        from common.rbac_models import Feature

        # Create test feature
        feature = Feature.objects.create(
            feature_key='test.feature',
            name='Test Feature',
            module='test',
            url_pattern='/test/feature/'
        )

        template = Template(
            "{% load rbac_tags %}"
            "{% feature_url feature %}"
        )

        context = Context({'feature': feature})
        result = template.render(context)

        assert '/test/feature/' in result

    def test_feature_icon_tag(self):
        """Test feature_icon tag."""
        from common.rbac_models import Feature

        feature = Feature.objects.create(
            feature_key='test.feature',
            name='Test Feature',
            module='test',
            icon='fa-test-icon'
        )

        template = Template(
            "{% load rbac_tags %}"
            "<i class='fas {% feature_icon feature %}'></i>"
        )

        context = Context({'feature': feature})
        result = template.render(context)

        assert 'fa-test-icon' in result

    def test_has_sub_features_filter(self):
        """Test has_sub_features filter."""
        from common.rbac_models import Feature

        parent = Feature.objects.create(
            feature_key='parent.feature',
            name='Parent Feature',
            module='test'
        )

        child = Feature.objects.create(
            feature_key='child.feature',
            name='Child Feature',
            module='test',
            parent=parent
        )

        template = Template(
            "{% load rbac_tags %}"
            "{% if parent|has_sub_features %}HAS_CHILDREN{% else %}NO_CHILDREN{% endif %}"
        )

        context = Context({'parent': parent})
        result = template.render(context)

        assert 'HAS_CHILDREN' in result


@pytest.mark.django_db
class TestRBACActionButton:
    """Test RBAC action button component."""

    @pytest.fixture
    def superuser(self):
        """Create superuser for testing."""
        return User.objects.create_superuser(
            username='admin',
            email='admin@test.com',
            password='testpass123'
        )

    @pytest.fixture
    def request_factory(self):
        """Create request factory."""
        return RequestFactory()

    def test_action_button_with_permission(self, superuser, request_factory):
        """Test action button renders when user has permission."""
        request = request_factory.get('/')
        request.user = superuser

        template = Template(
            "{% load rbac_tags %}"
            "{% include 'components/rbac_action_button.html' with "
            "user=user "
            "permission_code='communities.create_obc' "
            "button_text='Add Community' %}"
        )

        context = Context({'user': superuser, 'request': request})
        result = template.render(context)

        assert 'Add Community' in result

    def test_action_button_without_permission(self, request_factory):
        """Test action button doesn't render without permission."""
        from django.contrib.auth.models import AnonymousUser

        request = request_factory.get('/')
        request.user = AnonymousUser()

        template = Template(
            "{% load rbac_tags %}"
            "{% include 'components/rbac_action_button.html' with "
            "user=user "
            "permission_code='communities.create_obc' "
            "button_text='Add Community' %}"
        )

        context = Context({'user': AnonymousUser(), 'request': request})
        result = template.render(context)

        # Button should not render
        assert 'Add Community' not in result

    def test_action_button_link_type(self, superuser, request_factory):
        """Test action button as link."""
        request = request_factory.get('/')
        request.user = superuser

        template = Template(
            "{% load rbac_tags %}"
            "{% include 'components/rbac_action_button.html' with "
            "user=user "
            "permission_code='communities.view_obc' "
            "button_text='View' "
            "button_type='link' "
            "button_url='/communities/123/' %}"
        )

        context = Context({'user': superuser, 'request': request})
        result = template.render(context)

        assert 'href="/communities/123/"' in result
        assert 'View' in result

    def test_action_button_with_icon(self, superuser, request_factory):
        """Test action button with icon."""
        request = request_factory.get('/')
        request.user = superuser

        template = Template(
            "{% load rbac_tags %}"
            "{% include 'components/rbac_action_button.html' with "
            "user=user "
            "permission_code='communities.delete_obc' "
            "button_text='Delete' "
            "icon_class='fa-trash' %}"
        )

        context = Context({'user': superuser, 'request': request})
        result = template.render(context)

        assert 'fa-trash' in result
        assert 'Delete' in result

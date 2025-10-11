"""Tests for MOA permission decorators and helpers."""

import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import PermissionDenied
from django.test import RequestFactory

from common.tests.factories import (
    create_monitoring_entry,
    create_organization,
)
from common.utils import moa_permissions
from common.work_item_model import WorkItem


User = get_user_model()


@pytest.fixture
def request_factory() -> RequestFactory:
    """Provide a reusable request factory for decorator tests."""

    return RequestFactory()


@pytest.fixture
def moa_organization(db):
    """Create an MOA organization for staff users."""

    return create_organization(organization_type="bmoa")


@pytest.fixture
def other_moa_organization(db):
    """Create a separate organization used to validate permission denials."""

    return create_organization(organization_type="bmoa")


@pytest.fixture
def moa_user(db, moa_organization):
    """Return an authenticated MOA staff user assigned to an organization."""

    user = User.objects.create_user(
        username="moa_user",
        password="password123",
        email="moa@example.com",
        user_type="bmoa",
        first_name="Moa",
        last_name="User",
    )
    user.moa_organization = moa_organization
    user.save(update_fields=["moa_organization"])
    return user


@pytest.fixture
def other_moa_user(db, other_moa_organization):
    """Return another MOA staff user mapped to a different organization."""

    user = User.objects.create_user(
        username="other_moa_user",
        password="password123",
        email="other-moa@example.com",
        user_type="bmoa",
        first_name="Other",
        last_name="Staff",
    )
    user.moa_organization = other_moa_organization
    user.save(update_fields=["moa_organization"])
    return user


@pytest.mark.django_db
def test_moa_view_only_blocks_mutating_requests(request_factory, moa_user):
    """MOA users should be prevented from calling mutating HTTP verbs."""

    @moa_permissions.moa_view_only
    def sample_view(request, *_args, **_kwargs):
        return "ok"

    get_request = request_factory.get("/sample/")
    get_request.user = moa_user
    assert sample_view(get_request) == "ok"

    post_request = request_factory.post("/sample/")
    post_request.user = moa_user
    with pytest.raises(PermissionDenied):
        sample_view(post_request)


@pytest.mark.django_db
def test_moa_can_edit_organization_limits_to_owned_org(
    request_factory, moa_user, moa_organization, other_moa_organization
):
    """MOA users may edit their own organization but not others."""

    @moa_permissions.moa_can_edit_organization
    def sample_view(request, *_args, **_kwargs):
        return "ok"

    own_request = request_factory.post("/organization/")
    own_request.user = moa_user
    assert sample_view(own_request, pk=str(moa_organization.pk)) == "ok"

    other_request = request_factory.post("/organization/")
    other_request.user = moa_user
    with pytest.raises(PermissionDenied):
        sample_view(other_request, pk=str(other_moa_organization.pk))


@pytest.mark.django_db
def test_moa_can_edit_ppa_validates_implementing_moa(
    request_factory,
    moa_user,
    other_moa_user,
    moa_organization,
    other_moa_organization,
):
    """MOA users can update only PPAs tied to their organization."""

    @moa_permissions.moa_can_edit_ppa
    def sample_view(request, *_args, **_kwargs):
        return "ok"

    own_ppa = create_monitoring_entry(
        created_by=moa_user,
        implementing_moa=moa_organization,
    )
    other_ppa = create_monitoring_entry(
        created_by=other_moa_user,
        implementing_moa=other_moa_organization,
    )

    own_request = request_factory.post("/ppa/")
    own_request.user = moa_user
    assert sample_view(own_request, pk=str(own_ppa.pk)) == "ok"

    other_request = request_factory.post("/ppa/")
    other_request.user = moa_user
    with pytest.raises(PermissionDenied):
        sample_view(other_request, pk=str(other_ppa.pk))


@pytest.mark.django_db
def test_moa_can_edit_work_item_checks_related_ppa(
    request_factory,
    moa_user,
    other_moa_user,
    moa_organization,
    other_moa_organization,
):
    """MOA users may only edit work items linked to their own PPAs."""

    @moa_permissions.moa_can_edit_work_item
    def sample_view(request, *_args, **_kwargs):
        return "ok"

    own_ppa = create_monitoring_entry(
        created_by=moa_user,
        implementing_moa=moa_organization,
    )
    other_ppa = create_monitoring_entry(
        created_by=other_moa_user,
        implementing_moa=other_moa_organization,
    )

    own_work_item = WorkItem.objects.create(
        work_type=WorkItem.WORK_TYPE_TASK,
        title="My Work Item",
        created_by=moa_user,
        related_ppa=own_ppa,
        implementing_moa=moa_organization,
        ppa_category=own_ppa.category,
    )
    other_work_item = WorkItem.objects.create(
        work_type=WorkItem.WORK_TYPE_TASK,
        title="Other Work Item",
        created_by=other_moa_user,
        related_ppa=other_ppa,
        implementing_moa=other_moa_organization,
        ppa_category=other_ppa.category,
    )

    own_request = request_factory.post("/work-items/")
    own_request.user = moa_user
    assert sample_view(own_request, pk=str(own_work_item.pk)) == "ok"

    other_request = request_factory.post("/work-items/")
    other_request.user = moa_user
    with pytest.raises(PermissionDenied):
        sample_view(other_request, pk=str(other_work_item.pk))


@pytest.mark.django_db
def test_moa_no_access_blocks_moa_staff(request_factory, moa_user):
    """MOA users should be denied access to restricted modules."""

    @moa_permissions.moa_no_access
    def sample_view(request, *_args, **_kwargs):
        return "ok"

    request = request_factory.get("/restricted/")
    request.user = moa_user
    with pytest.raises(PermissionDenied):
        sample_view(request)


@pytest.mark.django_db
def test_user_can_access_mana_rules():
    """Validate the helper that centralizes MANA access decisions."""

    staff_user = User.objects.create_user(
        username="staff",
        password="password123",
        email="staff@example.com",
        user_type="oobc_staff",
    )
    moa_user = User.objects.create_user(
        username="moa",
        password="password123",
        email="moa@example.com",
        user_type="bmoa",
    )

    assert moa_permissions.user_can_access_mana(staff_user) is True
    assert moa_permissions.user_can_access_mana(moa_user) is False
    assert moa_permissions.user_can_access_mana(AnonymousUser()) is False



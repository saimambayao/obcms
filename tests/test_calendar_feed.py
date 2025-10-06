import json
from datetime import date

import pytest
from django.test import RequestFactory
from django.contrib.auth import get_user_model

from common.views.calendar import work_items_calendar_feed
from common.work_item_model import WorkItem


pytestmark = pytest.mark.django_db


def test_work_items_calendar_feed_returns_data(rf: RequestFactory):
    user = get_user_model().objects.create_user(
        username="calendar_tester",
        password="example123",
        email="calendar@example.com",
        user_type="oobc_staff",
        is_approved=True,
    )

    WorkItem.objects.create(
        work_type=WorkItem.WORK_TYPE_PROJECT,
        title="Calendar Integration Test",
        start_date=date(2025, 1, 1),
        due_date=date(2025, 1, 5),
        created_by=user,
    )

    request = rf.get("/oobc-management/calendar/work-items/feed/")
    request.user = user

    response = work_items_calendar_feed(request)
    assert response.status_code == 200

    payload = json.loads(response.content)
    assert isinstance(payload, dict)
    assert "workItems" in payload
    assert payload["workItems"], "Calendar feed should include at least one work item"

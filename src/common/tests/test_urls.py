"""URL routing regressions for community CRUD views."""

from django.test import SimpleTestCase
from django.urls import resolve, reverse

from common.views.communities import (
    communities_delete,
    communities_delete_municipal,
    communities_edit,
    communities_edit_municipal,
    communities_restore,
    communities_restore_municipal,
)
from common.views.management import (
    oobc_calendar,
    oobc_calendar_feed_json,
    oobc_calendar_feed_ics,
    oobc_calendar_brief,
)


class CommunityUrlTests(SimpleTestCase):
    """Ensure barangay and municipal CRUD URLs route to the expected views."""

    def test_barangay_edit_url(self) -> None:
        url = reverse("communities:communities_edit", args=[1])
        self.assertEqual(url, "/communities/1/edit/")
        self.assertIs(resolve(url).func, communities_edit)

    def test_barangay_delete_url(self) -> None:
        url = reverse("communities:communities_delete", args=[1])
        self.assertEqual(url, "/communities/1/delete/")
        self.assertIs(resolve(url).func, communities_delete)

    def test_municipal_edit_url(self) -> None:
        url = reverse("communities:communities_edit_municipal", args=[2])
        self.assertEqual(url, "/communities/municipal/2/edit/")
        self.assertIs(resolve(url).func, communities_edit_municipal)

    def test_municipal_delete_url(self) -> None:
        url = reverse("communities:communities_delete_municipal", args=[2])
        self.assertEqual(url, "/communities/municipal/2/delete/")
        self.assertIs(resolve(url).func, communities_delete_municipal)

    def test_barangay_restore_url(self) -> None:
        url = reverse("communities:communities_restore", args=[1])
        self.assertEqual(url, "/communities/1/restore/")
        self.assertIs(resolve(url).func, communities_restore)

    def test_municipal_restore_url(self) -> None:
        url = reverse("communities:communities_restore_municipal", args=[2])
        self.assertEqual(url, "/communities/municipal/2/restore/")
        self.assertIs(resolve(url).func, communities_restore_municipal)

    def test_oobc_calendar_url(self) -> None:
        url = reverse("common:oobc_calendar")
        self.assertEqual(url, "/oobc-management/calendar/")
        self.assertIs(resolve(url).func, oobc_calendar)

    def test_oobc_calendar_feed_json_url(self) -> None:
        url = reverse("common:oobc_calendar_feed_json")
        self.assertEqual(url, "/oobc-management/calendar/feed/json/")
        self.assertIs(resolve(url).func, oobc_calendar_feed_json)

    def test_oobc_calendar_feed_ics_url(self) -> None:
        url = reverse("common:oobc_calendar_feed_ics")
        self.assertEqual(url, "/oobc-management/calendar/feed/ics/")
        self.assertIs(resolve(url).func, oobc_calendar_feed_ics)

    def test_oobc_calendar_brief_url(self) -> None:
        url = reverse("common:oobc_calendar_brief")
        self.assertEqual(url, "/oobc-management/calendar/brief/")
        self.assertIs(resolve(url).func, oobc_calendar_brief)

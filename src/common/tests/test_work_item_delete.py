"""
Tests for WorkItem deletion functionality.

Verifies:
- DELETE request handling
- HTMX response headers
- Calendar event removal
- Cascade deletion
"""

import json
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from common.work_item_model import WorkItem

User = get_user_model()


class WorkItemDeleteTest(TestCase):
    """Test work item deletion from calendar modal."""

    def setUp(self):
        """Create test user and work items."""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')

        # Create a test work item (activity)
        self.work_item = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_ACTIVITY,
            title='Test Activity',
            description='Test description',
            status=WorkItem.STATUS_NOT_STARTED,
            priority=WorkItem.PRIORITY_MEDIUM,
            created_by=self.user
        )

        # Create a child task
        self.child_task = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title='Child Task',
            description='Child task description',
            status=WorkItem.STATUS_NOT_STARTED,
            priority=WorkItem.PRIORITY_LOW,
            parent=self.work_item,
            created_by=self.user
        )

    def test_delete_view_allows_delete_method(self):
        """Test that DELETE method is allowed."""
        url = reverse('common:work_item_delete', kwargs={'pk': self.work_item.pk})
        response = self.client.delete(url)

        # Should not be 405 Method Not Allowed
        self.assertNotEqual(response.status_code, 405)

    def test_delete_request_removes_work_item(self):
        """Test DELETE request actually deletes the work item."""
        url = reverse('common:work_item_delete', kwargs={'pk': self.work_item.pk})
        work_item_id = str(self.work_item.pk)

        response = self.client.delete(url)

        # Should return 200 OK
        self.assertEqual(response.status_code, 200)

        # Work item should be deleted
        self.assertFalse(WorkItem.objects.filter(pk=self.work_item.pk).exists())

        # Child should also be deleted (cascade)
        self.assertFalse(WorkItem.objects.filter(pk=self.child_task.pk).exists())

    def test_delete_response_has_htmx_headers(self):
        """Test DELETE response includes HX-Trigger headers."""
        url = reverse('common:work_item_delete', kwargs={'pk': self.work_item.pk})
        work_item_id = str(self.work_item.pk)

        response = self.client.delete(url)

        # Check HX-Trigger header exists
        self.assertIn('HX-Trigger', response.headers)

        # Parse the trigger data
        trigger_data = json.loads(response.headers['HX-Trigger'])

        # Verify trigger events
        self.assertIn('workItemDeleted', trigger_data)
        self.assertIn('showToast', trigger_data)
        self.assertIn('refreshCalendar', trigger_data)

        # Verify workItemDeleted details
        deleted_event = trigger_data['workItemDeleted']
        self.assertEqual(deleted_event['id'], work_item_id)
        self.assertEqual(deleted_event['title'], 'Test Activity')
        self.assertEqual(deleted_event['type'], 'Activity')

        # Verify toast message
        toast = trigger_data['showToast']
        self.assertIn('deleted successfully', toast['message'])
        self.assertEqual(toast['level'], 'success')

        # Verify refresh flag
        self.assertTrue(trigger_data['refreshCalendar'])

    def test_delete_nonexistent_work_item_returns_404(self):
        """Test deleting non-existent work item returns 404."""
        url = reverse('common:work_item_delete', kwargs={'pk': '00000000-0000-0000-0000-000000000000'})

        response = self.client.delete(url)

        self.assertEqual(response.status_code, 404)

    def test_unauthenticated_user_cannot_delete(self):
        """Test unauthenticated users cannot delete work items."""
        self.client.logout()

        url = reverse('common:work_item_delete', kwargs={'pk': self.work_item.pk})
        response = self.client.delete(url)

        # Should redirect to login
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

        # Work item should still exist
        self.assertTrue(WorkItem.objects.filter(pk=self.work_item.pk).exists())

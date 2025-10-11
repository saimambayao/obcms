import os
import tempfile
from io import BytesIO
from unittest.mock import MagicMock, patch

import pytest
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, TransactionTestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from ..models import Document, DocumentAccess, DocumentCategory, DocumentComment

User = get_user_model()

pytestmark = pytest.mark.integration


class DocumentModelTest(TestCase):
    """Test Document model functionality."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.category = DocumentCategory.objects.create(
            name="Test Category", description="Test category description"
        )

    def test_document_creation(self):
        """Test basic document creation."""
        # Create a simple test file
        test_file = SimpleUploadedFile(
            "test.txt", b"file_content", content_type="text/plain"
        )

        document = Document.objects.create(
            title="Test Document",
            description="Test description",
            file=test_file,
            category=self.category,
            uploaded_by=self.user,
            confidentiality_level="public",
            original_filename="test.txt",
        )

        self.assertEqual(document.title, "Test Document")
        self.assertEqual(document.uploaded_by, self.user)
        self.assertEqual(document.category, self.category)
        self.assertEqual(document.confidentiality_level, "public")
        self.assertEqual(document.download_count, 0)

    def test_document_str_representation(self):
        """Test document string representation."""
        document = Document.objects.create(
            title="Test Document",
            description="Test description",
            category=self.category,
            uploaded_by=self.user,
        )

        self.assertEqual(str(document), "Test Document")

    def test_document_file_size_calculation(self):
        """Test file size is calculated correctly."""
        test_content = b"x" * 1024  # 1KB
        test_file = SimpleUploadedFile(
            "test.txt", test_content, content_type="text/plain"
        )

        document = Document.objects.create(
            title="Test Document",
            file=test_file,
            category=self.category,
            uploaded_by=self.user,
        )

        self.assertEqual(document.file_size, 1024)


class DocumentCategoryModelTest(TestCase):
    """Test DocumentCategory model."""

    def test_category_creation(self):
        """Test category creation."""
        category = DocumentCategory.objects.create(
            name="Legal Documents", description="Legal and regulatory documents"
        )

        self.assertEqual(category.name, "Legal Documents")
        self.assertEqual(str(category), "Legal Documents")

    def test_category_ordering(self):
        """Test category ordering."""
        category1 = DocumentCategory.objects.create(name="Z Category")
        category2 = DocumentCategory.objects.create(name="A Category")

        categories = list(DocumentCategory.objects.all())
        self.assertEqual(categories[0], category2)  # A Category should come first


class DocumentAccessModelTest(TestCase):
    """Test DocumentAccess model."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.grantor = User.objects.create_user(
            username="grantor", email="grantor@example.com", password="testpass123"
        )
        self.category = DocumentCategory.objects.create(name="Test Category")
        self.document = Document.objects.create(
            title="Test Document", category=self.category, uploaded_by=self.grantor
        )

    def test_document_access_creation(self):
        """Test document access creation."""
        access = DocumentAccess.objects.create(
            document=self.document,
            user=self.user,
            access_type="view",
            granted_by=self.grantor,
            ip_address="127.0.0.1",
        )

        self.assertEqual(access.document, self.document)
        self.assertEqual(access.user, self.user)
        self.assertEqual(access.access_type, "view")
        self.assertTrue(access.is_active)


class DocumentAPITest(APITestCase):
    """Test Document API endpoints."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.staff_user = User.objects.create_user(
            username="staffuser",
            email="staff@example.com",
            password="testpass123",
            is_staff=True,
        )
        self.superuser = User.objects.create_superuser(
            username="admin", email="admin@example.com", password="admin123"
        )

        self.category = DocumentCategory.objects.create(
            name="Test Category", description="Test category"
        )

        self.client = APIClient()

    def test_unauthenticated_access_denied(self):
        """Test that unauthenticated users cannot access documents."""
        url = reverse("documents:document-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_document_list_authenticated(self):
        """Test authenticated user can list documents."""
        self.client.force_authenticate(user=self.user)

        # Create a public document
        Document.objects.create(
            title="Public Document",
            category=self.category,
            uploaded_by=self.user,
            confidentiality_level="public",
        )

        url = reverse("documents:document-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_document_access_filtering(self):
        """Test that users only see documents they have access to."""
        self.client.force_authenticate(user=self.user)

        # Create documents with different confidentiality levels
        public_doc = Document.objects.create(
            title="Public Document",
            category=self.category,
            uploaded_by=self.staff_user,
            confidentiality_level="public",
        )

        internal_doc = Document.objects.create(
            title="Internal Document",
            category=self.category,
            uploaded_by=self.staff_user,
            confidentiality_level="internal",
        )

        secret_doc = Document.objects.create(
            title="Secret Document",
            category=self.category,
            uploaded_by=self.staff_user,
            confidentiality_level="secret",
        )

        url = reverse("documents:document-list")
        response = self.client.get(url)

        # Regular user should only see public documents
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["title"], "Public Document")

    def test_staff_user_access(self):
        """Test that staff users can see internal documents."""
        self.client.force_authenticate(user=self.staff_user)

        # Create documents with different confidentiality levels
        public_doc = Document.objects.create(
            title="Public Document",
            category=self.category,
            uploaded_by=self.user,
            confidentiality_level="public",
        )

        internal_doc = Document.objects.create(
            title="Internal Document",
            category=self.category,
            uploaded_by=self.user,
            confidentiality_level="internal",
        )

        url = reverse("documents:document-list")
        response = self.client.get(url)

        # Staff user should see both public and internal documents
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)

    def test_superuser_access_all(self):
        """Test that superusers can see all documents."""
        self.client.force_authenticate(user=self.superuser)

        # Create documents with different confidentiality levels
        for level in ["public", "internal", "restricted", "confidential", "secret"]:
            Document.objects.create(
                title=f"{level.title()} Document",
                category=self.category,
                uploaded_by=self.user,
                confidentiality_level=level,
            )

        url = reverse("documents:document-list")
        response = self.client.get(url)

        # Superuser should see all documents
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 5)

    @patch("recommendations.documents.models.Document.file")
    def test_document_upload(self, mock_file):
        """Test document upload functionality."""
        self.client.force_authenticate(user=self.user)

        # Mock file upload
        test_file = SimpleUploadedFile(
            "test.pdf", b"fake pdf content", content_type="application/pdf"
        )

        data = {
            "title": "Uploaded Document",
            "description": "Test upload description",
            "file": test_file,
            "category": self.category.id,
            "confidentiality_level": "public",
            "tags": "test,upload",
        }

        url = reverse("documents:document-list")
        response = self.client.post(url, data, format="multipart")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["title"], "Uploaded Document")
        self.assertEqual(response.data["uploaded_by"], self.user.id)

    def test_document_download_access_control(self):
        """Test document download with access control."""
        self.client.force_authenticate(user=self.user)

        # Create a restricted document uploaded by another user
        other_user = User.objects.create_user(
            username="otheruser", email="other@example.com", password="testpass123"
        )

        document = Document.objects.create(
            title="Restricted Document",
            category=self.category,
            uploaded_by=other_user,
            confidentiality_level="restricted",
        )

        url = reverse("documents:document-download", kwargs={"pk": document.id})
        response = self.client.get(url)

        # Should be forbidden for user without access
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_grant_access_functionality(self):
        """Test granting access to documents."""
        self.client.force_authenticate(user=self.user)

        # Create a document
        document = Document.objects.create(
            title="Test Document",
            category=self.category,
            uploaded_by=self.user,
            confidentiality_level="internal",
        )

        # Grant access to another user
        other_user = User.objects.create_user(
            username="otheruser", email="other@example.com", password="testpass123"
        )

        url = reverse("documents:document-grant-access", kwargs={"pk": document.id})
        data = {"user_ids": [other_user.id], "access_type": "view"}

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["granted_access"]), 1)

        # Verify access was granted
        access_exists = DocumentAccess.objects.filter(
            document=document, user=other_user, is_active=True
        ).exists()
        self.assertTrue(access_exists)

    def test_document_statistics(self):
        """Test document statistics endpoint."""
        self.client.force_authenticate(user=self.user)

        # Create some test documents
        for i in range(3):
            Document.objects.create(
                title=f"Document {i}",
                category=self.category,
                uploaded_by=self.user,
                confidentiality_level="public",
                download_count=i,
            )

        url = reverse("documents:document-statistics")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["total_documents"], 3)
        self.assertEqual(response.data["total_downloads"], 3)  # 0+1+2

    def test_document_search(self):
        """Test document search functionality."""
        self.client.force_authenticate(user=self.user)

        # Create documents with different titles
        Document.objects.create(
            title="Important Meeting Notes",
            category=self.category,
            uploaded_by=self.user,
            confidentiality_level="public",
        )

        Document.objects.create(
            title="Budget Report 2024",
            category=self.category,
            uploaded_by=self.user,
            confidentiality_level="public",
        )

        url = reverse("documents:document-list")
        response = self.client.get(url, {"search": "meeting"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(
            response.data["results"][0]["title"], "Important Meeting Notes"
        )


class DocumentCategoryAPITest(APITestCase):
    """Test DocumentCategory API endpoints."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_category_list(self):
        """Test listing document categories."""
        DocumentCategory.objects.create(
            name="Legal Documents", description="Legal category"
        )

        url = reverse("documents:category-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["name"], "Legal Documents")

    def test_category_documents(self):
        """Test getting documents in a category."""
        category = DocumentCategory.objects.create(
            name="Test Category", description="Test category"
        )

        # Create documents in this category
        for i in range(2):
            Document.objects.create(
                title=f"Document {i}",
                category=category,
                uploaded_by=self.user,
                confidentiality_level="public",
            )

        url = reverse("documents:category-documents", kwargs={"pk": category.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)


class DocumentCommentAPITest(APITestCase):
    """Test DocumentComment API endpoints."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.category = DocumentCategory.objects.create(name="Test Category")
        self.document = Document.objects.create(
            title="Test Document",
            category=self.category,
            uploaded_by=self.user,
            confidentiality_level="public",
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_create_comment(self):
        """Test creating a document comment."""
        data = {"document": self.document.id, "content": "This is a test comment"}

        url = reverse("documents:comment-list")
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["content"], "This is a test comment")
        self.assertEqual(response.data["author"], self.user.id)

    def test_list_comments(self):
        """Test listing comments for a document."""
        # Create some comments
        DocumentComment.objects.create(
            document=self.document, author=self.user, content="First comment"
        )
        DocumentComment.objects.create(
            document=self.document, author=self.user, content="Second comment"
        )

        url = reverse("documents:comment-list")
        response = self.client.get(url, {"document": self.document.id})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)

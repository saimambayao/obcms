# OBCMS Comprehensive Testing Strategy

**Status:** Implementation in progress
**Last Updated:** 2025-10-02
**Owner:** OOBC Development Team

## Executive Summary

This document defines the comprehensive testing strategy for the Other Bangsamoro Communities Management System (OBCMS). It maps modern testing practices to OBCMS-specific requirements, tools, and workflows, ensuring quality, security, and reliability for a government system serving Bangsamoro communities.

## Implementation Roadmap

1. **Stabilise the baseline** – keep the Django 4.2 LTS upgrade path validated by running the full suite (`../venv/bin/python -m pytest --ds=obc_management.settings`) on every feature branch and capturing coverage deltas.
2. **Codify fast feedback** – enforce `black`, `isort`, `flake8`, and the `-m unit` subset in pre-commit; wire the same linters into CI to prevent regressions slipping past local hooks.
3. **Harden service boundaries** – expand integration fixtures for Celery, file storage, and HTMX flows so shared behaviours are covered by contract tests instead of view-only assertions.
4. **Regressions & performance** – maintain the new calendar regression harness (`src/tests/test_calendar_performance.py`) alongside the targeted performance checkpoints in `src/tests/performance/` to guard caching, query counts, and ICS generation.
5. **Reporting & observability** – publish the latest `pytest`, `flake8`, and coverage artefacts with each release and log gaps in `docs/testing/TEST_RESULTS_REPORT.md` to inform upcoming sprints.
   - Pre-release dry runs follow the [Staging Rehearsal Checklist](staging_rehearsal_checklist.md) to validate migrations, smoke tests, Celery queues, and performance baselines.

## Stack Overview

**Backend:**
- Django 4.2 LTS + Django REST Framework
- PostgreSQL (production) / SQLite (development)
- Celery + Redis (background tasks)
- JWT authentication (SimpleJWT)

**Frontend:**
- Django Templates + HTMX
- Tailwind CSS
- Leaflet (maps)
- FullCalendar (scheduling)

**Infrastructure:**
- Docker + Docker Compose (Coolify-managed)
- Traefik/Nginx (reverse proxy via Coolify)
- Local Docker volumes (media files)
- PostgreSQL (production database)
- Redis (Celery broker)
- S3-compatible storage (optional - for database backups and horizontal scaling scenarios)

## Testing Taxonomy & OBCMS Implementation

### 1. Code & Build-Time Checks (Fast Feedback)

#### 1.1 Unit Tests

**Purpose:** Verify isolated behavior of functions, methods, and classes.

**OBCMS Implementation:**
- **Framework:** pytest + pytest-django
- **Location:** `src/<app>/tests/test_<module>.py`
- **Coverage Target:** 80%+ for business logic

**Key Areas to Test:**

1. **Model Methods & Properties**
   ```python
   # src/communities/tests/test_models.py
   def test_barangay_obc_full_name():
       """Test full_name property returns correct format."""
       barangay = BarangayOBCFactory(
           name="Test Barangay",
           municipality__name="Test Municipality"
       )
       assert barangay.full_name == "Test Barangay, Test Municipality"

   def test_demographic_completeness_score():
       """Test demographic data completeness calculation."""
       profile = BarangayOBCProfileFactory(
           population=1000,
           households=200,
           # ... other fields
       )
       score = profile.completeness_score()
       assert 0 <= score <= 100
   ```

2. **Utility Functions & Helpers**
   ```python
   # src/common/tests/test_utils.py
   def test_format_philippine_phone_number():
       """Test phone number formatting."""
       assert format_phone("+639171234567") == "+63 917 123 4567"
       assert format_phone("09171234567") == "+63 917 123 4567"

   def test_calculate_fiscal_year():
       """Test fiscal year calculation for BARMM."""
       date = datetime(2025, 7, 1)  # July 1, 2025
       assert calculate_fiscal_year(date) == 2026  # FY2026 starts July 1
   ```

3. **Serializer Validation**
   ```python
   # src/mana/tests/test_serializers.py
   def test_assessment_serializer_validates_date_range():
       """Test assessment date validation."""
       data = {
           'title': 'Test Assessment',
           'start_date': '2025-12-31',
           'end_date': '2025-01-01',  # Invalid: before start
       }
       serializer = AssessmentSerializer(data=data)
       assert not serializer.is_valid()
       assert 'end_date' in serializer.errors
   ```

4. **Business Logic & Calculations**
   ```python
   # src/mana/tests/test_prioritization.py
   def test_need_priority_score_calculation():
       """Test community need prioritization algorithm."""
       need = NeedFactory(
           community_votes=150,
           alignment_score=8.5,
           estimated_budget=500000,
           beneficiaries=1200
       )
       score = need.calculate_priority_score()
       assert isinstance(score, float)
       assert score > 0
   ```

**Command:**
```bash
# Run all unit tests
pytest src/ -v --cov=src --cov-report=html

# Run specific app
pytest src/mana/tests/ -v

# Run with markers
pytest -m unit -v
```

---

#### 1.1.5 pytest-django vs Django TestCase - Choosing Your Approach

**TL;DR:** Use pytest-django for most tests. Use Django TestCase for complex database transaction testing.

**pytest-django (Recommended for OBCMS):**

✅ **Advantages:**
- Less boilerplate - write tests as functions, not classes
- Better fixture system - reusable test setup with `@pytest.fixture`
- Clear assertion output - shows actual vs expected values
- Parametrized tests - test multiple scenarios easily
- Better IDE support - easier to run individual tests

```python
# pytest-django style (RECOMMENDED)
import pytest

@pytest.fixture
def region_ix():
    """Fixture for Region IX."""
    return RegionFactory(code='IX', name='Zamboanga Peninsula')

def test_barangay_creation(region_ix):
    """Test barangay creation (pytest style)."""
    barangay = BarangayOBC.objects.create(
        name="Test Barangay",
        region=region_ix
    )
    assert barangay.name == "Test Barangay"
    assert barangay.region.code == "IX"
```

**Django TestCase (Use When Needed):**

✅ **Use TestCase When:**
- Testing complex database transactions with `atomic()` blocks
- Need `TransactionTestCase` for transaction-specific behavior
- Testing Django's `TestCase.setUpTestData()` for performance
- Legacy codebase already uses TestCase extensively

```python
# Django TestCase style (when needed)
from django.test import TestCase

class BarangayTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        """Run once per test class (faster)."""
        cls.region = RegionFactory(code='IX')

    def test_barangay_creation(self):
        """Test barangay creation (TestCase style)."""
        barangay = BarangayOBC.objects.create(
            name="Test Barangay",
            region=self.region
        )
        self.assertEqual(barangay.name, "Test Barangay")
        self.assertEqual(barangay.region.code, "IX")
```

**Comparison Table:**

| Feature | pytest-django | Django TestCase |
|---------|---------------|-----------------|
| **Boilerplate** | Minimal ✅ | More verbose |
| **Fixtures** | Excellent ✅ | Manual setup |
| **Assertion output** | Detailed ✅ | Basic |
| **Parametrization** | Built-in ✅ | Manual |
| **Transaction testing** | Basic | Excellent ✅ |
| **Learning curve** | Gentle ✅ | Steeper (unittest) |
| **Community trend (2025)** | Growing ✅ | Stable |

**OBCMS Recommendation:**
- **Default to pytest-django** for new tests
- **Use TestCase only for:**
  - Transaction-specific tests (e.g., testing `atomic()` blocks)
  - When migrating legacy tests
  - When `setUpTestData()` performance optimization is critical

**Migration Path:**
```python
# If you have existing TestCase tests, you can mix both approaches:

# Old TestCase test (keep if working fine)
class LegacyBarangayTests(TestCase):
    def test_something(self):
        pass

# New pytest test (use for new tests)
def test_new_feature():
    pass
```

**pytest-django Setup:**
```bash
# Already installed in requirements/development.txt
pip install pytest-django

# pytest.ini configuration (already in project)
# See section 1.2 below for full configuration
```

---

#### 1.2 Static Analysis & Linting

**Tools:**
- **black** - Code formatting
- **isort** - Import sorting
- **flake8** - Style guide enforcement
- **mypy** - Type checking (future enhancement)

**Configuration:**

```toml
# pyproject.toml
[tool.black]
line-length = 100
target-version = ['py312']
exclude = '''
/(
    \.git
  | \.venv
  | venv
  | migrations
)/
'''

[tool.isort]
profile = "black"
line_length = 100
skip = ["migrations", ".venv", "venv"]

[tool.pytest.ini_options]
DJANGO_SETTINGS_MODULE = "obc_management.settings"
python_files = ["test_*.py", "*_test.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
markers = [
    "unit: Unit tests",
    "integration: Integration tests",
    "e2e: End-to-end tests",
    "api: API endpoint tests",
    "admin: Django admin interface tests",
    "htmx: HTMX interaction tests",
    "security: Security and access control tests (CRITICAL)",
    "regional_isolation: Regional data isolation tests (SECURITY CRITICAL)",
    "performance: Performance and load tests",
    "smoke: Smoke tests for critical paths",
    "slow: Slow-running tests",
]
```

**Pre-commit Hook:**
```bash
# .git/hooks/pre-commit
#!/bin/bash
source venv/bin/activate
black --check src/
isort --check-only src/
flake8 src/
pytest src/ -m unit --quiet
```

**Command:**
```bash
# Format code
black src/
isort src/

# Check without modifying
black --check src/
isort --check-only src/
flake8 src/
```

#### 1.3 Software Composition Analysis (SCA)

**Purpose:** Scan dependencies for known CVEs.

**Tools:**
- **pip-audit** - Python dependency vulnerability scanner
- **Safety** - Alternative dependency checker
- **OWASP Dependency-Check** - Universal scanner

**Implementation:**

```bash
# Install pip-audit
pip install pip-audit

# Scan dependencies
pip-audit --requirement requirements/base.txt
pip-audit --requirement requirements/development.txt

# CI Integration
pip-audit --requirement requirements/base.txt --format json --output audit-report.json
```

**Critical Dependencies to Monitor:**
- Django & DRF (security releases)
- Celery & Redis clients
- Pillow (image processing)
- psycopg2 (PostgreSQL driver)
- boto3 (AWS S3 client)

### 2. Service & Integration Layers

#### 2.1 Integration Tests

**Purpose:** Test interactions between components/services at boundaries.

**OBCMS Implementation:**

**Key Integration Points:**

1. **Database Transactions & Queries**
   ```python
   # src/communities/tests/test_integration.py
   @pytest.mark.integration
   def test_barangay_creation_with_profile():
       """Test creating barangay with profile in transaction."""
       with transaction.atomic():
           barangay = BarangayOBC.objects.create(
               name="Test Barangay",
               municipality=municipality,
               region=region
           )
           profile = BarangayOBCProfile.objects.create(
               barangay=barangay,
               population=1000,
               households=200
           )

       assert BarangayOBC.objects.filter(pk=barangay.pk).exists()
       assert profile.barangay_id == barangay.id
   ```

2. **Celery Task Execution**
   ```python
   # src/monitoring/tests/test_tasks.py
   @pytest.mark.integration
   def test_generate_monitoring_report_task(celery_worker):
       """Test Celery task generates report."""
       result = generate_monitoring_report.delay(report_id=1)
       assert result.get(timeout=10) == {'status': 'success'}

       report = MonitoringReport.objects.get(pk=1)
       assert report.status == 'completed'
       assert report.pdf_file is not None
   ```

3. **File Upload & Storage**
   ```python
   # src/common/tests/test_storage_integration.py
   @pytest.mark.integration
   def test_upload_document():
       """Test document upload to storage backend.

       Note: This test works with both filesystem (default for Coolify)
       and S3 storage (when USE_S3=1 for horizontal scaling).
       The test is storage-backend agnostic.
       """
       document = SimpleUploadedFile(
           "test.pdf",
           b"file_content",
           content_type="application/pdf"
       )

       uploaded = MonitoringDocument.objects.create(
           title="Test Document",
           file=document
       )

       # These assertions work regardless of storage backend
       assert uploaded.file.name.startswith('monitoring/')
       assert uploaded.file.storage.exists(uploaded.file.name)

   @pytest.mark.integration
   @pytest.mark.skipif(
       not os.getenv('USE_S3'),
       reason="S3 tests only run when USE_S3=1 (horizontal scaling deployment)"
   )
   def test_s3_signed_urls():
       """Test S3 signed URL generation for private files.

       Only runs when S3 is enabled (multi-server deployments).
       """
       from django.core.files.storage import default_storage

       # Upload test file
       path = default_storage.save('test/private.pdf', ContentFile(b'secret'))

       # Get signed URL
       url = default_storage.url(path)

       # Verify URL is signed (has query parameters)
       assert '?' in url
       assert 'Signature=' in url or 'X-Amz-Signature=' in url

       # Cleanup
       default_storage.delete(path)
   ```

4. **Multi-App Workflows**
   ```python
   # src/tests/integration/test_mana_to_monitoring.py
   @pytest.mark.integration
   def test_need_to_monitoring_entry_workflow():
       """Test creating monitoring entry from approved need."""
       need = Need.objects.create(
           title="Build Health Center",
           status='approved',
           estimated_budget=2000000
       )

       # Simulate workflow trigger
       entry = create_monitoring_entry_from_need(need)

       assert entry.title == need.title
       assert entry.budget == need.estimated_budget
       assert entry.source_need_id == need.id
   ```

5. **Project Management Portal HTMX Dashboards & Task Automation**
   ```python
   # src/project_central/tests/test_views.py
   class MyTasksWithProjectsViewTests(TestCase):
       def test_htmx_request_renders_partial(self):
           """Ensure the project task table responds via HTMX with filters."""
           response = self.client.get(
               reverse("project_central:my_tasks_with_projects"),
               {"status": StaffTask.STATUS_COMPLETED},
               HTTP_HX_REQUEST="true",
           )
           self.assertEqual(response.status_code, 200)
           self.assertTemplateUsed(response, "project_central/partials/project_task_table.html")
           self.assertIn("Compile field report", response.content.decode())

   class GenerateWorkflowTasksViewTests(TestCase):
       def test_generate_workflow_tasks_is_idempotent(self):
           """Idempotency filter prevents duplicate workflow task batches."""
           url = reverse("project_central:generate_workflow_tasks", args=[self.workflow.id])
           self.client.post(url)
           first_count = StaffTask.objects.filter(linked_workflow=self.workflow).count()
           self.client.post(url)
           self.assertEqual(
               StaffTask.objects.filter(linked_workflow=self.workflow).count(),
               first_count,
           )

   # src/common/tests/test_task_automation.py
   def test_create_tasks_with_resource_bookings():
       """Task templates provision CalendarResourceBooking records when specified."""
       tasks = create_tasks_from_template(
           "test_template",
           created_by=admin_user,
           resource_bookings={'default': [{'resource_id': resource.id, 'duration_hours': 3}]},
       )
       booking = CalendarResourceBooking.objects.get(object_id=tasks[0].pk)
       assert booking.resource == resource
   ```
   See [Task Template Automation Service Guide](../development/task_template_automation.md) for the full contract, idempotency guarantees, and booking spec reference.

6. **Celery Notification Batching**
   ```python
   # src/common/tests/test_tasks_notifications.py
   @patch("common.tasks.group")
   def test_batch_dispatches_group(mock_group):
       """Pending CalendarNotification records dispatch via Celery groups."""
       send_calendar_notifications_batch(batch_size=10)
       mock_group.assert_called_once()

   @patch("common.tasks.send_mail", side_effect=RuntimeError("Mail error"))
   def test_send_single_records_failure(mock_send_mail):
       """Retries mark CalendarNotification as failed with error message."""
       with pytest.raises(RuntimeError):
           send_single_calendar_notification(notification.id)
       notification.refresh_from_db()
       assert notification.status == CalendarNotification.STATUS_FAILED
   ```

**Command:**
```bash
pytest src/ -m integration -v --tb=short
```

#### 2.2 API Tests

**Purpose:** Validate REST API behavior, correctness, and error handling.

**OBCMS Implementation:**

**Test Cases:**

1. **Authentication & Authorization**
   ```python
   # src/api/tests/test_auth.py
   def test_api_requires_authentication(client):
       """Test API endpoints require authentication."""
       response = client.get('/api/v1/mana/assessments/')
       assert response.status_code == 401

   def test_jwt_token_authentication(api_client, user):
       """Test JWT token grants API access."""
       refresh = RefreshToken.for_user(user)
       api_client.credentials(
           HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}'
       )

       response = api_client.get('/api/v1/mana/assessments/')
       assert response.status_code == 200

   def test_regional_facilitator_cannot_access_other_regions(
       api_client, region_ix_facilitator
   ):
       """Test regional facilitators see only their region's data."""
       api_client.force_authenticate(user=region_ix_facilitator)

       # Create data in Region XII
       assessment_xii = AssessmentFactory(region__code='XII')

       response = api_client.get('/api/v1/mana/assessments/')
       data = response.json()

       # Should not include Region XII assessment
       ids = [item['id'] for item in data['results']]
       assert assessment_xii.id not in ids
   ```

2. **CRUD Operations**
   ```python
   # src/mana/tests/test_api.py
   def test_create_assessment_via_api(api_client, facilitator_user):
       """Test creating assessment via API."""
       api_client.force_authenticate(user=facilitator_user)

       data = {
           'title': 'FY2026 Region IX Assessment',
           'region': facilitator_user.region.id,
           'start_date': '2025-07-01',
           'end_date': '2025-09-30',
           'status': 'planning'
       }

       response = api_client.post('/api/v1/mana/assessments/', data)
       assert response.status_code == 201

       created = Assessment.objects.get(pk=response.json()['id'])
       assert created.title == data['title']
   ```

3. **Filtering & Pagination**
   ```python
   def test_api_pagination(api_client, authenticated_user):
       """Test API pagination works correctly."""
       # Create 25 barangays
       BarangayOBCFactory.create_batch(25)

       response = api_client.get('/api/v1/communities/barangays/')
       data = response.json()

       assert data['count'] == 25
       assert len(data['results']) == 20  # Default page size
       assert data['next'] is not None

   def test_api_filtering_by_region(api_client, authenticated_user):
       """Test API filtering by region."""
       response = api_client.get(
           '/api/v1/communities/barangays/',
           {'region': 'IX'}
       )
       data = response.json()

       for barangay in data['results']:
           assert barangay['region']['code'] == 'IX'
   ```

4. **Error Handling**
   ```python
   def test_api_validation_errors(api_client, facilitator_user):
       """Test API returns proper validation errors."""
       api_client.force_authenticate(user=facilitator_user)

       data = {
           'title': '',  # Required field empty
           'start_date': '2025-12-31',
           'end_date': '2025-01-01'  # Before start_date
       }

       response = api_client.post('/api/v1/mana/assessments/', data)
       assert response.status_code == 400

       errors = response.json()
       assert 'title' in errors
       assert 'end_date' in errors
   ```

**Postman/Newman Integration:**

```bash
# Export Postman collection
# Run with Newman in CI
newman run postman_collection.json \
  --environment postman_environment.json \
  --reporters cli,json \
  --reporter-json-export newman-report.json
```

### 3. UI/System Level

#### 3.1 End-to-End (E2E) Tests

**Purpose:** Exercise real user flows across the full stack.

**Recommended Tool:** **Playwright** (better Django integration than Cypress)

**Installation:**
```bash
pip install playwright pytest-playwright
playwright install chromium firefox webkit
```

**OBCMS E2E Scenarios:**

1. **User Authentication Flow**
   ```python
   # src/tests/e2e/test_auth_flows.py
   def test_facilitator_login_and_dashboard_access(page):
       """Test facilitator can log in and access dashboard."""
       page.goto("http://localhost:8000/login/")

       page.fill('input[name="username"]', 'facilitator_ix')
       page.fill('input[name="password"]', 'test_password')
       page.click('button[type="submit"]')

       # Should redirect to dashboard
       expect(page).to_have_url(re.compile(r'/dashboard/'))
       expect(page.locator('h1')).to_contain_text('Dashboard')
   ```

2. **MANA Assessment Workflow**
   ```python
   def test_create_and_conduct_assessment(page, facilitator_login):
       """Test complete assessment creation and data entry."""
       # Navigate to assessments
       page.goto("http://localhost:8000/mana/assessments/")
       page.click('text=Create New Assessment')

       # Fill assessment form
       page.fill('input[name="title"]', 'Test Assessment')
       page.select_option('select[name="region"]', 'IX')
       page.fill('input[name="start_date"]', '2025-07-01')
       page.fill('input[name="end_date"]', '2025-09-30')
       page.click('button[type="submit"]')

       # Verify created
       expect(page.locator('.alert-success')).to_be_visible()
       expect(page.locator('text=Test Assessment')).to_be_visible()

       # Navigate to assessment detail
       page.click('text=Test Assessment')

       # Add community need
       page.click('text=Add Need')
       page.fill('input[name="title"]', 'Build School')
       page.select_option('select[name="category"]', 'education')
       page.fill('textarea[name="description"]', 'Need new elementary school')
       page.fill('input[name="estimated_budget"]', '5000000')
       page.click('button:has-text("Save Need")')

       # Verify need added
       expect(page.locator('text=Build School')).to_be_visible()
   ```

3. **Coordination Event Scheduling**
   ```python
   def test_schedule_coordination_event(page, admin_login):
       """Test scheduling multi-stakeholder coordination event."""
       page.goto("http://localhost:8000/coordination/events/")
       page.click('text=Schedule Event')

       # Fill event form
       page.fill('input[name="title"]', 'Regional Coordination Meeting')
       page.select_option('select[name="event_type"]', 'coordination')
       page.fill('input[name="date"]', '2025-08-15')
       page.fill('input[name="time"]', '09:00')

       # Select stakeholders
       page.check('input[value="dswd"]')
       page.check('input[value="dilg"]')
       page.check('input[value="da"]')

       page.click('button:has-text("Schedule")')

       # Verify on calendar
       page.goto("http://localhost:8000/coordination/calendar/")
       expect(page.locator('text=Regional Coordination Meeting')).to_be_visible()
   ```

4. **Monitoring Entry HTMX Updates**
   ```python
   def test_monitoring_status_update_instant_ui(page, staff_login):
       """Test HTMX instant UI update on status change."""
       page.goto("http://localhost:8000/monitoring/entries/")

       # Get initial status
       entry_card = page.locator('[data-entry-id="1"]')
       initial_status = entry_card.locator('.status-badge').inner_text()

       # Change status via dropdown
       entry_card.locator('select[name="status"]').select_option('in_progress')

       # Wait for HTMX swap (should be instant, no page reload)
       page.wait_for_timeout(500)

       # Verify UI updated without reload
       new_status = entry_card.locator('.status-badge').inner_text()
       assert new_status == 'In Progress'
       assert new_status != initial_status

       # Verify no page reload occurred
       assert 'monitoring/entries' in page.url
   ```

**Run E2E Tests:**
```bash
# Run all E2E tests
pytest src/tests/e2e/ -v --headed  # With browser UI
pytest src/tests/e2e/ -v --browser firefox
pytest src/tests/e2e/ -v --slowmo 500  # Slow motion for debugging

# Run specific test
pytest src/tests/e2e/test_mana_workflows.py::test_create_and_conduct_assessment -v
```

#### 3.2 Cross-Browser Compatibility Tests

**Purpose:** Ensure functionality across browsers and devices.

**Strategy:**

1. **Primary Targets:**
   - Chrome/Edge (Chromium) - Latest 2 versions
   - Firefox - Latest 2 versions
   - Safari - Latest version (macOS/iOS)
   - Mobile Chrome/Safari (responsive design)

2. **Playwright Matrix:**
   ```python
   # pytest.ini
   [pytest]
   playwright_browser = ["chromium", "firefox", "webkit"]

   # Run across all browsers
   pytest src/tests/e2e/ --browser chromium --browser firefox --browser webkit
   ```

3. **Responsive Design Tests:**
   ```python
   def test_mobile_navigation(page):
       """Test mobile hamburger menu works."""
       page.set_viewport_size({"width": 375, "height": 667})  # iPhone SE
       page.goto("http://localhost:8000/")

       # Mobile menu should be hidden initially
       expect(page.locator('.mobile-menu')).not_to_be_visible()

       # Click hamburger
       page.click('.hamburger-icon')

       # Menu should appear
       expect(page.locator('.mobile-menu')).to_be_visible()
   ```

**BrowserStack Integration (Optional):**
```bash
# For real device testing
# Configure in .env
BROWSERSTACK_USERNAME=your_username
BROWSERSTACK_ACCESS_KEY=your_key

# Run tests on BrowserStack
pytest src/tests/e2e/ --browser-stack
```

#### 3.3 Visual Regression Tests

**Purpose:** Catch unintended visual changes.

**Tool:** **playwright-pytest** with screenshot comparison

**Implementation:**

```python
# src/tests/visual/test_ui_regression.py
def test_dashboard_visual_snapshot(page, facilitator_login):
    """Visual regression test for dashboard."""
    page.goto("http://localhost:8000/dashboard/")
    page.wait_for_load_state('networkidle')

    # Take screenshot and compare to baseline
    expect(page).to_have_screenshot('dashboard.png')

def test_barangay_card_visual(page, authenticated_user):
    """Visual regression test for barangay card component."""
    page.goto("http://localhost:8000/communities/barangays/")

    # Isolate component
    card = page.locator('.barangay-card').first
    expect(card).to_have_screenshot('barangay-card.png')
```

**Update Baselines:**
```bash
# Update baseline screenshots
pytest src/tests/visual/ --update-snapshots
```

#### 3.4 Accessibility Tests

**Purpose:** Ensure WCAG 2.1 AA compliance.

**Tools:**
- **axe-core** (via playwright-pytest)
- **Pa11y** (automated scanner)
- **Manual testing** with screen readers

**Automated Tests:**

```python
# src/tests/accessibility/test_a11y.py
from pytest_playwright.axe import Axe

def test_dashboard_accessibility(page, facilitator_login):
    """Test dashboard meets WCAG 2.1 AA."""
    page.goto("http://localhost:8000/dashboard/")

    axe = Axe(page)
    violations = axe.run()

    assert len(violations) == 0, f"Accessibility violations: {violations}"

def test_form_accessibility(page, staff_login):
    """Test form has proper labels and ARIA."""
    page.goto("http://localhost:8000/communities/barangays/create/")

    # Check all inputs have labels
    inputs = page.locator('input, select, textarea').all()
    for input_elem in inputs:
        # Should have associated label or aria-label
        label_id = input_elem.get_attribute('aria-labelledby')
        aria_label = input_elem.get_attribute('aria-label')
        input_id = input_elem.get_attribute('id')

        has_label = (
            label_id or
            aria_label or
            page.locator(f'label[for="{input_id}"]').count() > 0
        )

        assert has_label, f"Input missing label: {input_elem}"
```

**Pa11y CI Integration:**

```bash
# Install Pa11y
npm install -g pa11y-ci

# pa11y-config.json
{
  "defaults": {
    "standard": "WCAG2AA",
    "runners": ["axe", "htmlcs"],
    "chromeLaunchConfig": {
      "args": ["--no-sandbox"]
    }
  },
  "urls": [
    "http://localhost:8000/",
    "http://localhost:8000/login/",
    "http://localhost:8000/dashboard/",
    "http://localhost:8000/mana/assessments/",
    "http://localhost:8000/communities/barangays/"
  ]
}

# Run Pa11y
pa11y-ci --config pa11y-config.json
```

**Manual Testing Checklist:**
- [ ] Keyboard navigation (Tab, Enter, Escape)
- [ ] Screen reader testing (NVDA/JAWS/VoiceOver)
- [ ] Color contrast ratios (4.5:1 for text)
- [ ] Focus indicators visible
- [ ] Form error announcements
- [ ] Dynamic content updates announced
- [ ] Skip navigation links
- [ ] Heading hierarchy (h1 > h2 > h3)

#### 3.5 Usability Testing

**Purpose:** Validate with real users completing tasks.

**OBCMS Usability Test Scenarios:**

1. **Task: Create MANA Assessment**
   - Participant: New facilitator user
   - Success Metric: Complete task without help in < 5 minutes
   - Observe: Confusion points, error recovery

2. **Task: Find and Update Barangay Data**
   - Participant: Data entry clerk
   - Success Metric: Find barangay and update population in < 2 minutes
   - Observe: Search behavior, form usability

3. **Task: Schedule Coordination Meeting**
   - Participant: Regional coordinator
   - Success Metric: Schedule meeting with 3 stakeholders in < 3 minutes
   - Observe: Calendar interaction, stakeholder selection

**Documentation Template:**

```markdown
# Usability Test Session: [Date]

## Participant Profile
- Role: Regional Facilitator
- Experience: 6 months with OOBC
- Tech comfort: Moderate

## Task 1: Create MANA Assessment
- Time: 6:23 (target: 5:00)
- Success: Yes
- Issues:
  - Confused about "Fiscal Year" dropdown (expected calendar year)
  - Unclear where to add barangays to assessment
- Suggestions:
  - Add tooltip explaining fiscal year starts July 1
  - Make "Add Barangays" button more prominent

## Task 2: ...
```

### 4. Non-Functional & Security

#### 4.1 Performance Testing

**Purpose:** Validate system handles expected load.

**Approach:**
- **Pytest instrumentation (default)** – lightweight checks in `src/tests/performance/` and `src/tests/test_calendar_performance.py` track query counts, cache hits, and response payloads for the integrated calendar. The harness uses `CaptureQueriesContext` plus helper utilities to keep budgets explicit and fast (sub‑minute runtime).
- **Locust (optional stress testing)** – synthetic load for scaling exercises and pre-deployment rehearsals when we need concurrency modelling beyond pytest’s scope.

**Pytest Performance Guardrails:**

```python
# src/tests/performance/test_calendar_feed.py
@pytest.mark.django_db
@pytest.mark.performance
def test_calendar_feed_performance(perf_calendar_dataset, perf_http_runner):
    result = perf_http_runner.get(
        "common:oobc_calendar_feed_json",
        user=perf_calendar_dataset["user"],
        params={"modules": "coordination,staff"},
    )

    assert result.status_code == 200
    assert result.query_count <= 14
    assert result.duration_ms < 750


# src/tests/test_calendar_performance.py
class CalendarPerformanceRegressionTests(TestCase):
    def test_calendar_feed_json_reuses_cached_payload(self) -> None:
        create_event(self.user, title="JSON Feed Event")

        with CaptureQueriesContext(connection) as cold_queries:
            self.client.get(feed_url)

        with CaptureQueriesContext(connection) as warm_queries:
            self.client.get(feed_url)

        assert len(warm_queries) < len(cold_queries)
```

**Tool:** **Locust** (Python-based load testing)

**Installation:**
```bash
pip install locust
```

**Load Test Scenarios:**

1. **Baseline Load Test**
   ```python
   # src/tests/performance/locustfile.py
   from locust import HttpUser, task, between

   class OBCMSUser(HttpUser):
       wait_time = between(1, 3)

       def on_start(self):
           """Log in before starting tasks."""
           response = self.client.post("/login/", {
               "username": "test_facilitator",
               "password": "test_password"
           })
           self.csrftoken = response.cookies.get('csrftoken')

       @task(3)
       def view_dashboard(self):
           """View dashboard (high frequency)."""
           self.client.get("/dashboard/")

       @task(2)
       def browse_barangays(self):
           """Browse barangay list."""
           self.client.get("/communities/barangays/")

       @task(1)
       def view_assessments(self):
           """View MANA assessments."""
           self.client.get("/mana/assessments/")

       @task(1)
       def api_request(self):
           """API request with JWT."""
           headers = {"Authorization": f"Bearer {self.access_token}"}
           self.client.get("/api/v1/mana/assessments/", headers=headers)
   ```

2. **Stress Test**
   ```python
   class StressTestUser(HttpUser):
       """Stress test with heavy queries."""

       @task
       def complex_report_query(self):
           """Generate complex monitoring report."""
           self.client.post("/monitoring/reports/generate/", {
                "report_type": "comprehensive",
                "region": "IX",
                "date_from": "2025-01-01",
                "date_to": "2025-12-31"
            })
   ```

**Run Performance Tests:**
```bash
# Pytest guardrails (run with default Django settings module)
../venv/bin/python -m pytest --ds=obc_management.settings -m performance
```

```bash
# Run with Web UI
locust -f src/tests/performance/locustfile.py --host=http://localhost:8000

# Run headless
locust -f src/tests/performance/locustfile.py \
  --host=http://localhost:8000 \
  --users 100 \
  --spawn-rate 10 \
  --run-time 5m \
  --headless

# Export results
locust -f src/tests/performance/locustfile.py \
  --host=http://localhost:8000 \
  --users 100 \
  --spawn-rate 10 \
  --run-time 5m \
  --headless \
  --html performance-report.html
```

**Performance Benchmarks:**

| Metric | Target | Max Acceptable |
|--------|--------|----------------|
| Dashboard load | < 500ms | < 1s |
| API response (list) | < 200ms | < 500ms |
| API response (detail) | < 100ms | < 300ms |
| Page load (with data) | < 2s | < 3s |
| Concurrent users | 100 | 200 |
| Database queries per request | < 20 | < 50 |

3. **Database Query Performance**
   ```python
   # src/tests/performance/test_booking_conflicts.py
   @pytest.mark.django_db
   @pytest.mark.performance
   def test_booking_conflict_validation(perf_booking_dataset):
       resource = perf_booking_dataset["resource"]
       base_start = perf_booking_dataset["base_start"]
       overlap_start = base_start + timedelta(minutes=45)
       overlap_end = overlap_start + timedelta(hours=2)

       def conflict_lookup() -> bool:
           return CalendarResourceBooking.objects.filter(
               resource=resource,
               start_datetime__lt=overlap_end,
               end_datetime__gt=overlap_start,
               status__in=[
                   CalendarResourceBooking.STATUS_PENDING,
                   CalendarResourceBooking.STATUS_APPROVED,
               ],
           ).exists()

       result = measure_callable(conflict_lookup)

       assert result.value is True
       assert result.query_count <= 2
       assert result.duration_ms < 120
   ```

##### 4.1.1 Calendar Regression Benchmarks

- **Tooling:** pytest + Django test client instrumentation (`tests/perf_utils/`).
- **Entry Point:** `scripts/run_calendar_perf.sh` (wraps `pytest -m performance`).
- **Primary Scenarios:** consolidated calendar feed, resource booking conflict lookup (see `docs/testing/calendar_performance_plan.md`).
- **Execution Modes:**
  - Local smoke: `scripts/run_calendar_perf.sh -k calendar_feed`
  - Nightly CI: schedule the same script and persist `var/perf_reports/` artifacts
- **Thresholds:** Enforced directly in the tests; updates require sign-off from the calendar module owners.
- **Maintenance:** QA maintains the shared utilities and CI wiring; the calendar team owns dataset/threshold changes; quarterly reviews keep scenarios aligned with production patterns.
- **Recommended environment:** run on a workstation with ≥4 CPU cores and 16 GB RAM; close CPU-bound background tasks before capturing metrics.
- **JSON output:** the run script writes metrics to `var/perf_reports/*.json`; each entry includes scenario name, dataset label, duration (ms), and query count (plus payload size for feed/HTMX/ICS).

#### 4.2 Security Testing

##### 4.2.1 SAST (Static Application Security Testing)

**Tool:** **Bandit** (Python security linter)

```bash
# Install
pip install bandit

# Run scan
bandit -r src/ -f json -o bandit-report.json

# Exclude test files
bandit -r src/ -x src/*/tests/

# CI integration
bandit -r src/ -ll  # Only medium/high severity
```

**Common Issues to Catch:**
- Hardcoded passwords/secrets
- SQL injection risks
- Command injection
- Insecure cryptography
- Debug mode in production

##### 4.2.2 DAST (Dynamic Application Security Testing)

**Tool:** **OWASP ZAP** (Zed Attack Proxy)

```bash
# Run ZAP baseline scan
docker run -t owasp/zap2docker-stable zap-baseline.py \
  -t http://localhost:8000 \
  -r zap-report.html

# Full scan (takes longer)
docker run -t owasp/zap2docker-stable zap-full-scan.py \
  -t http://localhost:8000 \
  -r zap-full-report.html
```

**ZAP Configuration:**
- Authenticate before scanning (provide test credentials)
- Exclude admin endpoints from aggressive scans
- Focus on API endpoints and forms

##### 4.2.3 OWASP Top 10 Testing

**Manual Security Test Checklist:**

1. **A01:2021 - Broken Access Control**
   ```python
   # src/tests/security/test_access_control.py
   def test_facilitator_cannot_access_admin_panel(client, facilitator_user):
       """Test non-admin cannot access admin."""
       client.force_login(facilitator_user)
       response = client.get('/admin/')
       assert response.status_code == 302  # Redirect to login

   def test_facilitator_cannot_edit_other_region_data(
       api_client, region_ix_facilitator
   ):
       """Test facilitators isolated to their region."""
       api_client.force_authenticate(user=region_ix_facilitator)

       # Try to update Region XII assessment
       assessment_xii = AssessmentFactory(region__code='XII')
       response = api_client.patch(
           f'/api/v1/mana/assessments/{assessment_xii.id}/',
           {'title': 'Hacked'}
       )

       assert response.status_code == 404  # Should not be visible
   ```

2. **A02:2021 - Cryptographic Failures**
   ```python
   def test_passwords_are_hashed(db):
       """Test passwords never stored in plaintext."""
       user = User.objects.create_user(
           username='test',
           password='plaintext123'
       )

       # Password should be hashed with pbkdf2_sha256
       assert user.password.startswith('pbkdf2_sha256$')
       assert 'plaintext123' not in user.password

   def test_session_cookies_secure(client, live_server):
       """Test session cookies have secure flags."""
       with override_settings(
           SESSION_COOKIE_SECURE=True,
           SESSION_COOKIE_HTTPONLY=True,
           SESSION_COOKIE_SAMESITE='Lax'
       ):
           response = client.get('/')
           cookie = response.cookies.get('sessionid')

           assert cookie.get('secure') is True
           assert cookie.get('httponly') is True
   ```

3. **A03:2021 - Injection**
   ```python
   def test_sql_injection_protection(client, admin_user):
       """Test SQL injection attempts are blocked."""
       client.force_login(admin_user)

       # Attempt SQL injection in search
       malicious_input = "'; DROP TABLE communities_barangayobc; --"
       response = client.get(
           '/communities/barangays/',
           {'search': malicious_input}
       )

       # Should not execute SQL, should return safe results
       assert response.status_code == 200
       assert BarangayOBC.objects.count() > 0  # Table still exists
   ```

4. **A05:2021 - Security Misconfiguration**
   ```python
   def test_debug_mode_disabled_in_production():
       """Test DEBUG is False in production settings."""
       from obc_management.settings.production import DEBUG
       assert DEBUG is False

   def test_sensitive_settings_not_exposed(client):
       """Test sensitive settings not exposed in error pages."""
       with override_settings(DEBUG=False):
           response = client.get('/nonexistent-page/')
           assert response.status_code == 404

           # Should not expose settings
           assert 'SECRET_KEY' not in response.content.decode()
           assert 'DATABASE' not in response.content.decode()
   ```

5. **A07:2021 - Identification and Authentication Failures**
   ```python
   def test_account_lockout_after_failed_attempts(client):
       """Test account locks after 5 failed login attempts."""
       for i in range(6):
           response = client.post('/login/', {
               'username': 'test_user',
               'password': 'wrong_password'
           })

       # 6th attempt should be blocked
       assert response.status_code == 429  # Too Many Requests
       assert 'Account locked' in response.content.decode()

   def test_password_complexity_requirements():
       """Test weak passwords are rejected."""
       with pytest.raises(ValidationError):
           user = User(username='test')
           user.set_password('12345')  # Too weak
           user.full_clean()
   ```

##### 4.2.4 Secrets & Configuration Security

**Tool:** **detect-secrets**

```bash
# Install
pip install detect-secrets

# Initialize baseline
detect-secrets scan > .secrets.baseline

# Audit results
detect-secrets audit .secrets.baseline

# CI integration
detect-secrets scan --baseline .secrets.baseline
```

**Pre-commit Hook:**
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/Yelp/detect-secrets
    rev: v1.4.0
    hooks:
      - id: detect-secrets
        args: ['--baseline', '.secrets.baseline']
```

**What to Scan For:**
- AWS keys
- Database passwords
- JWT secrets
- API tokens
- Private keys

### 5. Release & Deployment Gates

#### 5.1 Smoke Tests

**Purpose:** Quick critical-path checks after deployment.

**OBCMS Smoke Test Suite:**

```python
# src/tests/smoke/test_smoke.py
import pytest

@pytest.mark.smoke
class TestSmokeSuite:
    """Critical path tests that must pass before release."""

    def test_homepage_loads(self, client):
        """Test homepage accessible."""
        response = client.get('/')
        assert response.status_code == 200

    def test_login_page_loads(self, client):
        """Test login page accessible."""
        response = client.get('/login/')
        assert response.status_code == 200

    def test_admin_login_works(self, client, admin_user):
        """Test admin can log in."""
        response = client.post('/login/', {
            'username': admin_user.username,
            'password': 'admin_password'
        }, follow=True)
        assert response.status_code == 200
        assert admin_user.username in response.content.decode()

    def test_api_health_check(self, client):
        """Test API health endpoint."""
        response = client.get('/api/health/')
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'ok'
        assert data['database'] == 'connected'
        assert data['redis'] == 'connected'

    def test_database_connection(self, db):
        """Test database accessible."""
        from django.db import connection
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        assert cursor.fetchone()[0] == 1

    def test_celery_broker_connection(self):
        """Test Celery/Redis connection."""
        from celery import current_app
        inspector = current_app.control.inspect()
        assert inspector.ping() is not None

    def test_static_files_accessible(self, client):
        """Test static files served correctly."""
        response = client.get('/static/common/css/styles.css')
        assert response.status_code == 200

    def test_media_files_accessible(self, client):
        """Test media files served correctly."""
        # Upload test file
        from django.core.files.uploadedfile import SimpleUploadedFile
        test_file = SimpleUploadedFile("test.txt", b"content")
        # ... upload logic
        # Verify accessible
```

**Run Smoke Tests:**
```bash
# After deployment
pytest src/tests/smoke/ -v --tb=line

# In CI pipeline
pytest -m smoke -v --maxfail=1  # Stop on first failure
```

#### 5.2 Regression Suite

**Purpose:** Catch change-related breakage.

**Strategy:**
- Tag all tests with pytest markers
- Run targeted regression based on changed code

```python
# pytest.ini
[pytest]
markers =
    smoke: Critical smoke tests
    regression: Regression test suite
    unit: Unit tests
    integration: Integration tests
    e2e: End-to-end tests
    api: API tests
    security: Security tests
    performance: Performance tests
```

**Run Regression:**
```bash
# Full regression suite
pytest -m "smoke or regression" -v

# Targeted regression (only affected areas)
# If models.py changed, run model tests
pytest src/communities/tests/test_models.py -v

# If API changed, run API tests
pytest -m api -v
```

#### 5.3 Database Migration Tests

**Purpose:** Verify migrations apply and rollback safely.

**Test Strategy:**

1. **Forward Migration Test**
   ```python
   # src/tests/migrations/test_forward_migrations.py
   def test_all_migrations_apply_cleanly():
       """Test all migrations apply without errors."""
       from django.core.management import call_command
       call_command('migrate', verbosity=0)

   def test_migration_0020_adds_fields():
       """Test migration 0020 adds expected fields."""
       from mana.models import Need

       # Check fields exist
       assert hasattr(Need, 'community_votes')
       assert hasattr(Need, 'budget_inclusion_date')
   ```

2. **Backward Migration Test**
   ```python
   def test_migration_rollback():
       """Test migration can roll back safely."""
       from django.core.management import call_command

       # Rollback one migration
       call_command('migrate', 'mana', '0019', verbosity=0)

       # Verify old state
       from mana.models import Need
       assert not hasattr(Need, 'community_votes')

       # Re-apply
       call_command('migrate', 'mana', '0020', verbosity=0)
   ```

3. **Data Migration Test**
   ```python
   def test_data_migration_preserves_data():
       """Test data migration doesn't lose data."""
       # Create test data before migration
       # ... populate database

       # Apply migration
       call_command('migrate', verbosity=0)

       # Verify data still exists and transformed correctly
       assert Model.objects.count() == expected_count
   ```

**Run Migration Tests:**
```bash
# Test migrations
pytest src/tests/migrations/ -v

# Test on fresh database
rm src/db.sqlite3
pytest src/tests/migrations/ -v
```

#### 5.4 Operational Acceptance Testing (OAT)

**Purpose:** Verify system operability before production release.

**OBCMS OAT Checklist:**

**1. Backup & Restore**
```bash
# Test database backup
cd scripts
./db_backup.sh

# Verify backup created
ls -lh ../backups/db_backup_*.sql.gz

# Test restore (on test environment)
./db_restore.sh ../backups/db_backup_latest.sql.gz
```

**2. Monitoring & Alerting**
- [ ] Sentry error tracking configured
- [ ] Sentry test error sent and received
- [ ] Uptime monitoring active (UptimeRobot/Pingdom)
- [ ] Email alerts configured for critical errors
- [ ] Django admin log monitoring enabled

**3. Log Accessibility**
```bash
# Verify logs are written
tail -f src/logs/django.log
tail -f src/logs/celery.log

# Test log rotation
logrotate -f /etc/logrotate.d/obcms
```

**4. Background Jobs & Schedulers**
```python
# src/tests/oat/test_background_jobs.py
def test_celery_worker_running():
    """Test Celery worker is active."""
    from celery import current_app
    inspector = current_app.control.inspect()
    active = inspector.active()
    assert active is not None and len(active) > 0

def test_scheduled_tasks_configured():
    """Test periodic tasks are scheduled."""
    from django_celery_beat.models import PeriodicTask

    # Check expected tasks exist
    assert PeriodicTask.objects.filter(
        name='Generate Daily Monitoring Report'
    ).exists()
```

**5. Permissions & Role-Based Access**
```python
def test_all_user_roles_have_permissions():
    """Test all roles have appropriate permissions."""
    from django.contrib.auth.models import Group

    required_groups = [
        'Regional Facilitator',
        'Provincial Coordinator',
        'Data Entry Clerk',
        'OOBC Administrator'
    ]

    for group_name in required_groups:
        group = Group.objects.get(name=group_name)
        assert group.permissions.count() > 0

def test_sensitive_permissions_restricted():
    """Test dangerous permissions not given to low-level users."""
    facilitator_group = Group.objects.get(name='Regional Facilitator')

    # Facilitators should NOT be able to delete users
    delete_user_perm = Permission.objects.get(
        codename='delete_user',
        content_type__app_label='auth'
    )

    assert delete_user_perm not in facilitator_group.permissions.all()
```

**6. Email Sending**
```python
def test_email_configuration():
    """Test email sending works."""
    from django.core.mail import send_mail

    send_mail(
        'Test Email',
        'This is a test email from OBCMS OAT.',
        'noreply@oobc.gov.ph',
        ['test@example.com'],
        fail_silently=False,
    )

    # Check email backend logs or test mailbox
```

#### 5.5 Feature Flag Validation

**Tool:** **django-waffle** (feature flagging)

**Installation:**
```bash
pip install django-waffle
```

**Usage:**

```python
# settings.py
INSTALLED_APPS += ['waffle']

# Enable feature for specific users/groups
from waffle.models import Flag
flag = Flag.objects.create(
    name='new_dashboard_layout',
    everyone=False
)

# In views
from waffle import flag_is_active

def dashboard(request):
    if flag_is_active(request, 'new_dashboard_layout'):
        return render(request, 'dashboard_new.html')
    else:
        return render(request, 'dashboard_old.html')
```

**Test Feature Flags:**
```python
def test_feature_flag_on_behavior(client, admin_user):
    """Test new feature when flag is ON."""
    Flag.objects.create(name='new_dashboard_layout', everyone=True)

    client.force_login(admin_user)
    response = client.get('/dashboard/')

    assert 'New Dashboard' in response.content.decode()

def test_feature_flag_off_behavior(client, admin_user):
    """Test old behavior when flag is OFF."""
    Flag.objects.create(name='new_dashboard_layout', everyone=False)

    client.force_login(admin_user)
    response = client.get('/dashboard/')

    assert 'Old Dashboard' in response.content.decode()
```

#### 5.6 Blue-Green & Canary Deployments

**Blue-Green Strategy:**

1. **Deploy to "green" environment**
2. **Run smoke tests on green**
3. **If passing, switch traffic to green**
4. **Keep blue as rollback target**

**Canary Strategy:**

1. **Deploy new version to canary servers**
2. **Route 5% of traffic to canary**
3. **Monitor error rates, latency, SLIs**
4. **If healthy, gradually increase to 100%**

**OBCMS Deployment Script:**
```bash
# scripts/deploy_canary.sh
#!/bin/bash
set -e

# Deploy canary
docker-compose -f docker-compose.canary.yml up -d

# Wait for startup
sleep 10

# Run smoke tests against canary
pytest src/tests/smoke/ --base-url=http://canary.obcms.local

# Monitor for 5 minutes
echo "Monitoring canary for 5 minutes..."
sleep 300

# Check error rates
ERROR_RATE=$(curl -s http://canary.obcms.local/api/metrics/ | jq '.error_rate')

if (( $(echo "$ERROR_RATE < 0.01" | bc -l) )); then
    echo "Canary healthy, promoting to production"
    # Switch traffic
    ./switch_to_canary.sh
else
    echo "Canary unhealthy, rolling back"
    docker-compose -f docker-compose.canary.yml down
    exit 1
fi
```

### 6. In-Production Safety Nets

#### 6.1 Synthetic Monitoring

**Purpose:** Continuously test critical journeys in production.

**Tool:** **Playwright** scheduled tests

**Implementation:**

1. **Synthetic Tests**
   ```python
   # src/tests/synthetic/test_critical_paths.py
   def test_synthetic_login_flow(page):
       """Synthetic test: User can log in."""
       page.goto(PRODUCTION_URL)
       page.click('text=Login')

       page.fill('input[name="username"]', SYNTHETIC_USER)
       page.fill('input[name="password"]', SYNTHETIC_PASSWORD)
       page.click('button[type="submit"]')

       # Should reach dashboard
       expect(page).to_have_url(re.compile(r'/dashboard/'))
       expect(page.locator('h1')).to_contain_text('Dashboard')

   def test_synthetic_api_health(api_client):
       """Synthetic test: API is responsive."""
       response = api_client.get(f'{PRODUCTION_URL}/api/health/')
       assert response.status_code == 200
       assert response.json()['status'] == 'ok'
   ```

2. **Scheduled Execution**
   ```bash
   # crontab -e
   # Run every 15 minutes
   */15 * * * * cd /path/to/obcms && pytest src/tests/synthetic/ --base-url=https://obcms.oobc.gov.ph >> /var/log/synthetic-tests.log 2>&1
   ```

3. **Alert on Failure**
   ```python
   # scripts/run_synthetic_tests.py
   import subprocess
   import requests

   result = subprocess.run(
       ['pytest', 'src/tests/synthetic/', '-v'],
       capture_output=True
   )

   if result.returncode != 0:
       # Send alert
       requests.post(
           'https://hooks.slack.com/services/...',
           json={
               'text': f'❌ Synthetic tests failed!\n{result.stdout.decode()}'
           }
       )
   ```

**Monitoring Service Alternatives:**
- **Checkly** - Playwright-based monitoring service
- **Datadog Synthetics** - Comprehensive synthetic monitoring
- **New Relic Synthetics** - Scripted browser tests

#### 6.2 Chaos Engineering

**Purpose:** Build confidence in failure handling.

**Tool:** **Chaos Toolkit** or manual experiments

**Chaos Experiments for OBCMS:**

1. **Database Connection Loss**
   ```bash
   # Simulate database outage
   docker-compose stop db

   # Expected behavior:
   # - User sees error page (not crash)
   # - Celery tasks retry automatically
   # - Connection pool recovers when DB returns

   # Restore
   docker-compose start db
   ```

2. **Redis/Celery Failure**
   ```bash
   # Stop Redis
   docker-compose stop redis

   # Expected behavior:
   # - Web app still serves pages (degrades gracefully)
   # - Background tasks queue but don't execute
   # - No user-facing errors

   # Restore
   docker-compose start redis
   ```

3. **High Memory Pressure**
   ```bash
   # Limit container memory
   docker update --memory="256m" obcms_web

   # Generate load
   locust -f src/tests/performance/locustfile.py --users 200

   # Expected behavior:
   # - Application remains responsive
   # - Gunicorn workers restart if OOM
   # - No data corruption

   # Restore
   docker update --memory="2g" obcms_web
   ```

4. **Network Latency**
   ```bash
   # Simulate 500ms latency
   tc qdisc add dev eth0 root netem delay 500ms

   # Test user experience
   # Expected: Longer load times but no errors

   # Remove latency
   tc qdisc del dev eth0 root netem
   ```

**Chaos Engineering Checklist:**
- [ ] Test in staging environment first
- [ ] Have rollback plan ready
- [ ] Monitor during experiments
- [ ] Document unexpected behaviors
- [ ] Improve resilience based on findings

## Test Directory Structure

```
obcms/
├── src/
│   ├── <app>/
│   │   ├── tests/
│   │   │   ├── __init__.py
│   │   │   ├── factories.py          # Factory Boy factories
│   │   │   ├── conftest.py           # Pytest fixtures
│   │   │   ├── test_models.py        # Unit tests for models
│   │   │   ├── test_views.py         # Unit tests for views
│   │   │   ├── test_serializers.py   # Unit tests for serializers
│   │   │   ├── test_api.py           # API integration tests
│   │   │   └── test_forms.py         # Form validation tests
│   │   └── ...
│   │
│   └── tests/                         # Project-level tests
│       ├── integration/               # Cross-app integration tests
│       │   ├── test_mana_coordination.py
│       │   └── test_policy_monitoring.py
│       │
│       ├── e2e/                       # End-to-end tests
│       │   ├── conftest.py
│       │   ├── test_facilitator_workflows.py
│       │   ├── test_admin_workflows.py
│       │   └── test_public_pages.py
│       │
│       ├── visual/                    # Visual regression tests
│       │   └── test_ui_regression.py
│       │
│       ├── accessibility/             # Accessibility tests
│       │   └── test_a11y.py
│       │
│       ├── security/                  # Security tests
│       │   ├── test_access_control.py
│       │   ├── test_authentication.py
│       │   └── test_owasp_top10.py
│       │
│       ├── performance/               # Performance tests
│       │   ├── conftest.py
│       │   ├── test_booking_conflicts.py
│       │   └── test_calendar_feed.py
│       │
│       ├── perf_utils/                # Shared performance helpers
│       │   ├── __init__.py
│       │   ├── factories.py
│       │   └── runner.py
│       │
│       ├── test_calendar_integration.py
│       ├── test_calendar_performance.py
│       └── test_calendar_system.py
│
├── docs/testing/                      # Test documentation
│   ├── README.md
│   ├── TESTING_STRATEGY.md            # This document
│   ├── test-plan-template.md
│   └── reports/
│
└── scripts/
    ├── run_tests.sh                   # Test runner script
    └── run_synthetic_tests.py         # Synthetic test runner
```

## Test Data Management

### Factory Boy Setup

```bash
pip install factory_boy faker
```

**Factory Examples:**

```python
# src/communities/tests/factories.py
import factory
from factory.django import DjangoModelFactory
from faker import Faker
from communities.models import Region, Province, Municipality, BarangayOBC

fake = Faker()

class RegionFactory(DjangoModelFactory):
    class Meta:
        model = Region
        django_get_or_create = ('code',)

    code = 'IX'
    name = 'Zamboanga Peninsula'

class ProvinceFactory(DjangoModelFactory):
    class Meta:
        model = Province

    name = factory.Faker('province', locale='fil_PH')
    region = factory.SubFactory(RegionFactory)

class MunicipalityFactory(DjangoModelFactory):
    class Meta:
        model = Municipality

    name = factory.Faker('city', locale='fil_PH')
    province = factory.SubFactory(ProvinceFactory)

class BarangayOBCFactory(DjangoModelFactory):
    class Meta:
        model = BarangayOBC

    name = factory.Faker('barangay', locale='fil_PH')
    municipality = factory.SubFactory(MunicipalityFactory)
    region = factory.LazyAttribute(lambda o: o.municipality.province.region)

    # Demographics
    population = factory.Faker('random_int', min=100, max=5000)
    households = factory.LazyAttribute(lambda o: o.population // 5)
    bangsamoro_population = factory.LazyAttribute(
        lambda o: fake.random_int(min=o.population // 2, max=o.population)
    )
```

**Using Factories:**

```python
# In tests
def test_barangay_demographics():
    barangay = BarangayOBCFactory(
        population=1000,
        bangsamoro_population=800
    )

    assert barangay.bangsamoro_percentage == 80.0

def test_create_multiple_barangays():
    # Create 10 barangays at once
    barangays = BarangayOBCFactory.create_batch(10)
    assert len(barangays) == 10
```

### Fixtures & Test Data Commands

```python
# src/communities/management/commands/setup_test_data.py
from django.core.management.base import BaseCommand
from communities.tests.factories import (
    RegionFactory, ProvinceFactory, BarangayOBCFactory
)

class Command(BaseCommand):
    help = 'Create test data for development and testing'

    def handle(self, *args, **options):
        # Create regions
        region_ix = RegionFactory(code='IX', name='Zamboanga Peninsula')
        region_xii = RegionFactory(code='XII', name='SOCCSKSARGEN')

        # Create provinces
        zamboanga_del_sur = ProvinceFactory(
            name='Zamboanga del Sur',
            region=region_ix
        )

        # Create 50 barangays
        BarangayOBCFactory.create_batch(50, region=region_ix)

        self.stdout.write(
            self.style.SUCCESS('Successfully created test data')
        )
```

**Run:**
```bash
cd src
./manage.py setup_test_data
```

## CI/CD Pipeline Integration

### GitHub Actions Workflow

```yaml
# .github/workflows/test.yml
name: Test Suite

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements/development.txt

      - name: Run Black
        run: black --check src/

      - name: Run isort
        run: isort --check-only src/

      - name: Run flake8
        run: flake8 src/ --count --show-source --statistics

      - name: Run Bandit security scan
        run: bandit -r src/ -ll

  test:
    runs-on: ubuntu-latest
    needs: lint

    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: obcms_test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432

      redis:
        image: redis:7
        ports:
          - 6379:6379

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements/development.txt

      - name: Run migrations
        env:
          DATABASE_URL: postgresql://postgres:postgres@localhost/obcms_test
          REDIS_URL: redis://localhost:6379/0
        run: |
          cd src
          python manage.py migrate --settings=obc_management.settings.testing

      - name: Run unit tests
        env:
          DATABASE_URL: postgresql://postgres:postgres@localhost/obcms_test
          REDIS_URL: redis://localhost:6379/0
        run: |
          pytest src/ -m "unit or integration" -v \
            --cov=src \
            --cov-report=xml \
            --cov-report=html

      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage.xml

  security-scan:
    runs-on: ubuntu-latest
    needs: test
    steps:
      - uses: actions/checkout@v3

      - name: Run pip-audit
        run: |
          pip install pip-audit
          pip-audit --requirement requirements/base.txt

      - name: Run detect-secrets
        run: |
          pip install detect-secrets
          detect-secrets scan --baseline .secrets.baseline

  e2e-tests:
    runs-on: ubuntu-latest
    needs: test
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements/development.txt
          playwright install chromium

      - name: Start application
        run: |
          cd src
          python manage.py migrate
          python manage.py runserver &
          sleep 5

      - name: Run E2E tests
        run: |
          pytest src/tests/e2e/ -v --browser chromium

      - name: Upload test artifacts
        if: failure()
        uses: actions/upload-artifact@v3
        with:
          name: playwright-screenshots
          path: src/tests/e2e/screenshots/

  accessibility-scan:
    runs-on: ubuntu-latest
    needs: test
    steps:
      - uses: actions/checkout@v3

      - name: Install Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'

      - name: Install Pa11y CI
        run: npm install -g pa11y-ci

      - name: Start application
        run: |
          cd src
          python manage.py runserver &
          sleep 5

      - name: Run Pa11y accessibility scan
        run: pa11y-ci --config pa11y-config.json
```

### Pre-Deployment Tests

```yaml
# .github/workflows/pre-deploy.yml
name: Pre-Deployment Tests

on:
  push:
    tags:
      - 'v*'

jobs:
  smoke-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Deploy to staging
        run: ./scripts/deploy_staging.sh

      - name: Run smoke tests
        run: pytest src/tests/smoke/ --base-url=https://staging.obcms.local

      - name: Run OAT tests
        run: pytest src/tests/oat/ -v

  performance-baseline:
    runs-on: ubuntu-latest
    needs: smoke-tests
    steps:
      - uses: actions/checkout@v3

      - name: Install Locust
        run: pip install locust

      - name: Run performance tests
        run: |
          locust -f src/tests/performance/locustfile.py \
            --host=https://staging.obcms.local \
            --users 50 \
            --spawn-rate 5 \
            --run-time 2m \
            --headless \
            --html performance-report.html

      - name: Upload performance report
        uses: actions/upload-artifact@v3
        with:
          name: performance-report
          path: performance-report.html
```

## Test Execution Schedule

### CI Pipeline Stages

| Stage | Tests | Duration | Trigger |
|-------|-------|----------|---------|
| **Pre-commit** | Unit, Lint | 1-2 min | Every commit |
| **CI (PR)** | Unit, Integration, API, Lint, SAST | 5-10 min | Pull request |
| **Pre-Deploy (Staging)** | E2E, Visual, A11y, DAST, Smoke, OAT | 15-30 min | Before deploy |
| **Deployment** | Smoke, Canary validation | 5-10 min | During deploy |
| **Post-Deploy** | Synthetic monitors | Continuous | In production |

### Nightly Tests

```bash
# crontab -e
# Run comprehensive test suite nightly
0 2 * * * cd /path/to/obcms && ./scripts/run_nightly_tests.sh
```

**Nightly Test Script:**
```bash
#!/bin/bash
# scripts/run_nightly_tests.sh

set -e

echo "Starting nightly test suite..."

# Full regression
pytest src/ -v \
  --cov=src \
  --cov-report=html \
  --html=test-report.html

# Performance baseline
locust -f src/tests/performance/locustfile.py \
  --host=http://localhost:8000 \
  --users 100 \
  --spawn-rate 10 \
  --run-time 10m \
  --headless \
  --html performance-report.html

# Security scans
bandit -r src/ -f html -o security-report.html
pip-audit --requirement requirements/base.txt

# Accessibility scan
pa11y-ci --config pa11y-config.json

# Send report
python scripts/send_test_report.py
```

## Metrics & Reporting

### Coverage Requirements

- **Overall Coverage:** 80%+
- **Critical Modules:** 90%+ (models, serializers, business logic)
- **Views:** 70%+ (harder to test, UI changes frequently)
- **Utilities:** 90%+

**Enforce in CI:**
```bash
pytest --cov=src --cov-fail-under=80
```

### Test Quality Metrics

Track these metrics over time:

1. **Test Count Growth**
   - Unit tests should grow with codebase
   - Target: 3-5 unit tests per new feature

2. **Test Execution Time**
   - Unit tests: < 10 seconds
   - Integration: < 1 minute
   - E2E: < 5 minutes
   - Full suite: < 15 minutes

3. **Flakiness Rate**
   - Target: < 1% flaky tests
   - Fix or quarantine flaky tests immediately

4. **Bug Escape Rate**
   - Bugs found in production that tests missed
   - Target: < 5% of all bugs

### Test Reports

**Generate HTML Report:**
```bash
pytest --html=test-report.html --self-contained-html
```

**Coverage Report:**
```bash
pytest --cov=src --cov-report=html
open htmlcov/index.html
```

**JUnit XML (for CI):**
```bash
pytest --junitxml=test-results.xml
```

## Continuous Improvement

### Test Review Checklist

When reviewing PRs, verify:
- [ ] New code has unit tests (80%+ coverage)
- [ ] API changes have API tests
- [ ] UI changes have E2E tests (critical paths)
- [ ] Tests are not flaky (run 3 times locally)
- [ ] Tests follow naming conventions
- [ ] Factories used instead of manual object creation
- [ ] Tests are isolated (no shared state)

### Testing Retrospective (Monthly)

Review and discuss:
1. **Escaped Bugs:** Why did tests miss them?
2. **Flaky Tests:** Which tests are unstable?
3. **Slow Tests:** Which tests take too long?
4. **Coverage Gaps:** Where is coverage low?
5. **Test Debt:** What tests need refactoring?

### Testing Training

Ensure team knows:
- Pytest basics and fixtures
- Factory Boy usage
- Playwright for E2E tests
- How to run tests locally
- How to debug failing tests
- When to write unit vs integration vs E2E tests

## Appendix: Quick Reference

### Common Commands

```bash
# Run all tests
pytest

# Run specific app
pytest src/mana/tests/

# Run by marker
pytest -m unit
pytest -m "unit or integration"
pytest -m "not slow"

# Run specific test
pytest src/mana/tests/test_models.py::test_assessment_creation

# Run with coverage
pytest --cov=src --cov-report=html

# Run with verbose output
pytest -v -s

# Run and stop on first failure
pytest -x

# Run failed tests from last run
pytest --lf

# Run tests matching pattern
pytest -k "test_api"

# Parallel execution
pytest -n auto  # Requires pytest-xdist
```

### Pytest Fixtures

```python
# conftest.py
import pytest
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.fixture
def admin_user(db):
    """Create admin user."""
    return User.objects.create_superuser(
        username='admin',
        email='admin@oobc.gov.ph',
        password='admin_password'
    )

@pytest.fixture
def api_client():
    """Get DRF API client."""
    from rest_framework.test import APIClient
    return APIClient()

@pytest.fixture
def authenticated_api_client(api_client, admin_user):
    """Get authenticated API client."""
    api_client.force_authenticate(user=admin_user)
    return api_client
```

### Test Naming Conventions

- `test_<function_name>_<scenario>`
- `test_<model>_<method>_<expected_behavior>`
- `test_api_<endpoint>_<http_method>_<scenario>`

**Examples:**
- `test_barangay_full_name_returns_correct_format`
- `test_api_assessments_post_requires_authentication`
- `test_priority_score_calculation_with_high_votes`

### Environment Variables for Testing

```bash
# .env.test
DEBUG=False
SECRET_KEY=test-secret-key-not-for-production
DATABASE_URL=postgresql://test:test@localhost/obcms_test
REDIS_URL=redis://localhost:6379/1
CELERY_TASK_ALWAYS_EAGER=True  # Run tasks synchronously in tests
EMAIL_BACKEND=django.core.mail.backends.locmem.EmailBackend
```

---

**Document Version:** 1.0
**Last Reviewed:** 2025-10-01
**Next Review:** 2025-11-01
**Owner:** OOBC Development Team
**Approved By:** Technical Lead

"""
End-to-End tests for Budget Preparation Module using Playwright

Tests the complete budget preparation lifecycle from UI perspective:
- Creating budget proposals
- Adding programs and line items
- Submitting and approving budgets
- Viewing budget reports

Requirements:
- Playwright must be installed
- Set RUN_PLAYWRIGHT_E2E=1 to enable tests
- Set PLAYWRIGHT_BASE_URL for server URL (default: http://localhost:8000)
- Set PLAYWRIGHT_USERNAME and PLAYWRIGHT_PASSWORD for authentication
"""

import os
import re
import time
from decimal import Decimal

import pytest

try:
    from playwright.sync_api import Page, expect
except ImportError:  # pragma: no cover
    pytest.skip(
        "Playwright is required for budget preparation E2E tests",
        allow_module_level=True,
    )

pytestmark = pytest.mark.skipif(
    os.environ.get("RUN_PLAYWRIGHT_E2E") != "1",
    reason="Set RUN_PLAYWRIGHT_E2E=1 to execute Playwright E2E tests against a live server.",
)


@pytest.fixture
def authenticated_page(page: Page):
    """Fixture to provide an authenticated page session."""
    base_url = os.environ.get("PLAYWRIGHT_BASE_URL", "http://localhost:8000")
    username = os.environ.get("PLAYWRIGHT_USERNAME", "playwright")
    password = os.environ.get("PLAYWRIGHT_PASSWORD", "Playwright123!")

    # Login
    page.goto(f"{base_url}/login/")
    page.get_by_label("Username").fill(username)
    page.get_by_label("Password").fill(password)
    page.get_by_role("button", name=re.compile("Sign In", re.IGNORECASE)).click()

    # Verify redirect to dashboard
    expect(page).to_have_url(re.compile(".*/dashboard/.*"), timeout=15000)

    yield page


@pytest.fixture
def base_url():
    """Fixture for base URL."""
    return os.environ.get("PLAYWRIGHT_BASE_URL", "http://localhost:8000")


class TestBudgetProposalCreation:
    """Test creating budget proposals through the UI."""

    def test_create_budget_proposal(self, authenticated_page: Page, base_url: str):
        """Test creating a new budget proposal."""
        page = authenticated_page
        console_messages = []
        page.on("console", lambda msg: console_messages.append(msg.text))

        # Navigate to budget preparation
        page.goto(f"{base_url}/budget/preparation/")
        expect(page).to_have_url(re.compile(".*/budget/preparation/.*"), timeout=10000)

        # Click "New Budget Proposal" button
        page.get_by_role("button", name=re.compile("New.*Proposal", re.IGNORECASE)).click()

        # Wait for form to appear
        form = page.locator("form#budget-proposal-form, form[id*='proposal']")
        expect(form).to_be_visible(timeout=5000)

        # Fill in budget proposal details
        unique_suffix = int(time.time())
        fiscal_year = "2025"
        title = f"E2E Test Budget Proposal {unique_suffix}"

        page.locator('select[name="fiscal_year"]').select_option(fiscal_year)
        page.locator('input[name="title"]').fill(title)
        page.locator('textarea[name="description"]').fill("Budget proposal created via E2E test")
        page.locator('input[name="total_requested_budget"]').fill("100000000")

        # Submit form
        page.get_by_role("button", name=re.compile("Save|Submit|Create", re.IGNORECASE)).click()

        # Wait for success toast
        toast = page.locator('#toast-container, .toast, [role="alert"]')
        toast.wait_for(state="visible", timeout=10000)
        toast_text = toast.inner_text(timeout=1000)
        assert any(word in toast_text.lower() for word in ['success', 'created', 'saved']), \
            f"Unexpected toast message: {toast_text}"

        # Verify redirect to proposal detail or list
        page.wait_for_url(re.compile(".*/budget/preparation/.*"), timeout=10000)

        # Verify proposal appears in list
        proposal_title = page.locator(f"text='{title}'")
        expect(proposal_title).to_be_visible(timeout=5000)

    def test_add_program_budget(self, authenticated_page: Page, base_url: str):
        """Test adding a program budget to a proposal."""
        page = authenticated_page

        # Navigate to an existing proposal (assumes at least one exists)
        page.goto(f"{base_url}/budget/preparation/")

        # Click first proposal
        first_proposal = page.locator('.proposal-item, [data-proposal-id]').first
        first_proposal.click()

        # Wait for proposal detail page
        expect(page).to_have_url(re.compile(".*/budget/preparation/proposal/\\d+/.*"), timeout=10000)

        # Click "Add Program" button
        page.get_by_role("button", name=re.compile("Add.*Program", re.IGNORECASE)).click()

        # Fill program budget form
        form = page.locator("form#program-budget-form, form[id*='program']")
        expect(form).to_be_visible(timeout=5000)

        # Select PPA/monitoring entry
        ppa_select = page.locator('select[name="monitoring_entry"], select[name="ppa_id"]')
        if ppa_select.count():
            options = ppa_select.first.locator("option[value]")
            valid_values = [
                option.get_attribute("value")
                for option in options.all()
                if option.get_attribute("value")
            ]
            if valid_values:
                ppa_select.first.select_option(value=valid_values[0])

        page.locator('input[name="requested_amount"]').fill("50000000")
        page.locator('input[name="priority_rank"]').fill("1")

        # Submit
        page.get_by_role("button", name=re.compile("Save|Submit|Add", re.IGNORECASE)).click()

        # Verify success
        toast = page.locator('#toast-container, .toast, [role="alert"]')
        toast.wait_for(state="visible", timeout=10000)

    def test_add_line_items(self, authenticated_page: Page, base_url: str):
        """Test adding line items to a program budget."""
        page = authenticated_page

        # Navigate to proposal with programs
        page.goto(f"{base_url}/budget/preparation/")
        first_proposal = page.locator('.proposal-item, [data-proposal-id]').first
        first_proposal.click()

        # Click on first program
        first_program = page.locator('.program-item, [data-program-id]').first
        first_program.click()

        # Click "Add Line Item" button
        page.get_by_role("button", name=re.compile("Add.*Line.*Item", re.IGNORECASE)).click()

        # Fill line item form
        form = page.locator("form#line-item-form, form[id*='line']")
        expect(form).to_be_visible(timeout=5000)

        page.locator('select[name="category"]').select_option("personnel")
        page.locator('input[name="description"], textarea[name="description"]').fill("E2E Test Line Item")
        page.locator('input[name="unit_cost"]').fill("30000000")
        page.locator('input[name="quantity"]').fill("1")

        # Verify auto-calculation of total_cost
        page.wait_for_timeout(500)  # Allow time for calculation
        total_cost_value = page.locator('input[name="total_cost"]').input_value()
        assert total_cost_value == "30000000"

        # Submit
        page.get_by_role("button", name=re.compile("Save|Submit|Add", re.IGNORECASE)).click()

        # Verify success
        toast = page.locator('#toast-container, .toast, [role="alert"]')
        toast.wait_for(state="visible", timeout=10000)


class TestBudgetWorkflow:
    """Test budget proposal workflow (submit, approve)."""

    def test_submit_budget_proposal(self, authenticated_page: Page, base_url: str):
        """Test submitting a draft proposal."""
        page = authenticated_page

        # Navigate to a draft proposal
        page.goto(f"{base_url}/budget/preparation/")

        # Find draft proposal (assumes filtering or status indicators)
        draft_proposal = page.locator('[data-status="draft"]').first
        if draft_proposal.count() == 0:
            pytest.skip("No draft proposals available for testing")

        draft_proposal.click()

        # Click "Submit" button
        submit_button = page.get_by_role("button", name=re.compile("Submit", re.IGNORECASE))
        submit_button.click()

        # Confirm submission if modal appears
        confirm_button = page.locator('button:has-text("Confirm"), button:has-text("Yes")')
        if confirm_button.count() > 0:
            confirm_button.click()

        # Verify status change
        page.wait_for_timeout(1000)
        status_badge = page.locator('.status-badge, [data-status]')
        expect(status_badge).to_have_text(re.compile("Submitted", re.IGNORECASE), timeout=5000)

    def test_approve_budget_proposal(self, authenticated_page: Page, base_url: str):
        """Test approving a submitted proposal (requires admin permissions)."""
        page = authenticated_page

        # Navigate to submitted proposal
        page.goto(f"{base_url}/budget/preparation/")

        submitted_proposal = page.locator('[data-status="submitted"]').first
        if submitted_proposal.count() == 0:
            pytest.skip("No submitted proposals available for approval")

        submitted_proposal.click()

        # Click "Approve" button
        approve_button = page.get_by_role("button", name=re.compile("Approve", re.IGNORECASE))
        if approve_button.count() == 0:
            pytest.skip("User does not have approval permissions")

        approve_button.click()

        # Fill approval form
        approval_form = page.locator("form#approval-form, form[id*='approval']")
        if approval_form.count() > 0:
            page.locator('input[name="total_approved_budget"]').fill("95000000")
            page.locator('textarea[name="approval_notes"]').fill("Approved via E2E test")
            page.get_by_role("button", name=re.compile("Confirm|Approve", re.IGNORECASE)).click()

        # Verify status change
        page.wait_for_timeout(1000)
        status_badge = page.locator('.status-badge, [data-status]')
        expect(status_badge).to_have_text(re.compile("Approved", re.IGNORECASE), timeout=5000)


class TestBudgetReports:
    """Test budget reporting and analytics."""

    def test_view_budget_summary(self, authenticated_page: Page, base_url: str):
        """Test viewing budget summary dashboard."""
        page = authenticated_page

        # Navigate to budget reports
        page.goto(f"{base_url}/budget/preparation/reports/")

        # Verify summary cards are visible
        total_budget_card = page.locator('[data-metric="total_budget"], .stat-card:has-text("Total Budget")')
        expect(total_budget_card).to_be_visible(timeout=5000)

        # Verify charts/visualizations load
        chart = page.locator('canvas, .chart, [data-chart]')
        if chart.count() > 0:
            expect(chart.first).to_be_visible(timeout=5000)

    def test_variance_report(self, authenticated_page: Page, base_url: str):
        """Test variance analysis report."""
        page = authenticated_page

        # Navigate to variance report
        page.goto(f"{base_url}/budget/preparation/reports/variance/")

        # Verify variance table loads
        variance_table = page.locator('table#variance-table, table.variance-report')
        expect(variance_table).to_be_visible(timeout=5000)

        # Verify table has data
        rows = page.locator('table tbody tr')
        assert rows.count() > 0, "Variance report has no data"

    def test_export_budget_pdf(self, authenticated_page: Page, base_url: str):
        """Test exporting budget as PDF."""
        page = authenticated_page

        # Navigate to a proposal
        page.goto(f"{base_url}/budget/preparation/")
        first_proposal = page.locator('.proposal-item, [data-proposal-id]').first
        first_proposal.click()

        # Click export button
        export_button = page.get_by_role("button", name=re.compile("Export|Download|PDF", re.IGNORECASE))
        if export_button.count() == 0:
            pytest.skip("Export functionality not available")

        # Handle download
        with page.expect_download() as download_info:
            export_button.click()

        download = download_info.value
        assert download.suggested_filename.endswith('.pdf'), "Downloaded file is not a PDF"


class TestBudgetValidation:
    """Test client-side and server-side validation."""

    def test_required_fields_validation(self, authenticated_page: Page, base_url: str):
        """Test that required fields show validation errors."""
        page = authenticated_page

        # Navigate to new proposal form
        page.goto(f"{base_url}/budget/preparation/")
        page.get_by_role("button", name=re.compile("New.*Proposal", re.IGNORECASE)).click()

        form = page.locator("form#budget-proposal-form, form[id*='proposal']")
        expect(form).to_be_visible(timeout=5000)

        # Try to submit without filling required fields
        page.get_by_role("button", name=re.compile("Save|Submit|Create", re.IGNORECASE)).click()

        # Verify validation errors appear
        error_messages = page.locator('.error-message, .invalid-feedback, [role="alert"]')
        assert error_messages.count() > 0, "No validation errors shown for required fields"

    def test_numeric_validation(self, authenticated_page: Page, base_url: str):
        """Test numeric field validation."""
        page = authenticated_page

        # Navigate to new proposal form
        page.goto(f"{base_url}/budget/preparation/")
        page.get_by_role("button", name=re.compile("New.*Proposal", re.IGNORECASE)).click()

        form = page.locator("form#budget-proposal-form, form[id*='proposal']")
        expect(form).to_be_visible(timeout=5000)

        # Try to enter non-numeric value
        budget_input = page.locator('input[name="total_requested_budget"]')
        budget_input.fill("invalid")

        # Verify validation error
        page.get_by_role("button", name=re.compile("Save|Submit|Create", re.IGNORECASE)).click()

        error = page.locator('.error-message:has-text("budget"), .invalid-feedback')
        if error.count() > 0:
            assert True  # Validation working
        else:
            # Check if input was rejected/cleared
            assert budget_input.input_value() == "", "Invalid input was accepted"


class TestBudgetResponsiveness:
    """Test responsive design across different screen sizes."""

    def test_mobile_view(self, authenticated_page: Page, base_url: str):
        """Test budget interface on mobile viewport."""
        page = authenticated_page

        # Set mobile viewport
        page.set_viewport_size({"width": 375, "height": 667})  # iPhone SE size

        # Navigate to budget preparation
        page.goto(f"{base_url}/budget/preparation/")

        # Verify mobile menu/navigation works
        mobile_menu = page.locator('[data-mobile-menu], .mobile-menu, button[aria-label*="menu"]')
        if mobile_menu.count() > 0:
            mobile_menu.click()
            nav = page.locator('nav, .navigation')
            expect(nav).to_be_visible(timeout=2000)

    def test_tablet_view(self, authenticated_page: Page, base_url: str):
        """Test budget interface on tablet viewport."""
        page = authenticated_page

        # Set tablet viewport
        page.set_viewport_size({"width": 768, "height": 1024})  # iPad size

        # Navigate to budget preparation
        page.goto(f"{base_url}/budget/preparation/")

        # Verify table columns are visible
        table = page.locator('table')
        if table.count() > 0:
            expect(table).to_be_visible(timeout=2000)


class TestPerformanceMetrics:
    """Test page load performance and metrics."""

    def test_budget_list_load_time(self, authenticated_page: Page, base_url: str):
        """Test that budget list loads within acceptable time."""
        page = authenticated_page

        start_time = time.time()
        page.goto(f"{base_url}/budget/preparation/")

        # Wait for main content to load
        content = page.locator('.budget-list, main, [role="main"]')
        expect(content).to_be_visible(timeout=5000)

        load_time = time.time() - start_time

        # Assert load time is under 3 seconds
        assert load_time < 3.0, f"Page load took {load_time:.2f}s, target is < 3s"

    def test_no_console_errors(self, authenticated_page: Page, base_url: str):
        """Test that no JavaScript console errors occur."""
        page = authenticated_page

        console_errors = []
        page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)

        # Navigate and interact with page
        page.goto(f"{base_url}/budget/preparation/")
        page.wait_for_load_state("networkidle")

        # Filter out known acceptable errors (if any)
        critical_errors = [err for err in console_errors if not any(
            ignore in err.lower() for ignore in ['favicon', 'analytics']
        )]

        assert len(critical_errors) == 0, f"Console errors detected: {critical_errors}"

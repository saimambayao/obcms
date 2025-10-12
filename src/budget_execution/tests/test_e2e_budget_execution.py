"""
End-to-End tests for Budget Execution Module using Playwright

Tests the complete budget execution lifecycle from UI perspective:
- Releasing allotments
- Creating obligations
- Recording disbursements
- Viewing execution reports

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
        "Playwright is required for budget execution E2E tests",
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


class TestAllotmentRelease:
    """Test releasing allotments from approved budgets."""

    def test_release_quarterly_allotment(self, authenticated_page: Page, base_url: str):
        """Test releasing a quarterly allotment."""
        page = authenticated_page
        console_messages = []
        page.on("console", lambda msg: console_messages.append(msg.text))

        # Navigate to budget execution
        page.goto(f"{base_url}/budget/execution/")
        expect(page).to_have_url(re.compile(".*/budget/execution/.*"), timeout=10000)

        # Select an approved program budget
        approved_budget = page.locator('[data-status="approved"]').first
        if approved_budget.count() == 0:
            pytest.skip("No approved budgets available for allotment release")

        approved_budget.click()

        # Click "Release Allotment" button
        release_button = page.get_by_role("button", name=re.compile("Release.*Allotment", re.IGNORECASE))
        release_button.click()

        # Fill allotment form
        form = page.locator("form#allotment-form, form[id*='allotment']")
        expect(form).to_be_visible(timeout=5000)

        page.locator('select[name="quarter"]').select_option("Q1")
        page.locator('input[name="amount"]').fill("10000000")
        page.locator('textarea[name="release_notes"]').fill("Q1 allotment released via E2E test")

        # Submit
        page.get_by_role("button", name=re.compile("Release|Submit|Save", re.IGNORECASE)).click()

        # Verify success
        toast = page.locator('#toast-container, .toast, [role="alert"]')
        toast.wait_for(state="visible", timeout=10000)
        toast_text = toast.inner_text(timeout=1000)
        assert any(word in toast_text.lower() for word in ['success', 'released', 'created']), \
            f"Unexpected toast message: {toast_text}"

    def test_allotment_constraint_validation(self, authenticated_page: Page, base_url: str):
        """Test that allotment cannot exceed approved budget."""
        page = authenticated_page

        # Navigate to execution
        page.goto(f"{base_url}/budget/execution/")

        approved_budget = page.locator('[data-status="approved"]').first
        if approved_budget.count() == 0:
            pytest.skip("No approved budgets available")

        approved_budget.click()

        # Get approved amount from page
        approved_amount_text = page.locator('[data-field="approved_amount"], .approved-amount').inner_text()
        approved_amount = float(re.sub(r'[^\d.]', '', approved_amount_text))

        # Try to release allotment exceeding approved budget
        release_button = page.get_by_role("button", name=re.compile("Release.*Allotment", re.IGNORECASE))
        release_button.click()

        form = page.locator("form#allotment-form, form[id*='allotment']")
        expect(form).to_be_visible(timeout=5000)

        page.locator('select[name="quarter"]').select_option("Q1")
        page.locator('input[name="amount"]').fill(str(approved_amount * 2))  # Exceed approved

        page.get_by_role("button", name=re.compile("Release|Submit|Save", re.IGNORECASE)).click()

        # Verify error message
        error = page.locator('.error-message, .invalid-feedback, [role="alert"]')
        expect(error).to_be_visible(timeout=5000)
        error_text = error.inner_text()
        assert any(word in error_text.lower() for word in ['exceed', 'approved', 'budget']), \
            "Constraint validation not working"

    def test_view_allotment_history(self, authenticated_page: Page, base_url: str):
        """Test viewing allotment release history."""
        page = authenticated_page

        # Navigate to allotment history
        page.goto(f"{base_url}/budget/execution/allotments/")

        # Verify allotments table loads
        table = page.locator('table#allotments-table, table.allotment-list')
        expect(table).to_be_visible(timeout=5000)

        # Verify table has data
        rows = page.locator('table tbody tr')
        if rows.count() > 0:
            # Click first row to view details
            rows.first.click()

            # Verify detail panel shows
            detail_panel = page.locator('.allotment-detail, [data-allotment-detail]')
            expect(detail_panel).to_be_visible(timeout=3000)


class TestObligationManagement:
    """Test creating and managing obligations."""

    def test_create_obligation(self, authenticated_page: Page, base_url: str):
        """Test creating an obligation against an allotment."""
        page = authenticated_page

        # Navigate to execution
        page.goto(f"{base_url}/budget/execution/")

        # Find released allotment
        released_allotment = page.locator('[data-status="released"]').first
        if released_allotment.count() == 0:
            pytest.skip("No released allotments available")

        released_allotment.click()

        # Click "Create Obligation" button
        create_button = page.get_by_role("button", name=re.compile("Create.*Obligation|New.*Obligation", re.IGNORECASE))
        create_button.click()

        # Fill obligation form
        form = page.locator("form#obligation-form, form[id*='obligation']")
        expect(form).to_be_visible(timeout=5000)

        unique_suffix = int(time.time())

        # Select work item
        work_item_select = page.locator('select[name="work_item"]')
        if work_item_select.count():
            options = work_item_select.locator("option[value]")
            valid_values = [
                option.get_attribute("value")
                for option in options.all()
                if option.get_attribute("value")
            ]
            if valid_values:
                work_item_select.select_option(value=valid_values[0])

        page.locator('input[name="amount"]').fill("5000000")
        page.locator('input[name="payee"]').fill(f"E2E Test Contractor {unique_suffix}")
        page.locator('textarea[name="description"]').fill("Obligation created via E2E test")

        # Submit
        page.get_by_role("button", name=re.compile("Create|Submit|Save", re.IGNORECASE)).click()

        # Verify success
        toast = page.locator('#toast-container, .toast, [role="alert"]')
        toast.wait_for(state="visible", timeout=10000)
        toast_text = toast.inner_text(timeout=1000)
        assert 'success' in toast_text.lower() or 'created' in toast_text.lower()

    def test_obligation_exceeds_allotment_validation(self, authenticated_page: Page, base_url: str):
        """Test that obligation cannot exceed allotment amount."""
        page = authenticated_page

        # Navigate to execution
        page.goto(f"{base_url}/budget/execution/")

        released_allotment = page.locator('[data-status="released"]').first
        if released_allotment.count() == 0:
            pytest.skip("No released allotments available")

        released_allotment.click()

        # Get allotment amount
        allotment_amount_text = page.locator('[data-field="allotment_amount"], .allotment-amount').inner_text()
        allotment_amount = float(re.sub(r'[^\d.]', '', allotment_amount_text))

        # Try to create obligation exceeding allotment
        create_button = page.get_by_role("button", name=re.compile("Create.*Obligation", re.IGNORECASE))
        create_button.click()

        form = page.locator("form#obligation-form, form[id*='obligation']")
        expect(form).to_be_visible(timeout=5000)

        page.locator('input[name="amount"]').fill(str(allotment_amount * 2))  # Exceed
        page.locator('input[name="payee"]').fill("Test Contractor")

        page.get_by_role("button", name=re.compile("Create|Submit|Save", re.IGNORECASE)).click()

        # Verify error
        error = page.locator('.error-message, .invalid-feedback, [role="alert"]')
        expect(error).to_be_visible(timeout=5000)
        error_text = error.inner_text()
        assert any(word in error_text.lower() for word in ['exceed', 'allotment', 'available'])

    def test_multiple_obligations_within_limit(self, authenticated_page: Page, base_url: str):
        """Test creating multiple obligations within allotment limit."""
        page = authenticated_page

        # Navigate to execution
        page.goto(f"{base_url}/budget/execution/")

        released_allotment = page.locator('[data-status="released"]').first
        if released_allotment.count() == 0:
            pytest.skip("No released allotments available")

        released_allotment.click()

        # Get available balance
        balance_text = page.locator('[data-field="available_balance"], .available-balance').inner_text()
        available_balance = float(re.sub(r'[^\d.]', '', balance_text))

        if available_balance < 1000000:
            pytest.skip("Insufficient balance for multiple obligations")

        # Create first obligation
        create_button = page.get_by_role("button", name=re.compile("Create.*Obligation", re.IGNORECASE))
        create_button.click()

        form = page.locator("form#obligation-form, form[id*='obligation']")
        expect(form).to_be_visible(timeout=5000)

        page.locator('input[name="amount"]').fill("500000")
        page.locator('input[name="payee"]').fill("Test Contractor 1")
        page.get_by_role("button", name=re.compile("Create|Submit", re.IGNORECASE)).click()

        # Wait for success
        page.wait_for_timeout(2000)

        # Create second obligation
        create_button.click()
        form = page.locator("form#obligation-form, form[id*='obligation']")
        expect(form).to_be_visible(timeout=5000)

        page.locator('input[name="amount"]').fill("500000")
        page.locator('input[name="payee"]').fill("Test Contractor 2")
        page.get_by_role("button", name=re.compile("Create|Submit", re.IGNORECASE)).click()

        # Verify both obligations appear
        page.wait_for_timeout(2000)
        obligation_rows = page.locator('.obligation-item, [data-obligation-id]')
        assert obligation_rows.count() >= 2, "Multiple obligations not created"


class TestDisbursementProcessing:
    """Test recording disbursements."""

    def test_record_disbursement(self, authenticated_page: Page, base_url: str):
        """Test recording a disbursement for an obligation."""
        page = authenticated_page

        # Navigate to obligations
        page.goto(f"{base_url}/budget/execution/obligations/")

        # Select an obligated item
        obligated_item = page.locator('[data-status="obligated"]').first
        if obligated_item.count() == 0:
            pytest.skip("No obligations available for disbursement")

        obligated_item.click()

        # Click "Record Disbursement" button
        disburse_button = page.get_by_role("button", name=re.compile("Record.*Disbursement|Disburse", re.IGNORECASE))
        disburse_button.click()

        # Fill disbursement form
        form = page.locator("form#disbursement-form, form[id*='disbursement']")
        expect(form).to_be_visible(timeout=5000)

        page.locator('input[name="amount"]').fill("2500000")
        page.locator('select[name="payment_method"]').select_option("check")
        page.locator('input[name="check_number"]').fill("CHK123456")
        page.locator('textarea[name="notes"]').fill("Disbursement recorded via E2E test")

        # Submit
        page.get_by_role("button", name=re.compile("Record|Submit|Save", re.IGNORECASE)).click()

        # Verify success
        toast = page.locator('#toast-container, .toast, [role="alert"]')
        toast.wait_for(state="visible", timeout=10000)

    def test_progressive_disbursement_30_30_40(self, authenticated_page: Page, base_url: str):
        """Test 30-30-40 progressive disbursement pattern."""
        page = authenticated_page

        # Navigate to obligations
        page.goto(f"{base_url}/budget/execution/obligations/")

        obligated_item = page.locator('[data-status="obligated"]').first
        if obligated_item.count() == 0:
            pytest.skip("No obligations available")

        obligated_item.click()

        # Get obligation amount
        obligation_amount_text = page.locator('[data-field="obligation_amount"]').inner_text()
        obligation_amount = float(re.sub(r'[^\d.]', '', obligation_amount_text))

        # First disbursement: 30%
        disburse_button = page.get_by_role("button", name=re.compile("Record.*Disbursement", re.IGNORECASE))
        disburse_button.click()

        form = page.locator("form#disbursement-form")
        expect(form).to_be_visible(timeout=5000)

        first_payment = obligation_amount * 0.30
        page.locator('input[name="amount"]').fill(str(int(first_payment)))
        page.locator('select[name="payment_method"]').select_option("check")
        page.get_by_role("button", name=re.compile("Record|Submit", re.IGNORECASE)).click()

        page.wait_for_timeout(2000)

        # Second disbursement: 30%
        disburse_button.click()
        form = page.locator("form#disbursement-form")
        expect(form).to_be_visible(timeout=5000)

        page.locator('input[name="amount"]').fill(str(int(first_payment)))
        page.locator('select[name="payment_method"]').select_option("check")
        page.get_by_role("button", name=re.compile("Record|Submit", re.IGNORECASE)).click()

        page.wait_for_timeout(2000)

        # Verify status updated to partially_disbursed
        status_badge = page.locator('.status-badge, [data-status]')
        expect(status_badge).to_have_text(re.compile("Partially", re.IGNORECASE), timeout=3000)

    def test_disbursement_exceeds_obligation_validation(self, authenticated_page: Page, base_url: str):
        """Test that disbursement cannot exceed obligation amount."""
        page = authenticated_page

        # Navigate to obligations
        page.goto(f"{base_url}/budget/execution/obligations/")

        obligated_item = page.locator('[data-status="obligated"]').first
        if obligated_item.count() == 0:
            pytest.skip("No obligations available")

        obligated_item.click()

        # Get obligation amount
        obligation_amount_text = page.locator('[data-field="obligation_amount"]').inner_text()
        obligation_amount = float(re.sub(r'[^\d.]', '', obligation_amount_text))

        # Try to disburse more than obligated
        disburse_button = page.get_by_role("button", name=re.compile("Record.*Disbursement", re.IGNORECASE))
        disburse_button.click()

        form = page.locator("form#disbursement-form")
        expect(form).to_be_visible(timeout=5000)

        page.locator('input[name="amount"]').fill(str(obligation_amount * 2))
        page.locator('select[name="payment_method"]').select_option("check")
        page.get_by_role("button", name=re.compile("Record|Submit", re.IGNORECASE)).click()

        # Verify error
        error = page.locator('.error-message, .invalid-feedback, [role="alert"]')
        expect(error).to_be_visible(timeout=5000)


class TestExecutionReports:
    """Test budget execution reporting."""

    def test_execution_dashboard(self, authenticated_page: Page, base_url: str):
        """Test viewing execution dashboard."""
        page = authenticated_page

        # Navigate to execution dashboard
        page.goto(f"{base_url}/budget/execution/dashboard/")

        # Verify key metrics are visible
        metrics = [
            "total_allotted",
            "total_obligated",
            "total_disbursed",
            "utilization_rate"
        ]

        for metric in metrics:
            metric_card = page.locator(f'[data-metric="{metric}"]')
            if metric_card.count() > 0:
                expect(metric_card).to_be_visible(timeout=5000)

        # Verify charts load
        chart = page.locator('canvas, .chart, [data-chart]')
        if chart.count() > 0:
            expect(chart.first).to_be_visible(timeout=5000)

    def test_quarterly_execution_report(self, authenticated_page: Page, base_url: str):
        """Test quarterly execution report."""
        page = authenticated_page

        # Navigate to quarterly report
        page.goto(f"{base_url}/budget/execution/reports/quarterly/")

        # Select quarter
        quarter_select = page.locator('select[name="quarter"]')
        if quarter_select.count() > 0:
            quarter_select.select_option("Q1")

        # Verify report table loads
        report_table = page.locator('table.quarterly-report')
        expect(report_table).to_be_visible(timeout=5000)

    def test_utilization_rate_calculation(self, authenticated_page: Page, base_url: str):
        """Test utilization rate calculation display."""
        page = authenticated_page

        # Navigate to execution dashboard
        page.goto(f"{base_url}/budget/execution/dashboard/")

        # Get utilization rate
        utilization_card = page.locator('[data-metric="utilization_rate"]')
        if utilization_card.count() == 0:
            pytest.skip("Utilization rate not displayed")

        expect(utilization_card).to_be_visible(timeout=5000)

        # Verify percentage format
        utilization_text = utilization_card.inner_text()
        assert '%' in utilization_text, "Utilization rate not displayed as percentage"

    def test_export_execution_report_excel(self, authenticated_page: Page, base_url: str):
        """Test exporting execution report to Excel."""
        page = authenticated_page

        # Navigate to execution reports
        page.goto(f"{base_url}/budget/execution/reports/")

        # Click export button
        export_button = page.get_by_role("button", name=re.compile("Export|Download|Excel", re.IGNORECASE))
        if export_button.count() == 0:
            pytest.skip("Export functionality not available")

        # Handle download
        with page.expect_download() as download_info:
            export_button.click()

        download = download_info.value
        filename = download.suggested_filename
        assert filename.endswith(('.xlsx', '.xls')), "Downloaded file is not Excel format"


class TestExecutionWorkflow:
    """Test complete execution workflow."""

    def test_full_execution_cycle(self, authenticated_page: Page, base_url: str):
        """Test complete cycle: allotment → obligation → disbursement."""
        page = authenticated_page
        unique_suffix = int(time.time())

        # Step 1: Release Allotment
        page.goto(f"{base_url}/budget/execution/")
        approved_budget = page.locator('[data-status="approved"]').first
        if approved_budget.count() == 0:
            pytest.skip("No approved budgets available")

        approved_budget.click()

        release_button = page.get_by_role("button", name=re.compile("Release.*Allotment", re.IGNORECASE))
        release_button.click()

        form = page.locator("form#allotment-form")
        expect(form).to_be_visible(timeout=5000)

        page.locator('select[name="quarter"]').select_option("Q1")
        page.locator('input[name="amount"]').fill("10000000")
        page.get_by_role("button", name=re.compile("Release|Submit", re.IGNORECASE)).click()

        page.wait_for_timeout(2000)

        # Step 2: Create Obligation
        create_obligation = page.get_by_role("button", name=re.compile("Create.*Obligation", re.IGNORECASE))
        create_obligation.click()

        form = page.locator("form#obligation-form")
        expect(form).to_be_visible(timeout=5000)

        page.locator('input[name="amount"]').fill("8000000")
        page.locator('input[name="payee"]').fill(f"E2E Contractor {unique_suffix}")
        page.get_by_role("button", name=re.compile("Create|Submit", re.IGNORECASE)).click()

        page.wait_for_timeout(2000)

        # Step 3: Record Disbursement
        disburse_button = page.get_by_role("button", name=re.compile("Record.*Disbursement", re.IGNORECASE))
        disburse_button.click()

        form = page.locator("form#disbursement-form")
        expect(form).to_be_visible(timeout=5000)

        page.locator('input[name="amount"]').fill("2400000")  # 30%
        page.locator('select[name="payment_method"]').select_option("check")
        page.get_by_role("button", name=re.compile("Record|Submit", re.IGNORECASE)).click()

        # Verify success
        toast = page.locator('#toast-container, .toast')
        toast.wait_for(state="visible", timeout=10000)


class TestAccessibilityCompliance:
    """Test WCAG 2.1 AA accessibility compliance."""

    def test_keyboard_navigation(self, authenticated_page: Page, base_url: str):
        """Test keyboard navigation through forms."""
        page = authenticated_page

        # Navigate to execution
        page.goto(f"{base_url}/budget/execution/")

        # Try tabbing through interface
        page.keyboard.press("Tab")
        page.keyboard.press("Tab")
        page.keyboard.press("Tab")

        # Verify focus is visible
        focused_element = page.evaluate("document.activeElement.tagName")
        assert focused_element in ['A', 'BUTTON', 'INPUT', 'SELECT'], "Keyboard navigation not working"

    def test_form_labels(self, authenticated_page: Page, base_url: str):
        """Test that all form inputs have labels."""
        page = authenticated_page

        # Navigate to new allotment form
        page.goto(f"{base_url}/budget/execution/")
        approved_budget = page.locator('[data-status="approved"]').first
        if approved_budget.count() > 0:
            approved_budget.click()
            release_button = page.get_by_role("button", name=re.compile("Release.*Allotment", re.IGNORECASE))
            release_button.click()

            form = page.locator("form")
            if form.count() > 0:
                # Check all inputs have labels
                inputs = page.locator('input:not([type="hidden"]), select, textarea')
                for i in range(inputs.count()):
                    input_elem = inputs.nth(i)
                    input_id = input_elem.get_attribute("id")
                    if input_id:
                        label = page.locator(f'label[for="{input_id}"]')
                        # If no explicit label, check for aria-label
                        if label.count() == 0:
                            aria_label = input_elem.get_attribute("aria-label")
                            assert aria_label, f"Input {input_id} has no label"

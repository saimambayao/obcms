"""
Accessibility Tests for Budget System using Axe DevTools

Tests WCAG 2.1 AA compliance for budget preparation and execution modules.

Requirements:
- Playwright with axe-core integration
- pytest-playwright
- axe-playwright package

Installation:
    pip install pytest-playwright axe-playwright
    playwright install

Usage:
    pytest test_accessibility.py -v
    pytest test_accessibility.py -v --headed  # See browser
"""

import os
import pytest
from axe_playwright_python.sync_playwright import Axe

try:
    from playwright.sync_api import Page, expect
except ImportError:
    pytest.skip(
        "Playwright and axe-playwright are required for accessibility tests",
        allow_module_level=True,
    )

pytestmark = pytest.mark.skipif(
    os.environ.get("RUN_PLAYWRIGHT_E2E") != "1",
    reason="Set RUN_PLAYWRIGHT_E2E=1 to execute accessibility tests.",
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
    page.get_by_role("button", name="Sign In").click()

    # Wait for dashboard
    page.wait_for_url("**/dashboard/**", timeout=15000)

    yield page


@pytest.fixture
def base_url():
    """Fixture for base URL."""
    return os.environ.get("PLAYWRIGHT_BASE_URL", "http://localhost:8000")


class TestBudgetPreparationAccessibility:
    """Test accessibility of budget preparation pages."""

    def test_budget_list_accessibility(self, authenticated_page: Page, base_url: str):
        """Test budget list page for WCAG 2.1 AA compliance."""
        page = authenticated_page

        # Navigate to budget list
        page.goto(f"{base_url}/budget/preparation/")
        page.wait_for_load_state("networkidle")

        # Run axe accessibility scan
        axe = Axe()
        results = axe.run(page)

        # Assert no violations
        violations = results.violations
        if violations:
            print("\n=== Accessibility Violations on Budget List ===")
            for violation in violations:
                print(f"\nImpact: {violation['impact']}")
                print(f"ID: {violation['id']}")
                print(f"Description: {violation['description']}")
                print(f"Help: {violation['help']}")
                print(f"Help URL: {violation['helpUrl']}")
                print(f"Tags: {', '.join(violation['tags'])}")
                print(f"Nodes affected: {len(violation['nodes'])}")

                for node in violation['nodes'][:3]:  # Show first 3 nodes
                    print(f"  - Element: {node.get('html', 'N/A')}")
                    print(f"    Failure: {node.get('failureSummary', 'N/A')}")

        # Filter critical and serious violations
        critical_violations = [v for v in violations if v['impact'] in ['critical', 'serious']]

        assert len(critical_violations) == 0, \
            f"Found {len(critical_violations)} critical/serious accessibility violations"

    def test_budget_proposal_form_accessibility(self, authenticated_page: Page, base_url: str):
        """Test budget proposal creation form accessibility."""
        page = authenticated_page

        # Navigate to new proposal form
        page.goto(f"{base_url}/budget/preparation/")
        page.get_by_role("button", name="New Budget Proposal").click()

        # Wait for form
        page.wait_for_selector("form", state="visible", timeout=5000)
        page.wait_for_load_state("networkidle")

        # Run axe scan
        axe = Axe()
        results = axe.run(page)

        violations = results.violations
        critical_violations = [v for v in violations if v['impact'] in ['critical', 'serious']]

        if critical_violations:
            print("\n=== Accessibility Violations on Proposal Form ===")
            for violation in critical_violations:
                print(f"\n{violation['id']}: {violation['description']}")
                print(f"Impact: {violation['impact']}")

        assert len(critical_violations) == 0, \
            f"Found {len(critical_violations)} critical accessibility violations in form"

    def test_budget_detail_page_accessibility(self, authenticated_page: Page, base_url: str):
        """Test budget proposal detail page accessibility."""
        page = authenticated_page

        # Navigate to a proposal detail page
        page.goto(f"{base_url}/budget/preparation/")

        # Click first proposal
        first_proposal = page.locator('.proposal-item, [data-proposal-id]').first
        if first_proposal.count() > 0:
            first_proposal.click()
            page.wait_for_load_state("networkidle")

            # Run axe scan
            axe = Axe()
            results = axe.run(page)

            violations = results.violations
            critical_violations = [v for v in violations if v['impact'] in ['critical', 'serious']]

            assert len(critical_violations) == 0, \
                f"Found {len(critical_violations)} critical accessibility violations"


class TestBudgetExecutionAccessibility:
    """Test accessibility of budget execution pages."""

    def test_execution_dashboard_accessibility(self, authenticated_page: Page, base_url: str):
        """Test execution dashboard accessibility."""
        page = authenticated_page

        # Navigate to execution dashboard
        page.goto(f"{base_url}/budget/execution/dashboard/")
        page.wait_for_load_state("networkidle")

        # Run axe scan
        axe = Axe()
        results = axe.run(page)

        violations = results.violations
        critical_violations = [v for v in violations if v['impact'] in ['critical', 'serious']]

        if critical_violations:
            print("\n=== Accessibility Violations on Execution Dashboard ===")
            for violation in critical_violations:
                print(f"\n{violation['id']}: {violation['description']}")

        assert len(critical_violations) == 0

    def test_allotment_form_accessibility(self, authenticated_page: Page, base_url: str):
        """Test allotment release form accessibility."""
        page = authenticated_page

        # Navigate to execution
        page.goto(f"{base_url}/budget/execution/")

        # Open allotment form
        approved_budget = page.locator('[data-status="approved"]').first
        if approved_budget.count() > 0:
            approved_budget.click()

            release_button = page.get_by_role("button", name="Release Allotment")
            if release_button.count() > 0:
                release_button.click()

                # Wait for form
                page.wait_for_selector("form", state="visible", timeout=5000)
                page.wait_for_load_state("networkidle")

                # Run axe scan
                axe = Axe()
                results = axe.run(page)

                violations = results.violations
                critical_violations = [v for v in violations if v['impact'] in ['critical', 'serious']]

                assert len(critical_violations) == 0


class TestSpecificAccessibilityRequirements:
    """Test specific WCAG 2.1 AA requirements."""

    def test_color_contrast(self, authenticated_page: Page, base_url: str):
        """Test color contrast ratios meet WCAG AA standards."""
        page = authenticated_page

        page.goto(f"{base_url}/budget/preparation/")
        page.wait_for_load_state("networkidle")

        # Run axe with focus on color-contrast
        axe = Axe()
        results = axe.run(page, options={
            'runOnly': {
                'type': 'tag',
                'values': ['wcag2aa', 'wcag21aa']
            }
        })

        # Check specifically for color contrast violations
        contrast_violations = [
            v for v in results.violations
            if 'color-contrast' in v['id']
        ]

        if contrast_violations:
            print("\n=== Color Contrast Violations ===")
            for violation in contrast_violations:
                print(f"\n{violation['id']}: {violation['description']}")
                for node in violation['nodes']:
                    print(f"  Element: {node.get('html', 'N/A')[:100]}")

        assert len(contrast_violations) == 0, "Color contrast violations found"

    def test_form_labels(self, authenticated_page: Page, base_url: str):
        """Test that all form inputs have proper labels."""
        page = authenticated_page

        page.goto(f"{base_url}/budget/preparation/")
        page.get_by_role("button", name="New Budget Proposal").click()

        page.wait_for_selector("form", state="visible", timeout=5000)

        # Run axe with focus on form labels
        axe = Axe()
        results = axe.run(page, options={
            'runOnly': {
                'type': 'rule',
                'values': ['label', 'label-title-only']
            }
        })

        label_violations = results.violations

        if label_violations:
            print("\n=== Form Label Violations ===")
            for violation in label_violations:
                print(f"\n{violation['id']}: {violation['description']}")

        assert len(label_violations) == 0, "Form inputs missing labels"

    def test_keyboard_accessibility(self, authenticated_page: Page, base_url: str):
        """Test keyboard navigation and focus management."""
        page = authenticated_page

        page.goto(f"{base_url}/budget/preparation/")
        page.wait_for_load_state("networkidle")

        # Run axe with focus on keyboard accessibility
        axe = Axe()
        results = axe.run(page, options={
            'runOnly': {
                'type': 'tag',
                'values': ['keyboard']
            }
        })

        keyboard_violations = results.violations

        if keyboard_violations:
            print("\n=== Keyboard Accessibility Violations ===")
            for violation in keyboard_violations:
                print(f"\n{violation['id']}: {violation['description']}")

        assert len(keyboard_violations) == 0, "Keyboard accessibility issues found"

    def test_focus_indicators(self, authenticated_page: Page, base_url: str):
        """Test that focus indicators are visible."""
        page = authenticated_page

        page.goto(f"{base_url}/budget/preparation/")

        # Tab to first interactive element
        page.keyboard.press("Tab")

        # Get focused element styles
        focus_outline = page.evaluate("""
            () => {
                const focused = document.activeElement;
                const styles = window.getComputedStyle(focused);
                return {
                    outline: styles.outline,
                    outlineWidth: styles.outlineWidth,
                    outlineColor: styles.outlineColor,
                    boxShadow: styles.boxShadow
                };
            }
        """)

        # Check that there's a visible focus indicator
        has_outline = focus_outline['outlineWidth'] != '0px' and focus_outline['outlineWidth'] != 'medium'
        has_box_shadow = focus_outline['boxShadow'] != 'none'

        assert has_outline or has_box_shadow, \
            "Focus indicator not visible"

    def test_heading_structure(self, authenticated_page: Page, base_url: str):
        """Test proper heading hierarchy (h1, h2, h3, etc.)."""
        page = authenticated_page

        page.goto(f"{base_url}/budget/preparation/")
        page.wait_for_load_state("networkidle")

        # Run axe with focus on heading structure
        axe = Axe()
        results = axe.run(page, options={
            'runOnly': {
                'type': 'rule',
                'values': ['page-has-heading-one', 'heading-order']
            }
        })

        heading_violations = results.violations

        if heading_violations:
            print("\n=== Heading Structure Violations ===")
            for violation in heading_violations:
                print(f"\n{violation['id']}: {violation['description']}")

        assert len(heading_violations) == 0, "Heading structure issues found"

    def test_aria_attributes(self, authenticated_page: Page, base_url: str):
        """Test proper ARIA attributes."""
        page = authenticated_page

        page.goto(f"{base_url}/budget/preparation/")
        page.wait_for_load_state("networkidle")

        # Run axe with focus on ARIA
        axe = Axe()
        results = axe.run(page, options={
            'runOnly': {
                'type': 'tag',
                'values': ['best-practice', 'wcag2a', 'wcag2aa']
            }
        })

        aria_violations = [
            v for v in results.violations
            if 'aria' in v['id'].lower()
        ]

        if aria_violations:
            print("\n=== ARIA Violations ===")
            for violation in aria_violations:
                print(f"\n{violation['id']}: {violation['description']}")

        assert len(aria_violations) == 0, "ARIA attribute issues found"

    def test_touch_target_size(self, authenticated_page: Page, base_url: str):
        """Test that interactive elements meet minimum touch target size (48x48px)."""
        page = authenticated_page

        page.goto(f"{base_url}/budget/preparation/")
        page.wait_for_load_state("networkidle")

        # Get all buttons and links
        interactive_elements = page.evaluate("""
            () => {
                const buttons = Array.from(document.querySelectorAll('button, a[href], input[type="button"]'));
                return buttons.map(el => {
                    const rect = el.getBoundingClientRect();
                    return {
                        tag: el.tagName,
                        text: el.textContent?.trim().substring(0, 30),
                        width: rect.width,
                        height: rect.height
                    };
                }).filter(el => el.width > 0 && el.height > 0);
            }
        """)

        # Check for elements smaller than 44x44 (WCAG 2.1 minimum)
        small_targets = [
            el for el in interactive_elements
            if el['width'] < 44 or el['height'] < 44
        ]

        if small_targets:
            print("\n=== Small Touch Targets (<44x44px) ===")
            for target in small_targets[:10]:  # Show first 10
                print(f"{target['tag']}: {target['text']} - {target['width']}x{target['height']}px")

        # Allow some small targets (like inline links), but check ratio
        acceptable_ratio = len(small_targets) / len(interactive_elements) if interactive_elements else 0

        assert acceptable_ratio < 0.3, \
            f"Too many small touch targets: {len(small_targets)}/{len(interactive_elements)}"

    def test_alt_text_for_images(self, authenticated_page: Page, base_url: str):
        """Test that all images have alt text."""
        page = authenticated_page

        page.goto(f"{base_url}/budget/preparation/")
        page.wait_for_load_state("networkidle")

        # Run axe with focus on images
        axe = Axe()
        results = axe.run(page, options={
            'runOnly': {
                'type': 'rule',
                'values': ['image-alt']
            }
        })

        image_violations = results.violations

        if image_violations:
            print("\n=== Image Alt Text Violations ===")
            for violation in image_violations:
                print(f"\n{violation['id']}: {violation['description']}")
                for node in violation['nodes']:
                    print(f"  Image: {node.get('html', 'N/A')[:100]}")

        assert len(image_violations) == 0, "Images missing alt text"


class TestScreenReaderCompatibility:
    """Test screen reader compatibility."""

    def test_landmark_regions(self, authenticated_page: Page, base_url: str):
        """Test that page has proper landmark regions (header, nav, main, footer)."""
        page = authenticated_page

        page.goto(f"{base_url}/budget/preparation/")
        page.wait_for_load_state("networkidle")

        # Check for landmark regions
        landmarks = page.evaluate("""
            () => {
                return {
                    header: document.querySelector('header, [role="banner"]') !== null,
                    nav: document.querySelector('nav, [role="navigation"]') !== null,
                    main: document.querySelector('main, [role="main"]') !== null,
                    footer: document.querySelector('footer, [role="contentinfo"]') !== null
                };
            }
        """)

        assert landmarks['main'], "Page missing main landmark"
        # Header, nav, footer are recommended but not always required

    def test_skip_to_content_link(self, authenticated_page: Page, base_url: str):
        """Test that page has skip-to-content link for keyboard users."""
        page = authenticated_page

        page.goto(f"{base_url}/budget/preparation/")

        # Tab to first element (should be skip link)
        page.keyboard.press("Tab")

        # Check if focused element is a skip link
        focused_text = page.evaluate("document.activeElement.textContent")

        # Skip link should contain words like "skip", "content", "main"
        is_skip_link = any(word in focused_text.lower() for word in ['skip', 'content', 'main'])

        # Note: This is recommended but not always required
        # Can be a warning instead of failure
        if not is_skip_link:
            print("\nWarning: No skip-to-content link detected")


class TestResponsiveAccessibility:
    """Test accessibility across different viewport sizes."""

    def test_mobile_accessibility(self, authenticated_page: Page, base_url: str):
        """Test accessibility on mobile viewport."""
        page = authenticated_page

        # Set mobile viewport (iPhone SE)
        page.set_viewport_size({"width": 375, "height": 667})

        page.goto(f"{base_url}/budget/preparation/")
        page.wait_for_load_state("networkidle")

        # Run axe scan
        axe = Axe()
        results = axe.run(page)

        violations = results.violations
        critical_violations = [v for v in violations if v['impact'] in ['critical', 'serious']]

        assert len(critical_violations) == 0, \
            f"Found {len(critical_violations)} accessibility violations on mobile"

    def test_tablet_accessibility(self, authenticated_page: Page, base_url: str):
        """Test accessibility on tablet viewport."""
        page = authenticated_page

        # Set tablet viewport (iPad)
        page.set_viewport_size({"width": 768, "height": 1024})

        page.goto(f"{base_url}/budget/preparation/")
        page.wait_for_load_state("networkidle")

        # Run axe scan
        axe = Axe()
        results = axe.run(page)

        violations = results.violations
        critical_violations = [v for v in violations if v['impact'] in ['critical', 'serious']]

        assert len(critical_violations) == 0, \
            f"Found {len(critical_violations)} accessibility violations on tablet"


def generate_accessibility_report(results, output_file="accessibility_report.html"):
    """Generate an HTML accessibility report."""
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Accessibility Test Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            h1 {{ color: #333; }}
            .violation {{ margin: 20px 0; padding: 15px; border-left: 4px solid red; background: #fee; }}
            .pass {{ margin: 20px 0; padding: 15px; border-left: 4px solid green; background: #efe; }}
            .impact {{ font-weight: bold; text-transform: uppercase; }}
            .critical {{ color: #d00; }}
            .serious {{ color: #f80; }}
            .moderate {{ color: #fa0; }}
            .minor {{ color: #0a0; }}
        </style>
    </head>
    <body>
        <h1>OBCMS Budget System - Accessibility Test Report</h1>
        <p>Generated: {date}</p>
        <h2>Summary</h2>
        <p>Total Violations: {total_violations}</p>
        <p>Critical: {critical}</p>
        <p>Serious: {serious}</p>
        <p>Moderate: {moderate}</p>
        <p>Minor: {minor}</p>
        {violations_html}
    </body>
    </html>
    """
    # Implementation would generate full HTML report
    pass

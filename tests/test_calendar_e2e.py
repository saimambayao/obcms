import os
import re
import time

import pytest

try:
    from playwright.sync_api import Page, expect
except ImportError:  # pragma: no cover - handled via skip
    pytest.skip(
        "Playwright is required for calendar E2E tests",
        allow_module_level=True,
    )

pytestmark = pytest.mark.skipif(
    os.environ.get("RUN_PLAYWRIGHT_E2E") != "1",
    reason="Set RUN_PLAYWRIGHT_E2E=1 to execute Playwright calendar E2E against a live server.",
)

def test_calendar_e2e(page: Page):
    console_messages = []
    page.on("console", lambda message: console_messages.append(message.text))

    base_url = os.environ.get("PLAYWRIGHT_BASE_URL", "http://localhost:8000")
    username = os.environ.get("PLAYWRIGHT_USERNAME", "playwright")
    password = os.environ.get("PLAYWRIGHT_PASSWORD", "Playwright123!")

    # Login first (calendar view requires authentication)
    page.goto(f"{base_url}/login/")
    page.get_by_label("Username").fill(username)
    page.get_by_label("Password").fill(password)
    page.get_by_role("button", name="Sign In to OBCMS").click()

    # Confirm redirect to dashboard
    expect(page).to_have_url(re.compile(".*/dashboard/.*"), timeout=15000)

    # Navigate to advanced calendar
    page.goto(f"{base_url}/oobc-management/calendar/advanced-modern/")

    # 1. Check for calendar visibility
    calendar = page.locator(".fc")
    expect(calendar).to_be_visible(timeout=10000)

    page.wait_for_function(
        "() => window.calendar && Array.isArray(window.calendar.getEvents())",
        timeout=10000,
    )

    baseline_events = page.evaluate(
        "window.calendar ? window.calendar.getEvents().map(event => ({id: event.id, title: event.title})) : []"
    )
    ids_before = {event["id"] for event in baseline_events}

    # 2. Add a new work item via double click (opens sidebar form)
    page.wait_for_timeout(1500)

    target_date = page.evaluate(
        """() => {
            const cells = Array.from(document.querySelectorAll('.fc-daygrid-day'));
            const emptyCell = cells.find(cell => !cell.querySelector('.fc-event'));
            const target = emptyCell || cells[0];
            return target ? target.getAttribute('data-date') : null;
        }"""
    )
    assert target_date, "Unable to locate a calendar day cell"
    page.evaluate(
        """targetDate => {
            if (typeof window.debugOpenCreateForm === 'function') {
                window.debugOpenCreateForm({dateStr: targetDate, jsEvent: {detail: 2}});
            } else {
                throw new Error('debugOpenCreateForm helper not available');
            }
        }""",
        target_date,
    )

    detail_panel = page.locator("#detailPanel")
    expect(detail_panel).to_have_class(re.compile(".*open.*"), timeout=5000)

    form = page.locator("#detailPanelBody form")
    expect(form).to_be_visible(timeout=5000)

    unique_suffix = int(time.time())
    title = f"Playwright Calendar {unique_suffix}"

    implementing_value = form.locator('[name="implementing_moa"]').first.input_value()
    assert implementing_value, "Implementing MOA did not auto-populate"

    form.locator('input[name="title"]').fill(title)
    assert form.locator('input[name="title"]').input_value() == title
    form.locator('textarea[name="description"]').fill("Calendar E2E created via Playwright.")

    ppa_select = form.locator('select[name="ppa_id"], select[name="related_ppa"]')
    if ppa_select.count():
        options = ppa_select.first.locator("option[value]")
        valid_values = [
            option.get_attribute("value")
            for option in options.all()
            if option.get_attribute("value")
        ]
        if valid_values:
            ppa_select.first.select_option(value=valid_values[0])

    if target_date:
        form.locator('input[name=\"start_date\"]').fill(target_date)
        form.locator('input[name=\"due_date\"]').fill(target_date)

    form.locator('button[type="submit"]').click()

    toast = page.locator('#toast-container')
    toast.wait_for(state="visible", timeout=10000)
    toast_text = toast.inner_text(timeout=1000)
    assert 'created successfully' in toast_text.lower(), f"Unexpected toast: {toast_text}"

    if "Please select a MOA PPA" in page.locator("#detailPanelBody").inner_text():
        body_html = page.locator("#detailPanelBody").inner_html()
        from pathlib import Path

        Path("playwright_create_error.html").write_text(body_html)
        raise AssertionError("Create form returned validation error; see playwright_create_error.html")

    assert page.evaluate("Boolean(window.calendar)"), "Calendar instance not initialised"

    new_ids = set()
    debug_events = []
    for _ in range(120):
        debug_events = page.evaluate(
            "window.calendar ? window.calendar.getEvents().map(event => ({id: event.id, title: event.title})) : []"
        )
        ids_after = {event["id"] for event in debug_events}
        new_ids = ids_after - ids_before
        if new_ids:
            break
        page.wait_for_timeout(500)
    else:
        raise AssertionError(
            "Calendar did not register any new event after creation.\n"
            f"Console logs: {console_messages}\n"
            f"Baseline count: {len(ids_before)}\n"
            f"Final events: {debug_events}"
        )

    new_titles = [event["title"] for event in debug_events if event["id"] in new_ids]
    assert any(title.startswith("Playwright Calendar") for title in new_titles), (
        "New calendar event detected but it does not match expected prefix.\n"
        f"Expected prefix: 'Playwright Calendar'\n"
        f"New titles: {new_titles}\n"
        f"Console logs: {console_messages}"
    )

    page.wait_for_timeout(300)

    # Allow calendar animations to settle for visual confirmation if needed
    page.wait_for_timeout(1000)

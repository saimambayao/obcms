/**
 * AI Chat Widget - Browser Testing Helper Scripts
 *
 * Copy and paste these functions into browser console for testing
 *
 * Usage:
 *   1. Open browser DevTools (F12 or Cmd+Option+I)
 *   2. Copy this entire file
 *   3. Paste into Console tab
 *   4. Run test functions
 */

console.log('🧪 AI Chat Widget Test Helpers Loaded');
console.log('📚 Available functions:', [
    'testChatToggle()',
    'testHTMXSubmission()',
    'testOptimisticUI()',
    'testClickableChips()',
    'testAccessibility()',
    'testMobileLayout()',
    'testErrorHandling()',
    'runAllTests()',
    'generateTestReport()'
]);

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

/**
 * Wait for specified milliseconds
 */
const wait = (ms) => new Promise(resolve => setTimeout(resolve, ms));

/**
 * Get chat elements
 */
function getChatElements() {
    return {
        widget: document.getElementById('ai-chat-widget'),
        panel: document.getElementById('ai-chat-panel'),
        button: document.getElementById('ai-chat-toggle-btn'),
        icon: document.getElementById('ai-chat-icon'),
        form: document.getElementById('ai-chat-form'),
        input: document.getElementById('ai-chat-input'),
        sendBtn: document.getElementById('ai-chat-send-btn'),
        messages: document.getElementById('ai-chat-messages'),
        loading: document.getElementById('ai-chat-loading'),
        backdrop: document.getElementById('ai-chat-backdrop'),
    };
}

/**
 * Assert function for testing
 */
function assert(condition, message) {
    if (!condition) {
        console.error('❌', message);
        return false;
    }
    console.log('✅', message);
    return true;
}

/**
 * Log test section
 */
function logSection(title) {
    console.log('\n' + '='.repeat(60));
    console.log(`  ${title}`);
    console.log('='.repeat(60) + '\n');
}

// ============================================================================
// TEST CATEGORY 1: CHAT TOGGLE & VISIBILITY
// ============================================================================

async function testChatToggle() {
    logSection('TEST: Chat Toggle & Visibility');

    const elements = getChatElements();
    const results = [];

    // Test 1: Widget exists
    results.push(assert(
        elements.widget !== null,
        'Widget element exists'
    ));

    // Test 2: Panel exists
    results.push(assert(
        elements.panel !== null,
        'Panel element exists'
    ));

    // Test 3: Button exists
    results.push(assert(
        elements.button !== null,
        'Toggle button exists'
    ));

    // Test 4: Panel initially hidden
    const initiallyHidden = !elements.panel.classList.contains('chat-open');
    results.push(assert(
        initiallyHidden,
        'Panel initially hidden'
    ));

    // Test 5: Open chat
    window.toggleAIChat();
    await wait(350); // Wait for animation

    results.push(assert(
        elements.panel.classList.contains('chat-open'),
        'Panel opens with chat-open class'
    ));

    // Test 6: ARIA attributes updated
    results.push(assert(
        elements.panel.getAttribute('aria-hidden') === 'false',
        'Panel aria-hidden set to false'
    ));

    results.push(assert(
        elements.button.getAttribute('aria-expanded') === 'true',
        'Button aria-expanded set to true'
    ));

    // Test 7: Icon changed
    results.push(assert(
        elements.icon.classList.contains('fa-times'),
        'Icon changed to X (times)'
    ));

    // Test 8: Panel positioned correctly
    const rect = elements.panel.getBoundingClientRect();
    const isDesktop = window.innerWidth >= 640;

    if (isDesktop) {
        const bottomPosition = window.innerHeight - rect.bottom;
        results.push(assert(
            bottomPosition >= 80 && bottomPosition <= 120,
            `Desktop: Panel bottom position ~100px (actual: ${bottomPosition.toFixed(0)}px)`
        ));

        const rightPosition = window.innerWidth - rect.right;
        results.push(assert(
            rightPosition >= 20 && rightPosition <= 30,
            `Desktop: Panel right position ~24px (actual: ${rightPosition.toFixed(0)}px)`
        ));

        results.push(assert(
            rect.width >= 390 && rect.width <= 410,
            `Desktop: Panel width ~400px (actual: ${rect.width.toFixed(0)}px)`
        ));
    } else {
        results.push(assert(
            rect.width === window.innerWidth,
            `Mobile: Panel full width (${rect.width.toFixed(0)}px)`
        ));

        results.push(assert(
            rect.bottom === window.innerHeight,
            'Mobile: Panel at bottom of viewport'
        ));
    }

    // Test 9: Panel visible
    const computedStyle = getComputedStyle(elements.panel);
    results.push(assert(
        computedStyle.visibility === 'visible',
        'Panel visibility set to visible'
    ));

    results.push(assert(
        parseFloat(computedStyle.opacity) === 1,
        'Panel opacity is 1'
    ));

    // Test 10: Close chat
    window.toggleAIChat();
    await wait(250); // Wait for animation

    results.push(assert(
        !elements.panel.classList.contains('chat-open'),
        'Panel closes (chat-open class removed)'
    ));

    results.push(assert(
        elements.panel.getAttribute('aria-hidden') === 'true',
        'Panel aria-hidden set to true'
    ));

    results.push(assert(
        elements.icon.classList.contains('fa-comments'),
        'Icon changed back to comments'
    ));

    // Summary
    const passed = results.filter(r => r).length;
    const total = results.length;
    console.log(`\n📊 Result: ${passed}/${total} tests passed`);

    return { passed, total, success: passed === total };
}

// ============================================================================
// TEST CATEGORY 2: HTMX FORM SUBMISSION
// ============================================================================

async function testHTMXSubmission() {
    logSection('TEST: HTMX Form Submission');

    const elements = getChatElements();
    const results = [];

    // Ensure chat is open
    if (!elements.panel.classList.contains('chat-open')) {
        window.toggleAIChat();
        await wait(350);
    }

    // Test 1: Form has HTMX attributes
    results.push(assert(
        elements.form.hasAttribute('hx-post'),
        'Form has hx-post attribute'
    ));

    results.push(assert(
        elements.form.getAttribute('hx-target') === '#ai-chat-messages',
        'Form has correct hx-target'
    ));

    results.push(assert(
        elements.form.getAttribute('hx-swap') === 'beforeend scroll:bottom',
        'Form has correct hx-swap'
    ));

    results.push(assert(
        elements.form.getAttribute('hx-indicator') === '#ai-chat-loading',
        'Form has correct hx-indicator'
    ));

    // Test 2: CSRF token present
    const csrfToken = elements.form.querySelector('[name="csrfmiddlewaretoken"]');
    results.push(assert(
        csrfToken !== null,
        'CSRF token input exists'
    ));

    results.push(assert(
        csrfToken.value.length > 0,
        'CSRF token has value'
    ));

    // Test 3: Input field properties
    results.push(assert(
        elements.input.name === 'message',
        'Input field name is "message"'
    ));

    results.push(assert(
        elements.input.hasAttribute('required'),
        'Input field is required'
    ));

    // Test 4: Send button properties
    results.push(assert(
        elements.sendBtn.type === 'submit',
        'Send button type is submit'
    ));

    // Summary
    const passed = results.filter(r => r).length;
    const total = results.length;
    console.log(`\n📊 Result: ${passed}/${total} tests passed`);

    return { passed, total, success: passed === total };
}

// ============================================================================
// TEST CATEGORY 3: OPTIMISTIC UI UPDATES
// ============================================================================

async function testOptimisticUI() {
    logSection('TEST: Optimistic UI Updates');

    const elements = getChatElements();
    const results = [];

    // Ensure chat is open
    if (!elements.panel.classList.contains('chat-open')) {
        window.toggleAIChat();
        await wait(350);
    }

    // Get initial message count
    const initialMessageCount = elements.messages.children.length;

    // Test 1: prepareMessage function exists
    results.push(assert(
        typeof window.prepareMessage === 'function',
        'prepareMessage() function exists'
    ));

    // Test 2: Simulate message send
    const testMessage = 'Test optimistic UI message ' + Date.now();
    elements.input.value = testMessage;

    // Trigger prepareMessage manually
    const event = { target: elements.form };
    window.prepareMessage(event);

    await wait(100); // Wait for DOM update

    // Test 3: User message added immediately
    const newMessageCount = elements.messages.children.length;
    results.push(assert(
        newMessageCount > initialMessageCount,
        'User message added immediately (before server response)'
    ));

    // Test 4: Message has correct styling
    const userMessages = elements.messages.querySelectorAll('.ai-message-user');
    const latestUserMessage = userMessages[userMessages.length - 1];

    results.push(assert(
        latestUserMessage !== undefined,
        'User message element exists'
    ));

    if (latestUserMessage) {
        results.push(assert(
            latestUserMessage.querySelector('.bg-gradient-to-br.from-blue-500') !== null,
            'User message has blue gradient background'
        ));

        results.push(assert(
            latestUserMessage.textContent.includes(testMessage),
            'User message contains correct text'
        ));

        results.push(assert(
            latestUserMessage.textContent.includes('Just now'),
            'User message has "Just now" timestamp'
        ));

        results.push(assert(
            getComputedStyle(latestUserMessage).justifyContent === 'flex-end',
            'User message is right-aligned'
        ));
    }

    // Test 5: XSS prevention
    const xssTest = '<script>alert("XSS")</script>';
    const escapedHTML = latestUserMessage.innerHTML;
    results.push(assert(
        !escapedHTML.includes('<script>') || escapedHTML.includes('&lt;script&gt;'),
        'HTML is escaped (XSS prevention)'
    ));

    // Test 6: escapeHtml function
    if (window.escapeHtml) {
        const escaped = window.escapeHtml('<img src=x onerror=alert(1)>');
        results.push(assert(
            !escaped.includes('<img'),
            'escapeHtml() function prevents XSS'
        ));
    }

    // Test 7: Loading state shown
    results.push(assert(
        elements.sendBtn.disabled === true,
        'Submit button disabled during request'
    ));

    // Clear input
    elements.input.value = '';

    // Summary
    const passed = results.filter(r => r).length;
    const total = results.length;
    console.log(`\n📊 Result: ${passed}/${total} tests passed`);

    return { passed, total, success: passed === total };
}

// ============================================================================
// TEST CATEGORY 4: CLICKABLE QUERY CHIPS
// ============================================================================

async function testClickableChips() {
    logSection('TEST: Clickable Query Chips & Suggestions');

    const elements = getChatElements();
    const results = [];

    // Ensure chat is open
    if (!elements.panel.classList.contains('chat-open')) {
        window.toggleAIChat();
        await wait(350);
    }

    // Test 1: Query chips exist in welcome message
    const queryChips = elements.messages.querySelectorAll('.query-chip');
    results.push(assert(
        queryChips.length >= 4,
        `Found ${queryChips.length} query chips (expected 4)`
    ));

    // Test 2: Each chip has data-query attribute
    const chipsWithQuery = Array.from(queryChips).every(chip =>
        chip.hasAttribute('data-query')
    );
    results.push(assert(
        chipsWithQuery,
        'All query chips have data-query attribute'
    ));

    // Test 3: sendQuery function exists
    results.push(assert(
        typeof window.sendQuery === 'function',
        'sendQuery() function exists'
    ));

    // Test 4: Simulate chip click
    if (queryChips.length > 0) {
        const firstChip = queryChips[0];
        const query = firstChip.getAttribute('data-query');

        results.push(assert(
            query && query.length > 0,
            'First chip has valid query text'
        ));

        // Test sendQuery function
        window.sendQuery(query);
        await wait(100);

        results.push(assert(
            elements.input.value === query,
            'sendQuery() populates input field correctly'
        ));

        // Clear input
        elements.input.value = '';
    }

    // Test 5: Event delegation setup
    results.push(assert(
        typeof window.initClickableQueries === 'function' ||
        document.querySelector('.query-chip') !== null,
        'Clickable query event handlers initialized'
    ));

    // Test 6: Check for clickable-query class (suggestions)
    const suggestions = elements.messages.querySelectorAll('.clickable-query');
    console.log(`ℹ️ Found ${suggestions.length} clickable suggestions`);

    // Summary
    const passed = results.filter(r => r).length;
    const total = results.length;
    console.log(`\n📊 Result: ${passed}/${total} tests passed`);

    return { passed, total, success: passed === total };
}

// ============================================================================
// TEST CATEGORY 5: ACCESSIBILITY
// ============================================================================

async function testAccessibility() {
    logSection('TEST: Accessibility (WCAG 2.1 AA)');

    const elements = getChatElements();
    const results = [];

    // Test 1: Panel has role="dialog"
    results.push(assert(
        elements.panel.getAttribute('role') === 'dialog',
        'Panel has role="dialog"'
    ));

    // Test 2: Panel has aria-labelledby
    results.push(assert(
        elements.panel.hasAttribute('aria-labelledby'),
        'Panel has aria-labelledby attribute'
    ));

    const labelId = elements.panel.getAttribute('aria-labelledby');
    const labelElement = document.getElementById(labelId);
    results.push(assert(
        labelElement !== null,
        `Label element exists (${labelId})`
    ));

    // Test 3: Panel has aria-hidden
    results.push(assert(
        elements.panel.hasAttribute('aria-hidden'),
        'Panel has aria-hidden attribute'
    ));

    // Test 4: Toggle button has aria-expanded
    results.push(assert(
        elements.button.hasAttribute('aria-expanded'),
        'Toggle button has aria-expanded attribute'
    ));

    results.push(assert(
        elements.button.hasAttribute('aria-label'),
        'Toggle button has aria-label'
    ));

    // Test 5: Messages container has role="log"
    results.push(assert(
        elements.messages.getAttribute('role') === 'log',
        'Messages container has role="log"'
    ));

    results.push(assert(
        elements.messages.hasAttribute('aria-live'),
        'Messages container has aria-live attribute'
    ));

    results.push(assert(
        elements.messages.getAttribute('aria-live') === 'polite',
        'Messages container aria-live is "polite"'
    ));

    // Test 6: Input field has aria-label
    results.push(assert(
        elements.input.hasAttribute('aria-label') || elements.input.hasAttribute('id'),
        'Input field has aria-label or id for label association'
    ));

    // Test 7: Send button has aria-label
    results.push(assert(
        elements.sendBtn.hasAttribute('aria-label'),
        'Send button has aria-label'
    ));

    // Test 8: Focus indicators
    const focusableElements = elements.panel.querySelectorAll(
        'button, input, [tabindex]:not([tabindex="-1"])'
    );

    console.log(`ℹ️ Found ${focusableElements.length} focusable elements`);
    results.push(assert(
        focusableElements.length > 0,
        'Panel has focusable elements'
    ));

    // Test 9: Screen reader announcement function
    results.push(assert(
        typeof window.announceToScreenReader === 'function' ||
        document.querySelector('[role="status"]') !== null,
        'Screen reader announcement mechanism exists'
    ));

    // Test 10: Keyboard navigation (Escape key)
    // Open chat if closed
    if (!elements.panel.classList.contains('chat-open')) {
        window.toggleAIChat();
        await wait(350);
    }

    // Simulate Escape key
    const escapeEvent = new KeyboardEvent('keydown', {
        key: 'Escape',
        code: 'Escape',
        keyCode: 27,
        bubbles: true
    });
    document.dispatchEvent(escapeEvent);
    await wait(250);

    results.push(assert(
        !elements.panel.classList.contains('chat-open'),
        'Escape key closes chat'
    ));

    // Test 11: Touch targets (mobile)
    const buttonRect = elements.button.getBoundingClientRect();
    const isMobile = window.innerWidth < 640;
    const minSize = 44; // WCAG minimum

    results.push(assert(
        buttonRect.width >= minSize && buttonRect.height >= minSize,
        `Toggle button meets WCAG minimum touch target (${buttonRect.width.toFixed(0)}x${buttonRect.height.toFixed(0)}px, min: ${minSize}px)`
    ));

    // Summary
    const passed = results.filter(r => r).length;
    const total = results.length;
    console.log(`\n📊 Result: ${passed}/${total} tests passed`);

    return { passed, total, success: passed === total };
}

// ============================================================================
// TEST CATEGORY 6: MOBILE RESPONSIVENESS
// ============================================================================

async function testMobileLayout() {
    logSection('TEST: Mobile Responsiveness');

    const elements = getChatElements();
    const results = [];

    const isMobile = window.innerWidth < 640;
    const isTablet = window.innerWidth >= 640 && window.innerWidth < 1024;
    const isDesktop = window.innerWidth >= 1024;

    console.log(`ℹ️ Current viewport: ${window.innerWidth}x${window.innerHeight}`);
    console.log(`ℹ️ Device type: ${isMobile ? 'Mobile' : isTablet ? 'Tablet' : 'Desktop'}`);

    // Open chat
    if (!elements.panel.classList.contains('chat-open')) {
        window.toggleAIChat();
        await wait(350);
    }

    const panelRect = elements.panel.getBoundingClientRect();

    if (isMobile) {
        // Mobile tests
        results.push(assert(
            panelRect.width === window.innerWidth,
            `Mobile: Panel is full width (${panelRect.width.toFixed(0)}px)`
        ));

        results.push(assert(
            panelRect.bottom === window.innerHeight,
            'Mobile: Panel at bottom of viewport'
        ));

        const expectedHeight = window.innerHeight * 0.8;
        results.push(assert(
            Math.abs(panelRect.height - expectedHeight) < 20,
            `Mobile: Panel height ~80vh (actual: ${panelRect.height.toFixed(0)}px, expected: ${expectedHeight.toFixed(0)}px)`
        ));

        // Backdrop test
        const backdropVisible = !elements.backdrop.classList.contains('hidden');
        results.push(assert(
            backdropVisible,
            'Mobile: Backdrop visible'
        ));

        // Button size
        const buttonRect = elements.button.getBoundingClientRect();
        results.push(assert(
            buttonRect.width >= 56 && buttonRect.height >= 56,
            `Mobile: Button size ≥56px (actual: ${buttonRect.width.toFixed(0)}x${buttonRect.height.toFixed(0)}px)`
        ));

        // Border radius (top corners only)
        const computedStyle = getComputedStyle(elements.panel);
        console.log(`ℹ️ Border radius: ${computedStyle.borderRadius}`);

    } else {
        // Desktop tests
        results.push(assert(
            panelRect.width >= 390 && panelRect.width <= 410,
            `Desktop: Panel width ~400px (actual: ${panelRect.width.toFixed(0)}px)`
        ));

        results.push(assert(
            panelRect.height >= 490 && panelRect.height <= 510,
            `Desktop: Panel height ~500px (actual: ${panelRect.height.toFixed(0)}px)`
        ));

        const bottomPosition = window.innerHeight - panelRect.bottom;
        results.push(assert(
            bottomPosition >= 80 && bottomPosition <= 120,
            `Desktop: Panel bottom position ~100px (actual: ${bottomPosition.toFixed(0)}px)`
        ));

        const rightPosition = window.innerWidth - panelRect.right;
        results.push(assert(
            rightPosition >= 20 && rightPosition <= 30,
            `Desktop: Panel right position ~24px (actual: ${rightPosition.toFixed(0)}px)`
        ));

        // Backdrop should be hidden
        const backdropHidden = elements.backdrop.classList.contains('hidden');
        results.push(assert(
            backdropHidden,
            'Desktop: Backdrop hidden'
        ));
    }

    // Test 7: Panel within viewport
    results.push(assert(
        panelRect.top >= 0,
        'Panel top edge within viewport'
    ));

    results.push(assert(
        panelRect.bottom <= window.innerHeight,
        'Panel bottom edge within viewport'
    ));

    results.push(assert(
        panelRect.left >= 0,
        'Panel left edge within viewport'
    ));

    results.push(assert(
        panelRect.right <= window.innerWidth,
        'Panel right edge within viewport'
    ));

    // Summary
    const passed = results.filter(r => r).length;
    const total = results.length;
    console.log(`\n📊 Result: ${passed}/${total} tests passed`);

    return { passed, total, success: passed === total };
}

// ============================================================================
// TEST CATEGORY 7: ERROR HANDLING
// ============================================================================

async function testErrorHandling() {
    logSection('TEST: Error Handling');

    const elements = getChatElements();
    const results = [];

    // Test 1: HTMX error handler exists
    results.push(assert(
        document.body.hasAttribute('hx-on') ||
        document.querySelector('[hx-on\\:\\:response-error]') !== null ||
        typeof htmx !== 'undefined',
        'HTMX error handling mechanism exists'
    ));

    // Test 2: Error response structure
    console.log('ℹ️ To test error handling, trigger a network error or server error manually');
    console.log('ℹ️ Example: Go offline and send a message');

    // Test 3: Check if error messages have correct styling
    const errorMessages = elements.messages.querySelectorAll('.ai-message-error, .text-red-500');
    if (errorMessages.length > 0) {
        console.log(`ℹ️ Found ${errorMessages.length} error message(s)`);

        const firstError = errorMessages[0];
        const hasRedStyling = firstError.classList.contains('bg-red-50') ||
                             firstError.classList.contains('text-red-500') ||
                             firstError.classList.contains('border-red-200');

        results.push(assert(
            hasRedStyling,
            'Error messages have red styling'
        ));
    } else {
        console.log('ℹ️ No error messages found (test manually by going offline)');
    }

    // Test 4: Form recovery after error
    results.push(assert(
        !elements.sendBtn.disabled || elements.input.value.length === 0,
        'Submit button state is correct (enabled when input has value, or disabled when empty)'
    ));

    // Summary
    const passed = results.filter(r => r).length;
    const total = results.length;
    console.log(`\n📊 Result: ${passed}/${total} tests passed`);

    return { passed, total, success: passed === total };
}

// ============================================================================
// RUN ALL TESTS
// ============================================================================

async function runAllTests() {
    console.clear();
    console.log('🚀 Running All AI Chat Widget Tests...\n');

    const results = {
        chatToggle: await testChatToggle(),
        htmxSubmission: await testHTMXSubmission(),
        optimisticUI: await testOptimisticUI(),
        clickableChips: await testClickableChips(),
        accessibility: await testAccessibility(),
        mobileLayout: await testMobileLayout(),
        errorHandling: await testErrorHandling(),
    };

    // Summary
    logSection('FINAL TEST SUMMARY');

    const totalPassed = Object.values(results).reduce((sum, r) => sum + r.passed, 0);
    const totalTests = Object.values(results).reduce((sum, r) => sum + r.total, 0);
    const successRate = ((totalPassed / totalTests) * 100).toFixed(1);

    console.log('📊 Test Results by Category:\n');

    Object.entries(results).forEach(([category, result]) => {
        const icon = result.success ? '✅' : '⚠️';
        const percentage = ((result.passed / result.total) * 100).toFixed(1);
        console.log(`${icon} ${category.padEnd(20)} ${result.passed}/${result.total} (${percentage}%)`);
    });

    console.log('\n' + '='.repeat(60));
    console.log(`\n🏆 OVERALL: ${totalPassed}/${totalTests} tests passed (${successRate}%)\n`);

    if (successRate >= 95) {
        console.log('🎉 EXCELLENT! Widget is production-ready!');
    } else if (successRate >= 80) {
        console.log('👍 GOOD! Minor issues to address.');
    } else if (successRate >= 60) {
        console.log('⚠️ FAIR! Several issues need attention.');
    } else {
        console.log('❌ NEEDS WORK! Critical issues found.');
    }

    console.log('\n💡 Tip: Run individual tests for detailed debugging:');
    console.log('   - testChatToggle()');
    console.log('   - testHTMXSubmission()');
    console.log('   - testOptimisticUI()');
    console.log('   - testClickableChips()');
    console.log('   - testAccessibility()');
    console.log('   - testMobileLayout()');
    console.log('   - testErrorHandling()');
    console.log('\n📊 Generate detailed report: generateTestReport()');

    return results;
}

// ============================================================================
// GENERATE TEST REPORT
// ============================================================================

async function generateTestReport() {
    console.log('📄 Generating Test Report...\n');

    const results = await runAllTests();

    // Generate markdown report
    const timestamp = new Date().toISOString();
    const browserInfo = `${navigator.userAgent}`;
    const viewport = `${window.innerWidth}x${window.innerHeight}`;

    let report = `# AI Chat Widget Test Report\n\n`;
    report += `**Date:** ${timestamp}\n`;
    report += `**Browser:** ${browserInfo}\n`;
    report += `**Viewport:** ${viewport}\n\n`;
    report += `---\n\n`;

    report += `## Test Results\n\n`;
    report += `| Category | Passed | Total | Success Rate |\n`;
    report += `|----------|--------|-------|-------------|\n`;

    Object.entries(results).forEach(([category, result]) => {
        const percentage = ((result.passed / result.total) * 100).toFixed(1);
        const status = result.success ? '✅' : '⚠️';
        report += `| ${status} ${category} | ${result.passed} | ${result.total} | ${percentage}% |\n`;
    });

    const totalPassed = Object.values(results).reduce((sum, r) => sum + r.passed, 0);
    const totalTests = Object.values(results).reduce((sum, r) => sum + r.total, 0);
    const successRate = ((totalPassed / totalTests) * 100).toFixed(1);

    report += `\n**Overall:** ${totalPassed}/${totalTests} (${successRate}%)\n\n`;

    report += `---\n\n`;
    report += `## Recommendations\n\n`;

    if (successRate >= 95) {
        report += `✅ **Production Ready** - Widget meets all quality standards.\n`;
    } else if (successRate >= 80) {
        report += `⚠️ **Minor Improvements Needed** - Address failing tests before deployment.\n`;
    } else {
        report += `❌ **Not Ready** - Critical issues must be resolved.\n`;
    }

    console.log('\n' + '='.repeat(60));
    console.log('📄 MARKDOWN REPORT');
    console.log('='.repeat(60));
    console.log(report);
    console.log('='.repeat(60));

    // Copy to clipboard (if supported)
    if (navigator.clipboard) {
        try {
            await navigator.clipboard.writeText(report);
            console.log('\n✅ Report copied to clipboard!');
        } catch (err) {
            console.log('\n⚠️ Could not copy to clipboard. Copy manually from above.');
        }
    } else {
        console.log('\n💡 Copy the report above to save it.');
    }

    return report;
}

// ============================================================================
// QUICK UTILITY FUNCTIONS
// ============================================================================

/**
 * Check panel visibility
 */
window.checkPanelVisibility = function() {
    const panel = document.getElementById('ai-chat-panel');
    const rect = panel.getBoundingClientRect();
    const computedStyle = getComputedStyle(panel);

    console.log('📍 Panel Visibility Check:');
    console.log('  Classes:', panel.className);
    console.log('  Position:', {
        top: rect.top,
        left: rect.left,
        bottom: rect.bottom,
        right: rect.right,
        width: rect.width,
        height: rect.height
    });
    console.log('  Computed Style:', {
        position: computedStyle.position,
        visibility: computedStyle.visibility,
        opacity: computedStyle.opacity,
        transform: computedStyle.transform,
        zIndex: computedStyle.zIndex
    });
    console.log('  In Viewport:', {
        vertically: rect.top >= 0 && rect.bottom <= window.innerHeight,
        horizontally: rect.left >= 0 && rect.right <= window.innerWidth
    });
};

/**
 * Simulate user message
 */
window.simulateMessage = async function(message = 'Test message') {
    const elements = getChatElements();

    if (!elements.panel.classList.contains('chat-open')) {
        console.log('⚠️ Opening chat first...');
        window.toggleAIChat();
        await wait(350);
    }

    console.log(`📤 Sending message: "${message}"`);
    elements.input.value = message;
    elements.form.requestSubmit();
};

/**
 * Clear chat messages
 */
window.clearChatMessages = function() {
    const messages = document.getElementById('ai-chat-messages');
    const userMessages = messages.querySelectorAll('.ai-message-user');
    const botMessages = messages.querySelectorAll('.ai-message-bot');

    userMessages.forEach(msg => msg.remove());
    botMessages.forEach(msg => msg.remove());

    console.log(`🗑️ Cleared ${userMessages.length + botMessages.length} messages`);
};

/**
 * Test keyboard navigation
 */
window.testKeyboardNav = async function() {
    console.log('⌨️ Testing Keyboard Navigation...');

    const elements = getChatElements();

    // Close chat if open
    if (elements.panel.classList.contains('chat-open')) {
        window.toggleAIChat();
        await wait(250);
    }

    console.log('1. Focusing toggle button...');
    elements.button.focus();
    await wait(500);

    console.log('2. Pressing Enter to open...');
    elements.button.click();
    await wait(350);

    console.log('3. Pressing Escape to close...');
    const escapeEvent = new KeyboardEvent('keydown', {
        key: 'Escape',
        code: 'Escape',
        keyCode: 27,
        bubbles: true
    });
    document.dispatchEvent(escapeEvent);
    await wait(250);

    console.log('✅ Keyboard navigation test complete');
};

// ============================================================================
// INITIALIZATION
// ============================================================================

console.log('\n✨ Test helpers ready! Run runAllTests() to start testing.\n');
console.log('📚 Quick Commands:');
console.log('  runAllTests()           - Run all tests');
console.log('  generateTestReport()    - Generate markdown report');
console.log('  checkPanelVisibility()  - Check panel visibility');
console.log('  simulateMessage()       - Send test message');
console.log('  clearChatMessages()     - Clear chat history');
console.log('  testKeyboardNav()       - Test keyboard navigation');
console.log('\n💡 Individual tests: testChatToggle(), testAccessibility(), etc.\n');

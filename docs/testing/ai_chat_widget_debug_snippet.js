/**
 * AI Chat Widget - Debug Snippet
 *
 * Paste this into browser console (F12) to diagnose issues
 * with the AI chat widget.
 *
 * Usage:
 *   1. Open any authenticated page in OBCMS
 *   2. Press F12 to open browser console
 *   3. Paste this entire code
 *   4. Press Enter
 *   5. Review output
 */

(function() {
    'use strict';

    console.log('%c=== AI Chat Widget Debug Report ===', 'font-weight: bold; font-size: 16px; color: #10b981;');
    console.log('Generated:', new Date().toLocaleString());
    console.log('');

    // Check if user is authenticated
    const isAuthenticated = document.querySelector('#ai-chat-widget') !== null;
    console.log('%c1. Authentication Check', 'font-weight: bold; color: #3b82f6;');
    console.log('   User authenticated:', isAuthenticated ? '✅ YES' : '❌ NO (widget hidden for guests)');
    if (!isAuthenticated) {
        console.log('%c   → Widget only shows for logged-in users', 'color: #f59e0b;');
        console.log('   → Please login and reload this page');
        return;
    }
    console.log('');

    // Check DOM elements
    console.log('%c2. DOM Elements Check', 'font-weight: bold; color: #3b82f6;');

    const elements = {
        'Widget Container': document.getElementById('ai-chat-widget'),
        'Toggle Button': document.getElementById('ai-chat-toggle-btn'),
        'Chat Icon': document.getElementById('ai-chat-icon'),
        'Chat Panel': document.getElementById('ai-chat-panel'),
        'Chat Messages': document.getElementById('ai-chat-messages'),
        'Chat Backdrop': document.getElementById('ai-chat-backdrop'),
    };

    Object.entries(elements).forEach(([name, element]) => {
        if (element) {
            console.log(`   ✅ ${name}:`, element);
        } else {
            console.log(`   ❌ ${name}: NOT FOUND`);
        }
    });
    console.log('');

    // Check JavaScript function
    console.log('%c3. JavaScript Function Check', 'font-weight: bold; color: #3b82f6;');
    if (typeof window.toggleAIChat === 'function') {
        console.log('   ✅ toggleAIChat() function exists');
    } else {
        console.log('   ❌ toggleAIChat() function NOT FOUND');
        console.log('   → Check if component file is loaded correctly');
    }
    console.log('');

    // Check current state
    console.log('%c4. Current State', 'font-weight: bold; color: #3b82f6;');
    const panel = document.getElementById('ai-chat-panel');
    const button = document.getElementById('ai-chat-toggle-btn');

    if (panel && button) {
        const isOpen = panel.classList.contains('chat-open');
        console.log('   Panel state:', isOpen ? '🟢 OPEN' : '🔴 CLOSED');
        console.log('   Button aria-expanded:', button.getAttribute('aria-expanded'));
        console.log('   Panel aria-hidden:', panel.getAttribute('aria-hidden'));
        console.log('   Panel classes:', panel.className);
        console.log('   Panel opacity:', window.getComputedStyle(panel).opacity);
        console.log('   Panel pointer-events:', window.getComputedStyle(panel).pointerEvents);
    }
    console.log('');

    // Check CSS styles
    console.log('%c5. CSS Styles Check', 'font-weight: bold; color: #3b82f6;');
    if (panel) {
        const styles = window.getComputedStyle(panel);
        console.log('   Position:', styles.position);
        console.log('   Z-index:', styles.zIndex);
        console.log('   Width:', styles.width);
        console.log('   Height:', styles.height);
        console.log('   Transform:', styles.transform);
        console.log('   Transition:', styles.transition);
        console.log('   Display:', styles.display);
    }
    console.log('');

    // Check button styles
    console.log('%c6. Button Styles Check', 'font-weight: bold; color: #3b82f6;');
    if (button) {
        const btnStyles = window.getComputedStyle(button);
        console.log('   Width:', btnStyles.width);
        console.log('   Height:', btnStyles.height);
        console.log('   Background:', btnStyles.background.substring(0, 100) + '...');
        console.log('   Z-index:', btnStyles.zIndex);
        console.log('   Cursor:', btnStyles.cursor);
    }
    console.log('');

    // Check viewport size
    console.log('%c7. Viewport Check', 'font-weight: bold; color: #3b82f6;');
    const width = window.innerWidth;
    const height = window.innerHeight;
    const isMobile = width < 640;
    console.log('   Viewport size:', `${width}px × ${height}px`);
    console.log('   Device type:', isMobile ? '📱 MOBILE (< 640px)' : '💻 DESKTOP (≥ 640px)');
    console.log('   Expected layout:', isMobile ? 'Bottom sheet with backdrop' : 'Panel above button');
    console.log('');

    // Check backdrop (mobile)
    if (isMobile) {
        console.log('%c8. Mobile Backdrop Check', 'font-weight: bold; color: #3b82f6;');
        const backdrop = document.getElementById('ai-chat-backdrop');
        if (backdrop) {
            const backdropStyles = window.getComputedStyle(backdrop);
            console.log('   ✅ Backdrop exists');
            console.log('   Hidden class:', backdrop.classList.contains('hidden') ? 'YES' : 'NO');
            console.log('   Opacity:', backdropStyles.opacity);
            console.log('   Pointer events:', backdropStyles.pointerEvents);
        } else {
            console.log('   ❌ Backdrop NOT FOUND');
        }
        console.log('');
    }

    // Check for JavaScript errors
    console.log('%c9. Error Check', 'font-weight: bold; color: #3b82f6;');
    console.log('   Check console for any red error messages above this report');
    console.log('');

    // Interactive tests
    console.log('%c10. Interactive Tests', 'font-weight: bold; color: #3b82f6;');
    console.log('   Run these commands to test manually:');
    console.log('');
    console.log('   %cwindow.toggleAIChat()%c - Toggle chat open/close', 'background: #f3f4f6; padding: 2px 6px; border-radius: 4px; font-family: monospace;', '');
    console.log('');
    console.log('   %cdocument.getElementById("ai-chat-panel").classList.contains("chat-open")%c - Check if open', 'background: #f3f4f6; padding: 2px 6px; border-radius: 4px; font-family: monospace;', '');
    console.log('');

    // Performance test
    console.log('%c11. Performance Test', 'font-weight: bold; color: #3b82f6;');
    console.log('   Run this to test toggle performance:');
    console.log('');
    console.log('   %c' + `
const startTime = performance.now();
window.toggleAIChat();
setTimeout(() => {
    const endTime = performance.now();
    console.log('Toggle duration:', (endTime - startTime).toFixed(2) + 'ms');
    window.toggleAIChat(); // Close again
}, 350);
    `.trim(), 'background: #f3f4f6; padding: 8px; border-radius: 4px; font-family: monospace; display: block; white-space: pre;', '');
    console.log('');

    // Summary
    console.log('%c=== Summary ===', 'font-weight: bold; font-size: 16px; color: #10b981;');

    const allElementsExist = Object.values(elements).every(el => el !== null);
    const functionExists = typeof window.toggleAIChat === 'function';

    if (allElementsExist && functionExists) {
        console.log('%c✅ All checks passed! Widget should work correctly.', 'color: #10b981; font-weight: bold;');
        console.log('');
        console.log('Try clicking the emerald button in the bottom-right corner.');
        console.log('Or run: %cwindow.toggleAIChat()%c', 'background: #f3f4f6; padding: 2px 6px; border-radius: 4px; font-family: monospace;', '');
    } else {
        console.log('%c❌ Issues detected:', 'color: #ef4444; font-weight: bold;');
        if (!allElementsExist) {
            console.log('   - Some DOM elements are missing');
            console.log('   - Check if component file is properly loaded');
        }
        if (!functionExists) {
            console.log('   - toggleAIChat() function not found');
            console.log('   - Check browser console for JavaScript errors');
        }
        console.log('');
        console.log('%cRecommended Actions:', 'font-weight: bold; color: #f59e0b;');
        console.log('1. Verify component file exists: src/templates/components/ai_chat_widget.html');
        console.log('2. Check base.html includes the component: {% include "components/ai_chat_widget.html" %}');
        console.log('3. Hard refresh the page (Ctrl+Shift+R or Cmd+Shift+R)');
        console.log('4. Check Django server logs for template errors');
    }
    console.log('');

    // Help text
    console.log('%c=== Need Help? ===', 'font-weight: bold; font-size: 14px; color: #8b5cf6;');
    console.log('📚 Documentation: docs/ui/AI_CHAT_WIDGET_QUICK_REFERENCE.md');
    console.log('🧪 Testing Guide: docs/testing/AI_CHAT_WIDGET_TESTING_GUIDE.md');
    console.log('📝 Full Summary: AI_CHAT_WIDGET_FIX_COMPLETE.md');
    console.log('');
    console.log('%cHappy debugging! 🐛', 'color: #10b981; font-weight: bold;');

})();

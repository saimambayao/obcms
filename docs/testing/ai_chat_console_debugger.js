/**
 * AI Chat Position Debugger
 *
 * PURPOSE: Diagnose AI chat widget positioning issues
 * USAGE: Copy-paste this entire script into browser console
 *
 * WHAT IT DOES:
 * - Analyzes widget, button, and panel positioning
 * - Checks viewport visibility
 * - Provides actionable recommendations
 * - Suggests fixes for common issues
 *
 * WHEN TO USE:
 * - Panel not visible when opened
 * - Widget in wrong position
 * - Panel cut off or extending beyond viewport
 * - Z-index conflicts with other elements
 */

(function() {
    console.log('🔍 AI CHAT POSITION DEBUGGER');
    console.log('================================');
    console.log('Starting diagnostic...\n');

    // Get elements
    const widget = document.getElementById('ai-chat-widget');
    const button = document.getElementById('ai-chat-toggle-btn');
    const panel = document.getElementById('ai-chat-panel');

    // Check if elements exist
    if (!widget || !button || !panel) {
        console.error('❌ CRITICAL: Elements not found');
        console.error('   Widget exists:', !!widget);
        console.error('   Button exists:', !!button);
        console.error('   Panel exists:', !!panel);
        console.error('\n💡 FIX: Ensure ai_chat_widget.html is included in base template');
        return;
    }

    console.log('✅ All elements found\n');

    // 1. Widget Container Analysis
    const widgetRect = widget.getBoundingClientRect();
    const widgetStyle = window.getComputedStyle(widget);

    console.log('1️⃣ WIDGET CONTAINER ANALYSIS');
    console.log('─────────────────────────────');
    console.log('Position:', widgetStyle.position,
        widgetStyle.position === 'fixed' ? '✅' : '❌ Should be "fixed"');
    console.log('Bottom:', widgetStyle.bottom);
    console.log('Right:', widgetStyle.right);
    console.log('Z-Index:', widgetStyle.zIndex);
    console.log('Dimensions:', {
        width: Math.round(widgetRect.width) + 'px',
        height: Math.round(widgetRect.height) + 'px'
    });
    console.log('Viewport Position:', {
        top: Math.round(widgetRect.top) + 'px',
        left: Math.round(widgetRect.left) + 'px',
        bottom: Math.round(window.innerHeight - widgetRect.bottom) + 'px from bottom',
        right: Math.round(window.innerWidth - widgetRect.right) + 'px from right'
    });

    // 2. Toggle Button Analysis
    const buttonRect = button.getBoundingClientRect();
    const buttonStyle = window.getComputedStyle(button);

    console.log('\n2️⃣ TOGGLE BUTTON ANALYSIS');
    console.log('─────────────────────────────');
    console.log('Size:', Math.round(buttonRect.width) + 'x' + Math.round(buttonRect.height) + 'px');
    console.log('Is Active:', button.classList.contains('chat-active') ? '✅ Open' : '❌ Closed');
    console.log('Aria Expanded:', button.getAttribute('aria-expanded'));

    // 3. Chat Panel Analysis
    const panelRect = panel.getBoundingClientRect();
    const panelStyle = window.getComputedStyle(panel);

    console.log('\n3️⃣ CHAT PANEL ANALYSIS');
    console.log('─────────────────────────────');
    console.log('Position:', panelStyle.position);
    console.log('Visibility:', panelStyle.visibility);
    console.log('Opacity:', panelStyle.opacity);
    console.log('Classes:', panel.className);
    console.log('Has "chat-open"?', panel.classList.contains('chat-open') ? '✅ YES' : '❌ NO');

    console.log('\nPositioning Properties:');
    console.log('  Top:', panelStyle.top);
    console.log('  Bottom:', panelStyle.bottom);
    console.log('  Left:', panelStyle.left);
    console.log('  Right:', panelStyle.right);

    console.log('\nDimensions:');
    console.log('  Width:', panelStyle.width);
    console.log('  Height:', panelStyle.height);
    console.log('  Max-Height:', panelStyle.maxHeight);

    console.log('\nVisual Properties:');
    console.log('  Transform:', panelStyle.transform);
    console.log('  Z-Index:', panelStyle.zIndex);
    console.log('  Pointer Events:', panelStyle.pointerEvents);

    console.log('\nBounding Rectangle:');
    console.log('  Top:', Math.round(panelRect.top) + 'px');
    console.log('  Bottom:', Math.round(panelRect.bottom) + 'px');
    console.log('  Left:', Math.round(panelRect.left) + 'px');
    console.log('  Right:', Math.round(panelRect.right) + 'px');
    console.log('  Width:', Math.round(panelRect.width) + 'px');
    console.log('  Height:', Math.round(panelRect.height) + 'px');

    // 4. Viewport Information
    const viewportHeight = window.innerHeight;
    const viewportWidth = window.innerWidth;
    const isMobile = viewportWidth < 640;

    console.log('\n4️⃣ VIEWPORT INFORMATION');
    console.log('─────────────────────────────');
    console.log('Width:', viewportWidth + 'px');
    console.log('Height:', viewportHeight + 'px');
    console.log('Device Type:', isMobile ? 'Mobile (< 640px)' : 'Desktop (≥ 640px)');
    console.log('Orientation:', window.innerWidth > window.innerHeight ? 'Landscape' : 'Portrait');

    // 5. Visibility Check
    const isTopVisible = panelRect.top >= 0;
    const isBottomVisible = panelRect.bottom <= viewportHeight;
    const isLeftVisible = panelRect.left >= 0;
    const isRightVisible = panelRect.right <= viewportWidth;
    const isFullyVisible = isTopVisible && isBottomVisible && isLeftVisible && isRightVisible;

    console.log('\n5️⃣ VISIBILITY CHECK');
    console.log('─────────────────────────────');
    console.log('Panel Fully Visible:', isFullyVisible ? '✅ YES' : '❌ NO');

    if (!isFullyVisible) {
        console.log('\nVisibility Issues:');
        if (!isTopVisible) {
            console.error('  ❌ TOP edge is ABOVE viewport');
            console.error('     Panel top:', Math.round(panelRect.top) + 'px');
            console.error('     Viewport top:', '0px');
            console.error('     Overflow:', Math.round(Math.abs(panelRect.top)) + 'px above viewport');
        }
        if (!isBottomVisible) {
            console.error('  ❌ BOTTOM edge is BELOW viewport');
            console.error('     Panel bottom:', Math.round(panelRect.bottom) + 'px');
            console.error('     Viewport bottom:', viewportHeight + 'px');
            console.error('     Overflow:', Math.round(panelRect.bottom - viewportHeight) + 'px below viewport');
        }
        if (!isLeftVisible) {
            console.error('  ❌ LEFT edge is outside viewport');
            console.error('     Panel left:', Math.round(panelRect.left) + 'px');
        }
        if (!isRightVisible) {
            console.error('  ❌ RIGHT edge is outside viewport');
            console.error('     Panel right:', Math.round(panelRect.right) + 'px');
            console.error('     Viewport right:', viewportWidth + 'px');
        }
    } else {
        console.log('  ✅ Top edge visible');
        console.log('  ✅ Bottom edge visible');
        console.log('  ✅ Left edge visible');
        console.log('  ✅ Right edge visible');
    }

    // 6. Z-Index Hierarchy Check
    console.log('\n6️⃣ Z-INDEX HIERARCHY');
    console.log('─────────────────────────────');

    const widgetZIndex = parseInt(widgetStyle.zIndex) || 0;
    const panelZIndex = parseInt(panelStyle.zIndex) || 0;

    console.log('Widget z-index:', widgetZIndex, widgetZIndex >= 9999 ? '✅' : '⚠️ Should be 9999');
    console.log('Panel z-index:', panelZIndex, panelZIndex >= 9999 ? '✅' : '⚠️ Should be 9999');

    // Check for conflicting elements
    const highZIndexElements = [];
    document.querySelectorAll('*').forEach(el => {
        const z = parseInt(window.getComputedStyle(el).zIndex);
        if (z > widgetZIndex && z !== panelZIndex) {
            highZIndexElements.push({
                element: el.tagName + (el.id ? '#' + el.id : '') + (el.className ? '.' + el.className.split(' ').join('.') : ''),
                zIndex: z
            });
        }
    });

    if (highZIndexElements.length > 0) {
        console.warn('\n⚠️ Elements with HIGHER z-index found (may cover chat):');
        highZIndexElements.slice(0, 5).forEach(item => {
            console.warn('  -', item.element, '(z-index:', item.zIndex + ')');
        });
        if (highZIndexElements.length > 5) {
            console.warn('  ... and', highZIndexElements.length - 5, 'more');
        }
    } else {
        console.log('  ✅ No z-index conflicts detected');
    }

    // 7. Recommendations
    console.log('\n7️⃣ RECOMMENDATIONS');
    console.log('─────────────────────────────');

    let hasIssues = false;

    // Widget position check
    if (widgetStyle.position !== 'fixed') {
        console.error('❌ ISSUE: Widget is not fixed position');
        console.log('   💡 FIX: Run this command:');
        console.log('   document.getElementById("ai-chat-widget").style.position = "fixed";');
        hasIssues = true;
    }

    // Panel visibility check
    if (panelStyle.visibility === 'hidden' && !panel.classList.contains('chat-open')) {
        console.warn('⚠️ Panel is hidden (expected when closed)');
        console.log('   💡 To test: Run toggleAIChat() to open panel');
    }

    // Panel above viewport
    if (panelRect.top < 0) {
        console.error('❌ ISSUE: Panel is ABOVE viewport');
        console.log('   💡 FIX: Adjust bottom positioning');
        console.log('   document.getElementById("ai-chat-panel").style.bottom = "88px";');
        hasIssues = true;
    }

    // Panel too tall
    if (panelRect.bottom > viewportHeight) {
        console.error('❌ ISSUE: Panel is TOO TALL or BELOW viewport');
        console.log('   💡 FIX: Reduce max-height');
        console.log('   document.getElementById("ai-chat-panel").style.maxHeight = "calc(100vh - 140px)";');
        hasIssues = true;
    }

    // Panel opacity
    if (panelStyle.opacity === '0' && panel.classList.contains('chat-open')) {
        console.error('❌ ISSUE: Panel is open but opacity is 0');
        console.log('   💡 FIX: Force opacity');
        console.log('   document.getElementById("ai-chat-panel").style.opacity = "1";');
        hasIssues = true;
    }

    // Mobile-specific checks
    if (isMobile) {
        if (panelStyle.position !== 'fixed') {
            console.error('❌ ISSUE: Panel should be fixed on mobile');
            console.log('   💡 FIX: Panel should use position: fixed on mobile');
            hasIssues = true;
        }
        if (panelRect.width < viewportWidth - 10) {
            console.error('❌ ISSUE: Panel is not full-width on mobile');
            console.log('   💡 FIX: Panel should be full-width (100vw)');
            hasIssues = true;
        }
    }

    // Z-index issues
    if (widgetZIndex < 9999) {
        console.error('❌ ISSUE: Widget z-index too low');
        console.log('   💡 FIX: Increase z-index');
        console.log('   document.getElementById("ai-chat-widget").style.zIndex = "9999";');
        hasIssues = true;
    }

    if (!hasIssues && isFullyVisible) {
        console.log('✅ No positioning issues detected!');
        console.log('   Panel is correctly positioned and visible');
    }

    // 8. Quick Actions
    console.log('\n8️⃣ QUICK ACTIONS');
    console.log('─────────────────────────────');
    console.log('Run these commands in console:\n');

    console.log('👁️ Add visual debug overlay:');
    console.log('   addVisualDebug()');

    console.log('\n🔄 Toggle chat open/closed:');
    console.log('   toggleAIChat()');

    console.log('\n🔧 Apply quick fix (force visibility):');
    console.log('   applyQuickFix()');

    console.log('\n🔄 Complete reset:');
    console.log('   resetChatPosition()');

    console.log('\n🐛 Enable debug mode (red/green borders):');
    console.log('   document.getElementById("ai-chat-widget").classList.add("debug-chat")');

    // Summary
    console.log('\n================================');
    console.log('📊 DIAGNOSTIC SUMMARY');
    console.log('================================');
    console.log('Widget Position:', widgetStyle.position === 'fixed' ? '✅ Correct' : '❌ Incorrect');
    console.log('Panel Visibility:', isFullyVisible ? '✅ Visible' : '❌ Not Visible');
    console.log('Z-Index:', widgetZIndex >= 9999 ? '✅ Correct' : '❌ Too Low');
    console.log('Mobile Layout:', isMobile ? (panelRect.width >= viewportWidth - 10 ? '✅ Full Width' : '❌ Not Full Width') : 'N/A (Desktop)');
    console.log('Issues Found:', hasIssues ? '❌ YES - See recommendations above' : '✅ NONE');
    console.log('================================');
    console.log('✅ Diagnostic complete\n');

    // Define global helper functions
    window.applyQuickFix = function() {
        console.log('🔧 Applying quick fix...');
        const p = document.getElementById('ai-chat-panel');
        p.style.cssText = `
            position: fixed !important;
            bottom: 88px !important;
            right: 24px !important;
            max-height: calc(100vh - 140px) !important;
            opacity: 1 !important;
            visibility: visible !important;
            pointer-events: auto !important;
            transform: scale(1) !important;
            border: 3px solid green !important;
        `;
        p.classList.add('chat-open');
        console.log('✅ Quick fix applied (green border = active)');
    };

    window.resetChatPosition = function() {
        console.log('🔄 Resetting to default position...');
        const w = document.getElementById('ai-chat-widget');
        const p = document.getElementById('ai-chat-panel');
        const b = document.getElementById('ai-chat-toggle-btn');

        w.style.cssText = `
            position: fixed;
            bottom: 1.5rem;
            right: 1.5rem;
            z-index: 9999;
        `;

        p.style.cssText = `
            position: fixed;
            bottom: 88px;
            right: 24px;
            max-height: calc(100vh - 140px);
        `;
        p.classList.remove('chat-open');

        b.classList.remove('chat-active');
        b.setAttribute('aria-expanded', 'false');

        console.log('✅ Reset complete');
    };

    console.log('💡 TIP: Helper functions are now available globally');
    console.log('   - applyQuickFix()');
    console.log('   - resetChatPosition()');
    console.log('   - addVisualDebug() (if visual debugger loaded)');

})();

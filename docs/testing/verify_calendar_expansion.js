/**
 * Calendar Width Expansion Verification Script
 *
 * Usage:
 * 1. Open the Advanced Modern Calendar page
 * 2. Open browser DevTools (F12)
 * 3. Paste this entire script into the Console tab
 * 4. Press Enter to run
 *
 * The script will:
 * - Check initial state
 * - Test toggle functionality
 * - Verify calendar resizing
 * - Provide detailed diagnostics
 */

(async function verifyCalendarWidthExpansion() {
    'use strict';

    console.clear();
    console.log('%c=== CALENDAR WIDTH EXPANSION VERIFICATION ===', 'font-size: 18px; font-weight: bold; color: #3b82f6;');
    console.log('%cDate: ' + new Date().toLocaleString(), 'color: #64748b;');
    console.log('%cViewport: ' + window.innerWidth + 'x' + window.innerHeight, 'color: #64748b;');
    console.log('');

    // Test utilities
    let passCount = 0;
    let failCount = 0;
    let warnCount = 0;

    function pass(message) {
        console.log('%c✅ PASS', 'color: #10b981; font-weight: bold;', message);
        passCount++;
    }

    function fail(message, details) {
        console.error('%c❌ FAIL', 'color: #ef4444; font-weight: bold;', message);
        if (details) console.error('   Details:', details);
        failCount++;
    }

    function warn(message, details) {
        console.warn('%c⚠️  WARN', 'color: #f59e0b; font-weight: bold;', message);
        if (details) console.warn('   Details:', details);
        warnCount++;
    }

    function info(message) {
        console.log('%c📋 INFO', 'color: #3b82f6; font-weight: bold;', message);
    }

    function section(title) {
        console.log('');
        console.log('%c' + title, 'font-size: 14px; font-weight: bold; color: #0f172a; background: #e0f2fe; padding: 4px 8px; border-left: 4px solid #3b82f6;');
        console.log('');
    }

    // Helper to wait for animations
    function wait(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    // Get DOM elements
    const container = document.querySelector('.calendar-container');
    const toggleBtn = document.getElementById('toggleSidebarBtn');
    const icon = document.getElementById('sidebarToggleIcon');
    const sidebar = document.getElementById('calendarSidebar');
    const calendar = document.querySelector('#calendar');
    const calendarMain = document.querySelector('.calendar-main');

    // Check if elements exist
    section('DOM Element Check');

    if (!container) {
        fail('Calendar container not found', 'Missing element: .calendar-container');
        return;
    } else {
        pass('Calendar container found');
    }

    if (!toggleBtn) {
        fail('Toggle button not found', 'Missing element: #toggleSidebarBtn');
        return;
    } else {
        pass('Toggle button found');
    }

    if (!icon) {
        fail('Toggle icon not found', 'Missing element: #sidebarToggleIcon');
        return;
    } else {
        pass('Toggle icon found');
    }

    if (!sidebar) {
        fail('Sidebar not found', 'Missing element: #calendarSidebar');
        return;
    } else {
        pass('Sidebar found');
    }

    if (!calendar) {
        fail('Calendar element not found', 'Missing element: #calendar');
        return;
    } else {
        pass('Calendar element found');
    }

    // Detect viewport mode
    const isMobile = window.innerWidth < 1024;
    const viewportMode = isMobile ? 'MOBILE' : 'DESKTOP';

    section('Viewport Mode Detection');
    info('Viewport width: ' + window.innerWidth + 'px');
    info('Mode: ' + viewportMode + ' (' + (isMobile ? '< 1024px' : '≥ 1024px') + ')');

    // Test 1: Initial State
    section('Test 1: Initial State');

    const initialGridColumns = getComputedStyle(container).gridTemplateColumns;
    info('Grid columns: ' + initialGridColumns);

    if (!isMobile) {
        // Desktop initial state
        const sidebarCollapsed = container.classList.contains('sidebar-collapsed');
        const hasChevronLeft = icon.classList.contains('fa-chevron-left');
        const hasChevronRight = icon.classList.contains('fa-chevron-right');
        const hasBars = icon.classList.contains('fa-bars');

        if (sidebarCollapsed) {
            warn('Sidebar is collapsed on initial load', 'Expected: visible by default');
        } else {
            pass('Sidebar is visible (default state)');
        }

        if (hasChevronLeft) {
            pass('Icon shows chevron-left (←) - correct for visible sidebar');
        } else if (hasChevronRight) {
            warn('Icon shows chevron-right (→)', 'Expected: chevron-left for visible sidebar');
        } else if (hasBars) {
            fail('Icon shows bars (☰) on desktop', {
                expected: 'fa-chevron-left',
                actual: 'fa-bars',
                context: 'Desktop should show chevrons, not bars'
            });
        } else {
            fail('Icon has unknown state', icon.className);
        }

        if (initialGridColumns.startsWith('280px')) {
            pass('Grid shows sidebar column (280px)');
        } else {
            fail('Grid does not show sidebar column', {
                expected: '280px 1fr 0px',
                actual: initialGridColumns
            });
        }
    } else {
        // Mobile initial state
        const sidebarOpen = sidebar.classList.contains('open');
        const hasBars = icon.classList.contains('fa-bars');
        const hasTimes = icon.classList.contains('fa-times');

        if (sidebarOpen) {
            warn('Sidebar is open on initial load (mobile)', 'Expected: closed by default');
        } else {
            pass('Sidebar is closed (default state)');
        }

        if (hasBars) {
            pass('Icon shows bars (☰) - correct for closed sidebar');
        } else if (hasTimes) {
            warn('Icon shows times (×)', 'Expected: bars for closed sidebar');
        } else {
            fail('Icon has unknown state on mobile', icon.className);
        }

        if (initialGridColumns.startsWith('0px')) {
            pass('Grid hides sidebar column (mobile layout)');
        } else {
            warn('Grid shows sidebar column on mobile', initialGridColumns);
        }
    }

    // Test 2: Calendar Dimensions
    section('Test 2: Calendar Dimensions');

    const initialCalendarWidth = calendar.offsetWidth;
    const initialCalendarHeight = calendar.offsetHeight;
    const containerWidth = container.offsetWidth;

    info('Calendar width: ' + initialCalendarWidth + 'px');
    info('Calendar height: ' + initialCalendarHeight + 'px');
    info('Container width: ' + containerWidth + 'px');

    if (initialCalendarHeight > 0) {
        pass('Calendar has height (' + initialCalendarHeight + 'px)');
    } else {
        fail('Calendar has no height', {
            calendarHeight: initialCalendarHeight,
            containerHeight: container.offsetHeight
        });
    }

    if (!isMobile) {
        const expectedWidth = containerWidth - 280; // Approximate (sidebar width)
        const widthDiff = Math.abs(initialCalendarWidth - expectedWidth);

        if (widthDiff < 100) {
            pass('Calendar width is correct (~' + expectedWidth + 'px)');
        } else {
            warn('Calendar width seems off', {
                expected: expectedWidth + 'px (approx)',
                actual: initialCalendarWidth + 'px',
                difference: widthDiff + 'px'
            });
        }
    }

    // Test 3: Toggle Functionality
    section('Test 3: Toggle Functionality');

    info('Clicking toggle button...');
    toggleBtn.click();

    await wait(50); // Wait for immediate DOM updates

    if (!isMobile) {
        // Desktop toggle test
        const sidebarCollapsedAfter = container.classList.contains('sidebar-collapsed');
        const hasChevronRight = icon.classList.contains('fa-chevron-right');

        if (sidebarCollapsedAfter) {
            pass('Sidebar collapsed class added');
        } else {
            fail('Sidebar collapsed class not added', container.className);
        }

        if (hasChevronRight) {
            pass('Icon changed to chevron-right (→)');
        } else {
            fail('Icon did not change to chevron-right', icon.className);
        }

        const gridColumnsAfter = getComputedStyle(container).gridTemplateColumns;
        info('Grid columns after toggle: ' + gridColumnsAfter);

        if (gridColumnsAfter.startsWith('0px')) {
            pass('Grid columns updated to hide sidebar');
        } else {
            fail('Grid columns did not update', {
                expected: '0px 1fr 0px',
                actual: gridColumnsAfter
            });
        }
    } else {
        // Mobile toggle test
        const sidebarOpenAfter = sidebar.classList.contains('open');
        const hasTimes = icon.classList.contains('fa-times');

        if (sidebarOpenAfter) {
            pass('Sidebar opened (mobile overlay)');
        } else {
            fail('Sidebar did not open', sidebar.className);
        }

        if (hasTimes) {
            pass('Icon changed to times (×)');
        } else {
            fail('Icon did not change to times', icon.className);
        }
    }

    // Test 4: Calendar Resize (Desktop only)
    if (!isMobile) {
        section('Test 4: Calendar Resize (Desktop)');

        info('Waiting 400ms for resize to complete...');
        await wait(400);

        const calendarWidthAfter = calendar.offsetWidth;
        const widthIncrease = calendarWidthAfter - initialCalendarWidth;

        info('Calendar width before: ' + initialCalendarWidth + 'px');
        info('Calendar width after: ' + calendarWidthAfter + 'px');
        info('Width increase: ' + widthIncrease + 'px');

        if (widthIncrease > 200) {
            pass('Calendar expanded significantly (+' + widthIncrease + 'px)');
        } else if (widthIncrease > 50) {
            warn('Calendar expanded slightly (+' + widthIncrease + 'px)', 'Expected: +280px approximately');
        } else {
            fail('Calendar did not expand', {
                before: initialCalendarWidth + 'px',
                after: calendarWidthAfter + 'px',
                increase: widthIncrease + 'px'
            });
        }

        // Check if calendar is close to full width
        const containerWidthNow = container.offsetWidth;
        const widthUtilization = (calendarWidthAfter / containerWidthNow) * 100;

        info('Width utilization: ' + widthUtilization.toFixed(1) + '%');

        if (widthUtilization > 95) {
            pass('Calendar uses full container width (' + widthUtilization.toFixed(1) + '%)');
        } else if (widthUtilization > 85) {
            warn('Calendar uses most of container width (' + widthUtilization.toFixed(1) + '%)');
        } else {
            fail('Calendar not using full width', widthUtilization.toFixed(1) + '% utilization');
        }
    } else {
        section('Test 4: Calendar Resize (Skipped on Mobile)');
        info('Mobile viewport: calendar width should remain unchanged');
    }

    // Test 5: Toggle Back (Restore Initial State)
    section('Test 5: Toggle Back (Restore)');

    info('Clicking toggle button again...');
    toggleBtn.click();

    await wait(50);

    if (!isMobile) {
        const sidebarCollapsedAfterRestore = container.classList.contains('sidebar-collapsed');
        const hasChevronLeft = icon.classList.contains('fa-chevron-left');

        if (!sidebarCollapsedAfterRestore) {
            pass('Sidebar collapsed class removed');
        } else {
            fail('Sidebar still collapsed', container.className);
        }

        if (hasChevronLeft) {
            pass('Icon changed back to chevron-left (←)');
        } else {
            fail('Icon did not change back', icon.className);
        }

        await wait(400);

        const calendarWidthRestored = calendar.offsetWidth;
        const widthDiff = Math.abs(calendarWidthRestored - initialCalendarWidth);

        info('Calendar width restored: ' + calendarWidthRestored + 'px (diff: ' + widthDiff + 'px)');

        if (widthDiff < 10) {
            pass('Calendar width restored to initial (' + calendarWidthRestored + 'px)');
        } else {
            warn('Calendar width not exactly restored', {
                initial: initialCalendarWidth + 'px',
                restored: calendarWidthRestored + 'px',
                difference: widthDiff + 'px'
            });
        }
    } else {
        const sidebarOpenAfterRestore = sidebar.classList.contains('open');
        const hasBars = icon.classList.contains('fa-bars');

        if (!sidebarOpenAfterRestore) {
            pass('Sidebar closed');
        } else {
            fail('Sidebar still open', sidebar.className);
        }

        if (hasBars) {
            pass('Icon changed back to bars (☰)');
        } else {
            fail('Icon did not change back', icon.className);
        }
    }

    // Test 6: Check for JavaScript Errors
    section('Test 6: JavaScript Integration');

    if (typeof window.calendar !== 'undefined') {
        pass('FullCalendar instance exists (window.calendar)');

        if (typeof window.calendar.updateSize === 'function') {
            pass('calendar.updateSize() method exists');
        } else {
            fail('calendar.updateSize() method not found');
        }
    } else {
        warn('FullCalendar instance not accessible via window.calendar', 'May be scoped within IIFE');
    }

    // Check for FullCalendar DOM elements
    const fcElement = document.querySelector('.fc');
    if (fcElement) {
        pass('FullCalendar rendered (.fc element exists)');
    } else {
        fail('FullCalendar not rendered', 'Missing .fc element');
    }

    // Test 7: Accessibility
    section('Test 7: Accessibility');

    const ariaLabel = toggleBtn.getAttribute('aria-label');
    if (ariaLabel) {
        pass('Toggle button has aria-label: "' + ariaLabel + '"');
    } else {
        warn('Toggle button missing aria-label');
    }

    // Summary
    section('Test Summary');

    console.log('');
    console.log('%c📊 RESULTS', 'font-size: 16px; font-weight: bold; color: #0f172a;');
    console.log('%c  Pass:  ' + passCount, 'color: #10b981; font-weight: bold;');
    console.log('%c  Fail:  ' + failCount, 'color: #ef4444; font-weight: bold;');
    console.log('%c  Warn:  ' + warnCount, 'color: #f59e0b; font-weight: bold;');
    console.log('%c  Total: ' + (passCount + failCount + warnCount), 'color: #64748b; font-weight: bold;');
    console.log('');

    if (failCount === 0 && warnCount === 0) {
        console.log('%c🎉 ALL TESTS PASSED!', 'font-size: 20px; font-weight: bold; color: #10b981; background: #d1fae5; padding: 8px 16px; border-radius: 8px;');
        console.log('%cCalendar width expansion is working perfectly.', 'color: #059669; font-weight: bold;');
    } else if (failCount === 0) {
        console.log('%c✅ TESTS PASSED (with warnings)', 'font-size: 16px; font-weight: bold; color: #f59e0b; background: #fef3c7; padding: 8px 16px; border-radius: 8px;');
        console.log('%cSome minor issues detected. Review warnings above.', 'color: #d97706;');
    } else {
        console.log('%c❌ TESTS FAILED', 'font-size: 16px; font-weight: bold; color: #ef4444; background: #fee2e2; padding: 8px 16px; border-radius: 8px;');
        console.log('%cCritical issues detected. Review failures above.', 'color: #dc2626; font-weight: bold;');
    }

    console.log('');
    console.log('%c--- END OF VERIFICATION ---', 'color: #94a3b8;');
    console.log('');

    // Return results object
    return {
        viewport: {
            width: window.innerWidth,
            height: window.innerHeight,
            mode: viewportMode,
            isMobile: isMobile
        },
        results: {
            pass: passCount,
            fail: failCount,
            warn: warnCount,
            total: passCount + failCount + warnCount
        },
        elements: {
            container: !!container,
            toggleBtn: !!toggleBtn,
            icon: !!icon,
            sidebar: !!sidebar,
            calendar: !!calendar
        },
        state: {
            iconClass: icon?.className,
            gridColumns: getComputedStyle(container)?.gridTemplateColumns,
            calendarWidth: calendar?.offsetWidth,
            containerWidth: container?.offsetWidth
        }
    };
})();

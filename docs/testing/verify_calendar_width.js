/**
 * Calendar Width Verification Script
 *
 * Run this in the browser console on the Modern Calendar page
 * to verify the width fixes are working correctly.
 *
 * Usage:
 * 1. Open http://localhost:8000/oobc-management/coordination/calendar/modern/
 * 2. Open browser console (F12)
 * 3. Copy and paste this entire script
 * 4. Press Enter
 */

(function verifyCalendarWidth() {
    console.group('📊 FullCalendar Width Verification');

    // 1. Check container exists
    const container = document.getElementById('modernCalendar');
    if (!container) {
        console.error('❌ Calendar container #modernCalendar not found!');
        console.groupEnd();
        return;
    }
    console.log('✅ Calendar container found');

    // 2. Check container dimensions
    const containerWidth = container.offsetWidth;
    const containerHeight = container.offsetHeight;
    console.log(`📏 Container dimensions: ${containerWidth}px × ${containerHeight}px`);

    if (containerWidth < 400) {
        console.error(`❌ Container width too narrow: ${containerWidth}px (expected > 600px)`);
    } else if (containerWidth < 600) {
        console.warn(`⚠️ Container width suboptimal: ${containerWidth}px (recommended > 600px)`);
    } else {
        console.log(`✅ Container width good: ${containerWidth}px`);
    }

    if (containerHeight < 700) {
        console.warn(`⚠️ Container height: ${containerHeight}px (expected ~750px)`);
    } else {
        console.log(`✅ Container height good: ${containerHeight}px`);
    }

    // 3. Check FullCalendar element
    const fcElement = container.querySelector('.fc');
    if (!fcElement) {
        console.error('❌ FullCalendar .fc element not found!');
        console.groupEnd();
        return;
    }
    console.log('✅ FullCalendar .fc element found');

    const fcWidth = fcElement.offsetWidth;
    const fcHeight = fcElement.offsetHeight;
    console.log(`📏 FullCalendar .fc dimensions: ${fcWidth}px × ${fcHeight}px`);

    // 4. Check width match
    const widthDiff = Math.abs(containerWidth - fcWidth);
    if (widthDiff > 20) {
        console.error(`❌ Width mismatch! Container: ${containerWidth}px, FC: ${fcWidth}px (diff: ${widthDiff}px)`);
    } else {
        console.log(`✅ Width match good (diff: ${widthDiff}px)`);
    }

    // 5. Check view harness
    const viewHarness = container.querySelector('.fc-view-harness');
    if (viewHarness) {
        const harnessWidth = viewHarness.offsetWidth;
        console.log(`📏 View harness width: ${harnessWidth}px`);
        if (Math.abs(harnessWidth - fcWidth) > 20) {
            console.warn(`⚠️ View harness width mismatch: ${harnessWidth}px vs ${fcWidth}px`);
        } else {
            console.log('✅ View harness width correct');
        }
    } else {
        console.warn('⚠️ View harness not found (calendar may not be initialized yet)');
    }

    // 6. Check scrollgrid
    const scrollgrid = container.querySelector('.fc-scrollgrid');
    if (scrollgrid) {
        const gridWidth = scrollgrid.offsetWidth;
        console.log(`📏 Scrollgrid width: ${gridWidth}px`);
        if (Math.abs(gridWidth - fcWidth) > 20) {
            console.error(`❌ Scrollgrid width issue: ${gridWidth}px vs ${fcWidth}px`);
        } else {
            console.log('✅ Scrollgrid width correct');
        }
    } else {
        console.warn('⚠️ Scrollgrid not found (calendar may not be initialized yet)');
    }

    // 7. Check parent flex container
    const parentContainer = container.closest('.flex-1');
    if (parentContainer) {
        const parentWidth = parentContainer.offsetWidth;
        const computedStyle = window.getComputedStyle(parentContainer);
        const minWidth = computedStyle.minWidth;
        console.log(`📏 Parent flex container width: ${parentWidth}px`);
        console.log(`📏 Parent flex container min-width: ${minWidth}`);

        if (minWidth === '0px' || minWidth === 'auto') {
            console.error(`❌ Parent container has no min-width! This causes collapse.`);
        } else {
            console.log(`✅ Parent container min-width set: ${minWidth}`);
        }
    }

    // 8. Check current view
    const currentView = container.querySelector('.fc-view');
    if (currentView) {
        const viewClass = Array.from(currentView.classList).find(c => c.startsWith('fc-'));
        console.log(`📅 Current view: ${viewClass || 'unknown'}`);
    }

    // 9. Check columns (for week/month view)
    const columns = container.querySelectorAll('.fc-col-header-cell');
    if (columns.length > 0) {
        console.log(`📊 Calendar columns: ${columns.length}`);
        const firstColWidth = columns[0].offsetWidth;
        const lastColWidth = columns[columns.length - 1].offsetWidth;
        console.log(`📏 First column: ${firstColWidth}px, Last column: ${lastColWidth}px`);

        if (firstColWidth < 50) {
            console.error(`❌ Columns too narrow: ${firstColWidth}px (expected > 80px for week view)`);
        } else if (firstColWidth < 80 && columns.length === 7) {
            console.warn(`⚠️ Week view columns narrow: ${firstColWidth}px (recommended > 100px)`);
        } else {
            console.log(`✅ Column widths reasonable`);
        }
    }

    // 10. Final verdict
    console.log('\n🎯 VERDICT:');
    if (containerWidth < 400) {
        console.error('❌ FAIL: Calendar is rendering as narrow strip');
        console.log('💡 Check that fixes are applied:');
        console.log('   1. JavaScript: height: "parent", contentHeight: 700');
        console.log('   2. HTML: Removed min-w-0, added min-width: 600px');
        console.log('   3. CSS: Explicit heights, scrollgrid overrides');
    } else if (containerWidth < 600) {
        console.warn('⚠️ PARTIAL: Calendar width suboptimal but functional');
    } else {
        console.log('✅ SUCCESS: Calendar rendering with proper width!');
    }

    console.groupEnd();

    // Return useful debug info
    return {
        containerWidth,
        containerHeight,
        fcWidth,
        fcHeight,
        widthMatch: widthDiff < 20,
        columnsCount: container.querySelectorAll('.fc-col-header-cell').length
    };
})();

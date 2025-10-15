/**
 * Calendar Event Deletion - Debug Snippets
 *
 * Copy and paste these snippets into the browser console while on the calendar page
 * to debug event deletion issues.
 *
 * Usage:
 * 1. Navigate to: http://localhost:8000/oobc-management/calendar/
 * 2. Open browser console (F12 or Cmd+Option+I)
 * 3. Paste and run the relevant snippet below
 */

// ============================================
// 1. List All Calendar Events with IDs
// ============================================
// Shows all events currently loaded in the calendar
console.log('📊 All Calendar Events:');
console.table(
    calendar.getEvents().map((evt, idx) => ({
        Index: idx,
        ID: evt.id,
        'ID Type': typeof evt.id,
        'ID Length': String(evt.id).length,
        Title: evt.title,
        Start: evt.start ? evt.start.toISOString().split('T')[0] : 'N/A',
        End: evt.end ? evt.end.toISOString().split('T')[0] : 'N/A'
    }))
);


// ============================================
// 2. Search for Event by UUID
// ============================================
// Replace 'YOUR-UUID-HERE' with actual UUID
(function() {
    const uuid = 'YOUR-UUID-HERE';  // ← CHANGE THIS

    console.log(`🔍 Searching for UUID: ${uuid}\n`);

    const formats = [
        { id: uuid, label: 'Raw UUID' },
        { id: `work-item-${uuid}`, label: 'Work Item Format' },
        { id: `coordination-event-${uuid}`, label: 'Coordination Format' },
        { id: `staff-task-${uuid}`, label: 'Staff Task Format' }
    ];

    formats.forEach(fmt => {
        const found = calendar.getEventById(fmt.id);
        if (found) {
            console.log(`✅ FOUND using ${fmt.label}: "${fmt.id}"`);
            console.log('   Event:', found);
        } else {
            console.log(`❌ NOT FOUND using ${fmt.label}: "${fmt.id}"`);
        }
    });

    // Try Array.find()
    console.log('\n🔎 Trying Array.find() method:');
    const allEvents = calendar.getEvents();
    const found = allEvents.find(evt =>
        formats.some(fmt => evt.id === fmt.id)
    );

    if (found) {
        console.log('✅ Found via Array.find():', found);
    } else {
        console.log('❌ Not found via Array.find()');
        console.log('   Available IDs:', allEvents.map(e => e.id).join(', '));
    }
})();


// ============================================
// 3. Test Event Deletion (Simulation)
// ============================================
// Simulates the workItemDeleted event without actually deleting from DB
(function() {
    const testWorkItemId = 'YOUR-UUID-HERE';  // ← CHANGE THIS

    console.log(`🧪 Simulating deletion of work item: ${testWorkItemId}\n`);

    // Trigger the same event as HTMX DELETE
    document.body.dispatchEvent(new CustomEvent('workItemDeleted', {
        detail: {
            id: testWorkItemId,
            title: 'Test Work Item',
            type: 'Task'
        }
    }));

    console.log('✅ Event triggered. Check console output above for results.');
})();


// ============================================
// 4. Compare Event IDs (Pattern Matching)
// ============================================
// Shows which events match a specific pattern
(function() {
    const pattern = 'work-item-';  // ← CHANGE THIS (e.g., 'staff-task-', 'coordination-event-')

    console.log(`🔎 Events matching pattern: "${pattern}"\n`);

    const matching = calendar.getEvents().filter(evt =>
        String(evt.id).includes(pattern)
    );

    if (matching.length > 0) {
        console.log(`✅ Found ${matching.length} matching event(s):`);
        console.table(matching.map(evt => ({
            ID: evt.id,
            Title: evt.title,
            Type: evt.extendedProps?.workType || 'N/A'
        })));
    } else {
        console.log(`❌ No events found matching pattern: "${pattern}"`);
        console.log('   All event IDs:', calendar.getEvents().map(e => e.id).join(', '));
    }
})();


// ============================================
// 5. Verify ID Format Consistency
// ============================================
// Checks if all event IDs follow the same format
(function() {
    console.log('🔍 Checking ID format consistency:\n');

    const events = calendar.getEvents();
    const formats = {
        'work-item-': 0,
        'coordination-event-': 0,
        'staff-task-': 0,
        'raw-uuid': 0,
        'other': 0
    };

    const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

    events.forEach(evt => {
        const id = String(evt.id);

        if (id.startsWith('work-item-')) {
            formats['work-item-']++;
        } else if (id.startsWith('coordination-event-')) {
            formats['coordination-event-']++;
        } else if (id.startsWith('staff-task-')) {
            formats['staff-task-']++;
        } else if (uuidRegex.test(id)) {
            formats['raw-uuid']++;
        } else {
            formats['other']++;
        }
    });

    console.log('📊 ID Format Distribution:');
    console.table(formats);

    const totalEvents = events.length;
    const dominantFormat = Object.keys(formats).reduce((a, b) =>
        formats[a] > formats[b] ? a : b
    );

    console.log(`\n📈 Total events: ${totalEvents}`);
    console.log(`🏆 Dominant format: ${dominantFormat} (${formats[dominantFormat]} events)`);

    if (formats['other'] > 0) {
        console.warn('⚠️  Warning: Some events have unexpected ID formats!');
        const otherEvents = events.filter(evt => {
            const id = String(evt.id);
            return !id.startsWith('work-item-') &&
                   !id.startsWith('coordination-event-') &&
                   !id.startsWith('staff-task-') &&
                   !uuidRegex.test(id);
        });
        console.log('   Other format events:', otherEvents.map(e => e.id));
    }
})();


// ============================================
// 6. Extract UUID from Prefixed ID
// ============================================
// Extracts the UUID portion from a prefixed event ID
(function() {
    const prefixedId = 'work-item-4ce93060-8aee-4a4d-a5e9-f0fef99959ad';  // ← CHANGE THIS

    console.log(`🔧 Extracting UUID from: "${prefixedId}"\n`);

    const uuidRegex = /([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/i;
    const match = prefixedId.match(uuidRegex);

    if (match) {
        const uuid = match[1];
        console.log(`✅ Extracted UUID: ${uuid}`);
        console.log(`   Prefix: ${prefixedId.replace(uuid, '')}`);

        // Try to find this event
        const event = calendar.getEventById(prefixedId);
        if (event) {
            console.log(`✅ Event found in calendar:`, event);
        } else {
            console.log(`❌ Event NOT found in calendar with ID: ${prefixedId}`);
        }
    } else {
        console.log(`❌ No UUID found in: "${prefixedId}"`);
    }
})();


// ============================================
// 7. Manual Event Removal Test
// ============================================
// Manually removes an event to test the removal mechanism
(function() {
    const eventId = 'work-item-YOUR-UUID-HERE';  // ← CHANGE THIS

    console.log(`🗑️  Attempting to remove event: ${eventId}\n`);

    const event = calendar.getEventById(eventId);

    if (event) {
        console.log(`✅ Found event:`, event);
        console.log(`🔧 Removing event...`);
        event.remove();
        console.log(`✅ Event removed successfully!`);
        console.log(`📊 Remaining events: ${calendar.getEvents().length}`);
    } else {
        console.log(`❌ Event not found with ID: ${eventId}`);
        console.log(`📋 Available event IDs:`);
        calendar.getEvents().forEach((evt, idx) => {
            console.log(`   ${idx + 1}. ${evt.id} - "${evt.title}"`);
        });
    }
})();


// ============================================
// 8. Benchmark Array.find() vs getEventById()
// ============================================
// Compares performance of both methods
(function() {
    const targetUuid = 'YOUR-UUID-HERE';  // ← CHANGE THIS
    const targetId = `work-item-${targetUuid}`;
    const iterations = 1000;

    console.log(`⏱️  Performance Benchmark (${iterations} iterations)\n`);

    // Benchmark getEventById()
    const start1 = performance.now();
    for (let i = 0; i < iterations; i++) {
        calendar.getEventById(targetId);
    }
    const end1 = performance.now();
    const time1 = end1 - start1;

    // Benchmark Array.find()
    const start2 = performance.now();
    for (let i = 0; i < iterations; i++) {
        calendar.getEvents().find(evt => evt.id === targetId);
    }
    const end2 = performance.now();
    const time2 = end2 - start2;

    console.log(`🏁 Results:`);
    console.log(`   getEventById():  ${time1.toFixed(2)}ms (avg: ${(time1 / iterations).toFixed(4)}ms per call)`);
    console.log(`   Array.find():    ${time2.toFixed(2)}ms (avg: ${(time2 / iterations).toFixed(4)}ms per call)`);
    console.log(`   Difference:      ${(time2 - time1).toFixed(2)}ms`);

    if (time1 < time2) {
        console.log(`   ✅ getEventById() is ${((time2 / time1) - 1) * 100).toFixed(1)}% faster`);
    } else {
        console.log(`   ✅ Array.find() is ${((time1 / time2) - 1) * 100).toFixed(1)}% faster`);
    }

    console.log(`\n📊 Total events in calendar: ${calendar.getEvents().length}`);
})();


// ============================================
// 9. Test Event Listener (Live)
// ============================================
// Adds a temporary listener to see actual deletion events
(function() {
    console.log('👂 Installing temporary workItemDeleted listener...\n');

    const handler = function(event) {
        console.log('🔔 workItemDeleted event received:');
        console.log('   ID:', event.detail.id);
        console.log('   Title:', event.detail.title);
        console.log('   Type:', event.detail.type);
        console.log('   Full detail:', event.detail);
    };

    document.body.addEventListener('workItemDeleted', handler);

    console.log('✅ Listener installed. Delete a work item to see the event.');
    console.log('⚠️  To remove this listener, run: document.body.removeEventListener("workItemDeleted", handler);');

    // Store handler globally for removal
    window._debugWorkItemDeletedHandler = handler;
})();

// To remove the listener:
// document.body.removeEventListener('workItemDeleted', window._debugWorkItemDeletedHandler);


// ============================================
// 10. Full Diagnostic Report
// ============================================
// Generates a complete report of the calendar state
(function() {
    console.log('📋 FULL CALENDAR DIAGNOSTIC REPORT\n');
    console.log('='.repeat(80) + '\n');

    const events = calendar.getEvents();
    const sources = calendar.getEventSources();

    // Basic info
    console.log('📊 CALENDAR STATISTICS:');
    console.log(`   Total Events: ${events.length}`);
    console.log(`   Event Sources: ${sources.length}`);
    console.log(`   Current View: ${calendar.view.type}`);
    console.log(`   Current Date: ${calendar.getDate().toISOString().split('T')[0]}\n`);

    // ID format distribution
    console.log('🔍 ID FORMAT DISTRIBUTION:');
    const formats = {
        'work-item-': 0,
        'coordination-event-': 0,
        'staff-task-': 0,
        'raw-uuid': 0,
        'other': 0
    };

    const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

    events.forEach(evt => {
        const id = String(evt.id);
        if (id.startsWith('work-item-')) formats['work-item-']++;
        else if (id.startsWith('coordination-event-')) formats['coordination-event-']++;
        else if (id.startsWith('staff-task-')) formats['staff-task-']++;
        else if (uuidRegex.test(id)) formats['raw-uuid']++;
        else formats['other']++;
    });

    Object.keys(formats).forEach(key => {
        const count = formats[key];
        const pct = events.length > 0 ? ((count / events.length) * 100).toFixed(1) : '0.0';
        console.log(`   ${key.padEnd(25)} ${String(count).padStart(3)} events (${pct}%)`);
    });

    console.log('\n📝 SAMPLE EVENTS (First 5):');
    events.slice(0, 5).forEach((evt, idx) => {
        console.log(`   ${idx + 1}. ID: ${evt.id}`);
        console.log(`      Title: "${evt.title}"`);
        console.log(`      Type: ${evt.extendedProps?.workType || 'N/A'}`);
        console.log('');
    });

    // Event sources
    console.log('🔌 EVENT SOURCES:');
    sources.forEach((source, idx) => {
        console.log(`   ${idx + 1}. ID: ${source.id || 'N/A'}`);
        console.log(`      URL: ${source.url || 'Function-based'}`);
        console.log('');
    });

    console.log('='.repeat(80));
    console.log('✅ Report complete\n');
})();


// ============================================
// QUICK COPY-PASTE SNIPPETS
// ============================================

/*

// List all event IDs (one-liner):
console.log(calendar.getEvents().map(e => e.id).join('\n'));

// Count events:
console.log(`Total events: ${calendar.getEvents().length}`);

// Find event by partial ID match:
calendar.getEvents().find(e => e.id.includes('YOUR-PARTIAL-ID'))

// Remove all events (DANGER!):
calendar.getEvents().forEach(e => e.remove());

// Refresh calendar:
calendar.refetchEvents();

// Get current view info:
console.log(calendar.view);

// Trigger test deletion:
document.body.dispatchEvent(new CustomEvent('workItemDeleted', {
    detail: { id: 'YOUR-UUID', title: 'Test', type: 'Task' }
}));

*/

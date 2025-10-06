/**
 * CALENDAR EVENT DELETION DEBUGGER
 *
 * Copy and paste this entire script into your browser console
 * while viewing the calendar page.
 *
 * This will set up comprehensive logging to identify why
 * events aren't being removed from the calendar.
 */

(function() {
  console.clear();
  console.log('%c🔍 CALENDAR DEBUG MODE ACTIVATED', 'background: #222; color: #10b981; font-size: 16px; padding: 10px;');
  console.log('This script will monitor calendar events and deletions.\n');

  // Get calendar instance
  let calendar;
  try {
    calendar = window.calendar || FullCalendar.Calendar.getInstance(document.getElementById('calendar'));
    if (!calendar) {
      console.error('❌ Calendar instance not found!');
      console.log('Trying alternative methods...');

      // Try to get from global scope
      const calendarEl = document.getElementById('calendar');
      if (calendarEl && calendarEl._fc) {
        calendar = calendarEl._fc.calendar;
        console.log('✅ Found calendar via _fc property');
      }
    }
  } catch (e) {
    console.error('❌ Error getting calendar:', e);
    return;
  }

  if (!calendar) {
    console.error('❌ Could not find calendar instance. Make sure you\'re on a calendar page.');
    return;
  }

  console.log('✅ Calendar instance found\n');

  // ====================================
  // PART 1: CURRENT CALENDAR STATE
  // ====================================
  console.log('%c📊 PART 1: CURRENT CALENDAR STATE', 'background: #3b82f6; color: white; font-size: 14px; padding: 5px;');

  const allEvents = calendar.getEvents();
  console.log(`Total events in calendar: ${allEvents.length}\n`);

  if (allEvents.length > 0) {
    console.log('Sample event structure (first 3 events):');
    allEvents.slice(0, 3).forEach((event, index) => {
      console.log(`\nEvent ${index + 1}:`, {
        id: event.id,
        idType: typeof event.id,
        title: event.title,
        start: event.start?.toISOString(),
        extendedProps: event.extendedProps
      });
    });

    console.log('\nAll event IDs in calendar:');
    const idTable = allEvents.map(e => ({
      ID: e.id,
      Type: typeof e.id,
      Title: e.title.substring(0, 30) + (e.title.length > 30 ? '...' : '')
    }));
    console.table(idTable);
  } else {
    console.log('⚠️ No events in calendar');
  }

  // ====================================
  // PART 2: INSTALL DELETE MONITOR
  // ====================================
  console.log('\n%c🎯 PART 2: DELETE EVENT MONITOR INSTALLED', 'background: #f59e0b; color: white; font-size: 14px; padding: 5px;');
  console.log('Now delete an event and watch the logs below...\n');

  // Track deletion attempts
  let deletionAttempts = 0;

  // Monitor workItemDeleted events
  document.body.addEventListener('workItemDeleted', function(event) {
    deletionAttempts++;

    console.log(`\n%c🗑️ DELETION ATTEMPT #${deletionAttempts}`, 'background: #ef4444; color: white; font-size: 14px; padding: 5px;');
    console.log('Timestamp:', new Date().toISOString());

    // Log the event detail
    console.log('\n1️⃣ Event Detail Received:');
    console.log('Full detail object:', event.detail);

    // Extract ID (try different paths)
    const possibleIds = {
      'detail.id': event.detail?.id,
      'detail.workItem.id': event.detail?.workItem?.id,
      'detail.data.id': event.detail?.data?.id,
      'detail.item.id': event.detail?.item?.id
    };

    console.log('Possible ID paths:', possibleIds);

    // Determine which ID to use
    const eventId = event.detail?.id || event.detail?.workItem?.id || event.detail?.data?.id;
    console.log(`\n2️⃣ ID to search for: "${eventId}" (type: ${typeof eventId})`);

    if (!eventId) {
      console.error('❌ CRITICAL: No ID found in event detail!');
      console.log('Available properties:', Object.keys(event.detail || {}));
      return;
    }

    // Try to find in calendar
    console.log('\n3️⃣ Searching calendar...');
    const calendarEvent = calendar.getEventById(eventId);

    if (calendarEvent) {
      console.log('✅ SUCCESS: Event found in calendar!');
      console.log('Event object:', calendarEvent);

      // Remove it
      console.log('Attempting removal...');
      calendarEvent.remove();

      // Verify removal
      setTimeout(() => {
        const stillExists = calendar.getEventById(eventId);
        if (!stillExists) {
          console.log('%c✅ VERIFIED: Event successfully removed', 'background: #10b981; color: white; padding: 5px;');
        } else {
          console.error('%c❌ FAILED: Event still exists after removal!', 'background: #dc2626; color: white; padding: 5px;');
        }
      }, 100);

    } else {
      console.error('❌ FAILED: Event NOT found in calendar');

      // Diagnostic information
      console.log('\n🔍 DIAGNOSTICS:');
      console.log('What we searched for:', {
        value: eventId,
        type: typeof eventId,
        stringified: String(eventId),
        isNumber: !isNaN(eventId)
      });

      console.log('\nWhat exists in calendar:');
      const existingIds = calendar.getEvents().map(e => ({
        id: e.id,
        type: typeof e.id,
        matches: e.id == eventId,
        strictMatch: e.id === eventId,
        title: e.title.substring(0, 40)
      }));
      console.table(existingIds);

      // Try variants
      console.log('\n🔬 TRYING VARIANTS:');
      const variants = [
        { label: 'Original', value: eventId },
        { label: 'String', value: String(eventId) },
        { label: 'Number', value: Number(eventId) },
        { label: 'work-item- prefix', value: `work-item-${eventId}` },
        { label: 'workitem- prefix', value: `workitem-${eventId}` },
        { label: 'event- prefix', value: `event-${eventId}` }
      ];

      variants.forEach(variant => {
        const found = calendar.getEventById(variant.value);
        const status = found ? '✅ FOUND' : '❌ NOT FOUND';
        console.log(`${status} "${variant.label}": ${variant.value} (${typeof variant.value})`);

        if (found) {
          console.log('%c🎯 POTENTIAL FIX IDENTIFIED!', 'background: #10b981; color: white; font-size: 14px; padding: 5px;');
          console.log(`The correct ID format is: "${variant.value}"`);
          console.log(`You need to use: calendar.getEventById(${variant.label === 'Original' ? 'eventId' : JSON.stringify(variant.value)})`);
        }
      });

      // Suggest workaround
      console.log('\n💡 WORKAROUND: Refreshing entire calendar...');
      calendar.refetchEvents();
      console.log('Calendar refreshed. Event should disappear now.');
    }

    console.log('\n' + '='.repeat(80) + '\n');
  });

  // ====================================
  // PART 3: HELPER FUNCTIONS
  // ====================================
  console.log('\n%c⚙️ HELPER FUNCTIONS AVAILABLE', 'background: #8b5cf6; color: white; font-size: 14px; padding: 5px;');

  window.calendarDebug = {
    // List all events
    listEvents: function() {
      const events = calendar.getEvents();
      console.log(`Total events: ${events.length}`);
      console.table(events.map(e => ({
        ID: e.id,
        Type: typeof e.id,
        Title: e.title,
        Start: e.start?.toISOString()
      })));
    },

    // Find event by title
    findByTitle: function(title) {
      const events = calendar.getEvents().filter(e =>
        e.title.toLowerCase().includes(title.toLowerCase())
      );
      console.log(`Found ${events.length} events matching "${title}"`);
      console.table(events.map(e => ({
        ID: e.id,
        Title: e.title
      })));
      return events;
    },

    // Manually remove event
    removeById: function(id) {
      const event = calendar.getEventById(id);
      if (event) {
        event.remove();
        console.log(`✅ Removed event: ${event.title}`);
      } else {
        console.error(`❌ Event not found: ${id}`);
      }
    },

    // Remove by title
    removeByTitle: function(title) {
      const events = this.findByTitle(title);
      events.forEach(e => {
        e.remove();
        console.log(`✅ Removed: ${e.title}`);
      });
    },

    // Refresh calendar
    refresh: function() {
      calendar.refetchEvents();
      console.log('✅ Calendar refreshed');
    },

    // Show statistics
    stats: function() {
      const events = calendar.getEvents();
      const types = {};
      events.forEach(e => {
        const type = typeof e.id;
        types[type] = (types[type] || 0) + 1;
      });

      console.log('Calendar Statistics:');
      console.log(`Total events: ${events.length}`);
      console.log('ID types:', types);
      console.log('Date range:', {
        earliest: events.reduce((min, e) => !min || e.start < min ? e.start : min, null),
        latest: events.reduce((max, e) => !max || e.start > max ? e.start : max, null)
      });
    }
  };

  console.log('\nAvailable commands:');
  console.log('  calendarDebug.listEvents()           - List all events');
  console.log('  calendarDebug.findByTitle("meeting") - Find events by title');
  console.log('  calendarDebug.removeById(123)        - Remove event by ID');
  console.log('  calendarDebug.removeByTitle("test")  - Remove events by title');
  console.log('  calendarDebug.refresh()              - Refresh calendar');
  console.log('  calendarDebug.stats()                - Show statistics');

  console.log('\n%c✅ SETUP COMPLETE', 'background: #10b981; color: white; font-size: 16px; padding: 10px;');
  console.log('Delete an event now and watch the diagnostic output above.\n');

})();

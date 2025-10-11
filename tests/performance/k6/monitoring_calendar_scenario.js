import http from 'k6/http';
import { check, group, sleep } from 'k6';
import { Trend, Rate } from 'k6/metrics';

import { buildAuthHeaders, requireBaseUrl } from './lib/auth.js';

const BASE_URL = requireBaseUrl();
const ENTRY_ID = __ENV.K6_MONITORING_ENTRY_ID || JSON.parse(open('./env.example.json')).monitoringEntryId;

if (!ENTRY_ID || ENTRY_ID === '00000000-0000-0000-0000-000000000000') {
  throw new Error('Provide K6_MONITORING_ENTRY_ID env var (UUID of a monitoring entry with work items).');
}

const calendarUrl = `${BASE_URL}/monitoring/entry/${ENTRY_ID}/calendar-feed/`;
const syncUrl = `${BASE_URL}/api/monitoring/entries/${ENTRY_ID}/sync-from-workitem/`;

const calendarDuration = new Trend('monitoring_calendar_duration', true);
const syncDuration = new Trend('monitoring_sync_duration', true);
const calendarErrorRate = new Rate('monitoring_calendar_error_rate');
const syncErrorRate = new Rate('monitoring_sync_error_rate');

export const options = {
  scenarios: {
    monitoring_calendar_stream: {
      executor: 'ramping-arrival-rate',
      startRate: 5,
      timeUnit: '1s',
      preAllocatedVUs: 20,
      maxVUs: 40,
      stages: [
        { duration: '2m', target: 20 },
        { duration: '5m', target: 20 },
        { duration: '2m', target: 0 },
      ],
    },
  },
  thresholds: {
    monitoring_calendar_duration: ['p(95)<600'],
    monitoring_sync_duration: ['p(95)<700'],
    monitoring_calendar_error_rate: ['rate<0.01'],
    monitoring_sync_error_rate: ['rate<0.01'],
  },
};

export function setup() {
  return {
    headers: buildAuthHeaders(),
  };
}

export default function monitorCalendars(data) {
  const authHeaders = data.headers;

  group('calendar feed polling', () => {
    const res = http.get(calendarUrl, { headers: authHeaders });
    const ok = check(res, {
      'calendar feed returns 200': (r) => r.status === 200,
      'calendar feed payload is JSON': (r) => r.headers['Content-Type']?.includes('application/json') ?? false,
    });
    calendarDuration.add(res.timings.duration);
    calendarErrorRate.add(!ok);
  });

  group('workitem synchronization trigger', () => {
    const headers = { ...authHeaders, 'Content-Type': 'application/json' };
    const res = http.post(syncUrl, JSON.stringify({}), { headers });
    const ok = check(res, {
      'sync endpoint returns success': (r) => r.status === 200 || r.status === 204,
    });
    syncDuration.add(res.timings.duration);
    syncErrorRate.add(!ok);
  });

  sleep(1);
}

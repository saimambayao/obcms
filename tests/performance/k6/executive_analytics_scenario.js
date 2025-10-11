import http from 'k6/http';
import { check, group, sleep } from 'k6';
import { Trend, Rate } from 'k6/metrics';

import { buildAuthHeaders, requireBaseUrl } from './lib/auth.js';

const BASE_URL = requireBaseUrl();
const ANALYTICS_SCENARIO_ID =
  __ENV.K6_ANALYTICS_SCENARIO_ID || JSON.parse(open('./env.example.json')).analyticsScenarioId;

const pages = [
  {
    name: 'budget feedback dashboard',
    url: `${BASE_URL}/oobc-management/budget-feedback/`,
  },
  {
    name: 'annual planning dashboard',
    url: `${BASE_URL}/oobc-management/annual-planning/`,
  },
  {
    name: 'scenario list',
    url: `${BASE_URL}/oobc-management/scenarios/`,
  },
];

const apiEndpoints = [
  {
    name: 'policy recommendations feed',
    url: `${BASE_URL}/api/policy-tracking/recommendations/`,
  },
  {
    name: 'monitoring scenarios API',
    url: `${BASE_URL}/api/monitoring/scenarios/`,
  },
];

if (ANALYTICS_SCENARIO_ID && ANALYTICS_SCENARIO_ID !== '00000000-0000-0000-0000-000000000000') {
    apiEndpoints.push({
      name: 'scenario detail API',
      url: `${BASE_URL}/api/monitoring/scenarios/${ANALYTICS_SCENARIO_ID}/`,
    });
}

const pageDuration = new Trend('executive_dashboard_duration', true);
const pageErrorRate = new Rate('executive_dashboard_error_rate');
const apiDuration = new Trend('executive_api_duration', true);
const apiErrorRate = new Rate('executive_api_error_rate');

export const options = {
  scenarios: {
    executive_dashboards: {
      executor: 'constant-vus',
      vus: 15,
      duration: '6m',
    },
  },
  thresholds: {
    executive_dashboard_duration: ['p(95)<800'],
    executive_api_duration: ['p(95)<700'],
    executive_dashboard_error_rate: ['rate<0.01'],
    executive_api_error_rate: ['rate<0.01'],
  },
};

export function setup() {
  return {
    headers: buildAuthHeaders(),
  };
}

export default function runExecutiveDashboards(data) {
  const headers = data.headers;

  group('dashboard pages', () => {
    for (const page of pages) {
      const res = http.get(page.url, { headers });
      const ok = check(res, {
        [`${page.name} returns 200`]: (r) => r.status === 200,
        [`${page.name} renders HTML`]: (r) => r.headers['Content-Type']?.includes('text/html') ?? false,
      });
      pageDuration.add(res.timings.duration, { page: page.name });
      pageErrorRate.add(!ok);
    }
  });

  group('analytics APIs', () => {
    for (const endpoint of apiEndpoints) {
      const res = http.get(endpoint.url, { headers });
      const ok = check(res, {
        [`${endpoint.name} 200`]: (r) => r.status === 200,
        [`${endpoint.name} JSON`]: (r) => r.headers['Content-Type']?.includes('application/json') ?? false,
      });
      apiDuration.add(res.timings.duration, { endpoint: endpoint.name });
      apiErrorRate.add(!ok);
    }
  });

  sleep(1);
}

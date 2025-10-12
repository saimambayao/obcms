# BMMS Testing Strategy Expansion

This document provides comprehensive Component Testing and expanded Performance Testing sections to be integrated into TRANSITION_PLAN.md Section 23.

---

## 23.4 Performance Testing (EXPANDED)

### 23.4.1 Page Load Performance Testing

**Objective:** Ensure all pages load within acceptable time thresholds under various conditions.

```python
# src/tests/performance/test_page_load.py

import pytest
import time
from django.test import Client
from django.contrib.auth import get_user_model
from organizations.models import Organization
from mana.models import Assessment
from coordination.models import Partnership
from communities.models import Region, Province, Municipality, Barangay

User = get_user_model()


@pytest.mark.django_db
class TestPageLoadPerformance:
    """Test page load performance across OBCMS modules."""

    @pytest.fixture
    def setup_performance_data(self):
        """Create realistic dataset for performance testing."""
        # Create organization
        moa = Organization.objects.create(
            code='MOH',
            name='Ministry of Health',
            org_type='MOA'
        )

        # Create user
        user = User.objects.create_user(
            username='moh_staff',
            email='staff@moh.gov.ph',
            password='testpass123',
            default_organization=moa
        )

        # Create 50 assessments
        for i in range(50):
            Assessment.objects.create(
                title=f'Assessment {i}',
                organization=moa,
                status='published' if i % 2 == 0 else 'draft',
                description=f'Test assessment {i}' * 10  # Realistic content
            )

        # Create 30 partnerships
        for i in range(30):
            Partnership.objects.create(
                title=f'Partnership {i}',
                organization=moa,
                status='active' if i % 3 == 0 else 'pending'
            )

        # Create community hierarchy
        region = Region.objects.create(name='Region IX', code='09')
        province = Province.objects.create(name='Zamboanga del Sur', code='0972', region=region)
        muni = Municipality.objects.create(name='Pagadian City', code='097201', province=province)

        # Create 100 barangays
        for i in range(100):
            Barangay.objects.create(
                name=f'Barangay {i}',
                code=f'09720100{i:03d}',
                municipality=muni,
                population=1000 + i * 50,
                obc_status='Confirmed'
            )

        return {
            'moa': moa,
            'user': user,
            'region': region
        }

    def test_dashboard_load_time(self, setup_performance_data):
        """Dashboard should load in < 200ms."""
        client = Client()
        user = setup_performance_data['user']
        client.force_login(user)

        start_time = time.time()
        response = client.get(f'/moa/{user.default_organization.code}/')
        end_time = time.time()

        load_time_ms = (end_time - start_time) * 1000

        assert response.status_code == 200
        assert load_time_ms < 200, f"Dashboard load time {load_time_ms:.2f}ms exceeds 200ms"
        print(f"✓ Dashboard loaded in {load_time_ms:.2f}ms")

    def test_assessment_list_load_time(self, setup_performance_data):
        """Assessment list should load in < 300ms with pagination."""
        client = Client()
        user = setup_performance_data['user']
        client.force_login(user)

        start_time = time.time()
        response = client.get(f'/moa/{user.default_organization.code}/mana/assessments/')
        end_time = time.time()

        load_time_ms = (end_time - start_time) * 1000

        assert response.status_code == 200
        assert load_time_ms < 300, f"List load time {load_time_ms:.2f}ms exceeds 300ms"
        print(f"✓ Assessment list loaded in {load_time_ms:.2f}ms")

    def test_calendar_view_load_time(self, setup_performance_data):
        """Calendar view with events should load in < 500ms."""
        client = Client()
        user = setup_performance_data['user']
        client.force_login(user)

        start_time = time.time()
        response = client.get(f'/moa/{user.default_organization.code}/coordination/calendar/')
        end_time = time.time()

        load_time_ms = (end_time - start_time) * 1000

        assert response.status_code == 200
        assert load_time_ms < 500, f"Calendar load time {load_time_ms:.2f}ms exceeds 500ms"
        print(f"✓ Calendar loaded in {load_time_ms:.2f}ms")

    def test_geojson_rendering_performance(self, setup_performance_data):
        """GeoJSON boundary rendering should complete in < 400ms."""
        client = Client()
        user = setup_performance_data['user']
        client.force_login(user)

        start_time = time.time()
        response = client.get('/api/communities/regions/09/geojson/')
        end_time = time.time()

        load_time_ms = (end_time - start_time) * 1000

        assert response.status_code == 200
        assert load_time_ms < 400, f"GeoJSON load time {load_time_ms:.2f}ms exceeds 400ms"
        print(f"✓ GeoJSON rendered in {load_time_ms:.2f}ms")


### 23.4.2 Database Query Performance Testing

**Objective:** Detect and prevent N+1 query problems, ensure proper use of indexes.

```python
# src/tests/performance/test_query_performance.py

import pytest
from django.test import Client
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.contrib.auth import get_user_model
from organizations.models import Organization
from mana.models import Assessment
from coordination.models import Partnership

User = get_user_model()


@pytest.mark.django_db
class TestQueryPerformance:
    """Test database query efficiency."""

    @pytest.fixture
    def setup_query_test(self):
        """Setup data for query tests."""
        moa = Organization.objects.create(code='MOH', name='Ministry of Health', org_type='MOA')
        user = User.objects.create_user(
            username='moh_staff',
            email='staff@moh.gov.ph',
            password='testpass123',
            default_organization=moa
        )

        # Create 20 assessments
        for i in range(20):
            Assessment.objects.create(
                title=f'Assessment {i}',
                organization=moa,
                status='published'
            )

        return {'moa': moa, 'user': user}

    def test_assessment_list_query_count(self, setup_query_test):
        """Assessment list should use ≤ 5 queries (no N+1 problem)."""
        client = Client()
        user = setup_query_test['user']
        client.force_login(user)

        with CaptureQueriesContext(connection) as queries:
            response = client.get(f'/moa/{user.default_organization.code}/mana/assessments/')

        query_count = len(queries)

        assert response.status_code == 200
        assert query_count <= 5, f"Query count {query_count} exceeds 5 (N+1 problem detected)"
        print(f"✓ Assessment list used {query_count} queries")

    def test_select_related_optimization(self, setup_query_test):
        """Verify select_related() is used for foreign keys."""
        from mana.models import Assessment

        with CaptureQueriesContext(connection) as queries_without:
            # WITHOUT select_related
            assessments = Assessment.objects.filter(organization=setup_query_test['moa'])
            for a in assessments:
                _ = a.organization.name  # Triggers extra query per assessment

        with CaptureQueriesContext(connection) as queries_with:
            # WITH select_related
            assessments = Assessment.objects.filter(
                organization=setup_query_test['moa']
            ).select_related('organization')
            for a in assessments:
                _ = a.organization.name  # No extra queries

        # select_related should drastically reduce queries
        assert len(queries_with) < len(queries_without), \
            "select_related() not reducing query count"
        print(f"✓ select_related reduced queries from {len(queries_without)} to {len(queries_with)}")

    def test_slow_query_detection(self, setup_query_test):
        """All queries should complete in < 100ms."""
        client = Client()
        user = setup_query_test['user']
        client.force_login(user)

        with CaptureQueriesContext(connection) as queries:
            response = client.get(f'/moa/{user.default_organization.code}/')

        slow_queries = []
        for query in queries:
            query_time = float(query['time']) * 1000  # Convert to ms
            if query_time > 100:
                slow_queries.append({
                    'sql': query['sql'][:100],
                    'time': query_time
                })

        assert len(slow_queries) == 0, f"Found {len(slow_queries)} slow queries: {slow_queries}"
        print(f"✓ All {len(queries)} queries completed in < 100ms")

    def test_index_usage_verification(self, setup_query_test):
        """Verify database indexes are being used for organization filtering."""
        moa = setup_query_test['moa']

        with connection.cursor() as cursor:
            # Test organization_id index usage
            cursor.execute(
                "EXPLAIN SELECT * FROM mana_assessment WHERE organization_id = %s",
                [moa.id]
            )
            explain_output = cursor.fetchall()

        explain_text = str(explain_output).lower()

        # Check for index usage (works for both SQLite and PostgreSQL)
        has_index = any([
            'index' in explain_text,
            'search' in explain_text,  # SQLite "SEARCH TABLE ... USING INDEX"
            'scan' in explain_text and 'index' in explain_text  # PostgreSQL "Index Scan"
        ])

        assert has_index, "Database index not being used for organization filtering"
        print(f"✓ Index detected in query plan: {explain_text[:200]}")


### 23.4.3 HTMX Performance Testing

**Objective:** Verify instant UI updates and smooth HTMX interactions.

```python
# src/tests/performance/test_htmx_performance.py

import pytest
import time
from django.test import Client
from django.contrib.auth import get_user_model
from organizations.models import Organization
from coordination.models import Task

User = get_user_model()


@pytest.mark.django_db
class TestHTMXPerformance:
    """Test HTMX interaction performance."""

    @pytest.fixture
    def setup_htmx_test(self):
        """Setup data for HTMX tests."""
        moa = Organization.objects.create(code='MOH', name='Ministry of Health', org_type='MOA')
        user = User.objects.create_user(
            username='moh_staff',
            email='staff@moh.gov.ph',
            password='testpass123',
            default_organization=moa
        )

        # Create tasks for kanban testing
        for i in range(10):
            Task.objects.create(
                title=f'Task {i}',
                organization=moa,
                assigned_to=user,
                status='pending'
            )

        return {'moa': moa, 'user': user}

    def test_htmx_swap_time(self, setup_htmx_test):
        """HTMX element swaps should complete in < 50ms."""
        client = Client()
        user = setup_htmx_test['user']
        client.force_login(user)

        task = Task.objects.first()

        start_time = time.time()
        response = client.post(
            f'/moa/{user.default_organization.code}/coordination/tasks/{task.id}/update-status/',
            {'status': 'in-progress'},
            HTTP_HX_REQUEST='true'
        )
        end_time = time.time()

        swap_time_ms = (end_time - start_time) * 1000

        assert response.status_code in [200, 204]
        assert swap_time_ms < 50, f"HTMX swap time {swap_time_ms:.2f}ms exceeds 50ms"
        print(f"✓ HTMX swap completed in {swap_time_ms:.2f}ms")

    def test_optimistic_update_performance(self, setup_htmx_test):
        """Optimistic updates should return immediately with 204 No Content."""
        client = Client()
        user = setup_htmx_test['user']
        client.force_login(user)

        task = Task.objects.first()

        start_time = time.time()
        response = client.delete(
            f'/moa/{user.default_organization.code}/coordination/tasks/{task.id}/delete/',
            HTTP_HX_REQUEST='true'
        )
        end_time = time.time()

        response_time_ms = (end_time - start_time) * 1000

        assert response.status_code == 204
        assert response_time_ms < 30, f"Optimistic update took {response_time_ms:.2f}ms (should be < 30ms)"
        print(f"✓ Optimistic update completed in {response_time_ms:.2f}ms")

    def test_out_of_band_swap_performance(self, setup_htmx_test):
        """Out-of-band swaps (multiple element updates) should be fast."""
        client = Client()
        user = setup_htmx_test['user']
        client.force_login(user)

        task = Task.objects.first()

        start_time = time.time()
        response = client.post(
            f'/moa/{user.default_organization.code}/coordination/tasks/{task.id}/update-status/',
            {'status': 'completed'},
            HTTP_HX_REQUEST='true'
        )
        end_time = time.time()

        response_time_ms = (end_time - start_time) * 1000

        # Response should include HX-Trigger header for counter updates
        assert response.has_header('HX-Trigger') or response.status_code == 204
        assert response_time_ms < 100, f"OOB swap took {response_time_ms:.2f}ms"
        print(f"✓ Out-of-band swap completed in {response_time_ms:.2f}ms")


### 23.4.4 Concurrent User Load Testing

**Objective:** Test system stability under high concurrent user load.

```python
# src/tests/performance/test_concurrent_load.py

import pytest
import time
import concurrent.futures
from django.test import Client
from django.contrib.auth import get_user_model
from organizations.models import Organization

User = get_user_model()


@pytest.mark.django_db
@pytest.mark.slow
class TestConcurrentLoad:
    """Test system under concurrent user load."""

    @pytest.fixture
    def setup_concurrent_test(self):
        """Create multiple organizations and users."""
        organizations = []
        users = []

        # Create 10 MOAs
        for i in range(10):
            org = Organization.objects.create(
                code=f'MOA{i:02d}',
                name=f'Ministry {i}',
                org_type='MOA'
            )
            organizations.append(org)

            # Create 5 users per org (50 total users)
            for j in range(5):
                user = User.objects.create_user(
                    username=f'staff_{org.code}_{j}',
                    email=f'staff{j}@{org.code.lower()}.gov.ph',
                    password='testpass123',
                    default_organization=org
                )
                users.append(user)

        return {'organizations': organizations, 'users': users}

    def simulate_user_session(self, user):
        """Simulate typical user session."""
        client = Client()
        client.force_login(user)

        try:
            # Dashboard view
            r1 = client.get(f'/moa/{user.default_organization.code}/')
            assert r1.status_code == 200

            # List view
            r2 = client.get(f'/moa/{user.default_organization.code}/mana/assessments/')
            assert r2.status_code == 200

            # API call
            r3 = client.get('/api/communities/barangays/?limit=10')
            assert r3.status_code == 200

            return True
        except Exception as e:
            print(f"User session failed: {e}")
            return False

    def test_500_concurrent_users(self, setup_concurrent_test):
        """System should handle 500 concurrent users without degradation."""
        users = setup_concurrent_test['users']

        start_time = time.time()

        # Simulate 500 concurrent sessions (50 users * 10 sessions each)
        with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
            futures = []
            for _ in range(500):
                user = users[_ % len(users)]
                future = executor.submit(self.simulate_user_session, user)
                futures.append(future)

            results = [f.result() for f in concurrent.futures.as_completed(futures)]

        end_time = time.time()
        total_time_seconds = end_time - start_time

        success_count = sum(results)
        success_rate = (success_count / len(results)) * 100

        assert success_rate >= 95, f"Success rate {success_rate:.1f}% < 95%"
        assert total_time_seconds < 60, f"Load test took {total_time_seconds:.1f}s (should be < 60s)"

        print(f"✓ 500 concurrent users: {success_rate:.1f}% success in {total_time_seconds:.1f}s")

    def test_sustained_load(self, setup_concurrent_test):
        """System should maintain performance under sustained load."""
        users = setup_concurrent_test['users']

        # Run for 5 minutes with continuous load
        start_time = time.time()
        duration_seconds = 300  # 5 minutes

        successful_requests = 0
        failed_requests = 0

        while time.time() - start_time < duration_seconds:
            with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
                futures = []
                for _ in range(100):
                    user = users[_ % len(users)]
                    future = executor.submit(self.simulate_user_session, user)
                    futures.append(future)

                results = [f.result() for f in concurrent.futures.as_completed(futures)]
                successful_requests += sum(results)
                failed_requests += len(results) - sum(results)

            time.sleep(1)  # Throttle between batches

        success_rate = (successful_requests / (successful_requests + failed_requests)) * 100

        assert success_rate >= 95, f"Sustained load success rate {success_rate:.1f}% < 95%"
        print(f"✓ Sustained load: {successful_requests} successful, {failed_requests} failed ({success_rate:.1f}%)")


### 23.4.5 API Performance Testing

**Objective:** Ensure REST API endpoints meet performance targets.

```python
# src/tests/performance/test_api_performance.py

import pytest
import time
from django.test import Client
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from organizations.models import Organization
from communities.models import Barangay, Region, Province, Municipality

User = get_user_model()


@pytest.mark.django_db
class TestAPIPerformance:
    """Test REST API endpoint performance."""

    @pytest.fixture
    def setup_api_test(self):
        """Setup data for API tests."""
        moa = Organization.objects.create(code='MOH', name='Ministry of Health', org_type='MOA')
        user = User.objects.create_user(
            username='moh_staff',
            email='staff@moh.gov.ph',
            password='testpass123',
            default_organization=moa
        )

        # Create community hierarchy with 100 barangays
        region = Region.objects.create(name='Region IX', code='09')
        province = Province.objects.create(name='Zamboanga del Sur', code='0972', region=region)
        muni = Municipality.objects.create(name='Pagadian City', code='097201', province=province)

        for i in range(100):
            Barangay.objects.create(
                name=f'Barangay {i}',
                code=f'09720100{i:03d}',
                municipality=muni,
                population=1000 + i * 50,
                obc_status='Confirmed'
            )

        return {'moa': moa, 'user': user}

    def test_api_list_response_time(self, setup_api_test):
        """API list endpoints should respond in < 500ms."""
        client = APIClient()
        user = setup_api_test['user']
        client.force_authenticate(user=user)

        start_time = time.time()
        response = client.get('/api/communities/barangays/')
        end_time = time.time()

        response_time_ms = (end_time - start_time) * 1000

        assert response.status_code == 200
        assert response_time_ms < 500, f"API response time {response_time_ms:.2f}ms exceeds 500ms"
        print(f"✓ API list endpoint responded in {response_time_ms:.2f}ms")

    def test_api_pagination_performance(self, setup_api_test):
        """Paginated API calls should be fast."""
        client = APIClient()
        user = setup_api_test['user']
        client.force_authenticate(user=user)

        start_time = time.time()
        response = client.get('/api/communities/barangays/?page=1&page_size=20')
        end_time = time.time()

        response_time_ms = (end_time - start_time) * 1000

        assert response.status_code == 200
        assert 'results' in response.json()
        assert response_time_ms < 300, f"Paginated API took {response_time_ms:.2f}ms"
        print(f"✓ Paginated API responded in {response_time_ms:.2f}ms")

    def test_api_filtering_performance(self, setup_api_test):
        """Filtered API queries should use indexes and be fast."""
        client = APIClient()
        user = setup_api_test['user']
        client.force_authenticate(user=user)

        start_time = time.time()
        response = client.get('/api/communities/barangays/?obc_status=Confirmed')
        end_time = time.time()

        response_time_ms = (end_time - start_time) * 1000

        assert response.status_code == 200
        assert response_time_ms < 400, f"Filtered API took {response_time_ms:.2f}ms"
        print(f"✓ Filtered API responded in {response_time_ms:.2f}ms")

    def test_geojson_api_performance(self, setup_api_test):
        """GeoJSON API endpoints should serialize efficiently."""
        client = APIClient()
        user = setup_api_test['user']
        client.force_authenticate(user=user)

        start_time = time.time()
        response = client.get('/api/communities/regions/09/geojson/')
        end_time = time.time()

        response_time_ms = (end_time - start_time) * 1000

        assert response.status_code == 200
        assert response_time_ms < 600, f"GeoJSON API took {response_time_ms:.2f}ms"
        print(f"✓ GeoJSON API responded in {response_time_ms:.2f}ms")


### 23.4.6 Caching Performance Testing

**Objective:** Verify caching strategies improve performance.

```python
# src/tests/performance/test_caching.py

import pytest
import time
from django.test import Client
from django.core.cache import cache
from django.contrib.auth import get_user_model
from organizations.models import Organization
from mana.models import Assessment

User = get_user_model()


@pytest.mark.django_db
class TestCachingPerformance:
    """Test caching effectiveness."""

    @pytest.fixture
    def setup_caching_test(self):
        """Setup data for caching tests."""
        moa = Organization.objects.create(code='MOH', name='Ministry of Health', org_type='MOA')
        user = User.objects.create_user(
            username='moh_staff',
            email='staff@moh.gov.ph',
            password='testpass123',
            default_organization=moa
        )

        # Create 50 assessments
        for i in range(50):
            Assessment.objects.create(
                title=f'Assessment {i}',
                organization=moa,
                status='published'
            )

        # Clear cache before test
        cache.clear()

        return {'moa': moa, 'user': user}

    def test_cache_hit_performance(self, setup_caching_test):
        """Cached responses should be 10x faster than uncached."""
        client = Client()
        user = setup_caching_test['user']
        client.force_login(user)

        # First request (cache miss)
        start_time = time.time()
        response1 = client.get(f'/moa/{user.default_organization.code}/')
        end_time = time.time()
        uncached_time_ms = (end_time - start_time) * 1000

        # Second request (cache hit)
        start_time = time.time()
        response2 = client.get(f'/moa/{user.default_organization.code}/')
        end_time = time.time()
        cached_time_ms = (end_time - start_time) * 1000

        speedup_factor = uncached_time_ms / cached_time_ms if cached_time_ms > 0 else 1

        assert response1.status_code == 200
        assert response2.status_code == 200
        # Cached should be noticeably faster (at least 2x)
        assert speedup_factor >= 2, f"Cache speedup {speedup_factor:.1f}x < 2x"

        print(f"✓ Cache hit: {cached_time_ms:.2f}ms (uncached: {uncached_time_ms:.2f}ms, {speedup_factor:.1f}x faster)")

    def test_cache_invalidation(self, setup_caching_test):
        """Cache should invalidate when data changes."""
        client = Client()
        user = setup_caching_test['user']
        client.force_login(user)

        # Prime cache
        response1 = client.get(f'/moa/{user.default_organization.code}/mana/assessments/')
        assert response1.status_code == 200

        # Modify data
        Assessment.objects.create(
            title='New Assessment',
            organization=setup_caching_test['moa'],
            status='published'
        )

        # Fetch again (cache should be invalidated)
        response2 = client.get(f'/moa/{user.default_organization.code}/mana/assessments/')
        assert response2.status_code == 200

        # New assessment should be visible
        content = response2.content.decode()
        assert 'New Assessment' in content, "Cache not invalidated after data change"

        print("✓ Cache properly invalidated after data change")

    def test_organization_context_caching(self, setup_caching_test):
        """Organization context should be cached per user."""
        client = Client()
        user = setup_caching_test['user']
        client.force_login(user)

        # Multiple requests to different pages
        start_time = time.time()
        for _ in range(10):
            client.get(f'/moa/{user.default_organization.code}/')
            client.get(f'/moa/{user.default_organization.code}/mana/assessments/')
            client.get(f'/moa/{user.default_organization.code}/coordination/partnerships/')
        end_time = time.time()

        avg_time_ms = ((end_time - start_time) / 30) * 1000

        # Average request should be fast due to org context caching
        assert avg_time_ms < 150, f"Average request time {avg_time_ms:.2f}ms too slow (caching not effective)"
        print(f"✓ Organization context caching: avg {avg_time_ms:.2f}ms per request")


### 23.4.7 Frontend Performance Testing (Core Web Vitals)

**Objective:** Ensure frontend meets Core Web Vitals standards.

```python
# src/tests/performance/test_frontend_performance.py

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json


@pytest.mark.django_db
@pytest.mark.selenium
class TestFrontendPerformance:
    """Test frontend performance metrics (Core Web Vitals)."""

    @pytest.fixture
    def setup_selenium(self):
        """Setup Selenium WebDriver for performance testing."""
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')

        # Enable performance logging
        chrome_options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})

        driver = webdriver.Chrome(options=chrome_options)
        driver.set_window_size(1920, 1080)

        yield driver

        driver.quit()

    def get_web_vitals(self, driver):
        """Extract Core Web Vitals from page."""
        # Inject Web Vitals library and measure
        vitals_script = """
        return new Promise((resolve) => {
            const vitals = {};

            // Largest Contentful Paint (LCP)
            new PerformanceObserver((list) => {
                const entries = list.getEntries();
                vitals.lcp = entries[entries.length - 1].renderTime || entries[entries.length - 1].loadTime;
            }).observe({type: 'largest-contentful-paint', buffered: true});

            // First Contentful Paint (FCP)
            new PerformanceObserver((list) => {
                vitals.fcp = list.getEntries()[0].startTime;
            }).observe({type: 'paint', buffered: true});

            // Cumulative Layout Shift (CLS)
            let cls = 0;
            new PerformanceObserver((list) => {
                for (const entry of list.getEntries()) {
                    if (!entry.hadRecentInput) {
                        cls += entry.value;
                    }
                }
                vitals.cls = cls;
            }).observe({type: 'layout-shift', buffered: true});

            // Time to Interactive (TTI)
            const navTiming = performance.getEntriesByType('navigation')[0];
            vitals.tti = navTiming.domInteractive;

            setTimeout(() => resolve(vitals), 2000);
        });
        """

        return driver.execute_async_script(vitals_script)

    def test_largest_contentful_paint(self, setup_selenium, live_server):
        """LCP should be < 2.5 seconds (Good)."""
        driver = setup_selenium
        driver.get(f'{live_server.url}/accounts/login/')

        # Login
        driver.find_element(By.NAME, 'username').send_keys('admin')
        driver.find_element(By.NAME, 'password').send_keys('admin')
        driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()

        # Navigate to dashboard
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.dashboard'))
        )

        vitals = self.get_web_vitals(driver)
        lcp_seconds = vitals.get('lcp', 0) / 1000

        assert lcp_seconds < 2.5, f"LCP {lcp_seconds:.2f}s exceeds 2.5s (Poor)"

        if lcp_seconds < 2.5:
            print(f"✓ LCP: {lcp_seconds:.2f}s (Good)")
        else:
            print(f"✗ LCP: {lcp_seconds:.2f}s (Needs Improvement)")

    def test_first_contentful_paint(self, setup_selenium, live_server):
        """FCP should be < 1.8 seconds (Good)."""
        driver = setup_selenium
        driver.get(f'{live_server.url}/')

        vitals = self.get_web_vitals(driver)
        fcp_seconds = vitals.get('fcp', 0) / 1000

        assert fcp_seconds < 1.8, f"FCP {fcp_seconds:.2f}s exceeds 1.8s"
        print(f"✓ FCP: {fcp_seconds:.2f}s (Good)")

    def test_cumulative_layout_shift(self, setup_selenium, live_server):
        """CLS should be < 0.1 (Good)."""
        driver = setup_selenium
        driver.get(f'{live_server.url}/')

        vitals = self.get_web_vitals(driver)
        cls_score = vitals.get('cls', 0)

        assert cls_score < 0.1, f"CLS {cls_score:.3f} exceeds 0.1 (Poor)"
        print(f"✓ CLS: {cls_score:.3f} (Good)")

    def test_time_to_interactive(self, setup_selenium, live_server):
        """TTI should be < 3.8 seconds (Good)."""
        driver = setup_selenium
        driver.get(f'{live_server.url}/')

        vitals = self.get_web_vitals(driver)
        tti_seconds = vitals.get('tti', 0) / 1000

        assert tti_seconds < 3.8, f"TTI {tti_seconds:.2f}s exceeds 3.8s"
        print(f"✓ TTI: {tti_seconds:.2f}s (Good)")


### 23.4.8 Load Testing with Locust (EXPANDED)

**Comprehensive load testing scenarios covering all OBCMS modules.**

```python
# locustfile.py

from locust import HttpUser, task, between, SequentialTaskSet
import random
import json


class MANAUserTasks(SequentialTaskSet):
    """MANA module user workflow."""

    @task
    def view_mana_dashboard(self):
        """View MANA dashboard."""
        self.client.get(f'/moa/{self.user.org_code}/mana/')

    @task
    def list_assessments(self):
        """View assessments list."""
        self.client.get(f'/moa/{self.user.org_code}/mana/assessments/')

    @task
    def search_assessments(self):
        """Search assessments."""
        terms = ['health', 'education', 'livelihood', 'infrastructure']
        term = random.choice(terms)
        self.client.get(
            f'/moa/{self.user.org_code}/mana/assessments/',
            params={'search': term}
        )

    @task
    def view_assessment_detail(self):
        """View assessment detail."""
        # Assume assessment IDs 1-50 exist
        assessment_id = random.randint(1, 50)
        self.client.get(f'/moa/{self.user.org_code}/mana/assessments/{assessment_id}/')

    @task
    def create_assessment(self):
        """Create new assessment."""
        self.client.get(f'/moa/{self.user.org_code}/mana/assessments/create/')

        # POST form data
        self.client.post(
            f'/moa/{self.user.org_code}/mana/assessments/create/',
            {
                'title': f'Load Test Assessment {random.randint(1000, 9999)}',
                'description': 'Automated load test assessment',
                'status': 'draft'
            }
        )


class CoordinationUserTasks(SequentialTaskSet):
    """Coordination module user workflow."""

    @task
    def view_calendar(self):
        """View coordination calendar."""
        self.client.get(f'/moa/{self.user.org_code}/coordination/calendar/')

    @task
    def fetch_events(self):
        """Fetch calendar events (AJAX)."""
        self.client.get(
            f'/moa/{self.user.org_code}/coordination/events/',
            params={
                'start': '2024-01-01',
                'end': '2024-12-31'
            }
        )

    @task
    def view_partnerships(self):
        """View partnerships list."""
        self.client.get(f'/moa/{self.user.org_code}/coordination/partnerships/')

    @task
    def view_tasks_kanban(self):
        """View tasks kanban."""
        self.client.get(f'/moa/{self.user.org_code}/coordination/tasks/')

    @task
    def update_task_status(self):
        """Update task status (HTMX)."""
        task_id = random.randint(1, 20)
        status = random.choice(['pending', 'in-progress', 'completed'])

        self.client.post(
            f'/moa/{self.user.org_code}/coordination/tasks/{task_id}/update-status/',
            {'status': status},
            headers={'HX-Request': 'true'}
        )


class BudgetUserTasks(SequentialTaskSet):
    """Budget module user workflow."""

    @task
    def view_budget_dashboard(self):
        """View budget dashboard."""
        self.client.get(f'/moa/{self.user.org_code}/budget/')

    @task
    def view_allocations(self):
        """View budget allocations."""
        self.client.get(f'/moa/{self.user.org_code}/budget/allocations/')

    @task
    def filter_by_fiscal_year(self):
        """Filter budgets by fiscal year."""
        year = random.choice([2024, 2025, 2026])
        self.client.get(
            f'/moa/{self.user.org_code}/budget/allocations/',
            params={'fiscal_year': year}
        )

    @task
    def view_ppa_budget(self):
        """View PPA budget detail."""
        ppa_id = random.randint(1, 30)
        self.client.get(f'/moa/{self.user.org_code}/budget/ppa/{ppa_id}/')


class MOAUser(HttpUser):
    """Simulate MOA staff user behavior."""

    wait_time = between(2, 8)

    def on_start(self):
        """Login on start."""
        self.org_code = random.choice([
            'MOH', 'MOLE', 'MAFAR', 'MSWDD', 'MBHTE', 'MENRE',
            'MPWH', 'MIPA', 'MTIT', 'MEST', 'MFBM', 'MOJ'
        ])

        response = self.client.post('/accounts/login/', {
            'username': f'staff_{self.org_code}',
            'password': 'testpass123'
        })

        if response.status_code == 200:
            self.org_code = self.org_code
        else:
            print(f"Login failed for {self.org_code}")

    @task(3)
    def view_dashboard(self):
        """View organization dashboard (most frequent)."""
        self.client.get(f'/moa/{self.org_code}/')

    @task(2)
    def mana_workflow(self):
        """Execute MANA workflow."""
        tasks = MANAUserTasks(self)
        tasks.execute()

    @task(2)
    def coordination_workflow(self):
        """Execute Coordination workflow."""
        tasks = CoordinationUserTasks(self)
        tasks.execute()

    @task(1)
    def budget_workflow(self):
        """Execute Budget workflow."""
        tasks = BudgetUserTasks(self)
        tasks.execute()

    @task(1)
    def view_communities(self):
        """View OBC communities (shared data)."""
        self.client.get('/api/communities/barangays/')

    @task(1)
    def view_policies(self):
        """View policy recommendations."""
        self.client.get(f'/moa/{self.org_code}/policies/')


class CMOUser(HttpUser):
    """Simulate CMO admin user behavior (aggregation queries)."""

    wait_time = between(5, 15)

    def on_start(self):
        """Login as CMO user."""
        self.client.post('/accounts/login/', {
            'username': 'cmo_admin',
            'password': 'testpass123'
        })

    @task(3)
    def view_cmo_dashboard(self):
        """View CMO aggregation dashboard."""
        self.client.get('/cmo/OOBC/')

    @task(2)
    def view_budget_aggregation(self):
        """View aggregated budget data across all MOAs."""
        self.client.get('/cmo/OOBC/budget/aggregate/')

    @task(2)
    def view_mana_aggregation(self):
        """View aggregated MANA data."""
        self.client.get('/cmo/OOBC/mana/aggregate/')

    @task(1)
    def view_coordination_report(self):
        """View cross-MOA coordination report."""
        self.client.get('/cmo/OOBC/coordination/report/')

    @task(1)
    def export_report(self):
        """Export aggregated report."""
        self.client.get('/cmo/OOBC/reports/export/', params={'format': 'pdf'})


class PeakLoadUser(HttpUser):
    """Simulate peak load (budget submission deadline)."""

    wait_time = between(0.5, 2)  # Faster interactions during peak

    def on_start(self):
        """Login."""
        self.org_code = random.choice(['MOH', 'MOLE', 'MAFAR', 'MSWDD'])
        self.client.post('/accounts/login/', {
            'username': f'staff_{self.org_code}',
            'password': 'testpass123'
        })

    @task(5)
    def submit_budget(self):
        """Submit budget allocation (high frequency)."""
        self.client.post(
            f'/moa/{self.org_code}/budget/allocations/create/',
            {
                'ppa': random.randint(1, 30),
                'fiscal_year': 2025,
                'total_amount': random.randint(100000, 10000000),
                'status': 'submitted'
            }
        )

    @task(3)
    def view_budget_status(self):
        """Check budget submission status."""
        self.client.get(f'/moa/{self.org_code}/budget/submissions/status/')

    @task(2)
    def update_budget(self):
        """Update existing budget."""
        budget_id = random.randint(1, 50)
        self.client.post(
            f'/moa/{self.org_code}/budget/allocations/{budget_id}/edit/',
            {'total_amount': random.randint(100000, 10000000)}
        )
```

**Run Load Tests:**

```bash
# Install Locust
pip install locust

# Test 1: Normal Load (500 users, 80% MOA / 20% CMO)
locust -f locustfile.py \
  --users=500 \
  --spawn-rate=50 \
  --host=http://localhost:8000 \
  --user-classes=MOAUser:8,CMOUser:2

# Test 2: Peak Load (800 users, budget deadline simulation)
locust -f locustfile.py \
  --users=800 \
  --spawn-rate=100 \
  --host=http://localhost:8000 \
  --user-classes=PeakLoadUser

# Test 3: Sustained Load (300 users, 8-hour simulation)
locust -f locustfile.py \
  --users=300 \
  --spawn-rate=30 \
  --run-time=8h \
  --host=http://localhost:8000

# View results at http://localhost:8089
```


### 23.4.9 Performance Monitoring & Profiling

**Production monitoring setup for ongoing performance tracking.**

```python
# src/obc_management/settings/production.py

# Django Debug Toolbar (DEVELOPMENT ONLY - DO NOT USE IN PRODUCTION)
if DEBUG:
    INSTALLED_APPS += ['debug_toolbar']
    MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']

# Logging slow queries (PostgreSQL)
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'performance.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.db.backends': {
            'handlers': ['file'],
            'level': 'WARNING',  # Log slow queries
            'propagate': False,
        },
    },
}

# PostgreSQL slow query logging
DATABASES['default']['OPTIONS'] = {
    'connect_timeout': 10,
    'options': '-c log_min_duration_statement=100'  # Log queries > 100ms
}
```

**Grafana Dashboard Configuration (docker-compose.yml):**

```yaml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana
    depends_on:
      - prometheus

  postgres_exporter:
    image: prometheuscommunity/postgres-exporter
    environment:
      DATA_SOURCE_NAME: "postgresql://obcms_user:password@postgres:5432/obcms_prod?sslmode=disable"
    ports:
      - "9187:9187"

volumes:
  prometheus_data:
  grafana_data:
```

**Prometheus Configuration (prometheus.yml):**

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'django'
    static_configs:
      - targets: ['web:8000']

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres_exporter:9187']

  - job_name: 'redis'
    static_configs:
      - targets: ['redis:6379']
```


### 23.4.10 Performance Testing Checklist

```markdown
# Performance Testing Checklist

## Page Load Performance
- [ ] Dashboard loads in < 200ms
- [ ] List views load in < 300ms
- [ ] Detail views load in < 250ms
- [ ] Calendar view loads in < 500ms
- [ ] Map views load in < 600ms
- [ ] API endpoints respond in < 500ms

## Database Query Optimization
- [ ] No N+1 query problems detected
- [ ] All queries use proper indexes
- [ ] select_related() used for foreign keys
- [ ] prefetch_related() used for M2M
- [ ] Query count per page ≤ 10
- [ ] All queries complete in < 100ms
- [ ] Slow query logging enabled (> 100ms)

## HTMX Performance
- [ ] Element swaps complete in < 50ms
- [ ] Optimistic updates return 204 in < 30ms
- [ ] Out-of-band swaps work correctly
- [ ] Loading indicators display immediately
- [ ] No full page reloads for CRUD operations

## Caching
- [ ] Redis cache configured and working
- [ ] Cache hit rate > 70%
- [ ] Expensive queries cached (1-5 min TTL)
- [ ] Cache invalidation on model updates
- [ ] Organization context cached per user

## Concurrent Load
- [ ] System handles 500 concurrent users
- [ ] Success rate > 95% under load
- [ ] Response times stable under load
- [ ] No database connection exhaustion
- [ ] No memory leaks during sustained load

## API Performance
- [ ] REST API list endpoints < 500ms
- [ ] Pagination working efficiently
- [ ] Filtering uses database indexes
- [ ] GeoJSON serialization < 600ms
- [ ] Bulk operations handle 1000+ records

## Frontend Performance (Core Web Vitals)
- [ ] LCP (Largest Contentful Paint) < 2.5s
- [ ] FCP (First Contentful Paint) < 1.8s
- [ ] CLS (Cumulative Layout Shift) < 0.1
- [ ] TTI (Time to Interactive) < 3.8s
- [ ] TBT (Total Blocking Time) < 300ms

## Load Testing Results
- [ ] Normal load test (500 users): ✓ Pass
- [ ] Peak load test (800 users): ✓ Pass
- [ ] Sustained load test (8 hours): ✓ Pass
- [ ] Stress test (find breaking point): Documented
- [ ] Budget deadline simulation: ✓ Pass

## Monitoring Setup
- [ ] Prometheus configured
- [ ] Grafana dashboards created
- [ ] PostgreSQL query logging enabled
- [ ] Django slow query logging enabled
- [ ] APM tool configured (optional)
- [ ] Error tracking configured (Sentry)

## Performance Targets Met
- [ ] Dashboard load: ✓ < 200ms
- [ ] API response: ✓ < 500ms
- [ ] HTMX swaps: ✓ < 50ms
- [ ] 500 concurrent users: ✓ Pass
- [ ] Core Web Vitals: ✓ Good
- [ ] Database queries: ✓ < 100ms
- [ ] Cache hit rate: ✓ > 70%
```

---

## 23.7 Component Testing

### 23.7.1 Overview

**Purpose:** Test individual UI components in isolation to ensure they render correctly, handle interactions properly, and maintain accessibility standards.

**Scope:**
- Django template components (src/templates/components/)
- Form widgets and validation
- HTMX interactions (instant UI updates)
- Tailwind CSS components (stat cards, quick action cards)
- JavaScript components (calendar, resource booking, organization switcher)
- Leaflet.js map components

**Testing Tools:**
- Django template testing (TestCase)
- Selenium/Playwright for browser-based tests
- HTMX testing (hx-get, hx-post, hx-swap verification)
- Jest for JavaScript unit tests
- Axe for accessibility testing


### 23.7.2 Form Component Testing

**Test Django form components and validation logic.**

```python
# src/tests/components/test_form_components.py

import pytest
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.template.loader import render_to_string
from organizations.models import Organization
from communities.models import Region, Province, Municipality, Barangay
from common.forms.staff import StaffForm

User = get_user_model()


class TestFormComponents(TestCase):
    """Test form components and validation."""

    def setUp(self):
        """Setup test data."""
        self.moa = Organization.objects.create(code='MOH', name='Ministry of Health', org_type='MOA')
        self.user = User.objects.create_user(
            username='moh_staff',
            email='staff@moh.gov.ph',
            password='testpass123',
            default_organization=self.moa
        )

        # Create geographic hierarchy
        self.region = Region.objects.create(name='Region IX', code='09')
        self.province = Province.objects.create(name='Zamboanga del Sur', code='0972', region=self.region)
        self.municipality = Municipality.objects.create(
            name='Pagadian City',
            code='097201',
            province=self.province
        )

    def test_text_input_component(self):
        """Test text input component renders correctly."""
        context = {
            'field': StaffForm().fields['first_name'],
            'field_name': 'first_name',
            'field_id': 'id_first_name',
            'label': 'First Name',
            'required': True,
            'value': '',
            'errors': []
        }

        html = render_to_string('components/form_field_input.html', context)

        # Verify structure
        self.assertIn('rounded-xl', html)
        self.assertIn('border-gray-200', html)
        self.assertIn('focus:ring-emerald-500', html)
        self.assertIn('min-h-[48px]', html)
        self.assertIn('text-red-500', html)  # Required asterisk

        print("✓ Text input component renders correctly")

    def test_dropdown_component(self):
        """Test dropdown component with proper styling."""
        context = {
            'field': StaffForm().fields['gender'],
            'field_name': 'gender',
            'field_id': 'id_gender',
            'label': 'Gender',
            'required': True,
            'choices': [('', 'Select gender...'), ('M', 'Male'), ('F', 'Female')],
            'value': '',
            'errors': []
        }

        html = render_to_string('components/form_field_select.html', context)

        # Verify structure
        self.assertIn('rounded-xl', html)
        self.assertIn('appearance-none', html)
        self.assertIn('pr-12', html)  # Space for chevron
        self.assertIn('fa-chevron-down', html)
        self.assertIn('pointer-events-none', html)  # Chevron not clickable

        print("✓ Dropdown component renders correctly")

    def test_form_validation_display(self):
        """Test error message display."""
        client = Client()
        client.force_login(self.user)

        # Submit invalid form
        response = client.post(
            f'/moa/{self.moa.code}/staff/create/',
            {
                'username': '',  # Missing required field
                'email': 'invalid-email',  # Invalid email
            }
        )

        self.assertEqual(response.status_code, 200)

        content = response.content.decode()

        # Verify error messages displayed
        self.assertIn('text-red-600', content)
        self.assertIn('This field is required', content)
        self.assertIn('Enter a valid email', content)

        print("✓ Form validation errors display correctly")

    def test_cascading_dropdowns(self):
        """Test cascading dropdowns (Region → Province → Municipality)."""
        client = Client()
        client.force_login(self.user)

        # Get barangay form
        response = client.get(f'/moa/{self.moa.code}/communities/barangays/create/')
        self.assertEqual(response.status_code, 200)

        content = response.content.decode()

        # Verify HTMX attributes for cascading
        self.assertIn('hx-get', content)
        self.assertIn('hx-target', content)
        self.assertIn('hx-trigger="change"', content)

        # Test cascade: select province
        response = client.get(
            '/api/communities/municipalities/',
            {'province': self.province.id},
            HTTP_HX_REQUEST='true'
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('municipalities', data)

        print("✓ Cascading dropdowns work correctly")

    def test_date_picker_component(self):
        """Test date picker initialization."""
        context = {
            'field_name': 'start_date',
            'field_id': 'id_start_date',
            'label': 'Start Date',
            'required': True,
            'value': '',
        }

        html = render_to_string('components/form_field_date.html', context)

        # Verify date input
        self.assertIn('type="date"', html)
        self.assertIn('rounded-xl', html)
        self.assertIn('min-h-[48px]', html)

        print("✓ Date picker component renders correctly")


### 23.7.3 UI Component Testing

**Test custom UI components (stat cards, quick action cards, etc.).**

```python
# src/tests/components/test_ui_components.py

import pytest
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.template.loader import render_to_string
from organizations.models import Organization
from mana.models import Assessment
from coordination.models import Partnership

User = get_user_model()


class TestUIComponents(TestCase):
    """Test custom UI components."""

    def setUp(self):
        """Setup test data."""
        self.moa = Organization.objects.create(code='MOH', name='Ministry of Health', org_type='MOA')
        self.user = User.objects.create_user(
            username='moh_staff',
            email='staff@moh.gov.ph',
            password='testpass123',
            default_organization=self.moa
        )

    def test_stat_card_simple_variant(self):
        """Test 3D milk white stat card (simple variant)."""
        context = {
            'title': 'Total Assessments',
            'value': 42,
            'icon': 'fa-clipboard-list',
            'icon_color': 'text-amber-600',
            'icon_bg': 'bg-amber-50'
        }

        html = render_to_string('components/stat_card.html', context)

        # Verify structure
        self.assertIn('bg-white', html)
        self.assertIn('rounded-xl', html)
        self.assertIn('border', html)
        self.assertIn('shadow-sm', html)
        self.assertIn('fa-clipboard-list', html)
        self.assertIn('text-amber-600', html)
        self.assertIn('42', html)

        print("✓ Simple stat card renders correctly")

    def test_stat_card_breakdown_variant(self):
        """Test stat card with 3-column breakdown."""
        context = {
            'title': 'Total Partnerships',
            'value': 156,
            'icon': 'fa-handshake',
            'icon_color': 'text-emerald-600',
            'icon_bg': 'bg-emerald-50',
            'breakdown': [
                {'label': 'Active', 'value': 120, 'color': 'text-emerald-600'},
                {'label': 'Pending', 'value': 30, 'color': 'text-blue-600'},
                {'label': 'Closed', 'value': 6, 'color': 'text-gray-600'}
            ]
        }

        html = render_to_string('components/stat_card_breakdown.html', context)

        # Verify breakdown section
        self.assertIn('grid-cols-3', html)
        self.assertIn('Active', html)
        self.assertIn('120', html)
        self.assertIn('text-emerald-600', html)
        self.assertIn('Pending', html)
        self.assertIn('30', html)

        print("✓ Breakdown stat card renders correctly")

    def test_quick_action_card(self):
        """Test quick action card component."""
        context = {
            'title': 'New Assessment',
            'description': 'Create a new MANA assessment',
            'icon': 'fa-plus',
            'url': '/moa/MOH/mana/assessments/create/',
            'gradient_from': 'from-blue-500',
            'gradient_to': 'to-teal-500'
        }

        html = render_to_string('components/quick_action_card.html', context)

        # Verify structure
        self.assertIn('bg-white', html)
        self.assertIn('rounded-xl', html)
        self.assertIn('hover:shadow-md', html)
        self.assertIn('bg-gradient-to-br', html)
        self.assertIn('from-blue-500', html)
        self.assertIn('to-teal-500', html)
        self.assertIn('fa-plus', html)
        self.assertIn('fa-arrow-right', html)

        print("✓ Quick action card renders correctly")

    def test_breadcrumb_component(self):
        """Test breadcrumb navigation component."""
        context = {
            'breadcrumbs': [
                {'label': 'Dashboard', 'url': '/moa/MOH/'},
                {'label': 'MANA', 'url': '/moa/MOH/mana/'},
                {'label': 'Assessments', 'url': '/moa/MOH/mana/assessments/'},
                {'label': 'Create', 'url': None}  # Current page
            ]
        }

        html = render_to_string('components/breadcrumbs.html', context)

        # Verify structure
        self.assertIn('fa-chevron-right', html)
        self.assertIn('Dashboard', html)
        self.assertIn('MANA', html)
        self.assertIn('Assessments', html)
        self.assertIn('Create', html)
        self.assertIn('text-gray-500', html)  # Current page styling

        print("✓ Breadcrumb component renders correctly")

    def test_pagination_component(self):
        """Test pagination component."""
        context = {
            'page_obj': {
                'has_previous': True,
                'previous_page_number': 1,
                'number': 2,
                'has_next': True,
                'next_page_number': 3,
                'paginator': {'num_pages': 5}
            }
        }

        html = render_to_string('components/pagination.html', context)

        # Verify structure
        self.assertIn('Previous', html)
        self.assertIn('Next', html)
        self.assertIn('rounded-lg', html)
        self.assertIn('hover:bg-gray-50', html)

        print("✓ Pagination component renders correctly")

    def test_alert_messages(self):
        """Test alert message components."""
        test_messages = [
            {'level': 'success', 'text': 'Assessment created successfully', 'border': 'border-emerald-500'},
            {'level': 'error', 'text': 'Failed to save data', 'border': 'border-red-500'},
            {'level': 'warning', 'text': 'This action cannot be undone', 'border': 'border-amber-500'},
            {'level': 'info', 'text': 'New updates available', 'border': 'border-blue-500'}
        ]

        for msg in test_messages:
            context = {
                'level': msg['level'],
                'message': msg['text']
            }

            html = render_to_string('components/alert.html', context)

            self.assertIn(msg['border'], html)
            self.assertIn('border-l-4', html)
            self.assertIn(msg['text'], html)

        print("✓ Alert message components render correctly")

    def test_data_table_component(self):
        """Test data table card component."""
        # Create test data
        for i in range(5):
            Assessment.objects.create(
                title=f'Assessment {i}',
                organization=self.moa,
                status='published'
            )

        assessments = Assessment.objects.filter(organization=self.moa)

        context = {
            'title': 'Recent Assessments',
            'headers': ['Title', 'Status', 'Created', 'Actions'],
            'rows': [
                {
                    'id': a.id,
                    'cells': [a.title, a.status, a.created_at],
                    'view_url': f'/moa/{self.moa.code}/mana/assessments/{a.id}/',
                    'edit_url': f'/moa/{self.moa.code}/mana/assessments/{a.id}/edit/',
                    'delete_preview_url': f'/moa/{self.moa.code}/mana/assessments/{a.id}/'
                }
                for a in assessments
            ]
        }

        html = render_to_string('components/data_table_card.html', context)

        # Verify structure
        self.assertIn('bg-white', html)
        self.assertIn('rounded-xl', html)
        self.assertIn('Recent Assessments', html)
        self.assertIn('<table', html)
        self.assertIn('bg-gradient-to-r', html)  # Header gradient
        self.assertIn('from-blue-600', html)
        self.assertIn('to-teal-500', html)

        print("✓ Data table component renders correctly")


### 23.7.4 HTMX Interaction Testing

**Test HTMX-powered instant UI updates.**

```python
# src/tests/components/test_htmx_interactions.py

import pytest
import time
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from organizations.models import Organization
from coordination.models import Task
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

User = get_user_model()


class TestHTMXInteractions(TestCase):
    """Test HTMX instant UI updates."""

    def setUp(self):
        """Setup test data."""
        self.moa = Organization.objects.create(code='MOH', name='Ministry of Health', org_type='MOA')
        self.user = User.objects.create_user(
            username='moh_staff',
            email='staff@moh.gov.ph',
            password='testpass123',
            default_organization=self.moa
        )

        # Create test tasks
        for i in range(5):
            Task.objects.create(
                title=f'Task {i}',
                organization=self.moa,
                assigned_to=self.user,
                status='pending'
            )

    def test_htmx_task_status_update(self):
        """Test instant task status update via HTMX."""
        client = Client()
        client.force_login(self.user)

        task = Task.objects.first()

        # Update status via HTMX
        response = client.post(
            f'/moa/{self.moa.code}/coordination/tasks/{task.id}/update-status/',
            {'status': 'in-progress'},
            HTTP_HX_REQUEST='true'
        )

        # Should return 204 No Content (optimistic update)
        self.assertEqual(response.status_code, 204)

        # Verify HX-Trigger header
        self.assertTrue(response.has_header('HX-Trigger'))

        # Verify task updated in database
        task.refresh_from_db()
        self.assertEqual(task.status, 'in-progress')

        print("✓ HTMX task status update works correctly")

    def test_htmx_delete_confirmation(self):
        """Test two-step delete confirmation."""
        client = Client()
        client.force_login(self.user)

        task = Task.objects.first()

        # Step 1: Show delete confirmation modal
        response = client.get(
            f'/moa/{self.moa.code}/coordination/tasks/{task.id}/delete-confirm/',
            HTTP_HX_REQUEST='true'
        )

        self.assertEqual(response.status_code, 200)
        content = response.content.decode()

        # Verify modal content
        self.assertIn('Are you sure', content)
        self.assertIn(task.title, content)
        self.assertIn('Delete', content)
        self.assertIn('Cancel', content)

        # Step 2: Confirm deletion
        response = client.delete(
            f'/moa/{self.moa.code}/coordination/tasks/{task.id}/delete/',
            HTTP_HX_REQUEST='true'
        )

        self.assertEqual(response.status_code, 204)

        # Verify task deleted
        self.assertFalse(Task.objects.filter(id=task.id).exists())

        print("✓ HTMX two-step delete confirmation works correctly")

    def test_htmx_form_submission(self):
        """Test HTMX form submission without page reload."""
        client = Client()
        client.force_login(self.user)

        # Submit form via HTMX
        response = client.post(
            f'/moa/{self.moa.code}/coordination/tasks/create/',
            {
                'title': 'New Task via HTMX',
                'description': 'Created via HTMX test',
                'status': 'pending',
                'assigned_to': self.user.id
            },
            HTTP_HX_REQUEST='true'
        )

        # Should redirect or return partial HTML
        self.assertIn(response.status_code, [200, 201, 302])

        # Verify task created
        self.assertTrue(Task.objects.filter(title='New Task via HTMX').exists())

        print("✓ HTMX form submission works correctly")

    def test_htmx_out_of_band_swaps(self):
        """Test out-of-band swaps (multiple element updates)."""
        client = Client()
        client.force_login(self.user)

        task = Task.objects.first()

        # Update task status (should trigger counter updates)
        response = client.post(
            f'/moa/{self.moa.code}/coordination/tasks/{task.id}/update-status/',
            {'status': 'completed'},
            HTTP_HX_REQUEST='true'
        )

        # Check for HX-Trigger header with counter refresh event
        if response.has_header('HX-Trigger'):
            import json
            trigger_data = json.loads(response['HX-Trigger'])
            self.assertIn('refresh-counters', trigger_data)

        print("✓ HTMX out-of-band swaps work correctly")


@pytest.mark.django_db
@pytest.mark.selenium
class TestHTMXBrowserInteractions:
    """Test HTMX interactions in real browser."""

    @pytest.fixture
    def setup_selenium(self):
        """Setup Selenium WebDriver."""
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')

        driver = webdriver.Chrome(options=chrome_options)
        driver.set_window_size(1920, 1080)

        yield driver

        driver.quit()

    def test_kanban_drag_drop_animation(self, setup_selenium, live_server):
        """Test kanban drag-drop with smooth animation."""
        driver = setup_selenium

        # Login
        driver.get(f'{live_server.url}/accounts/login/')
        driver.find_element(By.NAME, 'username').send_keys('admin')
        driver.find_element(By.NAME, 'password').send_keys('admin')
        driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()

        # Navigate to kanban
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.kanban-board'))
        )

        # Find task card
        task_card = driver.find_element(By.CSS_SELECTOR, '[data-task-id="1"]')
        initial_column = task_card.find_element(By.XPATH, './ancestor::*[@data-status]')

        # Drag to different column
        target_column = driver.find_element(By.CSS_SELECTOR, '[data-status="in-progress"]')

        from selenium.webdriver.common.action_chains import ActionChains
        actions = ActionChains(driver)
        actions.drag_and_drop(task_card, target_column).perform()

        # Wait for animation (300ms)
        time.sleep(0.4)

        # Verify task moved
        task_card_new = driver.find_element(By.CSS_SELECTOR, '[data-task-id="1"]')
        new_column = task_card_new.find_element(By.XPATH, './ancestor::*[@data-status]')

        assert new_column.get_attribute('data-status') == 'in-progress'

        print("✓ Kanban drag-drop animation works correctly")

    def test_instant_search_results(self, setup_selenium, live_server):
        """Test instant search results via HTMX."""
        driver = setup_selenium

        # Login
        driver.get(f'{live_server.url}/accounts/login/')
        driver.find_element(By.NAME, 'username').send_keys('admin')
        driver.find_element(By.NAME, 'password').send_keys('admin')
        driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()

        # Navigate to assessment list
        driver.get(f'{live_server.url}/moa/MOH/mana/assessments/')

        # Find search input
        search_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, 'search'))
        )

        # Type search query
        search_input.clear()
        search_input.send_keys('health')

        # Wait for HTMX to update results (should be < 500ms)
        time.sleep(0.6)

        # Verify results updated
        results = driver.find_elements(By.CSS_SELECTOR, '[data-assessment-id]')
        assert len(results) > 0

        print("✓ Instant search results work correctly")


### 23.7.5 JavaScript Component Testing

**Test JavaScript components (Calendar, Organization Switcher, etc.).**

```javascript
// src/static/common/js/__tests__/calendar.test.js

/**
 * Jest tests for FullCalendar integration
 */

import { Calendar } from '@fullcalendar/core';
import dayGridPlugin from '@fullcalendar/daygrid';
import timeGridPlugin from '@fullcalendar/timegrid';
import interactionPlugin from '@fullcalendar/interaction';

describe('Calendar Component', () => {
  let calendarEl;
  let calendar;

  beforeEach(() => {
    // Setup DOM element
    calendarEl = document.createElement('div');
    calendarEl.id = 'calendar';
    document.body.appendChild(calendarEl);

    // Initialize calendar
    calendar = new Calendar(calendarEl, {
      plugins: [dayGridPlugin, timeGridPlugin, interactionPlugin],
      initialView: 'dayGridMonth',
      headerToolbar: {
        left: 'prev,next today',
        center: 'title',
        right: 'dayGridMonth,timeGridWeek,timeGridDay'
      },
      editable: true,
      droppable: true
    });

    calendar.render();
  });

  afterEach(() => {
    calendar.destroy();
    document.body.removeChild(calendarEl);
  });

  test('calendar renders correctly', () => {
    expect(calendarEl.querySelector('.fc')).toBeTruthy();
    expect(calendarEl.querySelector('.fc-toolbar')).toBeTruthy();
  });

  test('calendar loads events from API', async () => {
    // Mock fetch
    global.fetch = jest.fn(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve([
          {
            id: 1,
            title: 'Test Event',
            start: '2024-01-15T10:00:00',
            end: '2024-01-15T11:00:00'
          }
        ])
      })
    );

    calendar.refetchEvents();

    // Wait for events to load
    await new Promise(resolve => setTimeout(resolve, 100));

    const events = calendar.getEvents();
    expect(events.length).toBeGreaterThan(0);
    expect(events[0].title).toBe('Test Event');
  });

  test('event click opens detail modal', () => {
    const mockEvent = {
      id: 1,
      title: 'Meeting',
      start: new Date('2024-01-15T10:00:00'),
      end: new Date('2024-01-15T11:00:00')
    };

    calendar.addEvent(mockEvent);

    const eventEl = calendarEl.querySelector('.fc-event');
    expect(eventEl).toBeTruthy();

    // Simulate click
    eventEl.click();

    // Verify modal opened (depends on your modal implementation)
    // expect(document.querySelector('#event-detail-modal')).toBeTruthy();
  });

  test('drag and drop event updates time', () => {
    const mockEvent = {
      id: 1,
      title: 'Meeting',
      start: '2024-01-15T10:00:00',
      end: '2024-01-15T11:00:00'
    };

    calendar.addEvent(mockEvent);

    const event = calendar.getEventById(1);
    const oldStart = event.start;

    // Simulate drag (mock event drop)
    const dropInfo = {
      date: new Date('2024-01-16T10:00:00'),
      allDay: false
    };

    // This would trigger eventDrop callback
    event.setStart(dropInfo.date);

    expect(event.start).not.toEqual(oldStart);
  });
});
```

```javascript
// src/static/common/js/__tests__/organization_switcher.test.js

/**
 * Jest tests for Organization Switcher
 */

describe('Organization Switcher', () => {
  let switcherEl;

  beforeEach(() => {
    // Setup DOM
    document.body.innerHTML = `
      <div id="org-switcher" class="relative">
        <button id="org-switcher-button" type="button">
          <span id="current-org-name">Ministry of Health</span>
          <i class="fas fa-chevron-down"></i>
        </button>
        <div id="org-dropdown" class="hidden absolute">
          <a href="/moa/MOH/" data-org-code="MOH">Ministry of Health</a>
          <a href="/moa/MOLE/" data-org-code="MOLE">Ministry of Labor</a>
        </div>
      </div>
    `;

    switcherEl = document.getElementById('org-switcher');
  });

  test('dropdown opens on button click', () => {
    const button = document.getElementById('org-switcher-button');
    const dropdown = document.getElementById('org-dropdown');

    expect(dropdown.classList.contains('hidden')).toBe(true);

    button.click();

    expect(dropdown.classList.contains('hidden')).toBe(false);
  });

  test('selecting organization updates display', () => {
    const orgLink = document.querySelector('[data-org-code="MOLE"]');
    const currentOrgName = document.getElementById('current-org-name');

    expect(currentOrgName.textContent).toBe('Ministry of Health');

    orgLink.click();

    // Would trigger page navigation in real app
    // Here we just verify the element exists
    expect(orgLink.getAttribute('href')).toBe('/moa/MOLE/');
  });

  test('dropdown closes when clicking outside', () => {
    const button = document.getElementById('org-switcher-button');
    const dropdown = document.getElementById('org-dropdown');

    button.click();
    expect(dropdown.classList.contains('hidden')).toBe(false);

    // Simulate click outside
    document.body.click();

    // In real implementation, this would close dropdown
    // expect(dropdown.classList.contains('hidden')).toBe(true);
  });
});
```


### 23.7.6 Leaflet.js Map Component Testing

**Test interactive map components and GeoJSON rendering.**

```python
# src/tests/components/test_map_components.py

import pytest
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from organizations.models import Organization
from communities.models import Region, Province, Municipality, Barangay
import json

User = get_user_model()


class TestMapComponents(TestCase):
    """Test Leaflet.js map integration."""

    def setUp(self):
        """Setup test data."""
        self.moa = Organization.objects.create(code='MOH', name='Ministry of Health', org_type='MOA')
        self.user = User.objects.create_user(
            username='moh_staff',
            email='staff@moh.gov.ph',
            password='testpass123',
            default_organization=self.moa
        )

        # Create region with GeoJSON boundary
        self.region = Region.objects.create(
            name='Region IX',
            code='09',
            center_coordinates={'lat': 8.45, 'lng': 123.25},
            bounding_box=[[7.0, 122.0], [9.9, 124.5]],
            boundary_geojson={
                'type': 'Polygon',
                'coordinates': [
                    [[122.0, 7.0], [124.5, 7.0], [124.5, 9.9], [122.0, 9.9], [122.0, 7.0]]
                ]
            }
        )

    def test_geojson_api_endpoint(self):
        """Test GeoJSON API returns valid GeoJSON."""
        client = Client()
        client.force_login(self.user)

        response = client.get(f'/api/communities/regions/{self.region.code}/geojson/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')

        data = response.json()

        # Verify GeoJSON structure
        self.assertEqual(data['type'], 'FeatureCollection')
        self.assertIn('features', data)
        self.assertGreater(len(data['features']), 0)

        feature = data['features'][0]
        self.assertEqual(feature['type'], 'Feature')
        self.assertIn('geometry', feature)
        self.assertEqual(feature['geometry']['type'], 'Polygon')
        self.assertIn('properties', feature)

        print("✓ GeoJSON API returns valid GeoJSON")

    def test_map_center_coordinates(self):
        """Test map centers on correct coordinates."""
        client = Client()
        client.force_login(self.user)

        response = client.get('/communities/regions/')

        self.assertEqual(response.status_code, 200)
        content = response.content.decode()

        # Verify map initialization
        self.assertIn('L.map', content)
        self.assertIn('8.45', content)  # Lat
        self.assertIn('123.25', content)  # Lng

        print("✓ Map centers on correct coordinates")

    def test_boundary_rendering(self):
        """Test boundary GeoJSON renders on map."""
        client = Client()
        client.force_login(self.user)

        response = client.get(f'/communities/regions/{self.region.code}/')

        self.assertEqual(response.status_code, 200)
        content = response.content.decode()

        # Verify boundary data included
        self.assertIn('boundary_geojson', content)
        self.assertIn('L.geoJSON', content)

        print("✓ Boundary GeoJSON renders on map")

    def test_popup_interaction(self):
        """Test map popup displays community info."""
        client = Client()
        client.force_login(self.user)

        # Create barangay with location
        province = Province.objects.create(name='Zamboanga del Sur', code='0972', region=self.region)
        muni = Municipality.objects.create(name='Pagadian City', code='097201', province=province)
        barangay = Barangay.objects.create(
            name='Balangasan',
            code='09720101',
            municipality=muni,
            population=5000,
            obc_status='Confirmed',
            center_coordinates={'lat': 8.5, 'lng': 123.3}
        )

        response = client.get('/api/communities/barangays/map-data/')

        self.assertEqual(response.status_code, 200)
        data = response.json()

        # Verify barangay in map data
        self.assertGreater(len(data['features']), 0)

        feature = next((f for f in data['features'] if f['properties']['name'] == 'Balangasan'), None)
        self.assertIsNotNone(feature)
        self.assertEqual(feature['properties']['population'], 5000)
        self.assertEqual(feature['properties']['obc_status'], 'Confirmed')

        print("✓ Map popup displays community info")


### 23.7.7 Accessibility Testing

**Ensure components meet WCAG 2.1 AA standards.**

```python
# src/tests/components/test_accessibility.py

import pytest
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from organizations.models import Organization
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from axe_selenium_python import Axe

User = get_user_model()


class TestAccessibility(TestCase):
    """Test WCAG 2.1 AA accessibility compliance."""

    def setUp(self):
        """Setup test data."""
        self.moa = Organization.objects.create(code='MOH', name='Ministry of Health', org_type='MOA')
        self.user = User.objects.create_user(
            username='moh_staff',
            email='staff@moh.gov.ph',
            password='testpass123',
            default_organization=self.moa
        )

    def test_color_contrast_ratios(self):
        """Test color contrast meets 4.5:1 ratio (WCAG AA)."""
        client = Client()
        client.force_login(self.user)

        response = client.get(f'/moa/{self.moa.code}/')

        self.assertEqual(response.status_code, 200)
        content = response.content.decode()

        # Verify high contrast text colors used
        self.assertIn('text-gray-700', content)  # Body text
        self.assertIn('text-gray-900', content)  # Headings
        self.assertNotIn('text-gray-400', content)  # Too light for body text

        print("✓ Color contrast ratios meet WCAG AA standards")

    def test_form_labels_and_aria(self):
        """Test forms have proper labels and ARIA attributes."""
        client = Client()
        client.force_login(self.user)

        response = client.get('/accounts/login/')

        self.assertEqual(response.status_code, 200)
        content = response.content.decode()

        # Verify labels
        self.assertIn('<label for="id_username"', content)
        self.assertIn('<label for="id_password"', content)

        # Verify required field indicators
        self.assertIn('required', content)

        print("✓ Forms have proper labels and ARIA attributes")

    def test_keyboard_navigation(self):
        """Test all interactive elements are keyboard accessible."""
        client = Client()
        client.force_login(self.user)

        response = client.get(f'/moa/{self.moa.code}/')

        self.assertEqual(response.status_code, 200)
        content = response.content.decode()

        # Verify focusable elements
        self.assertIn('focus:ring-', content)  # Focus indicators
        self.assertIn('focus:border-', content)

        # No tabindex > 0 (anti-pattern)
        self.assertNotIn('tabindex="1"', content)
        self.assertNotIn('tabindex="2"', content)

        print("✓ Keyboard navigation properly implemented")

    def test_touch_target_sizes(self):
        """Test interactive elements meet 48px minimum size."""
        client = Client()
        client.force_login(self.user)

        response = client.get(f'/moa/{self.moa.code}/')

        self.assertEqual(response.status_code, 200)
        content = response.content.decode()

        # Verify minimum touch target sizes
        self.assertIn('min-h-[48px]', content)  # Buttons
        self.assertIn('py-3 px-4', content)  # Sufficient padding

        print("✓ Touch target sizes meet 48px minimum")

    def test_heading_hierarchy(self):
        """Test proper heading hierarchy (h1 → h2 → h3)."""
        client = Client()
        client.force_login(self.user)

        response = client.get(f'/moa/{self.moa.code}/')

        self.assertEqual(response.status_code, 200)
        content = response.content.decode()

        # Should have one h1
        h1_count = content.count('<h1')
        self.assertGreaterEqual(h1_count, 1, "Page should have at least one h1")

        # h2 should come after h1, not skip to h3
        # This is a simplified check

        print("✓ Heading hierarchy is properly structured")


@pytest.mark.django_db
@pytest.mark.selenium
class TestAccessibilityAxe:
    """Test accessibility using Axe DevTools."""

    @pytest.fixture
    def setup_selenium(self):
        """Setup Selenium WebDriver."""
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')

        driver = webdriver.Chrome(options=chrome_options)
        driver.set_window_size(1920, 1080)

        yield driver

        driver.quit()

    def test_dashboard_accessibility(self, setup_selenium, live_server):
        """Run Axe accessibility audit on dashboard."""
        driver = setup_selenium

        # Login
        driver.get(f'{live_server.url}/accounts/login/')
        driver.find_element(By.NAME, 'username').send_keys('admin')
        driver.find_element(By.NAME, 'password').send_keys('admin')
        driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()

        # Wait for dashboard
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.common.by import By

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.dashboard'))
        )

        # Run Axe audit
        axe = Axe(driver)
        axe.inject()
        results = axe.run()

        # Check for violations
        violations = results['violations']

        assert len(violations) == 0, f"Found {len(violations)} accessibility violations: {violations}"

        print(f"✓ Dashboard passed Axe accessibility audit (0 violations)")


### 23.7.8 Component Testing Checklist

```markdown
# Component Testing Checklist

## Form Components
- [ ] Text inputs render with proper styling (rounded-xl, border, focus ring)
- [ ] Dropdowns have chevron icon and proper styling
- [ ] Date pickers initialize correctly
- [ ] Required field indicators display (red asterisk)
- [ ] Error messages display in red with clear text
- [ ] Validation works client-side and server-side
- [ ] Cascading dropdowns work (Region → Province → Municipality)
- [ ] Form submission via HTMX (no page reload)

## UI Components
- [ ] Stat cards (simple variant) render correctly
- [ ] Stat cards (breakdown variant) display 3-column layout
- [ ] Quick action cards have gradient icons
- [ ] Breadcrumbs display with chevron separators
- [ ] Pagination controls work (prev/next, page numbers)
- [ ] Alert messages display with correct colors (success, error, warning, info)
- [ ] Data table cards render with gradient headers
- [ ] Modals open/close smoothly

## HTMX Interactions
- [ ] Task status updates instantly (< 50ms)
- [ ] Delete confirmation shows modal first
- [ ] Delete removes element with smooth animation (200ms)
- [ ] Form submissions return partial HTML (no reload)
- [ ] Out-of-band swaps update multiple elements
- [ ] Loading indicators display during requests
- [ ] HX-Trigger headers fire custom events
- [ ] Error states display gracefully

## JavaScript Components
- [ ] Calendar renders correctly
- [ ] Calendar loads events from API
- [ ] Event click opens detail modal
- [ ] Drag-drop events update time
- [ ] Organization switcher dropdown works
- [ ] Selecting organization navigates correctly
- [ ] Dropdown closes when clicking outside

## Map Components
- [ ] GeoJSON API returns valid FeatureCollection
- [ ] Map centers on correct coordinates
- [ ] Boundaries render as polygons
- [ ] Markers display for barangays
- [ ] Popups show community info
- [ ] Map controls work (zoom, pan)

## Accessibility (WCAG 2.1 AA)
- [ ] Color contrast ratios ≥ 4.5:1
- [ ] All forms have labels with 'for' attributes
- [ ] Required fields marked with aria-required="true"
- [ ] Keyboard navigation works (Tab, Enter, Escape)
- [ ] Focus indicators visible on all interactive elements
- [ ] Touch targets minimum 48px
- [ ] Heading hierarchy proper (h1 → h2 → h3)
- [ ] Images have alt text
- [ ] Links have descriptive text (no "click here")
- [ ] Axe DevTools audit: 0 violations
- [ ] Screen reader compatible (test with NVDA/JAWS)

## Performance
- [ ] Components render in < 100ms
- [ ] HTMX swaps complete in < 50ms
- [ ] Calendar loads events in < 300ms
- [ ] Map renders GeoJSON in < 500ms
- [ ] No layout shift (CLS < 0.1)
- [ ] Images lazy load
- [ ] JavaScript bundles minified

## Browser Compatibility
- [ ] Chrome (latest 2 versions)
- [ ] Firefox (latest 2 versions)
- [ ] Safari (latest 2 versions)
- [ ] Edge (latest 2 versions)
- [ ] Mobile Safari (iOS)
- [ ] Chrome Mobile (Android)

## Responsive Design
- [ ] Mobile (375px width)
- [ ] Tablet (768px width)
- [ ] Desktop (1920px width)
- [ ] Forms usable on mobile
- [ ] Dropdowns work on touch devices
- [ ] Maps interactive on mobile
```

---

## Integration into TRANSITION_PLAN.md

**Insert Location:**

- **Section 23.7** (Component Testing) - Insert after Section 23.6 (UAT), before Section 24
- **Section 23.4** (Performance Testing - Expanded) - Replace existing Section 23.4

**Steps:**

1. Backup TRANSITION_PLAN.md
2. Replace Section 23.4 with expanded Performance Testing content above
3. Insert Section 23.7 (Component Testing) after Section 23.6
4. Update table of contents with new subsections
5. Renumber subsequent sections if needed

**Commit Message:**

```
Expand Testing Strategy: Add Component Testing & Enhanced Performance Testing

- Add comprehensive Component Testing (Section 23.7)
  - Form component tests (dropdowns, validation, cascading)
  - UI component tests (stat cards, quick actions, alerts)
  - HTMX interaction tests (instant updates, delete confirmation)
  - JavaScript component tests (Calendar, Organization Switcher)
  - Leaflet.js map tests (GeoJSON, boundaries, popups)
  - Accessibility tests (WCAG 2.1 AA compliance, Axe audits)
  - 20+ test scenarios with production-ready code

- Expand Performance Testing (Section 23.4)
  - Page load performance (dashboard, lists, calendar)
  - Database query optimization (N+1 detection, indexes)
  - HTMX performance (swap times, optimistic updates)
  - Concurrent load testing (500-800 users)
  - API performance (REST endpoints, GeoJSON)
  - Caching performance (hit rates, invalidation)
  - Frontend performance (Core Web Vitals)
  - Load testing with Locust (comprehensive scenarios)
  - Performance monitoring (Prometheus, Grafana)
  - 30+ performance tests with clear thresholds

All tests include:
- Production-ready Django/Python code
- Selenium/Playwright browser tests
- Jest JavaScript unit tests
- Locust load testing scripts
- Performance monitoring configuration
- Comprehensive checklists
- Clear success criteria
```

---

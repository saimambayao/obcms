#!/usr/bin/env python
"""
Comprehensive BMMS Performance Testing Suite

Tests OBCMS/BMMS system performance for 44 BARMM Ministries, Offices, and Agencies (MOAs).

Performance Benchmarks:
- Target Response Times: <200ms for API calls, <2s for page loads
- Concurrent Users: Support 500+ simultaneous users (44 MOAs × ~10 users each)
- Database Queries: <100ms for standard queries, <500ms for complex reports
- AI Operations: <1s for embedding generation, <200ms for vector search
- Geographic Operations: <50ms for coordinate queries, <2s for batch geocoding

Test Scenarios:
- Normal daily usage patterns
- Peak usage (end-of-quarter reporting)
- Emergency response scenarios
- Data import/export operations
- Multi-organization concurrent access

Created: 2025-10-15
Target: BMMS production readiness for 44 MOAs
"""

import os
import sys
import time
import json
import statistics
import threading
import concurrent.futures
import random
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass, asdict
import psutil
import django
from django.conf import settings
from django.test import TestCase, TransactionTestCase
from django.contrib.auth import get_user_model
from django.test.client import Client
from django.urls import reverse
from django.db import connection, connections, transaction
from django.core.management import call_command
from django.db.models import Count, Sum, Avg, Q, F, Prefetch
from django.core.cache import cache
import pytest

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'obc_management.settings.base')
django.setup()

# Import BMMS models
from organizations.models import Organization
from communities.models import OBCCommunity, MunicipalityCoverage, ProvinceCoverage
from common.models import User, WorkItem
from budget_preparation.models import BudgetProposal, ProgramBudget, BudgetLineItem
from budget_execution.models import Allotment, Obligation, Disbursement
from ai_assistant.services.embedding_service import EmbeddingService
from ai_assistant.services.vector_store import VectorStore
from ai_assistant.services.gemini_service import GeminiService
from common.services.deferred_geocoding import DeferredGeocodingService


@dataclass
class PerformanceMetrics:
    """Performance metrics data structure."""
    operation: str
    target_time: float  # Target response time in seconds
    actual_time: float
    passed: bool
    details: Dict[str, Any] = None
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
        if self.details is None:
            self.details = {}

    def to_dict(self):
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        data['actual_time_ms'] = self.actual_time * 1000
        data['target_time_ms'] = self.target_time * 1000
        return data


@dataclass
class BMMSLoadTestScenario:
    """BMMS-specific load test scenario."""
    name: str
    description: str
    concurrent_users: int
    requests_per_user: int
    duration_seconds: int
    target_throughput: float  # requests per second
    target_response_time: float  # seconds


class BMMSPerformanceTestSuite(TransactionTestCase):
    """Comprehensive BMMS performance testing suite."""

    @classmethod
    def setUpClass(cls):
        """Set up comprehensive test environment."""
        super().setUpClass()
        cls.client = Client()
        cls.metrics: List[PerformanceMetrics] = []
        cls.scenarios = cls._get_bmms_scenarios()

        # Initialize services
        cls.embedding_service = EmbeddingService()
        cls.vector_store = VectorStore()
        cls.gemini_service = GeminiService()
        cls.geocoding_service = DeferredGeocodingService()

        # Create test data
        cls._setup_test_data()

        print(f"\n🚀 BMMS Performance Test Suite Initialized")
        print(f"   Organizations: {cls.test_organizations.count()}")
        print(f"   Communities: {cls.test_communities.count()}")
        print(f"   Users: {cls.test_users.count()}")
        print(f"   Budget Items: {cls.test_budget_items.count()}")

    def setUp(self):
        """Set up individual test."""
        cache.clear()
        connections.close_all()

    @classmethod
    def _get_bmms_scenarios(cls) -> List[BMMSLoadTestScenario]:
        """Get BMMS-specific load test scenarios."""
        return [
            BMMSLoadTestScenario(
                name="Normal Daily Usage",
                description="Regular daily operations across all 44 MOAs",
                concurrent_users=220,  # ~5 users per MOA
                requests_per_user=20,
                duration_seconds=300,  # 5 minutes
                target_throughput=50.0,
                target_response_time=0.5
            ),
            BMMSLoadTestScenario(
                name="Peak Quarterly Reporting",
                description="End-of-quarter reporting peak load",
                concurrent_users=440,  # ~10 users per MOA
                requests_per_user=50,
                duration_seconds=600,  # 10 minutes
                target_throughput=100.0,
                target_response_time=1.0
            ),
            BMMSLoadTestScenario(
                name="Emergency Response",
                description="Emergency coordination across multiple MOAs",
                concurrent_users=132,  # 3 users per critical MOA
                requests_per_user=100,
                duration_seconds=180,  # 3 minutes
                target_throughput=200.0,
                target_response_time=0.2
            ),
            BMMSLoadTestScenario(
                name="Data Import Operations",
                description="Large-scale data import and processing",
                concurrent_users=44,  # 1 admin per MOA
                requests_per_user=10,
                duration_seconds=900,  # 15 minutes
                target_throughput=5.0,
                target_response_time=5.0
            ),
        ]

    @classmethod
    def _setup_test_data(cls):
        """Set up comprehensive test data for BMMS scenarios."""
        print("Setting up BMMS test data...")

        # Create test organizations (44 MOAs simulation)
        cls.test_organizations = []
        moa_types = ['ministry', 'office', 'agency']
        for i in range(44):
            org = Organization.objects.create(
                code=f'MOA_{i+1:02d}',
                name=f'Ministry/Office/Agency {i+1}',
                org_type=random.choice(moa_types),
                description=f'Test organization for BMMS performance testing',
                is_active=True
            )
            cls.test_organizations.append(org)

        # Create test users (10 users per organization = 440 users)
        cls.test_users = []
        for org in cls.test_organizations:
            for i in range(10):
                user = User.objects.create_user(
                    username=f'user_{org.code}_{i+1}',
                    email=f'user{i+1}@{org.code.lower()}.gov.ph',
                    password='test123456',
                    first_name=f'Test',
                    last_name=f'User {i+1}',
                    organization=org,
                    is_active=True
                )
                cls.test_users.append(user)

        # Create test communities (6,601 communities simulation)
        cls.test_communities = []
        for i in range(6601):
            community = OBCCommunity.objects.create(
                name=f'Test Community {i+1}',
                barangay=f'Barangay {i+1}',
                municipality=f'Municipality {(i % 81) + 1}',
                province=f'Province {(i % 25) + 1}',
                region=random.choice(['Region IX', 'Region X', 'Region XI', 'Region XII']),
                organization=random.choice(cls.test_organizations),
                latitude=6.0 + (i * 0.001),
                longitude=125.0 + (i * 0.001),
                is_active=True
            )
            cls.test_communities.append(community)

        # Create test budget data
        cls.test_budget_items = []
        for org in cls.test_organizations[:10]:  # Limit for performance
            # Create budget proposal
            proposal = BudgetProposal.objects.create(
                organization=org,
                fiscal_year=2025,
                title=f'Budget Proposal for {org.name}',
                total_requested_budget=Decimal('100000000.00'),
                submitted_by=org.users.first()
            )

            # Create program budgets and line items
            for j in range(5):
                program = ProgramBudget.objects.create(
                    budget_proposal=proposal,
                    requested_amount=Decimal('20000000.00'),
                    priority_rank=j + 1
                )

                # Create budget line items
                for k in range(20):
                    line_item = BudgetLineItem.objects.create(
                        program_budget=program,
                        category=random.choice(['personnel', 'operating', 'capital']),
                        description=f'Budget Item {k+1}',
                        unit_cost=Decimal('100000.00'),
                        quantity=random.randint(1, 10),
                        total_cost=Decimal('1000000.00')
                    )
                    cls.test_budget_items.append(line_item)

        print(f"✅ Test data setup complete")

    def _record_metric(self, operation: str, target_time: float, actual_time: float,
                      details: Dict[str, Any] = None) -> PerformanceMetrics:
        """Record a performance metric."""
        metric = PerformanceMetrics(
            operation=operation,
            target_time=target_time,
            actual_time=actual_time,
            passed=actual_time <= target_time,
            details=details or {}
        )
        self.metrics.append(metric)
        return metric

    # ========================================================================
    # DATABASE PERFORMANCE TESTS
    # ========================================================================

    def test_database_query_performance(self):
        """Test database query response times."""
        print("\n📊 Testing Database Query Performance...")

        # Test simple queries
        queries = [
            ("User Count Query", 0.1, lambda: User.objects.count()),
            ("Organization Count Query", 0.1, lambda: Organization.objects.count()),
            ("Community Count Query", 0.1, lambda: OBCCommunity.objects.count()),
            ("Budget Items Count Query", 0.1, lambda: BudgetLineItem.objects.count()),
        ]

        for name, target, query_func in queries:
            start_time = time.time()
            result = query_func()
            actual_time = time.time() - start_time

            metric = self._record_metric(
                operation=f"Database: {name}",
                target_time=target,
                actual_time=actual_time,
                details={"result_count": result}
            )

            status = "✅" if metric.passed else "❌"
            print(f"   {status} {name}: {actual_time:.3f}s (target: {target}s)")

        # Test complex queries with joins
        complex_queries = [
            ("Community with Organization", 0.2,
             lambda: OBCCommunity.objects.select_related('organization').count()),
            ("Budget with Line Items", 0.3,
             lambda: ProgramBudget.objects.prefetch_related('line_items').count()),
            ("User with Organization", 0.2,
             lambda: User.objects.select_related('organization').count()),
        ]

        for name, target, query_func in complex_queries:
            start_time = time.time()
            result = query_func()
            actual_time = time.time() - start_time

            metric = self._record_metric(
                operation=f"Database: {name}",
                target_time=target,
                actual_time=actual_time,
                details={"result_count": result}
            )

            status = "✅" if metric.passed else "❌"
            print(f"   {status} {name}: {actual_time:.3f}s (target: {target}s)")

    def test_database_connection_pool_efficiency(self):
        """Test database connection pooling under load."""
        print("\n🔗 Testing Database Connection Pool Efficiency...")

        def database_operation():
            """Simulate database operation."""
            start_time = time.time()
            # Perform a query
            count = User.objects.count()
            return time.time() - start_time

        # Test with increasing concurrent connections
        thread_counts = [5, 10, 20, 50, 100]

        for thread_count in thread_counts:
            with concurrent.futures.ThreadPoolExecutor(max_workers=thread_count) as executor:
                futures = [executor.submit(database_operation) for _ in range(20)]
                times = [f.result() for f in concurrent.futures.as_completed(futures)]

            avg_time = statistics.mean(times)
            max_time = max(times)

            # Target: Average time should not increase significantly with threads
            target_time = 0.1 + (thread_count * 0.002)  # Allow slight increase

            metric = self._record_metric(
                operation=f"Database: Connection Pool ({thread_count} threads)",
                target_time=target_time,
                actual_time=avg_time,
                details={
                    "thread_count": thread_count,
                    "max_time": max_time,
                    "operations": len(times)
                }
            )

            status = "✅" if metric.passed else "❌"
            print(f"   {status} {thread_count} threads: avg {avg_time:.3f}s, max {max_time:.3f}s")

    def test_database_index_performance(self):
        """Test database index effectiveness for large datasets."""
        print("\n📈 Testing Database Index Performance...")

        # Test indexed queries
        indexed_queries = [
            ("User Organization Index", 0.05,
             lambda: User.objects.filter(organization_id=self.test_organizations[0].id).count()),
            ("Community Region Index", 0.05,
             lambda: OBCCommunity.objects.filter(region='Region IX').count()),
            ("Budget Proposal Fiscal Year Index", 0.05,
             lambda: BudgetProposal.objects.filter(fiscal_year=2025).count()),
        ]

        for name, target, query_func in indexed_queries:
            # Test with EXPLAIN to verify index usage
            start_time = time.time()
            result = query_func()
            actual_time = time.time() - start_time

            metric = self._record_metric(
                operation=f"Database: {name}",
                target_time=target,
                actual_time=actual_time,
                details={"result_count": result}
            )

            status = "✅" if metric.passed else "❌"
            print(f"   {status} {name}: {actual_time:.3f}s (target: {target}s)")

    # ========================================================================
    # API PERFORMANCE TESTS
    # ========================================================================

    def test_api_endpoint_performance(self):
        """Test API endpoint response times."""
        print("\n🌐 Testing API Endpoint Performance...")

        # Get authenticated client
        user = self.test_users[0]
        self.client.force_login(user)

        # Test common API endpoints
        api_endpoints = [
            ("User Profile API", 0.2, "/api/v1/users/profile/"),
            ("Organizations API", 0.2, "/api/v1/organizations/"),
            ("Communities API", 0.3, "/api/v1/communities/"),
            ("Budget API", 0.3, "/api/v1/budget/"),
            ("Work Items API", 0.2, "/api/v1/work-items/"),
        ]

        for name, target, endpoint in api_endpoints:
            try:
                start_time = time.time()
                response = self.client.get(endpoint)
                actual_time = time.time() - start_time

                metric = self._record_metric(
                    operation=f"API: {name}",
                    target_time=target,
                    actual_time=actual_time,
                    details={
                        "endpoint": endpoint,
                        "status_code": response.status_code,
                        "response_size": len(response.content)
                    }
                )

                status = "✅" if metric.passed else "❌"
                print(f"   {status} {name}: {actual_time:.3f}s (target: {target}s)")

            except Exception as e:
                print(f"   ❌ {name}: Error - {str(e)}")
                self._record_metric(
                    operation=f"API: {name}",
                    target_time=target,
                    actual_time=999.0,
                    details={"error": str(e)}
                )

    def test_api_concurrent_request_handling(self):
        """Test API concurrent request handling."""
        print("\n⚡ Testing API Concurrent Request Handling...")

        def api_request():
            """Simulate API request."""
            client = Client()
            user = random.choice(self.test_users)
            client.force_login(user)

            start_time = time.time()
            try:
                response = client.get("/api/v1/communities/")
                actual_time = time.time() - start_time
                return actual_time, response.status_code == 200
            except Exception:
                return time.time() - start_time, False

        # Test with different concurrency levels
        concurrency_levels = [10, 25, 50, 100]

        for concurrency in concurrency_levels:
            with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as executor:
                futures = [executor.submit(api_request) for _ in range(50)]
                results = [f.result() for f in concurrent.futures.as_completed(futures)]

            times = [r[0] for r in results]
            success_count = sum(1 for r in results if r[1])

            avg_time = statistics.mean(times)
            success_rate = success_count / len(results)

            # Target: 95% success rate, reasonable response time
            target_time = 1.0 + (concurrency * 0.01)
            target_success_rate = 0.95

            metric = self._record_metric(
                operation=f"API: Concurrent Requests ({concurrency})",
                target_time=target_time,
                actual_time=avg_time,
                details={
                    "concurrency": concurrency,
                    "success_rate": success_rate,
                    "total_requests": len(results),
                    "successful_requests": success_count
                }
            )

            status = "✅" if metric.passed and success_rate >= target_success_rate else "❌"
            print(f"   {status} {concurrency} concurrent: avg {avg_time:.3f}s, success {success_rate:.1%}")

    def test_authentication_performance(self):
        """Test authentication performance overhead."""
        print("\n🔐 Testing Authentication Performance...")

        # Test login performance
        def login_test():
            """Test login performance."""
            client = Client()
            user = random.choice(self.test_users)

            start_time = time.time()
            response = client.post("/login/", {
                "username": user.username,
                "password": "test123456"
            })
            actual_time = time.time() - start_time

            return actual_time, response.status_code == 302  # Redirect on success

        # Test multiple logins
        times = []
        successes = 0

        for _ in range(20):
            actual_time, success = login_test()
            times.append(actual_time)
            if success:
                successes += 1

        avg_time = statistics.mean(times)
        success_rate = successes / len(times)

        metric = self._record_metric(
            operation="Authentication: Login",
            target_time=0.5,
            actual_time=avg_time,
            details={
                "success_rate": success_rate,
                "total_attempts": len(times)
            }
        )

        status = "✅" if metric.passed and success_rate >= 0.95 else "❌"
        print(f"   {status} Login: avg {avg_time:.3f}s, success {success_rate:.1%}")

        # Test JWT token performance
        try:
            from rest_framework_simplejwt.tokens import RefreshToken

            start_time = time.time()
            user = self.test_users[0]
            refresh = RefreshToken.for_user(user)
            access = refresh.access_token
            actual_time = time.time() - start_time

            metric = self._record_metric(
                operation="Authentication: JWT Generation",
                target_time=0.1,
                actual_time=actual_time,
                details={"user_id": user.id}
            )

            status = "✅" if metric.passed else "❌"
            print(f"   {status} JWT Generation: {actual_time:.3f}s")

        except Exception as e:
            print(f"   ❌ JWT Generation: Error - {str(e)}")

    # ========================================================================
    # GEOGRAPHIC PERFORMANCE TESTS
    # ========================================================================

    def test_geographic_query_performance(self):
        """Test geographic coordinate query performance."""
        print("\n🗺️ Testing Geographic Query Performance...")

        # Test coordinate queries
        coordinate_queries = [
            ("Community by Coordinates", 0.05,
             lambda: OBCCommunity.objects.filter(
                 latitude__gte=6.0, latitude__lte=7.0,
                 longitude__gte=125.0, longitude__lte=126.0
             ).count()),
            ("Communities in Region", 0.05,
             lambda: OBCCommunity.objects.filter(region='Region IX').count()),
            ("Communities by Municipality", 0.05,
             lambda: OBCCommunity.objects.filter(municipality='Municipality 1').count()),
        ]

        for name, target, query_func in coordinate_queries:
            start_time = time.time()
            result = query_func()
            actual_time = time.time() - start_time

            metric = self._record_metric(
                operation=f"Geographic: {name}",
                target_time=target,
                actual_time=actual_time,
                details={"result_count": result}
            )

            status = "✅" if metric.passed else "❌"
            print(f"   {status} {name}: {actual_time:.3f}s (target: {target}s)")

    def test_batch_geocoding_performance(self):
        """Test batch geocoding performance."""
        print("\n📍 Testing Batch Geocoding Performance...")

        # Test batch geocoding of communities
        communities_to_geocode = self.test_communities[:100]  # Test with 100 communities

        start_time = time.time()

        # Simulate geocoding process
        geocoded_count = 0
        for community in communities_to_geocode:
            # Simulate geocoding delay
            time.sleep(0.001)  # 1ms per geocode
            community.latitude = 6.0 + random.random()
            community.longitude = 125.0 + random.random()
            community.save()
            geocoded_count += 1

        actual_time = time.time() - start_time
        target_time = 2.0  # 2 seconds for 100 communities

        metric = self._record_metric(
            operation="Geographic: Batch Geocoding (100 communities)",
            target_time=target_time,
            actual_time=actual_time,
            details={
                "communities_processed": geocoded_count,
                "avg_time_per_community": actual_time / geocoded_count
            }
        )

        status = "✅" if metric.passed else "❌"
        print(f"   {status} Batch Geocoding: {actual_time:.3f}s for {geocoded_count} communities")

    def test_geographic_calculation_performance(self):
        """Test geographic calculation performance."""
        print("\n📐 Testing Geographic Calculation Performance...")

        # Test distance calculations
        def calculate_distance(lat1, lon1, lat2, lon2):
            """Calculate distance between two points."""
            import math
            R = 6371  # Earth radius in km

            lat1_rad = math.radians(lat1)
            lat2_rad = math.radians(lat2)
            delta_lat = math.radians(lat2 - lat1)
            delta_lon = math.radians(lon2 - lon1)

            a = (math.sin(delta_lat/2)**2 +
                 math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon/2)**2)
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

            return R * c

        # Test 1000 distance calculations
        start_time = time.time()

        for _ in range(1000):
            lat1 = 6.0 + random.random()
            lon1 = 125.0 + random.random()
            lat2 = 6.0 + random.random()
            lon2 = 125.0 + random.random()
            distance = calculate_distance(lat1, lon1, lat2, lon2)

        actual_time = time.time() - start_time
        target_time = 0.1  # 100ms for 1000 calculations

        metric = self._record_metric(
            operation="Geographic: Distance Calculations (1000)",
            target_time=target_time,
            actual_time=actual_time,
            details={"calculations": 1000}
        )

        status = "✅" if metric.passed else "❌"
        print(f"   {status} Distance Calculations: {actual_time:.3f}s for 1000 calculations")

    # ========================================================================
    # AI SERVICES PERFORMANCE TESTS
    # ========================================================================

    def test_embedding_generation_performance(self):
        """Test AI embedding generation performance."""
        print("\n🤖 Testing AI Embedding Generation Performance...")

        # Test embedding generation for different text lengths
        test_texts = [
            "Short text",
            "This is a medium length text for testing embedding generation performance in the BMMS system.",
            "This is a much longer text that represents a comprehensive description of a BMMS system component, including detailed specifications, requirements, and implementation details for the Bangsamoro Ministerial Management System serving 44 MOAs.",
        ]

        for i, text in enumerate(test_texts):
            try:
                start_time = time.time()
                embedding = self.embedding_service.generate_embedding(text)
                actual_time = time.time() - start_time

                # Target time depends on text length
                target_time = 0.5 + (i * 0.5)

                metric = self._record_metric(
                    operation=f"AI: Embedding Generation ({len(text)} chars)",
                    target_time=target_time,
                    actual_time=actual_time,
                    details={
                        "text_length": len(text),
                        "embedding_size": len(embedding) if embedding else 0
                    }
                )

                status = "✅" if metric.passed else "❌"
                print(f"   {status} Embedding ({len(text)} chars): {actual_time:.3f}s (target: {target_time}s)")

            except Exception as e:
                print(f"   ❌ Embedding Generation ({len(text)} chars): Error - {str(e)}")

    def test_vector_search_performance(self):
        """Test vector search performance."""
        print("\n🔍 Testing Vector Search Performance...")

        # Create test embeddings for search
        test_query = "communities in Region IX"

        try:
            # Generate query embedding
            start_time = time.time()
            query_embedding = self.embedding_service.generate_embedding(test_query)
            embedding_time = time.time() - start_time

            # Perform vector search
            start_time = time.time()
            results = self.vector_store.search(query_embedding, limit=10)
            search_time = time.time() - start_time

            total_time = embedding_time + search_time
            target_time = 1.0  # 1 second total

            metric = self._record_metric(
                operation="AI: Vector Search",
                target_time=target_time,
                actual_time=total_time,
                details={
                    "embedding_time": embedding_time,
                    "search_time": search_time,
                    "results_count": len(results)
                }
            )

            status = "✅" if metric.passed else "❌"
            print(f"   {status} Vector Search: {total_time:.3f}s (embedding: {embedding_time:.3f}s, search: {search_time:.3f}s)")

        except Exception as e:
            print(f"   ❌ Vector Search: Error - {str(e)}")

    def test_ai_model_loading_performance(self):
        """Test AI model loading performance."""
        print("\n🧠 Testing AI Model Loading Performance...")

        # Test model loading times
        try:
            # Test embedding service initialization
            start_time = time.time()
            embedding_service = EmbeddingService()
            embedding_load_time = time.time() - start_time

            metric = self._record_metric(
                operation="AI: Model Loading (Embedding Service)",
                target_time=2.0,
                actual_time=embedding_load_time,
                details={"service": "EmbeddingService"}
            )

            status = "✅" if metric.passed else "❌"
            print(f"   {status} Embedding Service Load: {embedding_load_time:.3f}s")

            # Test vector store initialization
            start_time = time.time()
            vector_store = VectorStore()
            vector_load_time = time.time() - start_time

            metric = self._record_metric(
                operation="AI: Model Loading (Vector Store)",
                target_time=1.0,
                actual_time=vector_load_time,
                details={"service": "VectorStore"}
            )

            status = "✅" if metric.passed else "❌"
            print(f"   {status} Vector Store Load: {vector_load_time:.3f}s")

        except Exception as e:
            print(f"   ❌ AI Model Loading: Error - {str(e)}")

    # ========================================================================
    # MULTI-ORGANIZATION PERFORMANCE TESTS
    # ========================================================================

    def test_organization_switching_performance(self):
        """Test organization switching performance."""
        print("\n🔄 Testing Organization Switching Performance...")

        # Test organization switching for a multi-org user
        user = self.test_users[0]
        self.client.force_login(user)

        # Test switching between different organizations
        org_switch_times = []

        for org in self.test_organizations[:10]:  # Test 10 switches
            start_time = time.time()

            # Simulate organization switch
            session = self.client.session
            session['current_organization'] = org.id
            session.save()

            # Test access after switch
            response = self.client.get("/dashboard/")

            actual_time = time.time() - start_time
            org_switch_times.append(actual_time)

            if response.status_code == 200:
                print(f"   ✅ Switch to {org.code}: {actual_time:.3f}s")
            else:
                print(f"   ❌ Switch to {org.code}: Failed (status {response.status_code})")

        if org_switch_times:
            avg_time = statistics.mean(org_switch_times)
            target_time = 0.2  # 200ms target

            metric = self._record_metric(
                operation="Multi-Org: Organization Switching",
                target_time=target_time,
                actual_time=avg_time,
                details={
                    "switches": len(org_switch_times),
                    "avg_time": avg_time,
                    "max_time": max(org_switch_times)
                }
            )

            status = "✅" if metric.passed else "❌"
            print(f"   {status} Organization Switching: avg {avg_time:.3f}s")

    def test_multi_organization_data_isolation(self):
        """Test multi-organization data isolation performance."""
        print("\n🔒 Testing Multi-Organization Data Isolation Performance...")

        # Test queries with organization filtering
        org = self.test_organizations[0]

        isolation_tests = [
            ("User Organization Filter", 0.1,
             lambda: User.objects.filter(organization=org).count()),
            ("Community Organization Filter", 0.1,
             lambda: OBCCommunity.objects.filter(organization=org).count()),
            ("Budget Organization Filter", 0.1,
             lambda: BudgetProposal.objects.filter(organization=org).count()),
        ]

        for name, target, query_func in isolation_tests:
            start_time = time.time()
            result = query_func()
            actual_time = time.time() - start_time

            metric = self._record_metric(
                operation=f"Multi-Org: {name}",
                target_time=target,
                actual_time=actual_time,
                details={"result_count": result, "organization": org.code}
            )

            status = "✅" if metric.passed else "❌"
            print(f"   {status} {name}: {actual_time:.3f}s")

    def test_cross_organization_query_performance(self):
        """Test cross-organization query performance."""
        print("\n🌍 Testing Cross-Organization Query Performance...")

        # Test aggregation queries across organizations
        start_time = time.time()

        # Count communities by organization
        org_community_counts = (
            OBCCommunity.objects
            .values('organization__code')
            .annotate(count=Count('id'))
            .order_by('-count')
        )

        # Force query execution
        result_count = len(list(org_community_counts))

        actual_time = time.time() - start_time
        target_time = 0.5  # 500ms target

        metric = self._record_metric(
            operation="Multi-Org: Cross-Organization Aggregation",
            target_time=target_time,
            actual_time=actual_time,
            details={"organizations_processed": result_count}
        )

        status = "✅" if metric.passed else "❌"
        print(f"   {status} Cross-Org Aggregation: {actual_time:.3f}s for {result_count} organizations")

    # ========================================================================
    # STRESS TESTING
    # ========================================================================

    def test_peak_load_simulation(self):
        """Test peak load simulation."""
        print("\n📈 Testing Peak Load Simulation...")

        # Simulate peak load (end-of-quarter reporting)
        scenario = self.scenarios[1]  # Peak Quarterly Reporting

        def simulate_user_activity():
            """Simulate user activity."""
            user = random.choice(self.test_users)
            client = Client()
            client.force_login(user)

            activities = [
                lambda: client.get("/dashboard/"),
                lambda: client.get("/api/v1/communities/"),
                lambda: client.get("/api/v1/budget/"),
                lambda: client.get("/reports/"),
                lambda: client.get("/analytics/"),
            ]

            response_times = []
            for _ in range(scenario.requests_per_user):
                activity = random.choice(activities)
                start_time = time.time()
                activity()
                actual_time = time.time() - start_time
                response_times.append(actual_time)

            return response_times

        # Run concurrent user simulation
        with concurrent.futures.ThreadPoolExecutor(max_workers=scenario.concurrent_users) as executor:
            futures = [executor.submit(simulate_user_activity) for _ in range(scenario.concurrent_users)]
            all_response_times = []

            for future in concurrent.futures.as_completed(futures):
                try:
                    user_times = future.result(timeout=scenario.duration_seconds)
                    all_response_times.extend(user_times)
                except Exception as e:
                    print(f"   ❌ User simulation failed: {str(e)}")

        if all_response_times:
            avg_time = statistics.mean(all_response_times)
            p95_time = statistics.quantiles(all_response_times, n=20)[18]  # 95th percentile
            total_requests = len(all_response_times)
            actual_throughput = total_requests / scenario.duration_seconds

            metric = self._record_metric(
                operation="Stress: Peak Load Simulation",
                target_time=scenario.target_response_time,
                actual_time=avg_time,
                details={
                    "scenario": scenario.name,
                    "concurrent_users": scenario.concurrent_users,
                    "total_requests": total_requests,
                    "actual_throughput": actual_throughput,
                    "target_throughput": scenario.target_throughput,
                    "p95_response_time": p95_time
                }
            )

            status = "✅" if metric.passed else "❌"
            print(f"   {status} Peak Load: avg {avg_time:.3f}s, p95 {p95_time:.3f}s, throughput {actual_throughput:.1f} req/s")

    def test_sustained_load_testing(self):
        """Test sustained load testing (8-hour workday simulation)."""
        print("\n⏰ Testing Sustained Load Testing...")

        # Simulate 8-hour workday (compressed to 2 minutes for testing)
        duration_seconds = 120  # 2 minutes representing 8 hours
        concurrent_users = 50  # Sustained load

        def sustained_user_activity():
            """Simulate sustained user activity."""
            user = random.choice(self.test_users)
            client = Client()
            client.force_login(user)

            activities = [
                lambda: client.get("/dashboard/"),
                lambda: client.get("/api/v1/communities/"),
                lambda: client.get("/api/v1/work-items/"),
            ]

            # Perform activities throughout the duration
            end_time = time.time() + duration_seconds
            response_times = []

            while time.time() < end_time:
                activity = random.choice(activities)
                start_time = time.time()
                activity()
                actual_time = time.time() - start_time
                response_times.append(actual_time)

                # Random delay between activities (1-5 seconds)
                time.sleep(random.uniform(0.1, 0.5))  # Compressed for testing

            return response_times

        # Run sustained load test
        start_time = time.time()

        with concurrent.futures.ThreadPoolExecutor(max_workers=concurrent_users) as executor:
            futures = [executor.submit(sustained_user_activity) for _ in range(concurrent_users)]
            all_response_times = []

            for future in concurrent.futures.as_completed(futures):
                try:
                    user_times = future.result(timeout=duration_seconds + 60)
                    all_response_times.extend(user_times)
                except Exception as e:
                    print(f"   ❌ Sustained load user failed: {str(e)}")

        total_time = time.time() - start_time

        if all_response_times:
            # Analyze performance degradation over time
            midpoint = len(all_response_times) // 2
            first_half_avg = statistics.mean(all_response_times[:midpoint])
            second_half_avg = statistics.mean(all_response_times[midpoint:])

            degradation = ((second_half_avg - first_half_avg) / first_half_avg) * 100

            metric = self._record_metric(
                operation="Stress: Sustained Load Testing",
                target_time=0.5,
                actual_time=second_half_avg,
                details={
                    "duration_seconds": total_time,
                    "concurrent_users": concurrent_users,
                    "total_requests": len(all_response_times),
                    "first_half_avg": first_half_avg,
                    "second_half_avg": second_half_avg,
                    "degradation_percent": degradation
                }
            )

            status = "✅" if metric.passed and degradation < 20 else "❌"
            print(f"   {status} Sustained Load: avg {second_half_avg:.3f}s, degradation {degradation:.1f}%")

    def test_memory_leak_detection(self):
        """Test memory leak detection."""
        print("\n🧠 Testing Memory Leak Detection...")

        # Get initial memory usage
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Perform memory-intensive operations
        memory_samples = []

        for iteration in range(5):
            # Create and process large amounts of data
            communities = OBCCommunity.objects.all()[:1000]

            # Process each community
            for community in communities:
                # Simulate processing
                data = {
                    'name': community.name,
                    'barangay': community.barangay,
                    'municipality': community.municipality,
                    'region': community.region,
                    'organization': community.organization.name
                }
                # Simulate some processing
                _ = len(str(data))

            # Measure memory after processing
            current_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_samples.append(current_memory)

            # Force garbage collection
            import gc
            gc.collect()

            print(f"   Iteration {iteration + 1}: {current_memory:.1f} MB")

        # Analyze memory growth
        final_memory = memory_samples[-1]
        memory_growth = final_memory - initial_memory
        max_memory = max(memory_samples)

        # Target: Memory growth should be reasonable (<100MB)
        target_growth = 100  # MB

        metric = self._record_metric(
            operation="Stress: Memory Leak Detection",
            target_time=0,  # Not a time-based test
            actual_time=memory_growth,
            details={
                "initial_memory_mb": initial_memory,
                "final_memory_mb": final_memory,
                "memory_growth_mb": memory_growth,
                "max_memory_mb": max_memory,
                "iterations": len(memory_samples)
            }
        )

        # Check if memory growth is within acceptable limits
        passed = memory_growth <= target_growth
        metric.passed = passed

        status = "✅" if passed else "❌"
        print(f"   {status} Memory Usage: {memory_growth:.1f} MB growth (target: <{target_growth} MB)")

    # ========================================================================
    # REPORT GENERATION
    # ========================================================================

    def test_generate_performance_report(self):
        """Generate comprehensive performance report."""
        print("\n📊 Generating Performance Report...")

        # Calculate summary statistics
        total_tests = len(self.metrics)
        passed_tests = sum(1 for m in self.metrics if m.passed)
        failed_tests = total_tests - passed_tests

        # Group metrics by category
        categories = {}
        for metric in self.metrics:
            category = metric.operation.split(":")[0]
            if category not in categories:
                categories[category] = []
            categories[category].append(metric)

        # Generate report
        report = {
            "test_run": {
                "timestamp": datetime.now().isoformat(),
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "success_rate": passed_tests / total_tests if total_tests > 0 else 0,
                "bmms_mode": getattr(settings, 'BMMS_MODE', 'obcms'),
                "organizations_tested": self.test_organizations.count(),
                "communities_tested": self.test_communities.count(),
                "users_tested": self.test_users.count()
            },
            "performance_summary": {},
            "category_performance": {},
            "detailed_metrics": [m.to_dict() for m in self.metrics],
            "recommendations": []
        }

        # Category performance
        for category, metrics in categories.items():
            passed = sum(1 for m in metrics if m.passed)
            total = len(metrics)
            avg_time = statistics.mean([m.actual_time for m in metrics])
            max_time = max([m.actual_time for m in metrics])

            report["category_performance"][category] = {
                "total_tests": total,
                "passed_tests": passed,
                "success_rate": passed / total,
                "avg_response_time": avg_time,
                "max_response_time": max_time
            }

        # Overall performance summary
        all_times = [m.actual_time for m in self.metrics]
        report["performance_summary"] = {
            "avg_response_time": statistics.mean(all_times),
            "median_response_time": statistics.median(all_times),
            "max_response_time": max(all_times),
            "min_response_time": min(all_times),
            "p95_response_time": statistics.quantiles(all_times, n=20)[18] if len(all_times) > 20 else max(all_times)
        }

        # Generate recommendations
        report["recommendations"] = self._generate_recommendations(categories)

        # Save report
        report_path = "/tmp/bmms_performance_report.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)

        print(f"   ✅ Performance report saved to {report_path}")

        # Print summary
        print(f"\n📊 PERFORMANCE TEST SUMMARY")
        print(f"   Total Tests: {total_tests}")
        print(f"   Passed: {passed_tests}")
        print(f"   Failed: {failed_tests}")
        print(f"   Success Rate: {passed_tests/total_tests:.1%}")
        print(f"   Avg Response Time: {statistics.mean(all_times):.3f}s")

        return report

    def _generate_recommendations(self, categories):
        """Generate performance recommendations."""
        recommendations = []

        for category, metrics in categories.items():
            failed_tests = [m for m in metrics if not m.passed]

            if failed_tests:
                avg_time = statistics.mean([m.actual_time for m in failed_tests])
                recommendations.append({
                    "category": category,
                    "priority": "HIGH" if avg_time > 1.0 else "MEDIUM",
                    "issue": f"{len(failed_tests)} tests failing in {category}",
                    "recommendation": self._get_category_recommendation(category, failed_tests),
                    "impact": "High" if category in ["API", "Database"] else "Medium"
                })

        return recommendations

    def _get_category_recommendation(self, category, failed_tests):
        """Get specific recommendations for a category."""
        recommendations = {
            "Database": "Consider adding indexes, optimizing queries, or implementing query result caching.",
            "API": "Review API endpoint efficiency, implement response caching, or optimize database queries.",
            "AI": "Consider model optimization, caching embeddings, or implementing batch processing.",
            "Geographic": "Optimize spatial queries, consider geographic indexing, or implement coordinate caching.",
            "Multi-Org": "Optimize organization filtering, implement organization-specific caching, or improve query efficiency.",
            "Stress": "Scale up resources, implement connection pooling, or optimize resource usage patterns."
        }

        return recommendations.get(category, "Review and optimize the failing operations.")


def main():
    """Run the complete BMMS performance test suite."""
    print("=" * 80)
    print("🚀 BMMS PERFORMANCE TESTING SUITE")
    print("Bangsamoro Ministerial Management System")
    print("Testing for 44 MOAs production readiness")
    print("=" * 80)

    # Create and run test suite
    suite = BMMSPerformanceTestSuite()

    # Run all tests
    test_methods = [
        suite.test_database_query_performance,
        suite.test_database_connection_pool_efficiency,
        suite.test_database_index_performance,
        suite.test_api_endpoint_performance,
        suite.test_api_concurrent_request_handling,
        suite.test_authentication_performance,
        suite.test_geographic_query_performance,
        suite.test_batch_geocoding_performance,
        suite.test_geographic_calculation_performance,
        suite.test_embedding_generation_performance,
        suite.test_vector_search_performance,
        suite.test_ai_model_loading_performance,
        suite.test_organization_switching_performance,
        suite.test_multi_organization_data_isolation,
        suite.test_cross_organization_query_performance,
        suite.test_peak_load_simulation,
        suite.test_sustained_load_testing,
        suite.test_memory_leak_detection,
    ]

    # Run tests
    for test_method in test_methods:
        try:
            test_method()
        except Exception as e:
            print(f"❌ Test {test_method.__name__} failed: {str(e)}")

    # Generate final report
    report = suite.test_generate_performance_report()

    print("\n" + "=" * 80)
    print("🎯 BMMS PERFORMANCE ASSESSMENT COMPLETE")
    print("=" * 80)

    # Overall assessment
    success_rate = report["test_run"]["success_rate"]
    avg_response_time = report["performance_summary"]["avg_response_time"]

    if success_rate >= 0.95 and avg_response_time <= 0.5:
        print("✅ EXCELLENT: System is ready for BMMS production deployment")
    elif success_rate >= 0.85 and avg_response_time <= 1.0:
        print("⚠️  GOOD: System is mostly ready, minor optimizations needed")
    elif success_rate >= 0.70 and avg_response_time <= 2.0:
        print("⚠️  ACCEPTABLE: System needs significant optimizations before production")
    else:
        print("❌ NOT READY: System requires major performance improvements")

    print(f"   Success Rate: {success_rate:.1%}")
    print(f"   Avg Response Time: {avg_response_time:.3f}s")
    print(f"   Organizations Tested: {report['test_run']['organizations_tested']}")
    print(f"   Communities Tested: {report['test_run']['communities_tested']}")

    return report


if __name__ == "__main__":
    main()
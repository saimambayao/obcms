#!/usr/bin/env python3
"""
BMMS Phase 8 Capacity Planning Tool

Calculates infrastructure resource requirements for full rollout to 44 MOAs
with 700-1100 concurrent users.

Usage:
    python scripts/capacity_planning.py
    python scripts/capacity_planning.py --moas 44 --users 1000
    python scripts/capacity_planning.py --export-json capacity.json
"""

import argparse
import json
import math
from datetime import datetime
from typing import Dict, Any


class CapacityPlanner:
    """Calculate infrastructure capacity requirements for BMMS deployment."""

    def __init__(self, moas: int = 44, users: int = 1000):
        """
        Initialize capacity planner.

        Args:
            moas: Number of Ministries, Offices, and Agencies
            users: Expected concurrent users
        """
        self.moas = moas
        self.users = users
        self.users_per_moa = math.ceil(self.users / self.moas)

    def calculate_database_requirements(self) -> Dict[str, Any]:
        """
        Calculate PostgreSQL database requirements.

        Returns:
            Dictionary with database specifications
        """
        # Connection estimation:
        # - Each concurrent user: ~2-3 connections (web + background tasks)
        # - Celery workers: ~10 connections per worker
        # - PgBouncer overhead: ~20 connections

        base_connections = self.users * 3
        celery_connections = 50  # 5 workers × 10 connections
        overhead = 50
        total_connections = base_connections + celery_connections + overhead

        # Add 20% headroom for spikes
        max_connections = math.ceil(total_connections * 1.2)

        # Database size estimation:
        # - Base schema: ~500MB
        # - Per MOA data: ~50MB (plans, budgets, users)
        # - Per user data: ~5MB (sessions, audit logs)

        base_size_mb = 500
        moa_data_mb = self.moas * 50
        user_data_mb = self.users * 5
        total_size_mb = base_size_mb + moa_data_mb + user_data_mb

        # Add 100% headroom for growth
        storage_gb = math.ceil((total_size_mb * 2) / 1024)

        # RAM calculation (PostgreSQL best practices):
        # shared_buffers = 25% of RAM
        # For 1000 users, target ~16-32GB RAM → shared_buffers ~4-8GB

        if self.users < 200:
            ram_gb = 8
            shared_buffers_gb = 2
        elif self.users < 500:
            ram_gb = 16
            shared_buffers_gb = 4
        elif self.users < 1000:
            ram_gb = 32
            shared_buffers_gb = 8
        else:
            ram_gb = 64
            shared_buffers_gb = 16

        # Work mem per connection
        work_mem_mb = 16

        return {
            "max_connections": max_connections,
            "recommended_connections": 500,
            "pgbouncer_pool_size": 50,
            "pgbouncer_max_clients": max_connections,
            "storage_gb": storage_gb,
            "ram_gb": ram_gb,
            "shared_buffers_gb": shared_buffers_gb,
            "work_mem_mb": work_mem_mb,
            "read_replicas": 2,
            "backup_retention_days": 30,
            "estimated_backup_size_gb": storage_gb,
        }

    def calculate_application_server_requirements(self) -> Dict[str, Any]:
        """
        Calculate Django application server requirements.

        Returns:
            Dictionary with app server specifications
        """
        # Gunicorn workers recommendation: (2 × CPU cores) + 1
        # For high concurrency: 4-8 CPU cores per server

        cpu_cores_per_server = 8
        gunicorn_workers = (2 * cpu_cores_per_server) + 1  # 17 workers

        # RAM per server:
        # - Each Gunicorn worker: ~200-300MB
        # - Django app baseline: ~500MB
        # - OS overhead: ~1GB

        ram_per_worker_mb = 250
        baseline_ram_mb = 500
        os_overhead_mb = 1024
        ram_per_server_gb = math.ceil(
            (gunicorn_workers * ram_per_worker_mb + baseline_ram_mb + os_overhead_mb) / 1024
        )

        # Number of servers:
        # Target: 200-250 concurrent users per server (conservative)

        users_per_server = 200
        server_count = math.ceil(self.users / users_per_server)

        # Ensure minimum 4 servers for HA, max 8 for manageability
        server_count = max(4, min(server_count, 8))

        return {
            "server_count": server_count,
            "cpu_cores_per_server": cpu_cores_per_server,
            "ram_gb_per_server": ram_per_server_gb,
            "gunicorn_workers": gunicorn_workers,
            "gunicorn_threads": 2,
            "users_per_server": users_per_server,
            "total_cpu_cores": server_count * cpu_cores_per_server,
            "total_ram_gb": server_count * ram_per_server_gb,
        }

    def calculate_cache_requirements(self) -> Dict[str, Any]:
        """
        Calculate Redis cache requirements.

        Returns:
            Dictionary with Redis specifications
        """
        # Redis memory estimation:
        # - Session cache per user: ~50KB
        # - Query cache: ~500MB baseline
        # - Celery task queue: ~100MB
        # - Additional caching: 20% of database size

        session_cache_mb = (self.users * 50) / 1024  # KB to MB
        query_cache_mb = 500
        celery_queue_mb = 100
        additional_cache_mb = (self.calculate_database_requirements()["storage_gb"] * 1024) * 0.2

        total_cache_mb = session_cache_mb + query_cache_mb + celery_queue_mb + additional_cache_mb

        # Add 50% headroom
        cache_gb = math.ceil((total_cache_mb * 1.5) / 1024)

        # Minimum 8GB, maximum 32GB per instance
        cache_gb = max(8, min(cache_gb, 32))

        return {
            "memory_gb": cache_gb,
            "master_nodes": 1,
            "replica_nodes": 2,
            "sentinel_nodes": 3,
            "total_memory_gb": cache_gb * 3,  # master + 2 replicas
            "persistence": "AOF + RDB",
            "eviction_policy": "allkeys-lru",
        }

    def calculate_celery_requirements(self) -> Dict[str, Any]:
        """
        Calculate Celery worker requirements.

        Returns:
            Dictionary with Celery specifications
        """
        # Celery workers:
        # - Background tasks (email, reports, imports): 2-3 workers
        # - Long-running tasks (data processing): 1-2 workers
        # - Beat scheduler: 1 instance

        worker_count = 5
        cpu_cores_per_worker = 2
        ram_gb_per_worker = 2

        return {
            "worker_count": worker_count,
            "cpu_cores_per_worker": cpu_cores_per_worker,
            "ram_gb_per_worker": ram_gb_per_worker,
            "total_cpu_cores": worker_count * cpu_cores_per_worker,
            "total_ram_gb": worker_count * ram_gb_per_worker,
            "beat_scheduler": 1,
            "concurrency_per_worker": 4,
        }

    def calculate_storage_requirements(self) -> Dict[str, Any]:
        """
        Calculate file storage requirements.

        Returns:
            Dictionary with storage specifications
        """
        # Storage estimation:
        # - User uploads (documents, images): ~100MB per MOA
        # - Static files: ~500MB
        # - Media cache: ~1GB
        # - Logs: ~10GB (30 days retention)

        user_uploads_gb = (self.moas * 100) / 1024  # MB to GB
        static_files_gb = 0.5
        media_cache_gb = 1
        logs_gb = 10

        total_storage_gb = user_uploads_gb + static_files_gb + media_cache_gb + logs_gb

        # Add 100% headroom
        storage_gb = math.ceil(total_storage_gb * 2)

        # Minimum 100GB, maximum 1TB
        storage_gb = max(100, min(storage_gb, 1024))

        return {
            "total_storage_gb": storage_gb,
            "user_uploads_gb": math.ceil(user_uploads_gb * 2),
            "static_files_gb": 1,
            "media_cache_gb": 2,
            "logs_gb": 20,
            "backup_storage_gb": storage_gb * 2,  # 2x for backups
            "cdn_enabled": True,
        }

    def calculate_network_requirements(self) -> Dict[str, Any]:
        """
        Calculate network bandwidth requirements.

        Returns:
            Dictionary with network specifications
        """
        # Bandwidth estimation:
        # - Average request size: ~500KB (including assets)
        # - Requests per user per minute: ~10
        # - Peak load: 2x average

        avg_request_kb = 500
        requests_per_user_per_min = 10
        peak_multiplier = 2

        bandwidth_mbps = (
            (self.users * requests_per_user_per_min * avg_request_kb * peak_multiplier)
            / 60  # Convert to per second
            / 1024  # KB to MB
            * 8  # MB to Mbps
        )

        # Round up to nearest 100 Mbps
        bandwidth_mbps = math.ceil(bandwidth_mbps / 100) * 100

        # Minimum 1 Gbps for production
        bandwidth_mbps = max(1000, bandwidth_mbps)

        return {
            "bandwidth_mbps": bandwidth_mbps,
            "bandwidth_gbps": bandwidth_mbps / 1000,
            "peak_requests_per_second": (self.users * requests_per_user_per_min * peak_multiplier) / 60,
            "avg_requests_per_second": (self.users * requests_per_user_per_min) / 60,
        }

    def calculate_total_cost_estimate(self) -> Dict[str, Any]:
        """
        Calculate estimated monthly infrastructure cost (AWS/DigitalOcean pricing).

        Returns:
            Dictionary with cost estimates in USD
        """
        app = self.calculate_application_server_requirements()
        db = self.calculate_database_requirements()
        cache = self.calculate_cache_requirements()
        celery = self.calculate_celery_requirements()
        storage = self.calculate_storage_requirements()

        # Rough pricing (AWS/DO equivalent):
        # - App server (8 CPU, 16GB RAM): ~$150/month
        # - Database server (32GB RAM): ~$400/month
        # - Redis cluster (8GB × 3): ~$150/month
        # - Load balancer: ~$50/month
        # - Storage (per 100GB): ~$10/month
        # - Bandwidth (per 100GB): ~$10/month

        app_cost = app["server_count"] * 150
        db_cost = 400  # Primary + replicas included
        cache_cost = 150
        lb_cost = 50
        storage_cost = (storage["total_storage_gb"] / 100) * 10
        bandwidth_cost = 50  # Estimate

        total_monthly_cost = app_cost + db_cost + cache_cost + lb_cost + storage_cost + bandwidth_cost

        return {
            "application_servers_usd": app_cost,
            "database_usd": db_cost,
            "cache_usd": cache_cost,
            "load_balancer_usd": lb_cost,
            "storage_usd": math.ceil(storage_cost),
            "bandwidth_usd": bandwidth_cost,
            "total_monthly_usd": math.ceil(total_monthly_cost),
            "total_annual_usd": math.ceil(total_monthly_cost * 12),
        }

    def generate_report(self) -> Dict[str, Any]:
        """
        Generate complete capacity planning report.

        Returns:
            Comprehensive capacity planning report
        """
        return {
            "metadata": {
                "generated_at": datetime.utcnow().isoformat(),
                "bmms_phase": "Phase 8: Full Rollout",
                "moas": self.moas,
                "expected_users": self.users,
                "users_per_moa": self.users_per_moa,
            },
            "database": self.calculate_database_requirements(),
            "application_servers": self.calculate_application_server_requirements(),
            "cache": self.calculate_cache_requirements(),
            "celery": self.calculate_celery_requirements(),
            "storage": self.calculate_storage_requirements(),
            "network": self.calculate_network_requirements(),
            "cost_estimate": self.calculate_total_cost_estimate(),
        }

    def print_report(self):
        """Print formatted capacity planning report to console."""
        report = self.generate_report()

        print("=" * 80)
        print("BMMS PHASE 8 CAPACITY PLANNING REPORT")
        print("=" * 80)
        print(f"\nGenerated: {report['metadata']['generated_at']}")
        print(f"MOAs: {report['metadata']['moas']}")
        print(f"Expected Concurrent Users: {report['metadata']['expected_users']}")
        print(f"Users per MOA: {report['metadata']['users_per_moa']}")

        print("\n" + "=" * 80)
        print("DATABASE REQUIREMENTS (PostgreSQL)")
        print("=" * 80)
        db = report["database"]
        print(f"  Max Connections: {db['max_connections']}")
        print(f"  PgBouncer Pool Size: {db['pgbouncer_pool_size']}")
        print(f"  Storage: {db['storage_gb']} GB")
        print(f"  RAM: {db['ram_gb']} GB")
        print(f"  Shared Buffers: {db['shared_buffers_gb']} GB")
        print(f"  Work Memory: {db['work_mem_mb']} MB")
        print(f"  Read Replicas: {db['read_replicas']}")

        print("\n" + "=" * 80)
        print("APPLICATION SERVER REQUIREMENTS (Django)")
        print("=" * 80)
        app = report["application_servers"]
        print(f"  Server Count: {app['server_count']}")
        print(f"  CPU Cores per Server: {app['cpu_cores_per_server']}")
        print(f"  RAM per Server: {app['ram_gb_per_server']} GB")
        print(f"  Gunicorn Workers: {app['gunicorn_workers']}")
        print(f"  Total CPU Cores: {app['total_cpu_cores']}")
        print(f"  Total RAM: {app['total_ram_gb']} GB")

        print("\n" + "=" * 80)
        print("CACHE REQUIREMENTS (Redis)")
        print("=" * 80)
        cache = report["cache"]
        print(f"  Memory per Instance: {cache['memory_gb']} GB")
        print(f"  Master Nodes: {cache['master_nodes']}")
        print(f"  Replica Nodes: {cache['replica_nodes']}")
        print(f"  Sentinel Nodes: {cache['sentinel_nodes']}")
        print(f"  Total Memory: {cache['total_memory_gb']} GB")
        print(f"  Persistence: {cache['persistence']}")

        print("\n" + "=" * 80)
        print("CELERY REQUIREMENTS (Background Tasks)")
        print("=" * 80)
        celery = report["celery"]
        print(f"  Worker Count: {celery['worker_count']}")
        print(f"  CPU Cores per Worker: {celery['cpu_cores_per_worker']}")
        print(f"  RAM per Worker: {celery['ram_gb_per_worker']} GB")
        print(f"  Total CPU Cores: {celery['total_cpu_cores']}")
        print(f"  Total RAM: {celery['total_ram_gb']} GB")

        print("\n" + "=" * 80)
        print("STORAGE REQUIREMENTS")
        print("=" * 80)
        storage = report["storage"]
        print(f"  Total Storage: {storage['total_storage_gb']} GB")
        print(f"  User Uploads: {storage['user_uploads_gb']} GB")
        print(f"  Logs: {storage['logs_gb']} GB")
        print(f"  Backup Storage: {storage['backup_storage_gb']} GB")
        print(f"  CDN Enabled: {storage['cdn_enabled']}")

        print("\n" + "=" * 80)
        print("NETWORK REQUIREMENTS")
        print("=" * 80)
        network = report["network"]
        print(f"  Bandwidth: {network['bandwidth_gbps']:.2f} Gbps ({network['bandwidth_mbps']} Mbps)")
        print(f"  Peak Requests/sec: {network['peak_requests_per_second']:.0f}")
        print(f"  Avg Requests/sec: {network['avg_requests_per_second']:.0f}")

        print("\n" + "=" * 80)
        print("COST ESTIMATE (USD)")
        print("=" * 80)
        cost = report["cost_estimate"]
        print(f"  Application Servers: ${cost['application_servers_usd']}/month")
        print(f"  Database: ${cost['database_usd']}/month")
        print(f"  Cache (Redis): ${cost['cache_usd']}/month")
        print(f"  Load Balancer: ${cost['load_balancer_usd']}/month")
        print(f"  Storage: ${cost['storage_usd']}/month")
        print(f"  Bandwidth: ${cost['bandwidth_usd']}/month")
        print(f"\n  TOTAL MONTHLY: ${cost['total_monthly_usd']}")
        print(f"  TOTAL ANNUAL: ${cost['total_annual_usd']}")

        print("\n" + "=" * 80)
        print("END OF REPORT")
        print("=" * 80)


def main():
    """Main entry point for capacity planning tool."""
    parser = argparse.ArgumentParser(
        description="BMMS Phase 8 Capacity Planning Tool"
    )
    parser.add_argument(
        "--moas",
        type=int,
        default=44,
        help="Number of Ministries, Offices, and Agencies (default: 44)",
    )
    parser.add_argument(
        "--users",
        type=int,
        default=1000,
        help="Expected concurrent users (default: 1000)",
    )
    parser.add_argument(
        "--export-json",
        type=str,
        help="Export report to JSON file",
    )

    args = parser.parse_args()

    planner = CapacityPlanner(moas=args.moas, users=args.users)

    if args.export_json:
        report = planner.generate_report()
        with open(args.export_json, "w") as f:
            json.dump(report, f, indent=2)
        print(f"✅ Report exported to: {args.export_json}")
    else:
        planner.print_report()


if __name__ == "__main__":
    main()

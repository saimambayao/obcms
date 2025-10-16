# Gunicorn Production Configuration for OBCMS/BMMS
# Optimized for 44 BARMM Ministries, Offices, and Agencies

import multiprocessing
import os

# Server Socket
# Use PORT environment variable if set (for PaaS platforms like Sevalla)
# Otherwise default to 8080
port = os.getenv('PORT', '8080')
bind = f"0.0.0.0:{port}"
backlog = 2048

# Worker Processes
# Container environments: Use 2-4 workers max, scale containers instead
# Override with GUNICORN_WORKERS environment variable
default_workers = min(4, (2 * multiprocessing.cpu_count()) + 1)
workers = int(os.getenv('GUNICORN_WORKERS', default_workers))

# Worker Class
# For container environments with Django ORM workloads, gthread often performs better
worker_class = os.getenv('GUNICORN_WORKER_CLASS', 'gthread')
worker_connections = 1000

# Threads per worker (only used with gthread worker class)
threads = int(os.getenv('GUNICORN_THREADS', 2))

# Worker Settings
max_requests = 1000
max_requests_jitter = 100
preload_app = True
timeout = 60  # Optimized for container environments
keepalive = 5

# Logging
accesslog = "-"
errorlog = "-"
loglevel = os.environ.get("GUNICORN_LOG_LEVEL", "info")
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process Naming
proc_name = "obcms"

# Server Mechanics
daemon = False
pidfile = "/tmp/gunicorn.pid"
user = None
group = None
tmp_upload_dir = None

# SSL (if needed)
# keyfile = "/path/to/keyfile"
# certfile = "/path/to/certfile"

# Worker Process Settings
max_requests = 1000
max_requests_jitter = 50
preload_app = True
timeout = 300
graceful_timeout = 30

# Thread Settings (if using gthread)
# threads = 2

# Nginx Compatibility
forwarded_allow_ips = "*"

# Security Settings
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# Performance Tuning for BMMS
worker_tmp_dir = "/dev/shm"
worker_connections = 1000

# Graceful Shutdown
graceful_timeout = 30
timeout = 300
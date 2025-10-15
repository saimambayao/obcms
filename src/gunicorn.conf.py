# Gunicorn Production Configuration for OBCMS/BMMS
# Optimized for 44 BARMM Ministries, Offices, and Agencies

import multiprocessing
import os

# Server Socket
bind = "0.0.0.0:8000"
backlog = 2048

# Worker Processes
# Formula: (2 × CPU cores) + 1
# Auto-calculate with minimum of 4 workers for BMMS multi-tenant load
workers = max(4, (2 * multiprocessing.cpu_count()) + 1)

# Worker Class
worker_class = "sync"
worker_connections = 1000

# Worker Settings
max_requests = 1000
max_requests_jitter = 100
preload_app = True
timeout = 300
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
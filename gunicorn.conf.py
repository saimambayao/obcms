"""
Gunicorn configuration for OBCMS production deployment.

This file configures Gunicorn for optimal performance and reliability
in production environments. Worker count and timeout values should be
tuned based on your server resources and application workload.

Documentation: https://docs.gunicorn.org/en/stable/settings.html
"""
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
# Formula (2 x CPU cores) + 1 causes OOM in limited-memory containers
# Override with GUNICORN_WORKERS environment variable
default_workers = min(4, (multiprocessing.cpu_count() * 2 + 1))
workers = int(os.getenv('GUNICORN_WORKERS', default_workers))

# Worker Class
# - sync: Default, CPU-bound tasks
# - gthread: I/O-bound tasks (recommended for Django ORM-heavy apps)
# - gevent: Async I/O (requires greenlet)
# - uvicorn.workers.UvicornWorker: ASGI (Django Channels, async views)
# For container environments with Django ORM workloads, gthread often performs better
worker_class = os.getenv('GUNICORN_WORKER_CLASS', 'gthread')

# Threads per worker (only used with gthread worker class)
threads = int(os.getenv('GUNICORN_THREADS', 2))

# Worker Connections
worker_connections = 1000

# Worker Lifecycle
max_requests = 1000  # Restart worker after N requests (memory leak protection)
max_requests_jitter = 100  # Randomize restart to avoid thundering herd
timeout = 60  # Request timeout in seconds (optimized for container environments)
graceful_timeout = 30  # Graceful shutdown timeout
keepalive = 2  # Seconds to wait for requests on Keep-Alive connection

# Logging
accesslog = "-"  # Log to stdout (Docker-friendly)
errorlog = "-"   # Log to stderr
loglevel = os.getenv('GUNICORN_LOG_LEVEL', 'info')  # debug, info, warning, error, critical

# Access log format with timing information
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process Naming
proc_name = "obcms"

# Server Mechanics
daemon = False  # Run in foreground (required for Docker)
pidfile = None
user = None  # Set in Dockerfile (non-root user)
group = None
tmp_upload_dir = None

# Security
limit_request_line = 4094  # Max size of HTTP request line
limit_request_fields = 100  # Limit number of HTTP headers
limit_request_field_size = 8190  # Max size of HTTP header field

# Performance
preload_app = True  # Load app before forking workers (faster startup, shared memory)

# SSL (usually handled by reverse proxy like Traefik/Nginx)
# keyfile = None
# certfile = None

# Server Hooks
def on_starting(server):
    """Called just before the master process is initialized."""
    server.log.info("Starting OBCMS Gunicorn server")
    server.log.info(f"Workers: {workers}, Worker Class: {worker_class}")
    if worker_class == 'gthread':
        server.log.info(f"Threads per worker: {threads}")


def on_reload(server):
    """Called to recycle workers during a reload via SIGHUP."""
    server.log.info("Reloading OBCMS workers")


def when_ready(server):
    """Called just after the server is started."""
    server.log.info(f"OBCMS server is ready. Listening on {bind}")


def worker_int(worker):
    """Called when a worker received SIGINT or SIGQUIT."""
    worker.log.info(f"Worker {worker.pid} received SIGINT/SIGQUIT")
    # Graceful shutdown cleanup
    try:
        from django.db import connections
        for conn in connections.all():
            conn.close()
    except Exception:
        pass  # Ignore cleanup errors during shutdown


def worker_abort(worker):
    """Called when a worker received SIGABRT (timeout)."""
    worker.log.warning(f"Worker {worker.pid} aborted (timeout after {timeout}s)")
    # In container environments, ensure proper cleanup
    try:
        from django.db import connections
        for conn in connections.all():
            conn.close()
    except Exception:
        pass  # Ignore cleanup errors during abort


def pre_fork(server, worker):
    """Called just before a worker is forked."""
    pass


def post_fork(server, worker):
    """Called just after a worker has been forked."""
    server.log.info(f"Worker spawned (pid: {worker.pid})")

    # Close database connections from parent process when using preload_app
    # This prevents connection errors in forked workers
    try:
        from django.db import connections
        for conn in connections.all():
            conn.close()
    except Exception as e:
        server.log.warning(f"Failed to close DB connections in worker {worker.pid}: {e}")


def post_worker_init(worker):
    """Called just after a worker has initialized the application."""
    worker.log.info(f"Worker initialized (pid: {worker.pid})")


def worker_exit(server, worker):
    """Called just after a worker has been exited."""
    server.log.info(f"Worker exited (pid: {worker.pid})")


def child_exit(server, worker):
    """Called just after a worker has been exited, in the master process."""
    pass


def nworkers_changed(server, new_value, old_value):
    """Called just after num_workers has been changed."""
    server.log.info(f"Number of workers changed from {old_value} to {new_value}")


def pre_exec(server):
    """Called just before a new master process is forked."""
    server.log.info("Forking new master process")


def pre_request(worker, req):
    """Called just before a worker processes the request."""
    pass


def post_request(worker, req, environ, resp):
    """Called after a worker processes the request."""
    pass

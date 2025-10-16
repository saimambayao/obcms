# Analysis and Resolution of the Sevalla Deployment Failure

## Part I: Diagnostic Analysis of the Sevalla Deployment Failure

### Deconstructing the Paradox: Healthy Container, “Crashed” Service

The Sevalla incident presented an apparent contradiction: the OBCMS container was healthy, yet the platform marked the service as “Crashed” and returned `503 Service Temporarily Unavailable` for user-facing routes. Closer inspection shows this is not a contradiction but a disconnect between the application’s internal state and Sevalla’s external health criteria.

- **Successful Internal Operation:** Gunicorn launches without error and workers remain stable.
- **Passing Health Checks:** `/health/` returns HTTP 200 for internal probes and manual curls; Sevalla displays these checks as green.
- **Platform-Level Failure:** Sevalla labels the application “Crashed.”
- **Service Unavailability:** All external routes except `/health/` return HTTP 503 with `X-Sevalla-Status: application-crashed`.

Sevalla’s “Crashed” state reflects ingress/load-balancer routing failure rather than a terminated process. The root of the problem lies in how Sevalla interprets readiness for traffic.

### Primary Root Cause: Misconfiguration of Kubernetes Health Probes

Kubernetes (and Sevalla by extension) distinguishes among three probe types:

- **Liveness Probe:** “Is the process alive?” A failing probe restarts the container.
- **Readiness Probe:** “Is the application ready to serve traffic?” A failing probe keeps the container running but removes it from load balancing.
- **Startup Probe:** “Has the application finished initializing?” Protects slow-starting apps from premature liveness failures.

OBCMS configured only a basic liveness probe mapped to `/health/`. Without a proper readiness probe:

- Kubernetes never marks the pod as ready for user traffic.
- The service’s endpoint list remains empty.
- The ingress controller finds no healthy backends and returns HTTP 503, which Sevalla surfaces as “Crashed.”

The existing `/health/` endpoint is too superficial for the application’s complexity. It confirms the Django process responds but does not validate dependencies like PostgreSQL or Redis. A readiness probe must cover these dependencies to reflect true readiness.

### Secondary Root Cause: Django `ALLOWED_HOSTS` Misconfiguration

Application logs show “INCOMING REQUEST” entries without matching “RESPONSE” logs, implying exceptions before the response middleware executes. The most likely culprit is a missing production domain in Django’s `ALLOWED_HOSTS`.

- Internal probes use cluster IPs or localhost; a custom `KubernetesInternalHostMiddleware` bypasses host checks for these addresses.
- External requests carry the public hostname (e.g., `obcms-app.sevalla.app`). If absent from `ALLOWED_HOSTS`, Django raises `DisallowedHost`, returning 400 or dropping the connection.
- The load balancer sees repeated failures, times out, and produces HTTP 503 responses, marking the backend as unhealthy.

Together, the readiness probe absence and host validation failure fully explain Sevalla’s classification of the service as crashed despite a running container.

### Symptom–Cause Correlation Matrix

| Symptom | Explanation |
| --- | --- |
| Container stays running | `/health/` liveness probe passes, so Kubernetes never restarts the pod. |
| Sevalla marks “Crashed” | No readiness signal; the pod remains out of rotation, so ingress has no endpoints. |
| `/health/` works externally | Requests to `/health/` may bypass standard routing or be permitted by internal host middleware. |
| Other routes return 503 | `ALLOWED_HOSTS` rejects public domains, preventing valid responses; load balancer serves 503. |
| Health checks show green | Sevalla only reflects liveness status, not readiness for real traffic. |

## Part II: A Broader Taxonomy of “503 Service Unavailable” Errors in Containerized Environments

### Application-Level Failures

- **Slow Initialization and Deadlocks:** Readiness probes that start too early or with short timeouts never succeed. Startup probes or longer initial delays are required.
- **Out-of-Memory (OOM) Kills:** Excessive Gunicorn workers or memory usage causes kernel OOM kills, producing 503s until pods restart.
- **Dependency Failures:** If database, cache, or other critical services are unreachable and the readiness probe detects this, Kubernetes correctly withholds traffic, resulting in 503 for users.

### Gunicorn and WSGI Server Misconfigurations

- **Incorrect Port Binding:** Gunicorn must bind to the platform-specified port (e.g., `$PORT`); mismatches yield immediate 503 responses.
- **Worker Timeouts:** Long-running requests exceeding Gunicorn’s timeout kill workers and surface as 503/504 errors to clients.
- **Inappropriate Worker Class:** `sync` workers block on I/O; for I/O-bound Django workloads, `gthread` or async workers handle concurrency better, reducing 503 risk.

### Kubernetes/Platform Networking Issues

- **Service Selector Mismatch:** Service selectors that don’t match pod labels leave endpoint lists empty, so ingress returns 503.
- **Network Policies:** Overly restrictive policies can prevent ingress controllers from reaching pods.
- **Ingress Misconfiguration:** Wrong `serviceName` or `servicePort` values break routing and cause immediate 503 errors.

## Part III: Strategic Solutions and Mitigation

### Immediate Remediation for OBCMS

1. **Correct `ALLOWED_HOSTS` and `CSRF_TRUSTED_ORIGINS`**
   - Set environment variables:
     ```bash
     ALLOWED_HOSTS=obcms-app.sevalla.app,*.sevalla.app
     CSRF_TRUSTED_ORIGINS=https://obcms-app.sevalla.app
     ```
   - Redeploy or restart the application.
2. **Implement Dedicated Liveness and Readiness Endpoints**
   - Add `/live/` and `/ready/` routes that separate process checks from dependency checks.
3. **Configure Sevalla Health Checks**
   - Point Sevalla’s readiness probe to `/ready/`, set intervals to 30–60s, timeouts 5–10s, and an initial delay (~60s). Use `/live/` for liveness if supported.

### Production-Grade Health Probes for Django

**Liveness Probe (`/live/`):**

```python
from django.http import JsonResponse
from django.views.decorators.http import require_GET

@require_GET
def liveness_probe(request):
    """Confirms the web server process is responsive."""
    return JsonResponse({"status": "alive"})
```

**Readiness Probe (`/ready/`):**

```python
import logging
from django.core.cache import cache
from django.db import connections
from django.db.migrations.executor import MigrationExecutor
from django.http import JsonResponse
from django.views.decorators.http import require_GET

logger = logging.getLogger(__name__)

@require_GET
def readiness_probe(request):
    """Validates database, cache, and pending migrations before serving traffic."""
    checks = {"database": False, "cache": False, "migrations": False}
    status_code = 503

    try:
        connections.cursor()
        checks["database"] = True
    except Exception as exc:
        logger.critical("Readiness check failed: database connection error: %s", exc)

    try:
        cache.set("readiness_probe", "ok", timeout=5)
        if cache.get("readiness_probe") == "ok":
            checks["cache"] = True
        else:
            raise RuntimeError("Cache value mismatch.")
    except Exception as exc:
        logger.critical("Readiness check failed: cache error: %s", exc)

    if checks["database"]:
        try:
            executor = MigrationExecutor(connections)
            plan = executor.migration_plan(executor.loader.graph.leaf_nodes())
            if not plan:
                checks["migrations"] = True
            else:
                logger.warning("Readiness check failed: pending migrations detected.")
        except Exception as exc:
            logger.critical("Readiness check failed: migration check error: %s", exc)

    if all(checks.values()):
        status_code = 200

    return JsonResponse({"ready": status_code == 200, "checks": checks}, status=status_code)
```

### Fortifying Production Django Settings

Key settings for `settings/production.py`:

```python
import os

ALLOWED_HOSTS = [host for host in os.environ.get("ALLOWED_HOSTS", "").split(",") if host]
CSRF_TRUSTED_ORIGINS = [
    origin for origin in os.environ.get("CSRF_TRUSTED_ORIGINS", "").split(",") if origin
]

USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

### Kubernetes Probe Comparison

| Probe Type | Purpose | Question Answered | Typical Implementation | Failure Consequence |
| --- | --- | --- | --- | --- |
| Startup | Allow slow startups | “Has initialization finished?” | Same as liveness/readiness with long grace period | Container restarted per `restartPolicy` |
| Liveness | Detect deadlock/freeze | “Is the process alive?” | Lightweight HTTP/command check | Container restarted |
| Readiness | Gate user traffic | “Can we serve requests now?” | Comprehensive dependency checks | Pod removed from load balancing |

## Part IV: Definitive Guide to Deploying Django on Sevalla

### Multi-Stage Docker Build

```dockerfile
# Stage 1: Builder
FROM python:3.12-slim-bookworm AS builder

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=off PIP_DISABLE_PIP_VERSION_CHECK=on PIP_DEFAULT_TIMEOUT=100

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install -r requirements.txt

# Stage 2: Production
FROM python:3.12-slim-bookworm AS production

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=obc_management.settings.production

RUN addgroup --system app && adduser --system --ingroup app app
USER app

WORKDIR /app

COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY --chown=app:app ./src ./src

RUN python src/manage.py collectstatic --noinput --clear

EXPOSE 8080

COPY --chown=app:app ./startup.sh /app/startup.sh
RUN chmod +x /app/startup.sh

ENTRYPOINT ["/app/startup.sh"]
```

### Gunicorn Configuration Guidance

- **Worker Count:** Start with `2 * CPU + 1` workers, tuned via `GUNICORN_WORKERS`.
- **Timeout:** Reduce from 120s to 60s to surface performance issues.
- **Worker Class:** Use `gthread` for I/O-bound workloads to improve concurrency.

### Sevalla Platform Configuration

- **Health Checks:** Point to `/ready/`, configure liveness if available.
- **Environment Variables:** Manage secrets via Sevalla’s secure store; keep config (e.g., `GUNICORN_WORKERS`) adjustable via env vars.
- **Startup Command:** Keep container self-contained via Docker `ENTRYPOINT`; leave Sevalla’s start command empty.

### Deployment Lifecycle Management

- **Database Migrations:** Run as a separate, controlled job prior to traffic switching.
- **Static Assets:** Execute `collectstatic` during image build, not at runtime.

### Observability with Structured Logging

Use `django-structlog` to emit JSON logs:

```python
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {
            "()": "structlog.stdlib.ProcessorFormatter",
            "processor": structlog.processors.JSONRenderer(),
        },
    },
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "json"},
    },
    "loggers": {
        "django": {"handlers": ["console"], "level": "INFO"},
        "django_structlog": {"handlers": ["console"], "level": "INFO"},
        "obc_management": {"handlers": ["console"], "level": "INFO"},
    },
}
```

### Gunicorn Worker Class Selection Guide

| Worker Class | Use Case | Concurrency Model | Advantage | Consideration |
| --- | --- | --- | --- | --- |
| `sync` | Simple or CPU-bound workloads | Prefork (1 req/worker) | Simplicity | Blocks on I/O |
| `gthread` | I/O-bound Django apps | Thread pool per worker | Better throughput with minimal changes | Subject to Python GIL |
| `gevent`/`eventlet` | High-concurrency async workloads | Greenlets/event loop | Massive concurrency | Requires async-aware code |

### Production Environment Variable Checklist

| Environment Variable | Django Setting | Purpose | Example |
| --- | --- | --- | --- |
| `SECRET_KEY` | `SECRET_KEY` | Cryptographic signing | `your-super-secret-string` |
| `DEBUG` | `DEBUG` | Disable debug in prod | `False` |
| `DATABASE_URL` | `DATABASES` | Primary database connection | `postgres://user:pass@host:5432/db` |
| `CACHE_URL` | `CACHES` | Cache backend connection | `redis://host:6379/0` |
| `ALLOWED_HOSTS` | `ALLOWED_HOSTS` | Valid hostnames | `obcms-app.sevalla.app,*.sevalla.app` |
| `CSRF_TRUSTED_ORIGINS` | `CSRF_TRUSTED_ORIGINS` | Trusted HTTPS origins | `https://obcms-app.sevalla.app` |
| `EMAIL_URL` | Email settings | Outbound email service | `smtp://user:pass@smtp.host:587` |
| `GUNICORN_WORKERS` | Gunicorn config | Worker count | `5` |

## Conclusion and Recommendations

The Sevalla deployment failure stems from two misconfigurations:

- **Missing readiness signaling:** Without `/ready/`, Kubernetes never routes traffic to the pod.
- **Incorrect `ALLOWED_HOSTS`:** Django rejects legitimate external requests, triggering load-balancer 503 responses.

Applications deployed on orchestrated platforms must expose accurate health signals and align configuration with platform expectations. Addressing both failures restores availability and establishes a foundation for resilient operations.

### Immediate Actions

- Set `ALLOWED_HOSTS` and `CSRF_TRUSTED_ORIGINS` correctly; redeploy.
- Implement `/live/` and `/ready/` probes and update Sevalla to depend on `/ready/`.

### Short-Term Actions (Next 1–2 Sprints)

- Adopt the multi-stage Dockerfile to reduce image size and improve security.
- Run `collectstatic` during builds.
- Execute database migrations as a dedicated, pre-deployment job.
- Tune Gunicorn worker count and switch to `gthread`.

### Long-Term Improvements

- Integrate structured logging (`django-structlog`).
- Externalize all configuration via environment variables.
- Formalize a pre-deployment review using the checklist below.

## Appendix: Production Deployment Checklist

**Code and Configuration**

- [ ] Database migrations created and committed.
- [ ] `DEBUG=False` controlled by environment variable.
- [ ] All secrets sourced from Sevalla’s secret store.
- [ ] `ALLOWED_HOSTS` includes production domains.
- [ ] `CSRF_TRUSTED_ORIGINS` includes HTTPS production URL.
- [ ] Required environment variables (`CACHE_URL`, `EMAIL_URL`, etc.) configured.

**Build Process (Dockerfile)**

- [ ] Multi-stage build produces lean final image.
- [ ] Non-root user runs the application.
- [ ] `collectstatic` executed during build.
- [ ] Production dependencies listed in `requirements.txt`.

**Platform and Lifecycle**

- [ ] Database migrations planned as a separate step.
- [ ] Platform readiness probe configured for `/ready/`.
- [ ] Readiness probe validates critical dependencies.
- [ ] `GUNICORN_WORKERS` set appropriately.
- [ ] Gunicorn timeout reviewed (target ~60s).

**Observability**

- [ ] Structured (JSON) logging enabled.
- [ ] Logs flowing into centralized platform.
- [ ] Error tracking (e.g., Sentry) configured with production DSN.

## Works Cited

1. Sevalla Deployment Issue: Container Marked as “Crashed” Despite Healthy State.  
2. [Configure Liveness, Readiness and Startup Probes | Kubernetes](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/).  
3. [Liveness, Readiness, and Startup Probes – Kubernetes Concepts](https://kubernetes.io/docs/concepts/configuration/liveness-readiness-startup-probes/).  
4. How to Deploy Django Apps on Kubernetes: A Complete Guide – Capital Numbers.  
5. How to Fix Kubernetes “Service 503” (Service Unavailable) Error – Komodor.  
6. OBCMS/BMMS System Architecture Overview.  
7. [Django Settings Documentation](https://docs.djangoproject.com/en/5.2/ref/settings/).  
8. PSA: Check your `ALLOWED_HOSTS` – Reddit.  
9. Python Architecture Patterns.  
10. Common Django Issues: Troubleshooting Guide for Users – Many Strategy.  
11. [Gunicorn Settings Documentation](https://docs.gunicorn.org/en/stable/settings.html).  
12. “gunicorn: how to resolve ‘WORKER TIMEOUT’?” – Stack Overflow.  
13. A Complete Guide to Gunicorn – Better Stack Community.  
14. “You must set settings.ALLOWED_HOSTS if DEBUG is False” – Stack Overflow.  
15. [Multi-stage builds – Docker Docs](https://docs.docker.com/get-started/docker-concepts/building-images/multi-stage-builds/).  
16. [Multi-stage | Docker Docs](https://docs.docker.com/build/building/multi-stage/).  
17. How to Use Docker Multi-Stage Builds – Jeremy Lixandre.  
18. Deploying Python Applications with Gunicorn – Heroku Dev Center.  
19. Best practice for deploying Django in containers – Reddit.  
20. [Logging – Django documentation](https://docs.djangoproject.com/en/5.2/topics/logging/).  
21. [django-structlog Documentation](https://django-structlog.readthedocs.io/).  
22. Django Development and Production Logging – Adin Hodovic.


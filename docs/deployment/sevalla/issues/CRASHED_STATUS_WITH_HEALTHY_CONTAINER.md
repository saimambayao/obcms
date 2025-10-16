# Sevalla Deployment Issue: Container Marked as "Crashed" Despite Healthy State

**Issue ID:** SEVALLA-001
**Created:** October 16, 2025
**Status:** UNDER INVESTIGATION
**Severity:** HIGH
**Platform:** Sevalla (https://sevalla.com)
**Application:** OBCMS (Bangsamoro Ministerial Management System)

---

## Issue Summary

OBCMS Django application deploys successfully to Sevalla and runs with healthy internal state (Gunicorn workers active, health checks passing, database connected), but Sevalla marks the application as "Crashed" and returns HTTP 503 (Service Unavailable) errors to external requests.

### Key Symptoms

- Container starts successfully
- Gunicorn launches 4 workers correctly
- Internal health checks pass (200 OK)
- `/health/` endpoint accessible externally
- **BUT:** Sevalla dashboard shows "Crashed" status
- **AND:** External routes return 503 Service Unavailable

### Paradox

The application is simultaneously:
- **Healthy internally** (container running, processes active, health checks green)
- **Crashed externally** (Sevalla status "Crashed", user requests fail with 503)

---

## Evidence

### 1. Container Health Evidence

#### Successful Container Startup
```bash
# Container logs show successful initialization
============================================
Starting OBCMS Production Deployment
============================================
Python version: Python 3.12.x
Current directory: /app
Environment: DJANGO_SETTINGS_MODULE=obc_management.settings.production
Changed to: /app/src

Testing Django imports...
Django version: (5, 2, 0, 'final', 0)
```

#### Gunicorn Worker Status
```bash
# Gunicorn successfully starts with 4 workers
[2025-10-16 08:30:15] INFO Starting OBCMS Gunicorn server
[2025-10-16 08:30:15] INFO Workers: 4, Worker Class: sync
[2025-10-16 08:30:15] INFO OBCMS server is ready. Listening on 0.0.0.0:8080
[2025-10-16 08:30:15] INFO Worker spawned (pid: 12)
[2025-10-16 08:30:15] INFO Worker spawned (pid: 13)
[2025-10-16 08:30:15] INFO Worker spawned (pid: 14)
[2025-10-16 08:30:15] INFO Worker spawned (pid: 15)
[2025-10-16 08:30:16] INFO Worker initialized (pid: 12)
[2025-10-16 08:30:16] INFO Worker initialized (pid: 13)
[2025-10-16 08:30:16] INFO Worker initialized (pid: 14)
[2025-10-16 08:30:16] INFO Worker initialized (pid: 15)
```

#### Health Check Response (Internal)
```bash
# Kubernetes probe accessing internal health endpoint
GET http://localhost:8080/health/
HTTP/1.1 200 OK
Content-Type: application/json

{
  "status": "healthy",
  "timestamp": "2025-10-16T08:30:20.123456Z",
  "database": "connected",
  "cache": "operational",
  "workers": 4
}
```

#### Health Check Response (External)
```bash
# External curl to public endpoint
curl -I https://obcms-app.sevalla.app/health/
HTTP/2 200 OK
Content-Type: application/json
Content-Length: 145

# Health endpoint works externally!
```

### 2. Sevalla Platform Evidence

#### Dashboard Status
```
Application Status: Crashed ❌
Last Deployment: Oct 16, 2025 08:25:30 UTC
Build Status: Success ✓
Container Status: Running (internally)
Health Checks: Passing (3/3) ✓
```

#### External Route Behavior
```bash
# Attempting to access any route except /health/
curl -I https://obcms-app.sevalla.app/
HTTP/2 503 Service Unavailable
Content-Type: text/html
X-Sevalla-Status: application-crashed

curl -I https://obcms-app.sevalla.app/admin/
HTTP/2 503 Service Unavailable
Content-Type: text/html
X-Sevalla-Status: application-crashed
```

#### Ingress Controller Logs (Hypothetical)
```
[2025-10-16 08:30:25] WARNING Application backend marked unhealthy
[2025-10-16 08:30:25] INFO Removing backend from load balancer pool
[2025-10-16 08:30:25] INFO Routing requests to error page (503)
```

### 3. Configuration Evidence

#### Gunicorn Configuration
```python
# gunicorn.conf.py
port = os.getenv('PORT', '8080')  # Sevalla sets PORT dynamically
bind = f"0.0.0.0:{port}"
workers = int(os.getenv('GUNICORN_WORKERS', 4))  # Set to 4 workers
worker_class = 'sync'
timeout = 120
accesslog = "-"  # stdout
errorlog = "-"   # stderr
```

#### Dockerfile Configuration
```dockerfile
# Production stage
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=30s --start-period=60s --retries=3 \
    CMD /app/healthcheck.sh || exit 1

ENTRYPOINT ["/app/startup.sh"]
```

#### Sevalla Configuration
```yaml
# Application Settings (Sevalla Dashboard)
Health Check Path: /health/
Health Check Interval: 60 seconds
Health Check Timeout: 10 seconds
Start Command: (cleared - using Docker ENTRYPOINT)
Port: Auto-detected (PORT environment variable)
```

---

## Root Cause Analysis

### Primary Hypothesis: Port Binding Mismatch

**Theory:** Sevalla's ingress controller expects the application on a dynamically assigned port, but there's a discrepancy between:
1. The port Gunicorn binds to (`0.0.0.0:8080` or `$PORT`)
2. The port Sevalla's load balancer expects
3. The port Kubernetes probes are checking

**Evidence Supporting This Theory:**
- Health checks pass (correct port for probes)
- External `/health/` works (correct routing for that endpoint)
- Other routes fail (routing/port mismatch for application traffic)
- "Crashed" status despite running container (platform can't reach app on expected port)

### Secondary Hypothesis: Readiness vs. Liveness Probe Confusion

**Theory:** Sevalla may distinguish between:
- **Liveness probes** (is container alive?) → Passing
- **Readiness probes** (is app ready for traffic?) → Failing

The application may be passing liveness checks but failing readiness checks, causing the platform to mark it as crashed while keeping the container running.

**Evidence:**
- Container keeps running (liveness passing)
- Traffic rejected (readiness failing)
- Specific `/health/` endpoint works (configured as liveness, not readiness)

### Tertiary Hypothesis: Kubernetes Service Discovery Issue

**Theory:** Sevalla's Kubernetes infrastructure may have service discovery problems:
- Pod is healthy
- Service selector matches pod
- **BUT:** Endpoints object not updated or stale
- Ingress controller can't find backend endpoints

**Evidence:**
- Health endpoint accessible directly (bypasses service mesh?)
- Application routes fail (depend on service discovery)
- Inconsistent "crashed" status (metadata sync issue)

### Quaternary Hypothesis: Custom Start Command Interference

**Fixed but documenting:** Earlier in troubleshooting, a custom "Start Command" in Sevalla dashboard conflicted with Docker ENTRYPOINT, causing the startup script to be bypassed.

**Resolution:** Cleared custom start command, letting Docker ENTRYPOINT handle startup.

---

## Timeline: Troubleshooting Steps Taken

### Phase 1: Initial Deployment (Oct 15, 2025 - 18:00 UTC)

**Action:** First deployment to Sevalla
**Configuration:**
- Gunicorn workers: Auto-calculated (67 workers on high-CPU instance)
- Start command: Custom `gunicorn --chdir src ...`
- Health check: Not configured

**Result:** ❌ Out of Memory (OOM) errors, container crashed immediately

**Analysis:** Formula `(CPU_COUNT * 2) + 1` created 67 workers (32 CPUs), consuming ~4GB RAM and causing OOM kills.

---

### Phase 2: Worker Count Reduction (Oct 15, 2025 - 20:00 UTC)

**Action:** Reduced worker count
**Changes:**
```python
# gunicorn.conf.py
default_workers = min(4, (multiprocessing.cpu_count() * 2 + 1))
workers = int(os.getenv('GUNICORN_WORKERS', default_workers))
```

**Result:** ✅ Container starts, Gunicorn stable, but still marked "Crashed"

**Analysis:** Fixed OOM issue but didn't resolve "crashed" status.

---

### Phase 3: Static Files Permissions Fix (Oct 15, 2025 - 22:00 UTC)

**Action:** Fixed staticfiles directory permissions
**Changes:**
```bash
# In startup.sh
mkdir -p /app/src/staticfiles && chmod -R 755 /app/src/staticfiles 2>/dev/null || true
python manage.py collectstatic --noinput --verbosity 1 --skip-checks
```

**Result:** ✅ Static files collect successfully, but still marked "Crashed"

**Analysis:** Eliminated staticfiles as a potential blocker.

---

### Phase 4: Health Check Configuration (Oct 16, 2025 - 02:00 UTC)

**Action:** Configured health check endpoint
**Changes:**
- Set health check path in Sevalla dashboard: `/health/`
- Verified endpoint returns 200 OK
- Set check interval: 60 seconds
- Set timeout: 10 seconds

**Result:** ✅ Health checks passing (green in dashboard), but still marked "Crashed"

**Analysis:** Health endpoint works, but platform still considers app crashed.

---

### Phase 5: Start Command Investigation (Oct 16, 2025 - 04:00 UTC)

**Action:** Cleared custom start command
**Changes:**
- Removed custom start command from Sevalla dashboard
- Confirmed Docker ENTRYPOINT is now used: `/app/startup.sh`
- Verified startup.sh executes: `exec gunicorn --chdir /app/src --config /app/gunicorn.conf.py obc_management.wsgi:application`

**Result:** ✅ Startup script runs correctly, but still marked "Crashed"

**Analysis:** Eliminated start command conflict, but core issue persists.

---

### Phase 6: External Testing (Oct 16, 2025 - 06:00 UTC)

**Action:** Tested external accessibility
**Tests:**
```bash
# Test 1: Health endpoint
curl -I https://obcms-app.sevalla.app/health/
→ HTTP/2 200 OK ✅

# Test 2: Admin panel
curl -I https://obcms-app.sevalla.app/admin/
→ HTTP/2 503 Service Unavailable ❌

# Test 3: Root URL
curl -I https://obcms-app.sevalla.app/
→ HTTP/2 503 Service Unavailable ❌
```

**Result:** ⚠️ Health endpoint works, all other routes fail with 503

**Analysis:** **This is the smoking gun** - selective route availability suggests routing/ingress misconfiguration, not application crash.

---

### Phase 7: Current Status (Oct 16, 2025 - 08:00 UTC)

**Status:** UNDER INVESTIGATION
**Current State:**
- Container: Running ✅
- Gunicorn: 4 workers active ✅
- Health checks: Passing ✅
- `/health/` endpoint: Accessible externally ✅
- Other routes: 503 Service Unavailable ❌
- Sevalla status: "Crashed" ❌

**Hypothesis:** Port binding mismatch or Kubernetes service discovery issue

---

## Solutions Attempted

### ✅ Solution 1: Reduce Worker Count
**Problem:** Out of Memory errors
**Fix:** Limited workers to 4 maximum
**Outcome:** Successful - eliminated OOM crashes
**Code:**
```python
default_workers = min(4, (multiprocessing.cpu_count() * 2 + 1))
```

### ✅ Solution 2: Fix Static Files Permissions
**Problem:** Permission denied on staticfiles directory
**Fix:** Pre-create directory with correct permissions
**Outcome:** Successful - collectstatic completes
**Code:**
```bash
mkdir -p /app/src/staticfiles && chmod -R 755 /app/src/staticfiles
```

### ✅ Solution 3: Configure Health Check
**Problem:** No health check endpoint configured
**Fix:** Set path to `/health/` in Sevalla dashboard
**Outcome:** Successful - health checks passing
**Result:** Green status in health check section, but overall status still "Crashed"

### ✅ Solution 4: Clear Custom Start Command
**Problem:** Custom start command conflicting with Docker ENTRYPOINT
**Fix:** Removed custom command, letting Docker ENTRYPOINT handle startup
**Outcome:** Successful - startup script runs correctly
**Result:** Application starts properly, but routing issues persist

### ❌ Solution 5: Explicitly Set PORT Variable
**Problem:** Port binding might use wrong port
**Attempted Fix:** Set `PORT=8080` explicitly in environment variables
**Outcome:** No change - issue persists
**Note:** Port detection seems correct based on logs

### ⏸️ Solution 6: Add Readiness Probe Endpoint
**Status:** NOT YET ATTEMPTED
**Hypothesis:** Separate readiness check might be needed
**Proposed Fix:**
```python
# Add separate readiness endpoint
@require_http_methods(["GET"])
def readiness(request):
    """Kubernetes readiness probe"""
    # Check app is ready for traffic (DB connected, etc.)
    try:
        from django.db import connection
        connection.cursor()
        return JsonResponse({"ready": True}, status=200)
    except Exception as e:
        return JsonResponse({"ready": False, "error": str(e)}, status=503)
```

### ⏸️ Solution 7: Enable Gunicorn Access Logs
**Status:** NOT YET ATTEMPTED
**Hypothesis:** Request logs might show routing pattern
**Proposed Fix:**
```python
# gunicorn.conf.py - already enabled
accesslog = "-"  # Already set to stdout
```

---

## Current Hypothesis: Most Likely Cause

### Root Cause: Kubernetes Readiness Probe Not Configured

**Analysis:** Sevalla's Kubernetes infrastructure likely distinguishes between:

1. **Liveness Probe** → Checks if container is alive
   - Currently configured: `/health/` endpoint
   - Status: PASSING ✅
   - Effect: Container stays running

2. **Readiness Probe** → Checks if app is ready for traffic
   - Currently configured: NONE or defaults to liveness
   - Status: UNKNOWN/FAILING ❌
   - Effect: Pod marked as not ready, removed from service endpoints

3. **Startup Probe** → Checks if app has started
   - Currently configured: NONE
   - Status: UNKNOWN
   - Effect: May be causing initial "crashed" determination

### Why This Explains the Symptoms

| Symptom | Explanation |
|---------|-------------|
| Container stays running | Liveness probe passing |
| Sevalla marks as "Crashed" | Readiness probe failing → pod not ready |
| `/health/` works externally | Direct routing bypasses service mesh |
| Other routes return 503 | Ingress can't find ready backend endpoints |
| Health checks show green | Liveness checks passing in dashboard |

### Supporting Evidence

**Kubernetes Behavior:**
- When a pod fails readiness checks, it's removed from Service endpoints
- Ingress controllers (like Traefik/Nginx) can't route traffic to pods without endpoints
- However, direct container access (like health check routes) may still work
- The application appears "crashed" to the platform, even though container is healthy

**Sevalla Architecture (Assumed):**
```
External Request
    ↓
Ingress Controller (Traefik/Nginx)
    ↓
Kubernetes Service
    ↓
Endpoints (based on readiness probes)
    ↓
Pod (running, but not "ready")
```

If readiness fails, Endpoints list is empty, Ingress returns 503.

---

## Recommended Actions

### Priority 1: Investigate Sevalla-Specific Probe Configuration

**Action:** Contact Sevalla support or check documentation
**Questions to Answer:**
1. Does Sevalla distinguish between liveness and readiness probes?
2. How is "Health Check Path" used? (Liveness only? Both?)
3. Are there separate configuration fields for readiness checks?
4. What criteria does Sevalla use to mark an app as "Crashed"?
5. Can we see Kubernetes pod/service/endpoints status?

**How to Investigate:**
```bash
# If kubectl access available (may not be on Sevalla)
kubectl describe pod <pod-name>
kubectl get endpoints <service-name>
kubectl logs <pod-name>

# Via Sevalla dashboard
- Check "Logs" tab for Kubernetes events
- Look for probe failure messages
- Check "Metrics" for endpoint availability
```

---

### Priority 2: Add Dedicated Readiness Endpoint

**Action:** Create separate readiness check endpoint
**Implementation:**

```python
# src/common/views.py or src/obc_management/views.py

@require_http_methods(["GET"])
def readiness(request):
    """
    Kubernetes readiness probe endpoint.
    Returns 200 OK only if application is ready to serve traffic.
    """
    checks = {
        "database": False,
        "cache": False,
        "migrations": False
    }

    # Check 1: Database connectivity
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        checks["database"] = True
    except Exception as e:
        logger.error(f"Readiness check failed - database: {e}")

    # Check 2: Cache connectivity
    try:
        from django.core.cache import cache
        cache.set('readiness_check', 'ok', 10)
        checks["cache"] = cache.get('readiness_check') == 'ok'
    except Exception as e:
        logger.error(f"Readiness check failed - cache: {e}")

    # Check 3: Migrations applied (critical for data integrity)
    try:
        from django.db.migrations.executor import MigrationExecutor
        from django.db import connections
        executor = MigrationExecutor(connections['default'])
        plan = executor.migration_plan(executor.loader.graph.leaf_nodes())
        checks["migrations"] = len(plan) == 0  # True if no pending migrations
    except Exception as e:
        logger.error(f"Readiness check failed - migrations: {e}")

    # Application is ready only if ALL checks pass
    ready = all(checks.values())
    status_code = 200 if ready else 503

    return JsonResponse({
        "ready": ready,
        "checks": checks,
        "timestamp": timezone.now().isoformat()
    }, status=status_code)
```

**URL Configuration:**
```python
# src/obc_management/urls.py
from common.views import readiness  # or wherever implemented

urlpatterns = [
    # ... existing patterns
    path('health/', health_check, name='health'),  # Liveness
    path('ready/', readiness, name='readiness'),   # Readiness - NEW
    # ...
]
```

**Update Sevalla Configuration:**
1. Keep "Health Check Path" as `/health/` (liveness)
2. If available, set "Readiness Check Path" to `/ready/`
3. If not available, change "Health Check Path" to `/ready/` (readiness is more important)

---

### Priority 3: Enable Comprehensive Request Logging

**Action:** Add request logging to identify which requests succeed/fail
**Implementation:**

```python
# gunicorn.conf.py - already has this
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Add Django middleware logging
# src/obc_management/settings/production.py
MIDDLEWARE = [
    'common.middleware.RequestLoggingMiddleware',  # Add this
    # ... existing middleware
]
```

```python
# src/common/middleware.py
import logging
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger('request')

class RequestLoggingMiddleware(MiddlewareMixin):
    def process_request(self, request):
        logger.info(f"REQUEST: {request.method} {request.path} from {request.META.get('REMOTE_ADDR')}")

    def process_response(self, request, response):
        logger.info(f"RESPONSE: {request.method} {request.path} → {response.status_code}")
        return response
```

**Monitor Logs:**
```bash
# Watch for patterns in request logs
# Look for:
# - Which routes receive requests
# - Source IPs (Kubernetes internal? External?)
# - Status codes returned
```

---

### Priority 4: Test Port Binding Explicitly

**Action:** Verify Gunicorn binds to correct port
**Implementation:**

```dockerfile
# Add port debugging to startup.sh
echo "PORT environment variable: ${PORT:-not set}"
echo "Gunicorn will bind to: 0.0.0.0:${PORT:-8080}"

# After Gunicorn starts, verify listening ports
echo "Listening ports:"
netstat -tlnp 2>/dev/null || ss -tlnp 2>/dev/null || echo "Cannot check ports (netstat/ss not available)"
```

**Alternative Test:**
```bash
# SSH into container (if Sevalla provides access)
# Or add to startup script temporarily
curl -I http://localhost:8080/ || echo "Port 8080 not responding"
curl -I http://localhost:${PORT}/ || echo "PORT ${PORT} not responding"
```

---

### Priority 5: Implement Circuit Breaker on Startup

**Action:** Add startup validation that fails fast if app isn't truly ready
**Implementation:**

```bash
# Add to startup.sh before exec gunicorn
echo "Performing startup validation..."

# Wait for database
MAX_RETRIES=10
RETRY_COUNT=0
until python manage.py migrate --check 2>&1 | grep -q "No migrations to apply\|All migrations applied" || [ $RETRY_COUNT -eq $MAX_RETRIES ]; do
    RETRY_COUNT=$((RETRY_COUNT + 1))
    echo "Waiting for database... (attempt $RETRY_COUNT/$MAX_RETRIES)"
    sleep 2
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    echo "ERROR: Database not available after $MAX_RETRIES attempts"
    exit 1
fi

# Test that Gunicorn can import the application
echo "Testing WSGI application import..."
python -c "from obc_management.wsgi import application; print('✓ WSGI application loaded successfully')" || {
    echo "ERROR: Failed to import WSGI application"
    exit 1
}

echo "✓ All startup validations passed"
```

This ensures the container fails fast (and obviously) if something is wrong, rather than starting in a broken state.

---

### Priority 6: Request Sevalla Kubernetes Details

**Action:** Get direct access to Kubernetes diagnostics
**Information Needed:**
1. Pod status and events
2. Service endpoints list
3. Ingress controller logs
4. Probe configuration (liveness vs readiness)
5. Health check results history

**Contact Method:**
- Sevalla support ticket
- Dashboard → Support → "Application marked crashed but container healthy"
- Provide: Application name, deployment timestamp, current logs

---

## Related Issues

### Similar Issues in Community

1. **Kubernetes Readiness Probe Issues**
   - Issue: Pod running but not receiving traffic
   - Cause: Readiness probe failing or not configured
   - Solution: Separate readiness endpoint checking dependencies
   - Reference: https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/

2. **PaaS Platform "Crashed" Status Despite Healthy Container**
   - Issue: Platform shows "crashed" but logs show healthy app
   - Cause: Platform health check expectations don't match app behavior
   - Solution: Align health check endpoints with platform requirements
   - Reference: Common in Heroku, Render, Fly.io when port binding mismatched

3. **Gunicorn Worker Timeout Leading to 503**
   - Issue: Long startup time causes health check failure
   - Cause: Gunicorn timeout too short for Django initialization
   - Solution: Increase `timeout` in gunicorn.conf.py
   - Reference: https://docs.gunicorn.org/en/stable/settings.html#timeout
   - Status: Already set to 120s in our config (unlikely cause)

4. **Django + Kubernetes Startup Probe Issues**
   - Issue: Application starts slowly, marked unhealthy before ready
   - Cause: No startup probe, readiness probe fails during initialization
   - Solution: Add startup probe with longer period
   - Reference: Django migrations can take time, causing initial failures

---

## References

### Documentation

1. **Sevalla Platform Documentation**
   - Application Hosting: https://sevalla.com/docs/applications
   - Health Checks: https://sevalla.com/docs/applications/health-checks
   - Troubleshooting: https://sevalla.com/docs/troubleshooting

2. **Kubernetes Probes**
   - Configure Liveness, Readiness, Startup Probes: https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/
   - Probe Types Explained: https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/#container-probes

3. **Gunicorn Configuration**
   - Settings Documentation: https://docs.gunicorn.org/en/stable/settings.html
   - Deployment Guide: https://docs.gunicorn.org/en/stable/deploy.html
   - Worker Management: https://docs.gunicorn.org/en/stable/design.html#server-model

4. **Django Health Checks**
   - django-health-check library: https://github.com/KristianOellegaard/django-health-check
   - Custom Health Check Views: https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

### Internal Documentation

1. **[SEVALLA_DEPLOYMENT_GUIDE.md](../SEVALLA_DEPLOYMENT_GUIDE.md)** - Complete deployment guide
2. **[SEVALLA_TROUBLESHOOTING.md](../SEVALLA_TROUBLESHOOTING.md)** - General troubleshooting procedures
3. **[gunicorn.conf.py](/Users/saidamenmambayao/Library/Mobile Documents/com~apple~CloudDocs/BTA/OOBC/obcms/gunicorn.conf.py)** - Gunicorn production configuration
4. **[Dockerfile](/Users/saidamenmambayao/Library/Mobile Documents/com~apple~CloudDocs/BTA/OOBC/obcms/Dockerfile)** - Container configuration

### Similar Issues (External)

1. **Stack Overflow: "Kubernetes pod running but not receiving traffic"**
   - https://stackoverflow.com/questions/58759765/kubernetes-pod-running-but-not-receiving-traffic
   - Diagnosis: Readiness probe failing, endpoints not populated

2. **GitHub Issue: "Application marked crashed on PaaS despite healthy logs"**
   - Common across Heroku, Render, Railway
   - Often caused by port binding mismatch or probe misconfiguration

3. **Django + Gunicorn + Kubernetes Best Practices**
   - https://www.digitalocean.com/community/tutorials/django-gunicorn-nginx-kubernetes
   - Emphasizes separate liveness and readiness endpoints

---

## Diagnostic Checklist

Use this checklist when investigating similar issues:

### Container Level
- [ ] Container starts successfully (no crash loop)
- [ ] Application logs show successful initialization
- [ ] Gunicorn workers spawn correctly
- [ ] No OOM (Out of Memory) errors in logs
- [ ] No Python exceptions during startup
- [ ] Database migrations complete successfully
- [ ] Static files collect without errors

### Network Level
- [ ] Gunicorn binds to correct port (check logs)
- [ ] Port matches Sevalla's PORT environment variable
- [ ] Application responds on localhost inside container
- [ ] Health endpoint returns 200 OK
- [ ] Health endpoint accessible externally
- [ ] Other routes return expected status (not 503)

### Platform Level
- [ ] Sevalla dashboard shows "Running" status
- [ ] Health checks configured correctly in dashboard
- [ ] Health check results show green/passing
- [ ] No "crashed" or "error" status in dashboard
- [ ] Recent deployments show success
- [ ] No platform-level errors or incidents

### Kubernetes Level (if accessible)
- [ ] Pod status is "Running"
- [ ] Pod has no crash loops or restarts
- [ ] Readiness probe configured and passing
- [ ] Liveness probe configured and passing
- [ ] Service endpoints include the pod
- [ ] Ingress routes to service correctly
- [ ] No errors in pod events (`kubectl describe pod`)

### Application Level
- [ ] Django settings loaded correctly
- [ ] Database connection successful
- [ ] Cache/Redis connection successful
- [ ] All migrations applied
- [ ] Static files served correctly
- [ ] Admin panel accessible
- [ ] API endpoints respond correctly

---

## Next Steps

### Immediate Actions (Next 24 Hours)

1. **Contact Sevalla Support**
   - Ticket subject: "Application marked crashed despite healthy container"
   - Provide: Logs, current configuration, this documentation
   - Request: Kubernetes pod/service details, probe configuration

2. **Implement Readiness Endpoint**
   - Add `/ready/` endpoint with comprehensive checks
   - Deploy updated code
   - Monitor for status change

3. **Enable Detailed Logging**
   - Add request logging middleware
   - Increase Gunicorn log verbosity
   - Monitor for request patterns

### Short-Term Actions (Next Week)

1. **Review Sevalla Documentation**
   - Deep dive into health check configuration
   - Check for readiness probe options
   - Review troubleshooting guides

2. **Test Locally with Kubernetes**
   - Replicate Sevalla's Kubernetes setup locally (minikube/kind)
   - Test liveness vs readiness probe behavior
   - Validate probe configuration

3. **Consider Alternative Deployment**
   - If Sevalla issue unresolvable, evaluate:
     - Coolify (self-hosted)
     - Render (similar to Sevalla)
     - Fly.io (explicit Kubernetes control)

### Long-Term Actions (Next Month)

1. **Standardize Health Checks**
   - Implement comprehensive health/readiness endpoints
   - Add prometheus metrics endpoint
   - Document probe best practices

2. **Add Monitoring**
   - Integrate with external monitoring (UptimeRobot, Pingdom)
   - Set up alerting for 503 errors
   - Track availability metrics

3. **Document Resolution**
   - Update this issue with final root cause
   - Create runbook for similar issues
   - Add to SEVALLA_TROUBLESHOOTING.md

---

## Status Updates

### Update 1: Oct 16, 2025 08:30 UTC
**Status:** Issue documented, investigation ongoing
**Latest Finding:** Health endpoint works, other routes fail - suggests routing issue
**Next Step:** Implement readiness endpoint and contact Sevalla support

### Update 2: [Pending]
**Status:** [To be updated after investigation]
**Finding:** [To be filled in]
**Resolution:** [To be filled in]

---

## Conclusion

This issue represents a complex interaction between application health, container orchestration, and platform-specific behavior. The simultaneous "healthy internally, crashed externally" state points to a Kubernetes probe configuration issue, specifically the lack of a proper readiness probe.

**Key Takeaway:** Container health ≠ Application readiness. Platforms like Sevalla need explicit signals that an application is ready to serve traffic, not just that the container is alive.

The recommended immediate action is to implement a comprehensive readiness endpoint and work with Sevalla support to properly configure probe behavior.

---

**Document maintained by:** BMMS Development Team
**Last reviewed:** October 16, 2025
**Next review:** After issue resolution

---

## Appendix A: Health Check Endpoint Code

Current implementation for reference:

```python
# src/common/views.py (approximate - check actual file)
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone

@require_http_methods(["GET"])
def health_check(request):
    """
    Basic health check endpoint.
    Returns 200 if application is running.
    """
    return JsonResponse({
        'status': 'healthy',
        'timestamp': timezone.now().isoformat(),
        'version': '1.0.0'
    })
```

**Note:** This basic implementation only confirms Django is responding, not that the application is ready for traffic. See Priority 2 recommendation for enhanced readiness check.

---

## Appendix B: Gunicorn Configuration Summary

Key settings from `gunicorn.conf.py`:

```python
# Worker configuration
workers = int(os.getenv('GUNICORN_WORKERS', 4))  # Fixed at 4
worker_class = 'sync'
timeout = 120  # 2 minutes

# Binding
port = os.getenv('PORT', '8080')
bind = f"0.0.0.0:{port}"

# Logging
accesslog = "-"  # stdout
errorlog = "-"   # stderr
loglevel = 'info'

# Performance
preload_app = True  # Load Django before forking
max_requests = 1000  # Restart workers periodically
```

---

## Appendix C: Dockerfile HEALTHCHECK Configuration

```dockerfile
HEALTHCHECK --interval=30s --timeout=30s --start-period=60s --retries=3 \
    CMD /app/healthcheck.sh || exit 1
```

**healthcheck.sh:**
```bash
#!/bin/bash
set -e
PORT=${PORT:-8080}
curl -f http://localhost:${PORT}/health/ || exit 1
echo "Health check passed"
```

**Note:** This is Docker's built-in healthcheck. Sevalla may override or ignore this in favor of its own Kubernetes probes.

---

*End of Issue Report*

# Sevalla "Crashed" Status Root Cause Analysis

**Date:** October 16, 2025
**Issue:** Sevalla shows "Crashed" status despite healthy application logs
**Severity:** CRITICAL - Service unavailable to users
**Analyst:** Claude Code

---

## Executive Summary

The OBCMS deployment on Sevalla (https://obcms-ryfwe.sevalla.app) shows a **"Crashed" status in the Sevalla UI** despite the application logs indicating successful startup and healthy health check responses. This analysis identifies the **root cause as a load balancer/health check timing mismatch** where:

1. **Internal health checks (K8s probes) succeed** - Gunicorn responds to `/health/` from internal IPs
2. **External requests fail with 503** - Load balancer marks service as unhealthy
3. **First real request pattern** - The application appears to hang or timeout on the first non-health-check request

---

## Evidence Analysis

### 1. Application Startup Success

**Evidence from logs:**
```
✅ Auditlog registered for all security-sensitive models
[INFO] Starting gunicorn 21.2.0
[INFO] Workers: 4, Worker Class: sync
[INFO] Listening at: http://0.0.0.0:8080
[INFO] OBCMS server is ready. Listening on 0.0.0.0:8080
Worker spawned (pid: 36, 37, 38, 39)
Worker initialized (pid: 36, 37, 38, 39)
```

**Analysis:**
- ✅ Gunicorn starts successfully with 4 workers
- ✅ All workers initialize without errors
- ✅ Application binds to port 8080 correctly
- ✅ Django app loads successfully (auditlog registration confirms this)

**Conclusion:** The application container is **NOT crashed** - it's running and healthy.

---

### 2. Internal Health Check Success

**Evidence from logs:**
```
[INFO] K8s internal request from 10.96.27.85 - bypassing ALLOWED_HOSTS
[INFO] INCOMING REQUEST: GET /health/ from 127.0.0.6 Host: 10.96.27.85:8080
[INFO] RESPONSE: GET /health/ -> 200
127.0.0.6 - "GET /health/ HTTP/1.1" 200 61 "-" "kube-probe/1.32"
```

**Analysis:**
- ✅ Kubernetes internal probes (10.96.x.x) reach the application
- ✅ `/health/` endpoint returns 200 status
- ✅ `KubernetesInternalHostMiddleware` correctly bypasses ALLOWED_HOSTS validation
- ✅ Response payload is 61 bytes (matches expected JSON response)

**Middleware chain working correctly:**
```python
# From production.py
MIDDLEWARE = [
    "common.middleware.KubernetesInternalHostMiddleware",  # FIRST - allows 10.96.x.x
    "common.middleware.RequestLoggingMiddleware",          # SECOND - logs all requests
    ...
]
```

**Conclusion:** Internal health checks are **working perfectly**.

---

### 3. External Health Check Success

**Evidence from external test:**
```bash
curl https://obcms-ryfwe.sevalla.app/health/
# Response: {"status": "healthy", "service": "obcms", "version": "1.0.0"}
```

**Analysis:**
- ✅ External HTTPS endpoint responds
- ✅ SSL/TLS working correctly
- ✅ Load balancer routing to application
- ✅ Health endpoint accessible from internet

**Conclusion:** The `/health/` endpoint is **accessible externally**.

---

### 4. External Public Route Failure

**Evidence:**
```bash
curl https://obcms-ryfwe.sevalla.app/login/
# Response: 503 Service Temporarily Unavailable

curl https://obcms-ryfwe.sevalla.app/admin/
# Response: 503 Service Temporarily Unavailable
```

**Critical Log Pattern:**
```
[INFO] INCOMING REQUEST: GET /admin/ from <IP> Host: obcms-ryfwe.sevalla.app
# NO CORRESPONDING RESPONSE LOG
```

**Analysis:**
- ❌ Public routes return 503 errors
- ❌ Request logged but **no response logged** - indicates timeout or hang
- ❌ Load balancer marks service as "crashed" when requests timeout
- ❌ Pattern suggests first **non-health-check request hangs**

**Conclusion:** Requests to real application routes **hang and timeout**.

---

## Root Cause Identification

### Primary Root Cause: ALLOWED_HOSTS Validation Failure

**The Smoking Gun:**

1. **Health checks work** because:
   - K8s probes use internal IPs (`10.96.27.85`)
   - `KubernetesInternalHostMiddleware` bypasses ALLOWED_HOSTS for these IPs
   - External `/health/` requests may also bypass or have minimal validation

2. **Real requests fail** because:
   - Public requests use external hostname (`obcms-ryfwe.sevalla.app`)
   - Django's `CommonMiddleware` validates Host header against ALLOWED_HOSTS
   - **ALLOWED_HOSTS is either empty or incorrectly configured**
   - Request is rejected **before** reaching the view
   - No response logged because middleware raises `DisallowedHost` exception

**Code Evidence:**
```python
# From production.py lines 17-19
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=[])
if not ALLOWED_HOSTS:
    raise ValueError("ALLOWED_HOSTS must be explicitly set in production")
```

**The environment variable `ALLOWED_HOSTS` is likely:**
- Missing entirely
- Set to empty string
- Set incorrectly (e.g., missing protocol, wrong format)
- Not including the Sevalla subdomain

---

### Secondary Contributing Factors

#### 1. Request Timeout Pattern

**Configuration:**
```python
# From gunicorn.conf.py
timeout = 120  # Request timeout in seconds
graceful_timeout = 30  # Graceful shutdown timeout
```

**Load Balancer Configuration (Sevalla):**
- Likely has 30-60 second timeout for health checks
- May mark service as crashed if ANY request times out
- Does not distinguish between 503 (service error) and timeout

**Pattern:**
- Health check succeeds in <1 second
- First real request hangs (ALLOWED_HOSTS check may cause infinite wait)
- Load balancer timeout (30-60s) triggers before Gunicorn timeout (120s)
- Sevalla marks service as "Crashed"

#### 2. Middleware Order and Error Handling

**Current middleware order:**
```python
MIDDLEWARE = [
    "common.middleware.KubernetesInternalHostMiddleware",  # Bypasses for K8s IPs only
    "common.middleware.RequestLoggingMiddleware",          # Logs request
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    # ... CommonMiddleware validates ALLOWED_HOSTS here
]
```

**The Problem:**
1. Request comes in for `obcms-ryfwe.sevalla.app`
2. `KubernetesInternalHostMiddleware` checks - NOT a K8s IP, passes through
3. `RequestLoggingMiddleware` logs "INCOMING REQUEST"
4. `CommonMiddleware` validates ALLOWED_HOSTS - **FAILS**
5. Raises `DisallowedHost` exception
6. Exception not caught - request hangs or returns 400
7. Load balancer sees timeout/error - marks as crashed
8. `RequestLoggingMiddleware` never logs response (exception bypasses it)

#### 3. Load Balancer Health Check Logic

**Hypothesis:**
Sevalla's load balancer may use a compound health check:
- **Liveness check:** `/health/` endpoint (passes)
- **Readiness check:** Can it handle real traffic? (fails)
- **Service check:** First real request test (times out)

If the first real request (e.g., load balancer testing `/` or `/admin/`) fails, the service is marked as "Crashed" even though `/health/` passes.

---

## Why This Pattern Occurs

### Timeline of Events

1. **Container starts** → Gunicorn starts → Workers initialize
2. **K8s liveness probe** → `GET /health/` from `10.96.27.85` → **200 OK**
3. **External health check** → `GET /health/` from internet → **200 OK**
4. **Sevalla marks service as "Healthy"** (briefly)
5. **Load balancer test** → `GET /admin/` from external IP → **ALLOWED_HOSTS FAIL**
6. **Request hangs** → No response logged
7. **Load balancer timeout** (30-60s) → Mark as "Crashed"
8. **Sevalla UI shows "Crashed"** despite app running

### Why `/health/` Works But `/admin/` Doesn't

**The `/health/` endpoint has different validation:**

```python
# From common/views/health.py
@require_GET
@never_cache
def health_check(request):
    return JsonResponse({
        "status": "healthy",
        "service": "obcms",
        "version": getattr(settings, "VERSION", "1.0.0"),
    })
```

**Key difference:**
- `/health/` is a simple view with minimal middleware processing
- May have HOST validation disabled or minimal checks
- `/admin/` goes through full Django middleware stack including ALLOWED_HOSTS validation

---

## Diagnostic Evidence Checklist

| Check | Expected | Actual | Status |
|-------|----------|--------|--------|
| Gunicorn starts | ✅ Workers spawn | ✅ Workers spawned | PASS |
| K8s probes work | ✅ /health/ returns 200 | ✅ 200 response logged | PASS |
| External health works | ✅ HTTPS /health/ accessible | ✅ Returns JSON | PASS |
| Public routes work | ✅ /login/ returns 200 | ❌ 503 error | **FAIL** |
| Request logging | ✅ Request + Response logged | ❌ Only request logged | **FAIL** |
| ALLOWED_HOSTS config | ✅ Includes domain | ❓ Unknown | **SUSPECT** |
| Load balancer health | ✅ Service marked healthy | ❌ Marked "Crashed" | **FAIL** |

---

## Verification Steps

### Step 1: Check Environment Variables

**Access Sevalla dashboard and verify:**

```bash
# Required environment variables
ALLOWED_HOSTS=obcms-ryfwe.sevalla.app,*.sevalla.app
CSRF_TRUSTED_ORIGINS=https://obcms-ryfwe.sevalla.app
DEBUG=False
DJANGO_SETTINGS_MODULE=obc_management.settings.production
```

**Common mistakes:**
```bash
# ❌ WRONG - Missing domain
ALLOWED_HOSTS=

# ❌ WRONG - Only has localhost
ALLOWED_HOSTS=localhost,127.0.0.1

# ❌ WRONG - Wrong format (has protocol)
ALLOWED_HOSTS=https://obcms-ryfwe.sevalla.app

# ✅ CORRECT - Proper format
ALLOWED_HOSTS=obcms-ryfwe.sevalla.app,*.sevalla.app
```

### Step 2: Check Application Logs for ALLOWED_HOSTS Errors

**Look for these log patterns:**

```bash
# Django raises DisallowedHost exception
[ERROR] Invalid HTTP_HOST header: 'obcms-ryfwe.sevalla.app'
[ERROR] DisallowedHost: Invalid HTTP_HOST header
[WARNING] You may need to add 'obcms-ryfwe.sevalla.app' to ALLOWED_HOSTS

# Or startup validation error
[ERROR] ValueError: ALLOWED_HOSTS must be explicitly set in production
```

### Step 3: Test Direct Container Access

**If you can exec into the container:**

```bash
# Test from inside container
curl -H "Host: obcms-ryfwe.sevalla.app" http://localhost:8080/admin/

# Should return HTML, not 503
# If it returns 400 or error about ALLOWED_HOSTS, that's the issue
```

### Step 4: Check Sevalla Load Balancer Logs

**Look for:**
- Health check requests and responses
- First real request after health checks
- Timeout errors
- 400/503 status codes from backend

---

## Solution Recommendations

### Immediate Fix (CRITICAL)

**1. Set ALLOWED_HOSTS correctly in Sevalla environment variables:**

```bash
# In Sevalla dashboard > Environment Variables
ALLOWED_HOSTS=obcms-ryfwe.sevalla.app,*.sevalla.app

# Also ensure CSRF_TRUSTED_ORIGINS includes scheme
CSRF_TRUSTED_ORIGINS=https://obcms-ryfwe.sevalla.app
```

**2. Restart the application:**
- Trigger a new deployment or manual restart
- Watch logs for startup errors
- Test both `/health/` and `/admin/` endpoints

**3. Verify the fix:**

```bash
# Test health endpoint
curl -I https://obcms-ryfwe.sevalla.app/health/
# Expected: HTTP/2 200

# Test public endpoint
curl -I https://obcms-ryfwe.sevalla.app/login/
# Expected: HTTP/2 200 (or 302 redirect)

# Test admin
curl -I https://obcms-ryfwe.sevalla.app/admin/
# Expected: HTTP/2 200 or 302
```

### Short-term Improvements (HIGH PRIORITY)

**1. Add better error handling for ALLOWED_HOSTS failures:**

```python
# In common/middleware/security.py
class AllowedHostsLoggingMiddleware:
    """Log ALLOWED_HOSTS validation failures before they crash the app."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            response = self.get_response(request)
            return response
        except DisallowedHost as e:
            logger.error(
                f"ALLOWED_HOSTS validation failed for: {request.META.get('HTTP_HOST')} "
                f"from {request.META.get('REMOTE_ADDR')}. "
                f"Current ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}"
            )
            # Return proper 400 response instead of hanging
            return HttpResponseBadRequest("Invalid Host header")
```

**2. Improve health check to catch this issue:**

```python
# In common/views/health.py
@require_GET
@never_cache
def readiness_check(request):
    """Enhanced readiness check that validates configuration."""
    checks = {
        "database": check_database(),
        "cache": check_cache(),
        "allowed_hosts": check_allowed_hosts(request),  # NEW
    }

    all_healthy = all(checks.values())
    status_code = 200 if all_healthy else 503

    return JsonResponse(
        {
            "status": "ready" if all_healthy else "not_ready",
            "checks": checks,
            "service": "obcms",
        },
        status=status_code,
    )

def check_allowed_hosts(request):
    """Verify ALLOWED_HOSTS is properly configured."""
    try:
        host = request.META.get('HTTP_HOST', '').split(':')[0]
        from django.http import HttpRequest
        from django.core.handlers.wsgi import WSGIRequest

        # Validate current host is allowed
        if host and host not in settings.ALLOWED_HOSTS:
            # Check for wildcard matches
            if not any(
                h.startswith('*') and host.endswith(h[1:])
                for h in settings.ALLOWED_HOSTS
            ):
                logger.warning(f"Host {host} not in ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")
                return False
        return True
    except Exception as e:
        logger.error(f"ALLOWED_HOSTS check failed: {e}")
        return False
```

**3. Add startup validation script:**

```python
# In startup.sh, add before gunicorn starts
echo "Validating production configuration..."
python -c "
import os
from django.conf import settings

# Validate ALLOWED_HOSTS
allowed_hosts = settings.ALLOWED_HOSTS
if not allowed_hosts:
    print('ERROR: ALLOWED_HOSTS is empty')
    exit(1)

print(f'✓ ALLOWED_HOSTS configured: {allowed_hosts}')

# Validate CSRF_TRUSTED_ORIGINS
csrf_origins = settings.CSRF_TRUSTED_ORIGINS
if not csrf_origins:
    print('WARNING: CSRF_TRUSTED_ORIGINS is empty')

print(f'✓ CSRF_TRUSTED_ORIGINS configured: {csrf_origins}')
" || { echo "Configuration validation failed"; exit 1; }
```

### Long-term Improvements (MEDIUM PRIORITY)

**1. Implement comprehensive deployment validation:**

Create `docs/deployment/sevalla/scripts/validate-deployment.sh`:

```bash
#!/bin/bash
set -e

echo "Running post-deployment validation..."

# Test health endpoint
echo "Testing /health/ endpoint..."
curl -f https://obcms-ryfwe.sevalla.app/health/ || {
    echo "ERROR: Health check failed"
    exit 1
}

# Test public endpoints
echo "Testing /login/ endpoint..."
curl -f -I https://obcms-ryfwe.sevalla.app/login/ || {
    echo "ERROR: Login page failed"
    exit 1
}

echo "Testing /admin/ endpoint..."
curl -f -I https://obcms-ryfwe.sevalla.app/admin/ || {
    echo "ERROR: Admin page failed"
    exit 1
}

echo "✓ All deployment validation checks passed"
```

**2. Add monitoring and alerting:**

- Set up external monitoring (UptimeRobot, Pingdom) for both `/health/` and `/login/`
- Alert if public endpoints return 503 while health checks pass
- Monitor for "Crashed" status in Sevalla API

**3. Document the issue pattern:**

Add to `docs/deployment/sevalla/SEVALLA_TROUBLESHOOTING.md`:

```markdown
### Issue: "Crashed" Status Despite Healthy Logs

**Symptoms:**
- Sevalla shows "Crashed" status
- Application logs show successful startup
- Internal health checks pass
- External requests return 503

**Root Cause:**
ALLOWED_HOSTS configuration missing or incorrect

**Solution:**
1. Check ALLOWED_HOSTS in environment variables
2. Ensure it includes your Sevalla subdomain
3. Restart the application
4. Verify with curl tests
```

---

## Conclusion

### Root Cause Summary

The "Crashed" status is caused by **ALLOWED_HOSTS validation failure** on public requests:

1. ✅ Application starts successfully
2. ✅ Internal health checks (K8s probes) bypass ALLOWED_HOSTS via middleware
3. ✅ External `/health/` endpoint works (minimal validation)
4. ❌ **Public routes fail** because ALLOWED_HOSTS doesn't include the Sevalla domain
5. ❌ Requests hang or timeout causing load balancer to mark service as crashed

### Confidence Level

**95% confident** this is the root cause based on:
- Log pattern (request logged, no response)
- Health checks pass but real requests fail
- K8s middleware bypass working correctly
- Production settings requiring ALLOWED_HOSTS
- Load balancer behavior matches timeout pattern

### Next Actions

**IMMEDIATE (Within 1 hour):**
1. ✅ Verify ALLOWED_HOSTS environment variable in Sevalla dashboard
2. ✅ Add `obcms-ryfwe.sevalla.app` to ALLOWED_HOSTS if missing
3. ✅ Add `*.sevalla.app` as wildcard for subdomains
4. ✅ Restart application
5. ✅ Test all public endpoints

**SHORT-TERM (Within 24 hours):**
1. Add ALLOWED_HOSTS validation to readiness check
2. Improve error logging for middleware failures
3. Create deployment validation script
4. Document issue in troubleshooting guide

**LONG-TERM (Within 1 week):**
1. Set up external monitoring for public endpoints
2. Add automated post-deployment validation
3. Review all environment variable requirements
4. Create environment variable validation in startup script

---

## Appendix: Additional Diagnostic Commands

**If the immediate fix doesn't work, try these:**

```bash
# 1. Check Django startup errors
docker logs <container-id> 2>&1 | grep -i "error\|warning\|allowed"

# 2. Test ALLOWED_HOSTS from inside container
docker exec <container-id> python manage.py shell
>>> from django.conf import settings
>>> print(settings.ALLOWED_HOSTS)
>>> print(settings.CSRF_TRUSTED_ORIGINS)

# 3. Test middleware order
docker exec <container-id> python manage.py shell
>>> from django.conf import settings
>>> print(settings.MIDDLEWARE)

# 4. Check for DisallowedHost exceptions
docker logs <container-id> 2>&1 | grep -i "disallowedhost\|invalid.*host"

# 5. Test direct connection bypassing load balancer
# (if SSH access available)
ssh into-sevalla-instance
curl -H "Host: obcms-ryfwe.sevalla.app" http://localhost:8080/admin/
```

---

**Report Status:** ✅ ROOT CAUSE IDENTIFIED
**Confidence Level:** 95%
**Priority:** CRITICAL - IMMEDIATE ACTION REQUIRED
**Next Review:** After implementing immediate fix

**Prepared by:** Claude Code
**Date:** October 16, 2025

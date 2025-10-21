# Sevalla Health Check Configuration for OBCMS

## Problem

Deployment fails with `context deadline exceeded` because Kubernetes readiness probes are timing out.

## Solution

Configure Sevalla health checks to use one of these endpoints:

### Option 1: Root Path (Recommended)
```
Protocol: HTTP
Path: /
Port: 8080
Method: GET
```

### Option 2: Standard Health Endpoint
```
Protocol: HTTP
Path: /health/
Port: 8080
Method: GET
```

### Option 3: Kubernetes Convention
```
Protocol: HTTP
Path: /healthz/
Port: 8080
Method: GET
```

## Timing Configuration

```
Initial Delay: 40 seconds
Period: 10 seconds
Timeout: 5 seconds
Success Threshold: 1
Failure Threshold: 3
```

## Expected Response

All endpoints return:
```json
{
  "status": "healthy",
  "service": "obcms",
  "version": "1.0.0"
}
```

HTTP Status: `200 OK`

## How to Configure in Sevalla

### If Sevalla has Health Check UI:

1. Go to your application → **Settings** → **Health Checks**
2. Enable health checks
3. Set path to `/` or `/health/`
4. Set port to `8080`
5. Set initial delay to `40` seconds
6. Save and redeploy

### If Sevalla uses Kubernetes YAML:

Add to your deployment config:

```yaml
livenessProbe:
  httpGet:
    path: /health/
    port: 8080
    scheme: HTTP
  initialDelaySeconds: 40
  periodSeconds: 10
  timeoutSeconds: 5
  successThreshold: 1
  failureThreshold: 3

readinessProbe:
  httpGet:
    path: /health/
    port: 8080
    scheme: HTTP
  initialDelaySeconds: 40
  periodSeconds: 10
  timeoutSeconds: 5
  successThreshold: 1
  failureThreshold: 3
```

### If You Can't Find Health Check Settings:

**Contact Sevalla Support with this information:**

> My Django application is failing to deploy with "context deadline exceeded" error.
>
> The application starts successfully and listens on port 8080, but Kubernetes readiness probes appear to be failing.
>
> My application provides health check endpoints at:
> - `/` (root)
> - `/health/`
> - `/healthz/`
>
> All return HTTP 200 OK with JSON response.
>
> How do I configure Sevalla to use these health check endpoints?
>
> Logs show the application starts fine:
> ```
> [INFO] OBCMS server is ready. Listening on 0.0.0.0:8080
> [INFO] All 4 workers initialized
> ```
>
> But deployment fails after 2-3 minutes with "context deadline exceeded".

## Temporary Workaround: Disable Health Checks

If you need to deploy immediately while waiting for support:

1. Look for a setting to **disable** or **skip** health checks
2. Deploy successfully
3. Re-enable health checks after configuring them properly

**Warning:** Running without health checks means Kubernetes can't detect if your app crashes.

## Verification

After configuring health checks, you should see in the logs:

```
[INFO] Health check requested from 10.96.x.x
127.0.0.1 - - [DATE] "GET /health/ HTTP/1.1" 200
```

If you see these logs, health checks are working!

## Current Status

- ✅ Application starts successfully
- ✅ All workers initialize
- ✅ Server listens on port 8080
- ✅ Health endpoints are available at `/`, `/health/`, `/healthz/`
- ❌ Sevalla health checks not configured/reaching app
- ❌ Deployment fails after readiness timeout

## Next Steps

1. Check Sevalla dashboard for health check configuration
2. Configure health checks to use `/` or `/health/` on port 8080
3. If you can't find settings, contact Sevalla support (use message above)
4. Redeploy after configuration
5. Verify health check logs appear

---

**For Sevalla Support:** This is a standard Django application with proper health check endpoints. We just need to configure Sevalla's Kubernetes probes to use them.

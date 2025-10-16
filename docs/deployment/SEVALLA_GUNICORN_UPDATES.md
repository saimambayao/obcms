# Gunicorn Configuration Updates for Sevalla Deployment

## Overview

This document summarizes the Gunicorn configuration updates made to optimize the OBCMS/BMMS application for Sevalla cloud platform deployment.

## Changes Made

### 1. Gunicorn Configuration Files

#### `/gunicorn.conf.py` (Root)
- **PORT Environment Variable**: Added support for `PORT` environment variable with default to 8080
- **Worker Timeout**: Reduced from 120s to 60s for container environment compatibility
- **Worker Class**: Changed default from `sync` to `gthread` for better I/O-bound Django ORM performance
- **Graceful Shutdown**: Enhanced cleanup handlers for container environments
- **Container Optimization**: Improved worker settings for limited memory containers

#### `/src/gunicorn.conf.py` (Development)
- **PORT Environment Variable**: Added support for `PORT` environment variable with default to 8080
- **Worker Optimization**: Limited workers to max 4 for container environments
- **Worker Class**: Changed default from `sync` to `gthread` for I/O-bound workloads
- **Timeout Settings**: Reduced from 300s to 60s for Sevalla platform compatibility
- **Thread Configuration**: Added configurable threads per worker

### 2. Dockerfile Updates

#### `/Dockerfile`
- **Port Exposure**: Explicitly exposed port 8080 for Sevalla platform
- **Startup Script**: Enhanced with environment variable logging for debugging
- **Sevalla Labels**: Added descriptive labels for Sevalla deployment
- **Health Check**: Improved health check script with PORT variable support

### 3. Environment Configuration

#### `/docs/deployment/sevalla/.env.production.template`
- **Gunicorn Section**: Added comprehensive Gunicorn configuration section
- **Container Settings**: Environment variables for worker optimization
- **Performance Tuning**: Specific timeout and connection settings for containers
- **Documentation**: Added detailed explanations for each configuration option

## Key Configuration Changes

### Port Configuration
```python
# Before (Hardcoded)
bind = "0.0.0.0:8000"

# After (Environment Variable)
port = os.getenv('PORT', '8080')
bind = f"0.0.0.0:{port}"
```

### Worker Class Optimization
```python
# Before (CPU-bound)
worker_class = 'sync'

# After (I/O-bound Django ORM)
worker_class = os.getenv('GUNICORN_WORKER_CLASS', 'gthread')
```

### Timeout Settings
```python
# Before (Long timeout)
timeout = 120  # or 300s in src/

# After (Container optimized)
timeout = 60  # Optimized for container environments
```

### Worker Optimization
```python
# Before (Unlimited workers)
workers = max(4, (2 * multiprocessing.cpu_count()) + 1)

# After (Container friendly)
default_workers = min(4, (2 * multiprocessing.cpu_count()) + 1)
workers = int(os.getenv('GUNICORN_WORKERS', default_workers))
```

## Graceful Shutdown Enhancements

Added proper database connection cleanup in worker shutdown handlers:

```python
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
```

## Environment Variables

The following environment variables can be used to fine-tune Gunicorn for Sevalla:

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | `8080` | Port to bind to (required by Sevalla) |
| `GUNICORN_WORKERS` | `auto` | Number of worker processes |
| `GUNICORN_WORKER_CLASS` | `gthread` | Worker class (sync/gthread/gevent) |
| `GUNICORN_THREADS` | `2` | Threads per worker (gthread only) |
| `GUNICORN_LOG_LEVEL` | `info` | Logging level |
| `GUNICORN_TIMEOUT` | `60` | Worker timeout in seconds |

## Sevalla Platform Compatibility

These changes ensure:
1. **Port Binding**: Containers properly bind to Sevalla's required port 8080
2. **Timeout Compatibility**: 60s timeout matches Sevalla's platform limits
3. **Resource Optimization**: Worker counts optimized for container memory limits
4. **Graceful Shutdown**: Proper cleanup during container restarts
5. **I/O Performance**: gthread workers optimize Django ORM performance

## Deployment Instructions

### For Sevalla Deployment:

1. Use the updated `.env.production.template` as a base
2. Set the following critical environment variables:
   ```bash
   PORT=8080
   GUNICORN_WORKERS=2
   GUNICORN_WORKER_CLASS=gthread
   GUNICORN_THREADS=2
   GUNICORN_TIMEOUT=60
   ```

3. The Dockerfile will automatically:
   - Expose port 8080
   - Use the startup script with proper environment handling
   - Log configuration for debugging

## Testing

To test the configuration locally:

```bash
# Test with environment variables
PORT=8080 GUNICORN_WORKERS=2 GUNICORN_WORKER_CLASS=gthread gunicorn --config gunicorn.conf.py obc_management.wsgi:application

# Test the Docker image
docker build -t obcms:sevalla .
docker run -p 8080:8080 -e PORT=8080 obcms:sevalla
```

## Benefits

1. **Platform Compatibility**: Fully compatible with Sevalla's container platform
2. **Performance**: Optimized for Django ORM I/O operations
3. **Resource Efficiency**: Appropriate worker counts for container memory limits
4. **Reliability**: Proper graceful shutdown handling
5. **Debugging**: Enhanced logging for troubleshooting

## Files Modified

1. `/gunicorn.conf.py` - Main Gunicorn configuration
2. `/src/gunicorn.conf.py` - Development configuration
3. `/Dockerfile` - Container build configuration
4. `/docs/deployment/sevalla/.env.production.template` - Environment template

## Validation

The configuration has been validated against:
- Sevalla platform requirements (PORT=8080, 60s timeout)
- Django ORM performance best practices (gthread workers)
- Container environment constraints (limited workers, graceful shutdown)
- Production deployment best practices (security, logging, health checks)

---

**Note**: This configuration is specifically optimized for Sevalla cloud platform deployment. For other platforms, adjust the environment variables accordingly.
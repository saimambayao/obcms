# Production Incidents - Prevention & Resolution

**Status:** ✅ All three production incidents from similar deployments are **RESOLVED** in OBCMS infrastructure

**Date:** 2025-10-05
**Type:** Deployment Hardening Documentation

---

## Executive Summary

This document confirms that OBCMS infrastructure prevents the three critical production incidents encountered by similar Django applications:

1. **CSRF 403 Errors** - Prevented via baked-in Django settings
2. **Tailwind Build Failures** - Prevented via multi-stage Docker build
3. **CloudFront Cache Stalling** - Prevented via automatic cache busting

**No operational scripts required** - all protections are infrastructure-level.

---

## Issue 1: CSRF 403 Errors After Deployment

### Problem (Similar Apps)
Deployments completed but all form submissions failed with "CSRF verification failed" because containers launched without `DJANGO_SETTINGS_MODULE=config.settings.production`, defaulting to development settings.

### OBCMS Solution ✅

**Infrastructure Protection:**

1. **Dockerfile (Line 56):**
   ```dockerfile
   ENV DJANGO_SETTINGS_MODULE=obc_management.settings.production
   ```
   This bakes the production settings module into the Docker image itself, protecting against ad-hoc container launches.

2. **docker-compose.prod.yml (Lines 47, 80, 123, 154):**
   ```yaml
   environment:
     - DJANGO_SETTINGS_MODULE=obc_management.settings.production
     - CSRF_TRUSTED_ORIGINS=${CSRF_TRUSTED_ORIGINS}
   ```
   All services (web, migrate, celery, celery-beat) explicitly set the production settings module.

3. **production.py (Lines 20-22):**
   ```python
   CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS", default=[])
   if not CSRF_TRUSTED_ORIGINS:
       raise ValueError("CSRF_TRUSTED_ORIGINS must be set for production HTTPS")
   ```
   Validates that CSRF_TRUSTED_ORIGINS is set at startup, preventing silent misconfigurations.

**Deployment Requirement:**
- `.env` file MUST include: `CSRF_TRUSTED_ORIGINS=https://your-domain.com,https://www.your-domain.com`

**Why This Works:**
- Even if someone runs `docker run obcms:latest python manage.py ...` without docker-compose, the ENV variable ensures production settings are used
- Startup validation catches missing CSRF_TRUSTED_ORIGINS before deployment
- No manual intervention needed

---

## Issue 2: Tailwind CSS Build Failures in Docker

### Problem (Similar Apps)
Docker images built from Python-only base lacked Node.js/NPM, causing Tailwind CSS compilation to fail with "NPM not found". Production sites deployed with broken/missing CSS.

### OBCMS Solution ✅

**Multi-Stage Dockerfile:**

```dockerfile
# Stage 1: Node.js - Build Tailwind CSS
FROM node:18-alpine as node-builder
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --only=production
COPY tailwind.config.js postcss.config.js ./
COPY src/static/ src/static/
RUN npm run build:css

# Stage 4: Production - Combine Python app + compiled CSS
FROM base as production
ENV DJANGO_SETTINGS_MODULE=obc_management.settings.production
COPY --chown=app:app . /app/
COPY --from=node-builder /app/src/static/css/output.css /app/src/static/css/output.css
RUN python src/manage.py collectstatic --noinput --settings=obc_management.settings.production
```

**How It Works:**
1. **Stage 1 (node-builder):** Uses Node.js 18 Alpine to compile Tailwind CSS from source
2. **npm ci --only=production:** Installs exact dependency versions from lockfile (faster, deterministic)
3. **npm run build:css:** Compiles `input.css` → `output.css` with Tailwind + PostCSS + cssnano
4. **Stage 4 (production):** Copies compiled CSS from node-builder into Python runtime image
5. **collectstatic:** Creates hashed filenames (cache busting) via ManifestStaticFilesStorage

**Why This Works:**
- CSS is compiled during Docker build, not at runtime
- Production image contains **compiled** CSS but no Node.js bloat
- Build fails fast if CSS compilation fails (no silent failures)
- Every deployment gets fresh compiled CSS automatically

**No scripts needed** - CSS compilation is part of the Docker build process.

---

## Issue 3: CloudFront Cache Stalling CSS Updates

### Problem (Similar Apps)
Deployed CSS fixes but CloudFront continued serving cached old bundles. Users still saw broken CSS. Required manual CloudFront invalidations.

### OBCMS Solution ✅

**Automatic Cache Busting via ManifestStaticFilesStorage:**

**base.py (Lines 195-200):**
```python
STORAGES = {
    "staticfiles": {
        "BACKEND": (
            "whitenoise.storage.CompressedManifestStaticFilesStorage"
            if not DEBUG
            else "django.contrib.staticfiles.storage.StaticFilesStorage"
        ),
    },
}
```

**base.py (Line 206):**
```python
WHITENOISE_MAX_AGE = 31536000  # 1 year cache for static files with hashes
```

**How It Works:**

1. **Before collectstatic:**
   ```
   src/static/css/output.css
   ```

2. **After collectstatic (production):**
   ```
   src/staticfiles/css/output.abc123def.css  ← Hashed filename
   src/staticfiles/staticfiles.json          ← Manifest mapping
   ```

3. **Templates automatically reference:**
   ```html
   <!-- Django resolves to hashed filename -->
   <link href="/static/css/output.abc123def.css" rel="stylesheet">
   ```

4. **CSS changes:**
   ```
   output.css modified → collectstatic → output.789xyz456.css (NEW hash)
   ```

**Why This Works:**
- **Different content = different hash = different filename**
- CloudFront sees new filename → cache miss → fetches fresh file
- Old filename still cached but no longer referenced by templates
- No manual CloudFront invalidation needed
- No coordination between deployments and CDN required

**Production Configuration:**
- Whitenoise serves static files with 1-year max-age headers
- Safe because hashed filenames change when content changes
- CloudFront can cache aggressively without stale asset risk

---

## Comparison: OBCMS vs. Similar App

| Aspect | Similar App (Scripts Approach) | OBCMS (Infrastructure Approach) |
|--------|-------------------------------|----------------------------------|
| **CSRF Protection** | Manual env var checks | Baked into Dockerfile + startup validation |
| **CSS Compilation** | Repair scripts if build fails | Fail-fast Docker build |
| **Cache Busting** | Manual CloudFront invalidation scripts | Automatic via hashed filenames |
| **Operational Burden** | Operators must run scripts | Zero manual intervention |
| **Failure Mode** | Stale CSS until script runs | Deployment fails if CSS build fails |
| **Recovery Process** | Run deploy-css-fix.sh | Rebuild Docker image |

---

## Deployment Checklist

Before deploying OBCMS to production, verify:

### ✅ CSRF Configuration
```bash
# .env must include:
CSRF_TRUSTED_ORIGINS=https://your-domain.com,https://www.your-domain.com
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
```

### ✅ Docker Build Test
```bash
# This MUST succeed before deploying:
docker build --target production -t obcms:test .

# Verify CSS was compiled:
docker run --rm obcms:test ls -lh /app/src/static/css/output.css
# Should show recent timestamp and >0 bytes
```

### ✅ Static Files Configuration
```bash
# Verify ManifestStaticFilesStorage is active in production:
docker run --rm obcms:test python src/manage.py diffsettings | grep STORAGES
# Should show: CompressedManifestStaticFilesStorage
```

### ✅ Post-Deploy Verification
```bash
# 1. Check Django settings module
docker-compose -f docker-compose.prod.yml exec web env | grep DJANGO_SETTINGS_MODULE
# Expected: obc_management.settings.production

# 2. Verify hashed static files exist
docker-compose -f docker-compose.prod.yml exec web ls /app/src/staticfiles/css/
# Expected: output.[hash].css output.[hash].css.gz staticfiles.json

# 3. Test a form submission (should NOT get CSRF error)
curl -X POST https://your-domain.com/login/ -d "username=test" -H "Referer: https://your-domain.com"
# Expected: CSRF cookie warning or login form (NOT 403)
```

---

## Emergency Recovery (If Issues Occur)

### If CSRF 403 Errors Appear

**Diagnosis:**
```bash
docker-compose -f docker-compose.prod.yml exec web python -c "from django.conf import settings; print(settings.CSRF_TRUSTED_ORIGINS)"
```

**Fix:**
1. Update `.env` with correct `CSRF_TRUSTED_ORIGINS`
2. Restart services: `docker-compose -f docker-compose.prod.yml restart web`

### If CSS is Missing/Broken

**Diagnosis:**
```bash
docker-compose -f docker-compose.prod.yml exec web ls -lh /app/src/staticfiles/css/
```

**Fix:**
1. Rebuild Docker image: `docker-compose -f docker-compose.prod.yml build web`
2. Restart services: `docker-compose -f docker-compose.prod.yml up -d web`

**Root cause:** CSS compilation failed during build. Check Docker build logs.

### If CloudFront Serves Stale CSS (Should Never Happen)

**Diagnosis:**
```bash
# Check if hashed filenames are being generated
docker-compose -f docker-compose.prod.yml exec web cat /app/src/staticfiles/staticfiles.json | grep output.css
```

**Fix (Manual Invalidation as Last Resort):**
```bash
# Only needed if ManifestStaticFilesStorage is broken
aws cloudfront create-invalidation --distribution-id YOUR_DIST_ID --paths "/static/css/*"
```

**Root cause:** ManifestStaticFilesStorage not active. Verify `STORAGES` configuration.

---

## References

### OBCMS Configuration Files
- [Dockerfile](../../Dockerfile) - Multi-stage build with Node.js CSS compilation
- [docker-compose.prod.yml](../../docker-compose.prod.yml) - Production deployment configuration
- [src/obc_management/settings/production.py](../../src/obc_management/settings/production.py) - Production Django settings
- [src/obc_management/settings/base.py](../../src/obc_management/settings/base.py) - ManifestStaticFilesStorage configuration

### External References
- [Django CSRF Protection](https://docs.djangoproject.com/en/stable/ref/csrf/)
- [Django Static Files Storage](https://docs.djangoproject.com/en/stable/ref/contrib/staticfiles/#manifeststaticfilesstorage)
- [Docker Multi-Stage Builds](https://docs.docker.com/build/building/multi-stage/)
- [Whitenoise Documentation](http://whitenoise.evans.io/en/stable/)

---

## Conclusion

OBCMS infrastructure **automatically prevents** all three production incidents through:

1. **Baked-in production settings** (no ad-hoc launch vulnerabilities)
2. **Fail-fast CSS compilation** (no silent build failures)
3. **Automatic cache busting** (no manual CDN invalidations)

**No operational scripts required.** All protections are infrastructure-level and activate automatically during standard Docker builds and deployments.

The similar app needed scripts because they were **retrofitting** protections after incidents. OBCMS has these protections **built-in from day one**.

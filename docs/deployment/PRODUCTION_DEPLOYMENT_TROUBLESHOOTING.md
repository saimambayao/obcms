# Production Deployment Troubleshooting Guide

**Last Updated**: 2025-10-05
**Status**: ✅ Production-Ready Solutions

This guide addresses the three most critical production deployment failures that can cause complete system outages. Each section includes root cause analysis, symptoms, fixes, and prevention strategies.

---

## Table of Contents

1. [Problem 1: CSRF 403 Errors - Complete Form Failure](#problem-1-csrf-403-errors)
2. [Problem 2: Tailwind CSS Build Failures - Visual Breakdown](#problem-2-tailwind-css-build-failures)
3. [Problem 3: CloudFront Cache Stalling - Invisible Fixes](#problem-3-cloudfront-cache-stalling)
4. [Pre-Deployment Checklist](#pre-deployment-checklist)
5. [Emergency Rollback Procedures](#emergency-rollback-procedures)

---

## Problem 1: CSRF 403 Errors

### Impact Assessment

**Severity**: 🔴 **CRITICAL - System Unusable**

**What Breaks**:
- ✗ All 99 forms across 83 templates fail with 403 error
- ✗ Login, registration, password reset - **BLOCKED**
- ✗ MANA assessments, MOA processing, community data entry - **BLOCKED**
- ✗ Events, coordination, staff tasks, project workflows - **BLOCKED**
- ✗ Admin panel operations - **BLOCKED**

**OBCMS-Specific Impact**:
- Field officers cannot record community needs during site visits
- MANA facilitators cannot conduct assessment workshops
- Directors cannot approve projects or recommendations
- Citizens cannot access any services requiring forms
- **Result**: 0% system availability, complete operational shutdown

---

### Root Cause

Django 4.0+ requires explicit `CSRF_TRUSTED_ORIGINS` for HTTPS requests behind reverse proxies (Nginx, Traefik, Coolify, CloudFront).

**Why This Happens**:
1. Browser sends form submission to `https://obcms.gov.ph`
2. Reverse proxy forwards request to Django with `X-Forwarded-Proto: https` header
3. Django CSRF validation checks if origin `https://obcms.gov.ph` is in `CSRF_TRUSTED_ORIGINS`
4. If not found → **403 Forbidden** (CSRF verification failed)

---

### Symptoms

**User Experience**:
```
Error 403: Forbidden
CSRF verification failed. Request aborted.
```

**Django Logs**:
```
WARNING django.security.csrf: Forbidden (CSRF cookie not set.): /login/
WARNING django.security.csrf: Forbidden (Origin checking failed - https://obcms.gov.ph does not match any trusted origins.)
```

**Browser Console**:
```
POST https://obcms.gov.ph/login/ 403 (Forbidden)
```

---

### Fix (Step-by-Step)

#### Step 1: Identify Your Domains

List ALL domains that will serve your application:
```bash
# Production domains
https://obcms.gov.ph
https://www.obcms.gov.ph

# Staging domains
https://staging.obcms.gov.ph

# Development domains (if deploying dev to Docker)
http://localhost:8000
http://127.0.0.1:8000
```

#### Step 2: Update `.env` File

Edit your production `.env` file:

```env
# ✅ CORRECT FORMAT
CSRF_TRUSTED_ORIGINS=https://obcms.gov.ph,https://www.obcms.gov.ph

# ❌ COMMON MISTAKES - DO NOT USE THESE
# Missing scheme:
CSRF_TRUSTED_ORIGINS=obcms.gov.ph  # WRONG

# Trailing slash:
CSRF_TRUSTED_ORIGINS=https://obcms.gov.ph/  # WRONG

# Spaces in comma-separated list:
CSRF_TRUSTED_ORIGINS=https://obcms.gov.ph, https://www.obcms.gov.ph  # WRONG

# Mixed with ALLOWED_HOSTS format:
CSRF_TRUSTED_ORIGINS=obcms.gov.ph,www.obcms.gov.ph  # WRONG
```

**Format Requirements**:
- ✅ MUST include scheme (`https://` or `http://`)
- ✅ NO trailing slashes
- ✅ NO spaces in comma-separated list
- ✅ Include www and non-www variants
- ✅ Include staging/development domains if applicable

#### Step 3: Restart Services

**Docker Compose**:
```bash
cd /path/to/obcms
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d
```

**Coolify**:
- Navigate to your OBCMS application
- Click **Environment Variables**
- Update `CSRF_TRUSTED_ORIGINS`
- Click **Save**
- Click **Restart**

**Systemd/Standalone**:
```bash
sudo systemctl restart obcms
sudo systemctl restart nginx  # if using Nginx
```

#### Step 4: Verify Fix

**Test Login**:
1. Open `https://obcms.gov.ph/admin/` in incognito window
2. Enter credentials
3. Submit form
4. ✅ Should login successfully (no 403 error)

**Test Form Submission**:
1. Navigate to any data entry form (Communities, MANA, etc.)
2. Fill out form
3. Submit
4. ✅ Should save successfully (no 403 error)

**Check Logs**:
```bash
# Docker Compose
docker-compose -f docker-compose.prod.yml logs web | grep -i csrf

# Expected output: No CSRF warnings
```

---

### Prevention

**1. Environment Validation (Automatic)**

OBCMS now validates `CSRF_TRUSTED_ORIGINS` at startup. If missing or malformed, Django won't start:

```python
# src/obc_management/settings/production.py
if not CSRF_TRUSTED_ORIGINS:
    raise ValueError(
        "CSRF_TRUSTED_ORIGINS must be set for production HTTPS\n"
        "Example: CSRF_TRUSTED_ORIGINS=https://obcms.gov.ph,https://www.obcms.gov.ph"
    )

for origin in CSRF_TRUSTED_ORIGINS:
    if not origin.startswith(("https://", "http://")):
        raise ValueError(f"Invalid format: {origin} (must include https://)")
```

**2. Pre-Deployment Check**:
```bash
cd src
python manage.py check --deploy

# Expected output:
# System check identified no issues (0 silenced).
```

**3. Staging Testing**:
Always test form submissions in staging before production deployment:
- Login/logout
- Data entry form (any module)
- Admin panel operations

---

## Problem 2: Tailwind CSS Build Failures

### Impact Assessment

**Severity**: 🟡 **HIGH - Visual Breakdown**

**What Breaks**:
- ✗ All 200+ custom Tailwind utilities missing from final CSS
- ✗ Ocean/Emerald/Gold gradients (government branding) → invisible
- ✗ Rounded corners, shadows, 3D effects → flat appearance
- ✗ Animations, hover states, transitions → static
- ✗ Professional 2025 design → looks like unstyled HTML from 1998

**OBCMS-Specific Impact**:
- Government logo: Invisible square instead of gradient circle
- Stat cards: Flat white rectangles instead of 3D milk-white cards
- Navbar: No gradient, scrolling effects broken
- Forms: Dropdown chevrons missing, focus rings missing
- **Result**: System looks broken/unprofessional, damages government credibility

---

### Root Cause

Tailwind CSS build fails or produces incomplete CSS during Docker build. Common causes:

1. **Template files not copied before Tailwind scan** → Classes not detected
2. **Node.js dependencies installation fails** → Build tools missing
3. **Input CSS missing** → Nothing to build
4. **PostCSS/Tailwind plugins error** → Build crashes
5. **Build succeeds but output.css not copied to production stage** → CSS missing

---

### Symptoms

**User Experience**:
- Website loads but looks completely unstyled
- No colors, gradients, spacing
- Elements overlapping or misaligned
- Buttons/forms look like plain HTML

**Docker Build Logs**:
```bash
# Build failure symptoms
ERROR: failed to solve: process "/bin/sh -c npm run build:css" did not complete successfully

# OR (silent failure - worse)
✓ Built successfully (but output.css is empty or incomplete)
```

**Browser DevTools**:
```css
/* Missing utilities */
.bg-gradient-primary { /* Not defined */ }
.text-ocean-600 { /* Not defined */ }
.shadow-ocean-lg { /* Not defined */ }
```

---

### Fix (Step-by-Step)

#### Step 1: Verify Build Configuration

**Check `package.json`**:
```bash
cat package.json | grep -A3 "scripts"

# Expected output:
"scripts": {
  "build:css": "NODE_ENV=production postcss ./src/static/css/input.css -o ./src/static/css/output.css",
  ...
}
```

**Check `tailwind.config.js`**:
```bash
cat tailwind.config.js | grep -A5 "content"

# Expected output:
content: [
  './src/templates/**/*.html',
  './src/static/**/*.js',
  './src/**/templates/**/*.html',
],
```

**Verify `input.css` exists**:
```bash
ls -la src/static/css/input.css

# Expected output:
-rw-r--r-- 1 user user 4783 Oct 5 16:06 src/static/css/input.css
```

#### Step 2: Rebuild Docker Image

**Full rebuild (no cache)**:
```bash
cd /path/to/obcms

# Build with verbose output
docker build --target production --no-cache --progress=plain -t obcms:latest .

# Watch for Tailwind build step (should show):
# ✓ Tailwind CSS built successfully: 113888 bytes
```

**Look for errors**:
```
# Good output:
Step 8/15 : RUN npm run build:css
> obcms@1.0.0 build:css
> NODE_ENV=production postcss ./src/static/css/input.css -o ./src/static/css/output.css
✓ Tailwind CSS built successfully: 113888 bytes

# Bad output (example):
ERROR: Cannot find module 'tailwindcss'
```

#### Step 3: Verify CSS Output

**After successful build, check output.css**:
```bash
# Run a test container
docker run --rm obcms:latest ls -lh /app/src/static/css/output.css

# Expected: ~110KB file
-rw-r--r-- 1 app app 111K Oct 5 16:32 /app/src/static/css/output.css

# Verify custom utilities are present
docker run --rm obcms:latest grep -c "bg-gradient-primary" /app/src/static/css/output.css

# Expected: 1 (or more)
```

#### Step 4: Deploy Updated Image

**Docker Compose**:
```bash
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d --build
```

**Coolify**:
- Push updated Dockerfile to Git
- Coolify auto-deploys on push
- Or manually trigger rebuild in Coolify UI

#### Step 5: Verify Fix

**Test in Browser**:
1. Open `https://obcms.gov.ph` (use incognito/hard refresh)
2. Inspect stat card element
3. Check computed styles in DevTools
4. ✅ Should show gradients, shadows, rounded corners

**Check Network Tab**:
```
GET https://obcms.gov.ph/static/css/output.css
Status: 200 OK
Size: ~110 KB
```

---

### Prevention

**1. Automated Build Verification (Now Implemented)**

Dockerfile now includes automatic verification:

```dockerfile
# Build production CSS with Tailwind
RUN npm run build:css && \
    # Verify CSS was built successfully
    test -f src/static/css/output.css && \
    echo "✓ Tailwind CSS built successfully: $(wc -c < src/static/css/output.css) bytes" || \
    (echo "✗ ERROR: Tailwind CSS build failed - output.css not found" && exit 1)
```

**Benefits**:
- Docker build FAILS if CSS not generated (no silent failures)
- Shows file size in build logs (easy verification)
- Prevents deploying broken images

**2. Template Scanning (Now Implemented)**

Dockerfile copies templates before Tailwind build:

```dockerfile
# Copy templates so Tailwind can scan for class names
COPY src/templates/ src/templates/
```

**Benefits**:
- Tailwind detects all dynamic classes in templates
- No missing utilities in final CSS
- Safelist in `tailwind.config.js` ensures common classes always included

**3. CI/CD Build Tests**:

Add to GitHub Actions / GitLab CI:

```yaml
# .github/workflows/build.yml
- name: Build Docker Image
  run: docker build --target production -t obcms:test .

- name: Verify CSS Build
  run: |
    SIZE=$(docker run --rm obcms:test stat -c%s /app/src/static/css/output.css)
    if [ "$SIZE" -lt 100000 ]; then
      echo "ERROR: CSS file too small ($SIZE bytes)"
      exit 1
    fi
    echo "✓ CSS build verified: $SIZE bytes"
```

---

## Problem 3: CloudFront Cache Stalling

### Impact Assessment

**Severity**: 🟠 **MEDIUM - Invisible Fixes**

**What Breaks**:
- ✗ Deploy CSS fix → users don't see it for hours/days
- ✗ CloudFront caches old `output.css` for 1 year (default)
- ✗ User browsers also cache stale CSS
- ✗ Fix exists on server but never reaches users

**OBCMS-Specific Impact**:
- Deploy navbar scroll fix → field officers still see broken navbar
- Regional offices using cached CSS from CloudFront edge servers
- IT helpdesk flooded with "still broken" tickets
- Requires manual CloudFront invalidation → operational burden

---

### Root Cause

**Multi-Layer Caching**:
1. **Browser Cache**: User's browser caches `output.css` for 1 year
2. **CloudFront Cache**: CDN caches `output.css` for 1 year at edge locations
3. **Reverse Proxy Cache**: Nginx/Traefik may also cache static files

**Without cache-busting**, users keep loading old CSS until cache expires.

---

### Solution: Automatic Cache-Busting (Already Implemented)

OBCMS uses **WhiteNoise with ManifestStaticFilesStorage** which automatically:
- Generates unique hashed filenames for static files
- Updates references in templates to hashed versions
- Invalidates cache automatically on file changes

**How It Works**:

```html
<!-- Template code (before collectstatic) -->
<link rel="stylesheet" href="{% static 'css/output.css' %}">

<!-- Rendered HTML (after collectstatic) -->
<link rel="stylesheet" href="/static/css/output.a8f3d4e2.css">
```

**On CSS Update**:
- New build → `output.css` content changes
- `collectstatic` generates new hash: `output.b9e4f5c3.css`
- Templates reference new hash automatically
- Old cache ignored (different filename)

---

### Verification

**Check Hashed Filenames**:
```bash
# Inside Docker container
docker exec -it obcms-web-1 ls /app/src/staticfiles/css/

# Expected output:
output.css             # Original
output.a8f3d4e2.css   # Hashed version
```

**Check staticfiles.json Manifest**:
```bash
docker exec -it obcms-web-1 cat /app/src/staticfiles/staticfiles.json | grep output.css

# Expected output:
"css/output.css": "css/output.a8f3d4e2.css"
```

**Verify in Browser**:
1. View page source
2. Find `<link rel="stylesheet">`
3. ✅ Should see hashed filename: `output.[hash].css`

---

### Manual CloudFront Invalidation (If Needed)

**When Required**:
- HTML files changed (not hashed)
- Immediate cache clear needed for critical fix

**AWS CloudFront**:
```bash
# Install AWS CLI
pip install awscli

# Configure credentials
aws configure

# Create invalidation
aws cloudfront create-invalidation \
  --distribution-id E1234ABCD5678 \
  --paths "/*"

# Check status
aws cloudfront get-invalidation \
  --distribution-id E1234ABCD5678 \
  --id I1234ABCD5678
```

**Coolify** (if using built-in CDN):
- Navigate to application settings
- Find "Clear Cache" or "Purge CDN"
- Click to invalidate

**Note**: With hashed filenames, manual invalidation rarely needed for CSS/JS.

---

### Enhanced Cache Control Headers

**Add to Nginx config** (if using Nginx, not needed with WhiteNoise):

```nginx
# /etc/nginx/sites-available/obcms.conf
location /static/ {
    alias /app/staticfiles/;

    # Hashed files: cache forever (filenames change on update)
    location ~* \.(css|js|png|jpg|jpeg|gif|ico|svg|woff|woff2)$ {
        if ($request_filename ~* \.[0-9a-f]{8,}\.) {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
        # Non-hashed: cache briefly
        expires 1h;
        add_header Cache-Control "public, must-revalidate";
    }
}

# HTML files: never cache (always check for updates)
location / {
    expires -1;
    add_header Cache-Control "no-store, no-cache, must-revalidate";
}
```

---

### Graceful Degradation (Now Implemented)

**Setting Added**:
```python
# src/obc_management/settings/base.py
WHITENOISE_MANIFEST_STRICT = False
```

**Benefits**:
- If hashed file missing → serves original file (no 404)
- Prevents broken deployment during rollout
- Users see content (even if cache not optimal)

---

## Pre-Deployment Checklist

Run this checklist BEFORE every production deployment:

### 1. Environment Configuration

```bash
# Verify all required variables set
cd /path/to/obcms

# Check .env file
grep -E '^(SECRET_KEY|ALLOWED_HOSTS|CSRF_TRUSTED_ORIGINS|DATABASE_URL|EMAIL_BACKEND)=' .env

# Expected: All variables present with production values
```

**Critical Variables**:
- [ ] `SECRET_KEY` (50+ characters, cryptographically random)
- [ ] `DEBUG=0` (MUST be 0 in production)
- [ ] `ALLOWED_HOSTS` (your-domain.com,www.your-domain.com)
- [ ] `CSRF_TRUSTED_ORIGINS` (https://your-domain.com,https://www.your-domain.com)
- [ ] `DATABASE_URL` (PostgreSQL connection string)
- [ ] `EMAIL_BACKEND` (NOT console backend)

### 2. Deployment Checks

```bash
cd src

# Run Django deployment checks
python manage.py check --deploy

# Expected output:
# System check identified no issues (0 silenced).

# If warnings appear, review and fix:
# - SECURE_HSTS_SECONDS not set → OK if HTTPS handled by proxy
# - SECURE_SSL_REDIRECT disabled → OK if proxy handles redirect
```

### 3. Build Verification

```bash
# Build Docker image
docker build --target production -t obcms:latest .

# Verify CSS built
docker run --rm obcms:latest stat -c%s /app/src/static/css/output.css

# Expected: ~100000+ bytes
```

### 4. Staging Deployment

**ALWAYS deploy to staging first**:

```bash
# Deploy to staging
docker-compose -f docker-compose.prod.yml -p obcms-staging up -d

# Wait for services to start
sleep 30

# Test critical paths
curl -I https://staging.obcms.gov.ph/
curl -I https://staging.obcms.gov.ph/admin/
curl -I https://staging.obcms.gov.ph/health/
```

### 5. Staging Testing

**Functional Tests**:
- [ ] Login to admin panel
- [ ] Submit a form (any module)
- [ ] Upload a file
- [ ] View dashboard with stat cards
- [ ] Test mobile responsiveness

**Visual Tests**:
- [ ] Stat cards show 3D milk-white design
- [ ] Navbar gradient visible
- [ ] Forms have rounded corners, focus rings
- [ ] Icons, colors render correctly

**Performance Tests**:
- [ ] Page load < 3 seconds
- [ ] No console errors in DevTools
- [ ] CSS file loads correctly (Network tab)

### 6. Production Deployment

**Only after staging passes all tests**:

```bash
# Pull latest code
git pull origin main

# Deploy to production
docker-compose -f docker-compose.prod.yml up -d --build

# Monitor logs for 5 minutes
docker-compose -f docker-compose.prod.yml logs -f web
```

### 7. Post-Deployment Verification

**Smoke Tests** (within 5 minutes):
```bash
# Health check
curl https://obcms.gov.ph/health/

# Admin panel
curl -I https://obcms.gov.ph/admin/

# Static files
curl -I https://obcms.gov.ph/static/css/output.css
```

**User Testing** (within 30 minutes):
- [ ] Login as test user
- [ ] Submit form in each module
- [ ] View calendar, dashboard
- [ ] Test on mobile device

---

## Emergency Rollback Procedures

### Scenario 1: CSRF Errors After Deployment

**Symptoms**: All forms failing with 403

**Quick Fix (5 minutes)**:
```bash
# 1. Update .env
nano .env

# Add/fix:
CSRF_TRUSTED_ORIGINS=https://obcms.gov.ph,https://www.obcms.gov.ph

# 2. Restart
docker-compose -f docker-compose.prod.yml restart web

# 3. Verify
curl -I https://obcms.gov.ph/admin/
```

### Scenario 2: CSS Not Loading

**Symptoms**: Website looks unstyled

**Quick Fix (10 minutes)**:
```bash
# 1. Verify CSS file exists
docker exec obcms-web-1 ls -lh /app/src/staticfiles/css/

# 2. If missing, rebuild collectstatic
docker exec obcms-web-1 python src/manage.py collectstatic --noinput

# 3. Restart
docker-compose -f docker-compose.prod.yml restart web

# 4. Hard refresh browser (Ctrl+Shift+R)
```

### Scenario 3: Complete Rollback

**Symptoms**: Critical failure, need previous version

**Rollback (15 minutes)**:
```bash
# 1. Stop current deployment
docker-compose -f docker-compose.prod.yml down

# 2. Checkout previous version
git log --oneline -10  # Find last working commit
git checkout <commit-hash>

# 3. Rebuild and deploy
docker-compose -f docker-compose.prod.yml up -d --build

# 4. Verify
curl https://obcms.gov.ph/health/
```

---

## Monitoring & Alerts

### Log Monitoring

**Watch for CSRF errors**:
```bash
docker-compose -f docker-compose.prod.yml logs -f web | grep -i csrf
```

**Watch for 403/500 errors**:
```bash
docker-compose -f docker-compose.prod.yml logs -f web | grep -E "403|500"
```

### Health Checks

**Automated health check** (add to cron):
```bash
# /etc/cron.d/obcms-healthcheck
*/5 * * * * curl -sf https://obcms.gov.ph/health/ || echo "OBCMS DOWN" | mail -s "OBCMS Health Check Failed" admin@obcms.gov.ph
```

---

## Support

**For deployment issues**:
1. Check this troubleshooting guide first
2. Review deployment docs: [docs/deployment/](../deployment/)
3. Check GitHub issues: https://github.com/tech-bangsamoro/obcms/issues

**Critical production issues**:
- Email: oobc-tech@barmm.gov.ph
- Emergency hotline: [contact information]

---

**Document Version**: 1.0
**Last Tested**: 2025-10-05 (All fixes verified in staging)
**Next Review**: 2025-11-05

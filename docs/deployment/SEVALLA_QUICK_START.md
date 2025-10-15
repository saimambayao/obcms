# Sevalla Quick Start Guide

## Docker Build Fixed ✅

The Docker build errors have been resolved. Here's what was fixed:

1. ✅ Removed invalid shell redirection in COPY command
2. ✅ Removed duplicate package installations
3. ✅ Created lean `requirements/production.txt` (excludes heavy AI/ML deps)
4. ✅ Build completes successfully

## Current Status

**Build:** ✅ Success
**Runtime:** ⚠️ Needs environment variables

## Required Environment Variables

Your deployment is failing because production settings require these environment variables:

### 1. Generate SECRET_KEY

```bash
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

### 2. Set in Sevalla Dashboard

Go to your Sevalla project → Environment Variables and add:

```bash
# REQUIRED
SECRET_KEY=<generated-secret-key-from-above>
ALLOWED_HOSTS=your-app.sevalla.app,your-domain.com
CSRF_TRUSTED_ORIGINS=https://your-app.sevalla.app,https://your-domain.com

# Sevalla provides these automatically:
# DATABASE_URL (PostgreSQL)
# REDIS_URL (Redis)

# Email configuration (required for production)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@example.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=OBCMS <noreply@your-domain.com>

# Deployment flags
RUN_MIGRATIONS=true
DJANGO_SETTINGS_MODULE=obc_management.settings.production
```

### 3. Important Notes

**ALLOWED_HOSTS:**
- Include your Sevalla subdomain (e.g., `obcms.sevalla.app`)
- Include any custom domains
- Comma-separated, no spaces

**CSRF_TRUSTED_ORIGINS:**
- **MUST include `https://` prefix**
- Example: `https://obcms.sevalla.app` (not just `obcms.sevalla.app`)
- Comma-separated, no spaces

**EMAIL_BACKEND:**
- Cannot use `console` backend in production
- Configure real SMTP server (Gmail, SendGrid, AWS SES, etc.)
- For Gmail: use App Password, not regular password

## Deployment Steps

1. **Set environment variables** in Sevalla dashboard
2. **Ensure PostgreSQL** database is provisioned (Sevalla does this automatically)
3. **Ensure Redis** is provisioned (for Celery tasks)
4. **Deploy** - Sevalla will build from Dockerfile
5. **Check logs** to verify startup succeeded

## After First Successful Deployment

Once your app runs successfully the first time:

1. Set `RUN_MIGRATIONS=false` (migrations already applied)
2. Verify health endpoint: `https://your-app.sevalla.app/health/`
3. Access admin: `https://your-app.sevalla.app/admin/`

## Troubleshooting

### "ALLOWED_HOSTS must be explicitly set"
→ Add `ALLOWED_HOSTS` to environment variables

### "CSRF_TRUSTED_ORIGINS must be set"
→ Add `CSRF_TRUSTED_ORIGINS` with `https://` prefix

### "EMAIL_BACKEND must be configured for production"
→ Change from `console` to real SMTP backend

### Build fails with pip errors
→ Fixed! Use the updated Dockerfile with `requirements/production.txt`

## Heavy AI/ML Dependencies

The production build now excludes heavy AI/ML packages to speed up builds:
- torch (~800MB)
- sentence-transformers
- faiss-cpu
- google-cloud-aiplatform

**If you need AI features later:**
```dockerfile
# Add to Dockerfile after line 60
RUN pip install -r requirements/ai.txt
```

## Next Steps

1. Configure environment variables in Sevalla
2. Trigger new deployment
3. Monitor logs for successful startup
4. Test application at your Sevalla URL

## Reference

- Full environment template: `.env.production.example`
- Production settings: `src/obc_management/settings/production.py`
- Requirements: `requirements/production.txt` (lean), `requirements/ai.txt` (AI deps)

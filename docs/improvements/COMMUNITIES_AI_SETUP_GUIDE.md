# Communities AI Features - Setup Guide

## Quick Start

### 1. Get Google API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Get API Key" → "Create API key in new project"
4. Copy the API key

### 2. Configure Environment Variables

Add to `/Users/saidamenmambayao/Library/Mobile Documents/com~apple~CloudDocs/BTA/OOBC/obcms/src/.env`:

```env
# Google Gemini AI Configuration
GOOGLE_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-2.0-flash-exp
```

### 3. Update Django Settings

Add to `src/obc_management/settings/development.py`:

```python
# Google Gemini AI Configuration
GOOGLE_API_KEY = env('GOOGLE_API_KEY', default=None)
GEMINI_MODEL = env('GEMINI_MODEL', default='gemini-2.0-flash-exp')
```

### 4. Test Installation

```bash
cd src
python manage.py shell

>>> from communities.ai_services.data_validator import CommunityDataValidator
>>> validator = CommunityDataValidator()
>>> # Should NOT show warnings if configured correctly
```

### 5. Run Tests

```bash
cd src
python manage.py test communities.tests.test_ai_services
```

---

## API Key Safety

⚠️ **IMPORTANT**: Never commit API keys to version control!

### Check .gitignore

Ensure `.env` is in `.gitignore`:

```bash
# Check if .env is ignored
cat .gitignore | grep .env
```

If not, add it:

```bash
echo ".env" >> .gitignore
```

---

## Free Tier Limits

**Gemini Free Tier**:
- 60 requests per minute
- 1,500 requests per day
- FREE (no cost)

**For OOBC** (estimated usage):
- ~200 communities
- ~10 AI calls per community detail view (with caching)
- Should stay well within limits

**If limits exceeded**:
- Enable caching (24-hour cache recommended)
- Use background Celery tasks for batch processing
- Upgrade to paid tier ($0.00025 per 1,000 characters)

---

## Troubleshooting

### Error: "GOOGLE_API_KEY not configured"

**Solution**: Add API key to `.env` file and restart Django server

### Error: "API key not valid"

**Solution**:
1. Verify API key is correct (no extra spaces)
2. Check API is enabled in Google Cloud Console
3. Ensure billing is enabled (even for free tier)

### Tests failing with AttributeError

**Solution**: API key not in settings. Follow setup steps above.

### Slow AI responses

**Solution**:
1. Enable caching in views
2. Use background Celery tasks
3. Consider upgrading to Gemini Pro (faster)

---

## Production Deployment

### Environment Variables

```bash
# Production .env
GOOGLE_API_KEY=production_api_key_here
GEMINI_MODEL=gemini-2.0-flash-exp

# Separate key for production (recommended)
```

### Caching Configuration

```python
# settings/production.py
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
        'TIMEOUT': 86400,  # 24 hours for AI results
    }
}
```

### Celery Background Tasks

```python
# celerybeat_schedule.py
from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    'classify-community-needs-daily': {
        'task': 'communities.tasks.classify_all_community_needs',
        'schedule': crontab(hour=2, minute=0),  # 2 AM daily
    },
}
```

---

## Monitoring

### Log AI Usage

```python
# settings.py
LOGGING = {
    'loggers': {
        'communities.ai_services': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
```

### Check Logs

```bash
tail -f logs/django.log | grep "communities.ai"
```

---

## Cost Estimation

### Free Tier (Current Setup)
- **Cost**: $0/month
- **Capacity**: ~1,500 requests/day
- **Sufficient for**: ~150 community detail views/day

### Paid Tier (If Needed)
- **Cost**: ~$5-10/month (estimated)
- **Capacity**: Unlimited (within reason)
- **Use when**: >1,500 requests/day needed

### ROI Calculation
- AI validation saves ~5 min per community
- 200 communities × 5 min = 1,000 minutes (16.7 hours)
- Staff hourly rate × 16.7 = Cost savings
- **ROI**: Positive even with paid tier

---

## Support

### Google Gemini Support
- [Documentation](https://ai.google.dev/docs)
- [API Reference](https://ai.google.dev/api)
- [Community Forum](https://discuss.ai.google.dev/)

### OBCMS Support
- Check logs: `src/logs/django.log`
- GitHub Issues: (if applicable)
- Email: tech team

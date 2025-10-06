# OBCMS AI Deployment Guide

**Date:** October 6, 2025
**Version:** 1.0
**Status:** Production Ready

---

## Quick Start (5 Minutes)

### Option 1: Automated Deployment (Recommended)

```bash
# From OBCMS root directory
cd /path/to/obcms

# Run deployment script
./scripts/deploy_ai.sh

# Verify installation
./scripts/verify_ai.sh

# Start development server
cd src && python3 manage.py runserver
```

### Option 2: Manual Deployment

```bash
# 1. Activate virtual environment
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements/base.txt

# 3. Configure API key
echo "GOOGLE_API_KEY=your_key_here" >> .env

# 4. Run migrations
cd src
python3 manage.py migrate

# 5. Verify
python3 manage.py ai_health_check

# 6. Start server
python3 manage.py runserver
```

---

## Detailed Deployment Steps

### Prerequisites

**System Requirements:**
- Python 3.12+
- PostgreSQL 14+ (or SQLite for development)
- Redis 6+ (for caching and Celery)
- 4GB+ RAM
- 10GB+ disk space

**API Keys:**
- Google Gemini API key (get from https://ai.google.dev/)

### Step 1: Environment Setup

#### 1.1 Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate     # Windows

# Upgrade pip
pip install --upgrade pip
```

#### 1.2 Install Dependencies

```bash
# Install all AI dependencies
pip install -r requirements/base.txt

# This installs:
# - google-generativeai (Gemini API)
# - faiss-cpu (vector database)
# - sentence-transformers (embeddings)
# - torch (ML framework)
# - redis (caching)
# - celery (background tasks)
```

**Expected install time:** 5-10 minutes

#### 1.3 Verify Installation

```bash
python3 << 'EOF'
import google.generativeai
import faiss
import sentence_transformers
import redis
import celery
print("✓ All dependencies installed successfully")
EOF
```

### Step 2: Configuration

#### 2.1 Environment Variables

Create/update `.env` file:

```bash
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=1
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (SQLite for dev)
DATABASE_URL=sqlite:///db.sqlite3

# Redis & Celery
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0

# Google Gemini AI
GOOGLE_API_KEY=your_google_gemini_api_key_here
GEMINI_MODEL=gemini-2.0-flash-exp

# AI Configuration (Optional)
AI_DAILY_BUDGET=10.00
AI_MONTHLY_BUDGET=100.00
```

**🔑 Getting a Gemini API Key:**

1. Go to https://ai.google.dev/
2. Click "Get API Key"
3. Create new project or select existing
4. Copy API key
5. Add to `.env` file

**Free Tier Limits:**
- 60 requests per minute
- 1,500 requests per day
- Sufficient for OBCMS usage

#### 2.2 Django Settings

Verify `ai_assistant` is in `INSTALLED_APPS`:

```python
# src/obc_management/settings/base.py

INSTALLED_APPS = [
    # ... other apps ...
    'ai_assistant',  # ← Should be here
    'communities',
    'mana',
    'coordination',
    'recommendations',
    'project_central',
    'common',
]
```

### Step 3: Database Setup

#### 3.1 Run Migrations

```bash
cd src

# Check pending migrations
python3 manage.py showmigrations ai_assistant common

# Apply all migrations
python3 manage.py migrate

# Expected output:
# Running migrations:
#   Applying ai_assistant.0001_initial... OK
#   Applying ai_assistant.0002_aioperation_documentembedding... OK
#   Applying common.0025_chatmessage... OK
```

#### 3.2 Create Superuser

```bash
python3 manage.py createsuperuser

# Enter:
# - Username: admin
# - Email: admin@oobc.gov.ph
# - Password: (secure password)
```

#### 3.3 Load Sample Data (Optional)

```bash
# If you have fixtures
python3 manage.py loaddata communities mana coordination
```

### Step 4: Vector Index Setup

#### 4.1 Create Vector Indices Directory

```bash
# From src/ directory
mkdir -p ai_assistant/vector_indices

# Verify
ls -la ai_assistant/vector_indices
```

#### 4.2 Index Initial Data

```bash
# Index communities
python3 manage.py index_communities

# Expected output:
# Indexing 42 communities...
# ✓ Generated embeddings for 42 communities
# ✓ Vector index saved
# Completed in 12.5 seconds

# Index policies (if you have policies)
python3 manage.py index_policies

# Rebuild entire index
python3 manage.py rebuild_vector_index
```

### Step 5: Start Services

#### 5.1 Django Development Server

```bash
# Terminal 1: Django server
cd src
python3 manage.py runserver

# Server runs at http://localhost:8000
```

#### 5.2 Redis Server

```bash
# Terminal 2: Redis
redis-server

# Or if installed via Homebrew (Mac):
brew services start redis

# Verify Redis is running:
redis-cli ping
# Expected: PONG
```

#### 5.3 Celery Worker

```bash
# Terminal 3: Celery worker
cd src
celery -A obc_management worker -l info

# Expected output:
# celery@hostname ready.
# - *** --- Modules:
# - coordination.tasks
# - mana.tasks
# - project_central.tasks
# - recommendations.policy_tracking.tasks
```

#### 5.4 Celery Beat (Scheduler)

```bash
# Terminal 4: Celery beat
cd src
celery -A obc_management beat -l info

# Expected output:
# celery beat v5.3.0 is starting.
# Scheduler: PersistentScheduler
```

**Background Tasks Scheduled:**
- Daily: Anomaly detection (6 AM)
- Daily: Search analytics (3 AM)
- Weekly: Stakeholder matching (Monday 2 AM)
- Weekly: PPA forecasts (Monday 7 AM)
- Monthly: Generate M&E reports (1st of month, 8 AM)

### Step 6: Verification

#### 6.1 Run Verification Script

```bash
# From project root
./scripts/verify_ai.sh

# Checks:
# ✓ Service imports
# ✓ Database models
# ✓ Management commands
# ✓ Configuration
# ✓ Dependencies
# ✓ Health check
```

#### 6.2 Manual Health Check

```bash
cd src
python3 manage.py ai_health_check

# Expected output:
# ========================================
# AI INFRASTRUCTURE HEALTH CHECK
# ========================================
# 1. Checking Google API Key...
#    ✓ API Key configured
# 2. Checking Gemini Service...
#    ✓ Gemini API connection successful
# 3. Checking Cache (Redis)...
#    ✓ Cache operational
# 4. Checking AI Models...
#    ✓ All models accessible
# ...
# ========================================
# ✓ ALL CHECKS PASSED
# ========================================
```

#### 6.3 Test AI Features

**Test 1: Communities AI**
```python
cd src
python3 manage.py shell

# In shell:
from communities.ai_services import CommunityNeedsClassifier
from communities.models import BarangayOBC

classifier = CommunityNeedsClassifier()
community = BarangayOBC.objects.first()

if community:
    needs = classifier.classify_needs(community)
    print(needs)
# Expected: Dictionary with need categories and scores
```

**Test 2: Chat AI**
```python
from common.ai_services.chat import get_conversational_assistant

assistant = get_conversational_assistant()
response = assistant.chat(user_id=1, message="How many communities are there?")
print(response['response'])
# Expected: Natural language response with count
```

**Test 3: Vector Search**
```python
from ai_assistant.services import SimilaritySearchService

search = SimilaritySearchService()
results = search.search_communities("coastal fishing communities", limit=5)
print(f"Found {len(results)} similar communities")
```

### Step 7: Access the System

#### 7.1 Admin Panel

```
URL: http://localhost:8000/admin/
Login: admin / your_password

Navigate to:
- AI Assistant → AI Operations (view API usage, costs)
- AI Assistant → Document Embeddings (view indexed documents)
- Common → Chat Messages (view conversation history)
```

#### 7.2 User Interface

```
Communities: http://localhost:8000/communities/
MANA: http://localhost:8000/mana/
Coordination: http://localhost:8000/coordination/
Policies: http://localhost:8000/recommendations/policies/
Projects: http://localhost:8000/projects/

Chat Widget: Look for floating button (bottom-right) on any page
```

#### 7.3 API Endpoints

```bash
# Unified Search
curl http://localhost:8000/search/?q=coastal+communities

# Chat API
curl -X POST http://localhost:8000/chat/message/ \
  -H "Content-Type: application/json" \
  -d '{"message": "How many communities?"}'

# AI Health Check (API)
curl http://localhost:8000/api/ai/health/
```

---

## Production Deployment

### Additional Steps for Production

#### 1. Use PostgreSQL

```bash
# Update .env
DATABASE_URL=postgres://obcms_user:password@localhost:5432/obcms_prod

# Run migrations
python3 manage.py migrate
```

#### 2. Configure Gunicorn

```bash
# Install
pip install gunicorn

# Run
gunicorn obc_management.wsgi:application \
  --bind 0.0.0.0:8000 \
  --workers 4 \
  --timeout 120
```

#### 3. Use Supervisor for Process Management

```ini
# /etc/supervisor/conf.d/obcms.conf

[program:obcms_web]
command=/path/to/venv/bin/gunicorn obc_management.wsgi:application --bind 0.0.0.0:8000
directory=/path/to/obcms/src
user=obcms
autostart=true
autorestart=true

[program:obcms_celery]
command=/path/to/venv/bin/celery -A obc_management worker -l info
directory=/path/to/obcms/src
user=obcms
autostart=true
autorestart=true

[program:obcms_celerybeat]
command=/path/to/venv/bin/celery -A obc_management beat -l info
directory=/path/to/obcms/src
user=obcms
autostart=true
autorestart=true
```

#### 4. Configure Nginx

```nginx
# /etc/nginx/sites-available/obcms

server {
    listen 80;
    server_name obcms.yourdomain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /static/ {
        alias /path/to/obcms/static/;
    }

    location /media/ {
        alias /path/to/obcms/media/;
    }
}
```

#### 5. Set Production Environment

```bash
# .env for production
DEBUG=0
ALLOWED_HOSTS=obcms.yourdomain.com
SECRET_KEY=very-long-random-secret-key

# Use production Gemini API key
GOOGLE_API_KEY=production_key_here

# Secure cookies
SESSION_COOKIE_SECURE=1
CSRF_COOKIE_SECURE=1
```

---

## Monitoring & Maintenance

### Daily Checks

```bash
# Check Celery tasks
celery -A obc_management inspect active

# Check AI usage
cd src && python3 manage.py shell
from ai_assistant.utils import CostTracker
tracker = CostTracker()
print(f"Today's cost: ${tracker.get_daily_cost():.2f}")
print(f"This month: ${tracker.get_monthly_cost():.2f}")
```

### Weekly Maintenance

```bash
# Reindex vector stores
python3 manage.py rebuild_vector_index

# Review AI operations
# Admin → AI Operations → Filter by last 7 days

# Check cache hit rates
redis-cli
> INFO stats
```

### Monthly Reviews

- Review and update AI prompts
- Analyze search patterns
- Check cost trends
- Update cultural guidelines
- Review anomaly detection accuracy

---

## Troubleshooting

### Problem: "Module 'ai_assistant' not found"

**Solution:**
```bash
# Verify INSTALLED_APPS
python3 manage.py shell
from django.conf import settings
print('ai_assistant' in settings.INSTALLED_APPS)

# Should print: True
```

### Problem: "GOOGLE_API_KEY not found"

**Solution:**
```bash
# Check .env file
cat .env | grep GOOGLE_API_KEY

# Should show: GOOGLE_API_KEY=your_key

# Restart Django server after updating .env
```

### Problem: "Redis connection failed"

**Solution:**
```bash
# Start Redis
redis-server

# Or (Mac with Homebrew):
brew services start redis

# Verify
redis-cli ping
# Should respond: PONG
```

### Problem: "Celery tasks not running"

**Solution:**
```bash
# Check worker is running
celery -A obc_management inspect active

# Check beat is running
ps aux | grep "celery beat"

# Restart workers
pkill -f "celery worker"
celery -A obc_management worker -l info &
```

### Problem: "AI health check fails"

**Solution:**
```bash
# Run detailed health check
python3 manage.py ai_health_check --verbose

# Check logs
tail -f logs/ai_assistant.log

# Test Gemini API manually
python3 << 'EOF'
import google.generativeai as genai
import os
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
model = genai.GenerativeModel('gemini-2.0-flash-exp')
response = model.generate_content("Hello")
print(response.text)
EOF
```

---

## Performance Optimization

### Caching Strategy

```python
# In settings/production.py

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
        'KEY_PREFIX': 'obcms',
        'TIMEOUT': 3600,  # 1 hour default
    }
}

# AI-specific cache settings
AI_CACHE_TTL = {
    'gemini_response': 86400,    # 24 hours
    'embeddings': 604800,        # 7 days
    'search_results': 3600,      # 1 hour
    'policy_analysis': 604800,   # 7 days
}
```

### Database Optimization

```sql
-- Create indexes for AI operations
CREATE INDEX idx_ai_operation_created ON ai_assistant_aioperation(created_at);
CREATE INDEX idx_ai_operation_module ON ai_assistant_aioperation(module);
CREATE INDEX idx_chat_message_user ON common_chatmessage(user_id, created_at);
```

### Vector Index Optimization

```python
# For large datasets (>100K documents), use IVF index
# In ai_assistant/services/vector_store.py

# Replace IndexFlatL2 with IndexIVFFlat
nlist = 100  # Number of clusters
quantizer = faiss.IndexFlatL2(dimension)
index = faiss.IndexIVFFlat(quantizer, dimension, nlist)
```

---

## Security Checklist

- [ ] ✅ GOOGLE_API_KEY stored in .env (not in code)
- [ ] ✅ DEBUG=0 in production
- [ ] ✅ SECRET_KEY is strong and unique
- [ ] ✅ ALLOWED_HOSTS configured
- [ ] ✅ HTTPS enabled
- [ ] ✅ Rate limiting configured
- [ ] ✅ API key rotation scheduled (90 days)
- [ ] ✅ Audit logging enabled
- [ ] ✅ User authentication enforced on AI endpoints

---

## Cost Management

### Expected Monthly Costs

| Service | Usage | Cost |
|---------|-------|------|
| Google Gemini API | ~50K requests | $50-100 |
| Redis (managed) | Standard | $30 |
| Vector Storage | Local (FAISS) | $0 |
| **Total** | | **$80-130** |

### Cost Optimization Tips

1. **Enable Aggressive Caching**
   - Cache hit rate target: 80%+
   - Review cache TTLs weekly

2. **Use Batch Operations**
   - Process multiple requests together
   - Schedule heavy operations during off-peak

3. **Monitor Usage**
   - Set up daily cost alerts
   - Review AIOperation table weekly

4. **Optimize Prompts**
   - Shorter prompts = lower costs
   - Review and compress prompts quarterly

---

## Support & Resources

### Documentation
- Quick Start: `docs/ai/AI_QUICK_START.md`
- Full Strategy: `docs/ai/AI_STRATEGY_COMPREHENSIVE.md`
- Implementation Checklist: `docs/ai/AI_IMPLEMENTATION_CHECKLIST.md`

### Scripts
- Deployment: `scripts/deploy_ai.sh`
- Verification: `scripts/verify_ai.sh`

### Management Commands
```bash
python3 manage.py ai_health_check        # System health
python3 manage.py index_communities      # Index communities
python3 manage.py index_policies         # Index policies
python3 manage.py rebuild_vector_index   # Rebuild all indices
```

### Getting Help
- Check logs: `logs/ai_assistant.log`
- Review admin panel: AI Operations table
- Run health check with `--verbose` flag

---

## Changelog

### Version 1.0 (October 6, 2025)
- Initial AI deployment
- All 4 phases implemented
- Production-ready release

---

**Deployment Complete!** 🚀

The OBCMS AI system is now ready for production use.

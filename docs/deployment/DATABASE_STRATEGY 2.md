# Database Strategy - Development vs Production

**Created:** October 6, 2025
**Status:** Active Configuration

---

## 🎯 Current Question: "Are we using PostgreSQL everywhere now?"

**Short Answer:** You have **flexibility**. Use the right database for each scenario.

**Long Answer:** Let me explain the recommended strategy...

---

## 📊 Database Options Available

You have **3 databases** set up and ready to use:

| Database | Version | Best For | Switch Command |
|----------|---------|----------|----------------|
| **SQLite** | - | Daily development, rapid iteration | `cp .env.sqlite .env` |
| **PostgreSQL (Local)** | 17.6 | Production testing, feature development | `cp .env.postgres.local .env` |
| **PostgreSQL (Docker)** | 17.6 | Deployment testing, CI/CD | `cp .env.postgres.docker .env` |

---

## 🤔 Recommended Strategy

### Development (Daily Coding)

**Recommendation:** Use **SQLite** ✅

**Why:**
- ✅ **Fast startup** - No service to manage
- ✅ **Your data is safe** - 4.7MB of dev data preserved
- ✅ **Portable** - Just a file, easy to back up
- ✅ **No setup needed** - Works immediately
- ✅ **Good enough** - Django abstracts database differences

**When to use:**
- Adding features
- Testing changes
- UI/UX work
- Rapid prototyping
- Learning the codebase

**Switch to SQLite:**
```bash
cp .env.sqlite .env
python src/manage.py runserver
```

---

### Pre-Deployment Testing

**Recommendation:** Use **Local PostgreSQL 17** ⚡

**Why:**
- ✅ **Production-like** - Same database as production
- ✅ **Fast performance** - Native macOS, no Docker overhead
- ✅ **PostgreSQL-specific features** - Test JSONField, full-text search
- ✅ **Easy debugging** - Direct `psql` access
- ✅ **Catch PostgreSQL bugs early** - Before deployment

**When to use:**
- Before creating a pull request
- Testing database migrations
- Performance benchmarking
- PostgreSQL-specific feature testing
- Weekly integration testing

**Switch to Local PostgreSQL:**
```bash
cp .env.postgres.local .env
python src/manage.py runserver
```

---

### Deployment Simulation

**Recommendation:** Use **Docker PostgreSQL 17** 🐳

**Why:**
- ✅ **Matches production** - Exact deployment setup
- ✅ **Full stack testing** - Web + DB + Redis + Celery
- ✅ **CI/CD ready** - Same as staging/production
- ✅ **Easy reset** - `docker-compose down -v` and start fresh
- ✅ **Multi-service** - Test background tasks, caching

**When to use:**
- Testing Docker deployment
- Staging environment simulation
- Full system integration tests
- Before production deployment
- CI/CD pipeline testing

**Switch to Docker PostgreSQL:**
```bash
# Stop local PostgreSQL to avoid port conflict
brew services stop postgresql@17

# Start Docker services
docker-compose up -d

# Use Docker PostgreSQL
cp .env.postgres.docker .env
python src/manage.py runserver
```

---

## 🎯 My Recommended Workflow

### Daily Development (90% of the time)
```bash
# Use SQLite - fast, simple, has your data
cp .env.sqlite .env
python src/manage.py runserver
```

### Friday Testing (Weekly)
```bash
# Test with PostgreSQL before the weekend
cp .env.postgres.local .env
pytest -v
python src/manage.py runserver
# Manually test critical features
```

### Before Pull Request
```bash
# Final check with PostgreSQL
cp .env.postgres.local .env
pytest -v
python src/manage.py check --deploy
```

### Before Deployment
```bash
# Full Docker stack test
docker-compose up -d
cp .env.postgres.docker .env
pytest -v
# Smoke test all features
```

---

## ⚠️ Production Environment

**Production uses:** **PostgreSQL 17** (Required)

**Why PostgreSQL is required in production:**
- ✅ **Concurrent users** - Handles 100+ simultaneous connections
- ✅ **Data integrity** - ACID compliance, transactions
- ✅ **Performance** - 2-3x faster than SQLite
- ✅ **Scalability** - Supports thousands of users
- ✅ **Advanced features** - JSONField queries, full-text search
- ❌ **SQLite limitations** - Single writer, no network access

**Production setup options:**
1. **Managed PostgreSQL** (Recommended)
   - DigitalOcean Managed Database
   - AWS RDS PostgreSQL
   - Google Cloud SQL
   - Azure Database for PostgreSQL

2. **Self-hosted Docker** (docker-compose.prod.yml)
   - Uses `postgres:17-alpine`
   - Automated backups required
   - Monitoring required

---

## 📋 Migration Status

### Data Migration: Not Required

**Important:** You don't need to migrate SQLite data to PostgreSQL for development.

**Why:**
- ✅ SQLite has your dev/test data (4.7MB)
- ✅ PostgreSQL databases are fresh (empty)
- ✅ You can switch between them anytime
- ✅ Production will have its own data

**If you want the same data in all databases:**

**Option 1: Keep SQLite data where it is**
```bash
# Just use SQLite when you need your dev data
cp .env.sqlite .env
```

**Option 2: Manual re-entry**
```bash
# Use PostgreSQL and re-create test users
cp .env.postgres.local .env
python src/manage.py createsuperuser
# Add test communities via admin panel
```

**Option 3: Fresh start everywhere**
```bash
# Clean slate - good for final testing
# Use PostgreSQL and create fresh test data
```

---

## 🔄 Switching Databases

### Quick Switch Commands

**To SQLite:**
```bash
cp .env.sqlite .env && python src/manage.py runserver
```

**To Local PostgreSQL:**
```bash
cp .env.postgres.local .env && python src/manage.py runserver
```

**To Docker PostgreSQL:**
```bash
brew services stop postgresql@17  # Avoid port conflict
docker-compose up -d db
cp .env.postgres.docker .env && python src/manage.py runserver
```

### Check Current Database

```bash
cd src
python manage.py dbshell
```

**In SQLite:**
```sql
.tables
.quit
```

**In PostgreSQL:**
```sql
SELECT current_database(), version();
\q
```

---

## 🎨 Visual Summary

```
Development Flow:
┌─────────────────────────────────────────────────┐
│                                                 │
│  Daily Dev (90%)        │ SQLite                │
│  ─────────────────────────────────────────────  │
│                                                 │
│  Weekly Testing (5%)    │ Local PostgreSQL 17   │
│  ─────────────────────────────────────────────  │
│                                                 │
│  Pre-Deployment (5%)    │ Docker PostgreSQL 17  │
│  ─────────────────────────────────────────────  │
│                                                 │
│  Production (REQUIRED)  │ PostgreSQL 17         │
│                           (Managed/Self-hosted)  │
└─────────────────────────────────────────────────┘
```

---

## 💡 Key Insights

### You Are NOT Forced to Use PostgreSQL

**The migration gave you OPTIONS, not requirements:**
- ✅ SQLite still works perfectly
- ✅ Your SQLite data is safe (4.7MB preserved)
- ✅ Switch databases anytime with one command
- ✅ Use the right tool for each scenario

### When SQLite is Better

**Use SQLite when:**
- Rapid development
- Learning the codebase
- UI/UX prototyping
- Offline work
- You need your dev data

### When PostgreSQL is Better

**Use PostgreSQL when:**
- Testing production behavior
- PostgreSQL-specific features
- Performance testing
- Pre-deployment validation
- Final integration testing

### Production Requirement

**PostgreSQL is REQUIRED in production:**
- Handles concurrent users
- Better performance
- Data integrity guarantees
- Industry standard for web apps

---

## 🚀 Recommended Next Step

### For You Right Now

**I recommend switching back to SQLite for daily development:**

```bash
# Switch to SQLite (has your data)
cp .env.sqlite .env

# Verify it works
cd src
python manage.py runserver

# Visit http://localhost:8000/admin/
# Your dev data should be there
```

**Use PostgreSQL when:**
- Testing database migrations
- Before creating pull requests
- Weekly integration testing
- Pre-deployment validation

---

## 📚 Summary

### Current State (After Migration)

- ✅ **SQLite**: 4.7MB with dev data, ready to use
- ✅ **Local PostgreSQL 17**: Installed, migrations applied, empty
- ✅ **Docker PostgreSQL 17**: Running, migrations applied, empty
- ✅ **Environment templates**: Created for easy switching

### Your Current Configuration

**Active database:** Local PostgreSQL 17 (`obcms_local`)
**Recommendation:** Switch to SQLite for daily dev

### The Answer

**Q: "Are we using PostgreSQL in dev and prod now?"**

**A:** You **CAN** use PostgreSQL everywhere, but you **DON'T HAVE TO**.

**Better answer:**
- **Development:** Use **SQLite** for daily work ⚡ (recommended)
- **Testing:** Use **PostgreSQL** periodically 🧪 (recommended)
- **Production:** Use **PostgreSQL** always ✅ (required)

---

**You have flexibility. Use the database that makes sense for what you're doing right now.**

**Need your dev data?** → SQLite
**Testing migrations?** → Local PostgreSQL
**Deploying soon?** → Docker PostgreSQL
**In production?** → PostgreSQL (required)

---

**Created by:** Claude Code
**Date:** October 6, 2025
**See also:**
- [POSTGRESQL_QUICK_START.md](POSTGRESQL_QUICK_START.md)
- [docs/deployment/POSTGRESQL_MIGRATION_COMPLETE.md](docs/deployment/POSTGRESQL_MIGRATION_COMPLETE.md)

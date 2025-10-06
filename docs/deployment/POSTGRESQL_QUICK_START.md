# PostgreSQL Quick Start Guide

**OBCMS Database Configuration - Quick Reference**

---

## 🚀 Switch Database in 10 Seconds

### Use SQLite (Original)
```bash
cp .env.sqlite .env && python src/manage.py runserver
```

### Use Local PostgreSQL 17 (Recommended)
```bash
cp .env.postgres.local .env && python src/manage.py runserver
```

### Use Docker PostgreSQL 17
```bash
brew services stop postgresql@17  # Avoid port conflict
docker-compose up -d db
cp .env.postgres.docker .env && python src/manage.py runserver
```

---

## 📊 Database Status

| Database | Version | Status | Data |
|----------|---------|--------|------|
| SQLite | - | ✅ Active | 4.7MB (with dev data) |
| PostgreSQL (Local) | 17.6 | ✅ Active | Fresh (no data) |
| PostgreSQL (Docker) | 17.6 | ✅ Active | Fresh (no data) |

---

## ✅ Migration Complete

- **118/118 migrations applied** to all databases
- **SQLite data backed up** (2 backups created)
- **Environment templates created** (.env.sqlite, .env.postgres.local, .env.postgres.docker)
- **PostgreSQL 14 removed** (cleaned up old version)
- **psycopg3 3.2.10** installed and verified

---

## 🔧 Common Commands

**Check current database:**
```bash
cd src && python manage.py dbshell
```

**Create superuser:**
```bash
cd src && python manage.py createsuperuser
```

**Run migrations:**
```bash
cd src && python manage.py migrate
```

**Run tests:**
```bash
pytest -v
```

---

## 📚 Full Documentation

See [docs/deployment/POSTGRESQL_MIGRATION_COMPLETE.md](docs/deployment/POSTGRESQL_MIGRATION_COMPLETE.md) for:
- Complete migration report
- Detailed switching instructions
- Troubleshooting guide
- PostgreSQL administration commands
- Performance comparison
- Next steps and recommendations

---

**Migration completed October 6, 2025** ✅

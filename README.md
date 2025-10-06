# OBC Management System

**Other Bangsamoro Communities Management System**

A comprehensive web-based application designed to support the Office for Other Bangsamoro Communities (OOBC) in serving Other Bangsamoro Communities (OBCs) residing outside the Bangsamoro Autonomous Region in Muslim Mindanao (BARMM).

## Recent Updates

**WorkItem Unified Model (October 2025):**
The OBCMS now uses a unified WorkItem model for all work management (projects, activities, tasks). Legacy models (StaffTask, Event, ProjectWorkflow) have been deprecated and removed.

- **Migration Guide:** [WORKITEM_MIGRATION_COMPLETE.md](WORKITEM_MIGRATION_COMPLETE.md)
- **Documentation:** [docs/refactor/](docs/refactor/)
- **Feature Flags:** See `.env.example` for configuration

All new development should use WorkItem. See [Work Item Examples](docs/refactor/WORK_ITEM_IMPLEMENTATION_EXAMPLES.md) if available.

## Project Overview

This system digitalizes the OOBC's core functions including:
- Gathering information and assessing needs of OBCs
- Recommending policies and systematic programs
- Coordinating with stakeholders (BMOAs, LGUs, NGAs)
- Supporting MANA (Mapping and Needs Assessment) activities
- Facilitating evidence-based policy recommendations

## Technology Stack

- **Backend**: Django 4.2+ (Python web framework)
- **Database**: SQLite (upgradeable to PostgreSQL)
- **API**: Django REST Framework
- **Frontend**: Django templates with Tailwind CSS framework
- **Authentication**: Django built-in auth with JWT support
- **File Storage**: Local filesystem with cloud storage capability

## Project Structure

```
OBC-system/
├── src/                    # Django source code
│   ├── obc_management/     # Project settings and URLs
│   ├── common/             # Shared models, forms, and services
│   ├── communities/        # OBC community management
│   ├── coordination/       # Stakeholder coordination
│   ├── mana/               # Mapping and Needs Assessment
│   ├── monitoring/         # Monitoring & evaluation workflows
│   ├── recommendations/    # Recommendations namespace (policies, tracking, docs)
│   ├── templates/          # Project-level templates grouped by app
│   └── static/             # Static assets grouped by app
├── var/                    # Runtime artefacts (SQLite, logs, media)
├── requirements/           # Python dependency locks
├── scripts/                # Project scripts
├── docs/                   # Documentation
└── venv/                   # Local virtual environment
```

## Quick Start

### Prerequisites

- Python 3.12 (see `.python-version`)
- pip (Python package manager)
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd OBC-system
   ```

2. **Create and activate virtual environment**
   ```bash
   ./scripts/bootstrap_venv.sh       # idempotent helper (macOS/Linux)
   source venv/bin/activate          # On Windows: venv\Scripts\activate
   ```
   > Prefer to do it manually? Use `python3.12 -m venv venv` to ensure the interpreter matches the pinned version.

3. **Install dependencies**
   ```bash
   pip install -r requirements/development.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env file with your configuration
   ```

5. **Run database migrations**
   ```bash
   cd src
   ./manage.py migrate
   ```

6. **Create a superuser (optional)**
   ```bash
   ./manage.py createsuperuser
   ```

7. **Start the development server**
   ```bash
   ./manage.py runserver
   ```

The application will be available at `http://localhost:8000`

Runtime data (SQLite database, uploads, and logs) is stored under `var/` so the Django project tree stays focused on code.

## Core Modules

### 1. Communities Module
- **Purpose**: Comprehensive OBC information management
- **Features**: Community profiles, demographic data, stakeholder management, document management

### 2. MANA Module
- **Purpose**: Mapping and Needs Assessment capabilities
- **Features**: Assessment management, needs categorization, priority ranking, baseline studies

### 3. Coordination Module
- **Purpose**: Multi-stakeholder coordination
- **Features**: Stakeholder directory, meeting management, MOA tracking, communication hub

### 4. Recommendations Module
- **Purpose**: Evidence-based policy, program, and service recommendations
- **Features**: Recommendation tracking, approval workflows, knowledge/document repository, impact assessment

### 5. Monitoring & Evaluation Module
- **Purpose**: Track implementation and outcomes of OOBC initiatives
- **Features**: Monitoring entries, update workflows, performance dashboards, evidence attachments

## Development

Templates live in `src/templates/<app>/` and static assets in `src/static/<app>/`, keeping UI files alongside their Django apps.

### Code Style

The project uses:
- **Black** for code formatting
- **isort** for import sorting
- **flake8** for linting

Run formatting and linting:
```bash
black .
isort .
flake8
```

### Testing

Run tests:
```bash
pytest
```

Run tests with coverage:
```bash
coverage run -m pytest
coverage report
```

Each Django app stores its test suite inside `src/<app>/tests/` to keep scenarios close to the code they cover.

### API Documentation

When the server is running, API documentation is available at:
- Browsable API: `http://localhost:8000/api/`
- Admin interface: `http://localhost:8000/admin/`

## Deployment

### Docker Production Deployment

The system is production-ready with Docker and supports deployment to:
- **Coolify** (recommended for single-server deployments)
- **Docker Compose** (generic deployment)
- **Kubernetes** (requires S3 storage - see scaling guide)

**Quick Deploy with Docker:**
```bash
# Copy and configure environment
cp .env.example .env.prod
nano .env.prod  # Edit with production values

# Deploy with Docker Compose
docker-compose -f docker-compose.prod.yml up -d

# Verify health
curl http://localhost:8000/health/
```

For detailed deployment instructions, see:
- **[Production Deployment Guide](docs/deployment/production-deployment-issues-resolution.md)**
- **[Deployment Status](docs/deployment/DEPLOYMENT_IMPLEMENTATION_STATUS.md)**

### Environment Variables

Key environment variables for production:

```env
# Django Core (REQUIRED)
DJANGO_SETTINGS_MODULE=obc_management.settings.production
SECRET_KEY=your-production-secret-key-minimum-50-characters
DEBUG=0
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
CSRF_TRUSTED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Database (REQUIRED)
DATABASE_URL=postgres://user:password@host:port/database

# Redis/Celery (REQUIRED)
REDIS_URL=redis://host:port/0
CELERY_BROKER_URL=redis://host:port/0

# Email (REQUIRED for production)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=1
EMAIL_HOST_USER=noreply@yourdomain.com
EMAIL_HOST_PASSWORD=your-email-app-password

# Gunicorn Tuning (Optional)
GUNICORN_WORKERS=4  # Formula: (2 × CPU cores) + 1
GUNICORN_THREADS=2
GUNICORN_LOG_LEVEL=info
```

### Production Checklist

Before deploying to production, ensure:

**Security:**
- [ ] Set `DEBUG=0` (False)
- [ ] Generate strong `SECRET_KEY` (50+ characters)
- [ ] Configure `ALLOWED_HOSTS` with actual domain(s)
- [ ] Set `CSRF_TRUSTED_ORIGINS` with `https://` scheme
- [ ] Run `python manage.py check --deploy` with zero errors

**Infrastructure:**
- [ ] Configure production database (PostgreSQL 15+ required)
- [ ] Set up Redis for Celery background tasks
- [ ] Configure email backend (not console)
- [ ] Set up SSL/TLS certificates
- [ ] Configure health check endpoints (`/health/`, `/ready/`)

**Operations:**
- [ ] Configure logging (stdout/stderr for Docker)
- [ ] Set up database backup strategy
- [ ] Set up media file backup strategy (Docker volumes)
- [ ] Configure monitoring/alerting

**Testing:**
- [ ] Verify static files load (`/static/admin/css/base.css`)
- [ ] Test file uploads work
- [ ] Verify CSRF protection on forms
- [ ] Test Celery tasks execute
- [ ] Run smoke tests on critical workflows

## 📈 Scaling Considerations

### Current Architecture: Single-Server Deployment

**Media Storage:** Docker volumes (filesystem storage)

This setup is production-ready for:
- ✅ Government agencies with regional deployment
- ✅ Up to 10,000 concurrent users
- ✅ Up to 100GB media files
- ✅ Single Coolify/Docker host deployments

**Advantages:**
- Simple architecture with no external dependencies
- Zero cloud storage costs
- Fast local file access
- Easy to backup and restore

**Limitations:**
- Cannot horizontally scale web service (max 1 replica)
- Limited to single-server disk capacity
- No built-in CDN for global distribution

### Future Scaling: Multi-Server Deployment

**When you need to scale** (multiple web replicas, Kubernetes, high availability):

📚 **See:** [Migrating to S3 Storage](docs/deployment/s3-migration-guide.md)

You should implement S3 storage when:
- Traffic requires multiple web server replicas (>1000 concurrent users)
- Deploying to Kubernetes or container orchestration platforms
- Media storage exceeds 100GB or server disk capacity
- Need CDN for global file distribution
- Require zero-maintenance cloud backups

**Migration Path:** Filesystem → S3 can be done with zero downtime. All implementation details, code changes, and step-by-step migration instructions are documented in the scaling guide.

**Estimated Migration Effort:** 4-6 hours (includes testing)

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is developed for the Office for Other Bangsamoro Communities (OOBC) under the Bangsamoro Autonomous Region in Muslim Mindanao (BARMM).

## Support

For support and questions, please contact the OOBC development team.

---

**BANGSAMORO KA, SAAN KA MAN!** 
*(You are Bangsamoro, wherever you are!)*

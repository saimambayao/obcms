# OBC Management System

**Other Bangsamoro Communities Management System**

A comprehensive web-based platform that supports the Office for Other Bangsamoro Communities (OOBC) in serving Other Bangsamoro Communities (OBCs) outside the Bangsamoro Autonomous Region in Muslim Mindanao (BARMM). OBCMS unifies program management, community engagement, evidence tracking, and AI-assisted insights in one cohesive ecosystem.

## Recent Updates

- **Unified WorkItem Model | PRIORITY: CRITICAL | Complexity: Complex** - All work tracking now runs on the consolidated `WorkItem` hierarchy. Legacy `StaffTask`, `Event`, and `ProjectWorkflow` models have been fully retired. Migration details live in [src/STAFFTASK_TO_WORKITEM_MIGRATION_COMPLETE.md](src/STAFFTASK_TO_WORKITEM_MIGRATION_COMPLETE.md) with implementation examples in [docs/refactor/WORK_ITEM_IMPLEMENTATION_EXAMPLES.md](docs/refactor/WORK_ITEM_IMPLEMENTATION_EXAMPLES.md).
- **AI Query Intelligence Expansion | PRIORITY: HIGH | Complexity: Complex** - The AI Assistant now ships with comprehensive geographic, temporal, and cross-domain query packs powering 300+ natural language insights. See [WORKSTREAM6_NEW_QUERY_CATEGORIES_COMPLETE.md](WORKSTREAM6_NEW_QUERY_CATEGORIES_COMPLETE.md), [WORKSTREAM_4_GEOGRAPHIC_TEMPLATES_COMPLETE.md](WORKSTREAM_4_GEOGRAPHIC_TEMPLATES_COMPLETE.md), and [WORKSTREAM_3_QUICK_WINS_COMPLETE.md](WORKSTREAM_3_QUICK_WINS_COMPLETE.md).
- **Instant UI & HTMX Rollout | PRIORITY: HIGH | Complexity: Moderate** - Live updates, optimistic interactions, and animation standards are active across kanban boards, tables, and modals. Guidance: [docs/improvements/instant_ui_improvements_plan.md](docs/improvements/instant_ui_improvements_plan.md).
- **UI Component System Stabilized | PRIORITY: HIGH | Complexity: Moderate** - Forms, stat cards, and data tables follow the 3D Milk White design language with reusable templates. Reference [docs/ui/OBCMS_UI_COMPONENTS_STANDARDS.md](docs/ui/OBCMS_UI_COMPONENTS_STANDARDS.md) and associated component guides.
- **PostgreSQL + S3 Production Path | PRIORITY: HIGH | Complexity: Moderate** - Production deployments now include hardened PostgreSQL migration playbooks, AI Ops dashboards, and S3 storage pathways. Start with [docs/deployment/POSTGRESQL_MIGRATION_REVIEW.md](docs/deployment/POSTGRESQL_MIGRATION_REVIEW.md) and [docs/deployment/AI_DEPLOYMENT_GUIDE.md](docs/deployment/AI_DEPLOYMENT_GUIDE.md).

## Project Overview

OBCMS digitalizes OOBC's core mandates:
- Gathering comprehensive intelligence on OBC communities
- Assessing needs and translating them into programs, policies, and services
- Coordinating interventions with partner agencies and stakeholders
- Monitoring implementation progress and outcomes
- Delivering instant, AI-assisted decision support for staff and leadership

## Key Capabilities

### Work Management & Delivery
- Unified `WorkItem` hierarchy with task, activity, project, and initiative tracking
- Planning & Budgeting dashboards in `project_central` for program pipelines and prioritization
- Audit trails, document attachments, and progress analytics integrated with WorkItems

### Communities & MANA Intelligence
- Comprehensive community profiles, demographics, and geo-tagged information
- Needs assessments, prioritization matrices, and baseline studies via the `mana` module
- Geographic intelligence (region -> province -> municipality -> barangay) powered by curated AI query templates

### Stakeholder Coordination & Policy Intelligence
- Stakeholder directories, meeting logs, and MOA tracking within `coordination`
- Policy pipelines, evidence linkages, and monitoring of recommendations through `recommendations` and `policy_tracking`

### Monitoring & Evaluation
- Performance dashboards, scenario planning, and compliance checks under `monitoring`
- Exports, analytics utilities, and Celery-backed background tasks (`src/monitoring/services`)

### Conversational AI Assistant
- Embedded AI Assistant with cultural context safeguards (`src/ai_assistant`)
- 300+ curated query templates across temporal, geographic, and cross-domain domains in `src/common/ai_services/chat/query_templates/`
- User-facing guidance: [docs/USER_GUIDE_AI_CHAT.md](docs/USER_GUIDE_AI_CHAT.md) and implementation notes in [docs/ai/AI_CHAT_IMPLEMENTATION_SUMMARY.md](docs/ai/AI_CHAT_IMPLEMENTATION_SUMMARY.md)

## Technology Stack

- **Backend**: Django 4.2+, Django REST Framework, Celery
- **Database**: SQLite for development, PostgreSQL for production (via `DATABASE_URL`)
- **Frontend**: Django templates, Tailwind CSS, Alpine.js, HTMX for instant UI interactions
- **Background & Realtime**: Redis-backed Celery workers, task queues integrated with WorkItems
- **AI & Search**: Vectorized document embeddings and query templates optimized for the OBCMS AI Assistant
- **Authentication**: Django auth + JWT support for API access
- **Storage**: Local filesystem by default with S3-compatible support (production)

## Project Structure

```
obcms/
|- src/
|  |- obc_management/     # Django settings, URLs, ASGI/WSGI
|  |- common/             # Shared utilities, enums, AI helpers, form styles
|  |- communities/        # Community profiles, demographics, documents
|  |- coordination/       # Stakeholder coordination workflows
|  |- mana/               # Mapping and Needs Assessment tooling
|  |- monitoring/         # Monitoring and evaluation analytics
|  |- project_central/    # Planning, budgeting, dashboards, WorkItem views
|  |- recommendations/    # Policy, program, and document tracking
|  |- policy_tracking/    # Supplemental policy intelligence services
|  |- ai_assistant/       # Conversational AI assistant modules
|  |- api/                # API routers, serializers, integration points
|  |- templates/          # Shared and app-specific templates
|  |- static/             # Compiled Tailwind assets
|  |- services/           # Cross-cutting domain services and schedulers
|- docs/                   # Standards, deployment guides, plans, and reports
|- deployment/             # Infrastructure manifests and ops tooling
|- scripts/                # Bootstrap, migration, and maintenance scripts
|- requirements/           # Dependency lock files
|- var/                    # Runtime artifacts (SQLite, logs, media uploads)
```

## Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd obcms
   ```
2. **Create and activate the virtual environment**
   ```bash
   ./scripts/bootstrap_venv.sh
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```
3. **Install dependencies**
   ```bash
   pip install -r requirements/development.txt
   ```
4. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Fill in database, Redis, email, and AI credentials
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
The app runs at `http://localhost:8000`. Runtime data (SQLite, uploads, logs) lives under `var/`.

## Development Workflow

### Code Style & Tooling
- Formatters and linters: `black src`, `isort src`, `flake8 src`
- Tailwind build pipeline configured via `postcss.config.js` and `tailwind.config.js`
- Commit messages use imperative, capitalized subjects without trailing periods

### Testing
- Full suite: `pytest --ds=obc_management.settings`
- Focused runs: `pytest --ds=obc_management.settings -k "<pattern>"`
- Coverage: `coverage run -m pytest --ds=obc_management.settings && coverage report`
- Place tests alongside apps (`src/<app>/tests/`)

### Local Data Protection
- Do **not** delete `src/db.sqlite3` or backups under `var/`
- Use migrations to evolve the schema (`./manage.py migrate`)
- For data resets, coordinate through migration scripts rather than removing databases

## Documentation & Standards

- All documentation resides under `docs/` and is indexed in [docs/README.md](docs/README.md)
- UI patterns follow [docs/ui/OBCMS_UI_COMPONENTS_STANDARDS.md](docs/ui/OBCMS_UI_COMPONENTS_STANDARDS.md)
- Instant UI guidance and HTMX targets: [docs/improvements/instant_ui_improvements_plan.md](docs/improvements/instant_ui_improvements_plan.md)
- AI usage, prompts, and testing: [docs/USER_GUIDE_AI_CHAT.md](docs/USER_GUIDE_AI_CHAT.md) and [docs/ai/AI_CHAT_IMPLEMENTATION_SUMMARY.md](docs/ai/AI_CHAT_IMPLEMENTATION_SUMMARY.md)

## AI Assistant & Query Intelligence

- Query templates are organized in `src/common/ai_services/chat/query_templates/` covering geographic, temporal, budget, workload, and cross-domain scenarios
- Expansion milestones: [QUERY_EXPANSION_IMPLEMENTATION_COMPLETE.md](QUERY_EXPANSION_IMPLEMENTATION_COMPLETE.md) and [QUERY_TEMPLATE_EXPANSION_PHASE_4-6_COMPLETE.md](QUERY_TEMPLATE_EXPANSION_PHASE_4-6_COMPLETE.md)
- User workflow guides, accessibility requirements, and regression suites live in `docs/testing/AI_*` and `docs/ui/AI_*`
- AI operations dashboards and deployment guardrails: [docs/deployment/AI_DEPLOYMENT_GUIDE.md](docs/deployment/AI_DEPLOYMENT_GUIDE.md)

## Instant UI & UX Standards

- Use HTMX with `hx-swap="outerHTML swap:300ms"` patterns for smooth transitions
- Shared form components: `src/templates/components/form_field_*.html`
- Tailwind styling helpers applied via `_apply_form_field_styles` utilities in `src/common/forms/`
- Reference implementations: `src/templates/communities/provincial_manage.html` and the stat card templates documented in [docs/improvements/UI/STATCARD_TEMPLATE.md](docs/improvements/UI/STATCARD_TEMPLATE.md)

## Deployment

### Docker Production Deployment

The repository includes `docker-compose.prod.yml`, Gunicorn/NGINX configs, and environment templates for containerized deployments.

```bash
# Copy configuration
cp .env.example .env.prod
# Edit .env.prod with production credentials

# Launch services
docker-compose -f docker-compose.prod.yml up -d

# Health checks
curl http://localhost:8000/health/
```

Detailed runbooks:
- [docs/deployment/production-deployment-issues-resolution.md](docs/deployment/production-deployment-issues-resolution.md)
- [docs/deployment/DEPLOYMENT_IMPLEMENTATION_STATUS.md](docs/deployment/DEPLOYMENT_IMPLEMENTATION_STATUS.md)
- [docs/deployment/POSTGRESQL_MIGRATION_REVIEW.md](docs/deployment/POSTGRESQL_MIGRATION_REVIEW.md)

### Environment Variables

```env
# Django core
DJANGO_SETTINGS_MODULE=obc_management.settings.production
SECRET_KEY=your-production-secret-key-minimum-50-characters
DEBUG=0
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
CSRF_TRUSTED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Database
DATABASE_URL=postgres://user:password@host:port/database

# Redis / Celery
REDIS_URL=redis://host:port/0
CELERY_BROKER_URL=redis://host:port/0

# Email
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=1
EMAIL_HOST_USER=noreply@yourdomain.com
EMAIL_HOST_PASSWORD=your-email-app-password

# Gunicorn tuning (optional)
GUNICORN_WORKERS=4  # Formula: (2 * CPU cores) + 1
GUNICORN_THREADS=2
GUNICORN_LOG_LEVEL=info
```

### Production Checklist

**Security**
- [ ] `DEBUG=0`
- [ ] Strong `SECRET_KEY` (50+ characters)
- [ ] `ALLOWED_HOSTS` and `CSRF_TRUSTED_ORIGINS` populated
- [ ] `python manage.py check --deploy` passes

**Infrastructure**
- [ ] PostgreSQL database configured and reachable
- [ ] Redis available for Celery queues
- [ ] Outbound email provider configured
- [ ] SSL/TLS certificates installed
- [ ] `/health/` and `/ready/` endpoints monitored

**Operations**
- [ ] Structured logging routed to stdout/stderr for containers
- [ ] Automated database backups scheduled
- [ ] Media storage backup strategy in place (S3 or volume snapshots)
- [ ] Monitoring and alerting connected to ops channels

**Testing**
- [ ] Static files collected (`./manage.py collectstatic`)
- [ ] File uploads verified
- [ ] CSRF-protected forms exercised
- [ ] Celery task execution validated
- [ ] Critical workflows smoke-tested (communities, assessments, policy approvals)

## Scaling Strategy

- **Current Deployment | PRIORITY: HIGH | Complexity: Moderate** - Single-server Docker/Coolify stack using local volumes for media storage. Fits regional deployments with up to five WorkItem-heavy teams per site.
- **Scale-Out Path | PRIORITY: HIGH | Complexity: Complex** - Migrate media to S3-compatible storage, enable multiple web replicas, and integrate CDN coverage following [docs/deployment/s3-migration-guide.md](docs/deployment/s3-migration-guide.md). Ensure PostgreSQL high availability and Redis clustering before enabling horizontal scaling.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit with an imperative, capitalized message (`git commit -m "Add Amazing Feature"`)
4. Push the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request referencing relevant docs/tests and attach UI screenshots when templates change

## License

Developed for the Office for Other Bangsamoro Communities (OOBC) under the Bangsamoro Autonomous Region in Muslim Mindanao (BARMM). Internal use only unless otherwise agreed.

## Support

For assistance, reach out to the OOBC development team or consult the documentation index in `docs/README.md`.

---

**BANGSAMORO KA, SAAN KA MAN!**  
*(You are Bangsamoro, wherever you are!)*

# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Time Estimates Policy

**NEVER provide time estimates in hours, days, weeks, or months for implementation tasks.**

With powerful AI coding agents, a year's worth of traditional development work can be completed in a single day. Time estimates create false constraints and are obsolete in AI-assisted development.

**This applies to:**
- ❌ Conversational responses: "This will take 8 hours"
- ❌ Documentation files: "Week 1-2: Implement feature"
- ❌ Phase headers: "Phase 1 (Week 1-2)" or "Phase 2 (Days 3-5)"
- ❌ Implementation plans: Any timeline labels, week ranges, or date estimates
- ❌ Roadmaps: "Q1 2024", "Month 1", "Sprint 1-2"

**Instead, focus on:**
- **Priority**: CRITICAL, HIGH, MEDIUM, or LOW (all caps in phase headers)
- **Complexity**: Simple, Moderate, or Complex
- **Dependencies**: What must be done before this task (e.g., "Requires dashboard metrics view")
- **Prerequisites**: What needs to exist first (e.g., "Model must exist", "API endpoint required")

**Examples:**
- ❌ Bad: "This will take 8 hours to implement"
- ❌ Bad: "Week 1, Days 2-3: Enhanced dashboard"
- ❌ Bad: "Phase 1 (Week 1-2): Hero Sections"
- ❌ Bad: "Estimated Effort: 2-3 days"
- ✅ Good: "Phase 1 | PRIORITY: CRITICAL"
- ✅ Good: "Priority: HIGH | Complexity: Moderate | Requires: dashboard_metrics view"
- ✅ Good: "Dependencies: Dashboard metrics view must exist first"
- ✅ Good: "Prerequisites: Fix task deletion bug (dependency)"

**Critical:** This policy applies to ALL documentation files under `docs/`, including implementation plans, feature specifications, and phased rollout plans. Never use week ranges, day counts, hour estimates, or any time-based labels.

## Development Environment Setup

**Virtual Environment**: Always work from Python 3.12 `venv/`
```bash
./scripts/bootstrap_venv.sh  # idempotent helper
source venv/bin/activate     # On Windows: venv\Scripts\activate
```

**Working Directory**: All Django commands must be run from the `src/` directory
```bash
cd src
./manage.py [command]
```

## Common Development Commands

### Database Operations

**⚠️ CRITICAL WARNING: NEVER DELETE THE DATABASE ⚠️**

**NEVER run `rm db.sqlite3` or delete the database file.** This database contains valuable development data, user accounts, and test data that are essential for ongoing development. Always apply migrations to the existing database using `./manage.py migrate`.

If you encounter migration issues:
1. **DO NOT delete the database**
2. Fix migration conflicts properly using Django migration tools
3. Use `./manage.py migrate --fake` if needed
4. Ask the user before taking any destructive action

```bash
cd src
./manage.py makemigrations
./manage.py migrate  # Apply migrations to EXISTING database
./manage.py createsuperuser
```

### Development Server
```bash
cd src
./manage.py runserver
# Server runs at http://localhost:8000
# Admin interface: http://localhost:8000/admin/
```

### Code Quality and Testing
```bash
# Code formatting and linting
black .
isort .
flake8

# Testing
pytest
coverage run -m pytest
coverage report
```

### Dependencies
```bash
# Install development dependencies
pip install -r requirements/development.txt

# Install production dependencies only
pip install -r requirements/base.txt
```

## Architecture Overview

### Django Project Structure
- **Main Project**: `src/obc_management/` - Django settings and main configuration
- **Applications**: Each module is a separate Django app with models, views, admin, and migrations; Modules are Mapping and Needs Assesment (MANA), Coordination, Recommendations, M&E (including the Projects, Programs, and Activities or PPAs of the different Ministries, Offices, and Agencies or MOAs)
- **Environment**: Uses `django-environ` for environment variable management with `.env` file

### Core Applications
1. **common**: Base models, utilities, and shared functionality
2. **communities**: OBC (Other Bangsamoro Communities) profile and demographic management
3. **mana**: Mapping and Needs Assessment functionality 
4. **coordination**: Multi-stakeholder coordination and partnership management
5. **policies**: Policy recommendation tracking and evidence-based proposals

### Key Technical Components
- **Authentication**: Django built-in auth + JWT (SimpleJWT) for API access
- **API**: Django REST Framework with pagination, filtering, and browsable interface
- **Database**: SQLite for development, configurable for PostgreSQL production
- **Background Tasks**: Celery with Redis broker for async operations
- **Logging**: File and console logging configured, logs written to `src/logs/`

## Domain-Specific Context

### OOBC Mission
This system supports the Office for Other Bangsamoro Communities (OOBC) serving Bangsamoro communities outside BARMM (Bangsamoro Autonomous Region in Muslim Mindanao). 

### Geographic Scope
- Primary focus: Regions IX (Zamboanga Peninsula), Region X (Northern Mindanao), Region XI (Davao Region), and XII (SOCCSKSARGEN)
- Administrative hierarchy: Region > Province > Municipality/City > Barangay
- Timezone: Asia/Manila

## Environment Configuration

### Required Environment Variables
```env
SECRET_KEY=your-secret-key
DEBUG=True/False
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///path/to/db (or postgres://...)
REDIS_URL=redis://localhost:6379/0
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

### Settings Configuration
- **Debug Toolbar**: Automatically enabled in DEBUG mode
- **CORS**: Configured for localhost development
- **JWT**: 1-hour access tokens, 7-day refresh tokens
- **Pagination**: 20 items per page default

### Static Files Configuration
- **Location**: All static files are in `src/static/` (centralized approach)
- **Configuration**: `STATICFILES_DIRS = [BASE_DIR.parent / "static"]` points to `src/static/`
- **Structure**:
  - `src/static/common/` - Common app assets (CSS, JS, vendor/fullcalendar)
  - `src/static/vendor/` - Shared vendor libraries (Leaflet, localforage, idb)
  - `src/static/admin/` - Admin interface customizations
- **Important**: Server restart required after modifying `STATICFILES_DIRS`
- **See**: [docs/development/README.md](docs/development/README.md#static-files-architecture) for complete documentation

## Development Guidelines

### Model Relationships
- Use timezone-aware datetime fields (`USE_TZ = True`)
- Follow Django naming conventions for models and fields
- Implement proper `__str__` methods for admin interface
- Use foreign keys and many-to-many relationships appropriately for stakeholder connections

### API Development
- All APIs require authentication by default
- Use DRF filtering, searching, and ordering
- Implement proper serializers with validation
- Follow REST principles for URL patterns

### Frontend Integration
- Templates in `src/templates/` with Django template language
- Static files in `src/static/` served during development
- Uses Tailwind CSS for responsive, government-appropriate styling
- Support for dark mode and accessibility (WCAG 2.1 AA)

### UI Components & Standards ⭐

**CRITICAL**: All UI components MUST follow the official OBCMS UI standards documented in:

**📚 [OBCMS UI Components & Standards Guide](docs/ui/OBCMS_UI_COMPONENTS_STANDARDS.md)**

This comprehensive guide includes:

#### 1. **Stat Cards (3D Milk White)** ✅ Official Design
- **Simple variant**: No breakdown section
- **Breakdown variant**: 3-column breakdown with bottom alignment
- **Semantic icon colors**: Amber (total), Emerald (success), Blue (info), Purple (draft), Orange (warning), Red (critical)
- **Reference**: [STATCARD_TEMPLATE.md](docs/improvements/UI/STATCARD_TEMPLATE.md)
- **Implementation**: 100% complete across all dashboards

#### 2. **Quick Action Cards**
- Used in management dashboards for common workflows
- Gradient icon containers with hover effects
- Clear call-to-action with arrow indicators

#### 3. **Form Components**
- **Standard dropdown**: `rounded-xl`, emerald focus ring, chevron icon
- **Text inputs**: `min-h-[48px]` for accessibility
- **Radio cards**: Card-based selection with emerald border when selected
- **Checkboxes**: Standard checkboxes with proper spacing

#### 4. **Buttons**
- **Primary**: Blue-to-teal gradient for main actions
- **Secondary**: Outline buttons for cancel/back
- **Tertiary**: Text-only buttons for inline actions
- **Icon buttons**: Circular icon-only buttons

#### 5. **Cards & Containers**
- **White cards**: `rounded-xl`, border, subtle shadow
- **Card with footer**: Action buttons in gray footer section
- **Section containers**: Form sections with icon headers

#### 6. **Navigation**
- **Breadcrumbs**: Chevron-separated path
- **Tabs**: Bottom-border active state
- **Pagination**: Numbered pages with prev/next

#### 7. **Alerts & Messages**
- **Success**: Emerald border-left with icon
- **Error**: Red border-left with icon
- **Warning**: Amber border-left with icon
- **Info**: Blue border-left with icon

#### 8. **Tables**
- **Header**: Blue-to-teal gradient
- **Rows**: Hover state, alternating if needed
- **Status badges**: Rounded-full pills with semantic colors

#### 9. **Accessibility**
- WCAG 2.1 AA compliant
- High contrast ratios (4.5:1 minimum)
- Keyboard navigation support
- Touch targets minimum 48px
- Focus indicators on all interactive elements

**When creating or modifying UI:**
1. ✅ **Always check** the UI Components guide first
2. ✅ **Copy from** existing reference templates
3. ✅ **Follow** semantic color guidelines
4. ✅ **Test** on mobile, tablet, desktop
5. ✅ **Verify** accessibility compliance

### Form Component Library
- Reusable form partials are under `src/templates/components/` (`form_field.html`, `form_field_input.html`, `form_field_select.html`).
- Include them in templates instead of duplicating markup, e.g. `{% include "components/form_field_select.html" with field=form.municipality placeholder="Select municipality..." %}` to match the Barangay OBC dropdown styling.
- Widget classes are centralised via `_apply_form_field_styles` (see `src/common/forms/staff.py`); extend there when new input patterns are needed.

### Form Design Standards
**IMPORTANT**: When designing or modifying forms, ALWAYS reference existing templates for UI/UX consistency:
- **Review similar forms** in `src/templates/` to understand established patterns
- **Use component templates** (`src/templates/components/`) for standard form elements
- **Follow dropdown styling**: Use `rounded-xl`, `border-gray-200`, emerald focus rings, chevron icons
- **Standard dropdown pattern**:
  ```html
  <div class="space-y-1">
      <label for="field-id" class="block text-sm font-medium text-gray-700 mb-2">
          Field Label<span class="text-red-500">*</span>
      </label>
      <div class="relative">
          <select id="field-id" name="field_name" class="block w-full py-3 px-4 text-base rounded-xl border border-gray-200 shadow-sm focus:ring-emerald-500 focus:border-emerald-500 min-h-[48px] appearance-none pr-12 bg-white transition-all duration-200">
              <option value="">Select...</option>
          </select>
          <span class="pointer-events-none absolute inset-y-0 right-0 flex items-center pr-4">
              <i class="fas fa-chevron-down text-gray-400 text-sm"></i>
          </span>
      </div>
  </div>
  ```
- **Check reference templates**: `src/templates/communities/provincial_manage.html`, `src/templates/components/form_field_select.html`
- **Maintain consistency** in spacing, colors, borders, and interactive states across all forms

### Data Table Cards
- Directory/list pages should extend `components/data_table_card.html` so Barangay and Municipal OBC lists stay visually aligned.
- Pass a `headers` array and `rows` data with `view_url`, `edit_url`, and `delete_preview_url`. The component already handles the action buttons and the two-step delete confirmation (confirm dialog → redirect to detail for "Review before deletion").

## Instant UI & Smooth User Experience

### Priority: Always Implement Instant UI Updates
When working on this codebase, **always prioritize instant UI responses** and smooth interactions. Users expect modern web app behavior - no full page reloads, immediate feedback, and seamless transitions.

### HTMX Implementation Requirements
- **Consistent Targeting**: All interactive elements must use `data-task-id="{{ item.id }}"` for both kanban cards and table rows
- **Optimistic Updates**: Update the UI immediately when user performs an action, then handle server response
- **Smooth Animations**: Use `hx-swap="outerHTML swap:300ms"` or `delete swap:200ms` for transitions
- **Loading Indicators**: Always show spinners, disabled states, or progress feedback during operations

### Backend Response Standards
All views handling HTMX requests must follow this pattern:
```python
def task_operation_view(request, task_id):
    # ... perform operation ...

    if request.headers.get('HX-Request'):
        return HttpResponse(
            status=204,
            headers={
                'HX-Trigger': json.dumps({
                    'task-updated': {'id': task_id, 'action': 'delete'},
                    'show-toast': 'Task updated successfully',
                    'refresh-counters': True
                })
            }
        )
```

### UI Animation Standards
- **Task Movements**: 300ms smooth transitions between kanban columns
- **Modal Interactions**: Fade with scale transform for open/close
- **Button Feedback**: Immediate visual response to clicks (color change, disable state)
- **Error Handling**: Clear error states with recovery options, no silent failures

### Critical: Never Use Full Page Reloads
- Implement HTMX for all CRUD operations (Create, Read, Update, Delete)
- Use out-of-band swaps (`hx-swap-oob`) for updating multiple UI regions simultaneously
- Provide graceful fallback mechanisms when HTMX fails
- Maintain accessibility with proper ARIA live regions and state updates

### Current Issue to Fix
**Known Bug**: Task deletion in kanban view (`/oobc-management/staff/tasks/`) doesn't remove cards instantly. The modal targets `[data-task-row]` but kanban uses `[data-task-id]`. This must be fixed to ensure instant UI updates.

For detailed implementation guidance, refer to `docs/improvements/instant_ui_improvements_plan.md`.

## Documentation Guidelines

### Where to Write Documentation

**CRITICAL: All documentation files MUST be placed under the `docs/` directory.**

#### Documentation Organization Structure
```
docs/
├── deployment/          # Deployment guides, production setup
├── development/         # Development guidelines (NOT AI config)
├── testing/            # Testing guides, verification reports
├── reference/          # Technical reference (coordinates, standards)
├── improvements/       # Implementation tracking, improvement plans
├── guidelines/         # Program guidelines (MANA, policies)
├── product/           # Product roadmap, architecture
├── reports/           # Research, analysis reports
├── env/               # Environment-specific configs
├── admin-guide/       # Admin operations
└── ui/                # UI/UX documentation
```

#### Documentation Rules

1. **NEVER create documentation in project root**
   - ❌ Wrong: `NEW_FEATURE_GUIDE.md` in root
   - ✅ Correct: `docs/development/NEW_FEATURE_GUIDE.md`

2. **Choose the appropriate category:**
   - Implementation tracking → `docs/improvements/`
   - Deployment instructions → `docs/deployment/`
   - Testing procedures → `docs/testing/`
   - User guides → `docs/guidelines/`
   - Technical specs → `docs/reference/`

3. **Update the main index:**
   - After creating new docs, add them to `docs/README.md`
   - Include in the appropriate category section

4. **Use relative links:**
   - Within docs/: `[link](../other-category/file.md)`
   - From root to docs: `[link](docs/category/file.md)`

#### Configuration Files vs Documentation

**Configuration files stay in ROOT:**
- ✅ `CLAUDE.md` - AI configuration (ROOT)
- ✅ `GEMINI.md` - AI configuration (ROOT)
- ✅ `AGENTS.md` - AI configuration (ROOT)
- ✅ `README.md` - Project overview (ROOT)
- ✅ `.env.example` - Environment template (ROOT)

**Documentation files go in docs/:**
- ✅ `docs/development/README.md` - Development guide
- ✅ `docs/deployment/production-guide.md` - Deployment docs
- ✅ `docs/improvements/feature-plan.md` - Implementation plans

#### Example: Creating New Documentation

When implementing a new feature:

```bash
# ❌ WRONG - Don't create in root
echo "# New Feature" > AWESOME_FEATURE.md

# ✅ CORRECT - Create in appropriate docs/ subdirectory
echo "# New Feature" > docs/improvements/awesome_feature_implementation.md

# Update the index
# Add entry to docs/README.md under appropriate section
```

### Documentation Checklist

When creating or updating documentation:
- [ ] File is in appropriate `docs/` subdirectory
- [ ] Added to `docs/README.md` index
- [ ] Uses relative links correctly
- [ ] Follows naming convention (lowercase, underscores)
- [ ] Includes metadata (date, status, author if applicable)

**Reference:** See [docs/DOCUMENTATION_ORGANIZATION.md](docs/DOCUMENTATION_ORGANIZATION.md) for organization details.

---

## Production Deployment Guidelines

### ⚠️ CRITICAL: Pre-Deployment Checklist

**Before deploying OBCMS to staging or production, ALL of the following documents MUST be reviewed:**

#### 1. **Database Migration (CRITICAL - START HERE)**

**Primary Documents:**
- 📚 **[PostgreSQL Migration Summary](docs/deployment/POSTGRESQL_MIGRATION_SUMMARY.md)** ⭐ **READ FIRST**
  - Executive overview of entire migration process
  - Complete readiness checklist
  - Key decisions documented
  - Migration procedure summary

- 📚 **[PostgreSQL Migration Review](docs/deployment/POSTGRESQL_MIGRATION_REVIEW.md)** ⭐ **TECHNICAL DETAILS**
  - Comprehensive technical analysis of all 118 migrations
  - Step-by-step migration procedure
  - Performance expectations
  - Rollback procedures

**CRITICAL CONSIDERATIONS:**

**A. Geographic Data Implementation** ✅ **NO POSTGIS REQUIRED**
- 📚 **[Geographic Data Implementation Guide](docs/improvements/geography/GEOGRAPHIC_DATA_IMPLEMENTATION.md)**
  - **Decision:** Use JSONField (NOT PostGIS)
  - **Reason:** Production-ready, sufficient for OBCMS, no extra dependencies
  - Current implementation stores boundaries in GeoJSON format using PostgreSQL's native `jsonb` type
  - Perfect for Leaflet.js frontend integration
  - PostGIS adds complexity without benefit for current use case

- 📚 **[PostGIS Migration Guide](docs/improvements/geography/POSTGIS_MIGRATION_GUIDE.md)** (Reference only - NOT needed)
  - Only consider PostGIS if spatial queries become required
  - Migration guide available for future use

**B. Text Search Queries** ✅ **100% COMPATIBLE**
- 📚 **[Case-Sensitive Query Audit](docs/deployment/CASE_SENSITIVE_QUERY_AUDIT.md)**
  - Full codebase audit completed
  - **Result:** 0 case-sensitive queries in production code
  - All user-facing searches use `__icontains` (case-insensitive)
  - PostgreSQL migration will work identically to SQLite

**PostgreSQL Migration Specifics:**
```bash
# 1. Create PostgreSQL database (NO PostGIS extension needed)
CREATE DATABASE obcms_prod ENCODING 'UTF8';
CREATE USER obcms_user WITH PASSWORD 'secure-password';
GRANT ALL PRIVILEGES ON DATABASE obcms_prod TO obcms_user;

# 2. Update .env
DATABASE_URL=postgres://obcms_user:password@localhost:5432/obcms_prod

# 3. Run migrations (all 118 migrations are PostgreSQL-compatible)
cd src
python manage.py migrate

# Expected: All migrations apply successfully in 2-5 minutes
```

**Important Notes:**
- ❌ **DO NOT install PostGIS** - Not needed, adds unnecessary complexity
- ✅ **JSONField works natively** - PostgreSQL uses `jsonb` type automatically
- ✅ **Geographic data migration** - Boundaries stored as GeoJSON (human-readable)
- ✅ **No code changes required** - System is 100% PostgreSQL-compatible

#### 2. **Environment Configuration**

**Required Documents:**
- 📚 **[Staging Environment Guide](docs/env/staging-complete.md)** ⭐ **12-STEP PROCEDURE**
  - Complete staging deployment walkthrough
  - Environment variable templates
  - Database setup instructions
  - SSL/TLS configuration
  - Celery worker setup
  - Testing and validation procedures

- 📚 **[Pre-Staging Complete Report](docs/deployment/PRE_STAGING_COMPLETE.md)**
  - UI refinements completed
  - Performance test results (83% passing)
  - Code quality standardization
  - Overall deployment readiness

**Environment Variables Checklist:**
```env
# CRITICAL: Update ALL placeholders before deployment
SECRET_KEY=             # Generate: python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
DEBUG=0                 # MUST be 0 in production
ALLOWED_HOSTS=          # yourdomain.com,www.yourdomain.com
CSRF_TRUSTED_ORIGINS=   # https://yourdomain.com,https://www.yourdomain.com
DATABASE_URL=           # postgres://user:pass@host:5432/dbname
REDIS_URL=              # redis://redis:6379/0
EMAIL_BACKEND=          # django.core.mail.backends.smtp.EmailBackend (NOT console)
```

#### 3. **Security & Performance**

**Required Reviews:**
- 📚 **[Production Settings](src/obc_management/settings/production.py)**
  - HSTS, SSL redirect, secure cookies configured
  - Connection pooling enabled (CONN_MAX_AGE = 600)
  - CSP headers configured
  - All security warnings addressed

- 📚 **[Performance Test Results](docs/testing/PERFORMANCE_TEST_RESULTS.md)**
  - Calendar performance: Excellent (< 15ms)
  - Resource booking: Good (handles 25+ concurrent users)
  - HTMX rendering: Fast (< 50ms)
  - 83% test pass rate (10/12 tests)

**Security Checklist:**
```bash
# Run deployment checks BEFORE deploying
cd src
python manage.py check --deploy

# Expected: All warnings should be addressed in production.py
# Development warnings are OK (DEBUG=True, etc.)
```

#### 4. **Testing Strategy**

**Pre-Deployment Testing:**
```bash
# 1. Run full test suite
pytest -v
# Expected: 254/256 tests passing (99.2%)

# 2. Run performance tests
pytest tests/performance/ -v
# Expected: 10/12 tests passing (83%)

# 3. Security audit
python manage.py check --deploy
```

**Post-Deployment Verification:**
```bash
# 1. Health check
curl https://staging.obcms.gov.ph/health/
curl https://staging.obcms.gov.ph/ready/

# 2. Admin panel
curl -I https://staging.obcms.gov.ph/admin/

# 3. Test user login
# 4. Test each module (Communities, MANA, Coordination, etc.)
```

#### 5. **Deployment Platform Guides**

**Choose ONE deployment method:**

**Option A: Coolify (Recommended)**
- 📚 **[Coolify Deployment Checklist](docs/deployment/deployment-coolify.md)**
- 📚 **[Coolify Deployment Plan](docs/deployment/coolify-deployment-plan.md)**

**Option B: Docker Compose**
- 📚 **[Docker Guide](docs/deployment/docker-guide.md)**

#### 6. **UI/UX Verification**

**Review UI Implementation:**
- 📚 **[UI Refinements Complete](docs/improvements/UI/UI_REFINEMENTS_COMPLETE.md)**
  - Task deletion instant feedback verified
  - Code formatting with Black completed
  - UX pattern consistency checked
  - Production-ready UI confirmed

---

### Database Query Best Practices (PostgreSQL)

**IMPORTANT: Text Search Queries**

PostgreSQL is **case-sensitive** by default (unlike SQLite). Always use case-insensitive lookups:

```python
# ❌ BAD: Case-sensitive (different behavior in PostgreSQL)
Region.objects.filter(name__contains='BARMM')        # Case-sensitive
User.objects.filter(username__startswith='admin')    # Case-sensitive

# ✅ GOOD: Case-insensitive (consistent across databases)
Region.objects.filter(name__icontains='BARMM')       # Case-insensitive
User.objects.filter(username__istartswith='admin')   # Case-insensitive
User.objects.filter(email__iexact='admin@oobc.gov')  # Case-insensitive exact match
```

**Lookup Reference:**
- `__icontains` - Case-insensitive contains
- `__istartswith` - Case-insensitive starts with
- `__iendswith` - Case-insensitive ends with
- `__iexact` - Case-insensitive exact match

**Status:** ✅ OBCMS codebase already follows these patterns (verified via audit)

---

### Geographic Data Guidelines (PostgreSQL)

**Current Implementation: JSONField (Production-Ready)**

OBCMS uses Django's JSONField for geographic data storage:

```python
# Region, Province, Municipality, Barangay models
class Region(models.Model):
    # GeoJSON boundaries (PostgreSQL uses native 'jsonb' type)
    boundary_geojson = models.JSONField(null=True, blank=True)

    # Center coordinates {"lat": 8.45, "lng": 124.63}
    center_coordinates = models.JSONField(null=True, blank=True)

    # Bounding box [[south, west], [north, east]]
    bounding_box = models.JSONField(null=True, blank=True)
```

**PostgreSQL Storage:**
- Automatically uses `jsonb` type (efficient, indexed)
- Supports JSON operators (->>, ->, @>, etc.)
- Perfect for Leaflet.js (GeoJSON native)
- Human-readable (easy debugging)

**PostGIS Decision: NOT NEEDED** ✅
- Current use case: Display boundaries, store coordinates
- NOT needed: Spatial joins, distance queries, geometric calculations
- JSONField is production-ready and sufficient
- Avoid PostGIS complexity unless spatial queries become required

**See:** [Geographic Data Implementation Guide](docs/improvements/geography/GEOGRAPHIC_DATA_IMPLEMENTATION.md)

---

### Deployment Workflow

**Standard Deployment Sequence:**

1. **Development → Staging → Production**
   ```
   Development (SQLite)
         ↓
   Staging (PostgreSQL) ← Test here first
         ↓
   Production (PostgreSQL)
   ```

2. **Pre-Deployment Steps:**
   - [ ] Review ALL deployment documentation listed above
   - [ ] Verify PostgreSQL migration compatibility
   - [ ] Confirm geographic data implementation (JSONField, no PostGIS)
   - [ ] Validate case-insensitive query patterns
   - [ ] Generate production SECRET_KEY
   - [ ] Configure environment variables
   - [ ] Set up PostgreSQL database (NO PostGIS extension)

3. **Migration Execution:**
   ```bash
   # Staging deployment
   cd src
   export DJANGO_SETTINGS_MODULE=obc_management.settings.production
   python manage.py migrate
   python manage.py check --deploy
   python manage.py collectstatic --noinput
   ```

4. **Post-Deployment Verification:**
   - [ ] Run health checks
   - [ ] Execute smoke tests
   - [ ] Verify all modules functional
   - [ ] Check performance metrics
   - [ ] Monitor error logs (first 24 hours)

---

### Critical Reminders

**BEFORE Deployment:**
1. ✅ **Review PostgreSQL Migration Summary** (comprehensive overview)
2. ✅ **Confirm NO PostGIS installation** (JSONField is sufficient)
3. ✅ **Verify case-insensitive queries** (audit already completed - 100% compatible)
4. ✅ **Generate production SECRET_KEY** (50+ characters, cryptographically random)
5. ✅ **Update ALL environment variables** (no placeholders in production)
6. ✅ **Run deployment checks** (`python manage.py check --deploy`)
7. ✅ **Test in staging first** (NEVER deploy directly to production)

**Database Migration Checklist:**
- [ ] PostgreSQL database created (ENCODING 'UTF8')
- [ ] User and privileges configured
- [ ] DATABASE_URL environment variable set
- [ ] All 118 migrations reviewed (all PostgreSQL-compatible)
- [ ] NO PostGIS extension installed (not needed)
- [ ] JSONField geographic data verified (automatic jsonb type)
- [ ] Case-sensitive queries audited (100% compatible)

**Rollback Plan:**
- Option 1: Revert to SQLite (development only)
- Option 2: Restore PostgreSQL from backup
- Option 3: Fresh migration with `--fake-initial`

**See:** [PostgreSQL Migration Review](docs/deployment/POSTGRESQL_MIGRATION_REVIEW.md#rollback-plan)

---

### Documentation Index for Deployment

**Must-Read Before Any Deployment:**

1. **[PostgreSQL Migration Summary](docs/deployment/POSTGRESQL_MIGRATION_SUMMARY.md)** ⭐ START HERE
2. **[PostgreSQL Migration Review](docs/deployment/POSTGRESQL_MIGRATION_REVIEW.md)** ⭐ TECHNICAL
3. **[Case-Sensitive Query Audit](docs/deployment/CASE_SENSITIVE_QUERY_AUDIT.md)** ✅ VERIFIED
4. **[Geographic Data Implementation](docs/improvements/geography/GEOGRAPHIC_DATA_IMPLEMENTATION.md)** ✅ NO POSTGIS
5. **[Staging Environment Guide](docs/env/staging-complete.md)** ⭐ 12-STEP PROCEDURE
6. **[Pre-Staging Complete Report](docs/deployment/PRE_STAGING_COMPLETE.md)** ✅ READY

**Reference Documents:**
7. **[PostGIS Migration Guide](docs/improvements/geography/POSTGIS_MIGRATION_GUIDE.md)** 📋 Future reference only
8. **[Deployment Implementation Status](docs/deployment/DEPLOYMENT_IMPLEMENTATION_STATUS.md)**
9. **[Performance Test Results](docs/testing/PERFORMANCE_TEST_RESULTS.md)**
10. **[UI Refinements Complete](docs/improvements/UI/UI_REFINEMENTS_COMPLETE.md)**

**Full Documentation Index:** [docs/README.md](docs/README.md)

---

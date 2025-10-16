# Organization Context Middleware Guide

**BMMS Multi-Tenant Architecture Foundation**

This guide provides comprehensive documentation for the organization context middleware system that enables secure multi-tenant operation across 44 BARMM Ministries, Offices, and Agencies (MOAs).

## Executive Summary

The organization context middleware system provides:

- **Thread-safe multi-tenant data isolation** for concurrent requests
- **Comprehensive audit logging** for security and compliance
- **OCM special access patterns** for cross-organization oversight
- **Mode-aware behavior** supporting both OBCMS and BMMS modes
- **Automatic fallback mechanisms** for seamless user experience
- **Performance optimization** with caching and efficient query patterns

## Architecture Overview

### Core Components

1. **OrganizationMiddleware** (`organizations/middleware.py`)
   - Primary middleware for organization context management
   - Thread-safe implementation with comprehensive audit logging
   - Handles URL-based organization extraction and validation

2. **OrganizationContextMiddleware** (`common/middleware/organization_context.py`)
   - Legacy compatibility layer with enhanced integration
   - Supports existing OBCMS patterns while enabling BMMS features
   - Lazy loading for optimal performance

3. **Thread-Local Context Utilities** (`organizations/middleware.py`)
   - `get_thread_context()` - Current request context
   - `is_ocm_context()` - OCM user detection
   - `get_current_organization_id()` - Organization ID access
   - `get_current_organization_code()` - Organization code access

4. **Organization-Scoped Models** (`organizations/models/scoped.py`)
   - `OrganizationScopedModel` - Base class for multi-tenant models
   - `OrganizationScopedManager` - Automatic query filtering
   - Thread-local storage integration

### Data Flow

```
HTTP Request
    ↓
AuthenticationMiddleware
    ↓
OrganizationMiddleware
    ├─ Extract organization from URL (/moa/{CODE}/...)
    ├─ Validate user access permissions
    ├─ Set thread-local context
    ├─ Log context change
    └─ Set request.organization
    ↓
OrganizationContextMiddleware (Integration)
    ↓
Application Views/Models
    ├─ request.organization available
    ├─ get_current_organization() available
    ├─ Automatic query filtering
    └─ OCM access patterns
    ↓
Response
    ↓
Thread-local cleanup
```

## Configuration

### Settings Integration

Add to `src/obc_management/settings/base.py`:

```python
# Enable organization context logging
LOGGING["loggers"]["organizations.audit"] = {
    "handlers": ["organizations_audit", "console"],
    "level": "INFO",
    "propagate": False,
}

LOGGING["loggers"]["organizations.security"] = {
    "handlers": ["rbac_security", "console"],
    "level": "WARNING",
    "propagate": False,
}
```

### Middleware Stack

```python
MIDDLEWARE = [
    # ... existing middleware ...
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "organizations.middleware.OrganizationMiddleware",  # Primary organization context
    "common.middleware.organization_context.OrganizationContextMiddleware",  # Integration layer
    # ... remaining middleware ...
]
```

### Template Context Processors

```python
TEMPLATES = [{
    "OPTIONS": {
        "context_processors": [
            # ... existing processors ...
            "organizations.middleware.organization_context",  # Add organization data to templates
        ],
    },
}]
```

## Usage Patterns

### In Views

```python
def dashboard_view(request):
    # Organization is automatically available
    organization = request.organization

    if not organization:
        return redirect('organization_selection')

    # Query data is automatically filtered
    communities = OBCCommunity.objects.all()  # Only returns org-specific data

    # OCM users can access all organizations
    if request.is_ocm_user:
        all_communities = OBCCommunity.all_objects.all()

    return render(request, 'dashboard.html', {
        'organization': organization,
        'communities': communities,
    })
```

### In Models

```python
from organizations.models.scoped import OrganizationScopedModel

class Project(OrganizationScopedModel):
    name = models.CharField(max_length=200)
    description = models.TextField()

    # organization field is automatically added
    # queries are automatically filtered by current organization

    class Meta:
        verbose_name = 'Project'
        verbose_name_plural = 'Projects'

# Usage
projects = Project.objects.all()  # Automatically filtered by organization

# OCM users can access all organizations
if is_ocm_context():
    all_projects = Project.all_objects.all()
```

### In Templates

```html
{% if request.organization %}
    <div class="org-header">
        <h1>{{ request.organization.name }}</h1>
        <p class="org-code">{{ request.organization.code }}</p>
        {% if request.is_ocm_user %}
            <span class="badge ocm">OCM Access</span>
        {% endif %}
    </div>

    <div class="enabled-modules">
        {% for module in enabled_modules %}
            <span class="module-badge">{{ module }}</span>
        {% endfor %}
    </div>
{% else %}
    <div class="alert alert-warning">
        Please select an organization to continue.
    </div>
{% endif %}
```

## URL Patterns

### BMMS Mode (Multi-tenant)

```python
# Organization-specific URLs
/moa/OOBC/dashboard/    # OOBC organization dashboard
/moa/MOH/assessments/   # MOH assessments
/moa/OCM/reports/      # OCM aggregated reports

# Fallback to user's primary organization
/dashboard/               # Uses user's primary organization
/communities/             # Filtered by organization context
```

### OBCMS Mode (Single-tenant)

```python
# Standard URLs (auto-injects default OOBC organization)
/dashboard/
/communities/
/mana/assessments/
```

## Access Control

### User Access Rules

| User Type | Access Level | Description |
|-----------|-------------|-------------|
| **Superusers** | Full Access | Can access any organization with full permissions |
| **OCM Users** | Read-Only Access | Can view all organizations for oversight and reporting |
| **OOBC Staff** | Full Access | Can access all organizations for operational support |
| **MOA Staff** | Limited Access | Can only access their assigned organization |
| **Anonymous** | No Access | No organization context available |

### Organization Membership

```python
# Create organization membership
OrganizationMembership.objects.create(
    user=user,
    organization=organization,
    role='staff',  # admin, manager, staff, viewer
    is_primary=True,  # User's primary organization
    is_active=True,
    can_approve_plans=True,
    can_approve_budgets=False,
)
```

## Thread Safety

### Concurrent Request Handling

The middleware is designed for thread-safe operation:

```python
# Each request gets its own thread-local context
_request_id = threading.get_ident()
_thread_context.request_id = id(request)
_thread_context.organization_id = organization.id
_thread_context.user_id = request.user.id
```

### Memory Management

Automatic cleanup prevents memory leaks:

```python
def _cleanup_thread_context(self):
    """Clean up thread-local storage to prevent memory leaks."""
    try:
        clear_current_organization()

        # Clear all thread-local attributes
        attrs_to_clear = [
            'request_id', 'user_id', 'ip_address', 'user_agent',
            'start_time', 'organization_id', 'organization_code', 'is_ocm_user'
        ]

        for attr in attrs_to_clear:
            if hasattr(_thread_context, attr):
                delattr(_thread_context, attr)
    except Exception as e:
        logger.error(f'Error cleaning up thread context: {e}')
```

## Audit Logging

### Log Categories

1. **Organization Context Changes** (`organizations.audit`)
   - Organization selection and switching
   - User access validation
   - Mode transitions (OBCMS ↔ BMMS)

2. **Security Events** (`organizations.security`)
   - Unauthorized access attempts
   - Invalid organization codes
   - Permission violations
   - Context setting errors

### Log Format

```
INFO Organization context set | Org: MOH (123) | User: johndoe (456) | IP: 192.168.1.100 | Path: /moa/MOH/dashboard/ | OCM: False | Mode: BMMS
WARNING Unauthorized access attempt to MOH | User: unauthorized_user (789) | IP: 10.0.0.5 | Path: /moa/MOH/restricted/
ERROR Organization context error | Error: Database connection failed | User: testuser (123) | IP: 127.0.0.1 | Path: /dashboard/
```

### Log Rotation

Organization audit logs are automatically rotated:

```python
LOGGING["handlers"]["organizations_audit"] = {
    "level": "INFO",
    "class": "logging.handlers.RotatingFileHandler",
    "filename": BASE_DIR / "logs" / "organizations_audit.log",
    "maxBytes": 52428800,  # 50MB per file
    "backupCount": 20,  # Keep 20 backup files (~1GB total)
    "formatter": "security_audit",
}
```

## OCM Special Access Patterns

### OCM Detection

```python
def is_ocm_user(user) -> bool:
    """Check if user is from Office of Chief Minister (OCM)."""
    if user.is_superuser:
        return True

    if user.user_type == 'cm_office':
        return True

    # Check organization membership
    ocm_code = getattr(settings, 'RBAC_SETTINGS', {}).get('OCM_ORGANIZATION_CODE', 'OCM')
    return user.organization_memberships.filter(
        organization__code__iexact=ocm_code,
        is_active=True
    ).exists()
```

### Cross-Organization Queries

```python
# OCM users can access all organizations
if is_ocm_context():
    # All organizations for reporting
    all_orgs = Organization.objects.all()

    # Cross-organization data aggregation
    total_projects = Project.all_objects.aggregate(
        total=Count('id')
    )

    # Organization-specific breakdowns
    org_stats = {}
    for org in all_orgs:
        org_stats[org.code] = Project.all_objects.filter(
            organization=org
        ).count()
```

## Performance Optimization

### Caching Strategies

```python
# Organization model caching
@cache_page(300)  # 5 minutes
def organization_view(request, org_code):
    organization = get_object_or_404(Organization, code=org_code)
    return render(request, 'org_detail.html', {'org': organization})

# Query optimization with select_related
def get_organization_projects(organization):
    return Project.objects.filter(
        organization=organization
    ).select_related('organization', 'created_by')
```

### Database Query Optimization

```python
# Efficient queries with proper indexing
class Organization(models.Model):
    code = models.CharField(max_length=20, db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['is_active']),
            models.Index(fields=['org_type', 'is_active']),
        ]
```

## Testing

### Test Coverage

The middleware includes comprehensive test coverage:

- **Basic functionality**: Organization extraction, access control
- **Thread safety**: Concurrent request handling
- **Performance**: Request timing and memory usage
- **Security**: Unauthorized access attempts, audit logging
- **Integration**: Compatibility with existing systems

### Running Tests

```bash
# Run organization middleware tests
python manage.py test organizations.tests.test_middleware

# Run specific test class
python manage.py test organizations.tests.test_middleware.TestEnhancedMiddlewareFeatures

# Run with coverage
python manage.py test organizations.tests.test_middleware --cov=organizations
```

### Test Examples

```python
def test_ocm_user_access_any_organization(self, middleware, factory, organizations):
    """Test OCM user can access any organization."""
    request = factory.get('/moa/MOH/dashboard/')
    request.user = self.ocm_user

    def dummy_response(req):
        assert req.organization == organizations['moh']
        return None

    middleware.get_response = dummy_response
    response = middleware(request)

    assert not isinstance(response, HttpResponseForbidden)

def test_thread_safety(self, middleware, factory, organizations):
    """Test thread safety of organization context."""
    results = {}
    errors = []

    def worker(org_code, user, thread_id):
        try:
            request = factory.get(f'/moa/{org_code}/dashboard/')
            request.user = user
            response = middleware(request)
            results[thread_id] = {
                'organization': request.organization.code if request.organization else None,
                'thread_id': threading.get_ident()
            }
        except Exception as e:
            errors.append(f'Thread {thread_id}: {str(e)}')

    # Create multiple threads
    threads = []
    for i in range(5):
        thread = threading.Thread(
            target=worker,
            args=('MOH', self.moh_user, f'thread_{i}')
        )
        threads.append(thread)

    # Start and wait for completion
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    # Verify results
    assert len(errors) == 0
    assert len(results) == 5
    for result in results.values():
        assert result['organization'] == 'MOH'
```

## Troubleshooting

### Common Issues

#### 1. Organization Not Set

**Problem**: `request.organization` is None

**Solution**:
- Verify user has active OrganizationMembership
- Check URL pattern includes organization code
- Ensure middleware is in correct order (after AuthenticationMiddleware)

#### 2. Cross-Organization Data Leakage

**Problem**: User sees data from other organizations

**Solution**:
- Verify models inherit from `OrganizationScopedModel`
- Check thread-local context is properly set
- Ensure queries use default manager (not `all_objects`)

#### 3. Performance Issues

**Problem**: Slow response times

**Solution**:
- Add database indexes on organization foreign keys
- Use `select_related()` and `prefetch_related()` for queries
- Enable query caching where appropriate

#### 4. Audit Logs Not Working

**Problem**: No organization audit logs being generated

**Solution**:
- Verify logging configuration in settings
- Check log file permissions
- Ensure log level is set correctly

### Debug Mode

Enable debug logging:

```python
LOGGING["loggers"]["organizations"] = {
    "handlers": ["console", "file"],
    "level": "DEBUG",
    "propagate": False,
}
```

Add debugging to views:

```python
def debug_view(request):
    from organizations.middleware import get_thread_context

    context = get_thread_context()
    logger.debug(f'Organization context: {context}')
    logger.debug(f'Request organization: {request.organization}')
    logger.debug(f'Current org from thread: {get_current_organization()}')

    return HttpResponse("Debug info logged")
```

## Migration Guide

### From OBCMS to BMMS

1. **Update Settings**:
   ```python
   BMMS_MODE = 'bmms'
   ENABLE_MULTI_TENANT = True
   ```

2. **Add Organizations Middleware**:
   ```python
   MIDDLEWARE = [
       # ... existing middleware ...
       "organizations.middleware.OrganizationMiddleware",
       "common.middleware.organization_context.OrganizationContextMiddleware",
   ]
   ```

3. **Update Models**:
   ```python
   # Old:
   class Project(models.Model):
       name = models.CharField(max_length=200)

   # New:
   class Project(OrganizationScopedModel):
       name = models.CharField(max_length=200)
   ```

4. **Update Views**:
   ```python
   # Old:
   projects = Project.objects.all()

   # New (automatic filtering):
   projects = Project.objects.all()

   # Cross-organization access:
   if is_ocm_context():
       all_projects = Project.all_objects.all()
   ```

5. **Update Templates**:
   ```html
   <!-- Add organization context -->
   {% if request.organization %}
       <h1>{{ request.organization.name }}</h1>
   {% endif %}
   ```

## Security Considerations

### Data Isolation

- **Thread-local storage** prevents cross-request data leakage
- **Automatic query filtering** ensures users only see their organization's data
- **OCM read-only access** provides oversight without modification capabilities

### Access Control

- **Membership validation** ensures only authorized users can access organizations
- **Permission checks** enforced at middleware level
- **Audit logging** tracks all access attempts and context changes

### Session Security

- **Organization switching** requires valid membership
- **Session fixation** prevented by re-validating access
- **CSRF protection** maintained for all organization-specific actions

## Best Practices

### Development

1. **Always check organization context** in multi-tenant views
2. **Use organization-scoped models** for new data models
3. **Test with multiple organizations** to verify data isolation
4. **Implement proper access controls** for cross-organization features

### Operations

1. **Monitor audit logs** for security incidents
2. **Regular backup** of organization and membership data
3. **Performance monitoring** for multi-tenant load
4. **Access review** of OCM users and permissions

### Deployment

1. **Configure proper logging** in production
2. **Set log rotation** to manage disk space
3. **Monitor thread usage** in high-traffic scenarios
4. **Test failover** procedures for organization context

## References

- [BMMS Transition Plan](../plans/bmms/TRANSITION_PLAN.md)
- [OBCMS UI Standards](../ui/OBCMS_UI_STANDARDS_MASTER.md)
- [Django Middleware Documentation](https://docs.djangoproject.com/en/stable/topics/http/middleware/)
- [Django Thread Safety](https://docs.djangoproject.com/en/stable/faq/models/#faq-threadsafety)

---

**Last Updated**: October 16, 2025
**Version**: 1.0
**Maintainer**: OBCMS Development Team
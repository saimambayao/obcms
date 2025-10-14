# Security and Access Control Implications

## Overview

Switching from OBCMS to BMMS mode introduces significant security enhancements and access control changes. This document details all security-related modifications, new threat models, and compliance considerations when enabling BMMS multi-tenant mode.

## Security Architecture Changes

### 1. Multi-Tenant Data Isolation

**OBCMS Mode Security Model:**
```
┌─────────────────────────────────────────┐
│ Single Organization (OOBC)              │
│ ┌─────────────────────────────────────┐ │
│ │ All Data Accessible                 │ │
│ │ No Organization Boundaries          │ │
│ │ Basic Django Permissions            │ │
│ └─────────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

**BMMS Mode Security Model:**
```
┌─────────────────────────────────────────┐
│ Multi-Tenant Environment (44 MOAs)       │
│ ┌─────────┐ ┌─────────┐ ┌─────────┐       │
│ │   OOBC  │ │   MOH   │ │  MENR   │       │
│ │Data Only│ │Data Only│ │Data Only│       │
│ └─────────┘ └─────────┘ └─────────┘       │
│                                         │
│ ┌─────────────────────────────────────┐ │
│ │ OCM Read-Only Aggregated Access     │ │
│ └─────────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

### 2. Access Control Layer Changes

**Authentication Flow Modifications:**

**OBCMS Mode:**
```python
def login_view(request):
    if request.method == 'POST':
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            # Auto-grant access to OOBC
            return redirect('/dashboard/')
    return render(request, 'login.html')
```

**BMMS Mode:**
```python
def login_view(request):
    if request.method == 'POST':
        user = authenticate(username=username, password=password)
        if user is not None:
            # Verify user has at least one organization membership
            if not user.organizationmembership_set.exists():
                return render(request, 'login.html', {
                    'error': 'No organization access assigned. Contact administrator.'
                })
            
            login(request, user)
            # Set primary organization as default
            primary_org = user.organizationmembership_set.filter(
                is_primary=True, 
                is_active=True
            ).first()
            
            if primary_org:
                request.session['selected_organization_id'] = primary_org.organization_id
                return redirect(f'/moa/{primary_org.organization.code}/dashboard/')
            else:
                return redirect('/select-organization/')
    
    return render(request, 'login.html')
```

### 3. Middleware Security Enhancements

**OrganizationMiddleware Security Logic:**
```python
class OrganizationMiddleware:
    def __call__(self, request: HttpRequest) -> HttpResponse:
        if is_obcms_mode():
            # OBCMS mode: simple auto-injection
            request.organization = get_default_organization()
            return self.get_response(request)
        
        # BMMS mode: strict validation
        org_code = self._extract_org_code_from_url(request.path)
        
        if org_code:
            organization = self._get_organization_from_code(org_code)
            
            if not organization:
                # Security: Don't reveal organization existence
                logger.warning(f"Invalid organization code attempted: {org_code}")
                return HttpResponseForbidden("Access denied")
            
            # Critical security check
            if not self._user_can_access_organization(request.user, organization):
                # Log security event
                self._log_unauthorized_access(request, organization)
                return HttpResponseForbidden("Access denied")
            
            request.organization = organization
        
        response = self.get_response(request)
        return response
    
    def _user_can_access_organization(self, user, organization) -> bool:
        """Multi-layer access validation"""
        if isinstance(user, AnonymousUser) or not user.is_authenticated:
            return False
        
        # Superuser access (controlled)
        if user.is_superuser:
            logger.info(f"Superuser {user.username} accessing {organization.code}")
            return True
        
        # Organization membership validation
        has_membership = OrganizationMembership.objects.filter(
            user=user,
            organization=organization,
            is_active=True
        ).exists()
        
        if not has_membership:
            logger.warning(f"User {user.username} lacks membership for {organization.code}")
        
        return has_membership
    
    def _log_unauthorized_access(self, request, organization):
        """Security event logging"""
        logger.warning(
            f"Unauthorized organization access attempt: "
            f"user={request.user.username if request.user.is_authenticated else 'anonymous'}, "
            f"target_org={organization.code}, "
            f"ip={self._get_client_ip(request)}, "
            f"user_agent={request.META.get('HTTP_USER_AGENT', 'unknown')}, "
            f"path={request.path}"
        )
```

## Data Isolation Enforcement

### 1. Database-Level Security

**Organization-Scoped Query Filtering:**
```python
class OrganizationManager(models.Manager):
    """Auto-filters queries by current organization"""
    def get_queryset(self):
        current_org = get_current_organization()
        if current_org:
            return super().get_queryset().filter(organization=current_org)
        return super().get_queryset()

class AllOrganizationsManager(models.Manager):
    """OCM access to all organizations (read-only)"""
    def get_queryset(self):
        return super().get_queryset()

class Community(OrganizationScopedModel):
    name = models.CharField(max_length=200)
    organization = models.ForeignKey(Organization, on_delete=models.PROTECT)
    
    # Default manager: organization-scoped
    objects = OrganizationManager()
    
    # OCM manager: all organizations
    all_objects = AllOrganizationsManager()
    
    def save(self, *args, **kwargs):
        # Security: Auto-set organization context
        if not self.organization_id:
            current_org = get_current_organization()
            if not current_org:
                raise SecurityError("Organization context required")
            self.organization = current_org
        
        # Audit logging
        self._log_data_operation('save')
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        # Security: Validate organization context
        current_org = get_current_organization()
        if self.organization_id != current_org.id:
            raise SecurityError("Cannot delete data from different organization")
        
        # Audit logging
        self._log_data_operation('delete')
        super().delete(*args, **kwargs)
```

### 2. Cross-Organization Access Prevention

**View-Level Security Decorators:**
```python
def require_organization(view_func):
    """Decorator ensuring organization context"""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if is_obcms_mode():
            # OBCMS mode: auto-inject OOBC
            request.organization = get_default_organization()
            return view_func(request, *args, **kwargs)
        
        # BMMS mode: validate organization context
        if not hasattr(request, 'organization') or not request.organization:
            return HttpResponseForbidden("Organization context required")
        
        # Additional security checks
        if not _validate_organization_access(request):
            return HttpResponseForbidden("Invalid organization access")
        
        return view_func(request, *args, **kwargs)
    
    return _wrapped_view

def _validate_organization_access(request) -> bool:
    """Comprehensive organization access validation"""
    if not request.user.is_authenticated:
        return False
    
    # Check membership
    membership_exists = OrganizationMembership.objects.filter(
        user=request.user,
        organization=request.organization,
        is_active=True
    ).exists()
    
    if not membership_exists:
        # Log security violation
        log_security_event(
            user=request.user,
            organization=request.organization,
            event_type='unauthorized_organization_access',
            details={'path': request.path, 'method': request.method}
        )
        return False
    
    return True
```

### 3. OCM (Office of Chief Minister) Security

**OCM Access Control:**
```python
class OCMAccessMiddleware:
    """Enforces OCM read-only access patterns"""
    
    def __call__(self, request: HttpRequest) -> HttpResponse:
        if not self._is_ocm_user(request.user):
            return self.get_response(request)
        
        # OCM users get read-only aggregated access
        request.is_ocm_user = True
        request.ocm_readonly_mode = True
        
        response = self.get_response(request)
        
        # Ensure no data modification occurred
        if self._is_data_modifying_request(request):
            logger.critical(f"OCM user attempted data modification: {request.user.username}")
            return HttpResponseForbidden("OCM users have read-only access")
        
        return response
    
    def _is_ocm_user(self, user) -> bool:
        """Check if user is OCM staff"""
        if not user.is_authenticated:
            return False
        
        return (
            user.is_superuser or
            user.groups.filter(name='OCM Staff').exists() or
            hasattr(user, 'profile') and user.profile.department == 'OCM'
        )
    
    def _is_data_modifying_request(self, request) -> bool:
        """Detect requests that modify data"""
        modifying_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
        return request.method in modifying_methods
```

## Authentication and Authorization Changes

### 1. Enhanced User Model

**Organization-Aware User:**
```python
class User(AbstractUser):
    # Existing fields...
    
    # BMMS-specific fields
    default_organization = models.ForeignKey(
        Organization, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='default_users'
    )
    
    def get_organizations(self):
        """Get all organizations user has access to"""
        return Organization.objects.filter(
            organizationmembership__user=self,
            organizationmembership__is_active=True
        )
    
    def can_access_organization(self, organization):
        """Check if user can access specific organization"""
        if self.is_superuser:
            return True
        
        return self.organizationmembership_set.filter(
            organization=organization,
            is_active=True
        ).exists()
    
    def get_primary_organization(self):
        """Get user's primary organization"""
        membership = self.organizationmembership_set.filter(
            is_primary=True,
            is_active=True
        ).first()
        return membership.organization if membership else None

class OrganizationMembership(models.Model):
    """Tracks user access to organizations"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    is_primary = models.BooleanField(default=False)
    role = models.CharField(max_length=50, choices=ROLE_CHOICES)
    permissions = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'organization']
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['organization', 'is_active']),
        ]
```

### 2. RBAC Integration

**Multi-Tenant RBAC:**
```python
class MultiTenantPermission(models.Model):
    """Organization-scoped permissions"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    permission = models.CharField(max_length=100)
    granted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='granted_permissions')
    granted_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ['user', 'organization', 'permission']
        indexes = [
            models.Index(fields=['user', 'organization']),
            models.Index(fields=['organization', 'permission']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.organization.code} - {self.permission}"

def has_organization_permission(user, organization, permission):
    """Check if user has specific permission in organization"""
    if user.is_superuser:
        return True
    
    return MultiTenantPermission.objects.filter(
        user=user,
        organization=organization,
        permission=permission,
        expires_at__gt=timezone.now()
    ).exists()
```

## Security Logging and Monitoring

### 1. Comprehensive Audit Trail

**Security Event Logging:**
```python
class SecurityEventLogger:
    """Centralized security event logging"""
    
    @staticmethod
    def log_organization_access(user, organization, action, details=None):
        """Log organization access events"""
        event = {
            'timestamp': timezone.now().isoformat(),
            'event_type': 'organization_access',
            'user_id': user.id,
            'username': user.username,
            'organization_id': organization.id,
            'organization_code': organization.code,
            'action': action,
            'ip_address': get_client_ip(),
            'user_agent': get_user_agent(),
            'details': details or {},
        }
        
        # Log to file
        logger.info(f"Security Event: {json.dumps(event)}")
        
        # Store in database for analysis
        SecurityEvent.objects.create(**event)
    
    @staticmethod
    def log_cross_organization_attempt(user, target_org, source_org=None):
        """Log cross-organization access attempts"""
        event = {
            'timestamp': timezone.now().isoformat(),
            'event_type': 'cross_organization_attempt',
            'user_id': user.id,
            'username': user.username,
            'target_organization_id': target_org.id,
            'target_organization_code': target_org.code,
            'source_organization_id': source_org.id if source_org else None,
            'source_organization_code': source_org.code if source_org else None,
            'ip_address': get_client_ip(),
            'user_agent': get_user_agent(),
            'severity': 'WARNING',
        }
        
        logger.warning(f"Security Violation: {json.dumps(event)}")
        SecurityEvent.objects.create(**event)

class SecurityEvent(models.Model):
    """Security event tracking"""
    timestamp = models.DateTimeField(auto_now_add=True)
    event_type = models.CharField(max_length=50)
    user_id = models.IntegerField(null=True)
    username = models.CharField(max_length=150, null=True)
    organization_id = models.IntegerField(null=True)
    organization_code = models.CharField(max_length=10, null=True)
    action = models.CharField(max_length=100)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    details = models.JSONField(default=dict)
    severity = models.CharField(max_length=20, choices=[
        ('INFO', 'Info'),
        ('WARNING', 'Warning'),
        ('ERROR', 'Error'),
        ('CRITICAL', 'Critical'),
    ], default='INFO')
    
    class Meta:
        indexes = [
            models.Index(fields=['timestamp']),
            models.Index(fields=['event_type']),
            models.Index(fields=['user_id']),
            models.Index(fields=['organization_id']),
            models.Index(fields=['severity']),
        ]
```

### 2. Real-time Security Monitoring

**Security Dashboard:**
```python
def security_dashboard(request):
    """Real-time security monitoring dashboard"""
    if not request.user.is_superuser:
        return HttpResponseForbidden("Access denied")
    
    # Recent security events
    recent_events = SecurityEvent.objects.filter(
        timestamp__gte=timezone.now() - timedelta(hours=24)
    ).order_by('-timestamp')[:50]
    
    # Organization access statistics
    org_access_stats = SecurityEvent.objects.filter(
        event_type='organization_access',
        timestamp__gte=timezone.now() - timedelta(days=7)
    ).values('organization_code').annotate(
        access_count=Count('id'),
        unique_users=Count('user_id', distinct=True)
    ).order_by('-access_count')
    
    # Security violations
    violations = SecurityEvent.objects.filter(
        severity__in=['WARNING', 'ERROR', 'CRITICAL'],
        timestamp__gte=timezone.now() - timedelta(days=7)
    ).order_by('-timestamp')
    
    return render(request, 'security/dashboard.html', {
        'recent_events': recent_events,
        'org_access_stats': org_access_stats,
        'violations': violations,
        'total_users': User.objects.filter(is_active=True).count(),
        'total_organizations': Organization.objects.filter(is_active=True).count(),
    })
```

## Data Privacy and Compliance

### 1. Data Privacy Act 2012 Compliance

**Privacy Protection Measures:**
```python
class DataPrivacyManager:
    """Ensures compliance with Data Privacy Act 2012"""
    
    @staticmethod
    def anonymize_personal_data(queryset, organization):
        """Anonymize personal data for privacy compliance"""
        # Beneficiary data protection
        for obj in queryset:
            if hasattr(obj, 'beneficiary_name'):
                obj.beneficiary_name = f"Beneficiary {obj.id}"
            if hasattr(obj, 'contact_info'):
                obj.contact_info = "***-***-****"
            obj.save(update_fields=['beneficiary_name', 'contact_info'])
    
    @staticmethod
    def validate_data_access(user, organization, data_type):
        """Validate user has legal basis to access data"""
        # Check consent records
        if data_type == 'beneficiary':
            return BeneficiaryConsent.objects.filter(
                organization=organization,
                user=user,
                consent_given=True,
                expires_at__gt=timezone.now()
            ).exists()
        
        # Check organizational authorization
        return OrganizationMembership.objects.filter(
            user=user,
            organization=organization,
            is_active=True,
            role__in=['Data Officer', 'Administrator']
        ).exists()

class BeneficiaryConsent(models.Model):
    """Track beneficiary data consent"""
    beneficiary_id = models.CharField(max_length=50)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    consent_given = models.BooleanField(default=False)
    consent_date = models.DateTimeField()
    expires_at = models.DateTimeField()
    purpose = models.TextField()
    ip_address = models.GenericIPAddressField()
    
    class Meta:
        unique_together = ['beneficiary_id', 'organization', 'user']
```

### 2. GDPR-Inspired Features

**Data Subject Rights:**
```python
class DataSubjectRights:
    """Implement data subject rights similar to GDPR"""
    
    @staticmethod
    def export_user_data(user, organization):
        """Export all user data for organization"""
        data = {
            'personal_info': {
                'name': user.get_full_name(),
                'email': user.email,
                'username': user.username,
            },
            'organization_membership': OrganizationMembership.objects.filter(
                user=user, organization=organization
            ).values(),
            'access_logs': SecurityEvent.objects.filter(
                user=user, organization=organization
            ).values('timestamp', 'action', 'ip_address')[:100],
            'beneficiary_records': BeneficiaryRecord.objects.filter(
                created_by=user, organization=organization
            ).values(),
        }
        
        return data
    
    @staticmethod
    def delete_user_data(user, organization):
        """Delete user data from organization (right to be forgotten)"""
        with transaction.atomic():
            # Delete access logs
            SecurityEvent.objects.filter(user=user, organization=organization).delete()
            
            # Delete memberships
            OrganizationMembership.objects.filter(user=user, organization=organization).delete()
            
            # Anonymize created records instead of deleting
            BeneficiaryRecord.objects.filter(
                created_by=user, organization=organization
            ).update(created_by=None)
```

## Threat Model Changes

### 1. New Attack Vectors in BMMS Mode

**Cross-Organization Data Leakage:**
```python
# Potential attack: User tries to access other organization's data
# Prevention: OrganizationMiddleware + database filtering

def test_cross_org_attack_prevention():
    """Test that cross-organization attacks are prevented"""
    # Setup
    user1 = User.objects.create_user('user1', 'pass1')
    user2 = User.objects.create_user('user2', 'pass2')
    org1 = Organization.objects.create(code='ORG1', name='Organization 1')
    org2 = Organization.objects.create(code='ORG2', name='Organization 2')
    
    OrganizationMembership.objects.create(user=user1, organization=org1)
    OrganizationMembership.objects.create(user=user2, organization=org2)
    
    # Create test data
    community1 = Community.objects.create(name='Community 1', organization=org1)
    community2 = Community.objects.create(name='Community 2', organization=org2)
    
    # Simulate user1 trying to access org2 data
    set_current_organization(org1)
    
    # This should return empty (prevented)
    user1_communities = Community.objects.all()
    assert community1 in user1_communities
    assert community2 not in user1_communities
    
    # Direct query attempt should be blocked
    with pytest.raises(SecurityError):
        Community.objects.get(organization=org2, id=community2.id)
```

**Organization Enumeration:**
```python
# Potential attack: Attacker tries to discover valid organization codes
# Prevention: Generic error messages, rate limiting

def test_organization_enumeration_prevention():
    """Test that organization enumeration is prevented"""
    
    # Valid organization
    response = client.get('/moa/OOBC/dashboard/')
    assert response.status_code in [200, 302, 403]  # Not 404
    
    # Invalid organization
    response = client.get('/moa/INVALID/dashboard/')
    assert response.status_code == 403  # Not 404 (doesn't reveal existence)
    
    # Error message should be generic
    assert 'not found' not in response.content.decode().lower()
    assert 'access denied' in response.content.decode().lower()
```

### 2. Session Security Enhancements

**Organization-Aware Session Management:**
```python
class OrganizationSessionMiddleware:
    """Enhanced session security for multi-tenant environment"""
    
    def __call__(self, request: HttpRequest) -> HttpResponse:
        if is_bmms_mode():
            # Validate organization in session
            session_org_id = request.session.get('selected_organization_id')
            
            if session_org_id:
                try:
                    org = Organization.objects.get(id=session_org_id, is_active=True)
                    
                    # Validate user still has access
                    if not request.user.is_authenticated or \
                       not request.user.organizationmembership_set.filter(
                           organization=org, is_active=True
                       ).exists():
                        # Clear invalid session organization
                        del request.session['selected_organization_id']
                        logger.warning(f"Invalid session organization cleared for user {request.user.username}")
                
                except Organization.DoesNotExist:
                    del request.session['selected_organization_id']
        
        response = self.get_response(request)
        
        # Add security headers
        if is_bmms_mode():
            response['X-Content-Type-Options'] = 'nosniff'
            response['X-Frame-Options'] = 'DENY'
            response['X-XSS-Protection'] = '1; mode=block'
            response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        return response
```

## Security Configuration Changes

### 1. Environment-Specific Security Settings

**Production Security Hardening:**
```bash
# .env.bmms (Production security settings)
# Security settings
SECRET_KEY=generate-strong-secret-key-for-production-deployment
ALLOWED_HOSTS=bmms.oobc.gov.ph,www.bmms.oobc.gov.ph

# Security headers
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SESSION_COOKIE_HTTPONLY=True
CSRF_COOKIE_HTTPONLY=True

# BMMS-specific security
ENABLE_ORGANIZATION_ISOLATION=True
STRICT_CROSS_ORG_PREVENTION=True
LOG_ALL_ORGANIZATION_ACCESS=True
OCM_READONLY_MODE=True
RATE_LIMIT_ORG_SWITCHING=5/hour
```

### 2. Database Security Configuration

**PostgreSQL Security Settings:**
```sql
-- Row Level Security for additional protection
ALTER TABLE communities_community ENABLE ROW LEVEL SECURITY;

-- Policy to ensure users can only access their organization's data
CREATE POLICY organization_isolation_policy ON communities_community
    FOR ALL TO obcms_app
    USING (organization_id = current_setting('app.current_organization_id')::integer);

-- Audit trigger for all organization-scoped tables
CREATE OR REPLACE FUNCTION audit_organization_access()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO security_audit_log (
        table_name, operation, organization_id, user_id, timestamp
    ) VALUES (
        TG_TABLE_NAME, TG_OP, NEW.organization_id, current_setting('app.current_user_id')::integer, NOW()
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply audit trigger
CREATE TRIGGER community_audit_trigger
    AFTER INSERT OR UPDATE OR DELETE ON communities_community
    FOR EACH ROW EXECUTE FUNCTION audit_organization_access();
```

## Security Testing and Validation

### 1. Automated Security Tests

**Security Test Suite:**
```python
class BMMSecurityTestCase(TestCase):
    """Comprehensive security tests for BMMS mode"""
    
    def setUp(self):
        self.user1 = User.objects.create_user('user1', 'pass1')
        self.user2 = User.objects.create_user('user2', 'pass2')
        self.superuser = User.objects.create_user('admin', 'admin', is_superuser=True)
        
        self.org1 = Organization.objects.create(code='ORG1', name='Organization 1')
        self.org2 = Organization.objects.create(code='ORG2', name='Organization 2')
        
        OrganizationMembership.objects.create(user=self.user1, organization=self.org1)
        OrganizationMembership.objects.create(user=self.user2, organization=self.org2)
    
    def test_organization_data_isolation(self):
        """Test that organization data is properly isolated"""
        # Create data in org1
        set_current_organization(self.org1)
        community1 = Community.objects.create(name='Community 1', organization=self.org1)
        
        # Create data in org2
        set_current_organization(self.org2)
        community2 = Community.objects.create(name='Community 2', organization=self.org2)
        
        # User1 should only see org1 data
        self.client.login(username='user1', password='pass1')
        set_current_organization(self.org1)
        
        response = self.client.get('/moa/ORG1/communities/')
        self.assertContains(response, 'Community 1')
        self.assertNotContains(response, 'Community 2')
        
        # User1 should not access org2 data
        response = self.client.get('/moa/ORG2/communities/')
        self.assertEqual(response.status_code, 403)
    
    def test_superuser_access(self):
        """Test that superuser can access all organizations"""
        self.client.login(username='admin', password='admin')
        
        # Should access both organizations
        response = self.client.get('/moa/ORG1/communities/')
        self.assertIn(response.status_code, [200, 302])
        
        response = self.client.get('/moa/ORG2/communities/')
        self.assertIn(response.status_code, [200, 302])
    
    def test_ocm_readonly_access(self):
        """Test OCM read-only access"""
        # Create OCM user
        ocm_user = User.objects.create_user('ocm', 'ocm')
        ocm_group = Group.objects.create(name='OCM Staff')
        ocm_user.groups.add(ocm_group)
        
        self.client.login(username='ocm', password='ocm')
        
        # Should be able to view data
        response = self.client.get('/moa/ORG1/communities/')
        self.assertIn(response.status_code, [200, 302])
        
        # Should not be able to modify data
        response = self.client.post('/moa/ORG1/communities/create/', {
            'name': 'Test Community'
        })
        self.assertEqual(response.status_code, 403)
```

### 2. Penetration Testing Checklist

**Security Validation Items:**
- [ ] Cross-organization data access prevention
- [ ] Organization enumeration attack prevention
- [ ] Session security in multi-tenant environment
- [ ] OCM read-only access enforcement
- [ ] Audit logging completeness
- [ ] Input validation for organization codes
- [ ] Rate limiting on organization switching
- [ ] CSRF protection with organization context
- [ ] SQL injection prevention with organization filtering
- [ ] Authorization bypass prevention
- [ ] Data leakage prevention in error messages
- [ ] Secure cookie configuration

---

**Related Documentation:**
- [Mode Switching Process](MODE_SWITCHING_PROCESS.md) - Secure mode switching procedures
- [System Changes](SYSTEM_CHANGES.md) - Security-related system modifications
- [Data Preservation](DATA_PRESERVATION.md) - Data security during mode switching

**Last Updated:** October 14, 2025  
**Implementation Status:** Complete  
**Security Review:** Required for production deployment
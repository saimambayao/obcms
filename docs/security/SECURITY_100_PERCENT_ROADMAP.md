# OBCMS Security 100% Score Roadmap

**Document Version:** 1.0
**Date:** October 3, 2025
**Target:** Achieve 100/100 Security Score with All Categories EXCELLENT
**Timeline:** Immediate to 2 weeks

---

## Current State vs. Target State

| Risk Category | Current Status | Current Score | Target Score | Gap Analysis |
|--------------|----------------|---------------|--------------|--------------|
| **Authentication & Authorization** | ✅ EXCELLENT | 20/20 | 20/20 | ✅ **Complete** |
| **API Security** | ✅ GOOD | 15/20 | 20/20 | 5 points needed |
| **Data Protection** | ✅ GOOD | 15/20 | 20/20 | 5 points needed |
| **Infrastructure Security** | ✅ GOOD | 15/20 | 20/20 | 5 points needed |
| **Monitoring & Response** | ✅ GOOD | 14/20 | 20/20 | 6 points needed |
| **Input Validation** | ✅ EXCELLENT | 20/20 | 20/20 | ✅ **Complete** |
| **TOTAL** | **GOOD** | **85/100** | **100/100** | **15 points needed** |

---

## Gap Analysis & Implementation Plan

### 1. API Security: GOOD (15/20) → EXCELLENT (20/20)

#### Current Implementation ✅
- ✅ JWT authentication with blacklisting
- ✅ Rate limiting (6 throttle classes)
- ✅ CORS restrictions
- ✅ Permission classes (IsAuthenticated)

#### Missing for EXCELLENT (5 points)

**1.1 API Versioning Strategy** (2 points)
- **Status:** ⚠️ Missing
- **Impact:** Breaking changes can disrupt clients
- **Implementation:**
  ```python
  # src/obc_management/urls.py
  urlpatterns = [
      path('api/v1/', include('api.v1.urls')),  # Current version
      path('api/v2/', include('api.v2.urls')),  # Future version
  ]
  ```
- **File to create:** `src/api/v1/urls.py` (organize all API endpoints)
- **Timeline:** 2 hours

**1.2 API Request/Response Logging** (1 point)
- **Status:** ⚠️ Missing
- **Impact:** Limited forensics for API abuse
- **Implementation:**
  ```python
  # src/common/middleware.py
  class APILoggingMiddleware:
      """Log all API requests/responses for audit trail."""
      def __call__(self, request):
          if request.path.startswith('/api/'):
              log_api_request(request)  # Log method, path, user, IP
              response = self.get_response(request)
              log_api_response(response)  # Log status code, duration
              return response
  ```
- **Timeline:** 4 hours

**1.3 API Key Authentication (Optional Alternative)** (1 point)
- **Status:** ⚠️ Missing
- **Impact:** Service-to-service authentication limited to JWT only
- **Implementation:**
  ```python
  # src/common/authentication.py
  class APIKeyAuthentication(BaseAuthentication):
      """Allow API key authentication for service accounts."""
      def authenticate(self, request):
          api_key = request.META.get('HTTP_X_API_KEY')
          # Validate against APIKey model
  ```
- **Timeline:** 6 hours

**1.4 Disable DRF Browsable API in Production** (1 point)
- **Status:** ⚠️ Enabled in production
- **Impact:** Information disclosure, increases attack surface
- **Implementation:**
  ```python
  # src/obc_management/settings/production.py
  REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"] = [
      "rest_framework.renderers.JSONRenderer",
      # Remove BrowsableAPIRenderer in production
  ]
  ```
- **Timeline:** 15 minutes ✅ **QUICK WIN**

**1.5 API Schema Documentation (OpenAPI/Swagger)** (Bonus)
- **Status:** ⚠️ Missing
- **Impact:** Harder for developers to discover and use API correctly
- **Implementation:**
  ```bash
  pip install drf-spectacular
  ```
  ```python
  # Auto-generate OpenAPI 3.0 schema
  INSTALLED_APPS += ["drf_spectacular"]
  REST_FRAMEWORK["DEFAULT_SCHEMA_CLASS"] = "drf_spectacular.openapi.AutoSchema"
  ```
- **Timeline:** 3 hours

---

### 2. Data Protection: GOOD (15/20) → EXCELLENT (20/20)

#### Current Implementation ✅
- ✅ Password hashing (PBKDF2, 260k iterations)
- ✅ File upload validation
- ✅ Database connection pooling
- ✅ Environment variable security

#### Missing for EXCELLENT (5 points)

**2.1 Field-Level Encryption for PII** (2 points)
- **Status:** ⚠️ Missing
- **Impact:** Database dump exposes plaintext PII (names, emails, phone numbers)
- **Implementation:**
  ```python
  # Install django-encrypted-model-fields
  pip install django-encrypted-model-fields

  # src/common/models.py
  from encrypted_model_fields.fields import EncryptedCharField, EncryptedEmailField

  class User(AbstractUser):
      # Encrypt sensitive fields
      first_name = EncryptedCharField(max_length=150)
      last_name = EncryptedCharField(max_length=150)
      email = EncryptedEmailField()
      contact_number = EncryptedCharField(max_length=20, blank=True)
  ```
- **Migration Required:** Yes (data migration needed)
- **Timeline:** 8 hours (including migration planning)

**2.2 Database Encryption at Rest (PostgreSQL TDE)** (2 points)
- **Status:** ⚠️ Missing
- **Impact:** Physical disk access reveals data
- **Implementation:**
  ```sql
  -- PostgreSQL pgcrypto extension
  CREATE EXTENSION pgcrypto;

  -- Or use full-disk encryption at OS level (LUKS, dm-crypt)
  -- Or use PostgreSQL Transparent Data Encryption (TDE)
  ```
- **Environment:** Production only (requires DBA access)
- **Timeline:** 4 hours (DBA coordination)

**2.3 Secrets Management Service** (1 point)
- **Status:** ⚠️ Using .env files only
- **Impact:** Secrets stored in plaintext files
- **Implementation:**
  ```bash
  # Option 1: AWS Secrets Manager
  pip install boto3

  # Option 2: HashiCorp Vault
  pip install hvac

  # Option 3: Google Secret Manager
  pip install google-cloud-secret-manager
  ```
  ```python
  # src/obc_management/settings/production.py
  import boto3

  def get_secret(secret_name):
      client = boto3.client('secretsmanager')
      return client.get_secret_value(SecretId=secret_name)['SecretString']

  SECRET_KEY = get_secret('OBCMS_SECRET_KEY')
  DATABASE_URL = get_secret('OBCMS_DATABASE_URL')
  ```
- **Timeline:** 6 hours (cloud setup + integration)

**2.4 Data Retention & Deletion Policy** (Bonus)
- **Status:** ⚠️ Not implemented
- **Impact:** Data Privacy Act compliance gap
- **Implementation:**
  ```python
  # src/common/management/commands/cleanup_old_data.py
  class Command(BaseCommand):
      def handle(self):
          # Delete activity logs older than 1 year
          cutoff = timezone.now() - timedelta(days=365)
          old_logs = ActivityLog.objects.filter(created_at__lt=cutoff)
          old_logs.delete()
  ```
- **Timeline:** 4 hours

---

### 3. Infrastructure Security: GOOD (15/20) → EXCELLENT (20/20)

#### Current Implementation ✅
- ✅ Environment variable management
- ✅ Static file security (WhiteNoise)
- ✅ Health monitoring probes
- ✅ HTTPS enforcement

#### Missing for EXCELLENT (5 points)

**3.1 Web Application Firewall (WAF)** (2 points)
- **Status:** ⚠️ Missing
- **Impact:** No DDoS protection, SQL injection/XSS filtering
- **Implementation Options:**

  **Option 1: Cloudflare (Recommended - Free)**
  ```
  1. Create Cloudflare account
  2. Add obcms.gov.ph domain
  3. Update DNS nameservers
  4. Enable WAF rules (OWASP Core Ruleset)
  5. Enable DDoS protection
  6. Enable bot detection
  ```
  - **Cost:** Free (Pro plan $20/month for advanced features)
  - **Timeline:** 2 hours

  **Option 2: AWS WAF + CloudFront**
  ```python
  # AWS WAF configuration
  - Create WAF Web ACL
  - Add OWASP Top 10 rules
  - Add rate limiting rules
  - Attach to CloudFront distribution
  ```
  - **Cost:** ~$5-20/month (pay-per-use)
  - **Timeline:** 4 hours

  **Option 3: ModSecurity (Self-Hosted)**
  ```nginx
  # nginx.conf with ModSecurity
  load_module modules/ngx_http_modsecurity_module.so;

  modsecurity on;
  modsecurity_rules_file /etc/nginx/modsecurity/modsecurity.conf;
  ```
  - **Cost:** Free (infrastructure only)
  - **Timeline:** 6 hours

**3.2 Intrusion Detection System (IDS)** (1 point)
- **Status:** ⚠️ Missing
- **Impact:** No detection of malicious network traffic
- **Implementation:**
  ```bash
  # Install Fail2Ban (lightweight IDS)
  apt-get install fail2ban

  # Configure for Django
  # /etc/fail2ban/jail.local
  [django-auth]
  enabled = true
  port = http,https
  filter = django-auth
  logpath = /var/log/django/django.log
  maxretry = 5
  bantime = 3600
  ```
- **Timeline:** 3 hours

**3.3 Container Security Scanning** (1 point)
- **Status:** ⚠️ Missing
- **Impact:** Vulnerable Docker images
- **Implementation:**
  ```bash
  # Scan Docker images for vulnerabilities
  docker run --rm -v /var/run/docker.sock:/var/run/docker.sock aquasec/trivy image obcms:latest
  ```
  ```yaml
  # .github/workflows/security.yml
  - name: Scan Docker image
    uses: aquasecurity/trivy-action@master
    with:
      image-ref: 'obcms:latest'
      severity: 'CRITICAL,HIGH'
  ```
- **Timeline:** 2 hours

**3.4 Infrastructure as Code (IaC) Security Scanning** (1 point)
- **Status:** ⚠️ Missing
- **Impact:** Insecure infrastructure configurations
- **Implementation:**
  ```bash
  # Scan Docker Compose / Terraform files
  docker run --rm -v $(pwd):/src aquasec/tfsec /src
  ```
- **Timeline:** 2 hours

**3.5 Regular Security Updates Automation** (Bonus)
- **Status:** ⚠️ Manual only
- **Impact:** Delayed security patches
- **Implementation:**
  ```bash
  # Dependabot configuration
  # .github/dependabot.yml
  version: 2
  updates:
    - package-ecosystem: "pip"
      directory: "/"
      schedule:
        interval: "weekly"
      open-pull-requests-limit: 10
  ```
- **Timeline:** 1 hour ✅ **QUICK WIN**

---

### 4. Monitoring & Response: GOOD (14/20) → EXCELLENT (20/20)

#### Current Implementation ✅
- ✅ Security event logging (authentication, access)
- ✅ Audit logging (django-auditlog)
- ✅ Failed login tracking (django-axes)
- ✅ File logging (django.log)

#### Missing for EXCELLENT (6 points)

**4.1 Centralized Log Aggregation** (2 points)
- **Status:** ⚠️ Missing
- **Impact:** Distributed logs, hard to detect attack patterns
- **Implementation:**

  **Option 1: Graylog (Recommended - Open Source)**
  ```yaml
  # docker-compose.yml
  graylog:
    image: graylog/graylog:5.2
    environment:
      GRAYLOG_HTTP_EXTERNAL_URI: "http://logs.obcms.gov.ph/"
    ports:
      - "9000:9000"   # Web interface
      - "12201:12201" # GELF input
  ```
  ```python
  # Send logs to Graylog
  LOGGING["handlers"]["graylog"] = {
      "class": "graypy.GELFUDPHandler",
      "host": "graylog",
      "port": 12201,
  }
  ```
  - **Cost:** Free (infrastructure only)
  - **Timeline:** 6 hours

  **Option 2: ELK Stack (Elasticsearch, Logstash, Kibana)**
  - **Cost:** Free (infrastructure only)
  - **Timeline:** 8 hours

  **Option 3: Datadog (Commercial SaaS)**
  - **Cost:** $15/host/month
  - **Timeline:** 3 hours

**4.2 Real-Time Security Alerts** (2 points)
- **Status:** ⚠️ Missing
- **Impact:** Delayed response to security incidents
- **Implementation:**
  ```python
  # src/common/alerting.py
  import requests

  def send_security_alert(event_type, details, severity="WARNING"):
      """Send alert to Slack/Email/PagerDuty."""
      if severity in ["CRITICAL", "ERROR"]:
          # Send to Slack
          requests.post(settings.SLACK_WEBHOOK_URL, json={
              "text": f"🚨 Security Alert: {event_type}\n{details}"
          })

          # Send email to security team
          send_mail(
              subject=f"[SECURITY] {event_type}",
              message=details,
              recipient_list=settings.SECURITY_TEAM_EMAILS,
          )
  ```
  ```python
  # Integrate with security logging
  def log_failed_login(request, username, reason):
      # ... existing logging

      # Alert on 10+ failed logins in 5 minutes
      recent_failures = FailedLogin.objects.filter(
          created_at__gte=timezone.now() - timedelta(minutes=5)
      ).count()
      if recent_failures >= 10:
          send_security_alert(
              event_type="Brute Force Attack Detected",
              details=f"10+ failed logins in 5 minutes from IP {ip}",
              severity="CRITICAL"
          )
  ```
- **Timeline:** 4 hours

**4.3 Security Metrics Dashboard** (1 point)
- **Status:** ⚠️ Missing
- **Impact:** No visibility into security posture
- **Implementation:**
  ```python
  # src/common/views/security_dashboard.py
  @staff_member_required
  def security_dashboard(request):
      metrics = {
          "failed_logins_24h": FailedLogin.objects.filter(
              created_at__gte=timezone.now() - timedelta(hours=24)
          ).count(),
          "locked_accounts": User.objects.filter(is_locked=True).count(),
          "active_sessions": Session.objects.filter(
              expire_date__gte=timezone.now()
          ).count(),
          "recent_exports": DataExport.objects.filter(
              created_at__gte=timezone.now() - timedelta(hours=24)
          ).count(),
      }
      return render(request, "security/dashboard.html", metrics)
  ```
- **Timeline:** 6 hours

**4.4 Incident Response Playbook** (1 point)
- **Status:** ⚠️ Missing
- **Impact:** Chaotic response to security incidents
- **Implementation:**
  ```markdown
  # docs/security/INCIDENT_RESPONSE_PLAYBOOK.md

  ## Incident Classification
  - P0: Active data breach (Response: 15 minutes)
  - P1: Critical vulnerability (Response: 1 hour)
  - P2: Security policy violation (Response: 4 hours)
  - P3: Low severity (Response: 24 hours)

  ## Response Steps
  1. Detection & Triage (15 min)
  2. Containment (1 hour)
  3. Eradication
  4. Recovery
  5. Post-Incident Review (7 days)

  ## Contact Information
  - Security Lead: security@oobc.gov.ph
  - NPC Breach Notification: complaints@privacy.gov.ph
  ```
- **Timeline:** 4 hours (documentation)

**4.5 Automated Security Testing** (Bonus)
- **Status:** ⚠️ Manual only
- **Impact:** Regressions not caught early
- **Implementation:**
  ```python
  # tests/security/test_security.py
  class SecurityTestCase(TestCase):
      def test_api_requires_authentication(self):
          """Ensure all API endpoints require auth."""
          response = self.client.get('/api/communities/')
          self.assertEqual(response.status_code, 401)

      def test_rate_limiting_enforced(self):
          """Ensure rate limiting blocks excessive requests."""
          for i in range(150):
              response = self.client.get('/api/communities/')
          self.assertEqual(response.status_code, 429)

      def test_csrf_protection_active(self):
          """Ensure CSRF protection blocks unauthenticated POST."""
          response = self.client.post('/api/communities/', {})
          self.assertEqual(response.status_code, 403)
  ```
- **Timeline:** 4 hours

---

## Implementation Priority Matrix

### 🔴 CRITICAL (Do Immediately - Same Day)

**Total: 4 tasks, 2.25 hours**

| Task | Category | Points | Timeline | Complexity |
|------|----------|--------|----------|------------|
| **Disable DRF Browsable API (Production)** | API Security | +1 | 15 min | ✅ Trivial |
| **Enable Dependabot** | Infrastructure | +1 | 1 hour | ✅ Easy |
| **API Versioning Setup** | API Security | +2 | 2 hours | ⚠️ Moderate |

**Impact:** +4 points (89/100 score) in 2.25 hours

---

### 🟠 HIGH (Do Within 3 Days)

**Total: 6 tasks, 18 hours**

| Task | Category | Points | Timeline | Complexity |
|------|----------|--------|----------|------------|
| **Deploy Cloudflare WAF** | Infrastructure | +2 | 2 hours | ✅ Easy |
| **API Request/Response Logging** | API Security | +1 | 4 hours | ⚠️ Moderate |
| **Real-Time Security Alerts** | Monitoring | +2 | 4 hours | ⚠️ Moderate |
| **Incident Response Playbook** | Monitoring | +1 | 4 hours | ✅ Easy |
| **Container Security Scanning** | Infrastructure | +1 | 2 hours | ✅ Easy |
| **Fail2Ban IDS** | Infrastructure | +1 | 3 hours | ⚠️ Moderate |

**Impact:** +8 points (97/100 score) in 18 hours

---

### 🟡 MEDIUM (Do Within 1 Week)

**Total: 5 tasks, 23 hours**

| Task | Category | Points | Timeline | Complexity |
|------|----------|--------|----------|------------|
| **Centralized Log Aggregation (Graylog)** | Monitoring | +2 | 6 hours | ⚠️ Moderate |
| **Security Metrics Dashboard** | Monitoring | +1 | 6 hours | ⚠️ Moderate |
| **API Key Authentication** | API Security | +1 | 6 hours | ⚠️ Moderate |
| **Secrets Management Service** | Data Protection | +1 | 6 hours | 🔴 Complex |
| **Field-Level Encryption (PII)** | Data Protection | +2 | 8 hours | 🔴 Complex |

**Impact:** +7 points (100/100 score) ✅

---

### 🟢 LOW (Nice to Have - Week 2)

**Total: 4 tasks, 15 hours**

| Task | Category | Points | Timeline | Complexity |
|------|----------|--------|----------|------------|
| **Database Encryption at Rest** | Data Protection | +2 | 4 hours | 🔴 Complex |
| **Data Retention Policy** | Data Protection | Bonus | 4 hours | ⚠️ Moderate |
| **API Schema Documentation** | API Security | Bonus | 3 hours | ✅ Easy |
| **Automated Security Testing** | Monitoring | Bonus | 4 hours | ⚠️ Moderate |

**Impact:** Bonus points, compliance, developer experience

---

## Detailed Implementation Guides

### Quick Wins (Today - 2.25 hours)

#### 1. Disable DRF Browsable API in Production (15 min) ✅

**File:** `src/obc_management/settings/production.py`

```python
# Add after REST_FRAMEWORK configuration
REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"] = [
    "rest_framework.renderers.JSONRenderer",
    # BrowsableAPIRenderer removed for production security
]
```

**Verification:**
```bash
# Should return JSON only, no HTML
curl -H "Accept: text/html" https://obcms.gov.ph/api/communities/
```

---

#### 2. Enable Dependabot (1 hour) ✅

**File:** `.github/dependabot.yml`

```yaml
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 10
    reviewers:
      - "security-team"
    labels:
      - "security"
      - "dependencies"

  - package-ecosystem: "docker"
    directory: "/"
    schedule:
      interval: "weekly"

  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "monthly"
```

**Verification:**
- Push to GitHub
- Check Security tab → Dependabot alerts
- Weekly PRs for dependency updates

---

#### 3. API Versioning Setup (2 hours) ⚠️

**Step 1: Create versioned API structure**

```bash
mkdir -p src/api/v1
touch src/api/__init__.py
touch src/api/v1/__init__.py
touch src/api/v1/urls.py
```

**Step 2: Organize existing API endpoints**

`src/api/v1/urls.py`:
```python
"""API v1 URL Configuration."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

# Import viewsets from all apps
from communities.api.views import CommunityViewSet
from mana.api.views import AssessmentViewSet
from coordination.api.views import PartnershipViewSet

router = DefaultRouter()
router.register(r'communities', CommunityViewSet, basename='community')
router.register(r'assessments', AssessmentViewSet, basename='assessment')
router.register(r'partnerships', PartnershipViewSet, basename='partnership')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('rest_framework_simplejwt.urls')),
]
```

**Step 3: Update main URLs**

`src/obc_management/urls.py`:
```python
urlpatterns = [
    # ...existing patterns
    path('api/v1/', include('api.v1.urls')),  # Versioned API
    # path('api/', include('api.v1.urls')),  # Redirect old /api/ to /api/v1/
]
```

**Verification:**
```bash
curl https://obcms.gov.ph/api/v1/communities/
```

---

### High Priority (Within 3 Days - 18 hours)

#### 4. Deploy Cloudflare WAF (2 hours) ✅

**Step 1: Sign up for Cloudflare**
1. Go to https://cloudflare.com
2. Create account (free plan)
3. Add domain: `obcms.gov.ph`

**Step 2: Update DNS**
1. Cloudflare provides nameservers (e.g., `ns1.cloudflare.com`)
2. Update domain registrar to use Cloudflare nameservers
3. Wait for DNS propagation (15-60 min)

**Step 3: Enable WAF rules**
1. Go to Security → WAF
2. Enable OWASP Core Ruleset
3. Enable DDoS protection (automatic)
4. Enable bot fight mode

**Step 4: Configure security settings**
```
SSL/TLS → Full (strict)
Firewall → Create rules:
  - Block known bad bots
  - Challenge on high threat score (>50)
  - Rate limit: 100 requests/10 seconds per IP
```

**Step 5: Update Django settings**
```python
# src/obc_management/settings/production.py
# Trust Cloudflare proxy headers
AXES_IPWARE_META_PRECEDENCE_ORDER = [
    "HTTP_CF_CONNECTING_IP",  # Cloudflare real IP
    "HTTP_X_FORWARDED_FOR",
    "REMOTE_ADDR",
]
```

**Verification:**
- Test DDoS protection: `ab -n 1000 -c 100 https://obcms.gov.ph/`
- Check Cloudflare dashboard for blocked requests

---

#### 5. API Request/Response Logging (4 hours) ⚠️

**File:** `src/common/middleware.py`

```python
import logging
import time
import json
from django.utils.deprecation import MiddlewareMixin

api_logger = logging.getLogger('api')


class APILoggingMiddleware(MiddlewareMixin):
    """
    Log all API requests and responses for audit trail.

    Logs:
    - Request: method, path, user, IP, headers, body
    - Response: status code, duration, size
    """

    def process_request(self, request):
        # Only log API requests
        if not request.path.startswith('/api/'):
            return None

        # Store request start time
        request._api_log_start = time.time()

        # Log request details
        user = request.user if request.user.is_authenticated else "Anonymous"
        api_logger.info(
            f"API Request | "
            f"Method: {request.method} | "
            f"Path: {request.path} | "
            f"User: {user} | "
            f"IP: {self._get_client_ip(request)} | "
            f"User-Agent: {request.META.get('HTTP_USER_AGENT', 'Unknown')[:100]}"
        )

        return None

    def process_response(self, request, response):
        # Only log API responses
        if not request.path.startswith('/api/'):
            return response

        # Calculate request duration
        if hasattr(request, '_api_log_start'):
            duration = time.time() - request._api_log_start
        else:
            duration = 0

        # Log response details
        user = request.user if request.user.is_authenticated else "Anonymous"
        api_logger.info(
            f"API Response | "
            f"Method: {request.method} | "
            f"Path: {request.path} | "
            f"User: {user} | "
            f"Status: {response.status_code} | "
            f"Duration: {duration:.3f}s"
        )

        # Log errors with more details
        if response.status_code >= 400:
            api_logger.warning(
                f"API Error | "
                f"Method: {request.method} | "
                f"Path: {request.path} | "
                f"User: {user} | "
                f"Status: {response.status_code} | "
                f"IP: {self._get_client_ip(request)}"
            )

        return response

    def _get_client_ip(self, request):
        """Get client IP address (proxy-aware)."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', 'Unknown')
        return ip
```

**Add to middleware:**
```python
# src/obc_management/settings/base.py
MIDDLEWARE = [
    # ...existing middleware
    "common.middleware.APILoggingMiddleware",  # Add before response middleware
]
```

**Configure API logger:**
```python
# src/obc_management/settings/base.py
LOGGING["loggers"]["api"] = {
    "handlers": ["console", "file"],
    "level": "INFO",
    "propagate": False,
}
```

**Verification:**
```bash
# Make API request
curl -X GET http://localhost:8000/api/v1/communities/ -H "Authorization: Bearer <token>"

# Check logs
tail -f src/logs/django.log | grep "API"
```

---

#### 6. Real-Time Security Alerts (4 hours) ⚠️

**File:** `src/common/alerting.py`

```python
"""Real-time security alerting via Slack, Email, PagerDuty."""
import logging
import requests
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta

logger = logging.getLogger(__name__)


def send_security_alert(event_type, details, severity="WARNING", metadata=None):
    """
    Send security alert to configured channels.

    Args:
        event_type: Type of security event (e.g., "Brute Force Attack")
        details: Detailed description of the event
        severity: INFO, WARNING, ERROR, CRITICAL
        metadata: Additional context (dict)
    """
    severity_emoji = {
        "INFO": "ℹ️",
        "WARNING": "⚠️",
        "ERROR": "❌",
        "CRITICAL": "🚨",
    }

    emoji = severity_emoji.get(severity, "📢")

    # Format alert message
    alert_message = f"{emoji} **{severity}**: {event_type}\n\n{details}"

    if metadata:
        alert_message += f"\n\n**Metadata:**\n```json\n{json.dumps(metadata, indent=2)}\n```"

    # Send to Slack (if configured)
    if hasattr(settings, 'SLACK_WEBHOOK_URL') and settings.SLACK_WEBHOOK_URL:
        try:
            send_slack_alert(alert_message, severity)
        except Exception as e:
            logger.error(f"Failed to send Slack alert: {e}")

    # Send email (for ERROR and CRITICAL)
    if severity in ["ERROR", "CRITICAL"]:
        try:
            send_email_alert(event_type, alert_message)
        except Exception as e:
            logger.error(f"Failed to send email alert: {e}")


def send_slack_alert(message, severity):
    """Send alert to Slack channel."""
    color_map = {
        "INFO": "#36a64f",      # Green
        "WARNING": "#ff9900",   # Orange
        "ERROR": "#ff0000",     # Red
        "CRITICAL": "#8b0000",  # Dark red
    }

    payload = {
        "text": "🔒 OBCMS Security Alert",
        "attachments": [
            {
                "color": color_map.get(severity, "#808080"),
                "text": message,
                "footer": "OBCMS Security Monitoring",
                "footer_icon": "https://obcms.gov.ph/static/img/logo.png",
                "ts": int(timezone.now().timestamp()),
            }
        ]
    }

    response = requests.post(
        settings.SLACK_WEBHOOK_URL,
        json=payload,
        timeout=5
    )
    response.raise_for_status()


def send_email_alert(subject, message):
    """Send alert email to security team."""
    send_mail(
        subject=f"[OBCMS SECURITY] {subject}",
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=settings.SECURITY_TEAM_EMAILS,
        fail_silently=False,
    )
```

**Integrate with security logging:**

```python
# src/common/security_logging.py
from .alerting import send_security_alert

def log_failed_login(request, username, reason="Invalid credentials"):
    """Log failed login with alerting for brute force detection."""
    ip_address = get_client_ip(request)

    # ... existing logging code ...

    # Check for brute force attack
    from axes.models import AccessAttempt
    recent_failures = AccessAttempt.objects.filter(
        ip_address=ip_address,
        attempt_time__gte=timezone.now() - timedelta(minutes=5)
    ).count()

    if recent_failures >= 10:
        send_security_alert(
            event_type="Brute Force Attack Detected",
            details=(
                f"**IP Address:** {ip_address}\n"
                f"**Username:** {username}\n"
                f"**Failed Attempts:** {recent_failures} in 5 minutes\n"
                f"**User Agent:** {request.META.get('HTTP_USER_AGENT', 'Unknown')}"
            ),
            severity="CRITICAL",
            metadata={
                "ip": ip_address,
                "username": username,
                "attempts": recent_failures,
            }
        )
```

**Configuration:**

```python
# src/obc_management/settings/base.py
# Slack webhook URL (from environment)
SLACK_WEBHOOK_URL = env.str('SLACK_WEBHOOK_URL', default='')

# Security team emails
SECURITY_TEAM_EMAILS = env.list('SECURITY_TEAM_EMAILS', default=['security@oobc.gov.ph'])
```

**Environment variables:**
```env
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
SECURITY_TEAM_EMAILS=security@oobc.gov.ph,it@oobc.gov.ph
```

**Verification:**
```bash
# Trigger brute force alert (10 failed logins)
for i in {1..10}; do
    curl -X POST http://localhost:8000/login/ -d "username=test&password=wrong"
done

# Check Slack channel for alert
```

---

## Summary: Path to 100/100

### Sprint 1: Same Day (2.25 hours) → 89/100 ✅

```
✅ Disable DRF Browsable API      (15 min)  +1 point
✅ Enable Dependabot               (1 hour)  +1 point
✅ API Versioning Setup            (2 hours) +2 points
───────────────────────────────────────────────────
Total: 3 tasks, 2.25 hours, +4 points (89/100)
```

### Sprint 2: Within 3 Days (18 hours) → 97/100 ✅

```
✅ Deploy Cloudflare WAF           (2 hours) +2 points
✅ API Request/Response Logging    (4 hours) +1 point
✅ Real-Time Security Alerts       (4 hours) +2 points
✅ Incident Response Playbook      (4 hours) +1 point
✅ Container Security Scanning     (2 hours) +1 point
✅ Fail2Ban IDS                    (3 hours) +1 point
───────────────────────────────────────────────────
Total: 6 tasks, 18 hours, +8 points (97/100)
```

### Sprint 3: Within 1 Week (23 hours) → 100/100 ✅ 🎉

```
✅ Centralized Log Aggregation     (6 hours) +2 points
✅ Security Metrics Dashboard      (6 hours) +1 point
✅ API Key Authentication          (6 hours) +1 point
✅ Secrets Management Service      (6 hours) +1 point
✅ Field-Level Encryption (PII)    (8 hours) +2 points
───────────────────────────────────────────────────
Total: 5 tasks, 23 hours, +7 points (100/100) ✅
```

### Bonus: Week 2 (15 hours) → 100+ points 🚀

```
✅ Database Encryption at Rest     (4 hours) +2 points
✅ Data Retention Policy           (4 hours) Compliance
✅ API Schema Documentation        (3 hours) DevEx
✅ Automated Security Testing      (4 hours) CI/CD
───────────────────────────────────────────────────
Total: 4 tasks, 15 hours, +2 points + compliance + DevEx
```

---

## Final Security Score Projection

| Timeline | Score | Status | Notes |
|----------|-------|--------|-------|
| **Current** | 85/100 | GOOD | Production-ready |
| **Same Day** | 89/100 | GOOD+ | Quick wins completed |
| **Day 3** | 97/100 | EXCELLENT- | High priority done |
| **Week 1** | **100/100** | **✅ EXCELLENT** | **All categories EXCELLENT** |
| **Week 2** | 100+/100 | EXCELLENT+ | Bonus features, compliance |

---

## Risk Category Breakdown (Target: 100/100)

| Category | Current | Day 3 | Week 1 | Status |
|----------|---------|-------|--------|--------|
| **Authentication & Authorization** | 20/20 | 20/20 | 20/20 | ✅ EXCELLENT |
| **API Security** | 15/20 | 19/20 | 20/20 | ✅ EXCELLENT |
| **Data Protection** | 15/20 | 15/20 | 20/20 | ✅ EXCELLENT |
| **Infrastructure Security** | 15/20 | 20/20 | 20/20 | ✅ EXCELLENT |
| **Monitoring & Response** | 14/20 | 18/20 | 20/20 | ✅ EXCELLENT |
| **Input Validation** | 20/20 | 20/20 | 20/20 | ✅ EXCELLENT |
| **TOTAL** | **85/100** | **97/100** | **100/100** | **✅ EXCELLENT** |

---

**Next Steps:** Start with Sprint 1 (Same Day) quick wins to immediately boost score to 89/100.
